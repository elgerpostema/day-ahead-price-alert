#!/usr/bin/env python3
"""
Setup script to install test dependencies for the day-ahead-price-alert project.
This script installs pytest, flake8, and mypy for code quality checking.
"""

import subprocess
import sys

def install_requirements():
    """Install required test tools."""
    try:
        # Install pytest
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        
        # Install linters
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flake8"])
        
        # Install type checker
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mypy"])
        
        print("Successfully installed test dependencies.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_requirements()