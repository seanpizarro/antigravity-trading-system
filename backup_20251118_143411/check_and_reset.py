# check_and_reset.py
import sqlite3
from datetime import datetime

def check_and_reset():
    conn = sqlite3.connect('paper_trading.db')
    cursor = conn.cursor()
    
    print("🔍 DATABASE ANALYSIS")
    print("=" * 50)
    
    # Check all trades
    cursor.execute('SELECT trade_id, symbol, status FROM enhanced_trades')
    trades = cursor.fetchall()
    
    print(f"Total trades in database: {len(trades)}")
    
    open_trades = [t for t in trades if t[2] == 'OPEN']
    closed_trades = [t for t in trades if t[2] == 'CLOSED']
    
    print(f"Open trades: {len(open_trades)}")
    print(f"Closed trades: {len(closed_trades)}")
    
    # Show strategy breakdown
    cursor.execute('SELECT strategy_type, COUNT(*) FROM enhanced_trades GROUP BY strategy_type')
    print("\n📊 Strategy Breakdown:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} trades")
    
    # Reset all to CLOSED if needed
    if len(open_trades) > 20:  # Too many open positions
        print("\n🔄 Resetting open positions to CLOSED...")
        cursor.execute("UPDATE enhanced_trades SET status = 'CLOSED' WHERE status = 'OPEN'")
        conn.commit()
        print("✅ Database reset complete")
    elif len(open_trades) > 0:
        print(f"\n⚠️ {len(open_trades)} positions still open")
        print("Run with reset=True to close them all")
    
    conn.close()

if __name__ == "__main__":
    check_and_reset()
