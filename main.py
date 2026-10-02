import os
import requests
import xmltodict
from collections import defaultdict
from datetime import datetime, timedelta
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# ==================== Load the .env file =====================================
load_dotenv()

# ==================== Get the secrets ========================================
TELEGRAM_BOT_TOKEN= os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID= os.environ.get("TELEGRAM_CHAT_ID")
ENTSOE_API_KEY = os.environ.get("ENTSOE_API_KEY")

# ==================== Configuration ==========================================
# Timezone, will correct for daylightsaving
amsterdam_tz = ZoneInfo("Europe/Amsterdam")
utc_tz = ZoneInfo("UTC")

# ENTSO-E endpoint
ENTSOE_API_ENDPOINT = "https://web-api.tp.entsoe.eu/api"

# Price point below this the electricity is free for the user (cent per kWh)
# this is a negative number, because of taxes and profit margins
PRICE_LIMIT = -14.00

# ==================== Initialisation =========================================
# use today, start at midnight, end 1 day later
now = datetime.now(amsterdam_tz)

# start_day => fetch the data for today + 1 (that is tomorrow)
start_day = 1
# if the new prices are not available, just fetch it for today
if now.hour <= 15:
    start_day = 0
    print("Het is vóór 15:00. Prijzen voor vandaag worden opgehaald...")

start_local = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=start_day)
end_local = start_local + timedelta(days=1)
# convert to ENTSO-E format ( YYYYMMDDHHMM )
period_start = start_local.astimezone(utc_tz).strftime("%Y%m%d%H%M")
period_end = end_local.astimezone(utc_tz).strftime("%Y%m%d%H%M")

# ==================== Functions ==============================================

def send_telegram_message(text):
    """Stuurt het geformatteerde bericht naar de ingestelde Telegram chat."""
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

def fetch_day_ahead_prices():
    params = {
        "securityToken": ENTSOE_API_KEY,
        "documentType": "A44",
        "in_Domain": "10YNL----------L",
        "out_Domain": "10YNL----------L",
        "periodStart": period_start,
        "periodEnd": period_end,
    }
    try:
        response = requests.get(ENTSOE_API_ENDPOINT, params=params, timeout=30)
        
        # Als de server HTML stuurt, is de API-toegang op het account nog niet geactiveerd
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

def bereken_uurprijzen_en_uitersten(data_dict):
    if not data_dict or 'Publication_MarketDocument' not in data_dict:
        return

    market_doc = data_dict.get('Publication_MarketDocument', {})
    time_series_data = market_doc.get('TimeSeries', [])
    
    if isinstance(time_series_data, dict):
        time_series_data = [time_series_data]
        
    uur_prijzen_verzameling = defaultdict(list)

    for ts in time_series_data:
        period = ts.get('Period', {})
        if not period:
            continue
            
        start_utc_str = period['timeInterval']['start']
        start_utc = datetime.strptime(start_utc_str, "%Y-%m-%dT%H:%MZ").replace(tzinfo=utc_tz)
        start_nl = start_utc.astimezone(amsterdam_tz)
        
        resolution = period.get('resolution')
        points = period.get('Point', [])
        
        if isinstance(points, dict):
            points = [points]
        
        for point in points:
            position = int(point['position'])
            prijs_mwh = float(point['price.amount'])
            prijs_kwh = prijs_mwh / 10  
            
            if resolution == "PT15M":
                minuten_erbij = (position - 1) * 15
                punt_tijd = start_nl + timedelta(minutes=minuten_erbij)
            else:
                uren_erbij = position - 1
                punt_tijd = start_nl + timedelta(hours=uren_erbij)
                
            if start_local <= punt_tijd < end_local:
                afgerond_uur = punt_tijd.replace(minute=0, second=0, microsecond=0)
                uur_prijzen_verzameling[afgerond_uur].append(prijs_kwh)

    afgeronde_uurprijzen = {}
    for uur, prijzen in uur_prijzen_verzameling.items():
        gemiddelde = sum(prijzen) / len(prijzen)
        afgeronde_uurprijzen[uur] = round(gemiddelde)

    if not afgeronde_uurprijzen:
        print(f"Geen uurprijzen kunnen matchen binnen de dag {start_local.strftime('%d-%m-%Y')}.")
        return

    gesorteerde_uren = sorted(afgeronde_uurprijzen.keys())
    
    tijdsblokken = []
    huidig_blok_start = gesorteerde_uren[0]
    huidige_prijs = afgeronde_uurprijzen[huidig_blok_start]
    huidig_blok_eind = huidig_blok_start + timedelta(hours=1)

    for uur in gesorteerde_uren[1:]:
        prijs = afgeronde_uurprijzen[uur]
        if uur == huidig_blok_eind and prijs == huidige_prijs:
            huidig_blok_eind = uur + timedelta(hours=1)
        else:
            tijdsblokken.append({
                'start': huidig_blok_start,
                'eind': huidig_blok_eind,
                'prijs': huidige_prijs
            })
            huidig_blok_start = uur
            huidige_prijs = prijs
            huidig_blok_eind = uur + timedelta(hours=1)
            
    tijdsblokken.append({
        'start': huidig_blok_start,
        'eind': huidig_blok_eind,
        'prijs': huidige_prijs
    })

    laagste_blok = min(tijdsblokken, key=lambda x: x['prijs'])
    hoogste_blok = max(tijdsblokken, key=lambda x: x['prijs'])
    
    datum_str = gesorteerde_uren[0].strftime('%d-%m-%Y')

    output_lijnen = []
    output_lijnen.append(f"📊 *Stroomprijsanalyse voor {datum_str} (Afgerond)*")
    
    tijd_laag = f"{laagste_blok['start'].strftime('%H:%M')} tot {laagste_blok['eind'].strftime('%H:%M')}"
    output_lijnen.append(f"🟢 Goedkoopste tijdsblok: {tijd_laag} -> {laagste_blok['prijs']} ct/kWh")
    
    tijd_hoog = f"{hoogste_blok['start'].strftime('%H:%M')} tot {hoogste_blok['eind'].strftime('%H:%M')}"
    output_lijnen.append(f"🔴 Duurste tijdsblok:     {tijd_hoog} -> {hoogste_blok['prijs']} ct/kWh\n")
    
    limiet_afgerond = round(PRICE_LIMIT)
    has_free_electricity = False
    for blok in tijdsblokken:
        if blok['prijs'] <= limiet_afgerond:
            # Zodra het EERSTE gratis uur gevonden wordt, voegen we eenmalig de kop toe
            if not has_free_electricity:
                output_lijnen.append("\n🎉 Gratis/goedkope elektra uren:")
                has_free_electricity = True
                
            van_tijd = blok['start'].strftime('%H:%M')
            tot_tijd = blok['eind'].strftime('%H:%M')
            output_lijnen.append(f"   • {van_tijd} - {tot_tijd}: {blok['prijs']} ct/kWh")

    volledig_bericht = "\n".join(output_lijnen)
    print(volledig_bericht)
    send_telegram_message(volledig_bericht)

# ==================== Run the code============================================

#send_telegram_message(f"Hallo telegram: {period_start}")
data_dict = fetch_day_ahead_prices()

bereken_uurprijzen_en_uitersten(data_dict)

