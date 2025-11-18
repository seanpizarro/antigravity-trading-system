# test_market_integration.py
"""
Test market hours integration and automatic mock data fallback
"""
from market_utils import is_market_open, format_market_status
from opportunity_scanner import OpportunityScanner
from jax_engine import JAXRealTimeAnalytics

def test_integration():
    """Test market hours detection and opportunity scanning integration"""
    print("\n" + "="*70)
    print("🧪 TESTING MARKET HOURS INTEGRATION")
    print("="*70)
    
    # Show detailed market status
    print(f"\n{format_market_status()}")
    print(f"Market Open: {is_market_open()}")
    
    # Initialize scanner
    print("\n🔧 Initializing OpportunityScanner...")
    jax_engine = JAXRealTimeAnalytics()
    scanner = OpportunityScanner(jax_engine)
    
    # Scan for opportunities
    print("\n🔍 Scanning for opportunities...")
    opportunities = scanner.scan_opportunities()
    
    # Display results
    print(f"\n✅ Found {len(opportunities)} opportunities")
    print("="*70)
    
    if opportunities:
        for i, opp in enumerate(opportunities, 1):
            # Determine if this is mock or live data
            is_mock = opp.get('mock_data', False)
            market_flag = "🧪 MOCK" if is_mock else "📡 LIVE"
            
            print(f"\n{i}. {market_flag} OPPORTUNITY:")
            print(f"   Symbol: {opp['symbol']}")
            print(f"   Strategy: {opp['strategy']}")
            print(f"   Premium: ${opp['premium']:.2f}")
            print(f"   Type: {opp.get('option_type', 'N/A')}")
            print(f"   Strike: ${opp.get('strike', 0):.2f}")
            print(f"   DTE: {opp.get('days_to_expiration', 0)} days")
            
            # Show additional mock data flags
            if is_mock:
                print(f"   🎭 Mock Data Indicators:")
                print(f"      - AI Confidence: {opp.get('ai_confidence', 0):.1%}")
                print(f"      - Volume: {opp.get('volume', 0):,}")
    else:
        print("❌ No opportunities found")
    
    print("\n" + "="*70)
    print("✅ Integration test complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_integration()
