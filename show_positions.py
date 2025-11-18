#!/usr/bin/env python3
"""
Show all open positions across all accounts
"""

from dual_tastytrade_api import dual_tasty_api
from datetime import datetime
import json

def show_positions():
    """Display all open positions in a readable format"""
    print("\n" + "="*80)
    print("📊 OPEN POSITIONS REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Get all positions
    all_positions = dual_tasty_api.get_positions()
    
    if not all_positions:
        print("❌ No accounts found or unable to fetch positions.\n")
        return
    
    total_positions = 0
    
    # Display positions by account
    for account_type, positions in all_positions.items():
        print(f"\n🏦 {account_type.upper()} ACCOUNT")
        print("-" * 80)
        
        if not positions:
            print("   No open positions\n")
            continue
        
        total_positions += len(positions)
        
        # Display each position
        for position_id, position in positions.items():
            print(f"\n   Position ID: {position_id}")
            print(f"   Symbol:      {position.get('symbol', 'N/A')}")
            print(f"   Strategy:    {position.get('strategy_type', 'N/A')}")
            print(f"   Quantity:    {position.get('quantity', 'N/A')}")
            print(f"   Entry Price: ${position.get('entry_price', 0):.2f}")
            print(f"   Entry Time:  {position.get('entry_time', 'N/A')}")
            
            # Calculate current P&L if data available
            if 'current_price' in position and 'entry_price' in position:
                entry = position['entry_price']
                current = position['current_price']
                quantity = position.get('quantity', 0)
                pnl = (current - entry) * quantity * 100
                pnl_pct = ((current - entry) / entry * 100) if entry > 0 else 0
                
                color = "🟢" if pnl >= 0 else "🔴"
                print(f"   Current:     ${current:.2f}")
                print(f"   P&L:         {color} ${pnl:.2f} ({pnl_pct:+.2f}%)")
            
            print()
    
    # Summary
    print("="*80)
    print(f"SUMMARY: {total_positions} total open position(s)")
    print("="*80 + "\n")
    
    # Get account balances
    try:
        balances = dual_tasty_api.get_account_balances()
        print("\n💰 ACCOUNT BALANCES")
        print("-" * 80)
        for account_type, balance in balances.items():
            print(f"   {account_type.upper()}: ${balance:,.2f}")
        print()
    except Exception as e:
        print(f"\n⚠️ Could not fetch account balances: {e}\n")

def show_positions_json():
    """Display positions in JSON format"""
    print("\n" + "="*80)
    print("📊 OPEN POSITIONS (JSON)")
    print("="*80 + "\n")
    
    all_positions = dual_tasty_api.get_positions()
    print(json.dumps(all_positions, indent=2, default=str))
    print()

if __name__ == "__main__":
    import sys
    
    # Check for --json flag
    if "--json" in sys.argv:
        show_positions_json()
    else:
        show_positions()
