# test_integration.py
from enhanced_paper_dashboard import EnhancedPaperDashboard
from opportunity_scanner import OpportunityScanner
from jax_engine import JAXRealTimeAnalytics
import logging

logging.basicConfig(level=logging.INFO)

def test_integration():
    print("🧪 INTEGRATION TEST - All Fixes")
    print("=" * 50)
    
    # Test 1: Dashboard
    dashboard = EnhancedPaperDashboard()
    print("✅ Dashboard initialized")
    
    # Test 2: Scanner with mock data
    jax_analytics = JAXRealTimeAnalytics()
    scanner = OpportunityScanner(jax_analytics)
    opportunities = scanner.scan_opportunities()
    print(f"✅ Scanner found {len(opportunities)} opportunities")
    
    # Test 3: Alert system
    class MockAlert:
        def __init__(self, message, level):
            self.message = message
            self.alert_level = level
    
    # Test different alert levels
    test_alerts = [
        MockAlert("Low risk alert", 2),
        MockAlert("Medium risk alert", 5), 
        MockAlert("High risk alert", 8)
    ]
    
    for alert in test_alerts:
        dashboard.send_dual_alert(alert, 'paper')
    
    print("✅ All integration tests passed!")
    print("🎉 System is ready for 24/7 paper trading!")

if __name__ == "__main__":
    test_integration()