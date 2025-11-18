"""Test TastyTrade API account data"""
from config import TradingConfig
from tastytrade_api import TastyTradeAPI

try:
    config = TradingConfig()
    api = TastyTradeAPI(config.tastytrade_credentials)
    print("✓ Authentication successful!")
    
    account_data = api.get_account_data()
    print(f"\n✓ Account data fetched:")
    print(f"  Total Value: ${account_data.total_value:,.2f}")
    print(f"  Buying Power: ${account_data.buying_power:,.2f}")
    print(f"  Cash Balance: ${account_data.cash_balance:,.2f}")
    print(f"  Positions: {len(account_data.positions)}")
    
    if account_data.positions:
        print(f"\n  Position details:")
        for pos in account_data.positions:
            print(f"    - {pos.get('symbol', 'N/A')}: {pos.get('quantity', 0)} qty")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
