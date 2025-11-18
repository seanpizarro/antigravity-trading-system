#!/usr/bin/env python3
"""
Composer MCP Bridge
A minimal CLI that accepts MCP-style JSON requests on stdin and proxies to Composer API.

Expected input on stdin:
{
  "tool": "composer",
  "action": "accounts.list" | "accounts.holdings" | "market.options_overview",
  "payload": { ... }
}

Output on stdout:
{
  "ok": true,
  "result": <any>
}
or
{
  "ok": false,
  "error": "message"
}

Environment variables:
- COMPOSER_FIREBASE_TOKEN (primary)
- COMPOSER_API_KEY + COMPOSER_API_SECRET (fallback)
"""
import sys
import json
import os
import requests
import logging

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s", stream=sys.stderr)
logger = logging.getLogger(__name__)


class ComposerMCPBridge:
    """Minimal bridge to Composer API for MCP integration"""
    
    def __init__(self):
        self.base_url = "https://api.composer.trade"
        self.firebase_token = os.getenv("COMPOSER_FIREBASE_TOKEN")
        self.api_key = os.getenv("COMPOSER_API_KEY")
        self.api_secret = os.getenv("COMPOSER_API_SECRET")
        
        if not self.firebase_token and (not self.api_key or not self.api_secret):
            raise ValueError("Missing Composer credentials in environment")
        
        self.session = requests.Session()
        self._setup_auth()
    
    def _setup_auth(self):
        """Configure authentication headers"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Composer-MCP-Bridge/1.0"
        }
        
        if self.firebase_token:
            headers["Authorization"] = f"Bearer {self.firebase_token}"
            logger.info("Using Firebase authentication")
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Secret"] = self.api_secret
            logger.info("Using API key/secret authentication")
        
        self.session.headers.update(headers)
    
    def _make_request(self, method: str, endpoint: str, params=None, data=None):
        """Make authenticated request to Composer API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                resp = self.session.get(url, params=params, timeout=10)
            elif method == "POST":
                resp = self.session.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Composer API error: {e}")
            raise
    
    def accounts_list(self, payload):
        """Get list of accounts"""
        return self._make_request("GET", "/api/v0.1/accounts/list")
    
    def accounts_holdings(self, payload):
        """Get account holdings"""
        account_id = payload.get("account_id")
        if not account_id:
            raise ValueError("Missing account_id in payload")
        
        params = {}
        if "position_type" in payload:
            params["position_type"] = payload["position_type"]
        
        return self._make_request("GET", f"/api/v0.1/accounts/{account_id}/holdings", params=params)
    
    def market_options_overview(self, payload):
        """Get options overview for a symbol"""
        symbol = payload.get("symbol")
        if not symbol:
            raise ValueError("Missing symbol in payload")
        
        return self._make_request("GET", "/api/v1/market-data/options/overview", params={"symbol": symbol})
    
    def handle_action(self, action: str, payload: dict):
        """Route action to appropriate handler"""
        handlers = {
            "accounts.list": self.accounts_list,
            "accounts.holdings": self.accounts_holdings,
            "market.options_overview": self.market_options_overview,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unsupported action: {action}")
        
        return handler(payload)


def main():
    """Main entry point - reads JSON from stdin, writes JSON to stdout"""
    try:
        # Read request from stdin
        request_data = json.load(sys.stdin)
        
        tool = request_data.get("tool")
        action = request_data.get("action")
        payload = request_data.get("payload", {})
        
        if tool != "composer":
            raise ValueError(f"Expected tool='composer', got '{tool}'")
        
        if not action:
            raise ValueError("Missing 'action' field")
        
        # Initialize bridge and handle action
        bridge = ComposerMCPBridge()
        result = bridge.handle_action(action, payload)
        
        # Write success response
        response = {
            "ok": True,
            "result": result
        }
        json.dump(response, sys.stdout, indent=2)
        sys.exit(0)
        
    except Exception as e:
        # Write error response
        logger.error(f"Bridge error: {e}", exc_info=True)
        response = {
            "ok": False,
            "error": str(e)
        }
        json.dump(response, sys.stdout, indent=2)
        sys.exit(1)


if __name__ == "__main__":
    main()
