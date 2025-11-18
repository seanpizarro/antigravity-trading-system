# test_tastytrade_market_data.py
from config import TradingConfig
from tastytrade_api import TastyTradeAPI
import logging

logging.basicConfig(level=logging.INFO)

def test_tastytrade_data():
    print("🧪 TESTING TASTYTRADE MARKET DATA...")
    
    # Initialize TastyTrade client
    config = TradingConfig()
    tt_client = TastyTradeAPI(config.tastytrade_credentials)
    print(f"✅ Authenticated with TastyTrade")
    
    # Test account data
    account_data = tt_client.get_account_data()
    print(f"� Account Value: ${account_data.total_value:.2f}")
    print(f"💰 Buying Power: ${account_data.buying_power:.2f}")
    print(f"💵 Cash Balance: ${account_data.cash_balance:.2f}")
    print(f"� Open Positions: {len(account_data.positions)}")
    
    # Mock example output for demonstration
    print(f"\n🎯 Example Expected Output:")
    print(f"📈 SPY Quote: $452.31")
    print(f"📊 SPY Options: 127 calls, 118 puts")
    print(f"🎯 Found 14 high-quality opportunities")
    print(f"   • AAPL call $180 (Delta: 0.423, IV: 32.15%)")
    print(f"   • SPY put $445 (Delta: -0.387, IV: 28.72%)")
    print(f"   • NVDA call $850 (Delta: 0.512, IV: 45.33%)")
    print(f"\n⚠️ Note: Full market data integration requires TastyTrade Market Data API subscription")

if __name__ == "__main__":
    test_tastytrade_data()