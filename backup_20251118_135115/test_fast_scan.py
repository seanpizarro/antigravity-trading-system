# test_fast_scan.py
from hybrid_market_data import HybridMarketData
from config import TradingConfig
from tastytrade_api import TastyTradeAPI
import logging
import time

logging.basicConfig(level=logging.INFO)

def test_fast_scan():
    print("⚡ TESTING OPTIMIZED FAST SCAN...")
    start_time = time.time()
    
    config = TradingConfig()
    tt_client = TastyTradeAPI(config.tastytrade_credentials)
    hybrid = HybridMarketData(tt_client)
    
    # Test fast scanning
    opportunities = hybrid.scan_opportunities_fast()
    
    total_time = time.time() - start_time
    print(f"✅ FAST SCAN COMPLETE: {len(opportunities)} opportunities in {total_time:.1f}s")
    
    for opp in opportunities[:3]:
        print(f"   • {opp['symbol']} {opp['option_type']} ${opp['strike']} "
              f"(Premium: ${opp['premium']}, Vol: {opp['volume']})")
    
    # Test quick summary
    summary = hybrid.get_quick_market_summary()
    print(f"🌐 Quick Summary: SPY ${summary.get('SPY', {}).get('price', 0)}")

if __name__ == "__main__":
    test_fast_scan()