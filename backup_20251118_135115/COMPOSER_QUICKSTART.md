# Composer Integration Quick Start

Complete guide to using Composer Trade API with your options trading system.

## What You Get

The Composer integration adds optional capabilities to your trading system:

- **Portfolio Stats**: Pull holdings, stats, and performance metrics
- **Options Data**: Access options chains, contracts, and overview data
- **Backtesting**: Test strategies using Composer's backtest engine
- **Symphony Execution**: Create and manage algorithmic trading strategies
- **Redundancy**: Alternative data source when TastyTrade is throttled

## Architecture

Two integration modes are available:

### Direct REST Mode (Default)
```
Your App → composer_api.py → Composer REST API
```

### MCP Bridge Mode (Optional)
```
Your App → composer_api.py → composer_mcp_bridge.py → Composer REST API
                (optional)         (subprocess)
```

## Setup

### Step 1: Configure Authentication

**Option A - Firebase Token (Recommended)**

1. Login to https://app.composer.trade in your browser
2. Open DevTools (F12) → Network tab
3. Click around to trigger API calls
4. Find a request to `api.composer.trade` or `trading-api.composer.trade`
5. Copy the `Authorization` header value (starts with `Bearer eyJ...`)
6. Add to `.env`:
   ```
   COMPOSER_FIREBASE_TOKEN=your_long_token_here
   ```

**Option B - API Key/Secret (May Not Work)**

These credentials are already in your `.env`:
```
COMPOSER_API_KEY=897fb2d3-fe63-4eb4-bf4a-992b442c0ea9
COMPOSER_API_SECRET=417bca0e-a9c1-440c-b7f2-7fe614011f26
```

⚠️ **Note**: API key/secret may return 403 errors with Firebase-protected endpoints.

### Step 2: Optional - Get Your Account ID

1. Login to https://app.composer.trade
2. Open DevTools Console
3. Run: `localStorage.getItem('selectedAccount')`
4. Copy the account ID (format: `f7fe0727-6554-4e29-bc20-0ce016be5ebf`)
5. Add to `.env`:
   ```
   COMPOSER_ACCOUNT_ID=your_account_id_here
   ```

### Step 3: Optional - Enable MCP Bridge

For centralized auth management and IDE integration:

```bash
# In PowerShell
setx COMPOSER_MCP_ENABLED true
setx COMPOSER_MCP_COMMAND "python composer_mcp_bridge.py"
```

Or uncomment in `.env`:
```
COMPOSER_MCP_ENABLED=true
COMPOSER_MCP_COMMAND=python composer_mcp_bridge.py
```

## Testing

### Test Direct REST API

```bash
python test_composer.py
```

Expected results:
- ✅ With Firebase token: Full API access
- ⚠️ With API key/secret only: 403 Forbidden errors (expected)
- ❌ No credentials: Connection test fails gracefully

### Test MCP Bridge

```bash
python test_composer_mcp_bridge.py
```

This tests the MCP protocol and bridge implementation.

### Run Demo

```bash
python demo_composer_mcp.py
```

Shows protocol details, supported actions, and integration examples.

## Usage Examples

### Basic Usage

```python
from composer_api import ComposerTradeAPI

# Initialize (reads from environment variables)
api = ComposerTradeAPI()

# Check if configured
if api.is_configured:
    # Get accounts
    accounts = api.get_accounts_list()
    
    # Get holdings
    holdings = api.get_account_holdings("account-id")
    
    # Get options data
    spy_overview = api.get_options_overview("SPY")
    spy_chain = api.get_options_chain("SPY")
    
    # Portfolio stats
    stats = api.get_portfolio_stats("account-id")
```

### Integration with Risk Monitor

```python
# In risk_monitor.py
class RiskMonitor:
    def __init__(self, ..., composer=None):
        self.composer = composer
        self.composer_account_id = None
    
    def assess_risk(self):
        # ... existing risk assessment ...
        
        # Optional: Add Composer portfolio data
        if self.composer and self.composer.is_configured:
            try:
                stats = self.composer.get_portfolio_stats(self.composer_account_id)
                # Use stats to enrich risk assessment
            except Exception as e:
                self.logger.debug(f"Composer stats unavailable: {e}")
```

