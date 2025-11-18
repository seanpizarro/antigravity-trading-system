# test_after_hours.py
from opportunity_scanner import OpportunityScanner
from jax_engine import JAXRealTimeAnalytics

def test_after_hours():
    # Initialize scanner with required JAX engine
    jax_engine = JAXRealTimeAnalytics()
    scanner = OpportunityScanner(jax_engine)
    
    print("🌙 AFTER-HOURS TEST MODE")
    print("Generating mock opportunities...")
    
    opportunities = scanner._create_mock_opportunities()
    
    print(f"\n🎯 Found {len(opportunities)} mock opportunities:")
    print("="*70)
    for opp in opportunities:
        symbol = opp.get('symbol', 'N/A')
        strategy = opp.get('strategy', 'N/A')
        premium = opp.get('premium', 0)
        option_type = opp.get('option_type', 'N/A')
        strike = opp.get('strike', 0)
        expiration = opp.get('expiration', 'N/A')
        reason = opp.get('reason', 'No reason provided')
        
        print(f"📊 {symbol} {option_type.upper()} @ ${strike}")
        print(f"   Strategy: {strategy}")
        print(f"   Premium: ${premium:.2f}")
        print(f"   Expires: {expiration}")
        print(f"   Reason: {reason}")
        print("-"*70)

if __name__ == "__main__":
    test_after_hours()
