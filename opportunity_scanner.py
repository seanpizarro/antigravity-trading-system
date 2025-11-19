# In opportunity_scanner.py - OPTIMIZED VERSION
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List
import random
from hybrid_market_data import hybrid_data
from market_utils import is_market_open

# opportunity_scanner.py - ENHANCE FOR AFTER-HOURS
class OpportunityScanner:
    def __init__(self, jax_engine, tastytrade_client=None):
        self.jax_engine = jax_engine
        self.market_data = hybrid_data
        if tastytrade_client:
            self.market_data.tt = tastytrade_client
        self.logger = logging.getLogger(__name__)
        self.fast_mode = True
        self.market_hours_only = False  # 🎯 NEW: Allow after-hours scanning
    
    def scan_opportunities(self) -> List[Dict]:
        """Scan for opportunities with automatic mock data fallback"""
        
        if not is_market_open():
            self.logger.info("🌙 MARKET CLOSED - Using enhanced mock opportunities")
            opportunities = self._create_mock_opportunities()
            
            # Log the mock opportunities (standardized dict access)
            for opp in opportunities:
                symbol = opp.get('symbol', 'UNKNOWN')
                strategy = opp.get('strategy', 'N/A')
                premium = opp.get('premium', 0)
                self.logger.info(f"🎯 MOCK OPPORTUNITY: {symbol} {strategy} - ${premium:.2f}")
            
            return opportunities
        else:
            # Normal scanning logic for market hours
            self.logger.info("🟢 MARKET OPEN - Scanning live opportunities")
            if self.fast_mode:
                return self._scan_fast()
            else:
                return self._scan_comprehensive()
        
    def _calculate_opportunity_score(self, opportunity: Dict) -> float:
        """Calculate comprehensive opportunity score"""
        scores = []
        
        # AI Confidence (40% weight)
        scores.append(opportunity.get('ai_confidence', 0) * 0.4)
        
        # Volume quality (20% weight)
        volume_score = min(opportunity.get('volume', 0) / 2000, 1.0)
        scores.append(volume_score * 0.2)
        
        # Liquidity score (20% weight)
        spread = opportunity.get('bid_ask_spread', 0.1)
        spread_score = max(0, 1 - (spread / 0.2))  # Prefer spreads < $0.20
        scores.append(spread_score * 0.2)
        
        # IV Rank (20% weight) - prefer moderate IV
        iv = opportunity.get('implied_volatility', 20)
        iv_score = 1 - abs(iv - 25) / 50  # Prefer IV around 25%
        scores.append(max(0, iv_score) * 0.2)
        
        return sum(scores)
    
    def _scan_fast(self) -> List[Dict]:
        """Fast scan with after-hours support"""
        self.logger.info("⚡ FAST MODE: Scanning for opportunities...")
        start_time = time.time()
        
        try:
            # Get opportunities quickly
            opportunities = self.market_data.scan_opportunities_fast()
            
            # 🎯 ENHANCED: If no opportunities found, try with relaxed filters
            if not opportunities and not self._is_market_hours():
                self.logger.info("🌙 After-hours: Using relaxed filters...")
                opportunities = self._scan_with_relaxed_filters()
            
            if not opportunities:
                self.logger.warning("⚠️ No opportunities found even with relaxed filters")
                return []
            
            # Quick AI scoring on top opportunities
            opportunities_to_score = opportunities[:15]  # 🎯 Increased from 10 to 15
            scored_opportunities = self._analyze_with_ai_fast(opportunities_to_score)
            
            total_time = time.time() - start_time
            self.logger.info(f"✅ FAST SCAN: {len(scored_opportunities)} opportunities in {total_time:.1f}s")
            
            return scored_opportunities
            
        except Exception as e:
            self.logger.error(f"❌ Error in fast scan: {e}")
            return []
    
    def _scan_with_relaxed_filters(self) -> List[Dict]:
        """Scan with relaxed filters for after-hours or low-liquidity periods"""
        try:
            # Use the market data scanner but with different parameters
            opportunities = self.market_data.scan_opportunities_fast()
            
            # If still no opportunities, create some mock opportunities for testing
            if not opportunities:
                return self._create_mock_opportunities()
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"❌ Error in relaxed scan: {e}")
            return self._create_mock_opportunities()
    
    def _calculate_realistic_premium(self, option_type: str, strike: float, underlying_price: float, 
                                      iv: float, days_to_exp: int) -> float:
        """Calculate realistic premium based on option type, moneyness, IV, and DTE"""
        moneyness = abs(strike - underlying_price) / underlying_price
        
        # Base premium calculation
        if option_type == 'call':
            if strike < underlying_price:  # ITM call
                intrinsic_value = underlying_price - strike
                time_value = max(1.50, moneyness * underlying_price * 0.1 * (iv / 30))
                base_premium = intrinsic_value + time_value
            else:  # OTM call
                base_premium = random.uniform(0.50, 3.00) * (iv / 30) * (days_to_exp / 21)
        else:  # put
            if strike > underlying_price:  # ITM put
                intrinsic_value = strike - underlying_price
                time_value = max(1.50, moneyness * underlying_price * 0.1 * (iv / 30))
                base_premium = intrinsic_value + time_value
            else:  # OTM put
                base_premium = random.uniform(0.50, 3.00) * (iv / 30) * (days_to_exp / 21)
        
        # Adjust for days to expiration (time decay)
        dte_factor = (days_to_exp / 30) ** 0.5  # Square root for time decay curve
        premium = base_premium * dte_factor
        
        # Clamp to realistic range
        return max(0.50, min(premium, 6.00))
    
    def _create_mock_opportunities(self) -> List[Dict]:
        """Generate realistic mock opportunities that match market conditions"""
        self.logger.info("🧪 Creating enhanced mock opportunities with realistic patterns...")
        
        # Strategy-option type alignment rules
        strategy_option_alignment = {
            'bullish_bias': {'preferred_type': 'call', 'ratio': 0.9},  # 90% calls
            'bearish_bias': {'preferred_type': 'put', 'ratio': 0.9},   # 90% puts
            'momentum_play': {'preferred_type': 'call', 'ratio': 0.8}, # 80% calls
            'put_spread': {'preferred_type': 'put', 'ratio': 1.0},     # 100% puts
            'volatility_play': {'preferred_type': 'both', 'ratio': 0.5}, # 50/50
            'strangle': {'preferred_type': 'both', 'ratio': 0.5},
            'iron_condor': {'preferred_type': 'both', 'ratio': 0.5},
            'theta_decay': {'preferred_type': 'both', 'ratio': 0.5}
        }
        
        # Base patterns for different market conditions
        market_scenarios = {
            'bullish': {
                'symbols': ['SPY', 'QQQ', 'MSFT', 'NVDA', 'AAPL'],
                'strategies': ['bullish_bias', 'momentum_play'],
                'call_ratio': 0.7  # 70% calls in bullish market
            },
            'volatile': {
                'symbols': ['SPY', 'QQQ', 'TSLA', 'AMD', 'MRNA'],
                'strategies': ['volatility_play', 'strangle', 'iron_condor'],
                'call_ratio': 0.5
            },
            'bearish': {
                'symbols': ['SPY', 'IWM', 'DIA', 'XLF', 'XLE'],
                'strategies': ['bearish_bias', 'put_spread'],
                'call_ratio': 0.3
            }
        }
        
        # Select a random market scenario
        scenario_name = random.choice(list(market_scenarios.keys()))
        scenario = market_scenarios[scenario_name]
        opportunities = []
        
        self.logger.info(f"🎭 Using {scenario_name.upper()} market scenario")
        
        for symbol in random.sample(scenario['symbols'], 3):
            strategy = random.choice(scenario['strategies'])
            
            # Determine option type based on STRATEGY alignment (more important than scenario)
            alignment = strategy_option_alignment.get(strategy, {'preferred_type': 'call', 'ratio': 0.5})
            
            if alignment['preferred_type'] == 'call':
                option_type = 'call' if random.random() < alignment['ratio'] else 'put'
            elif alignment['preferred_type'] == 'put':
                option_type = 'put' if random.random() < alignment['ratio'] else 'call'
            else:  # 'both'
                option_type = 'call' if random.random() < 0.5 else 'put'
            
            # Realistic strike prices (adjust based on symbol)
            strike_ranges = {
                'SPY': (400, 500), 'QQQ': (350, 450), 'AAPL': (150, 200),
                'MSFT': (300, 400), 'NVDA': (100, 200), 'TSLA': (200, 300),
                'AMD': (100, 180), 'IWM': (180, 220), 'DIA': (340, 380),
                'XLF': (35, 45), 'XLE': (75, 95), 'MRNA': (80, 120)
            }
            strike_range = strike_ranges.get(symbol, (100, 500))
            strike = round(random.uniform(*strike_range), 2)
            
            # Calculate realistic underlying price near strike
            underlying_price = strike * random.uniform(0.95, 1.05)
            
            # Days to expiration
            days_to_exp = random.randint(5, 30)
            
            expiration = (datetime.now() + timedelta(days=days_to_exp)).strftime('%Y-%m-%d')
            
            # IV varies by scenario
            iv_ranges = {'bullish': (18, 28), 'volatile': (30, 50), 'bearish': (25, 40)}
            iv = round(random.uniform(*iv_ranges[scenario_name]), 1)
            
            # Calculate realistic premium based on moneyness, IV, and DTE
            premium = self._calculate_realistic_premium(option_type, strike, underlying_price, iv, days_to_exp)
            
            # Generate confidence score (65-88%)
            confidence_score = round(random.uniform(65, 88), 1)
            
            opportunity = {
                'symbol': symbol,
                'strategy': strategy,
                'confidence': confidence_score,  # 65.0 to 88.0 for percentage
                'ai_confidence': confidence_score / 100,  # 0.65 to 0.88 as decimal for compatibility
                'strike': strike,
                'expiration': expiration,
                'option_type': option_type,
                'premium': round(premium, 2),
                'quantity': random.randint(2, 6),
                'volume': random.randint(5000, 25000),  # More realistic option volumes
                'open_interest': random.randint(2000, 6000),
                'implied_volatility': iv,
                'underlying_price': round(underlying_price, 2),
                'days_to_expiration': days_to_exp,
                'reason': f'Mock {strategy} - {scenario_name} market conditions',
                'data_source': 'mock_after_hours',
                'mock_data': True,
                'scenario': scenario_name
            }
            opportunities.append(opportunity)
        
        self.logger.info(f"🧪 Generated {len(opportunities)} realistic mock opportunities")
        return opportunities
    
    def _is_market_hours(self) -> bool:
        """Check if we're in regular market hours"""
        now = datetime.now()
        current_time = now.time()
        
        # Market hours: 9:30 AM - 4:00 PM EST
        market_open = datetime.strptime("09:30", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()
        
        return market_open <= current_time <= market_close
    
    def _analyze_with_ai_fast(self, opportunities: List[Dict]) -> List[Dict]:
        """OPTIMIZED: Faster AI analysis with mock data support"""
        scored_opportunities = []
        
        for opportunity in opportunities:
            try:
                # For mock data, assign reasonable confidence scores
                if opportunity.get('data_source') == 'mock_after_hours':
                    # Mock opportunities get medium-high confidence for testing
                    ai_confidence = 0.65 + (hash(opportunity.get('symbol', '')) % 100) * 0.003
                    ai_confidence = min(ai_confidence, 0.85)  # Cap at 85%
                else:
                    # Real opportunities: use simple heuristic instead of JAX (which expects array data)
                    # Base confidence on premium and delta
                    base_confidence = 0.5
                    if 'premium' in opportunity:
                        base_confidence += min(opportunity.get('premium', 0) / 100, 0.2)
                    if 'delta' in opportunity:
                        base_confidence += abs(opportunity.get('delta', 0)) * 0.2
                    ai_confidence = min(base_confidence, 0.85)
                
                if ai_confidence >= 0.5:  # 🎯 Lower threshold for testing
                    enhanced_opp = opportunity.copy()
                    enhanced_opp['ai_confidence'] = round(ai_confidence, 3)
                    
                    # Add calculated fields for mock data
                    if 'delta' not in enhanced_opp:
                        enhanced_opp['delta'] = 0.45 if enhanced_opp['option_type'] == 'call' else -0.45
                    if 'theta' not in enhanced_opp:
                        enhanced_opp['theta'] = -0.08
                    
                    scored_opportunities.append(enhanced_opp)
                    
            except Exception as e:
                self.logger.error(f"❌ Error analyzing opportunity {opportunity.get('symbol', 'UNKNOWN')}: {e}")
                continue  # Skip on error
        
        # Sort by confidence
        scored_opportunities.sort(key=lambda x: x.get('ai_confidence', 0), reverse=True)
        return scored_opportunities[:8]  # 🎯 Return top 8 for more testing