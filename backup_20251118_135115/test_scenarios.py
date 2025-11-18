# test_scenarios.py
"""
Test different market scenarios for mock opportunity generation
"""
from opportunity_scanner import OpportunityScanner
from jax_engine import JAXRealTimeAnalytics

def test_multiple_scenarios():
    """Run multiple tests to see different market scenarios"""
    print("\n" + "="*70)
    print("🎭 TESTING MULTIPLE MARKET SCENARIOS")
    print("="*70)
    
    jax_engine = JAXRealTimeAnalytics()
    scanner = OpportunityScanner(jax_engine)
    
    # Run 5 iterations to see different scenarios
    for run in range(1, 6):
        print(f"\n{'='*70}")
        print(f"RUN #{run}")
        print("="*70)
        
        opportunities = scanner._create_mock_opportunities()
        
        if opportunities:
            scenario = opportunities[0].get('scenario', 'unknown')
            print(f"\n🎯 SCENARIO: {scenario.upper()}")
            
            # Count option types
            calls = sum(1 for o in opportunities if o['option_type'] == 'call')
            puts = sum(1 for o in opportunities if o['option_type'] == 'put')
            
            print(f"📊 Mix: {calls} calls / {puts} puts")
            print(f"💰 Avg Premium: ${sum(o['premium'] for o in opportunities) / len(opportunities):.2f}")
            print(f"📈 Avg IV: {sum(o['implied_volatility'] for o in opportunities) / len(opportunities):.1f}%")
            
            print("\n📋 OPPORTUNITIES:")
            for i, opp in enumerate(opportunities, 1):
                option_emoji = "📞" if opp['option_type'] == 'call' else "📉"
                print(f"   {i}. {option_emoji} {opp['symbol']} ${opp['strike']:.2f} {opp['option_type'].upper()}")
                print(f"      Strategy: {opp['strategy']} | Premium: ${opp['premium']:.2f}")
                print(f"      IV: {opp['implied_volatility']}% | DTE: {opp['days_to_expiration']} days")
                print(f"      Underlying: ${opp['underlying_price']:.2f}")
    
    print("\n" + "="*70)
    print("✅ Scenario testing complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_multiple_scenarios()
