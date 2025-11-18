# test_hybrid_system.py
from hybrid_market_data import HybridMarketData
from config import TradingConfig
from tastytrade_api import TastyTradeAPI
import logging

logging.basicConfig(level=logging.INFO)

def test_hybrid_system():
    print("🧪 TESTING HYBRID MARKET DATA SYSTEM...")
    
    # Initialize TastyTrade client
    config = TradingConfig()
    tt_client = TastyTradeAPI(config.tastytrade_credentials)
    hybrid = HybridMarketData(tt_client)
    
    # Test REAL account data (this works!)
    account_data = hybrid.get_account_data()
    print(f"✅ REAL Account Data: ${account_data.get('total_value', 0):.2f}")
    
    # Test free market data
    spy_quote = hybrid.get_quote('SPY')
    print(f"📈 SPY Quote: ${spy_quote.get('price', 0)} (via yfinance)")
    
    # Test options chain
    spy_chain = hybrid.get_options_chain('SPY')
    print(f"📊 SPY Options: {spy_chain.get('total_calls', 0)} calls, {spy_chain.get('total_puts', 0)} puts")
    
    # Test opportunity scanning
    opportunities = hybrid.scan_opportunities()
    print(f"🎯 Found {len(opportunities)} hybrid opportunities")
    
    for opp in opportunities[:3]:
        print(f"   • {opp['symbol']} {opp['option_type']} ${opp['strike']} "
              f"(Premium: ${opp['premium']}, IV: {opp['implied_volatility']}%)")
    
    # Test market summary
    summary = hybrid.get_market_summary()
    print(f"🌐 Market Summary: {len(summary)} components")

if __name__ == "__main__":
    test_hybrid_system()