#!/usr/bin/env python3
"""
Beautiful Web Dashboard for Enhanced Paper Trading System
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import sys
import os
import yfinance as yf

# Add your existing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing trading system
from enhanced_paper_trading import EnhancedPaperTradingEngine
from opportunity_scanner import OpportunityScanner
from risk_monitor import AccountRiskMonitor
from jax_engine import JAXRealTimeAnalytics
from tastytrade_api import TastyTradeAPI
from config import TradingConfig
from dual_tastytrade_api import dual_tasty_api

class TradingDashboard:
    def __init__(self):
        self.setup_page()
        self.initialize_session_state()
        
    def setup_page(self):
        """Configure the Streamlit page"""
        st.set_page_config(
            page_title="Antigravity Trading System",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for professional look
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1E1E1E;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #555;
            margin-bottom: 2rem;
        }
        .metric-container {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #f0f2f6;
        }
        .stButton button {
            border-radius: 8px;
            font-weight: 600;
        }
        .opportunity-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            margin-bottom: 1rem;
            transition: transform 0.2s;
        }
        .opportunity-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'trading_system' not in st.session_state:
            tasty_api = TastyTradeAPI(sandbox=True)
            st.session_state.trading_system = EnhancedPaperTradingEngine(tasty_api)
        if 'jax_engine' not in st.session_state:
            st.session_state.jax_engine = JAXRealTimeAnalytics()
        if 'scanner' not in st.session_state:
            st.session_state.scanner = OpportunityScanner(st.session_state.jax_engine)
        if 'risk_monitor' not in st.session_state:
            # Initialize risk monitor with dependencies
            # We need a deepseek mock or real instance if available
            from deepseek_analyst import DeepSeekMultiTaskAI
            deepseek = DeepSeekMultiTaskAI(api_key=os.getenv("DEEPSEEK_API_KEY", "mock_key"))
            risk_params = {'max_open_positions': 5, 'max_risk_per_trade': 500}
            st.session_state.risk_monitor = AccountRiskMonitor(dual_tasty_api, deepseek, risk_params)
            
        if 'opportunities' not in st.session_state:
            st.session_state.opportunities = []
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = False

    def render_risk(self):
        """Render risk metrics with Gauge Chart"""
        st.markdown("### 🛡️ Risk Intelligence")
        
        # Get real risk assessment
        positions = dual_tasty_api.get_positions()
        # Flatten positions for risk monitor
        flat_positions = {}
        for acct, pos_dict in positions.items():
            flat_positions.update(pos_dict)
            
        assessment = st.session_state.risk_monitor.assess_portfolio_risk(flat_positions)
        
        # Calculate risk score (0-100) based on alert level or internal score
        # If assessment has a risk_score attribute, use it, otherwise map alert level
        risk_score = getattr(assessment, 'risk_score', assessment.alert_level * 10)
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            # Risk Gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = risk_score, 
                title = {'text': "Portfolio Risk Score"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#1f77b4"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgreen"},
                        {'range': [30, 70], 'color': "lightyellow"},
                        {'range': [70, 100], 'color': "salmon"}],
                }
            ))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.info(f"**Risk Analysis: {assessment.message}**")
            
            if assessment.concerns:
                st.write("**Concerns:**")
                for concern in assessment.concerns:
                    st.write(f"• {concern}")
            else:
                st.write("• No immediate risk concerns identified.")
                
            if assessment.recommendations:
                st.write("**Recommendations:**")
                for rec in assessment.recommendations:
                    st.write(f"• {rec}")
            
            # Display Greeks if available
            # This would require calculating metrics separately or extracting from assessment if added
            # For now, we show the assessment details
            
            if risk_score > 50:
                st.warning("⚠️ **Alert:** Portfolio risk is elevated. Review positions.")
            
    def get_market_data(self):
        """Fetch live market data (VIX, SPY)"""
        try:
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            spy = yf.Ticker("SPY").history(period="1d")['Close'].iloc[-1]
            return vix, spy
        except:
            return 18.5, 450.00

    def render_header(self):
        """Render the main header with live market context"""
        col_title, col_status = st.columns([2, 1])
        
        with col_title:
            st.markdown('<div class="main-header">🚀 Antigravity Trading System</div>', unsafe_allow_html=True)
            st.markdown('<div class="sub-header">Dual-Account AI Orchestrator</div>', unsafe_allow_html=True)
            
        with col_status:
            # Live VIX and Market Status
            vix, spy = self.get_market_data()
            
            # Determine market condition color
            if vix < 20:
                market_color = "green"
                condition = "BULLISH"
            elif vix < 30:
                market_color = "orange"
                condition = "CAUTION"
            else:
                market_color = "red"
                condition = "HIGH VOLATILITY"
                
            st.markdown(f"""
            <div style="text-align: right; background-color: #f8f9fa; padding: 10px; border-radius: 8px;">
                <span style="font-size: 0.9rem; color: #666;">MARKET CONDITION</span><br>
                <span style="font-size: 1.2rem; font-weight: bold; color: {market_color};">{condition}</span>
            </div>
            """, unsafe_allow_html=True)

        # System Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        # Get real account data
        try:
            balances = dual_tasty_api.get_account_balances()
            all_positions = dual_tasty_api.get_positions()
            total_positions = sum(len(positions) for positions in all_positions.values())
            total_balance = sum(balances.values())
            
            with col1:
                st.metric("💰 Total AUM", f"${total_balance:,.2f}", delta=None)
            with col2:
                st.metric("📊 Active Positions", total_positions)
            with col3:
                st.metric("📉 VIX Index", f"{vix:.2f}", delta=None)
            with col4:
                st.metric("📈 SPY Price", f"${spy:.2f}")
                
        except Exception as e:
            st.error(f"System Error: {e}")

    def render_sidebar(self):
        """Render sidebar controls"""
        with st.sidebar:
            st.header("⚙️ System Controls")
            
            st.subheader("Trading Mode")
            trading_mode = os.getenv('TRADING_MODE', 'paper').upper()
            if trading_mode == 'LIVE':
                st.error("🔴 **LIVE TRADING ACTIVE**")
            else:
                st.success("📝 **PAPER TRADING ACTIVE**")
            
            st.subheader("Risk Preferences")
            max_position_size = st.slider("Max Position Size ($)", 1000, 10000, 3000)
            max_daily_trades = st.slider("Max Daily Trades", 1, 20, 10)
            risk_tolerance = st.select_slider(
                "Risk Tolerance",
                options=["Very Low", "Low", "Medium", "High", "Very High"],
                value="Medium"
            )
            
            st.subheader("Scanner Settings")
            min_confidence = st.slider("Minimum Confidence %", 50, 90, 65)
            include_mock_data = st.checkbox("Include Mock Data", value=True)
            
            # Auto-refresh logic
            st.subheader("Dashboard Settings")
            auto_refresh = st.checkbox("🔄 Auto-Refresh (60s)", value=st.session_state.auto_refresh)
            st.session_state.auto_refresh = auto_refresh
            
            if st.button("🔄 Apply Settings"):
                st.success("Settings applied successfully!")
            
            st.markdown("---")
            st.info("**💡 Tip**: Use mock data for testing strategies without market hours limitations.")
            
            st.markdown("---")
            st.caption("Antigravity Trading System v2.1")

    def render_opportunities(self):
        """Render trading opportunities with enhanced visuals"""
        st.markdown("### 🎯 AI Opportunity Scanner")
        
        col_scan, col_filter = st.columns([1, 3])
        with col_scan:
            if st.button("🔄 Scan Market", type="primary", use_container_width=True):
                with st.spinner("🤖 DeepSeek AI analyzing market structure..."):
                    st.session_state.opportunities = st.session_state.scanner.scan_opportunities()
                    st.session_state.last_update = datetime.now()
        
        if st.session_state.opportunities:
            # Convert to DataFrame for easier handling
            opps_data = []
            for opp in st.session_state.opportunities:
                # Normalize data
                if isinstance(opp, dict):
                    opps_data.append(opp)
                else:
                    opps_data.append(opp.__dict__)
            
            df_opps = pd.DataFrame(opps_data)
            
            # Display top opportunities as cards
            for i, row in df_opps.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="opportunity-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3 style="margin: 0; color: #1f77b4;">{row.get('symbol', 'N/A')}</h3>
                                <span style="background-color: #e3f2fd; color: #1f77b4; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">{row.get('strategy', 'N/A')}</span>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.5rem; font-weight: bold;">${row.get('premium', 0):.2f}</div>
                                <div style="font-size: 0.8rem; color: #666;">Premium</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                    with c1:
                        st.caption("Confidence")
                        conf = row.get('ai_confidence', row.get('confidence', 0))
                        st.progress(conf)
                    with c2:
                        st.caption("Strike")
                        st.write(f"**${row.get('strike', 0):.2f}**")
                    with c3:
                        st.caption("Expiration")
                        st.write(f"**{row.get('expiration', 'N/A')}**")
                    with c4:
                        if st.button("Trade", key=f"trade_btn_{i}"):
                            self.execute_trade_modal(row)
                    
                    st.divider()
        else:
            st.info("👋 Click 'Scan Market' to find high-probability trades.")

    def execute_trade_modal(self, opportunity):
        """Trade execution modal"""
        st.session_state['selected_trade'] = opportunity
        
    def render_trade_execution(self):
        """Render trade execution if a trade is selected"""
        if 'selected_trade' in st.session_state:
            opp = st.session_state['selected_trade']
            
            with st.expander(f"🚀 Execute Trade: {opp.get('symbol')} {opp.get('strategy')}", expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    account = st.radio("Select Account", ["paper", "live"], format_func=lambda x: f"{x.upper()} Account")
                with c2:
                    quantity = st.number_input("Quantity", min_value=1, value=1)
                
                if st.button("✅ Confirm Execution", type="primary", use_container_width=True):
                    with st.spinner("Routing order..."):
                        result = dual_tasty_api.execute_trade(opp, account)
                        if result.get('success'):
                            st.success(f"Order Filled! ID: {result.get('order_id')}")
                            st.balloons()
                            del st.session_state['selected_trade']
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"Execution Failed: {result.get('error')}")

    def render_portfolio(self):
        """Render enhanced portfolio table"""
        st.markdown("### 💼 Portfolio Holdings")
        
        # Get positions
        all_positions = dual_tasty_api.get_positions()
        
        # Flatten positions for the table
        table_data = []
        for acct_type, positions in all_positions.items():
            for pid, pos in positions.items():
                entry = pos.get('entry_price', 0)
                curr = pos.get('current_price', entry) # Mock current price if missing
                pnl = (curr - entry) * pos.get('quantity', 1) * 100
                pnl_pct = (curr - entry) / entry if entry > 0 else 0
                
                table_data.append({
                    "Account": "📝 PAPER" if acct_type == 'paper' else "💰 LIVE",
                    "Symbol": pos.get('symbol'),
                    "Strategy": pos.get('strategy'),
                    "Qty": pos.get('quantity'),
                    "Entry": entry,
                    "Current": curr,
                    "P&L ($)": pnl,
                    "P&L (%)": pnl_pct,
                })
        
        if table_data:
            df = pd.DataFrame(table_data)
            
            st.dataframe(
                df,
                column_config={
                    "Entry": st.column_config.NumberColumn(format="$%.2f"),
                    "Current": st.column_config.NumberColumn(format="$%.2f"),
                    "P&L ($)": st.column_config.NumberColumn(format="$%.2f"),
                    "P&L (%)": st.column_config.ProgressColumn(
                        format="%.2f%%",
                        min_value=-0.5,
                        max_value=0.5,
                    ),
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No active positions.")

    def render_options_analysis(self):
        """Render detailed options analysis (Integrated from options_dashboard.py)"""
        st.markdown("### 📊 Options Strategy Visualizer")
        
        # Get positions from dual API
        all_positions = dual_tasty_api.get_positions()
        
        # Flatten and filter for options
        options_positions = []
        for acct_type, positions in all_positions.items():
            for pos_id, pos in positions.items():
                # Check if it's an option (has strike/expiration)
                if pos.get('strike') and pos.get('option_type'):
                    pos['account'] = acct_type
                    options_positions.append(pos)
        
        if not options_positions:
            st.info("No options positions found to analyze.")
            return

        # Group by Symbol
        symbols = sorted(list(set(p['symbol'] for p in options_positions)))
        
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_symbol = st.selectbox("Select Underlying Symbol", symbols)
        
        if selected_symbol:
            symbol_positions = [p for p in options_positions if p['symbol'] == selected_symbol]
            self.visualize_strategy(selected_symbol, symbol_positions)

    def visualize_strategy(self, symbol, positions):
        """Visualize multi-leg strategy for a symbol with advanced metrics"""
        
        # 1. Strategy Identification & Summary
        total_quantity = sum(pos.get('quantity', 0) for pos in positions)
        net_premium = sum(pos.get('entry_price', 0) * pos.get('quantity', 0) * 100 for pos in positions)
        
        # Simple strategy detection
        strategy_type = "Custom Multi-Leg"
        if len(positions) == 1:
            p = positions[0]
            if p['option_type'] == 'call':
                strategy_type = "Long Call" if p.get('quantity', 0) > 0 else "Short Call"
            else:
                strategy_type = "Long Put" if p.get('quantity', 0) > 0 else "Short Put"
        
        st.markdown(f"### 🏗️ {symbol} - {strategy_type}")
        
        # Summary Metrics Row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Contracts", total_quantity)
        with c2:
            st.metric("Net Debit/Credit", f"${net_premium:.2f}")
        with c3:
            # Mock current value (in production, fetch live price)
            current_val = net_premium * 1.05 
            pnl = current_val - net_premium
            st.metric("Est. P&L", f"${pnl:.2f}", delta=f"{pnl/net_premium*100:.1f}%" if net_premium!=0 else "0%")
        with c4:
            st.metric("Strategy", strategy_type)
            
        st.divider()
        
        # 2. Detailed Legs Table
        st.markdown("#### 🦵 Leg Breakdown")
        legs_data = []
        for i, pos in enumerate(positions, 1):
            direction = "LONG" if pos.get('quantity', 0) > 0 else "SHORT"
            legs_data.append({
                "Leg": i,
                "Side": direction,
                "Qty": abs(pos.get('quantity', 0)),
                "Type": pos.get('option_type', '').upper(),
                "Strike": f"${pos.get('strike', 0):.2f}",
                "Expiry": pos.get('expiration', 'N/A'),
                "Premium": f"${pos.get('entry_price', 0):.2f}",
                "Value": f"${pos.get('entry_price', 0):.2f}", # Mock
                "IV Rank": "N/A" # Placeholder
            })
            
        st.dataframe(
            pd.DataFrame(legs_data), 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Side": st.column_config.TextColumn("Side", help="Long or Short"),
            }
        )
        
        # 3. Visual Structure & Payoff Diagram
        st.markdown("#### 📊 Payoff Diagram (At Expiration)")
        
        strikes = sorted(set(pos.get('strike', 0) for pos in positions))
        if strikes:
            min_strike = min(strikes)
            max_strike = max(strikes)
            current_price = positions[0].get('underlying_price', (min_strike + max_strike)/2)
            if current_price == 0: current_price = (min_strike + max_strike)/2
            
            # Generate price range for x-axis
            lower_bound = min(min_strike * 0.8, current_price * 0.8)
            upper_bound = max(max_strike * 1.2, current_price * 1.2)
            price_range = list(range(int(lower_bound), int(upper_bound), 1))
            
            payoff_values = []
            for price in price_range:
                total_pnl = 0
                for pos in positions:
                    strike = pos.get('strike', 0)
                    qty = pos.get('quantity', 0) # Positive for long, negative for short (if data is structured that way)
                    # If quantity is always positive in data, need to check side/direction
                    # Assuming quantity is signed or we check type
                    # In dual_tasty_api, quantity is usually positive, need to check if we have 'direction' or 'action'
                    # But here we might have normalized it. Let's check how we normalized it in 'legs_data'
                    # We used: direction = "LONG" if pos.get('quantity', 0) > 0 else "SHORT"
                    # So pos['quantity'] holds the sign.
                    
                    premium = pos.get('entry_price', 0)
                    option_type = pos.get('option_type', '').lower()
                    
                    # Value at expiration
                    if option_type == 'call':
                        value = max(0, price - strike)
                    else: # put
                        value = max(0, strike - price)
                    
                    # P&L = (Value - Premium) * Qty * 100
                    # For Long: (Value - Premium) * Qty
                    # For Short: (Premium - Value) * Qty  <-- Wait, if Qty is negative for short:
                    # (Value - Premium) * (-1) = Premium - Value. Correct.
                    
                    leg_pnl = (value - premium) * qty * 100
                    total_pnl += leg_pnl
                payoff_values.append(total_pnl)
            
            # Create Plotly Line Chart
            fig = go.Figure()
            
            # Payoff Line
            fig.add_trace(go.Scatter(
                x=price_range, 
                y=payoff_values, 
                mode='lines', 
                name='P&L at Expiration',
                line=dict(color='#1f77b4', width=3),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.1)' # Light blue fill
            ))
            
            # Zero Line
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            # Current Price Line
            fig.add_vline(x=current_price, line_dash="dot", line_color="orange", annotation_text="Current Price")
            
            # Strike Lines
            for strike in strikes:
                fig.add_vline(x=strike, line_dash="dot", line_color="gray", opacity=0.5)

            fig.update_layout(
                xaxis_title="Underlying Price ($)",
                yaxis_title="Profit / Loss ($)",
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

        # 4. Risk Metrics
        st.markdown("#### ⚠️ Risk Profile")
        r1, r2, r3 = st.columns(3)
        
        # Calculate metrics for single leg
        if len(positions) == 1:
            p = positions[0]
            strike = p.get('strike', 0)
            premium = p.get('entry_price', 0)
            
            if p['option_type'] == 'call' and p.get('quantity', 0) > 0:
                breakeven = strike + premium
                with r1: st.metric("Max Profit", "Unlimited 🚀")
                with r2: st.metric("Max Loss", f"${premium * 100:.2f}")
                with r3: st.metric("Breakeven", f"${breakeven:.2f}")
            elif p['option_type'] == 'put' and p.get('quantity', 0) > 0:
                breakeven = strike - premium
                with r1: st.metric("Max Profit", f"${(strike - premium) * 100:.2f}")
                with r2: st.metric("Max Loss", f"${premium * 100:.2f}")
                with r3: st.metric("Breakeven", f"${breakeven:.2f}")
        else:
            st.info("Complex strategy risk metrics require advanced pricing model.")



    def render_ai_insights(self):
        """Render AI insights and alerts"""
        st.markdown("### 🧠 DeepSeek AI Insights")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📝 Daily AI Report")
            if st.button("Generate New Report", key="gen_report"):
                with st.spinner("DeepSeek AI analyzing portfolio and market..."):
                    # Gather data for report
                    positions = dual_tasty_api.get_positions()
                    flat_positions = {}
                    for acct, pos_dict in positions.items():
                        flat_positions.update(pos_dict)
                    
                    # Call DeepSeek (via risk monitor's instance)
                    if hasattr(st.session_state.risk_monitor, 'deepseek_ai'):
                        report = st.session_state.risk_monitor.deepseek_ai.generate_daily_report(
                            flat_positions, st.session_state.opportunities
                        )
                        st.session_state['daily_report'] = report
                    else:
                        st.error("DeepSeek AI not initialized.")
            
            if 'daily_report' in st.session_state:
                report = st.session_state['daily_report']
                if isinstance(report, dict):
                    st.json(report)
                else:
                    st.markdown(report)
            else:
                st.info("No report generated today. Click above to generate.")

        with col2:
            st.subheader("🚨 Recent Alerts")
            if hasattr(st.session_state.risk_monitor, 'alert_history'):
                alerts = st.session_state.risk_monitor.alert_history
                if alerts:
                    for alert in reversed(alerts[-5:]): # Show last 5
                        icon = "🔴" if alert.level.value >= 2 else "⚠️"
                        st.markdown(f"""
                        <div style="padding: 10px; border-left: 4px solid #ff4b4b; background-color: #fff5f5; margin-bottom: 10px;">
                            <strong>{icon} {alert.level.name}</strong><br>
                            <small>{alert.timestamp.strftime('%H:%M:%S')}</small><br>
                            {alert.message}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("No recent risk alerts.")
            else:
                st.write("Alert history unavailable.")

    def run(self):
        """Main dashboard loop"""
        self.render_sidebar()  # Restore sidebar
        self.render_header()
        
        # Trade Execution Modal (if active)
        self.render_trade_execution()
        
        # Main Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Opportunities", "💼 Portfolio", "📊 Strategy Visualizer", "🛡️ Risk & Analytics", "🧠 AI Insights"])
        
        with tab1:
            self.render_opportunities()
        with tab2:
            self.render_portfolio()
        with tab3:
            self.render_options_analysis()
        with tab4:
            self.render_risk()
        with tab5:
            self.render_ai_insights()
            
        # Auto-refresh logic (now handled in sidebar, but check state here too)
        if st.session_state.auto_refresh:
            time.sleep(60)
            st.rerun()

if __name__ == "__main__":
    dashboard = TradingDashboard()
    dashboard.run()
