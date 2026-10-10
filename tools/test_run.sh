#!/bin/bash

echo "=== Testing day-ahead-price-alert installation ==="

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found"
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate" 
    echo "   pip install -r requirements.txt"
    echo "   pip install flake8 mypy pytest types-xmltodict"
    exit 1
fi

# Check if required files exist
if [ -f "main.py" ]; then
    echo "✅ main.py found"
else
    echo "❌ main.py not found"
    exit 1
fi

# Display current git status 
echo ""
echo "=== Git Status ==="
git status --porcelain

echo ""
echo "=== Project Structure ==="
ls -la

echo ""
echo "=== Configuration Check ==="
if [ -f ".env" ]; then
    echo "✅ .env file found (contains secret configuration)"
else
    echo "💡 No .env file found. Create one based on env.example"
    if [ -f "env.example" ]; then
        echo "Example configuration:"
        cat env.example
    fi
fi

echo ""
echo "=== Ready to Run ==="
echo "To test the script, add your credentials to .env file and run:"
echo "python3 main.py"

echo ""
echo "=== API Activation Required ==="
echo "⚠️  Before this will work, you must activate your ENTSO-E API key:"
echo "   Send email to transparency@entsoe.eu requesting RESTful API access"