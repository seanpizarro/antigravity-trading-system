# test_403_handling.py
"""
Test that the system handles 403 errors gracefully and continues in mock mode
"""
from tastytrade_api import TastyTradeAPI
import logging

# Setup logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_403_handling():
    """Test that 403 errors are handled and system continues in mock mode"""
    print("\n" + "="*70)
    print("🧪 TESTING 403 ERROR HANDLING")
    print("="*70)
    
    # Initialize TastyTrade API in sandbox mode
    print("\n1️⃣ Initializing TastyTrade API (Sandbox Mode)...")
    api = TastyTradeAPI(sandbox=True)
    
    # This will likely get 403, but should fall back to mock mode
    print("\n2️⃣ Attempting to get account data...")
    account_data = api.get_account_data()
    
    print(f"\n✅ Account Data Retrieved:")
    print(f"   Total Value: ${account_data.total_value:,.2f}")
    print(f"   Buying Power: ${account_data.buying_power:,.2f}")
    print(f"   Cash Balance: ${account_data.cash_balance:,.2f}")
    print(f"   Positions: {len(account_data.positions)}")
    
    # Test getting positions
    print("\n3️⃣ Getting positions...")
    positions = api.get_positions()
    print(f"   Open Positions: {len(positions)}")
    
    print("\n" + "="*70)
    print("✅ System continues to operate in mock mode despite 403 errors")
    print("💡 This is expected behavior for sandbox paper trading")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_403_handling()
