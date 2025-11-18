# Web Dashboard Setup Guide

## Install Required Packages

Run this command to install the web dashboard dependencies:

```bash
pip install streamlit plotly pandas
```

## Run the Dashboard

```bash
streamlit run web_dashboard.py
```

The dashboard will automatically open in your browser at http://localhost:8501

## Features

✅ **Real-time Opportunity Scanning** - Click "Scan Opportunities" to find trades
✅ **Portfolio Overview** - View your positions and strategy allocation
✅ **Risk Management** - Monitor risk levels and guidelines
✅ **Performance Analytics** - Track P&L and trading performance
✅ **Mock Data Support** - Test strategies 24/7 with realistic mock opportunities

## Dashboard Sections

1. **Opportunities Tab** - Scan and execute paper trades
2. **Portfolio Tab** - View positions and strategy breakdown
3. **Risk Tab** - Monitor risk metrics and guidelines
4. **Analytics Tab** - Performance charts and statistics

## Configuration

Use the sidebar to adjust:
- Maximum position size
- Daily trade limits
- Risk tolerance
- Scanner confidence threshold
- Mock data inclusion

## Tips

💡 Markets closed? Enable mock data for 24/7 testing
💡 Use the risk slider to match your trading style
💡 Click "Scan Opportunities" to refresh available trades
💡 All trades are paper trading - zero real money risk!
