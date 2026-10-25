#!/usr/bin/env bash

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install the required packages
pip install --upgrade pip
pip install -r requirements.txt

# Run the python script
python main.py

