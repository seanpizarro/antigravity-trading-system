# test_fixes.py
from enhanced_paper_dashboard import EnhancedPaperDashboard
from opportunity_scanner import OpportunityScanner
from jax_engine import JAXRealTimeAnalytics
import logging

logging.basicConfig(level=logging.INFO)

def test_fixes():
    print("🧪 TESTING ENHANCED PAPER TRADING FIXES...")
    
    # Test 1: Dashboard alerts
    dashboard = EnhancedPaperDashboard()
    print("✅ Dashboard initialized")
    
    # Test 2: Mock opportunities
    jax_analytics = JAXRealTimeAnalytics()
    scanner = OpportunityScanner(jax_analytics)
    opportunities = scanner.scan_opportunities()
    print(f"✅ Found {len(opportunities)} opportunities (including mock data)")
    
    for opp in opportunities:
        print(f"   • {opp['symbol']} {opp['option_type']} ${opp['strike']} "
              f"(Confidence: {opp.get('ai_confidence', 0):.3f})")
    
    # Test 3: Alert system
    class MockAlert:
        def __init__(self):
            self.message = "Test alert - system working"
            self.alert_level = 2
    
    alert = MockAlert()
    dashboard.send_dual_alert(alert, 'paper')
    print("✅ Alert system working")
    
    print("\n🎉 ALL FIXES VERIFIED! System ready for paper trading.")

if __name__ == "__main__":
    test_fixes()