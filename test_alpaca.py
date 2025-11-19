# test_alpaca.py - Test Alpaca API Integration
import os
import sys
import logging
from config import TradingConfig

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpaca_api import AlpacaAPI

def test_alpaca_connection():
    """Test Alpaca API connection and basic functionality"""
    print("🔄 Testing Alpaca API Integration...")

    # Load configuration
    config = TradingConfig()

    if not config.alpaca_credentials:
        print("❌ No Alpaca credentials found in environment")
        return False

    try:
        # Initialize Alpaca API (uses environment variables)
        alpaca = AlpacaAPI()

        print("✅ Alpaca API initialized successfully")

        # Test account info
        print("📊 Getting account information...")
        balances = alpaca.get_account_balances()
        print(f"   Cash: ${balances.get('cash_balance', 0):,.2f}")
        print(f"   Portfolio Value: ${balances.get('net_liquidating_value', 0):,.2f}")
        print(f"   Buying Power: ${balances.get('maintenance_excess', 0):,.2f}")

        # Test market clock
        print("🕐 Market is currently:", "Open" if alpaca.is_market_open() else "Closed")

        # Test getting positions
        print("📈 Getting positions...")
        positions = alpaca.get_positions()
        print(f"   Found {len(positions)} positions")

        if positions:
            for pos_id, pos in list(positions.items())[:3]:  # Show first 3 positions
                print(f"   {pos.get('symbol', 'N/A')}: {pos.get('quantity', 0)} @ ${pos.get('average_open_price', 0):.2f}")

        print("✅ Alpaca API test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Alpaca API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    success = test_alpaca_connection()
    sys.exit(0 if success else 1)