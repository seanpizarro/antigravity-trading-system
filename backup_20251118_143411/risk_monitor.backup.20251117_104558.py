# Educational Purpose Only - Paper Trading
"""
REAL-TIME RISK MONITOR - 24/7 portfolio risk assessment with DeepSeek intelligence
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from enum import Enum

from deepseek_analyst import DeepSeekMultiTaskAI, RiskAssessment
from jax_engine import JAXRealTimeAnalytics

class RiskLevel(Enum):
    NORMAL = 0
    CAUTION = 1
    WARNING = 2
    CRITICAL = 3

@dataclass
class RiskAlert:
    """Risk alert container"""
    level: RiskLevel
    message: str
    triggered_by: str
    timestamp: datetime
    actions: List[str]
    confidence: float

@dataclass
class PortfolioMetrics:
    """Comprehensive portfolio metrics"""
    total_value: float
    buying_power: float
    margin_usage: float
    max_drawdown: float
    portfolio_greeks: Dict[str, float]
    sector_concentration: Dict[str, float]
    strategy_mix: Dict[str, int]
    risk_score: float

class AccountRiskMonitor:
    """
    Real-time portfolio risk monitoring with DeepSeek analysis
    Continuously assesses account health and triggers protective actions
    """
    
    def __init__(self, tasty_api, deepseek_ai: DeepSeekMultiTaskAI, risk_parameters: Dict):
        self.tasty_api = tasty_api
        self.deepseek_ai = deepseek_ai
        self.risk_parameters = risk_parameters
        self.logger = logging.getLogger(__name__)
        
        # Risk thresholds
        self.thresholds = {
            'buying_power_usage': 0.7,  # 70% buying power used
            'margin_usage': 0.5,        # 50% margin used
            'max_drawdown': 0.1,        # 10% drawdown
            'sector_concentration': 0.3, # 30% in one sector
            'portfolio_delta': 100,     # Absolute delta limit
            'portfolio_gamma': 50,      # Absolute gamma limit
            'portfolio_vega': 200,      # Absolute vega limit
            'position_concentration': 0.2, # 20% in one position
        }
        
        # Alert system
        self.active_alerts = []
        self.alert_history = []
        self.last_risk_assessment = None
        
        # Performance tracking
        self.metrics_history = []
        self.risk_trend = []

    def calculate_dynamic_position_size(self, opportunity: Dict, account_balance: float) -> int:
        """Calculate position size based on multiple factors"""
        confidence = opportunity.get('ai_confidence', 0.5)
        iv = opportunity.get('implied_volatility', 20)
        premium = opportunity.get('premium', 0.50)  # Default to $0.50 if missing
        
        # Base position size (0.5% to 2% of account)
        base_size = account_balance * 0.01  # 1% default
        
        # Adjust for confidence
        confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5x to 1.0x
        
        # Adjust for volatility (smaller positions in high IV)
        iv_multiplier = 1.0 - (max(0, iv - 20) / 100)  # Reduce size as IV increases
        
        final_size = base_size * confidence_multiplier * iv_multiplier
        
        # Prevent division by zero
        if premium <= 0:
            premium = 0.50
        
        quantity = int(final_size / (premium * 100))  # Options are 100 shares
        
        return max(1, min(10, quantity))  # 1 to 10 contracts
        
    def assess_portfolio_risk(self, positions: Dict) -> RiskAssessment:
        """Assess portfolio risk with PROPER empty portfolio handling"""
        try:
            # 🎯 CRITICAL: Handle empty portfolio properly with market awareness
            if not positions or len(positions) == 0:
                # Check market conditions to determine if we should recommend entries
                market_condition = self._analyze_market_condition()
                
                if market_condition == 'bullish':
                    return RiskAssessment(
                        alert_level=1,  # Low risk but missing opportunities
                        message="Bullish market with no positions - consider strategic entries",
                        concerns=["No open positions", "Missing potential income opportunities"],
                        recommendations=["Consider opening positions in bullish market", "Start with small defined-risk trades"]
                    )
                else:
                    return RiskAssessment(
                        alert_level=0,
                        message="Portfolio is empty - ready for new opportunities",
                        concerns=[],
                        recommendations=[]
                    )
            
            # Calculate risk metrics for non-empty portfolio
            total_positions = len(positions)
            total_invested = 0
            strategy_concentration = {}
            concentration_concerns = []
            
            for position_id, position in positions.items():
                try:
                    if not position:
                        continue
                        
                    # Calculate position value
                    quantity = position.get('quantity', 0)
                    entry_price = position.get('entry_price', 0)
                    position_value = quantity * entry_price * 100
                    total_invested += position_value
                    
                    # Track strategy concentration
                    strategy = position.get('strategy_type', 'unknown')
                    strategy_concentration[strategy] = strategy_concentration.get(strategy, 0) + position_value
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Error processing position {position_id}: {e}")
                    continue
            
            # Calculate concentration risk
            max_concentration = 0
            for strategy, value in strategy_concentration.items():
                concentration = (value / total_invested) * 100 if total_invested > 0 else 0
                max_concentration = max(max_concentration, concentration)
                
                # Warn about high concentration
                if concentration > 40:
                    concern = f"High concentration in {strategy}: {concentration:.1f}%"
                    self.logger.warning(f"⚠️ {concern}")
                    concentration_concerns.append(concern)
            
            # Calculate overall risk score (0-10)
            risk_score = min(10, max_concentration / 10)  # Simple score based on concentration
            
            if risk_score >= 8:
                return RiskAssessment(
                    alert_level=8, 
                    message="Critical concentration risk", 
                    concerns=concentration_concerns,
                    recommendations=["Reduce position concentration", "Diversify across strategies"]
                )
            elif risk_score >= 5:
                return RiskAssessment(
                    alert_level=5, 
                    message="High concentration risk", 
                    concerns=concentration_concerns,
                    recommendations=["Consider diversifying positions"]
                )
            elif risk_score >= 3:
                return RiskAssessment(
                    alert_level=3, 
                    message="Moderate concentration risk", 
                    concerns=concentration_concerns,
                    recommendations=["Monitor position concentration"]
                )
            else:
                return RiskAssessment(
                    alert_level=0, 
                    message="Low risk portfolio", 
                    concerns=[],
                    recommendations=[]
                )
                
        except Exception as e:
            self.logger.error(f"❌ Risk assessment failed: {e}")
            return RiskAssessment(
                alert_level=0, 
                message="Risk assessment error", 
                concerns=[str(e)],
                recommendations=[]
            )
    
    def _check_position_limits(self, current_positions: Dict) -> bool:
        """Check if position count is within limits"""
        max_positions = self.risk_parameters.get('max_open_positions', 5)
        return len(current_positions) < max_positions
    
    def _check_risk_limits(self, opportunity: Dict) -> bool:
        """Check if trade risk is within limits"""
        trade_risk = opportunity.get('max_risk', 0)
        return trade_risk <= self.risk_parameters.get('max_risk_per_trade', 30)
    
    def _check_daily_limits(self) -> bool:
        """Check daily trading limits"""
        # Simplified - in production would track daily trades
        return True
    
    def approve_trade(self, opportunity: Dict, current_positions: Dict) -> bool:
        """Approve trade with mock data support"""
        try:
            # 🎯 ENHANCED: Handle mock data
            if opportunity.get('data_source', '').startswith('mock'):
                self.logger.info(f"🤖 Mock trade approval: {opportunity['symbol']}")
                return True
            
            # Existing approval logic for real trades
            if not self._check_position_limits(current_positions):
                return False
                
            if not self._check_risk_limits(opportunity):
                return False
                
            if not self._check_daily_limits():
                return False
                
            return True
                
        except Exception as e:
            self.logger.error(f"❌ Trade approval error: {e}")
            return False  # Deny on error for safety
    
    def approve_management_action(self, action) -> bool:
        """
        Approve or reject management action based on risk
        """
        try:
            # Check if action increases risk beyond limits
            if self._increases_risk_beyond_limits(action):
                return False
                
            # Check if action violates any risk parameters
            if self._violates_risk_parameters(action):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Management action approval failed: {e}")
            return False
    
    def get_protective_actions(self, alert: RiskAlert) -> List[Dict]:
        """
        Get recommended protective actions for risk alerts
        """
        protective_actions = []
        
        if alert.level in [RiskLevel.WARNING, RiskLevel.CRITICAL]:
            # Close most risky positions
            risky_positions = self._identify_risky_positions()
            for position in risky_positions:
                protective_actions.append({
                    'action_type': 'CLOSE',
                    'position_id': position['position_id'],
                    'reason': 'risk_reduction',
                    'priority': 'high'
                })
            
            # Reduce position sizes
            protective_actions.append({
                'action_type': 'REDUCE_SIZE',
                'reason': 'risk_management',
                'new_max_size': self.risk_parameters['max_risk_per_trade'] * 0.5  # 50% reduction
            })
        
        return protective_actions
    
    def _calculate_portfolio_metrics(self, account_data, open_positions: Dict) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        
        # Basic account metrics - handle both dict and AccountData
        if hasattr(account_data, 'total_value'):
            total_value = account_data.total_value
            buying_power = account_data.buying_power
            margin_used = account_data.margin_used
        else:
            total_value = account_data.get('total_value', 0)
            buying_power = account_data.get('buying_power', 0)
            margin_used = account_data.get('margin_used', 0)
        
        margin_usage = margin_used / total_value if total_value > 0 else 0
        
        # Portfolio Greeks
        portfolio_greeks = self._calculate_portfolio_greeks(open_positions)
        
        # Sector concentration
        sector_concentration = self._calculate_sector_concentration(open_positions)
        
        # Strategy mix
        strategy_mix = self._calculate_strategy_mix(open_positions)
        
        # Risk score (0-1, higher is riskier)
        risk_score = self._calculate_risk_score(
            portfolio_greeks, sector_concentration, margin_usage, len(open_positions)
        )
        
        return PortfolioMetrics(
            total_value=total_value,
            buying_power=buying_power,
            margin_usage=margin_usage,
            max_drawdown=self._calculate_max_drawdown(),
            portfolio_greeks=portfolio_greeks,
            sector_concentration=sector_concentration,
            strategy_mix=strategy_mix,
            risk_score=risk_score
        )
    
    def _calculate_portfolio_greeks(self, open_positions: Dict) -> Dict[str, float]:
        """Calculate portfolio-level Greeks"""
        # This would use JAX engine in production
        # Simplified for example
        total_delta = sum(pos.get('delta', 0) for pos in open_positions.values())
        total_gamma = sum(pos.get('gamma', 0) for pos in open_positions.values())
        total_theta = sum(pos.get('theta', 0) for pos in open_positions.values())
        total_vega = sum(pos.get('vega', 0) for pos in open_positions.values())
        
        return {
            'delta': total_delta,
            'gamma': total_gamma,
            'theta': total_theta,
            'vega': total_vega
        }
    
    def _calculate_sector_concentration(self, open_positions: Dict) -> Dict[str, float]:
        """Calculate sector concentration percentages"""
        sector_values = {}
        total_value = sum(pos.get('current_value', 0) for pos in open_positions.values())
        
        for position in open_positions.values():
            sector = position.get('sector', 'unknown')
            sector_values[sector] = sector_values.get(sector, 0) + position.get('current_value', 0)
        
        return {sector: value/total_value if total_value > 0 else 0 
                for sector, value in sector_values.items()}
    
    def _calculate_strategy_mix(self, open_positions: Dict) -> Dict[str, int]:
        """Calculate strategy type distribution"""
        mix = {}
        for position in open_positions.values():
            strategy = position.get('strategy_type', 'unknown')
            mix[strategy] = mix.get(strategy, 0) + 1
        return mix
    
    def _calculate_risk_score(self, greeks: Dict, sector_conc: Dict, 
                            margin_usage: float, position_count: int) -> float:
        """Calculate overall risk score (0-1)"""
        scores = []
        
        # Greek-based risk (with zero-division protection)
        if self.thresholds['portfolio_delta'] > 0:
            delta_risk = min(abs(greeks.get('delta', 0)) / self.thresholds['portfolio_delta'], 1.0)
            scores.append(delta_risk)
        
        if self.thresholds['portfolio_gamma'] > 0:
            gamma_risk = min(abs(greeks.get('gamma', 0)) / self.thresholds['portfolio_gamma'], 1.0)
            scores.append(gamma_risk)
        
        if self.thresholds['portfolio_vega'] > 0:
            vega_risk = min(abs(greeks.get('vega', 0)) / self.thresholds['portfolio_vega'], 1.0)
            scores.append(vega_risk)
        
        # Concentration risk
        max_sector_conc = max(sector_conc.values()) if sector_conc else 0
        if self.thresholds['sector_concentration'] > 0:
            sector_risk = min(max_sector_conc / self.thresholds['sector_concentration'], 1.0)
            scores.append(sector_risk)
        
        # Margin risk
        if self.thresholds['margin_usage'] > 0:
            margin_risk = min(margin_usage / self.thresholds['margin_usage'], 1.0)
            scores.append(margin_risk)
        
        # Position count risk
        max_positions = self.risk_parameters.get('max_open_positions', 5)
        if max_positions > 0:
            position_risk = min(position_count / max_positions, 1.0)
            scores.append(position_risk)
        
        # Return average, or 0 if no scores
        return sum(scores) / len(scores) if scores else 0.0
    
    def _check_automated_triggers(self, metrics: PortfolioMetrics, 
                                open_positions: Dict) -> List[RiskAlert]:
        """Check automated risk triggers"""
        alerts = []
        
        # Buying power usage
        bp_usage = 1 - (metrics.buying_power / metrics.total_value) if metrics.total_value > 0 else 0
        if bp_usage > self.thresholds['buying_power_usage']:
            alerts.append(RiskAlert(
                level=RiskLevel.WARNING,
                message=f"High buying power usage: {bp_usage:.1%}",
                triggered_by="buying_power",
                timestamp=datetime.now(),
                actions=["Reduce position sizes", "Close some positions"],
                confidence=0.9
            ))
        
        # Margin usage
        if metrics.margin_usage > self.thresholds['margin_usage']:
            alerts.append(RiskAlert(
                level=RiskLevel.CRITICAL,
                message=f"High margin usage: {metrics.margin_usage:.1%}",
                triggered_by="margin_usage",
                timestamp=datetime.now(),
                actions=["Immediately reduce margin usage", "Close positions"],
                confidence=0.95
            ))
        
        # Sector concentration
        max_sector = max(metrics.sector_concentration.values()) if metrics.sector_concentration else 0
        if max_sector > self.thresholds['sector_concentration']:
            alerts.append(RiskAlert(
                level=RiskLevel.WARNING,
                message=f"High sector concentration: {max_sector:.1%}",
                triggered_by="sector_concentration",
                timestamp=datetime.now(),
                actions=["Diversify sectors", "Reduce concentrated positions"],
                confidence=0.8
            ))
        
        # Greek exposures
        if abs(metrics.portfolio_greeks.get('delta', 0)) > self.thresholds['portfolio_delta']:
            alerts.append(RiskAlert(
                level=RiskLevel.WARNING,
                message=f"High delta exposure: {metrics.portfolio_greeks['delta']:.0f}",
                triggered_by="delta_exposure",
                timestamp=datetime.now(),
                actions=["Hedge delta", "Close directional positions"],
                confidence=0.85
            ))
        
        return alerts
    
    def _combine_risk_assessments(self, deepseek_assessment: RiskAssessment,
                                automated_alerts: List[RiskAlert]) -> RiskAssessment:
        """Combine DeepSeek assessment with automated alerts"""
        
        # Start with DeepSeek assessment
        final_alert_level = deepseek_assessment.alert_level
        final_concerns = deepseek_assessment.concerns.copy()
        final_recommendations = deepseek_assessment.recommendations.copy()
        
        # Incorporate automated alerts
        for alert in automated_alerts:
            if alert.level.value > final_alert_level:
                final_alert_level = alert.level.value
            
            final_concerns.append(alert.message)
            final_recommendations.extend(alert.actions)
        
        # Remove duplicates
        final_concerns = list(set(final_concerns))
        final_recommendations = list(set(final_recommendations))
        
        return RiskAssessment(
            alert_level=final_alert_level,
            message=deepseek_assessment.message,
            concerns=final_concerns,
            recommendations=final_recommendations
        )
    
    def _check_basic_risk_parameters(self, opportunity, open_positions: Dict) -> bool:
        """Check basic risk parameters for new trade"""
        
        # Position count limit
        if len(open_positions) >= self.risk_parameters.get('max_open_positions', 5):
            self.logger.warning("Position count limit reached")
            return False
        
        # Daily trade limit (tracked elsewhere, but check here too)
        # This would need access to daily trade count
        
        # Risk per trade
        trade_risk = opportunity.parameters.get('max_risk', 0)
        if trade_risk > self.risk_parameters.get('max_risk_per_trade', 30):
            self.logger.warning(f"Trade risk {trade_risk} exceeds limit")
            return False
        
        return True
    
    def _check_portfolio_impact(self, opportunity, open_positions: Dict) -> bool:
        """Check portfolio impact of new trade"""
        
        # Simulate adding this trade to portfolio
        simulated_positions = open_positions.copy()
        # simulated_positions['new_trade'] = opportunity  # This would need proper formatting
        
        # Calculate new portfolio Greeks
        # new_greeks = self._calculate_portfolio_greeks(simulated_positions)
        
        # Check Greek limits
        # if abs(new_greeks.get('delta', 0)) > self.thresholds['portfolio_delta']:
        #     return False
        
        # This is simplified - in production would use JAX engine for accurate simulation
        return True
    
    def _check_concentration_limits(self, opportunity, open_positions: Dict) -> bool:
        """Check concentration limits"""
        
        # Sector concentration
        opportunity_sector = self._get_ticker_sector(opportunity.ticker)
        current_sector_count = sum(1 for pos in open_positions.values() 
                                 if pos.get('sector') == opportunity_sector)
        
        sector_limit = self.risk_parameters.get('sector_limits', {}).get(opportunity_sector, 2)
        if current_sector_count >= sector_limit:
            self.logger.warning(f"Sector {opportunity_sector} limit reached")
            return False
        
        return True
    
    def _check_market_conditions(self, opportunity) -> bool:
        """Check current market conditions"""
        
        # Avoid trading during high volatility if strategy doesn't suit
        current_vix = self._get_vix_level()
        if (opportunity.strategy_type == 'CREDIT_SPREAD' and current_vix > 30):
            self.logger.warning("High VIX not suitable for credit spreads")
            return False
        
        # Check for market holidays or early closes
        if self._is_market_holiday():
            self.logger.warning("Market holiday - avoiding trades")
            return False
        
        return True
    
    def _increases_risk_beyond_limits(self, action) -> bool:
        """Check if management action increases risk beyond limits"""
        # Simplified - in production would simulate the action's impact
        return False
    
    def _violates_risk_parameters(self, action) -> bool:
        """Check if management action violates risk parameters"""
        # Simplified - in production would check against all risk parameters
        return False
    
    def _identify_risky_positions(self) -> List[Dict]:
        """Identify most risky positions for protective actions"""
        # This would analyze positions based on various risk metrics
        # Simplified for example
        return []
    
    def _trigger_risk_alert(self, assessment: RiskAssessment, metrics: PortfolioMetrics):
        """Trigger risk alert and add to active alerts"""
        alert_level = RiskLevel.CRITICAL if assessment.alert_level >= 7 else RiskLevel.WARNING
        
        alert = RiskAlert(
            level=alert_level,
            message=assessment.message,
            triggered_by="combined_assessment",
            timestamp=datetime.now(),
            actions=assessment.recommendations,
            confidence=0.8
        )
        
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        
        self.logger.warning(
            f"🚨 RISK ALERT Level {assessment.alert_level}: {assessment.message}"
        )
    
    def _update_risk_trend(self, assessment: RiskAssessment, risk_score: float):
        """Update risk trend for historical analysis"""
        trend_point = {
            'timestamp': datetime.now(),
            'risk_level': assessment.alert_level,
            'risk_score': risk_score,
            'concerns': assessment.concerns
        }
        
        self.risk_trend.append(trend_point)
        
        # Keep only last 7 days of data
        cutoff = datetime.now() - timedelta(days=7)
        self.risk_trend = [point for point in self.risk_trend 
                          if point['timestamp'] > cutoff]
    
    def _get_market_conditions(self) -> Dict:
        """Get current market conditions"""
        return {
            'vix': self._get_vix_level(),
            'market_trend': 'bullish',  # Simplified
            'economic_events': [],
            'sector_rotation': {}
        }
    
    def _analyze_market_condition(self) -> str:
        """Analyze current market condition to determine trading opportunities"""
        market_data = self._get_market_conditions()
        vix = market_data.get('vix', 20)
        trend = market_data.get('market_trend', 'neutral')
        
        # Simple market condition logic
        if trend == 'bullish' and vix < 25:
            return 'bullish'
        elif trend == 'bearish' or vix > 30:
            return 'bearish'
        else:
            return 'neutral'
    
    def _get_vix_level(self) -> float:
        """Get current VIX level"""
        # In production, this would call market data API
        return 18.5
    
    def _is_market_holiday(self) -> bool:
        """Check if today is a market holiday"""
        # In production, this would check holiday calendar
        return False
    
    def _get_ticker_sector(self, ticker: str) -> str:
        """Get sector for a ticker"""
        # Simplified sector mapping
        sector_map = {
            'SPY': 'etf', 'QQQ': 'etf', 'IWM': 'etf', 'DIA': 'etf',
            'AAPL': 'technology', 'MSFT': 'technology', 'GOOGL': 'technology',
            'AMZN': 'technology', 'META': 'technology', 'NVDA': 'technology',
            'JPM': 'financial', 'BAC': 'financial', 'GS': 'financial',
            'XOM': 'energy', 'CVX': 'energy',
            'DIS': 'discretionary', 'NFLX': 'discretionary'
        }
        return sector_map.get(ticker, 'unknown')
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown (simplified)"""
        # In production, this would use historical account value data
        return 0.05  # 5% example
    
    def get_risk_report(self) -> Dict:
        """Generate comprehensive risk report"""
        return {
            'current_risk_level': self.last_risk_assessment.alert_level if self.last_risk_assessment else 0,
            'risk_trend_7d': self.risk_trend[-7:] if len(self.risk_trend) >= 7 else self.risk_trend,
            'active_alerts': len(self.active_alerts),
            'recent_alerts_24h': [
                alert for alert in self.alert_history
                if alert.timestamp > datetime.now() - timedelta(hours=24)
            ],
            'risk_metrics': self.last_risk_assessment.__dict__ if self.last_risk_assessment else {}
        }
    
    def clear_resolved_alerts(self):
        """Clear alerts that have been resolved"""
        # In production, this would have logic to determine when alerts are resolved
        self.active_alerts = []

    def approve_trade(self, opportunity: Dict, current_positions: Dict) -> bool:
        """Approve trade with mock data support"""
        try:
            # 🎯 ENHANCED: Handle mock data
            if opportunity.get('data_source', '').startswith('mock'):
                self.logger.info(f"🤖 Mock trade approval: {opportunity['symbol']}")
                return True
            
            # Existing approval logic for real trades
            if not self._check_position_limits(current_positions):
                return False
                
            if not self._check_risk_limits(opportunity):
                return False
                
            if not self._check_daily_limits():
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Trade approval error: {e}")
            return False  # Deny on error for safety