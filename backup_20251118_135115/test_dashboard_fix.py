# test_dashboard_fix.py
from enhanced_paper_dashboard import EnhancedPaperDashboard
import logging

logging.basicConfig(level=logging.INFO)

def test_dashboard_fix():
    print("🧪 Testing Dashboard Fix...")
    
    # Create dashboard instance
    dashboard = EnhancedPaperDashboard()
    
    # Create a mock alert object (simulating what the risk monitor sends)
    class MockAlert:
        def __init__(self):
            self.message = "Test alert - dashboard working!"
            self.alert_level = 3
    
    # Test the fixed method
    alert = MockAlert()
    dashboard.send_dual_alert(alert, 'paper')
    
    print("✅ Dashboard fix verified!")

if __name__ == "__main__":
    test_dashboard_fix()