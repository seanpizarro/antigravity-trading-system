# Copilot Cheatsheet

Quick reference for common commands, API endpoints, and code patterns.

---

## Common Commands
- `python main.py` — Run main orchestrator
- `streamlit run web_dashboard.py` — Launch dashboard
- `python validate_system.py` — Run validation checks

## API Endpoints
- DeepSeek: https://api.deepseek.com/v1
- TastyTrade: https://api.tastytrade.com
- Alpaca: https://paper-api.alpaca.markets

## Code Patterns
- Daemon thread loop:
```python
while self.is_running:
    try:
        # work
        time.sleep(interval)
    except Exception as e:
        self.logger.error(f"Error: {e}")
        time.sleep(retry_interval)
```

---

*Add your own shortcuts and patterns here!*