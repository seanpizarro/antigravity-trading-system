# test_integrated_system.py
from tastytrade_api import TastyTradeAPI
from paper_trading import PaperTradingEngine
import logging

logging.basicConfig(level=logging.INFO)

def test_integrated_system():
    print("🧪 TESTING INTEGRATED PAPER TRADING SYSTEM...")
    
    # Initialize with sandbox mode (safe)
    tt_client = TastyTradeAPI(sandbox=True)
    
    # Test account data
    account_data = tt_client.get_account_data()
    print(f"✅ Account Data: ${account_data.total_value:.2f}")
    
    # Test paper trading engine
    paper_engine = PaperTradingEngine(tt_client)
    
    # Test portfolio
    portfolio = paper_engine.get_portfolio_summary()
    print(f"💰 Paper Portfolio: ${portfolio.get('total_value', 0):.2f}")
    
    # Test paper trade
    test_signal = {
        'symbol': 'SPY',
        'option_type': 'call', 
        'strike': 685,
        'premium': 2.15,
        'ai_confidence': 0.78
    }
    
    result = paper_engine.execute_paper_trade(test_signal)
    print(f"📝 Paper Trade Result: {result.get('success', False)}")
    
    if result.get('success'):
        print(f"   Trade ID: {result.get('trade_id')}")
        print(f"   Symbol: {result.get('symbol')}")
        print(f"   Quantity: {result.get('quantity')}")

if __name__ == "__main__":
    test_integrated_system()