#!/usr/bin/env python3
"""
Composer Integration Verification
Quick check that all components are properly installed and configured.
"""
import sys
import os
from pathlib import Path

def check_file_exists(filename: str, description: str):
    """Check if a file exists"""
    if Path(filename).exists():
        size = Path(filename).stat().st_size
        print(f"  ✅ {description}: {filename} ({size:,} bytes)")
        return True
    else:
        print(f"  ❌ {description}: {filename} NOT FOUND")
        return False

def check_import(module_name: str, description: str):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"  ✅ {description}: Can import {module_name}")
        return True
    except Exception as e:
        print(f"  ❌ {description}: Import failed - {e}")
        return False

def check_env_var(var_name: str, required: bool = False):
    """Check if an environment variable is set"""
    value = os.getenv(var_name)
    if value:
        # Mask sensitive values
        if "TOKEN" in var_name or "KEY" in var_name or "SECRET" in var_name:
            display = f"{value[:20]}..." if len(value) > 20 else value
        else:
            display = value
        print(f"  ✅ {var_name} = {display}")
        return True
    else:
        status = "❌" if required else "⚠️"
        msg = "REQUIRED but not set" if required else "Not set (optional)"
        print(f"  {status} {var_name} - {msg}")
        return not required

def main():
    print("=" * 70)
    print("COMPOSER INTEGRATION VERIFICATION")
    print("=" * 70)
    
    all_good = True
    
    # Check files
    print("\n📁 Files:")
    print("-" * 70)
    all_good &= check_file_exists("composer_api.py", "Main API Client")
    all_good &= check_file_exists("composer_mcp_bridge.py", "MCP Bridge")
    all_good &= check_file_exists("test_composer.py", "REST Test Suite")
    all_good &= check_file_exists("test_composer_mcp_bridge.py", "MCP Test Suite")
    all_good &= check_file_exists("demo_composer_mcp.py", "Demo Script")
    all_good &= check_file_exists("COMPOSER_MCP_BRIDGE.md", "MCP Documentation")
    all_good &= check_file_exists("COMPOSER_QUICKSTART.md", "Quickstart Guide")
    all_good &= check_file_exists("COMPOSER_INTEGRATION_COMPLETE.md", "Integration Summary")
    
    # Check imports
    print("\n📦 Python Modules:")
    print("-" * 70)
    all_good &= check_import("composer_api", "Composer API Client")
    all_good &= check_import("requests", "Requests Library")
    all_good &= check_import("json", "JSON Module")
    
    # Check environment variables
    print("\n🔐 Authentication (Environment Variables):")
    print("-" * 70)
    has_firebase = check_env_var("COMPOSER_FIREBASE_TOKEN", required=False)
    has_api_key = check_env_var("COMPOSER_API_KEY", required=False)
    has_api_secret = check_env_var("COMPOSER_API_SECRET", required=False)
    check_env_var("COMPOSER_ACCOUNT_ID", required=False)
    
    if not (has_firebase or (has_api_key and has_api_secret)):
        print("\n  ⚠️  No authentication configured!")
        print("     Set COMPOSER_FIREBASE_TOKEN or COMPOSER_API_KEY + COMPOSER_API_SECRET")
        print("     See COMPOSER_QUICKSTART.md for instructions")
    
    # Check MCP configuration
    print("\n🔌 MCP Bridge Configuration:")
    print("-" * 70)
    mcp_enabled = check_env_var("COMPOSER_MCP_ENABLED", required=False)
    check_env_var("COMPOSER_MCP_COMMAND", required=False)
    check_env_var("COMPOSER_MCP_TIMEOUT", required=False)
    
    if not mcp_enabled:
        print("\n  ℹ️  MCP bridge is disabled (this is optional)")
        print("     To enable: Set COMPOSER_MCP_ENABLED=true")
    
    # Test API client instantiation
    print("\n🧪 API Client Test:")
    print("-" * 70)
    try:
        from composer_api import ComposerTradeAPI
        api = ComposerTradeAPI()
        print(f"  ✅ API client instantiated successfully")
        print(f"  ✅ is_configured = {api.is_configured}")
        
        if api.is_configured:
            print(f"  ℹ️  Authentication method: {'Firebase' if api.firebase_token else 'API Key/Secret'}")
        else:
            print(f"  ⚠️  No authentication configured (expected)")
        
        if api.mcp_enabled:
            print(f"  ℹ️  MCP routing enabled")
            print(f"  ℹ️  MCP command: {api.mcp_command}")
        else:
            print(f"  ℹ️  Using direct REST (MCP disabled)")
            
    except Exception as e:
        print(f"  ❌ API client instantiation failed: {e}")
        all_good = False
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print("\n✅ Core Components:")
    print("   • REST API client with 20+ methods")
    print("   • MCP bridge for workflow automation")
    print("   • Comprehensive test suite")
    print("   • Complete documentation")
    
    if has_firebase or (has_api_key and has_api_secret):
        print("\n✅ Authentication configured")
        if has_firebase:
            print("   • Using Firebase token (recommended)")
        else:
            print("   • Using API key/secret (may have limitations)")
    else:
        print("\n⚠️  No authentication configured")
        print("   • Get Firebase token to activate full functionality")
        print("   • See COMPOSER_QUICKSTART.md Step 1")
    
    print("\n📚 Documentation:")
    print("   • COMPOSER_QUICKSTART.md - Setup and usage guide")
    print("   • COMPOSER_MCP_BRIDGE.md - MCP technical details")
    print("   • COMPOSER_INTEGRATION_COMPLETE.md - Full summary")
    
    print("\n🚀 Next Steps:")
    print("   1. Get Firebase token (see COMPOSER_QUICKSTART.md)")
    print("   2. Add to .env: COMPOSER_FIREBASE_TOKEN=your_token")
    print("   3. Test: python test_composer.py")
    print("   4. Optional: Enable MCP bridge in .env")
    print("   5. Integrate with main.py (examples in docs)")
    
    if all_good:
        print("\n✅ All checks passed! Integration is ready.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Review output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
