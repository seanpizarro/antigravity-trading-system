# paper_trading.py - UPDATED TO USE YOUR API
import logging
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
import json

class PaperTradingEngine:
    def __init__(self, tastytrade_client):
        self.tt = tastytrade_client
        self.logger = logging.getLogger(__name__)
        self.db_conn = self._init_database()
        
        # 🎯 Use real account data or paper defaults
        account_data = self.tt.get_account_data()
        self.paper_balance = account_data.total_value if account_data.total_value > 0 else 50000.00
        
    def _init_database(self):
        """Initialize SQLite database for trade journal"""
        conn = sqlite3.connect('paper_trading.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                symbol TEXT,
                option_type TEXT,
                strike REAL,
                expiration TEXT,
                action TEXT,
                quantity INTEGER,
                entry_price REAL,
                exit_price REAL,
                entry_time DATETIME,
                exit_time DATETIME,
                pnl REAL,
                status TEXT,
                ai_confidence REAL,
                strategy TEXT,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                total_value REAL,
                cash_balance REAL,
                positions_value REAL,
                daily_pnl REAL
            )
        ''')
        
        conn.commit()
        self.logger.info("✅ Paper trading database initialized")
        return conn
    
    def execute_paper_trade(self, signal: Dict) -> Dict:
        """Execute a paper trade using your TastyTrade API"""
        try:
            # Validate signal
            if not self._validate_signal(signal):
                return {'success': False, 'error': 'Invalid signal'}
            
            symbol = signal['symbol']
            option_type = signal.get('option_type', 'call')
            premium = signal.get('premium', 0)
            quantity = self._calculate_position_size(signal)
            
            # 🎯 Use your API's paper trading method
            result = self.tt.execute_paper_trade(
                symbol=symbol,
                order_type='LIMIT',
                quantity=quantity,
                price=premium
            )
            
            if result.get('success'):
                # Record trade in database
                trade_id = f"PAPER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self._record_trade({
                    'trade_id': trade_id,
                    'symbol': symbol,
                    'option_type': option_type,
                    'strike': signal.get('strike'),
                    'action': 'BUY',
                    'quantity': quantity,
                    'entry_price': premium,
                    'entry_time': datetime.now(),
                    'status': 'OPEN',
                    'ai_confidence': signal.get('ai_confidence', 0),
                    'strategy': 'AI_SCANNER'
                })
                
                self.logger.info(f"📝 PAPER TRADE EXECUTED: {symbol} {quantity} @ ${premium}")
                
                return {
                    'success': True,
                    'trade_id': trade_id,
                    'symbol': symbol,
                    'quantity': quantity,
                    'entry_price': premium,
                    'order_data': result
                }
            else:
                return {'success': False, 'error': result.get('error', 'Order failed')}
                
        except Exception as e:
            self.logger.error(f"❌ Paper trade execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_signal(self, signal: Dict) -> bool:
        """Validate trade signal before execution"""
        required_fields = ['symbol', 'premium', 'ai_confidence']
        
        for field in required_fields:
            if field not in signal:
                self.logger.error(f"❌ Missing required field: {field}")
                return False
        
        if signal.get('ai_confidence', 0) < 0.6:
            self.logger.warning("⚠️ Signal below confidence threshold")
            return False
            
        trade_cost = signal['premium'] * 100  # Options are 100 shares
        if trade_cost > self.paper_balance * 0.1:
            self.logger.warning("⚠️ Trade exceeds position size limit")
            return False
            
        return True
    
    def _calculate_position_size(self, signal: Dict) -> int:
        """Calculate position size based on risk management"""
        premium = signal['premium']
        confidence = signal.get('ai_confidence', 0.5)
        account_size = self.paper_balance
        
        kelly_fraction = max(0.01, min(0.1, confidence - 0.5))
        max_trade_value = account_size * kelly_fraction
        quantity = int(max_trade_value / (premium * 100))
        
        return max(1, min(10, quantity))
    
    def _record_trade(self, trade_data: Dict):
        """Record trade in database"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            INSERT INTO trades (
                trade_id, symbol, option_type, strike, action, quantity,
                entry_price, entry_time, status, ai_confidence, strategy
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data['trade_id'],
            trade_data['symbol'],
            trade_data['option_type'],
            trade_data.get('strike'),
            trade_data['action'],
            trade_data['quantity'],
            trade_data['entry_price'],
            trade_data['entry_time'],
            trade_data['status'],
            trade_data.get('ai_confidence', 0),
            trade_data.get('strategy', 'AI_SCANNER')
        ))
        self.db_conn.commit()
    
    def get_portfolio_summary(self) -> Dict:
        """Get paper trading portfolio summary"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                SELECT symbol, option_type, strike, quantity, entry_price, ai_confidence
                FROM trades WHERE status = 'OPEN'
            ''')
            open_positions = cursor.fetchall()
            
            positions_value = 0
            for position in open_positions:
                positions_value += position[3] * position[4] * 100
            
            cash_balance = self.paper_balance - positions_value
            
            return {
                'total_value': self.paper_balance,
                'cash_balance': cash_balance,
                'positions_value': positions_value,
                'open_positions': len(open_positions),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting portfolio summary: {e}")
            return {}