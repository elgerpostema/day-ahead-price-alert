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

# ==================== Initialisation =========================================
# use today, start at midnight, end 1 day later
now = datetime.now(amsterdam_tz)
start_local = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
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


# ==================== Run the code============================================

send_telegram_message(f"The test script has run.")
