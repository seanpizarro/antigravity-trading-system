#!/usr/bin/env python3
"""
Composer Trade API Client
Integration with Composer Trade platform for enhanced trading capabilities
"""
import requests
import json
import time
from typing import Dict, List, Optional, Any
import logging
import os
from datetime import datetime, timedelta
import subprocess

class ComposerTradeAPI:
    """
    API client for Composer Trade platform
    """

    def __init__(self):
        # Base URL from testing - api.composer.trade returns 403 (valid API endpoint)
        self.base_url = "https://api.composer.trade"  # Confirmed API endpoint

        # Firebase authentication (required per OpenAPI spec)
        self.firebase_token = os.getenv('COMPOSER_FIREBASE_TOKEN')

        # Alternative API key auth (may not work)
        self.api_key = os.getenv('COMPOSER_API_KEY')
        self.api_secret = os.getenv('COMPOSER_API_SECRET')

        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds

        # Optional MCP integration (feature-flagged)
        # If enabled, selected read-only calls can be routed via an MCP server/CLI.
        self.mcp_enabled = os.getenv("COMPOSER_MCP_ENABLED", "false").lower() in ("1", "true", "yes")
        self.mcp_command = os.getenv("COMPOSER_MCP_COMMAND")  # e.g., path to a CLI that talks to MCP
        try:
            self.mcp_timeout = float(os.getenv("COMPOSER_MCP_TIMEOUT", "8"))
        except ValueError:
            self.mcp_timeout = 8.0

        if not self.firebase_token and (not self.api_key or not self.api_secret):
            self.logger.warning(
                "⚠️  No Composer authentication configured.\n"
                "\n"
                "OPTION 1 (RECOMMENDED): Firebase Token\n"
                "  - Login to https://app.composer.trade in your browser\n"
                "  - Open DevTools (F12) → Network tab\n"
                "  - Click around the site to trigger API calls\n"
                "  - Find requests to 'api.composer.trade' or 'trading-api.composer.trade'\n"
                "  - Copy the Authorization header value (starts with 'Bearer eyJ...')\n"
                "  - Add to .env: COMPOSER_FIREBASE_TOKEN=<your_token>\n"
                "\n"
                "OPTION 2: API Key/Secret (may not work with Firebase endpoints)\n"
                "  - Add to .env: COMPOSER_API_KEY=<key>\n"
                "  - Add to .env: COMPOSER_API_SECRET=<secret>\n"
                "\n"
                "API client will continue but requests may fail with 403 errors."
            )

        self._setup_auth()

    @property
    def is_configured(self) -> bool:
        """True if some authentication is configured (Firebase or API key/secret)."""
        return bool(self.firebase_token or (self.api_key and self.api_secret))

    def _setup_auth(self):
        """Set up authentication headers based on available credentials"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'AI-Options-Trading-System/1.0'
        }

        # Prefer Firebase token (primary auth method per OpenAPI)
        if self.firebase_token:
            headers['Authorization'] = f'Bearer {self.firebase_token}'
            self.logger.info("Using Firebase authentication")
        else:
            # Fallback to API key/secret
            headers['Authorization'] = f'Bearer {self.api_key}'
            headers['X-API-Secret'] = self.api_secret
            self.logger.info("Using API key/secret authentication")

        self.session.headers.update(headers)

    def _via_mcp(self, action: str, payload: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Attempt to fulfill a request via MCP if enabled.

        Expects an MCP-aware CLI/bridge specified by COMPOSER_MCP_COMMAND that accepts
        a single JSON object on stdin and returns JSON on stdout in the shape:
            { "ok": true, "result": <any> } or { "ok": false, "error": "..." }

        Returns the result on success, or None on any failure (so we can fallback to REST).
        """
        if not (self.mcp_enabled and self.mcp_command):
            return None
        try:
            request_obj = {"tool": "composer", "action": action, "payload": payload or {}}
            proc = subprocess.run(
                [self.mcp_command],
                input=json.dumps(request_obj).encode("utf-8"),
                capture_output=True,
                timeout=self.mcp_timeout,
            )
            if proc.returncode != 0:
                self.logger.debug(f"MCP command non-zero exit ({proc.returncode}): {proc.stderr.decode(errors='ignore')}")
                return None
            try:
                data = json.loads(proc.stdout.decode("utf-8"))
            except Exception as e:
                self.logger.debug(f"MCP response JSON decode failed: {e}")
                return None
            if isinstance(data, dict) and data.get("ok") is True:
                return data.get("result")
            self.logger.debug(f"MCP returned error/invalid shape: {data}")
            return None
        except Exception as e:
            self.logger.debug(f"MCP invocation failed for action {action}: {e}")
            return None

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated API request with rate limiting"""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)

        url = f"{self.base_url}{endpoint}"
        self.last_request_time = time.time()

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=data)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Composer API request failed: {e}")
            raise

    def get_accounts_list(self) -> List[Dict]:
        """Get a list of accounts held by the user"""
        # Try MCP first (read-only, safe). Fallback to REST.
        mcp = self._via_mcp("accounts.list")
        if mcp is not None:
            return mcp
        return self._make_request('GET', '/api/v0.1/accounts/list')

    def get_account_holdings(self, account_id: str, position_type: Optional[str] = None) -> Dict:
        """Get current holdings in the account"""
        params = {'position_type': position_type} if position_type else None
        # Try MCP path
        mcp = self._via_mcp("accounts.holdings", {"account_id": account_id, **({} if not params else params)})
        if mcp is not None:
            return mcp
        return self._make_request('GET', f'/api/v0.1/accounts/{account_id}/holdings', params)

    def get_portfolio_stats(self, account_id: str) -> Dict:
        """Get aggregate portfolio statistics"""
        return self._make_request('GET', f'/api/v0.1/portfolio/accounts/{account_id}/total-stats')

    def get_holding_stats(self, account_id: str) -> Dict:
        """Get aggregate stats per holding"""
        return self._make_request('GET', f'/api/v0.1/portfolio/accounts/{account_id}/holding-stats')

    def get_portfolio_history(self, account_id: str) -> Dict:
        """Get portfolio value over time"""
        return self._make_request('GET', f'/api/v0.1/portfolio/accounts/{account_id}/portfolio-history')

    def get_options_chain(self, underlying_symbol: str, **kwargs) -> Dict:
        """Get options chain market data"""
        params = {'underlying_asset_symbol': underlying_symbol, **kwargs}
        return self._make_request('GET', '/api/v1/market-data/options/chain', params)

    def get_options_contract(self, symbol: str) -> Dict:
        """Get options contract market data"""
        return self._make_request('GET', '/api/v1/market-data/options/contract', {'symbol': symbol})

    def get_options_overview(self, symbol: str) -> Dict:
        """Get options overview for a symbol"""
        # Try MCP path
        mcp = self._via_mcp("market.options_overview", {"symbol": symbol})
        if mcp is not None:
            return mcp
        return self._make_request('GET', '/api/v1/market-data/options/overview', {'symbol': symbol})

    def get_order_requests(self, account_id: str, **kwargs) -> List[Dict]:
        """Get order requests for a broker account"""
        return self._make_request('GET', f'/api/v0.1/trading/accounts/{account_id}/order-requests', kwargs)

    def create_order_request(self, account_id: str, order_data: Dict) -> Dict:
        """Create and queue a new order request"""
        return self._make_request('POST', f'/api/v0.1/trading/accounts/{account_id}/order-requests', order_data)

    def create_symphony(self, symphony_data: Dict) -> Dict:
        """Create a new symphony (trading strategy)"""
        return self._make_request('POST', '/api/v0.1/symphonies', symphony_data)

    def update_symphony(self, symphony_id: str, symphony_data: Dict) -> Dict:
        """Update an existing symphony"""
        return self._make_request('PUT', f'/api/v0.1/symphonies/{symphony_id}', symphony_data)

    def delete_symphony(self, symphony_id: str) -> None:
        """Delete an existing symphony"""
        self._make_request('DELETE', f'/api/v0.1/symphonies/{symphony_id}')

    def run_backtest(self, symphony_id: str, backtest_config: Dict) -> Dict:
        """Run a backtest for a symphony"""
        return self._make_request('POST', f'/api/v0.1/symphonies/{symphony_id}/backtest', backtest_config)

    def run_general_backtest(self, backtest_config: Dict) -> Dict:
        """Run a general backtest"""
        return self._make_request('POST', '/api/v0.1/backtest', backtest_config)

    def invest_in_symphony(self, account_id: str, symphony_id: str, invest_data: Dict) -> Dict:
        """Invest more money into a symphony"""
        return self._make_request('POST', f'/api/v0.1/deploy/accounts/{account_id}/symphonies/{symphony_id}/invest', invest_data)

    def withdraw_from_symphony(self, account_id: str, symphony_id: str, withdraw_data: Dict) -> Dict:
        """Withdraw money from a symphony"""
        return self._make_request('POST', f'/api/v0.1/deploy/accounts/{account_id}/symphonies/{symphony_id}/withdraw', withdraw_data)

    def get_market_hours(self) -> Dict:
        """Get market hours for the next week"""
        return self._make_request('GET', '/api/v0.1/deploy/market-hours')

    def get_trading_signals(self) -> List[Dict]:
        """Get trading signals from Composer"""
        return self._make_request('GET', '/signals')

    def get_analytics(self, timeframe: str = '1D') -> Dict:
        """Get trading analytics"""
        return self._make_request('GET', '/analytics', {'timeframe': timeframe})

    def sync_positions(self, positions: List[Dict]) -> Dict:
        """Sync positions with Composer platform"""
        return self._make_request('POST', '/sync/positions', {'positions': positions})

    def get_risk_metrics(self) -> Dict:
        """Get risk metrics from Composer"""
        return self._make_request('GET', '/risk/metrics')

    def execute_strategy(self, strategy_name: str, parameters: Dict) -> Dict:
        """Execute a trading strategy on Composer"""
        data = {
            'strategy': strategy_name,
            'parameters': parameters,
            'timestamp': datetime.now().isoformat()
        }
        return self._make_request('POST', '/strategies/execute', data)

    def get_strategy_performance(self, strategy_id: str) -> Dict:
        """Get performance metrics for a strategy"""
        return self._make_request('GET', f'/strategies/{strategy_id}/performance')

    def create_alert(self, alert_config: Dict) -> Dict:
        """Create a trading alert"""
        return self._make_request('POST', '/alerts', alert_config)

    def get_alerts(self) -> List[Dict]:
        """Get active alerts"""
        return self._make_request('GET', '/alerts')

    def test_connection(self) -> bool:
        """Test API connection using accounts list endpoint"""
        try:
            self.get_accounts_list()
            self.logger.info("Composer API connection successful")
            return True
        except Exception as e:
            self.logger.error(f"Composer API connection failed: {e}")
            return False