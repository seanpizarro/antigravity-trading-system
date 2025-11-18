"""
ACTIVE TRADE MANAGER - DeepSeek-managed position management with JAX optimization
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from deepseek_analyst import DeepSeekMultiTaskAI, ManagementDecision
from jax_engine import JAXRealTimeAnalytics, PositionMetrics

@dataclass
class ManagementAction:
    """Trade management action to execute"""
    position_id: str
    action_type: str  # HOLD, CLOSE, ROLL, ADJUST
    parameters: Dict
    confidence: float
    rationale: str

class ActiveTradeManager:
    """
    Manages all open positions with DeepSeek intelligence and JAX optimization
    Continuously monitors and makes roll/close/adjust decisions
    """
    
    def __init__(self, deepseek_ai: DeepSeekMultiTaskAI, 
                 jax_engine: JAXRealTimeAnalytics,
                 tasty_api):
        self.deepseek_ai = deepseek_ai
        self.jax_engine = jax_engine
        self.tasty_api = tasty_api
        self.logger = logging.getLogger(__name__)
        
        # Management rules and thresholds
        self.management_rules = {
            'min_confidence': 0.7,
            'max_daily_management_actions': 5,
            'position_check_interval': 300,  # 5 minutes
            'emergency_close_threshold': -0.8,  # Close at 80% max loss
            'profit_targets': {
                'credit_spread': 0.5,  # 50% of max profit
                'debit_spread': 0.5    # 50% of max profit
            },
            'time_decay_threshold': 21,  # DTE threshold for roll consideration
            'volatility_alert_threshold': 0.3  # 30% IV change
        }
        
        # Track management history
        self.management_history = []
        self.daily_action_count = 0
        
    def manage_all_positions(self, positions: Dict) -> List[ManagementAction]:
        """Manage all positions with ROBUST error handling"""
        actions = []
        
        for position_id, position in positions.items():
            try:
                # 🎯 CRITICAL: Handle all possible data issues
                if not position or not isinstance(position, dict):
                    self.logger.warning(f"⚠️ Invalid position data for {position_id}")
                    continue
                
                # Extract data with safe defaults (position is a dict)
                symbol = position.get('symbol') or position.get('ticker', 'UNKNOWN')
                entry_time_str = position.get('entry_time')
                underlying_price = position.get('underlying_price', 0)
                
                # 🎯 FIX: Handle entry_time conversion safely
                try:
                    if isinstance(entry_time_str, str):
                        entry_time = datetime.fromisoformat(entry_time_str.replace('Z', '+00:00'))
                    else:
                        entry_time = datetime.now()
                        self.logger.warning(f"🔄 Using current time for position {position_id}")
                except Exception as e:
                    self.logger.warning(f"🔄 Invalid entry_time for {position_id}, using current time: {e}")
                    entry_time = datetime.now()
                
                # Only manage positions that are at least 1 hour old
                time_held = datetime.now() - entry_time
                if time_held.total_seconds() < 3600:  # 1 hour
                    continue
                
                # Calculate current position metrics (simplified)
                try:
                    entry_price = position.get('entry_price', 0)
                    quantity = position.get('quantity', 0)
                    
                    # Simple P&L calculation (in production, use current market price)
                    current_value = entry_price * quantity * 100  # Options are 100 shares
                    
                    # Management logic based on time held and strategy
                    strategy = position.get('strategy_type', 'ai_recommended')
                    confidence = position.get('ai_confidence', 0.5)
                    
                    # Close positions that have been held too long or low confidence
                    if time_held.total_seconds() > 86400:  # 24 hours
                        actions.append(ManagementAction(
                            action_type="CLOSE",
                            position_id=position_id,
                            reason="Time-based close (24h limit)"
                        ))
                    elif confidence < 0.3 and time_held.total_seconds() > 7200:  # 2 hours
                        actions.append(ManagementAction(
                            action_type="CLOSE", 
                            position_id=position_id,
                            reason="Low confidence close"
                        ))
                        
                except Exception as e:
                    self.logger.error(f"❌ Error calculating position metrics for {position_id}: {e}")
                    continue
                    
            except Exception as e:
                self.logger.error(f"❌ Error managing position {position_id}: {e}")
                continue
        
        return actions
    
    def _is_position_too_new(self, position: Dict) -> bool:
        """Check if position is too new to manage (avoid overtrading)"""
        # 🎯 FIX: Handle missing entry_time gracefully
        entry_time_str = position.entry_time
        if not entry_time_str:
            self.logger.warning(f"⚠️ Position missing entry_time, allowing management")
            return False  # Allow management if entry_time is missing
        
        try:
            entry_time = datetime.fromisoformat(entry_time_str)
            time_since_entry = datetime.now() - entry_time
            return time_since_entry < timedelta(hours=4)  # 4 hour cooldown
        except (ValueError, TypeError) as e:
            self.logger.warning(f"⚠️ Invalid entry_time format: {e}")
            return False  # Allow management if format is invalid
    
    def _get_current_market_conditions(self, position: Dict) -> Dict:
        """Get relevant market conditions for position management"""
        return {
            'vix': self._get_vix_level(),
            'market_trend': self._get_market_trend(),
            'sector_performance': self._get_sector_performance(position.sector),
            'volatility_regime': self._get_volatility_regime(),
            'economic_events': self._get_upcoming_events(position.ticker)
        }
    
    def _should_execute_management(self, decision: ManagementDecision, 
                                 position: Dict) -> bool:
        """
        Validate if management decision should be executed
        """
        # Check confidence threshold
        if decision.confidence < self.management_rules['min_confidence']:
            return False
            
        # Don't overtrade - limit actions per position
        recent_actions = self._get_recent_actions_for_position(position.position_id)
        if len(recent_actions) >= 2:  # Max 2 actions per position per day
            return False
            
        # Check if action is different from current state
        if decision.action_type == "HOLD":
            return False
            
        # Additional validation based on position specifics
        if not self._validate_management_decision(decision, position):
            return False
            
        return True
    
    def _validate_management_decision(self, decision: ManagementDecision, 
                                   position: Dict) -> bool:
        """Validate management decision against position state"""
        
        if decision.action_type == "CLOSE":
            return self._validate_close_decision(decision, position)
        elif decision.action_type == "ROLL":
            return self._validate_roll_decision(decision, position)
        elif decision.action_type == "ADJUST":
            return self._validate_adjust_decision(decision, position)
        else:
            return False
    
    def _validate_close_decision(self, decision: ManagementDecision, 
                               position: Dict) -> bool:
        """Validate close decision"""
        # Check if already at profit target
        current_pnl_pct = getattr(position, 'current_pnl', 0) / getattr(position, 'max_loss', 1)
        profit_target = self.management_rules['profit_targets'].get(
            position.strategy_type, 0.5
        )
        
        if current_pnl_pct >= profit_target:
            return True
            
        # Check if approaching expiration
        if position.dte <= 7:  # 7 days to expiration
            return True
            
        # Check if thesis is broken (large underlying move)
        if self._is_thesis_broken(position):
            return True
            
        return decision.confidence > 0.8  # High confidence required
    
    def _validate_roll_decision(self, decision: ManagementDecision, 
                              position: Dict) -> bool:
        """Validate roll decision"""
        # 🎯 FIX: Handle missing entry_time gracefully
        entry_time_str = position.entry_time
        if entry_time_str:
            try:
                entry_time = datetime.fromisoformat(entry_time_str)
                # Check if enough time has passed since entry
                if datetime.now() - entry_time < timedelta(days=7):
                    return False
            except (ValueError, TypeError) as e:
                self.logger.warning(f"⚠️ Invalid entry_time format in roll validation: {e}")
        
        # Check DTE threshold
        if position.dte > self.management_rules['time_decay_threshold']:
            return False
            
        # Check if roll makes economic sense
        if not self._is_roll_economical(position, decision.parameters):
            return False
            
        return True
    
    def _validate_adjust_decision(self, decision: ManagementDecision, 
                                position: Dict) -> bool:
        """Validate adjust decision"""
        # Adjustments are higher risk - require higher confidence
        if decision.confidence < 0.8:
            return False
            
        # Check if adjustment improves position
        if not self._improves_position(position, decision.parameters):
            return False
            
        return True
    
    def _is_thesis_broken(self, position: Dict) -> bool:
        """Check if original trade thesis is broken"""
        # Compare current underlying price to expected range
        current_price = position.underlying_price
        entry_price = position.entry_underlying_price
        
        # For credit spreads, thesis broken if price approaches short strike
        if position.strategy_type == 'CREDIT_SPREAD':
            short_strike = min([leg['strike'] for leg in position.legs])
            distance_to_short = abs(current_price - short_strike) / entry_price
            return distance_to_short < 0.05  # Within 5% of short strike
            
        # For debit spreads, thesis broken if price moves away from target
        else:
            expected_move = getattr(position, 'expected_move', 0.1)
            actual_move = abs(current_price - entry_price) / entry_price
            return actual_move > expected_move * 2  # Moved twice expected amount
    
    def _is_roll_economical(self, position: Dict, roll_params: Dict) -> bool:
        """Check if roll makes economic sense"""
        # Calculate roll cost
        roll_cost = roll_params.get('estimated_cost', 0)
        current_value = getattr(position, 'current_value', 0)
        
        # Roll should not cost more than 50% of current position value
        if abs(roll_cost) > abs(current_value) * 0.5:
            return False
            
        # Check if roll improves probability or reduces risk
        new_pop = roll_params.get('new_probability', 0)
        current_pop = getattr(position, 'probability_profit', 0)
        
        return new_pop > current_pop or roll_params.get('risk_reduction', 0) > 0
    
    def _improves_position(self, position: Dict, adjust_params: Dict) -> bool:
        """Check if adjustment improves position"""
        current_metrics = self.jax_engine.calculate_position_metrics(position)
        
        # Simulate adjusted position metrics
        adjusted_position = self._simulate_adjusted_position(position, adjust_params)
        adjusted_metrics = self.jax_engine.calculate_position_metrics(adjusted_position)
        
        # Adjustment should improve expected value or reduce risk
        return (adjusted_metrics.expected_value > current_metrics.expected_value or
                adjusted_metrics.greeks.delta < current_metrics.greeks.delta * 0.8)
    
    def _check_emergency_conditions(self, position: Dict, 
                                  metrics: PositionMetrics) -> Optional[ManagementAction]:
        """
        Check for emergency conditions requiring immediate action
        """
        # Check for maximum loss approach
        current_pnl_ratio = getattr(position, 'current_pnl', 0) / getattr(position, 'max_loss', 1)
        if current_pnl_ratio <= self.management_rules['emergency_close_threshold']:
            return ManagementAction(
                position_id=position.position_id,
                action_type="CLOSE",
                parameters={'reason': 'approaching_max_loss'},
                confidence=0.95,
                rationale=f"Emergency close: approaching maximum loss ({current_pnl_ratio:.1%})"
            )
        
        # Check for extreme volatility changes
        iv_change = self._get_iv_change(position)
        if abs(iv_change) > self.management_rules['volatility_alert_threshold']:
            return ManagementAction(
                position_id=position.position_id,
                action_type="CLOSE",
                parameters={'reason': 'extreme_volatility_change'},
                confidence=0.85,
                rationale=f"Emergency close: extreme IV change ({iv_change:.1%})"
            )
            
        # Check for corporate actions or news
        if self._has_dangerous_news(position.ticker):
            return ManagementAction(
                position_id=position.position_id,
                action_type="CLOSE", 
                parameters={'reason': 'dangerous_news'},
                confidence=0.9,
                rationale="Emergency close: dangerous news detected"
            )
            
        return None
    
    def _create_management_action(self, decision: ManagementDecision,
                                position: Dict, metrics: PositionMetrics) -> ManagementAction:
        """Create executable management action from decision"""
        return ManagementAction(
            position_id=position.position_id,
            action_type=decision.action_type,
            parameters=decision.parameters,
            confidence=decision.confidence,
            rationale=decision.rationale
        )
    
    def _get_recent_actions_for_position(self, position_id: str) -> List[Dict]:
        """Get recent management actions for a position"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        return [
            action for action in self.management_history
            if action['position_id'] == position_id 
            and action['timestamp'] > cutoff_time
        ]
    
    def _get_vix_level(self) -> float:
        """Get current VIX level (simplified)"""
        # In production, this would call a market data API
        return 18.5  # Example value
    
    def _get_market_trend(self) -> str:
        """Get current market trend (simplified)"""
        # In production, this would analyze SPY trend
        return "bullish"
    
    def _get_sector_performance(self, sector: str) -> float:
        """Get sector performance (simplified)"""
        # In production, this would call sector ETF data
        return 0.02  # 2% gain
    
    def _get_volatility_regime(self) -> str:
        """Get current volatility regime"""
        vix = self._get_vix_level()
        if vix < 15:
            return "low"
        elif vix < 25:
            return "normal" 
        else:
            return "high"
    
    def _get_upcoming_events(self, ticker: str) -> List[str]:
        """Get upcoming events for ticker (simplified)"""
        # In production, this would check earnings calendar
        return []
    
    def _get_iv_change(self, position: Dict) -> float:
        """Calculate IV change since entry"""
        current_iv = getattr(position, 'current_iv', 0.3)
        entry_iv = getattr(position, 'entry_iv', 0.3)
        return (current_iv - entry_iv) / entry_iv
    
    def _has_dangerous_news(self, ticker: str) -> bool:
        """Check for dangerous news (simplified)"""
        # In production, this would call news API
        return False
    
    def _simulate_adjusted_position(self, position: Dict, adjust_params: Dict) -> Dict:
        """Simulate position after adjustment"""
        # Create a copy of position with adjustments
        adjusted = position.copy()
        
        # Apply adjustments (simplified)
        if 'new_strikes' in adjust_params:
            for i, leg in enumerate(adjusted['legs']):
                if i < len(adjust_params['new_strikes']):
                    leg['strike'] = adjust_params['new_strikes'][i]
                    
        if 'new_expiration' in adjust_params:
            adjusted['expiration'] = adjust_params['new_expiration']
            adjusted['dte'] = (adjusted['expiration'] - datetime.now().date()).days
            
        return adjusted
    
    def log_management_action(self, action: ManagementAction, result: Dict):
        """Log management action and result"""
        log_entry = {
            'timestamp': datetime.now(),
            'position_id': action.position_id,
            'action_type': action.action_type,
            'confidence': action.confidence,
            'rationale': action.rationale,
            'result': result,
            'success': result.get('success', False)
        }
        self.management_history.append(log_entry)
        
        self.logger.info(
            f"Management action: {action.action_type} on {action.position_id} "
            f"(confidence: {action.confidence:.2f}) - "
            f"Success: {result.get('success', False)}"
        )