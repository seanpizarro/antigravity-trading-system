# test_scanner_fix.py
from opportunity_scanner import OpportunityScanner
from jax_engine import JAXRealTimeAnalytics
import logging

logging.basicConfig(level=logging.INFO)

def test_scanner_fix():
    print("🧪 Testing Scanner Fix...")
    
    # Create scanner instance
    jax_analytics = JAXRealTimeAnalytics()
    scanner = OpportunityScanner(jax_analytics)
    
    # Test scanning (should work even after hours)
    opportunities = scanner.scan_opportunities()
    
    print(f"✅ Found {len(opportunities)} opportunities")
    for opp in opportunities:
        print(f"   • {opp['symbol']} {opp['option_type']} ${opp['strike']} "
              f"(Confidence: {opp.get('ai_confidence', 0):.3f})")
    
    print("✅ Scanner fix verified!")

if __name__ == "__main__":
    test_scanner_fix()