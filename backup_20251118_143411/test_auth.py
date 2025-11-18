"""Test TastyTrade authentication"""
from config import TradingConfig
from tastytrade_api import TastyTradeAPI

try:
    config = TradingConfig()
    print("Config loaded successfully")
    print(f"Account: {config.tastytrade_credentials.get('account')}")
    
    api = TastyTradeAPI(config.tastytrade_credentials)
    print("✓ Authentication successful!")
    
except Exception as e:
    print(f"✗ Error: {e}")
