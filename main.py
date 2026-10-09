import os
import requests
import xmltodict
from collections import defaultdict
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration
try:
    from config import (
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID,
        ENTSOE_API_KEY,
        ENTSOE_API_ENDPOINT,
        PRICE_LIMIT,
        AMSTERDAM_TZ,
        UTC_TZ,
        ENTSOE_DOMAIN,
        PRICE_UPDATE_HOUR
    )
except ImportError:
    # Fallback for missing imports - set defaults
    from zoneinfo import ZoneInfo

    AMSTERDAM_TZ = ZoneInfo("Europe/Amsterdam")
    UTC_TZ = ZoneInfo("UTC")

    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
    ENTSOE_API_KEY = os.environ.get("ENTSOE_API_KEY")
    ENTSOE_API_ENDPOINT = "https://web-api.tp.entsoe.eu/api"
    PRICE_LIMIT = -14.00
    ENTSOE_DOMAIN = "10YNL----------L"
    PRICE_UPDATE_HOUR = 15

# ==================== Core Functions ==========================================

def get_time_period():
    """Calculate the time period for price fetching based on current time."""
    now = datetime.now(AMSTERDAM_TZ)

    # start_day => fetch the data for today + 1 (that is tomorrow)
    start_day = 1
    # if the new prices are not available, just fetch it for today
    if now.hour <= PRICE_UPDATE_HOUR:
        start_day = 0
        print("Het is vóór 15:00. Prijzen voor vandaag worden opgehaald...")

    start_local = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=start_day)
    end_local = start_local + timedelta(days=1)

    # Convert to ENTSO-E format (YYYYMMDDHHMM)
    period_start = start_local.astimezone(UTC_TZ).strftime("%Y%m%d%H%M")
    period_end = end_local.astimezone(UTC_TZ).strftime("%Y%m%d%H%M")

    return {
        "start_local": start_local,
        "end_local": end_local,
        "period_start": period_start,
        "period_end": period_end
    }

