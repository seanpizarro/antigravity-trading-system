# enhanced_paper_trading.py
import logging
from datetime import datetime
from typing import Dict, List
import sqlite3

class EnhancedPaperTradingEngine:
    """Advanced paper trading with strategy tracking and performance analytics"""
    
    def __init__(self, tastytrade_client):
        self.tt = tastytrade_client
        self.logger = logging.getLogger(__name__)
        self.db_conn = self._init_enhanced_database()
        self.paper_balance = 50000.00
        self.strategies = {
            'high_confidence': {'trades': 0, 'pnl': 0},
            'volatility_play': {'trades': 0, 'pnl': 0},
            'ai_recommended': {'trades': 0, 'pnl': 0}
        }
        
    def _init_enhanced_database(self):
        """Initialize enhanced database with strategy tracking"""
        conn = sqlite3.connect('paper_trading.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Enhanced trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_trades (
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
                strategy_type TEXT,
                risk_level TEXT,
                market_condition TEXT,
                volatility_regime TEXT,
                notes TEXT
            )
        ''')
        
        # Strategy performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT,
                total_trades INTEGER,
                winning_trades INTEGER,
                total_pnl REAL,
                win_rate REAL,
                avg_pnl REAL,
                last_updated DATETIME
            )
        ''')
        
        conn.commit()
        self.logger.info("✅ Enhanced paper trading database initialized")
        return conn
    
    def execute_paper_trade(self, signal: Dict) -> Dict:
        """Execute paper trade with COMPLETE data structure"""
        try:
            if not self._validate_enhanced_signal(signal):
                return {'success': False, 'error': 'Invalid signal'}
            
            symbol = signal['symbol']
            option_type = signal.get('option_type', 'call')
            strike = signal.get('strike', 0)
            
            # 🎯 CRITICAL FIX: Realistic premium calculation
            premium = signal.get('premium')
            if not premium or premium <= 0:
                # Use realistic premium based on strike and market data
                underlying_price = signal.get('underlying_price', strike * 1.02)
                moneyness = abs(underlying_price - strike) / underlying_price
                
                if option_type == 'call':
                    if strike < underlying_price:  # ITM
                        premium = max(1.50, (underlying_price - strike) * 0.7)
                    else:  # OTM
                        premium = max(0.75, moneyness * underlying_price * 0.4)
                else:  # put
                    if strike > underlying_price:  # ITM
                        premium = max(1.50, (strike - underlying_price) * 0.7)
                    else:  # OTM
                        premium = max(0.75, moneyness * underlying_price * 0.4)
                
                # Round to reasonable increment
                premium = round(premium, 2)
                self.logger.info(f"🎯 Calculated premium: ${premium:.2f} for {symbol}")
            
            quantity = self._calculate_enhanced_position_size(signal)
            strategy_type = self._classify_strategy(signal)
            entry_time = datetime.now()
            trade_id = f"PAPER_{entry_time.strftime('%Y%m%d_%H%M%S')}"
            
            # 🎯 CRITICAL: Build COMPLETE position data
            position_data = {
                'position_id': trade_id,
                'trade_id': trade_id,
                'symbol': symbol,
                'ticker': symbol,  # Required by trade manager
                'option_type': option_type,
                'strike': strike,
                'action': 'BUY',
                'quantity': quantity,
                'entry_price': premium,
                'entry_time': entry_time.isoformat(),  # 🎯 MUST be string for JSON
                'underlying_price': signal.get('underlying_price', strike * 1.02),  # Required
                'status': 'OPEN',
                'ai_confidence': signal.get('ai_confidence', 0.5),
                'strategy_type': strategy_type,
                'premium': premium,
                'data_source': signal.get('data_source', 'paper_trading')
            }
            
            # Execute paper trade
            result = self.tt.execute_paper_trade(
                symbol=symbol,
                order_type='LIMIT',
                quantity=quantity,
                price=premium
            )
            
            if result.get('success'):
                # Record trade with COMPLETE data
                self._record_enhanced_trade(position_data)
                self._update_strategy_tracking(strategy_type, quantity * premium * 100)
                
                self.logger.info(f"📝 ENHANCED PAPER TRADE: {symbol} {strategy_type} - {quantity} @ ${premium}")
                
                return {
                    'success': True,
                    'trade_id': trade_id,
                    'symbol': symbol,
                    'quantity': quantity,
                    'entry_price': premium,
                    'strategy_type': strategy_type,
                    'position_data': position_data,  # 🎯 Return complete data
                    'order_data': result
                }
            else:
                return {'success': False, 'error': result.get('error', 'Order failed')}
                
        except Exception as e:
            self.logger.error(f"❌ Enhanced paper trade execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _classify_strategy(self, signal: Dict) -> str:
        """Enhanced strategy classification for better diversification"""
        confidence = signal.get('ai_confidence', 0)
        iv = signal.get('implied_volatility', 20)
        option_type = signal.get('option_type', 'call')
        volume = signal.get('volume', 0)
        
        # 🎯 ENHANCED: More diverse strategy classification
        if confidence >= 0.8 and volume > 2000:
            return 'high_volume_confidence'
        elif confidence >= 0.8:
            return 'high_confidence'
        elif iv > 30 and option_type == 'put':
            return 'high_iv_put'
        elif iv > 30:
            return 'high_iv_call'
        elif volume > 1500:
            return 'momentum_play'
        elif option_type == 'call' and confidence >= 0.6:
            return 'bullish_bias'
        elif option_type == 'put' and confidence >= 0.6:
            return 'bearish_bias'
        else:
            return 'ai_recommended'
    
    def _assess_risk_level(self, signal: Dict) -> str:
        """Assess risk level of trade"""
        confidence = signal.get('ai_confidence', 0)
        premium = signal.get('premium', 0)
        
        if confidence >= 0.8 and premium > 1.0:
            return 'LOW'
        elif confidence >= 0.6:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _get_market_condition(self) -> str:
        """Get current market condition (simplified)"""
        # In production, this would analyze VIX, market trends, etc.
        return "NEUTRAL"
    
    def _get_volatility_regime(self) -> str:
        """Get current volatility regime (simplified)"""
        # In production, this would analyze VIX, historical volatility, etc.
        return "NORMAL"
    
    def _validate_enhanced_signal(self, signal: Dict) -> bool:
        """Enhanced signal validation"""
        # Check for symbol/ticker (different field names from different sources)
        if 'symbol' not in signal and 'ticker' not in signal:
            self.logger.error("❌ Missing required field: symbol/ticker")
            return False
        
        # Normalize to 'symbol' if using 'ticker'
        if 'ticker' in signal and 'symbol' not in signal:
            signal['symbol'] = signal['ticker']
        
        # Handle different confidence field names
        if 'ai_confidence' not in signal and 'confidence' not in signal:
            self.logger.error("❌ Missing required field: ai_confidence/confidence")
            return False
        
        # Normalize confidence field
        if 'confidence' in signal and 'ai_confidence' not in signal:
            signal['ai_confidence'] = signal['confidence']
        
        # Check confidence threshold
        confidence = signal.get('ai_confidence', signal.get('confidence', 0))
        if confidence < 0.5:  # Lower threshold for testing
            self.logger.warning("⚠️ Signal below confidence threshold")
            return False
        
        # Premium is optional - extract from parameters if not present
        if 'premium' not in signal:
            if 'parameters' in signal and 'premium' in signal['parameters']:
                signal['premium'] = signal['parameters']['premium']
            else:
                # Assign default premium for testing
                signal['premium'] = 0.50  # $0.50 default
                self.logger.warning("⚠️ Premium not specified, using default $0.50")
            
        trade_cost = signal['premium'] * 100  # Options are 100 shares
        if trade_cost > self.paper_balance * 0.15:  # Increased to 15% for testing
            self.logger.warning("⚠️ Trade exceeds position size limit")
            return False
            
        return True
    
    def _calculate_enhanced_position_size(self, signal: Dict) -> int:
        """Enhanced position sizing with strategy consideration"""
        premium = signal['premium']
        confidence = signal.get('ai_confidence', 0.5)
        account_size = self.paper_balance
        strategy_type = self._classify_strategy(signal)
        
        # Strategy-based position sizing
        if strategy_type == 'high_confidence':
            kelly_fraction = 0.08  # 8% for high confidence
        elif strategy_type == 'volatility_play':
            kelly_fraction = 0.05  # 5% for volatility plays
        else:
            kelly_fraction = 0.03  # 3% for standard recommendations
        
        # Adjust based on confidence
        kelly_fraction *= min(1.0, confidence / 0.7)
        
        max_trade_value = account_size * kelly_fraction
        quantity = int(max_trade_value / (premium * 100))
        
        # Ensure reasonable bounds
        return max(1, min(20, quantity))  # Increased max to 20 for testing
    
    def _record_enhanced_trade(self, trade_data: Dict):
        """Record enhanced trade with strategy information"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            INSERT INTO enhanced_trades (
                trade_id, symbol, option_type, strike, action, quantity,
                entry_price, entry_time, status, ai_confidence, strategy,
                strategy_type, risk_level, market_condition, volatility_regime, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            trade_data.get('strategy', 'AI_SCANNER'),
            trade_data.get('strategy_type', 'ai_recommended'),
            trade_data.get('risk_level', 'MEDIUM'),
            trade_data.get('market_condition', 'NEUTRAL'),
            trade_data.get('volatility_regime', 'NORMAL'),
            trade_data.get('notes', '')
        ))
        self.db_conn.commit()
    
    def _update_strategy_tracking(self, strategy_type: str, trade_value: float):
        """Update strategy performance tracking"""
        if strategy_type in self.strategies:
            self.strategies[strategy_type]['trades'] += 1
            # For now, we'll track trade value; P&L will be updated when trades close
            self.strategies[strategy_type]['trade_value'] = self.strategies[strategy_type].get('trade_value', 0) + trade_value
    
    def get_enhanced_portfolio_summary(self) -> Dict:
        """Get enhanced portfolio summary with strategy breakdown"""
        try:
            cursor = self.db_conn.cursor()
            
            # Get open positions with strategy info
            cursor.execute('''
                SELECT strategy_type, COUNT(*), SUM(quantity * entry_price * 100)
                FROM enhanced_trades 
                WHERE status = 'OPEN'
                GROUP BY strategy_type
            ''')
            strategy_positions = cursor.fetchall()
            
            positions_value = 0
            strategy_breakdown = {}
            
            for strategy, count, value in strategy_positions:
                strategy_breakdown[strategy] = {
                    'count': count,
                    'value': value if value else 0
                }
                positions_value += value if value else 0
            
            # Get performance metrics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    AVG(pnl) as avg_pnl,
                    MAX(pnl) as best_trade,
                    MIN(pnl) as worst_trade,
                    SUM(pnl) as total_pnl
                FROM enhanced_trades 
                WHERE status = 'CLOSED'
            ''')
            metrics = cursor.fetchone()
            
            total_trades = metrics[0] if metrics[0] else 0
            winning_trades = metrics[1] if metrics[1] else 0
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            cash_balance = self.paper_balance - positions_value
            
            # Safely handle None values from metrics
            avg_pnl = metrics[2] if metrics[2] is not None else 0
            best_trade = metrics[3] if metrics[3] is not None else 0
            worst_trade = metrics[4] if metrics[4] is not None else 0
            total_pnl = metrics[5] if metrics[5] is not None else 0
            
            return {
                'total_value': self.paper_balance,
                'cash_balance': cash_balance,
                'cash_available': cash_balance,
                'positions_value': positions_value,
                'open_positions': sum([breakdown['count'] for breakdown in strategy_breakdown.values()]),
                'strategy_breakdown': strategy_breakdown,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'avg_return_pct': (avg_pnl / positions_value * 100) if positions_value > 0 and avg_pnl else 0,
                'best_trade': best_trade,
                'worst_trade': worst_trade,
                'total_pnl': total_pnl,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting enhanced portfolio summary: {e}")
            return {
                'total_value': self.paper_balance,
                'cash_balance': self.paper_balance,
                'cash_available': self.paper_balance,
                'positions_value': 0,
                'open_positions': 0,
                'strategy_breakdown': {},
                'total_trades': 0,
                'win_rate': 0,
                'avg_return_pct': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'total_pnl': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_positions(self):
        """Get current positions for web display"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                SELECT trade_id, symbol, option_type, strike, expiration, 
                       quantity, entry_price, entry_time, strategy_type
                FROM enhanced_trades 
                WHERE status = 'OPEN'
            ''')
            rows = cursor.fetchall()
            
            positions = []
            for row in rows:
                positions.append({
                    'trade_id': row[0],
                    'symbol': row[1],
                    'option_type': row[2],
                    'strike': row[3],
                    'expiration': row[4],
                    'quantity': row[5],
                    'entry_price': row[6],
                    'entry_time': row[7],
                    'strategy_type': row[8],
                    'current_pnl': 0,  # Would calculate from current market price
                    'days_held': (datetime.now() - datetime.fromisoformat(row[7])).days if row[7] else 0
                })
            
            return positions
        except Exception as e:
            self.logger.error(f"❌ Error getting positions: {e}")
            return []
    
    def get_balance(self):
        """Get current paper balance"""
        return self.paper_balance
    
    def get_total_pnl(self):
        """Calculate total P&L from closed trades"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT SUM(pnl) FROM enhanced_trades WHERE status = "CLOSED"')
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except Exception as e:
            self.logger.error(f"❌ Error calculating total P&L: {e}")
            return 0
    
    def get_performance_metrics(self):
        """Get performance metrics for web display"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    AVG(pnl) as avg_pnl,
                    MAX(pnl) as best_trade,
                    MIN(pnl) as worst_trade
                FROM enhanced_trades 
                WHERE status = 'CLOSED'
            ''')
            row = cursor.fetchone()
            
            total_trades = row[0] if row[0] else 0
            winning_trades = row[1] if row[1] else 0
            
            return {
                'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                'avg_return': row[2] if row[2] else 0,
                'total_trades': total_trades,
                'best_trade': row[3] if row[3] else 0,
                'worst_trade': row[4] if row[4] else 0
            }
        except Exception as e:
            self.logger.error(f"❌ Error getting performance metrics: {e}")
            return {
                'win_rate': 0,
                'avg_return': 0,
                'total_trades': 0,
                'best_trade': 0,
                'worst_trade': 0
            }
    
    def is_market_open(self):
        """Check if market is open"""
        from market_utils import is_market_open
        return is_market_open()