#!/usr/bin/env python3
"""
Options Positions Analysis Dashboard
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

def load_positions():
    """Load positions from paper_positions.json"""
    try:
        with open('paper_positions.json', 'r') as f:
            positions = json.load(f)
        return positions
    except Exception as e:
        st.error(f"Error loading positions: {e}")
        return {}

def analyze_options_positions():
    """Analyze and display current options positions"""
    positions = load_positions()
    
    # Navigation back to main dashboard
    col_nav, col_empty = st.columns([1, 3])
    with col_nav:
        st.markdown("""
        <a href="http://localhost:8509" target="_blank" style="
            background-color: #f0f2f6;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 8px 16px;
            text-decoration: none;
            color: #262730;
            display: inline-block;
            font-weight: 500;
            text-align: center;
            margin: 5px 0;
        ">🏠 Back to Main Dashboard</a>
        """, unsafe_allow_html=True)
        st.caption("Click to open in new tab")
    
    with col_empty:
        st.empty()
    
    if not positions:
        st.warning("No open positions found.")
        return
    
    # Filter valid options positions
    valid_positions = {}
    for pos_id, pos in positions.items():
        if (pos.get('symbol') and pos.get('strike') and 
            pos.get('option_type') and pos.get('expiration')):
            valid_positions[pos_id] = pos
    
    if not valid_positions:
        st.warning("No valid options positions found.")
        return
    
    st.title("📊 Options Positions Analysis")
    
    # Group positions by underlying symbol
    positions_by_symbol = {}
    for pos_id, pos in valid_positions.items():
        symbol = pos['symbol']
        if symbol not in positions_by_symbol:
            positions_by_symbol[symbol] = []
        positions_by_symbol[symbol].append(pos)
    
    for symbol, symbol_positions in positions_by_symbol.items():
        st.header(f"{symbol} Position Analysis")
        
        # Calculate summary metrics
        total_quantity = sum(pos.get('quantity', 0) for pos in symbol_positions)
        net_debit_credit = sum(pos.get('entry_price', 0) * pos.get('quantity', 0) * 100 for pos in symbol_positions)
        
        # Create summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Underlying Symbol", symbol)
        with col2:
            st.metric("Total Quantity", total_quantity)
        with col3:
            st.metric("Net Debit/Credit", f"${net_debit_credit:.2f}")
        with col4:
            st.metric("Strategy Type", "Custom Multi-Leg")
        
        st.subheader("Detailed Legs Table")
        
        # Prepare data for table
        legs_data = []
        for i, pos in enumerate(symbol_positions, 1):
            direction = "LONG" if pos.get('quantity', 0) > 0 else "SHORT"
            quantity = abs(pos.get('quantity', 0))
            option_type = pos['option_type'].upper()
            strike = pos['strike']
            expiry = pos['expiration']
            premium = pos.get('entry_price', 0)
            current_value = premium  # Simplified
            leg_pnl = 0  # Simplified
            
            legs_data.append({
                'Leg': i,
                'Direction': direction,
                'Quantity': quantity,
                'Type': option_type,
                'Symbol': symbol,
                'Strike': f"${strike}",
                'Expiry': expiry,
                'Premium': f"${premium:.2f}",
                'Current Value': f"${current_value:.2f}",
                'Leg P&L': f"${leg_pnl:.2f}"
            })
        
        df_legs = pd.DataFrame(legs_data)
        st.dataframe(df_legs, width='stretch')
        
        st.subheader("Visual Strategy Diagram")
        
        # Create a simple but effective visual representation
        strikes = sorted(set(pos['strike'] for pos in symbol_positions))
        min_strike = min(strikes) if strikes else 0
        max_strike = max(strikes) if strikes else 0
        
        # Create a simple bar chart style visualization
        fig = go.Figure()
        
        for i, pos in enumerate(symbol_positions):
            strike = pos['strike']
            direction = 1 if pos.get('quantity', 0) > 0 else -1
            option_type = pos['option_type'][0].upper()
            quantity = abs(pos.get('quantity', 0))
            
            # Create a bar for each position
            color = 'green' if direction > 0 else 'red'
            position_label = f"{'LONG' if direction > 0 else 'SHORT'} {option_type}"
            
            fig.add_trace(go.Bar(
                x=[strike],
                y=[quantity],
                name=f"{symbol} ${strike} {option_type}",
                marker_color=color,
                text=f"{'+' if direction > 0 else '-'}{option_type}{quantity}",
                textposition='auto',
                hovertemplate=f"<b>{symbol}</b><br>Strike: ${strike}<br>Type: {option_type}<br>Direction: {'LONG' if direction > 0 else 'SHORT'}<br>Quantity: {quantity}<extra></extra>"
            ))
        
        # Set proper axis ranges
        x_range_min = min_strike - 20 if min_strike == max_strike else min_strike - 10
        x_range_max = max_strike + 20 if min_strike == max_strike else max_strike + 10
        
        fig.update_layout(
            title=f"{symbol} Options Positions",
            xaxis_title="Strike Price ($)",
            yaxis_title="Quantity",
            showlegend=True,
            height=400,
            xaxis=dict(range=[x_range_min, x_range_max]),
            plot_bgcolor='rgba(240,240,240,0.8)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            bargap=0.5
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Alternative: Simple text-based diagram
        st.subheader("Position Summary")
        for pos in symbol_positions:
            strike = pos['strike']
            direction = "LONG" if pos.get('quantity', 0) > 0 else "SHORT"
            option_type = pos['option_type'].upper()
            quantity = abs(pos.get('quantity', 0))
            
            st.write(f"**{direction} {quantity} {option_type} @ ${strike}**")
        
        # Add legend explanation
        with st.expander("📖 Chart Legend"):
            st.markdown("""
            **Legend Explanation:**
            - 🟢 **Green Bars**: Long Positions
            - 🔴 **Red Bars**: Short Positions
            - **+C1**: Long 1 Call contract
            - **-P2**: Short 2 Put contracts
            """)
        
        st.subheader("Risk Metrics")
        
        # Calculate basic risk metrics
        if len(symbol_positions) == 1:
            # Single long call
            pos = symbol_positions[0]
            if pos.get('quantity', 0) > 0 and pos['option_type'] == 'call':
                premium = pos.get('entry_price', 0)
                strike = pos['strike']
                breakeven = strike + premium
                current_underlying = pos.get('underlying_price', 0)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Max Profit", "Unlimited")
                with col2:
                    st.metric("Max Loss", f"${premium * 100:.2f}")
                with col3:
                    st.metric("Breakeven", f"${breakeven:.2f}")
                with col4:
                    st.metric("Current Underlying", f"${current_underlying:.2f}")
                
                # Additional metrics
                col5, col6, col7, col8 = st.columns(4)
                with col5:
                    status = "ITM" if current_underlying > strike else "OTM"
                    st.metric("Moneyness", status)
                with col6:
                    days_to_expiry = (datetime.strptime(pos['expiration'], '%Y-%m-%d') - datetime.now()).days
                    st.metric("Days to Expiry", days_to_expiry)
                with col7:
                    st.metric("Strategy", "Long Call")
                with col8:
                    intrinsic_value = max(0, current_underlying - strike)
                    extrinsic_value = premium - intrinsic_value
                    st.metric("Extrinsic Value", f"${extrinsic_value:.2f}")
        else:
            # Multi-leg strategy
            st.info("Complex multi-leg strategy - detailed risk metrics require complete strategy definition")
            
        st.divider()

def main():
    """Main function"""
    st.set_page_config(
        page_title="Options Positions Analysis",
        page_icon="📊",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stMetric {
        background-color: #ffffff !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    .stMetric > div {
        color: #262730 !important;
    }
    .stMetric > div > div:nth-child(2) {
        color: #1f77b4 !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }
    .stMetric > div > div:nth-child(3) {
        color: #ff4b4b !important;
    }
    .stDataFrame {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
    }
    .stExpander {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
    }
    /* Ensure all text in metrics is visible */
    .stMetric * {
        color: inherit !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    analyze_options_positions()

if __name__ == "__main__":
    main()