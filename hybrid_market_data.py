# hybrid_market_data.py - OPTIMIZED VERSION
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time as dt_time
import logging
from typing import Dict, List, Optional
import time
import asyncio
import concurrent.futures
import math
import pytz

class HybridMarketData:
    def __init__(self, tastytrade_client=None):
        # 🎯 YFINANCE ONLY MODE: Ignore TastyTrade for data, only use for execution
        self.tt = None  # Force yfinance-only mode
        self.logger = logging.getLogger(__name__)
        self.logger.info("📊 MARKET DATA: Using yfinance exclusively (TastyTrade only for execution)")
        
        # 🎯 OPTIMIZED: Focus on high-liquidity symbols only
        self.universe = [
            'SPY', 'QQQ',  # Core ETFs (most liquid options)
            'AAPL', 'MSFT', 'NVDA',  # Top 3 tech
            'TSLA', 'AMD'  # Additional liquid names
        ]
        
        # 🎯 OPTIMIZED: Cache strategy
        self.cache = {}
        self.cache_duration = 300
        
        # 🎯 OPTIMIZED: Pre-load most used data
        self._preload_essential_data()

    def _preload_essential_data(self):
        """Pre-load essential market data on startup"""
        try:
            # Pre-load SPY and VIX - most important for context
            self.get_quote('SPY')
            self.get_quote('^VIX')
            self.logger.info("✅ Pre-loaded essential market data")
        except Exception as e:
            self.logger.warning(f"⚠️ Pre-load failed: {e}")
    
    def is_market_open(self) -> bool:
        """Check if markets are currently open"""
        try:
            eastern = pytz.timezone('US/Eastern')
            now = datetime.now(eastern)
            
            # Market hours: 9:30 AM - 4:00 PM ET, Mon-Fri
            market_open = dt_time(9, 30)
            market_close = dt_time(16, 0)
            
            is_open = (market_open <= now.time() <= market_close and 
                      now.weekday() < 5)  # Mon-Fri
            
            if not is_open:
                self.logger.info(f"📅 Markets closed - Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            return is_open
        except Exception as e:
            self.logger.warning(f"⚠️ Error checking market hours: {e}")
            return False  # Assume closed if error
    
    def generate_enhanced_mock_opportunities(self) -> List[Dict]:
        """Generate realistic mock opportunities when markets are closed"""
        self.logger.info("🎭 Generating enhanced mock opportunities for closed market...")
        mock_opportunities = []
        
        # Mock data for popular tickers
        mock_tickers = [
            {'symbol': 'SPY', 'price': 445.50, 'iv': 15.2},
            {'symbol': 'QQQ', 'price': 380.25, 'iv': 18.5},
            {'symbol': 'AAPL', 'price': 185.75, 'iv': 22.3},
            {'symbol': 'MSFT', 'price': 378.90, 'iv': 20.1},
            {'symbol': 'NVDA', 'price': 495.30, 'iv': 35.8}
        ]
        
        for ticker_data in mock_tickers:
            symbol = ticker_data['symbol']
            price = ticker_data['price']
            iv = ticker_data['iv']
            
            # Generate 1-2 mock opportunities per ticker
            num_opps = np.random.randint(0, 3)
            for i in range(num_opps):
                # Randomly choose strategy
                strategy = np.random.choice(['CREDIT_SPREAD', 'DEBIT_SPREAD'])
                is_call = np.random.choice([True, False])
                
                # Generate strikes around current price
                if strategy == 'CREDIT_SPREAD':
                    # OTM credit spread
                    distance = price * np.random.uniform(0.02, 0.05)
                    strike_short = price + distance if is_call else price - distance
                    strike_long = strike_short + (5 if is_call else -5)
                    premium = np.random.uniform(0.30, 0.80)
                else:
                    # ITM/ATM debit spread
                    distance = price * np.random.uniform(0.01, 0.03)
                    strike_long = price - distance if is_call else price + distance
                    strike_short = strike_long + (5 if is_call else -5)
                    premium = np.random.uniform(1.50, 3.50)
                
                mock_opportunities.append({
                    'symbol': symbol,
                    'strategy_type': strategy,
                    'option_type': 'call' if is_call else 'put',
                    'strike_short': round(strike_short, 2),
                    'strike_long': round(strike_long, 2),
                    'underlying_price': price,
                    'premium': round(premium, 2),
                    'dte': np.random.randint(30, 60),
                    'volume': np.random.randint(500, 5000),
                    'open_interest': np.random.randint(1000, 10000),
                    'implied_volatility': iv,
                    'ai_confidence': round(np.random.uniform(0.60, 0.85), 2),
                    'data_source': 'mock_closed_market'
                })
        
        self.logger.info(f"🎭 Generated {len(mock_opportunities)} mock opportunities")
        return mock_opportunities

    def get_quote(self, symbol: str) -> Dict:
        """OPTIMIZED: Get quote with better caching"""
        cache_key = f"quote_{symbol}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 60:  # 1 minute cache for quotes
                return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            # 🎯 OPTIMIZED: Use faster period and only necessary data
            history = ticker.history(period="1d", interval="1m")
            
            if history.empty:
                return {}
                
            current_price = history['Close'].iloc[-1]
            
            # 🎯 OPTIMIZED: Simplified change calculation
            info = ticker.info
            prev_close = info.get('previousClose', current_price)
            change_percent = ((current_price - prev_close) / prev_close) * 100
            
            result = {
                'symbol': symbol,
                'price': round(current_price, 2),
                'change': round(change_percent, 2),
                'volume': info.get('volume', 0),
                'data_source': 'yfinance',
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache[cache_key] = (result, time.time())
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching quote for {symbol}: {e}")
            return {}

    def get_options_chain(self, symbol: str, expiration: str = None) -> Dict:
        """OPTIMIZED: Faster options chain with limits"""
        cache_key = f"options_{symbol}_{expiration}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 120:  # 2 minute cache for options
                return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            
            # 🎯 OPTIMIZED: Get only nearest expiration
            expirations = ticker.options
            if not expirations:
                return {}
            
            if not expiration:
                expiration = expirations[0]  # Nearest expiration only
            
            # 🎯 OPTIMIZED: Get chain with timeout
            chain = ticker.option_chain(expiration)
            
            # 🎯 OPTIMIZED: Process only top 20 most liquid options each
            calls = self._process_yfinance_options(chain.calls.head(20), 'call')
            puts = self._process_yfinance_options(chain.puts.head(20), 'put')
            
            underlying_data = self.get_quote(symbol)
            
            result = {
                'symbol': symbol,
                'expiration': expiration,
                'underlying_price': underlying_data.get('price', 0),
                'calls': calls,
                'puts': puts,
                'total_calls': len(calls),
                'total_puts': len(puts),
                'data_source': 'yfinance',
                'timestamp': datetime.now().isoformat()
            }
            
            self.cache[cache_key] = (result, time.time())
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching options for {symbol}: {e}")
            return {}

    def _process_yfinance_options(self, df, option_type: str) -> List[Dict]:
        """Process yfinance options dataframe into dict list"""
        if df is None or df.empty:
            return []
        
        options_list = []
        for idx, row in df.iterrows():
            try:
                options_list.append({
                    'strike': float(row.get('strike', 0)),
                    'last_price': float(row.get('lastPrice', 0)),
                    'bid': float(row.get('bid', 0)),
                    'ask': float(row.get('ask', 0)),
                    'volume': int(row.get('volume', 0)),
                    'open_interest': int(row.get('openInterest', 0)),
                    'implied_volatility': float(row.get('impliedVolatility', 0)),
                    'delta': float(row.get('delta', 0)) if 'delta' in row else 0,
                    'option_type': option_type
                })
            except Exception as e:
                continue
        
        return options_list

    def get_account_data(self) -> Dict:
        """Get account data from TastyTrade if available"""
        if not self.tt:
            return {}
        
        try:
            return self.tt.get_account_data()
        except Exception as e:
            self.logger.error(f"❌ Error getting account data: {e}")
            return {}

    def scan_opportunities_fast(self) -> List[Dict]:
        """OPTIMIZED: Fast scanning under 30 seconds"""
        # 🎯 Check if market is open first
        if not self.is_market_open():
            return self.generate_enhanced_mock_opportunities()
        
        self.logger.info("⚡ FAST SCAN: Starting optimized opportunity scan...")
        start_time = time.time()
        opportunities = []
        
        # 🎯 OPTIMIZED: Scan symbols in sequence but faster
        for symbol in self.universe:
            try:
                symbol_start = time.time()
                
                # Get stock data
                stock_data = self.get_quote(symbol)
                if not stock_data or stock_data.get('price', 0) == 0:
                    continue
                
                # Get options chain
                options_chain = self.get_options_chain(symbol)
                if not options_chain:
                    continue
                
                # 🎯 OPTIMIZED: Find opportunities quickly
                symbol_opps = self._find_opportunities_fast(stock_data, options_chain)
                opportunities.extend(symbol_opps)
                
                symbol_time = time.time() - symbol_start
                self.logger.info(f"  ✅ {symbol}: {len(symbol_opps)} opportunities in {symbol_time:.1f}s")
                
                # 🎯 OPTIMIZED: Brief pause between symbols
                if len(self.universe) > 1:
                    time.sleep(1)  # 1 second between symbols vs 0.1*17=1.7s
                
            except Exception as e:
                self.logger.error(f"❌ Error scanning {symbol}: {e}")
                continue
        
        total_time = time.time() - start_time
        self.logger.info(f"🎯 FAST SCAN COMPLETE: {len(opportunities)} opportunities in {total_time:.1f}s")
        
        return opportunities

    def _find_opportunities_fast(self, stock_data: Dict, options_chain: Dict) -> List[Dict]:
        """OPTIMIZED: Faster opportunity finding"""
        opportunities = []
        underlying_price = stock_data['price']
        expiration = options_chain.get('expiration', 'N/A')
        
        # 🎯 OPTIMIZED: Scan only top 5 most liquid options each
        for option_type in ['calls', 'puts']:
            options_list = options_chain.get(option_type, [])
            # Sort by volume and take top 5
            options_list.sort(key=lambda x: x.get('volume', 0), reverse=True)
            
            for option in options_list[:5]:
                if self._is_quality_option_fast(option):
                    opportunity = self._create_opportunity_fast(stock_data, option, option_type, expiration)
                    if opportunity:
                        opportunities.append(opportunity)
        
        return opportunities

    def _is_quality_option_fast(self, option: Dict) -> bool:
        """OPTIMIZED: Faster quality checking"""
        try:
            # 🎯 OPTIMIZED: Simpler checks
            volume = option.get('volume', 0)
            oi = option.get('open_interest', 0)
            bid = option.get('bid', 0)
            ask = option.get('ask', 0)
            
            # Quick liquidity check
            if volume < 100 or oi < 200:
                return False
                
            # Quick spread check
            if bid == 0 or ask == 0 or (ask - bid) > 0.5:
                return False
            
            return True
            
        except:
            return False

    def _create_opportunity_fast(self, stock_data: Dict, option: Dict, option_type: str, expiration: str = 'N/A') -> Dict:
        """OPTIMIZED: Faster opportunity creation"""
        try:
            underlying_price = stock_data['price']
            strike = option['strike']
            premium = option['ask'] if option['ask'] > 0 else option['last_price']
            
            if premium <= 0:
                return None
            
            # 🎯 OPTIMIZED: Simplified calculations
            if option_type == 'calls':
                moneyness = 'ITM' if strike < underlying_price else 'OTM'
            else:
                moneyness = 'ITM' if strike > underlying_price else 'OTM'
            
            # Determine strategy based on moneyness and option type
            if moneyness == 'OTM':
                strategy = 'CREDIT_SPREAD' if option_type == 'calls' else 'PUT_CREDIT_SPREAD'
            else:
                strategy = 'DEBIT_SPREAD'
            
            return {
                'symbol': stock_data['symbol'],
                'underlying_price': underlying_price,
                'option_type': option_type[:-1],
                'strike': strike,
                'premium': round(premium, 2),
                'volume': option['volume'],
                'open_interest': option['open_interest'],
                'implied_volatility': round(option.get('implied_volatility', 0) * 100, 2),
                'delta': option.get('delta', 0),
                'moneyness': moneyness,
                'strategy': strategy,
                'expiration': expiration,
                'timestamp': datetime.now().isoformat(),
                'data_source': 'hybrid_fast'
            }
            
        except Exception as e:
            return None

    def get_quick_market_summary(self) -> Dict:
        """OPTIMIZED: Faster market summary"""
        try:
            summary = {}
            
            # 🎯 OPTIMIZED: Only essential data
            spy_data = self.get_quote('SPY')
            vix_data = self.get_quote('^VIX')
            account_data = self.get_account_data()
            
            if spy_data:
                summary['SPY'] = {
                    'price': spy_data.get('price', 0),
                    'change': spy_data.get('change', 0)
                }
            
            if vix_data:
                summary['VIX'] = vix_data.get('price', 0)
            
            if account_data:
                summary['account'] = {
                    'value': account_data.get('account_value', 0),
                    'buying_power': account_data.get('buying_power', 0)
                }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error in quick market summary: {e}")
            return {}

# Global instance
hybrid_data = HybridMarketData()