#!/usr/bin/env python3
"""
Test script to demonstrate the testing workflow for the day-ahead-price-alert project.
This script shows how the tester agent would run quality checks.
"""

import subprocess
import sys
import os

def run_flake8():
    """Run flake8 linter on the main.py file."""
    try:
        result = subprocess.run([
            sys.executable, "-m", "flake8", 
            "main.py", "--max-line-length=120"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✓ Flake8 linting passed")
        else:
            print("✗ Flake8 linting failed:")
            print(result.stdout)
            return False
        return True
    except Exception as e:
        print(f"Error running flake8: {e}")
        return False

def run_mypy():
    """Run mypy type checker on the main.py file."""
    try:
        result = subprocess.run([
            sys.executable, "-m", "mypy", 
            "main.py"
        ], capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✓ Mypy type checking passed")
        else:
            print("✗ Mypy type checking failed:")
            print(result.stdout)
            return False
        return True
    except Exception as e:
        print(f"Error running mypy: {e}")
        return False

def run_pytest():
    """Run pytest tests if any exist."""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            ".", "-v"
        ], capture_output=True, text=True, cwd=".")
        
        # If no tests found, this might be expected
        if "no tests found" in result.stdout.lower() or "no tests collected" in result.stdout.lower():
            print("ℹ No tests found (this is expected for a new project)")
            return True
        elif result.returncode == 0:
            print("✓ All pytest tests passed")
            return True
        else:
            print("✗ Some pytest tests failed:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"Error running pytest: {e}")
        return False

def main():
    """Main testing function."""
    print("Starting code quality checks...")
    
    # Run all checks
    checks = [run_flake8, run_mypy, run_pytest]
    passed = 0
    
    for check in checks:
        if check():
            passed += 1
    
    print(f"\nResults: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("✅ All quality checks passed!")
        return 0
    else:
        print("❌ Some quality checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())