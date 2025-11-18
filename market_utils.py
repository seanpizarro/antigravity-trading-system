# market_utils.py
"""
Market hours and trading utilities
"""
import pytz
from datetime import datetime, time

def is_market_open():
    """Check if US stock markets are currently open"""
    try:
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        
        # Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        # Check if weekend
        if now.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return False
            
        # Check if within market hours
        return market_open <= now.time() <= market_close
    except Exception as e:
        print(f"⚠️ Error checking market hours: {e}")
        return False  # Default to closed if error

def get_market_status():
    """Get detailed market status information"""
    try:
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        
        market_open_time = time(9, 30)
        market_close_time = time(16, 0)
        
        is_weekend = now.weekday() >= 5
        is_open = is_market_open()
        
        status = {
            'is_open': is_open,
            'is_weekend': is_weekend,
            'current_time_et': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'weekday': now.strftime('%A'),
            'market_opens_at': '09:30 ET',
            'market_closes_at': '16:00 ET'
        }
        
        # Add time until open/close
        if is_open:
            close_datetime = now.replace(hour=16, minute=0, second=0, microsecond=0)
            time_until_close = (close_datetime - now).total_seconds() / 60
            status['minutes_until_close'] = int(time_until_close)
        elif not is_weekend:
            if now.time() < market_open_time:
                open_datetime = now.replace(hour=9, minute=30, second=0, microsecond=0)
                time_until_open = (open_datetime - now).total_seconds() / 60
                status['minutes_until_open'] = int(time_until_open)
        
        return status
    except Exception as e:
        return {
            'is_open': False,
            'error': str(e)
        }

def format_market_status():
    """Get a formatted string of market status"""
    status = get_market_status()
    
    if status.get('error'):
        return f"⚠️ Error checking market: {status['error']}"
    
    if status['is_weekend']:
        return f"🌙 Markets Closed - {status['weekday']} (Weekend)"
    elif status['is_open']:
        mins = status.get('minutes_until_close', 0)
        return f"📈 Markets Open - Closes in {mins} minutes"
    else:
        mins = status.get('minutes_until_open', 0)
        if mins > 0:
            return f"🌙 Markets Closed - Opens in {mins} minutes"
        else:
            return f"🌙 Markets Closed - {status['current_time_et']}"
