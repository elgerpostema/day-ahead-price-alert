import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import get_time_period

def test_get_time_period():
    """Test the get_time_period function."""
    # This is a basic test - would need more comprehensive tests
    result = get_time_period()
    assert result is not None
    print("✓ Basic test passed")

if __name__ == "__main__":
    test_get_time_period()
    print("All tests passed!")