### Integration with Opportunity Scanner

```python
# In opportunity_scanner.py
class OpportunityScanner:
    def __init__(self, ..., composer=None):
        self.composer = composer
    
    def scan_opportunities(self):
        # ... existing scan logic ...
        
        # Optional: Cross-reference with Composer data
        if self.composer and self.composer.is_configured:
            try:
                overview = self.composer.get_options_overview(symbol)
                # Use as secondary data source
            except Exception as e:
                self.logger.debug(f"Composer data unavailable: {e}")
```

## MCP Bridge Details

When `COMPOSER_MCP_ENABLED=true`, these methods automatically route through the bridge:

- `get_accounts_list()`
- `get_account_holdings(account_id, ...)`
- `get_options_overview(symbol)`

All other methods use direct REST. If the bridge fails, it falls back to REST automatically.

### Why Use MCP?

1. **Centralized Auth**: Credentials managed in one place
2. **IDE Integration**: Query Composer from VS Code via MCP tools
3. **Token Rotation**: Easier to implement refresh logic
4. **Security**: Subprocess isolation prevents credential leakage
5. **Future-Proof**: Can add caching, rate limiting, retry logic centrally

## Current Status

### ✅ Complete
- Full REST API client with 20+ methods
- Optional MCP bridge with 3 actions
- Graceful fallback (REST → MCP → fail silently)
- Comprehensive test suite
- Documentation

### ⚠️ Blocked
- Need valid Firebase token for full functionality
- API key/secret returns 403 (authentication issue)

### 🔮 Future Enhancements
- Token refresh/rotation logic
- More MCP actions (backtests, order creation)
- Caching layer for frequently-accessed data
- Integration with dashboard for Composer portfolio view

## Troubleshooting

### 403 Forbidden Errors

Most common issue. Solutions:

1. **Get Firebase token** (see Step 1 above)
2. Check token hasn't expired (they typically last hours/days)
3. Verify you're logged into Composer in your browser
4. Try refreshing the page and extracting token again

### MCP Bridge Not Being Used

Check:
1. `COMPOSER_MCP_ENABLED=true` is set
2. `COMPOSER_MCP_COMMAND` points to correct path
3. Python can find `composer_mcp_bridge.py`
4. Look for debug logs: "MCP command non-zero exit" or "MCP response JSON decode failed"

### Import Errors

```bash
# Verify module loads
python -c "import composer_api; print('ok')"
```

If this fails, check:
- `requests` library is installed: `pip install requests`
- No syntax errors in `composer_api.py`

## Files Overview

| File | Purpose |
|------|---------|
| `composer_api.py` | Main REST API client with optional MCP routing |
| `composer_mcp_bridge.py` | MCP CLI bridge (stdin/stdout JSON protocol) |
| `test_composer.py` | Test direct REST API connection |
| `test_composer_mcp_bridge.py` | Test MCP bridge implementation |
| `demo_composer_mcp.py` | Interactive demo of MCP protocol |
| `COMPOSER_MCP_BRIDGE.md` | Detailed MCP bridge documentation |
| `COMPOSER_QUICKSTART.md` | This file |

## Next Steps

1. **Get Firebase token** (if you want full access):
   - Follow Step 1 above
   - Add to `.env` as `COMPOSER_FIREBASE_TOKEN`
   - Run `python test_composer.py` to verify

2. **Try MCP mode** (optional):
   - Enable MCP in `.env`
   - Run `python test_composer_mcp_bridge.py`
   - Check logs for "via MCP" vs "direct REST"

3. **Integrate with your app**:
   - Optional: Add Composer client to `main.py`
   - Pass to `RiskMonitor`, `OpportunityScanner`, etc.
   - Use try/except to keep integration non-blocking

## Questions?

- Check `COMPOSER_MCP_BRIDGE.md` for MCP details
- Check `SETUP.md` for general project setup
- Check `.env` for configuration options
