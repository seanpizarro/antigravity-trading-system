# test_multi_broker.py - Test Multi-Broker API Integration
import os
import sys
import logging
from multi_broker_api import MultiBrokerAPI

def test_multi_broker():
    """Test multi-broker API functionality"""
    print("🔄 Testing Multi-Broker API Integration...")

    try:
        # Initialize multi-broker API
        api = MultiBrokerAPI()
        print("✅ Multi-Broker API initialized")

        # Check available brokers
        available_brokers = api.get_available_brokers()
        print(f"📊 Available brokers: {available_brokers}")

        if not available_brokers:
            print("❌ No brokers available")
            return False

        # Test active broker
        active_broker = api.get_active_broker()
        print(f"🎯 Active broker: {active_broker}")

        # Test account info
        print("📊 Getting account information...")
        account = api.get_account_info()
        if account:
            print(f"   Broker: {account.broker}")
            print(f"   Account ID: {account.account_id}")
            print(".2f")
            print(".2f")
            print(f"   Status: {account.status}")
            print(f"   Paper Account: {account.is_paper}")
        else:
            print("   ❌ Failed to get account info")

        # Test positions
        print("📈 Getting positions...")
        positions = api.get_positions()
        print(f"   Found {len(positions)} positions")

        if positions:
            for pos in positions[:3]:  # Show first 3 positions
                print(f"   {pos.symbol}: {pos.quantity} @ ${pos.avg_entry_price:.2f} (P&L: ${pos.unrealized_pl:.2f})")

        # Test market status
        print("🕐 Checking market status...")
        is_open = api.is_market_open()
        print(f"   Market Open: {is_open}")

        # Test broker switching if multiple brokers available
        if len(available_brokers) > 1:
            print("🔄 Testing broker switching...")
            for broker in available_brokers:
                if broker != active_broker:
                    success = api.switch_broker(broker)
                    if success:
                        print(f"   ✅ Switched to {broker}")
                        new_active = api.get_active_broker()
                        print(f"   Active broker now: {new_active}")
                        # Switch back
                        api.switch_broker(active_broker)
                        break

        print("✅ Multi-Broker API test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Multi-Broker API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    success = test_multi_broker()
    sys.exit(0 if success else 1)