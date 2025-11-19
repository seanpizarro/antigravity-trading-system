# multi_broker_api.py - Multi-Broker Trading API Support
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from config import TradingConfig
from dual_tastytrade_api import DualTastyTradeAPI
from alpaca_api import AlpacaAPI, AlpacaAccountInfo, AlpacaPosition

class BrokerType(Enum):
    TASTYTRADE = "tastytrade"
    ALPACA = "alpaca"

@dataclass
class UnifiedAccountInfo:
    """Unified account information across brokers"""
    broker: str
    account_id: str
    cash: float
    portfolio_value: float
    buying_power: float
    status: str
    is_paper: bool = True

@dataclass
class UnifiedPosition:
    """Unified position information across brokers"""
    broker: str
    symbol: str
    quantity: float
    avg_entry_price: float
    market_value: float
    unrealized_pl: float
    current_price: float

class MultiBrokerAPI:
    """
    Multi-broker API supporting TastyTrade and Alpaca
    """

    def __init__(self, preferred_broker: str = None):
        self.logger = logging.getLogger(__name__)
        self.config = TradingConfig()

        # Initialize available brokers
        self.brokers = {}
        self.active_broker = None
        self.broker_health = {}  # Track broker connection status

        # Initialize TastyTrade if credentials available
        if self.config.tastytrade_credentials and self.config.tastytrade_credentials.get('client_id'):
            try:
                self.brokers[BrokerType.TASTYTRADE] = DualTastyTradeAPI()
                self.broker_health[BrokerType.TASTYTRADE] = True
                self.logger.info("✅ TastyTrade API initialized")
            except Exception as e:
                self.broker_health[BrokerType.TASTYTRADE] = False
                self.logger.warning(f"❌ Failed to initialize TastyTrade: {e}")

        # Initialize Alpaca if credentials available
        if self.config.alpaca_credentials and self.config.alpaca_credentials.get('api_key'):
            try:
                alpaca = AlpacaAPI()  # Use default initialization
                if alpaca.connected:  # Check if connection succeeded
                    self.brokers[BrokerType.ALPACA] = alpaca
                    self.broker_health[BrokerType.ALPACA] = True
                    self.logger.info("✅ Alpaca API initialized")
                else:
                    self.broker_health[BrokerType.ALPACA] = False
                    self.logger.warning("❌ Alpaca connection failed")
            except Exception as e:
                self.broker_health[BrokerType.ALPACA] = False
                self.logger.warning(f"❌ Failed to initialize Alpaca: {e}")

        # Set active broker (prefer healthy brokers)
        if preferred_broker:
            broker_type = BrokerType(preferred_broker.lower())
            if broker_type in self.brokers and self.broker_health.get(broker_type, False):
                self.active_broker = broker_type
            else:
                self.logger.warning(f"⚠️  Preferred broker {preferred_broker} not available")
        
        # If no active broker set, choose first healthy broker
        if not self.active_broker:
            for broker_type in self.brokers.keys():
                if self.broker_health.get(broker_type, False):
                    self.active_broker = broker_type
                    break

        if self.active_broker:
            self.logger.info(f"🎯 Active broker: {self.active_broker.value}")
        else:
            self.logger.warning("⚠️  No healthy brokers available")

    def get_account_info(self) -> Optional[UnifiedAccountInfo]:
        """Get unified account information"""
        if not self.active_broker or self.active_broker not in self.brokers:
            return None

        try:
            if self.active_broker == BrokerType.TASTYTRADE:
                # Get TastyTrade account info
                balances = self.brokers[self.active_broker].get_account_balances()
                accounts = self.brokers[self.active_broker].get_all_accounts()
                
                # Use paper account as primary
                paper_account = accounts.get('paper')
                if paper_account:
                    paper_balance = balances.get('paper', 0)
                    return UnifiedAccountInfo(
                        broker="tastytrade",
                        account_id=paper_account.account_number,
                        cash=paper_balance,  # Approximate cash as total balance
                        portfolio_value=paper_balance,
                        buying_power=paper_balance,  # Approximate buying power
                        status="active",
                        is_paper=True
                    )

            elif self.active_broker == BrokerType.ALPACA:
                # Get Alpaca account info
                account = self.brokers[self.active_broker].get_account()
                return UnifiedAccountInfo(
                    broker="alpaca",
                    account_id=account.account_id,
                    cash=account.cash,
                    portfolio_value=account.portfolio_value,
                    buying_power=account.buying_power,
                    status=account.status,
                    is_paper="paper" in self.config.alpaca_credentials.get('base_url', '')
                )

        except Exception as e:
            self.logger.error(f"Failed to get account info from {self.active_broker.value}: {e}")
            return None

    def get_positions(self) -> List[UnifiedPosition]:
        """Get unified positions across all accounts"""
        positions = []

        if not self.active_broker or self.active_broker not in self.brokers:
            return positions

        try:
            if self.active_broker == BrokerType.TASTYTRADE:
                # Get TastyTrade positions
                tt_positions = self.brokers[self.active_broker].get_positions()
                for symbol, pos_data in tt_positions.items():
                    if isinstance(pos_data, dict):
                        positions.append(UnifiedPosition(
                            broker="tastytrade",
                            symbol=symbol,
                            quantity=float(pos_data.get('quantity', 0)),
                            avg_entry_price=float(pos_data.get('average_price', 0)),
                            market_value=float(pos_data.get('market_value', 0)),
                            unrealized_pl=float(pos_data.get('realized_pl', 0)) + float(pos_data.get('unrealized_pl', 0)),
                            current_price=float(pos_data.get('current_price', 0))
                        ))

            elif self.active_broker == BrokerType.ALPACA:
                # Get Alpaca positions
                alpaca_positions = self.brokers[self.active_broker].get_positions()
                for pos in alpaca_positions:
                    positions.append(UnifiedPosition(
                        broker="alpaca",
                        symbol=pos.symbol,
                        quantity=pos.qty,
                        avg_entry_price=pos.avg_entry_price,
                        market_value=pos.market_value,
                        unrealized_pl=pos.unrealized_pl,
                        current_price=pos.current_price
                    ))

        except Exception as e:
            self.logger.error(f"Failed to get positions from {self.active_broker.value}: {e}")

        return positions

    def place_order(self, symbol: str, quantity: int, side: str, order_type: str = 'market',
                   limit_price: float = None) -> Optional[Dict]:
        """Place order with active broker"""
        if not self.active_broker or self.active_broker not in self.brokers:
            return None

        try:
            if self.active_broker == BrokerType.TASTYTRADE:
                # TastyTrade order placement
                opportunity = {
                    'symbol': symbol,
                    'quantity': quantity,
                    'side': side,
                    'order_type': order_type,
                    'limit_price': limit_price
                }
                return self.brokers[self.active_broker].execute_trade(opportunity)

            elif self.active_broker == BrokerType.ALPACA:
                # Alpaca order placement
                return self.brokers[self.active_broker].place_order(
                    symbol=symbol,
                    qty=quantity,
                    side=side,
                    order_type=order_type,
                    limit_price=limit_price
                )

        except Exception as e:
            self.logger.error(f"Failed to place order with {self.active_broker.value}: {e}")
            return None

    def switch_broker(self, broker_name: str) -> bool:
        """Switch active broker"""
        try:
            broker_type = BrokerType(broker_name.lower())
            if broker_type in self.brokers:
                self.active_broker = broker_type
                self.logger.info(f"🔄 Switched to broker: {broker_name}")
                return True
            else:
                self.logger.warning(f"Broker {broker_name} not available")
                return False
        except ValueError:
            self.logger.error(f"Invalid broker name: {broker_name}")
            return False

    def get_available_brokers(self) -> List[str]:
        """Get list of available and healthy brokers"""
        return [broker.value for broker in self.brokers.keys() if self.broker_health.get(broker, False)]

    def get_active_broker(self) -> Optional[str]:
        """Get currently active broker"""
        return self.active_broker.value if self.active_broker else None
    
    def get_broker_health(self) -> Dict[str, bool]:
        """Get health status of all configured brokers"""
        return {broker.value: status for broker, status in self.broker_health.items()}

    def is_market_open(self) -> bool:
        """Check if market is open"""
        if not self.active_broker or self.active_broker not in self.brokers:
            return False

        try:
            if self.active_broker == BrokerType.ALPACA:
                return self.brokers[self.active_broker].is_market_open()
            else:
                # For TastyTrade, assume market hours (could be enhanced)
                from datetime import datetime
                now = datetime.now().time()
                market_open = datetime.strptime("09:30", "%H:%M").time()
                market_close = datetime.strptime("16:00", "%H:%M").time()
                return market_open <= now <= market_close
        except Exception as e:
            self.logger.error(f"Failed to check market status: {e}")
            return False