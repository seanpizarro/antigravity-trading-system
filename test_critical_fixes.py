# test_critical_fixes.py
from enhanced_paper_trading import EnhancedPaperTradingEngine
from tastytrade_api import TastyTradeAPI
import logging

logging.basicConfig(level=logging.INFO)

def test_critical_fixes():
    print("🧪 TESTING CRITICAL FIXES...")
    
    tt = TastyTradeAPI(sandbox=True)
    engine = EnhancedPaperTradingEngine(tt)
    
    # Test with complete opportunity data
    test_opportunity = {
        'symbol': 'QQQ',
        'option_type': 'call',
        'strike': 440.0,
        'underlying_price': 445.21,
        'premium': 2.15,  # Now provided
        'volume': 1500,
        'open_interest': 2500,
        'implied_volatility': 15.5,
        'ai_confidence': 0.72,
        'data_source': 'test'
    }
    
    result = engine.execute_paper_trade(test_opportunity)
    
    if result.get('success'):
        position_data = result.get('position_data', {})
        print("✅ SUCCESS: Trade executed with complete data")
        print(f"   Position ID: {position_data.get('position_id')}")
        print(f"   Entry Time: {position_data.get('entry_time')}")
        print(f"   Underlying Price: {position_data.get('underlying_price')}")
        print(f"   Ticker: {position_data.get('ticker')}")
    else:
        print(f"❌ FAILED: {result.get('error')}")

if __name__ == "__main__":
    test_critical_fixes()
