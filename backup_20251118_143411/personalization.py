# Educational Purpose Only - Paper Trading
"""
PERSONALIZATION ENGINE - Learns and adapts to user's trading style
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict

from deepseek_analyst import DeepSeekMultiTaskAI

@dataclass
class TradingStyle:
    """User's trading style profile"""
    preferred_strategies: List[str]
    risk_tolerance: str  # conservative, moderate, aggressive
    holding_period_preference: str  # short, medium, long
    success_patterns: Dict[str, float]
    avoidance_patterns: Dict[str, float]
    adaptation_factors: Dict[str, float]

@dataclass
class TradePattern:
    """Pattern identified from trade history"""
    pattern_type: str
    success_rate: float
    confidence: float
    conditions: Dict[str, any]
    recommendation: str

class PersonalizedTradingAI:
    """
    Learns user's trading style and preferences over time
    Adapts system behavior based on successful patterns
    """
    
    def __init__(self, deepseek_ai: DeepSeekMultiTaskAI):
        self.deepseek_ai = deepseek_ai
        self.logger = logging.getLogger(__name__)
        
        # User profile
        self.trading_style = TradingStyle(
            preferred_strategies=['credit_spreads', 'debit_spreads'],
            risk_tolerance='conservative',
            holding_period_preference='medium',
            success_patterns={},
            avoidance_patterns={},
            adaptation_factors={}
        )
        
        # Learning data
        self.trade_history = []
        self.learning_data = {
            'strategy_performance': defaultdict(list),
            'market_condition_success': defaultdict(list),
            'time_of_day_success': defaultdict(list),
            'sector_performance': defaultdict(list)
        }
        
        # Pattern recognition
        self.identified_patterns = []
        
    def learn_from_recent_trades(self):
        """
        Learn from recent trade history to improve future performance
        Called weekly by main orchestrator
        """
        self.logger.info("🎯 Learning from recent trades")
        
        try:
            # Analyze recent trade performance
            recent_trades = self._get_recent_trades(days=30)
            
            if not recent_trades:
                self.logger.info("No recent trades to learn from")
                return
            
            # Update performance metrics
            self._update_performance_metrics(recent_trades)
            
            # Identify successful patterns
            new_patterns = self._identify_success_patterns(recent_trades)
            self.identified_patterns.extend(new_patterns)
            
            # Update trading style
            self._update_trading_style(new_patterns)
            
            # Get DeepSeek insights on patterns
            deepseek_insights = self._get_deepseek_learning_insights(recent_trades, new_patterns)
            self._incorporate_deepseek_insights(deepseek_insights)
            
            self.logger.info(f"Learning complete: Identified {len(new_patterns)} new patterns")
            
        except Exception as e:
            self.logger.error(f"Learning from trades failed: {e}")
    
    def adapt_scanning_criteria(self, base_criteria: Dict) -> Dict:
        """
        Adapt scanning criteria based on learned preferences
        """
        adapted_criteria = base_criteria.copy()
        
        # Adjust based on successful strategies
        if self.trading_style.preferred_strategies:
            strategy_weights = self._calculate_strategy_weights()
            adapted_criteria['strategy_weights'] = strategy_weights
        
        # Adjust risk parameters based on tolerance
        risk_adjustments = self._calculate_risk_adjustments()
        adapted_criteria['risk_parameters'].update(risk_adjustments)
        
        # Prioritize successful sectors
        successful_sectors = self._get_successful_sectors()
        if successful_sectors:
            adapted_criteria['sector_priorities'] = successful_sectors
        
        return adapted_criteria
    
    def adapt_management_rules(self, base_rules: Dict) -> Dict:
        """
        Adapt position management rules based on learned behavior
        """
        adapted_rules = base_rules.copy()
        
        # Adjust profit targets based on historical success
        profit_adjustments = self._calculate_profit_target_adjustments()
        adapted_rules['profit_targets'].update(profit_adjustments)
        
        # Adjust holding periods based on preference
        if self.trading_style.holding_period_preference == 'short':
            adapted_rules['time_decay_threshold'] = min(adapted_rules['time_decay_threshold'], 14)
        elif self.trading_style.holding_period_preference == 'long':
            adapted_rules['time_decay_threshold'] = max(adapted_rules['time_decay_threshold'], 28)
        
        return adapted_rules
    
    def get_personalized_recommendations(self, opportunities: List) -> List:
        """
        Get personalized recommendations based on user's style
        """
        scored_opportunities = []
        
        for opportunity in opportunities:
            # Calculate personalization score
            personalization_score = self._calculate_personalization_score(opportunity)
            
            # Adjust opportunity score
            adjusted_opportunity = opportunity.copy()
            adjusted_opportunity.confidence = (
                opportunity.confidence * 0.7 + personalization_score * 0.3
            )
            
            scored_opportunities.append(adjusted_opportunity)
        
        return sorted(scored_opportunities, key=lambda x: x.confidence, reverse=True)
    
    def _get_recent_trades(self, days: int = 30) -> List[Dict]:
        """Get recent trades from history"""
        cutoff = datetime.now() - timedelta(days=days)
        return [trade for trade in self.trade_history 
                if trade['timestamp'] > cutoff]
    
    def _update_performance_metrics(self, trades: List[Dict]):
        """Update performance metrics from trades"""
        for trade in trades:
            # Strategy performance
            strategy = trade.get('strategy_type', 'unknown')
            success = trade.get('success', False)
            self.learning_data['strategy_performance'][strategy].append(success)
            
            # Market condition performance
            market_condition = trade.get('market_condition', 'normal')
            self.learning_data['market_condition_success'][market_condition].append(success)
            
            # Time of day performance
            hour = trade['timestamp'].hour
            time_category = 'morning' if hour < 12 else 'afternoon' if hour < 17 else 'evening'
            self.learning_data['time_of_day_success'][time_category].append(success)
            
            # Sector performance
            sector = trade.get('sector', 'unknown')
            self.learning_data['sector_performance'][sector].append(success)
    
    def _identify_success_patterns(self, trades: List[Dict]) -> List[TradePattern]:
        """Identify patterns from successful trades"""
        patterns = []
        
        # Analyze strategy patterns
        strategy_patterns = self._analyze_strategy_patterns(trades)
        patterns.extend(strategy_patterns)
        
        # Analyze market condition patterns
        market_patterns = self._analyze_market_condition_patterns(trades)
        patterns.extend(market_patterns)
        
        # Analyze timing patterns
        timing_patterns = self._analyze_timing_patterns(trades)
        patterns.extend(timing_patterns)
        
        # Filter patterns by confidence
        confident_patterns = [p for p in patterns if p.confidence > 0.7]
        
        return confident_patterns
    
    def _analyze_strategy_patterns(self, trades: List[Dict]) -> List[TradePattern]:
        """Analyze patterns related to strategy types"""
        patterns = []
        
        # Group trades by strategy
        strategy_groups = defaultdict(list)
        for trade in trades:
            strategy_groups[trade.get('strategy_type', 'unknown')].append(trade)
        
        # Analyze each strategy
        for strategy, strategy_trades in strategy_groups.items():
            success_rate = self._calculate_success_rate(strategy_trades)
            confidence = self._calculate_confidence(strategy_trades)
            
            if len(strategy_trades) >= 5:  # Minimum sample size
                patterns.append(TradePattern(
                    pattern_type=f"strategy_{strategy}",
                    success_rate=success_rate,
                    confidence=confidence,
                    conditions={'strategy': strategy},
                    recommendation=f"Consider more {strategy} trades" if success_rate > 0.7 
                                 else f"Reduce {strategy} trades"
                ))
        
        return patterns
    
    def _analyze_market_condition_patterns(self, trades: List[Dict]) -> List[TradePattern]:
        """Analyze patterns related to market conditions"""
        patterns = []
        
        # Group by VIX levels
        vix_groups = defaultdict(list)
        for trade in trades:
            vix_level = 'low' if trade.get('vix', 20) < 15 else 'high' if trade.get('vix', 20) > 25 else 'normal'
            vix_groups[vix_level].append(trade)
        
        for vix_level, vix_trades in vix_groups.items():
            if len(vix_trades) >= 3:
                success_rate = self._calculate_success_rate(vix_trades)
                confidence = self._calculate_confidence(vix_trades)
                
                patterns.append(TradePattern(
                    pattern_type=f"vix_{vix_level}",
                    success_rate=success_rate,
                    confidence=confidence,
                    conditions={'vix_level': vix_level},
                    recommendation=f"Trade more in {vix_level} VIX environments" if success_rate > 0.7 
                                 else f"Be cautious in {vix_level} VIX environments"
                ))
        
        return patterns
    
    def _analyze_timing_patterns(self, trades: List[Dict]) -> List[TradePattern]:
        """Analyze patterns related to trade timing"""
        patterns = []
        
        # Group by day of week
        dow_groups = defaultdict(list)
        for trade in trades:
            dow = trade['timestamp'].strftime('%A')
            dow_groups[dow].append(trade)
        
        for dow, dow_trades in dow_groups.items():
            if len(dow_trades) >= 3:
                success_rate = self._calculate_success_rate(dow_trades)
                
                patterns.append(TradePattern(
                    pattern_type=f"timing_{dow}",
                    success_rate=success_rate,
                    confidence=self._calculate_confidence(dow_trades),
                    conditions={'day_of_week': dow},
                    recommendation=f"Focus trading on {dow}" if success_rate > 0.7 
                                 else f"Reduce trading on {dow}"
                ))
        
        return patterns
    
    def _update_trading_style(self, new_patterns: List[TradePattern]):
        """Update trading style based on new patterns"""
        
        # Update preferred strategies
        strategy_success = {}
        for pattern in new_patterns:
            if pattern.pattern_type.startswith('strategy_'):
                strategy = pattern.conditions['strategy']
                strategy_success[strategy] = pattern.success_rate
        
        if strategy_success:
            best_strategy = max(strategy_success, key=strategy_success.get)
            if strategy_success[best_strategy] > 0.6:  # Only update if successful
                if best_strategy not in self.trading_style.preferred_strategies:
                    self.trading_style.preferred_strategies.append(best_strategy)
        
        # Update success patterns
        for pattern in new_patterns:
            if pattern.success_rate > 0.7:
                self.trading_style.success_patterns[pattern.pattern_type] = pattern.success_rate
            elif pattern.success_rate < 0.4:
                self.trading_style.avoidance_patterns[pattern.pattern_type] = pattern.success_rate
    
    def _get_deepseek_learning_insights(self, trades: List[Dict], patterns: List[TradePattern]) -> Dict:
        """Get DeepSeek insights on trading patterns"""
        
        prompt = f"""
        TRADING STYLE ANALYSIS AND LEARNING
        
        RECENT TRADES (Last 30 days):
        {json.dumps(trades, indent=2, default=str)}
        
        IDENTIFIED PATTERNS:
        {json.dumps([p.__dict__ for p in patterns], indent=2)}
        
        CURRENT TRADING STYLE:
        {json.dumps(self.trading_style.__dict__, indent=2)}
        
        ANALYSIS REQUESTED:
        1. What are the key strengths in my trading approach?
        2. What patterns should I focus on or avoid?
        3. How should I adapt my strategy selection?
        4. What risk management adjustments would help?
        5. Any other personalized recommendations?
        
        Please provide specific, actionable insights for improvement.
        """
        
        try:
            # This would call DeepSeek API in production
            # For now, return mock insights
            return {
                'strengths': ['Good risk management', 'Consistent strategy application'],
                'improvements': ['Diversify across more sectors', 'Adjust profit targets based on market conditions'],
                'recommendations': ['Focus on credit spreads in low VIX environments', 'Reduce trading frequency on Mondays']
            }
        except:
            return {}
    
    def _incorporate_deepseek_insights(self, insights: Dict):
        """Incorporate DeepSeek insights into trading style"""
        if 'recommendations' in insights:
            for recommendation in insights['recommendations']:
                # Simple keyword matching for adaptation
                if 'credit spread' in recommendation.lower() and 'low vix' in recommendation.lower():
                    self.trading_style.adaptation_factors['credit_spreads_low_vix'] = 1.2
                elif 'reduce' in recommendation.lower() and 'monday' in recommendation.lower():
                    self.trading_style.adaptation_factors['reduce_monday_trading'] = 0.5
    
    def _calculate_strategy_weights(self) -> Dict[str, float]:
        """Calculate strategy weights based on performance"""
        weights = {}
        total_trades = sum(len(trades) for trades in self.learning_data['strategy_performance'].values())
        
        for strategy, trades in self.learning_data['strategy_performance'].items():
            if trades:
                success_rate = sum(trades) / len(trades)
                # Weight based on success rate and sample size
                weight = success_rate * (len(trades) / total_trades)
                weights[strategy] = weight
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
        
        return weights
    
    def _calculate_risk_adjustments(self) -> Dict[str, float]:
        """Calculate risk parameter adjustments"""
        adjustments = {}
        
        # Adjust based on overall success rate
        all_trades = [trade for trades in self.learning_data['strategy_performance'].values() 
                     for trade in trades]
        overall_success = sum(all_trades) / len(all_trades) if all_trades else 0.5
        
        if overall_success > 0.7:
            # Successful trader - can take slightly more risk
            adjustments['max_risk_per_trade'] = 1.1  # 10% increase
        elif overall_success < 0.4:
            # Struggling - reduce risk
            adjustments['max_risk_per_trade'] = 0.8  # 20% decrease
        
        return adjustments
    
    def _calculate_profit_target_adjustments(self) -> Dict[str, float]:
        """Calculate profit target adjustments"""
        adjustments = {}
        
        # Analyze if we're closing too early or too late
        early_closes = sum(1 for trade in self.trade_history 
                          if trade.get('closed_early', False) and trade.get('success', False))
        total_closes = sum(1 for trade in self.trade_history if trade.get('success', False))
        
        if total_closes > 0:
            early_close_rate = early_closes / total_closes
            if early_close_rate > 0.3:  # 30% of successful trades closed early
                adjustments['credit_spread'] = 0.6  # Increase to 60% profit target
            elif early_close_rate < 0.1:  # Rarely close early
                adjustments['credit_spread'] = 0.4  # Decrease to 40% profit target
        
        return adjustments
    
    def _get_successful_sectors(self) -> Dict[str, float]:
        """Get sectors with highest success rates"""
        sector_success = {}
        
        for sector, trades in self.learning_data['sector_performance'].items():
            if trades:
                success_rate = sum(trades) / len(trades)
                if len(trades) >= 3:  # Minimum sample
                    sector_success[sector] = success_rate
        
        # Return top 3 sectors by success rate
        top_sectors = dict(sorted(sector_success.items(), key=lambda x: x[1], reverse=True)[:3])
        return top_sectors
    
    def _calculate_personalization_score(self, opportunity) -> float:
        """Calculate personalization score for an opportunity"""
        score = 0.5  # Base score
        
        # Strategy preference
        if opportunity.strategy_type in self.trading_style.preferred_strategies:
            score += 0.2
        
        # Sector preference
        sector = self._get_opportunity_sector(opportunity)
        if sector in self._get_successful_sectors():
            score += 0.15
        
        # Market condition alignment
        if self._matches_success_patterns(opportunity):
            score += 0.15
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_opportunity_sector(self, opportunity) -> str:
        """Get sector for an opportunity"""
        # Simplified sector mapping
        sector_map = {
            'SPY': 'etf', 'QQQ': 'etf', 'IWM': 'etf', 'DIA': 'etf',
            'AAPL': 'technology', 'MSFT': 'technology', 'GOOGL': 'technology',
            'AMZN': 'technology', 'META': 'technology', 'NVDA': 'technology',
            'JPM': 'financial', 'BAC': 'financial', 'GS': 'financial',
            'XOM': 'energy', 'CVX': 'energy',
            'DIS': 'discretionary', 'NFLX': 'discretionary'
        }
        return sector_map.get(opportunity.ticker, 'unknown')
    
    def _matches_success_patterns(self, opportunity) -> bool:
        """Check if opportunity matches successful patterns"""
        # Simplified pattern matching
        current_vix = self._get_current_vix()
        vix_level = 'low' if current_vix < 15 else 'high' if current_vix > 25 else 'normal'
        
        # Check if this VIX level has been successful
        vix_pattern = f"vix_{vix_level}"
        if vix_pattern in self.trading_style.success_patterns:
            return self.trading_style.success_patterns[vix_pattern] > 0.6
        
        return False
    
    def _get_current_vix(self) -> float:
        """Get current VIX level"""
        # In production, this would call market data API
        return 18.5
    
    def _calculate_success_rate(self, trades: List[Dict]) -> float:
        """Calculate success rate from trades"""
        if not trades:
            return 0.0
        successful_trades = sum(1 for trade in trades if trade.get('success', False))
        return successful_trades / len(trades)
    
    def _calculate_confidence(self, trades: List[Dict]) -> float:
        """Calculate confidence level based on sample size"""
        # Basic confidence calculation based on sample size
        sample_size = len(trades)
        if sample_size >= 10:
            return 0.9
        elif sample_size >= 5:
            return 0.7
        elif sample_size >= 3:
            return 0.5
        else:
            return 0.3
    
    def add_trade_to_history(self, trade: Dict):
        """Add a completed trade to history for learning"""
        trade['timestamp'] = datetime.now()
        self.trade_history.append(trade)
        
        # Keep only last 365 days of history
        cutoff = datetime.now() - timedelta(days=365)
        self.trade_history = [
            trade for trade in self.trade_history 
            if trade['timestamp'] > cutoff
        ]
    
    def get_style_report(self) -> Dict:
        """Get current trading style report"""
        return {
            'trading_style': self.trading_style.__dict__,
            'identified_patterns': [p.__dict__ for p in self.identified_patterns],
            'performance_metrics': {
                'total_trades_learned': len(self.trade_history),
                'overall_success_rate': self._calculate_success_rate(self.trade_history),
                'pattern_count': len(self.identified_patterns)
            },
            'adaptation_summary': {
                'strategy_weights': self._calculate_strategy_weights(),
                'successful_sectors': self._get_successful_sectors(),
                'risk_adjustments': self._calculate_risk_adjustments()
            }
        }