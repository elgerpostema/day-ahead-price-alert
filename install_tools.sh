#!/bin/bash

# Script to install missing Python tools for the day-ahead-price-alert project
echo "Installing required Python tools..."

# Install pip if not available
if ! command -v pip &> /dev/null; then
    echo "Installing pip..."
    sudo apt update
    sudo apt install -y python3-pip
fi

# Install the required Python packages
echo "Installing Python packages..."
pip3 install --user flake8 mypy pytest xmltodict requests python-dotenv

echo "Installation complete!"
echo "You can now run quality checks with: python3 quality_check.py"