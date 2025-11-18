
import sys
import os
import pandas as pd
from datetime import datetime
import json

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dual_tastytrade_api import dual_tasty_api

def analyze_positions():
    # Get positions
    all_positions = dual_tasty_api.get_positions()
    
    # Flatten and filter
    valid_positions = []
    for acct, positions in all_positions.items():
        for pid, pos in positions.items():
            if pos.get('symbol') and pos.get('strike'):
                pos['account'] = acct
                valid_positions.append(pos)
    
    if not valid_positions:
        print("No valid positions found.")
        return

    # Group by symbol
    by_symbol = {}
    for pos in valid_positions:
        sym = pos['symbol']
        if sym not in by_symbol:
            by_symbol[sym] = []
        by_symbol[sym].append(pos)

    # Generate Report
    print("# 📊 Options Position Analysis\n")
    
    for sym, positions in by_symbol.items():
        # 1. Summary
        total_qty = sum(p.get('quantity', 0) for p in positions)
        net_cost = sum(p.get('entry_price', 0) * p.get('quantity', 0) * 100 for p in positions)
        
        # Determine Strategy
        if len(positions) == 1:
            p = positions[0]
            if p['option_type'] == 'call':
                strategy = "Long Call" if p['quantity'] > 0 else "Short Call"
            else:
                strategy = "Long Put" if p['quantity'] > 0 else "Short Put"
        else:
            strategy = "Multi-Leg Strategy" # Simplified for now

        print(f"## {sym} - {strategy}")
        print(f"- **Total Quantity:** {total_qty}")
        print(f"- **Net Debit/Credit:** ${net_cost:.2f}")
        print(f"- **Account:** {positions[0]['account'].upper()}")
        print("\n")

        # 2. Detailed Legs Table
        print("### Detailed Legs")
        print("| Leg | Dir | Qty | Type | Strike | Exp | Premium | Value |")
        print("|---|---|---|---|---|---|---|---|")
        
        for i, p in enumerate(positions, 1):
            direction = "LONG" if p.get('quantity', 0) > 0 else "SHORT"
            qty = abs(p.get('quantity', 0))
            otype = p.get('option_type', '').upper()
            strike = p.get('strike')
            exp = p.get('expiration')
            prem = p.get('entry_price', 0)
            val = prem # Mock current value
            
            print(f"| {i} | {direction} | {qty} | {otype} | ${strike} | {exp} | ${prem:.2f} | ${val:.2f} |")
        print("\n")

        # 3. Visual Diagram (ASCII)
        print("### Visual Structure")
        print("```")
        print(f"Price Axis:  Low <--------------------------------> High")
        
        # Sort by strike
        positions.sort(key=lambda x: x['strike'])
        
        for p in positions:
            direction = "+" if p.get('quantity', 0) > 0 else "-"
            otype = "C" if p.get('option_type') == 'call' else "P"
            strike = p['strike']
            
            # Simple stick diagram
            marker = f"{direction}{abs(p['quantity'])}{otype}"
            padding = " " * int((strike % 100) / 2) # simplistic spacing
            print(f"${strike:<6} : {marker}")
        print("```\n")

        # 4. Risk Metrics
        print("### Risk Metrics")
        if len(positions) == 1:
            p = positions[0]
            if p['option_type'] == 'call' and p['quantity'] > 0:
                breakeven = p['strike'] + p['entry_price']
                print(f"- **Max Profit:** Unlimited")
                print(f"- **Max Loss:** ${p['entry_price']*100:.2f}")
                print(f"- **Breakeven:** ${breakeven:.2f}")
            elif p['option_type'] == 'put' and p['quantity'] > 0:
                breakeven = p['strike'] - p['entry_price']
                print(f"- **Max Profit:** ${(p['strike'] - p['entry_price'])*100:.2f}")
                print(f"- **Max Loss:** ${p['entry_price']*100:.2f}")
                print(f"- **Breakeven:** ${breakeven:.2f}")
        
        print("\n---\n")

if __name__ == "__main__":
    analyze_positions()
