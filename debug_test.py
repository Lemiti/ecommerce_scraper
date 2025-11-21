#!/usr/bin/env python3
"""
Debug script to test individual components
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.request_manager import RequestManager
from src.utils.logger import setup_logger

def test_request_manager():
    """Test the RequestManager in isolation"""
    logger = setup_logger("debug")
    logger.info("Testing RequestManager...")
    
    try:
        config = {
            'delay_between_requests': 1.0,
            'timeout': 30,
            'retry_attempts': 3,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        manager = RequestManager(config)
        logger.info("✓ RequestManager initialized successfully")
        
        # Test a simple request
        response = manager.get("http://httpbin.org/json")
        if response and response.status_code == 200:
            logger.info("✓ RequestManager GET request successful")
            return True
        else:
            logger.error("✗ RequestManager GET request failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ RequestManager test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_request_manager()
    if success:
        print("All debug tests passed! ✅")
    else:
        print("Debug tests failed! ❌")
        sys.exit(1)