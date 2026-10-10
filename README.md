# day-ahead-price-alert

Track ENTSO-E electricity prices and send daily summaries via Telegram.

## Features

- Fetches day-ahead electricity prices from ENTSO-E API
- Analyzes hourly price data for the upcoming day
- Sends Telegram notifications with:
  - Price analysis (best/worst time blocks)
  - Price difference delta
- Handles timezone conversions correctly
- Includes comprehensive error handling and logging
- Configurable price thresholds

## Requirements

- Python 3.8+
- ENTSO-E API key (with RESTful access enabled)
- Telegram bot token and chat ID
- Virtual environment with dependencies

## Setup

1. Create virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install flake8 mypy pytest types-xmltodict
```

3. Configure environment variables:
```bash
cp env.example .env
# Edit .env with your actual credentials
```

4. Run the script:
```bash
python main.py
```

## Testing

Run quality checks:
```bash
./tools/test_run.sh
```

## Project Structure

- `main.py` - Main execution logic
- `config.py` - Configuration management  
- `test/` - Test files (test_main.py, test_setup.py)
- `tools/` - Development utilities (install_tools.sh, quality_check.py, test_run.sh)

## API Activation

Before using the script:
1. Send email to transparency@entsoe.eu requesting RESTful API access
2. Enable your API key for "RESTful API access"
3. Add the generated key to `.env` file

## Telegram Integration

The script automatically sends a formatted message to your configured Telegram chat containing:
- Time period analyzed
- Best and worst price blocks  
- Price difference between peak and trough