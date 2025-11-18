#!/usr/bin/env python3
"""
Analyze current open options positions and display complete details
"""

import json
import math
from datetime import datetime
from typing import Dict, List, Optional
import sys

def load_positions():
    """Load positions from paper_positions.json"""
    try:
        with open('paper_positions.json', 'r') as f:
            positions = json.load(f)
        return positions
    except Exception as e:
        print(f"Error loading positions: {e}")
        return {}

def analyze_options_positions():
    """Analyze and display current options positions"""
    positions = load_positions()
    
    if not positions:
        print("No open positions found.")
        return
    
    # Filter valid options positions
    valid_positions = {}
    for pos_id, pos in positions.items():
        if (pos.get('symbol') and pos.get('strike') and 
            pos.get('option_type') and pos.get('expiration')):
            valid_positions[pos_id] = pos
    
    if not valid_positions:
        print("No valid options positions found.")
        return
    
    print("# Current Open Options Positions Analysis")
    print()
    
    # Group positions by underlying symbol
    positions_by_symbol = {}
    for pos_id, pos in valid_positions.items():
        symbol = pos['symbol']
        if symbol not in positions_by_symbol:
            positions_by_symbol[symbol] = []
        positions_by_symbol[symbol].append(pos)
    
    for symbol, symbol_positions in positions_by_symbol.items():
        print(f"## {symbol} Position Analysis")
        print()
        
        # Calculate summary metrics
        total_quantity = sum(pos.get('quantity', 0) for pos in symbol_positions)
        net_debit_credit = sum(pos.get('entry_price', 0) * pos.get('quantity', 0) * 100 for pos in symbol_positions)
        
        # Estimate current P&L (simplified - would need real market data)
        current_underlying_price = symbol_positions[0].get('underlying_price', 0)
        estimated_pnl = 0
        
        print("### 1. Summary")
        print(f"- **Underlying Symbol**: {symbol}")
        print(f"- **Strategy Type**: Custom Multi-Leg")
        print(f"- **Total Position Quantity**: {total_quantity}")
        print(f"- **Net Debit/Credit**: ${net_debit_credit:.2f}")
        print(f"- **Current Mark-to-Market P&L**: ${estimated_pnl:.2f}")
        print(f"- **Current Total Greeks**: Not available (requires real-time data)")
        print()
        
        print("### 2. Detailed Legs Table")
        print()
        print("| Leg | Direction | Quantity | Type | Symbol | Strike | Expiry | IV Rank | Premium | Current Value | Leg P&L |")
        print("|-----|-----------|----------|------|--------|--------|--------|---------|---------|---------------|---------|")
        
        for i, pos in enumerate(symbol_positions, 1):
            direction = "LONG" if pos.get('quantity', 0) > 0 else "SHORT"
            quantity = abs(pos.get('quantity', 0))
            option_type = pos['option_type'].upper()
            strike = pos['strike']
            expiry = pos['expiration']
            premium = pos.get('entry_price', 0)
            current_value = premium  # Simplified - would need real market data
            leg_pnl = 0  # Simplified
            
            print(f"| {i} | {direction} | {quantity} | {option_type} | {symbol} | ${strike} | {expiry} | N/A | ${premium:.2f} | ${current_value:.2f} | ${leg_pnl:.2f} |")
        
        print()
        
        print("### 3. Visual Strategy Diagram")
        print()
        
        # Create simple ASCII diagram
        strikes = sorted(set(pos['strike'] for pos in symbol_positions))
        min_strike = min(strikes) if strikes else 0
        max_strike = max(strikes) if strikes else 0
        
        print(f"Price Axis: ${min_strike} {'-' * 20} ${max_strike}")
        print()
        
        for pos in symbol_positions:
            strike = pos['strike']
            direction = "+" if pos.get('quantity', 0) > 0 else "-"
            option_type = pos['option_type'][0].upper()  # C for call, P for put
            quantity = abs(pos.get('quantity', 0))
            
            # Position marker on price axis
            strike_pos = int((strike - min_strike) / (max_strike - min_strike) * 40) if max_strike > min_strike else 20
            marker_line = [' '] * 41
            marker_line[strike_pos] = direction + option_type + str(quantity)
            
            print(f"{''.join(marker_line)}  <- {direction}{option_type} ${strike} (Qty: {quantity})")
        
        print()
        
        print("### 4. Additional Risk Metrics")
        print()
        print("- **Max Profit**: Not calculable without complete strategy definition")
        print("- **Max Loss**: Not calculable without complete strategy definition") 
        print("- **Breakeven Price(s)**: Not calculable without complete strategy definition")
        print("- **Probability of Profit**: Not calculable without real-time data")
        print()
        
        print("---")
        print()

def main():
    """Main function"""
    print("Analyzing current options positions...")
    print("=" * 80)
    print()
    
    analyze_options_positions()
    
    print("=" * 80)
    print("Analysis complete.")

if __name__ == "__main__":
    main()
