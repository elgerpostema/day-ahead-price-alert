# day-ahead-price-alert

## Overview
This is a Python script that fetches day-ahead electricity prices from the ENTSO-E API and sends Telegram notifications with price analysis.

## Key Commands
- `python main.py` - Run the main script
- `./tools/test_run.sh` - Run installation and setup verification
- `source .venv/bin/activate && python3 -m pytest test/test_main.py` - Run unit tests

## Architecture
- **Entry point**: `main.py`
- **Configuration**: `config.py` 
- **Tests**: `test/` directory
- **Tools**: `tools/` directory

## Setup Prerequisites
1. Python 3.8+ with virtual environment
2. ENTSO-E API key with RESTful access enabled (send email to transparency@entsoe.eu)
3. Telegram bot token and chat ID
4. Run installation: `source .venv/bin/activate && pip install -r requirements.txt && pip install flake8 mypy pytest types-xmltodict`

## Environment Configuration
- Copy `.env.example` to `.env`
- Add your actual credentials to `.env` file
- Environment variables are loaded with `python-dotenv` at startup

## Testing
- Run unit test: `python3 -m pytest test/test_main.py`  
- Run all quality checks: `./tools/test_run.sh`

## GitHub Actions
- Scheduled daily execution at 14:00 UTC
- Uses workflow file `.github/workflows/run-daily.yml`
- Secrets required: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `ENTSOE_API_KEY`

## Dependencies
- `python-dotenv` - Environment variable loading  
- `requests` - HTTP requests to ENTSO-E API
- `xmltodict` - XML to dictionary conversion

## File Structure
- `main.py`: Core execution logic with all functionality
- `config.py`: Configuration management  
- `test/`: Unit tests and test setup
- `tools/`: Development utilities including test_run.sh