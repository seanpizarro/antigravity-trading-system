"""
ACTIVE TRADE MANAGER - DeepSeek-managed position management with JAX optimization
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from deepseek_analyst import DeepSeekMultiTaskAI, ManagementDecision
from jax_engine import JAXRealTimeAnalytics, PositionMetrics, GreekMetrics

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
        self.management_history: List[Dict] = []
        self.daily_action_count = 0

    def _improves_position(self, position: Dict, adjust_params: Dict) -> bool:
        """Check if adjustment improves position"""
        pos_dict = position.__dict__ if hasattr(position, '__dict__') else position
        current_metrics = self.jax_engine.calculate_position_metrics(pos_dict)
        adjusted_position = self._simulate_adjusted_position(pos_dict, adjust_params)
        adjusted_metrics = self.jax_engine.calculate_position_metrics(adjusted_position)
        return (adjusted_metrics.expected_value > current_metrics.expected_value or
                adjusted_metrics.greeks.delta < current_metrics.greeks.delta * 0.8)

    def _check_emergency_conditions(self, position: Dict,
                                      metrics: PositionMetrics) -> Optional[ManagementAction]:
        """Check for emergency conditions requiring immediate action"""
        current_pnl_ratio = getattr(position, 'current_pnl', 0) / getattr(position, 'max_loss', 1)
        if current_pnl_ratio <= self.management_rules['emergency_close_threshold']:
            return ManagementAction(
                position_id=getattr(position, 'position_id', 'unknown'),
                action_type="CLOSE",
                parameters={'reason': 'approaching_max_loss'},
                confidence=0.95,
                rationale=f"Emergency close: approaching maximum loss ({current_pnl_ratio:.1%})"
            )
        iv_change = self._get_iv_change(position)
        if abs(iv_change) > self.management_rules['volatility_alert_threshold']:
            return ManagementAction(
                position_id=getattr(position, 'position_id', 'unknown'),
                action_type="CLOSE",
                parameters={'reason': 'extreme_volatility_change'},
                confidence=0.85,
                rationale=f"Emergency close: extreme IV change ({iv_change:.1%})"
            )
        if self._has_dangerous_news(getattr(position, 'ticker', 'SPY')):
            return ManagementAction(
                position_id=getattr(position, 'position_id', 'unknown'),
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
            position_id=getattr(position, 'position_id', 'unknown'),
            action_type=decision.action_type,
            parameters=decision.parameters,
            confidence=decision.confidence,
            rationale=decision.rationale
        )

    def _get_recent_actions_for_position(self, position_id: str) -> List[Dict]:
        """Get recent management actions for a position"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        return [action for action in self.management_history
                if action['position_id'] == position_id and action['timestamp'] > cutoff_time]

    def _get_vix_level(self) -> float:
        """Get current VIX level (simplified)"""
        return 18.5

    def _get_market_trend(self) -> str:
        """Get current market trend (simplified)"""
        return "bullish"

    def _get_sector_performance(self, sector: str) -> float:
        """Get sector performance (simplified)"""
        return 0.02

    def _get_volatility_regime(self) -> str:
        vix = self._get_vix_level()
        if vix < 15:
            return "low"
        elif vix < 25:
            return "normal"
        else:
            return "high"

    def _get_upcoming_events(self, ticker: str) -> List[str]:
        return []

    def _get_iv_change(self, position: Dict) -> float:
        current_iv = getattr(position, 'current_iv', 0.3)
        entry_iv = getattr(position, 'entry_iv', 0.3)
        return (current_iv - entry_iv) / entry_iv

    def _has_dangerous_news(self, ticker: str) -> bool:
        return False

    def _simulate_adjusted_position(self, position: Dict, adjust_params: Dict) -> Dict:
        adjusted = position.copy()
        if 'new_strikes' in adjust_params:
            for i, leg in enumerate(adjusted.get('legs', [])):
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

    def manage_all_positions(self, positions: Dict) -> List[ManagementAction]:
        """Iterate over all positions, evaluate with DeepSeek, and return actions.
        - Skip positions newer than 1 hour.
        - Check emergency conditions first; if triggered, use that action immediately.
        - Otherwise, consult DeepSeek AI for management decision.
        """
        actions: List[ManagementAction] = []
        if not positions:
            return actions
        now = datetime.now()
        for position_id, pos in positions.items():
            entry_time_str = pos.get('entry_time')
            if entry_time_str:
                try:
                    entry_time = datetime.fromisoformat(entry_time_str)
                except Exception:
                    entry_time = None
                else:
                    if now - entry_time < timedelta(hours=1):
                        continue
            # Ensure position_id is present
            pos['position_id'] = position_id
            # Convert dict to object for DeepSeek
            position_obj = type('Position', (), pos)
            # Calculate metrics via JAX engine
            metrics = self.jax_engine.calculate_position_metrics(pos)
            
            # Check emergency conditions first
            emergency_action = self._check_emergency_conditions(position_obj, metrics)
            if emergency_action:
                actions.append(emergency_action)
                continue
            
            # Otherwise, use DeepSeek AI for decision
            market_conditions = {}
            decision = self.deepseek_ai.analyze_position_management(position_obj, metrics, market_conditions)
            action = self._create_management_action(decision, position_obj, metrics)
            actions.append(action)
        return actions