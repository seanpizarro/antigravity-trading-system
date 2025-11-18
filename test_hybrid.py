#!/usr/bin/env python3
"""Test the hybrid market data system"""
from hybrid_market_data import HybridMarketData
from config import TradingConfig
from tastytrade_api import TastyTradeAPI
import logging

logging.basicConfig(level=logging.INFO)

def test_hybrid_data():
    print("🧪 TESTING HYBRID MARKET DATA SYSTEM...")
    
    # Initialize with TastyTrade client for account data
    config = TradingConfig()
    tt_client = TastyTradeAPI(config.tastytrade_credentials)
    
    # Create hybrid data instance
    hybrid = HybridMarketData(tt_client)
    print("✅ Hybrid Market Data initialized")
    
    # Test quote (uses yfinance - free)
    print("\n📈 Testing Quote Data (yfinance)...")
    spy_quote = hybrid.get_quote('SPY')
    if spy_quote:
        print(f"   SPY: ${spy_quote['price']} ({spy_quote['change']:+.2f}%)")
        print(f"   Source: {spy_quote['data_source']}")
    
    # Test options chain (uses yfinance - free)
    print("\n📊 Testing Options Chain (yfinance)...")
    spy_options = hybrid.get_options_chain('SPY')
    if spy_options:
        print(f"   SPY Options: {spy_options.get('total_calls', 0)} calls, {spy_options.get('total_puts', 0)} puts")
        print(f"   Underlying: ${spy_options.get('underlying_price', 0)}")
    
    # Test account data (uses TastyTrade - real)
    print("\n💰 Testing Account Data (TastyTrade)...")
    account = hybrid.get_account_data()
    if account:
        print(f"   Account Value: ${account.get('total_value', 0):.2f}")
        print(f"   Buying Power: ${account.get('buying_power', 0):.2f}")
        print(f"   Positions: {account.get('positions', 0)}")
    
    # Test market summary
    print("\n📊 Testing Market Summary...")
    summary = hybrid.get_market_summary()
    if summary:
        spy = summary.get('quotes', {}).get('SPY', {})
        print(f"   SPY: ${spy.get('price', 0)}")
        vix = summary.get('volatility', {}).get('vix', 0)
        print(f"   VIX: {vix}")
        print(f"   Account: ${summary.get('account', {}).get('total_value', 0):.2f}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_hybrid_data()
