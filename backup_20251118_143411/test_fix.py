# save_as: test_fix.py
try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    print("✅ Email imports fixed successfully!")
    
    # Test the dashboard import
    from dashboard import RealTimeDashboard
    print("✅ Dashboard import works now!")
    
except ImportError as e:
    print(f"❌ Still having issues: {e}")