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
        # Initialize Alpaca API
        alpaca = AlpacaAPI(
            api_key=config.alpaca_credentials['api_key'],
            api_secret=config.alpaca_credentials['api_secret'],
            base_url=config.alpaca_credentials['base_url']
        )

        print("✅ Alpaca API initialized successfully")

        # Test account info
        print("📊 Getting account information...")
        account = alpaca.get_account()
        print(f"   Account ID: {account.account_id}")
        print(".2f")
        print(".2f")
        print(f"   Status: {account.status}")

        # Test market clock
        print("🕐 Checking market status...")
        clock = alpaca.get_clock()
        if clock:
            print(f"   Market Open: {clock.get('is_open', 'Unknown')}")
            print(f"   Next Open: {clock.get('next_open', 'Unknown')}")
            print(f"   Next Close: {clock.get('next_close', 'Unknown')}")

        # Test getting positions
        print("📈 Getting positions...")
        positions = alpaca.get_positions()
        print(f"   Found {len(positions)} positions")

        if positions:
            for pos in positions[:3]:  # Show first 3 positions
                print(f"   {pos.symbol}: {pos.qty} @ ${pos.avg_entry_price:.2f} (P&L: ${pos.unrealized_pl:.2f})")

        # Test getting a quote
        print("💰 Getting SPY quote...")
        quote = alpaca.get_quote('SPY')
        if quote:
            print(f"   SPY Ask: ${quote.get('askprice', 'N/A')}, Bid: ${quote.get('bidprice', 'N/A')}")

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