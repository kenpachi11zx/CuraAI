#!/usr/bin/env python3
"""
Test script for multiple API key functionality
Run this to verify your API keys are working correctly
"""

import os
import sys
from dotenv import load_dotenv

def test_api_keys():
    """Test if API keys are properly configured"""
    load_dotenv()
    
    print("🔍 Testing API Key Configuration...")
    print("=" * 50)
    
    # Check for multiple API keys
    api_keys = []
    i = 1
    while True:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if not key:
            # Check for single key format
            if i == 1:
                key = os.getenv("GEMINI_API_KEY")
            if not key:
                break
        api_keys.append(key)
        i += 1
    
    if not api_keys:
        print("❌ No API keys found!")
        print("Please set GEMINI_API_KEY or GEMINI_API_KEY_1 in your environment variables")
        return False
    
    print(f"✅ Found {len(api_keys)} API key(s)")
    
    for i, key in enumerate(api_keys, 1):
        # Mask the key for security
        masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
        print(f"   Key {i}: {masked_key}")
    
    if len(api_keys) > 1:
        print("\n🎯 Multiple API keys detected - Fallback mode enabled!")
        print("   The app will automatically switch to the next key if one fails")
    else:
        print("\n⚠️  Single API key detected")
        print("   Consider adding backup keys for better reliability")
    
    print("\n📋 Next Steps:")
    print("   1. Deploy to Render with these environment variables")
    print("   2. Monitor the /health endpoint for API key status")
    print("   3. Check logs for fallback events")
    
    return True

if __name__ == "__main__":
    success = test_api_keys()
    sys.exit(0 if success else 1) 