def send_telegram_message(text):
    """Send formatted message to configured Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Telegram bericht succesvol verzonden!")
    except Exception as e:
        print(f"Fout bij verzenden Telegram bericht: {e}")

def fetch_day_ahead_prices(period_start, period_end):
    """
    Fetch day-ahead electricity prices from ENTSO-E API.

    Args:
        period_start (str): Start time in ENTSO-E format
        period_end (str): End time in ENTSO-E format

    Returns:
        dict or None: Parsed XML data or None if error occurred
    """
    params = {
        "securityToken": ENTSOE_API_KEY,
        "documentType": "A44",
        "in_Domain": ENTSOE_DOMAIN,
        "out_Domain": ENTSOE_DOMAIN,
        "periodStart": period_start,
        "periodEnd": period_end,
    }
    try:
        response = requests.get(ENTSOE_API_ENDPOINT, params=params, timeout=30)
        
        # If the server returns HTML, API access hasn't been activated yet
        if response.text.strip().startswith("<!DOCTYPE html") or "html" in response.text[:50]:
            print("❌ ENTSO-E weigert de verbinding met een HTML-pagina.")
            print("💡 Oplossing: Heb je al een mail gestuurd naar 'transparency@entsoe.eu' om 'Restful API access' te activeren?")
            return None
            
        if response.status_code != 200:
            print(f"❌ ENTSO-E Server Fout (Status {response.status_code}):\n{response.text}")
            return None

        return xmltodict.parse(response.text)
        
    except Exception as e:
        print(f"❌ Netwerk Fout: {e}")
        return None

def calculate_hourly_prices(data_dict, start_local, end_local):
    """
    Calculate hourly price ranges from fetched data.
    
    Args:
        data_dict (dict): Parsed data from ENTSO-E API
        start_local (datetime): Start of the local period
        end_local (datetime): End of the local period
        
    Returns:
        None: Output is printed directly
    """
    if not data_dict or 'Publication_MarketDocument' not in data_dict:
        return

    market_doc = data_dict.get('Publication_MarketDocument', {})
    time_series_data = market_doc.get('TimeSeries', [])
    
    if isinstance(time_series_data, dict):
        time_series_data = [time_series_data]
        
    hourly_prices_collection = defaultdict(list)

    for time_series in time_series_data:
        period = time_series.get('Period', {})
        if not period:
            continue
            
        start_utc_str = period['timeInterval']['start']
        start_utc = datetime.strptime(start_utc_str, "%Y-%m-%dT%H:%MZ").replace(tzinfo=UTC_TZ)
        start_nl = start_utc.astimezone(AMSTERDAM_TZ)
        
        resolution = period.get('resolution')
        points = period.get('Point', [])
        
        if isinstance(points, dict):
            points = [points]
        
        for point in points:
            position = int(point['position'])
            price_per_mwh = float(point['price.amount'])
            price_per_kwh = price_per_mwh / 10  
            
            if resolution == "PT15M":
                minutes_added = (position - 1) * 15
                point_time = start_nl + timedelta(minutes=minutes_added)
            else:
                hours_added = position - 1
                point_time = start_nl + timedelta(hours=hours_added)
                
            if start_local <= point_time < end_local:
                rounded_hour = point_time.replace(minute=0, second=0, microsecond=0)
                hourly_prices_collection[rounded_hour].append(price_per_kwh)

    rounded_hourly_prices = {}
    for hour, prices in hourly_prices_collection.items():
        average = sum(prices) / len(prices)
        rounded_hourly_prices[hour] = round(average)

    if not rounded_hourly_prices:
        print(f"Geen uurprijzen kunnen matchen binnen de dag {start_local.strftime('%d-%m-%Y')}.")
        return

    sorted_hours = sorted(rounded_hourly_prices.keys())
    
    time_blocks = []
    current_block_start = sorted_hours[0]
    current_price = rounded_hourly_prices[current_block_start]
    current_block_end = current_block_start + timedelta(hours=1)

    for hour in sorted_hours[1:]:
        price = rounded_hourly_prices[hour]
        if hour == current_block_end and price == current_price:
            current_block_end = hour + timedelta(hours=1)
        else:
            time_blocks.append({
                'start': current_block_start,
                'end': current_block_end,
                'price': current_price
            })
            current_block_start = hour
            current_price = price
            current_block_end = hour + timedelta(hours=1)
            
    time_blocks.append({
        'start': current_block_start,
        'end': current_block_end,
        'price': current_price
    })

    lowest_block = min(time_blocks, key=lambda x: x['price'])
    highest_block = max(time_blocks, key=lambda x: x['price'])
    
    date_str = sorted_hours[0].strftime('%d-%m-%Y')

    output_lines = []
    output_lines.append(f"📊 Stroomprijsanalyse voor {date_str}")
    
    time_low = f"{lowest_block['start'].strftime('%H:%M')} tot {lowest_block['end'].strftime('%H:%M')}"
    output_lines.append(f"🟢 Goedkoopste tijdsblok: {time_low} -> {lowest_block['price']} ct/kWh")
    
    time_high = f"{highest_block['start'].strftime('%H:%M')} tot {highest_block['end'].strftime('%H:%M')}"
    output_lines.append(f"🔴 Duurste tijdsblok:     {time_high} -> {highest_block['price']} ct/kWh")

    delta_price = round(highest_block['price'] - lowest_block['price'], 2)
    output_lines.append(f"⚖️  Delta in prijs:        {delta_price} ct/kWh\n")

    limit_rounded = round(PRICE_LIMIT)
    has_free_electricity = False
    for block in time_blocks:
        if block['price'] <= limit_rounded:
            # As soon as the first free hour is found, we add a headline once
            if not has_free_electricity:
                output_lines.append("\n🎉 Gratis/goedkope elektra uren:")
                has_free_electricity = True
                
            start_time = block['start'].strftime('%H:%M')
            end_time = block['end'].strftime('%H:%M')
            output_lines.append(f"   • {start_time} - {end_time}: {block['price']} ct/kWh")

    full_message = "\n".join(output_lines)
    print(full_message)
    send_telegram_message(full_message)

def validate_environment():
    """Validate that all required environment variables are set."""
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID", 
        "ENTSOE_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Ontbrekende omgevingsvariabelen: {', '.join(missing_vars)}")
        print("💡 Voeg deze variabelen toe aan je .env bestand of omgeving")
        return False
    
    return True

# ==================== Main Execution Flow =====================================

def main():
    """Execute the main program flow."""
    try:
        # Validate environment setup
        if not validate_environment():
            print("❌ Fout: Vereiste omgevingsvariabelen zijn niet correct ingesteld")
            return
            
        print("🚀 Start van dagelijkse prijscontrole...")
        
        # Get time period for price fetching
        time_period = get_time_period()
        print(f"ℹ Ophaalperiode: {time_period['period_start']} tot {time_period['period_end']}")
        
        # Fetch price data from API
        print("📥 Bezig met ophalen van prijsdata van ENTSO-E API...")
        data_dict = fetch_day_ahead_prices(
            time_period["period_start"], 
            time_period["period_end"]
        )
        
        if data_dict is None:
            print("❌ Geen data ontvangen van ENTSO-E API")
            print("💡 Tip: Zorg dat uw API-sleutel geactiveerd is voor RESTful API toegang")
            print("💡 Stuur een e-mail naar transparency@entsoe.eu om activering te vragen")
            return
            
        # Process and display results
        print("📊 Bezig met verwerken van prijsdata...")
        calculate_hourly_prices(data_dict, time_period["start_local"], time_period["end_local"])
        
        print("✅ Dagelijkse prijscontrole voltooid!")
        
    except Exception as e:
        print(f"❌ Onverwachte fout in hoofdprogramma: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

