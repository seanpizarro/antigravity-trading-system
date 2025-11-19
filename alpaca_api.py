"""
ALPACA API INTEGRATION - Paper Trading Support
"""

import requests
import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TradeResult:
    """Result of trade execution"""
    success: bool
    position_id: str
    fill_price: float
    quantity: int
    message: str
    timestamp: datetime

@dataclass
class AlpacaAccountInfo:
    """Alpaca account information"""
    account_id: str
    cash: float
    portfolio_value: float
    buying_power: float
    daytrade_count: int
    status: str

@dataclass
class AlpacaPosition:
    """Alpaca position information"""
    symbol: str
    qty: float
    avg_entry_price: float
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_plpc: float
    current_price: float
    lastday_price: float
    change_today: float

class AlpacaAPI:
    """
    Alpaca API integration for paper trading
    """
    
    def __init__(self, paper: bool = True):
        self.paper = paper
        self.logger = logging.getLogger(__name__)
        
        # Load credentials (standardized to match .env)
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_API_SECRET', os.getenv('ALPACA_SECRET_KEY'))  # Support both names
        self.base_url = os.getenv('ALPACA_BASE_URL', os.getenv('ALPACA_ENDPOINT', 'https://paper-api.alpaca.markets/v2'))
        
        if not self.api_key or not self.secret_key:
            self.logger.warning("⚠️ Alpaca credentials not found in environment")
            self.connected = False
        else:
            self.headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key,
                "Content-Type": "application/json"
            }
            
            # Rate limiting
            self.last_request_time = 0
            self.min_request_interval = 0.2  # 200ms between requests
            
            # Verify connection
            self.connected = self._verify_connection()
        
    def _verify_connection(self) -> bool:
        """Verify connection to Alpaca"""
        try:
            response = requests.get(f"{self.base_url}/account", headers=self.headers, timeout=10)
            if response.status_code == 200:
                account = response.json()
                self.logger.info(f"✅ Connected to Alpaca Paper Account: {account.get('id')} (${float(account.get('equity', 0)):,.2f})")
                return True
            else:
                self.logger.error(f"❌ Alpaca connection failed: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Alpaca connection error: {e}")
            return False

    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        if hasattr(self, 'last_request_time'):
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
            self.last_request_time = time.time()

    def get_account_balances(self) -> Dict:
        """Get account balances with rate limiting"""
        if not self.connected:
            return {}
            
        try:
            self._rate_limit()
            response = requests.get(f"{self.base_url}/account", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'net_liquidating_value': float(data.get('equity', 0)),
                    'maintenance_excess': float(data.get('buying_power', 0)),
                    'cash_balance': float(data.get('cash', 0))
                }
            return {}
        except Exception as e:
            self.logger.error(f"Error fetching Alpaca balances: {e}")
            return {}

    def get_positions(self) -> Dict:
        """Get all open positions normalized to system format"""
        if not self.connected:
            return {}
            
        positions = {}
        try:
            self._rate_limit()
            response = requests.get(f"{self.base_url}/positions", headers=self.headers, timeout=10)
            if response.status_code == 200:
                alpaca_positions = response.json()
                for pos in alpaca_positions:
                    # Normalize to system format
                    symbol = pos['symbol']
                    quantity = int(pos['qty'])
                    market_value = float(pos['market_value'])
                    
                    # Create position ID
                    position_id = f"{symbol}_{pos['asset_id']}"
                    
                    positions[position_id] = {
                        'position_id': position_id,
                        'symbol': symbol,
                        'ticker': symbol,
                        'quantity': quantity,
                        'market_value': market_value,
                        'current_price': float(pos['current_price']),
                        'average_open_price': float(pos['avg_entry_price']),
                        'unrealized_pnl': float(pos['unrealized_pl']),
                        'unrealized_pnl_percent': float(pos['unrealized_plpc']),
                        'cost_basis': float(pos['cost_basis']),
                        'asset_class': pos['asset_class'],
                        # Add option specific fields if applicable (Alpaca supports options now, but basic mapping here)
                        'strategy_type': 'EQUITY' if pos['asset_class'] == 'us_equity' else 'OPTION',
                        'legs': [{'symbol': symbol, 'quantity': quantity, 'type': pos['asset_class']}]
                    }
            return positions
        except Exception as e:
            self.logger.error(f"Error fetching Alpaca positions: {e}")
            return {}

    def execute_paper_trade(self, symbol: str, order_type: str, quantity: int, price: float = 0.0) -> Dict:
        """Execute a paper trade (wrapper for execute_trade to match TastyTradeAPI interface)"""
        order = {
            'symbol': symbol,
            'quantity': quantity,
            'action': 'buy', # Default to buy for simple paper trades
            'type': order_type
        }
        result = self.execute_trade(order)
        
        return {
            "success": result.success,
            "order_id": result.position_id,
            "symbol": symbol,
            "quantity": quantity,
            "price": price, # Alpaca fills async, so we use requested price for immediate feedback
            "message": result.message,
            "error": result.message if not result.success else None
        }

    def execute_trade(self, order: Dict) -> TradeResult:
        """Execute a trade on Alpaca with validation"""
        if not self.connected:
            return TradeResult(False, "", 0.0, 0, "Not connected to Alpaca", datetime.now())
            
        try:
            # Map system order to Alpaca order
            symbol = order.get('symbol')
            qty = order.get('quantity', 1)
            side = order.get('action', 'buy').lower()
            
            if not symbol or qty <= 0:
                return TradeResult(False, "", 0.0, 0, "Invalid order parameters", datetime.now())
            
            type = 'market'  # Default to market for now
            
            payload = {
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": type,
                "time_in_force": "day"
            }
            
            self._rate_limit()
            response = requests.post(f"{self.base_url}/orders", json=payload, headers=self.headers, timeout=10)
            
            if response.status_code == 200 or response.status_code == 201:
                order_data = response.json()
                return TradeResult(
                    success=True,
                    position_id=order_data.get('id'),
                    fill_price=0.0, # Async fill
                    quantity=qty,
                    message=f"Order submitted: {order_data.get('status')}",
                    timestamp=datetime.now()
                )
            else:
                return TradeResult(
                    success=False,
                    position_id="",
                    fill_price=0.0,
                    quantity=0,
                    message=f"Alpaca Error: {response.text}",
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            self.logger.error(f"Error executing Alpaca trade: {e}")
            return TradeResult(False, "", 0.0, 0, str(e), datetime.now())

    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        if not self.connected:
            return False
        
        try:
            self._rate_limit()
            response = requests.get(f"{self.base_url}/clock", headers=self.headers, timeout=10)
            if response.status_code == 200:
                clock = response.json()
                return clock.get('is_open', False)
            return False
        except Exception as e:
            self.logger.error(f"Error checking market status: {e}")
            return False

    def close_position(self, position_id: str) -> TradeResult:
        """Close a position by symbol or ID"""
        try:
            # Alpaca closes by symbol usually, or position ID if mapped
            # Assuming position_id contains symbol or we look it up
            # For simplicity, if position_id looks like a symbol, use it
            
            # Extract symbol if ID is composite
            symbol = position_id.split('_')[0] if '_' in position_id else position_id
            
            response = requests.delete(f"{self.base_url}/positions/{symbol}", headers=self.headers)
            
            if response.status_code == 200:
                return TradeResult(True, position_id, 0.0, 0, "Position close initiated", datetime.now())
            else:
                return TradeResult(False, position_id, 0.0, 0, f"Failed to close: {response.text}", datetime.now())
                
        except Exception as e:
            return TradeResult(False, position_id, 0.0, 0, str(e), datetime.now())