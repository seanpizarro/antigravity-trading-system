# Composer MCP Bridge

A lightweight CLI bridge that proxies Composer Trade API requests via an MCP-style interface.

## Purpose

This bridge allows your trading system to route Composer API calls through a standardized MCP interface instead of direct REST calls. Benefits:

- **Centralized auth**: Credentials live in environment variables accessed by the bridge only
- **Graceful fallback**: If the bridge fails, the main API client falls back to direct REST
- **MCP compatibility**: Works with MCP-aware tools and IDEs that support stdin/stdout JSON protocols

## Architecture

```
composer_api.py → composer_mcp_bridge.py → Composer REST API
     (optional)         (subprocess)
```

## Installation

No extra dependencies needed beyond what's already in `requirements.txt`:
- `requests` (for API calls)

## Configuration

Set environment variables (PowerShell):

```powershell
# Primary authentication (recommended)
setx COMPOSER_FIREBASE_TOKEN "your_firebase_token_here"

# Alternative authentication
setx COMPOSER_API_KEY "your_api_key"
setx COMPOSER_API_SECRET "your_api_secret"

# Optional: your account ID for testing
setx COMPOSER_ACCOUNT_ID "your_account_id"

# Enable MCP routing in composer_api.py
setx COMPOSER_MCP_ENABLED true
setx COMPOSER_MCP_COMMAND "python composer_mcp_bridge.py"
```

Close and reopen your terminal to load the new environment variables.

## Usage

### Standalone Testing

Test the bridge directly:

```powershell
python test_composer_mcp_bridge.py
```

This will test all three supported actions:
- `accounts.list` - Get user accounts
- `accounts.holdings` - Get account holdings
- `market.options_overview` - Get options overview for a symbol

### Manual Testing

You can also test manually via stdin/stdout:

```powershell
echo '{"tool":"composer","action":"accounts.list","payload":{}}' | python composer_mcp_bridge.py
```

### Integration with Main System

Once `COMPOSER_MCP_ENABLED=true` is set, `composer_api.py` will automatically route these methods through the bridge:
- `get_accounts_list()`
- `get_account_holdings(account_id, ...)`
- `get_options_overview(symbol)`

All other methods continue to use direct REST calls.

## Protocol

### Input (stdin)

JSON object with:
```json
{
  "tool": "composer",
  "action": "accounts.list",
  "payload": {}
}
```

### Output (stdout)

Success:
```json
{
  "ok": true,
  "result": [ ... ]
}
```

Error:
```json
{
  "ok": false,
  "error": "Error message"
}
```

## Supported Actions

| Action | Payload | Description |
|--------|---------|-------------|
| `accounts.list` | `{}` | Get list of user accounts |
| `accounts.holdings` | `{"account_id": "..."}` | Get holdings for account |
| `market.options_overview` | `{"symbol": "SPY"}` | Get options overview |

## Adding New Actions

To add support for more Composer endpoints:

1. Add a handler method in `ComposerMCPBridge` class:
```python
def portfolio_stats(self, payload):
    account_id = payload.get("account_id")
    return self._make_request("GET", f"/api/v0.1/portfolio/accounts/{account_id}/total-stats")
```

2. Register it in the `handle_action` method:
```python
handlers = {
    # ... existing handlers ...
    "portfolio.stats": self.portfolio_stats,
}
```

3. Update `composer_api.py` to route the corresponding method through MCP.

## Troubleshooting

**403 Forbidden errors:**
- Your Firebase token expired or is invalid
- API key/secret doesn't have necessary permissions
- Try refreshing your Firebase token from the browser

**Bridge not being used:**
- Check `COMPOSER_MCP_ENABLED=true` is set
- Verify `COMPOSER_MCP_COMMAND` points to the correct path
- Look for debug logs in your application output

**Timeout errors:**
- Increase `COMPOSER_MCP_TIMEOUT` (default: 8 seconds)
- Check network connectivity to api.composer.trade

## Security Notes

- The bridge reads credentials from environment variables only
- Never hardcode tokens in the bridge code
- The `.env` file is gitignored to prevent credential leaks
- Bridge output goes only to stdout (no file logging of sensitive data)

## Performance

- Subprocess overhead: ~50-100ms per call
- If MCP call fails, fallback to direct REST adds no extra latency
- Rate limiting applies at the API client level (1 req/sec)

## Future Enhancements

- [ ] Support for write operations (create orders, execute strategies)
- [ ] Token refresh/rotation logic
- [ ] Batch request support
- [ ] Caching layer for frequently-accessed data
- [ ] MCP server mode (persistent process instead of per-call subprocess)
