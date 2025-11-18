# tastytrade_market_data.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from tastytrade_api import tastytrade  # Your existing API client

class TastytradeMarketData:
    def __init__(self, tastytrade_client):
        self.tt = tastytrade_client
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Trading universe - same as before
        self.universe = [
            'SPY', 'QQQ', 'IWM', 'DIA',
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA',
            'JPM', 'BAC', 'GS',
            'XOM', 'CVX',
            'DIS', 'NFLX'
        ]
        
    def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote from Tastytrade"""
        try:
            # Use your existing Tastytrade API
            quote = self.tt.get_quote(symbol)
            
            return {
                'symbol': symbol,
                'price': quote.get('last', 0),
                'bid': quote.get('bid', 0),
                'ask': quote.get('ask', 0),
                'change': quote.get('net-change', 0),
                'change_percent': quote.get('percent-change', 0),
                'volume': quote.get('volume', 0),
                'iv': quote.get('volatility', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching quote for {symbol}: {e}")
            return {}
    
    def get_options_chain(self, symbol: str, expiration: str = None) -> Dict:
        """Get comprehensive options chain from Tastytrade"""
        try:
            # Get available expirations
            expirations = self.tt.get_option_expirations(symbol)
            if not expirations and not expiration:
                return {}
            
            # Use nearest expiration if not specified
            if not expiration:
                expiration = expirations[0]['expiration-date'] if expirations else None
            
            if not expiration:
                return {}
            
            # Get the option chain
            chain = self.tt.get_option_chain(symbol, expiration)
            
            return self._process_tastytrade_chain(chain, symbol, expiration)
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching options chain for {symbol}: {e}")
            return {}
    
    def _process_tastytrade_chain(self, chain: Dict, symbol: str, expiration: str) -> Dict:
        """Process Tastytrade options chain into structured format"""
        try:
            calls = []
            puts = []
            
            # Tastytrade returns a list of option instruments
            for option in chain.get('items', []):
                option_data = self._extract_option_data(option)
                if option_data:
                    if option_data['option_type'] == 'call':
                        calls.append(option_data)
                    else:
                        puts.append(option_data)
            
            # Get underlying price
            underlying_quote = self.get_quote(symbol)
            
            return {
                'symbol': symbol,
                'expiration': expiration,
                'underlying_price': underlying_quote.get('price', 0),
                'calls': calls,
                'puts': puts,
                'total_calls': len(calls),
                'total_puts': len(puts),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error processing options chain: {e}")
            return {}
    
    def _extract_option_data(self, option: Dict) -> Dict:
        """Extract relevant data from Tastytrade option object"""
        try:
            # Extract key fields from Tastytrade response
            symbol = option.get('symbol', '')
            strike = option.get('strike-price', 0)
            option_type = 'call' if option.get('option-type') == 'C' else 'put'
            
            # Get quote for this specific option
            option_quote = self.tt.get_quote(symbol)
            
            return {
                'contract_symbol': symbol,
                'strike': strike,
                'option_type': option_type,
                'last_price': option_quote.get('last', 0),
                'bid': option_quote.get('bid', 0),
                'ask': option_quote.get('ask', 0),
                'bid_size': option_quote.get('bid-size', 0),
                'ask_size': option_quote.get('ask-size', 0),
                'volume': option_quote.get('volume', 0),
                'open_interest': option.get('open-interest', 0),
                'implied_volatility': option_quote.get('volatility', 0),
                'delta': option.get('delta', 0),
                'gamma': option.get('gamma', 0),
                'theta': option.get('theta', 0),
                'vega': option.get('vega', 0),
                'rho': option.get('rho', 0),
                'time_value': option_quote.get('last', 0) - max(0, strike - option_quote.get('underlying-price', 0)),
                'in_the_money': option.get('in-the-money', False)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting option data: {e}")
            return None
    
    def get_volatility_data(self, symbol: str = 'SPY') -> Dict:
        """Get comprehensive volatility data"""
        try:
            # Get VIX data
            vix_quote = self.get_quote('VIX')
            
            # Get SPY for historical context
            spy_quote = self.get_quote(symbol)
            
            # Get SPY options for implied volatility analysis
            spy_chain = self.get_options_chain(symbol)
            
            # Calculate average IV across strikes
            if spy_chain:
                all_options = spy_chain.get('calls', []) + spy_chain.get('puts', [])
                if all_options:
                    avg_iv = sum(opt.get('implied_volatility', 0) for opt in all_options) / len(all_options)
                else:
                    avg_iv = 0
            else:
                avg_iv = 0
            
            return {
                'vix': vix_quote.get('price', 0),
                'vix_change': vix_quote.get('change_percent', 0),
                'underlying_iv': spy_quote.get('iv', 0),
                'avg_options_iv': avg_iv,
                'volatility_regime': 'HIGH' if vix_quote.get('price', 0) > 20 else 'LOW',
                'iv_rank': self._calculate_iv_rank(symbol),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching volatility data: {e}")
            return {}
    
    def _calculate_iv_rank(self, symbol: str) -> float:
        """Calculate IV rank (simplified)"""
        try:
            # This would normally require historical IV data
            # For now, return a simplified version
            quote = self.get_quote(symbol)
            current_iv = quote.get('iv', 0)
            
            # Simplified IV rank (0-100)
            if current_iv < 10:
                return 0.0
            elif current_iv > 50:
                return 100.0
            else:
                return (current_iv - 10) / 40 * 100
                
        except:
            return 50.0  # Default middle value
    
    def scan_high_probability_trades(self) -> List[Dict]:
        """Scan for high-probability options trades using Tastytrade data"""
        opportunities = []
        
        for symbol in self.universe:
            try:
                self.logger.info(f"🔍 Scanning {symbol} for opportunities...")
                
                # Get underlying quote
                stock_quote = self.get_quote(symbol)
                if not stock_quote or stock_quote.get('price', 0) == 0:
                    continue
                
                # Get options chain
                options_chain = self.get_options_chain(symbol)
                if not options_chain:
                    continue
                
                # Look for high-quality opportunities
                symbol_opportunities = self._find_opportunities_in_chain(stock_quote, options_chain)
                opportunities.extend(symbol_opportunities)
                
                # Rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                self.logger.error(f"❌ Error scanning {symbol}: {e}")
                continue
        
        self.logger.info(f"🎯 Found {len(opportunities)} Tastytrade opportunities")
        return opportunities
    
    def _find_opportunities_in_chain(self, stock_quote: Dict, options_chain: Dict) -> List[Dict]:
        """Find trading opportunities in options chain"""
        opportunities = []
        underlying_price = stock_quote['price']
        
        # Scan both calls and puts
        for option_type in ['calls', 'puts']:
            for option in options_chain.get(option_type, []):
                # Apply filters for quality
                if self._is_high_quality_option(option, underlying_price):
                    opportunity = self._create_trade_opportunity(stock_quote, option, option_type)
                    if opportunity:
                        opportunities.append(opportunity)
        
        return opportunities
    
    def _is_high_quality_option(self, option: Dict, underlying_price: float) -> bool:
        """Determine if an option meets quality thresholds"""
        try:
            # Liquidity filters
            if option.get('volume', 0) < 100:
                return False
                
            if option.get('open_interest', 0) < 500:
                return False
                
            # Bid-ask spread filter
            bid = option.get('bid', 0)
            ask = option.get('ask', 0)
            if bid == 0 or ask == 0:
                return False
                
            spread_percent = (ask - bid) / bid if bid > 0 else 1.0
            if spread_percent > 0.1:  # Max 10% spread
                return False
            
            # Price filter - avoid very cheap options (high percentage spreads)
            if ask < 0.50:
                return False
                
            return True
            
        except:
            return False
    
    def _create_trade_opportunity(self, stock_quote: Dict, option: Dict, option_type: str) -> Dict:
        """Create a structured trade opportunity"""
        try:
            underlying_price = stock_quote['price']
            strike = option['strike']
            premium = option['ask']  # Use ask price for entry
            
            # Calculate moneyness
            if option_type == 'calls':
                moneyness = 'ITM' if strike < underlying_price else 'OTM'
                intrinsic = max(0, underlying_price - strike)
            else:
                moneyness = 'ITM' if strike > underlying_price else 'OTM'
                intrinsic = max(0, strike - underlying_price)
            
            time_value = premium - intrinsic
            
            # Calculate probability metrics (simplified)
            probability = self._calculate_probability(option, underlying_price, option_type)
            
            return {
                'symbol': stock_quote['symbol'],
                'underlying_price': underlying_price,
                'option_type': option_type[:-1],  # Remove 's'
                'strike': strike,
                'premium': round(premium, 2),
                'bid_ask_spread': round(option['ask'] - option['bid'], 2),
                'volume': option['volume'],
                'open_interest': option['open_interest'],
                'implied_volatility': round(option.get('implied_volatility', 0) * 100, 2),
                'delta': option.get('delta', 0),
                'theta': option.get('theta', 0),
                'gamma': option.get('gamma', 0),
                'moneyness': moneyness,
                'intrinsic_value': round(intrinsic, 2),
                'time_value': round(time_value, 2),
                'probability_otm': round(probability, 3),
                'volume_oi_ratio': round(option['volume'] / max(option['open_interest'], 1), 2),
                'liquidity_score': self._calculate_liquidity_score(option),
                'timestamp': datetime.now().isoformat(),
                'data_source': 'tastytrade'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error creating trade opportunity: {e}")
            return None
    
    def _calculate_probability(self, option: Dict, underlying_price: float, option_type: str) -> float:
        """Calculate probability OTM (simplified using delta)"""
        try:
            delta = abs(option.get('delta', 0.5))
            
            if option_type == 'calls':
                # For calls, probability OTM ≈ 1 - delta
                return 1 - delta
            else:
                # For puts, probability OTM ≈ delta
                return delta
                
        except:
            return 0.5
    
    def _calculate_liquidity_score(self, option: Dict) -> float:
        """Calculate liquidity score (0-1)"""
        try:
            scores = []
            
            # Volume score
            volume_score = min(option.get('volume', 0) / 1000, 1.0)
            scores.append(volume_score)
            
            # Open interest score
            oi_score = min(option.get('open_interest', 0) / 1000, 1.0)
            scores.append(oi_score)
            
            # Bid-ask spread score (inverse)
            spread = option.get('ask', 0) - option.get('bid', 0)
            mid_price = (option.get('ask', 0) + option.get('bid', 0)) / 2
            if mid_price > 0:
                spread_pct = spread / mid_price
                spread_score = max(0, 1 - (spread_pct / 0.1))  # Normalize to 10% max
            else:
                spread_score = 0
            scores.append(spread_score)
            
            return round(sum(scores) / len(scores), 3)
            
        except:
            return 0.5
    
    def get_market_summary(self) -> Dict:
        """Get comprehensive market summary"""
        try:
            summary = {}
            
            # Major indices
            indices = ['SPY', 'QQQ', 'IWM', 'DIA', 'VIX']
            for symbol in indices:
                quote = self.get_quote(symbol)
                if quote:
                    summary[symbol] = {
                        'price': quote.get('price', 0),
                        'change': quote.get('change', 0),
                        'change_percent': quote.get('change_percent', 0)
                    }
            
            # Volatility data
            vol_data = self.get_volatility_data()
            summary['volatility'] = vol_data
            
            # Market breadth (simplified)
            advancing = 0
            total = len(self.universe)
            for symbol in self.universe[:10]:  # Sample for speed
                quote = self.get_quote(symbol)
                if quote and quote.get('change', 0) > 0:
                    advancing += 1
            
            summary['market_breadth'] = {
                'advancing': advancing,
                'total': 10,
                'advance_decline_ratio': round(advancing / 10, 2)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error getting market summary: {e}")
            return {}