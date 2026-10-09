"""
Configuration module for day-ahead-price-alert project.
This module centralizes all configuration values and constants.
"""

from datetime import timezone
import os

# ==================== Environment Variables ====================
# Telegram configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ENTSO-E API configuration
ENTSOE_API_KEY = os.environ.get("ENTSOE_API_KEY")
ENTSOE_API_ENDPOINT = "https://web-api.tp.entsoe.eu/api"

# Price configuration - Price point below which electricity is considered free (cent per kWh)
# This is a negative number because of taxes and profit margins
PRICE_LIMIT = -14.00

# Timezone configurations
AMSTERDAM_TZ = timezone.utc  # This will be set by the zoneinfo library in main.py
UTC_TZ = timezone.utc

# ==================== API Constants ====================
# Domain constants for ENTSO-E API
ENTSOE_DOMAIN = "10YNL----------L"

# ==================== Timing Configuration ====================
# Hour threshold to determine when to get today's vs tomorrow's prices
PRICE_UPDATE_HOUR = 15