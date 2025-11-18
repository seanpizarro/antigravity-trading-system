#!/usr/bin/env python3
"""
Test script for Composer MCP Bridge
Validates that the bridge correctly handles MCP-style requests.
"""
import json
import subprocess
import sys
import os

def test_bridge(action: str, payload: dict = None):
    """Test the MCP bridge with a specific action"""
    print(f"\n🧪 Testing action: {action}")
    print(f"   Payload: {payload or '{}'}")
    
    request = {
        "tool": "composer",
        "action": action,
        "payload": payload or {}
    }
    
    try:
        proc = subprocess.run(
            [sys.executable, "composer_mcp_bridge.py"],
            input=json.dumps(request).encode("utf-8"),
            capture_output=True,
            timeout=15
        )
        
        # Parse response
        try:
            response = json.loads(proc.stdout.decode("utf-8"))
        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON response: {e}")
            print(f"   stdout: {proc.stdout.decode('utf-8', errors='ignore')}")
            print(f"   stderr: {proc.stderr.decode('utf-8', errors='ignore')}")
            return False
        
        # Check result
        if response.get("ok"):
            print(f"   ✅ Success")
            result = response.get("result")
            if isinstance(result, list):
                print(f"   Result: {len(result)} items")
            elif isinstance(result, dict):
                print(f"   Result keys: {list(result.keys())[:5]}")
            else:
                print(f"   Result: {result}")
            return True
        else:
            error = response.get("error", "Unknown error")
            print(f"   ⚠️  Error: {error}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout (>15s)")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def main():
    """Run MCP bridge tests"""
    print("=" * 60)
    print("Composer MCP Bridge Test Suite")
    print("=" * 60)
    
    # Check environment
    has_firebase = bool(os.getenv("COMPOSER_FIREBASE_TOKEN"))
    has_api_key = bool(os.getenv("COMPOSER_API_KEY") and os.getenv("COMPOSER_API_SECRET"))
    
    print(f"\n🔐 Authentication Status:")
    print(f"   Firebase Token: {'✅ Set' if has_firebase else '❌ Missing'}")
    print(f"   API Key/Secret: {'✅ Set' if has_api_key else '❌ Missing'}")
    
    if not (has_firebase or has_api_key):
        print("\n❌ No authentication configured. Set environment variables:")
        print("   COMPOSER_FIREBASE_TOKEN or")
        print("   COMPOSER_API_KEY + COMPOSER_API_SECRET")
        sys.exit(1)
    
    # Run tests
    results = []
    
    # Test 1: accounts.list
    results.append(test_bridge("accounts.list"))
    
    # Test 2: accounts.holdings (if we have an account ID)
    account_id = os.getenv("COMPOSER_ACCOUNT_ID")
    if account_id:
        results.append(test_bridge("accounts.holdings", {"account_id": account_id}))
    else:
        print(f"\n⏭️  Skipping accounts.holdings test (no COMPOSER_ACCOUNT_ID)")
    
    # Test 3: market.options_overview
    results.append(test_bridge("market.options_overview", {"symbol": "SPY"}))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed or returned errors")
        print("\nNote: 403 errors usually mean authentication issues.")
        print("Make sure your credentials are valid and have the right permissions.")
        sys.exit(1)


if __name__ == "__main__":
    main()
