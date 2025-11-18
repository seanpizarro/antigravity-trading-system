# alpaca_api.py - Alpaca Trading API Integration
import os
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time

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
    Alpaca Trading API wrapper for paper and live trading
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://paper-api.alpaca.markets/v2"):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret
        })

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Alpaca allows higher rate limits

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make authenticated request to Alpaca API with rate limiting"""
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)

        url = f"{self.base_url}{endpoint}"
        self.last_request_time = time.time()

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Alpaca API request failed: {e}")
            raise

    def get_account(self) -> AlpacaAccountInfo:
        """Get account information"""
        try:
            data = self._make_request('GET', '/account')
            return AlpacaAccountInfo(
                account_id=data['id'],
                cash=float(data['cash']),
                portfolio_value=float(data['portfolio_value']),
                buying_power=float(data['buying_power']),
                daytrade_count=int(data['daytrade_count']),
                status=data['status']
            )
        except Exception as e:
            self.logger.error(f"Failed to get account info: {e}")
            raise

    def get_positions(self) -> List[AlpacaPosition]:
        """Get all positions"""
        try:
            data = self._make_request('GET', '/positions')
            positions = []
            for pos in data:
                positions.append(AlpacaPosition(
                    symbol=pos['symbol'],
                    qty=float(pos['qty']),
                    avg_entry_price=float(pos['avg_entry_price']),
                    market_value=float(pos['market_value']),
                    cost_basis=float(pos['cost_basis']),
                    unrealized_pl=float(pos['unrealized_pl']),
                    unrealized_plpc=float(pos['unrealized_plpc']),
                    current_price=float(pos['current_price']),
                    lastday_price=float(pos['lastday_price']),
                    change_today=float(pos['change_today'])
                ))
            return positions
        except Exception as e:
            self.logger.error(f"Failed to get positions: {e}")
            return []

    def get_position(self, symbol: str) -> Optional[AlpacaPosition]:
        """Get position for specific symbol"""
        try:
            data = self._make_request('GET', f'/positions/{symbol}')
            return AlpacaPosition(
                symbol=data['symbol'],
                qty=float(data['qty']),
                avg_entry_price=float(data['avg_entry_price']),
                market_value=float(data['market_value']),
                cost_basis=float(data['cost_basis']),
                unrealized_pl=float(data['unrealized_pl']),
                unrealized_plpc=float(data['unrealized_plpc']),
                current_price=float(data['current_price']),
                lastday_price=float(data['lastday_price']),
                change_today=float(data['change_today'])
            )
        except Exception as e:
            self.logger.error(f"Failed to get position for {symbol}: {e}")
            return None

    def place_order(self, symbol: str, qty: int, side: str, order_type: str,
                   time_in_force: str = 'day', limit_price: float = None) -> Dict:
        """
        Place an order
        Args:
            symbol: Stock symbol
            qty: Quantity
            side: 'buy' or 'sell'
            order_type: 'market', 'limit', 'stop', 'stop_limit'
            time_in_force: 'day', 'gtc', 'opg', 'cls', 'ioc', 'fok'
            limit_price: Limit price for limit orders
        """
        order_data = {
            'symbol': symbol,
            'qty': str(qty),
            'side': side,
            'type': order_type,
            'time_in_force': time_in_force
        }

        if limit_price and order_type in ['limit', 'stop_limit']:
            order_data['limit_price'] = str(limit_price)

        try:
            response = self._make_request('POST', '/orders', json=order_data)
            self.logger.info(f"Order placed: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            raise

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            self._make_request('DELETE', f'/orders/{order_id}')
            self.logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            return False

    def get_orders(self, status: str = 'open') -> List[Dict]:
        """Get orders (open, closed, all)"""
        try:
            params = {'status': status} if status != 'all' else {}
            data = self._make_request('GET', '/orders', params=params)
            return data
        except Exception as e:
            self.logger.error(f"Failed to get orders: {e}")
            return []

    def get_clock(self) -> Dict:
        """Get market clock"""
        try:
            return self._make_request('GET', '/clock')
        except Exception as e:
            self.logger.error(f"Failed to get market clock: {e}")
            return {}

    def get_asset(self, symbol: str) -> Optional[Dict]:
        """Get asset information"""
        try:
            return self._make_request('GET', f'/assets/{symbol}')
        except Exception as e:
            self.logger.error(f"Failed to get asset {symbol}: {e}")
            return None

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get latest quote for symbol"""
        try:
            return self._make_request('GET', f'/last/quote/{symbol}')
        except Exception as e:
            self.logger.error(f"Failed to get quote for {symbol}: {e}")
            return None

    def get_bars(self, symbol: str, timeframe: str = '1D', limit: int = 100) -> List[Dict]:
        """Get historical bars"""
        try:
            params = {
                'timeframe': timeframe,
                'limit': limit
            }
            return self._make_request('GET', f'/bars/{symbol}', params=params)
        except Exception as e:
            self.logger.error(f"Failed to get bars for {symbol}: {e}")
            return []

    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        clock = self.get_clock()
        return clock.get('is_open', False) if clock else False