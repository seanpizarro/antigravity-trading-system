# Educational Purpose Only - Paper Trading
"""
JAX-ACCELERATED COMPUTATION ENGINE - Real-time Greeks, pricing, and optimization
"""

import jax
import jax.numpy as jnp
from jax import jit, vmap, grad, random
from jax.scipy.stats import norm
import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import logging

@dataclass
class GreekMetrics:
    """Portfolio Greeks container"""
    delta: float
    gamma: float  
    theta: float
    vega: float
    rho: float

@dataclass
class PositionMetrics:
    """Position-level metrics"""
    theoretical_value: float
    probability_profit: float
    expected_value: float
    greeks: GreekMetrics

# JIT-compiled pure functions (must be outside class)
@jit
def _score_opportunities_jit(liquidity_scores: jnp.array, technical_scores: jnp.array,
                             volatility_scores: jnp.array, diversification_scores: jnp.array) -> jnp.array:
    """Vectorized opportunity scoring - JIT compiled for performance"""
    weights = jnp.array([0.25, 0.30, 0.25, 0.20])  # Liquidity, Technical, Volatility, Diversification
    scores = (weights[0] * liquidity_scores + 
             weights[1] * technical_scores +
             weights[2] * volatility_scores + 
             weights[3] * diversification_scores)
    return scores

class JAXRealTimeAnalytics:
    """
    JAX-accelerated engine for real-time options calculations
    GPU/TPU optimized for maximum performance
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_jax()
        
    def setup_jax(self):
        """Configure JAX for optimal performance"""
        # Enable 64-bit precision for financial calculations
        jax.config.update("jax_enable_x64", True)
        
        # Pre-compile frequently used functions
        self._precompile_functions()
        
    def _precompile_functions(self):
        """Pre-compile key functions for maximum performance"""
        # Note: Can't JIT instance methods, only pure functions
        # self.opportunity_scoring will call _score_opportunities directly
        pass
        
    def _black_scholes_with_greeks(self, S: jnp.array, K: jnp.array, T: jnp.array, 
                                 r: jnp.array, sigma: jnp.array, option_type: jnp.array) -> Dict[str, jnp.array]:
        """
        Vectorized Black-Scholes with automatic Greeks calculation
        option_type: 1.0 for Call, -1.0 for Put
        """
        # Ensure inputs are float64
        S = S.astype(jnp.float64)
        K = K.astype(jnp.float64)
        T = T.astype(jnp.float64)
        r = r.astype(jnp.float64)
        sigma = sigma.astype(jnp.float64)
        option_type = option_type.astype(jnp.float64)

        # 🎯 SAFETY: Clip T and sigma to avoid division by zero
        T = jnp.maximum(T, 1e-5)
        sigma = jnp.maximum(sigma, 1e-5)

        d1 = (jnp.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * jnp.sqrt(T))
        d2 = d1 - sigma * jnp.sqrt(T)
        
        # Vectorized Price Calculation using jnp.where
        # Call Price: S * N(d1) - K * e^(-rT) * N(d2)
        call_price = S * norm.cdf(d1) - K * jnp.exp(-r * T) * norm.cdf(d2)
        
        # Put Price: K * e^(-rT) * N(-d2) - S * N(-d1)
        put_price = K * jnp.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        price = jnp.where(option_type == 1.0, call_price, put_price)
        
        # Greeks with auto-differentiation
        def bs_price_single(s, k, t, r_val, sigma_val, o_type):
            d1_val = (jnp.log(s / k) + (r_val + 0.5 * sigma_val ** 2) * t) / (sigma_val * jnp.sqrt(t))
            d2_val = d1_val - sigma_val * jnp.sqrt(t)
            
            c_p = s * norm.cdf(d1_val) - k * jnp.exp(-r_val * t) * norm.cdf(d2_val)
            p_p = k * jnp.exp(-r_val * t) * norm.cdf(-d2_val) - s * norm.cdf(-d1_val)
            
            return jnp.where(o_type == 1.0, c_p, p_p)
        
        # Delta
        delta_fn = grad(bs_price_single, argnums=0)
        delta = vmap(delta_fn)(S, K, T, r, sigma, option_type)
        
        # Gamma (second derivative wrt price)
        gamma_fn = grad(delta_fn, argnums=0)
        gamma = vmap(gamma_fn)(S, K, T, r, sigma, option_type)
        
        # Theta (negative derivative wrt time)
        theta_fn = grad(bs_price_single, argnums=2)
        theta = -vmap(theta_fn)(S, K, T, r, sigma, option_type) / 365.0
        
        # Vega (derivative wrt volatility)
        vega_fn = grad(bs_price_single, argnums=4)
        vega = vmap(vega_fn)(S, K, T, r, sigma, option_type) / 100.0
        
        # Rho (derivative wrt interest rate)
        rho_fn = grad(bs_price_single, argnums=3)
        rho = vmap(rho_fn)(S, K, T, r, sigma, option_type) / 100.0
        
        return {
            'prices': price,
            'deltas': delta, # Delta is already correct sign from differentiation
            'gammas': gamma,
            'thetas': theta,
            'vegas': vega,
            'rhos': rho
        }
    
    def calculate_spread_greeks(self, spread_data: Dict[str, jnp.array]) -> Dict[str, jnp.array]:
        """
        Calculate Greeks for multi-leg spreads (credit/debit spreads)
        Note: Cannot use @jit decorator on instance methods
        """
        # Extract leg data
        S = spread_data['underlying_price']
        strikes = spread_data['strikes']
        expirations = spread_data['expirations']
        volatilities = spread_data['volatilities']
        rates = spread_data['rates']
        option_types = spread_data['option_types']
        quantities = spread_data['quantities']
        
        # Calculate Greeks for each leg
        leg_greeks = self._black_scholes_with_greeks(
            S, strikes, expirations, 
            rates, volatilities, option_types
        )
        
        # Aggregate spread Greeks (weighted by quantities)
        spread_delta = jnp.sum(leg_greeks['deltas'] * quantities)
        spread_gamma = jnp.sum(leg_greeks['gammas'] * quantities)
        spread_theta = jnp.sum(leg_greeks['thetas'] * quantities)
        spread_vega = jnp.sum(leg_greeks['vegas'] * quantities)
        spread_rho = jnp.sum(leg_greeks['rhos'] * quantities)
        
        # Calculate spread theoretical value
        spread_value = jnp.sum(leg_greeks['prices'] * quantities)
        
        return {
            'value': spread_value,
            'delta': spread_delta,
            'gamma': spread_gamma, 
            'theta': spread_theta,
            'vega': spread_vega,
            'rho': spread_rho
        }
    
    def _calculate_portfolio_greeks(self, positions_data: Dict[str, jnp.array]) -> Dict[str, float]:
        """
        Calculate portfolio-level Greeks across all positions
        Note: Cannot use @jit decorator on instance methods
        """
        # Vectorized calculation of all position Greeks
        position_greeks = vmap(self.calculate_spread_greeks)(positions_data)
        
        # Aggregate portfolio Greeks
        portfolio_delta = jnp.sum(position_greeks['delta'])
        portfolio_gamma = jnp.sum(position_greeks['gamma'])
        portfolio_theta = jnp.sum(position_greeks['theta'])
        portfolio_vega = jnp.sum(position_greeks['vega'])
        portfolio_rho = jnp.sum(position_greeks['rho'])
        
        return {
            'portfolio_delta': float(portfolio_delta),
            'portfolio_gamma': float(portfolio_gamma),
            'portfolio_theta': float(portfolio_theta),
            'portfolio_vega': float(portfolio_vega),
            'portfolio_rho': float(portfolio_rho)
        }
    
    def _score_opportunities(self, opportunities_data: Dict[str, jnp.array]) -> jnp.array:
        """
        Vectorized opportunity scoring across entire universe
        Note: Calls JIT-compiled pure function
        """
        # Call the JIT-compiled pure function
        return _score_opportunities_jit(
            opportunities_data['liquidity_scores'],
            opportunities_data['technical_scores'],
            opportunities_data['volatility_scores'],
            opportunities_data['diversification_scores']
        )
    
    def _optimize_roll_decisions(self, positions_data: Dict[str, jnp.array], 
                               market_data: Dict[str, jnp.array]) -> jnp.array:
        """
        Optimize roll/close decisions using expected value maximization
        Note: Cannot JIT instance methods, only pure functions
        """
        def calculate_roll_ev(position_data, market_conditions):
            """Calculate expected value for roll scenarios"""
            current_value = position_data['current_value']
            roll_costs = position_data['roll_costs']
            success_probabilities = position_data['success_probabilities']
            
            # Expected value for each roll scenario
            roll_evs = success_probabilities * (current_value - roll_costs)
            
            # Compare to holding expected value
            hold_ev = position_data['hold_ev']
            
            # Find best action (0=hold, 1=roll1, 2=roll2, etc.)
            best_action = jnp.argmax(jnp.concatenate([jnp.array([hold_ev]), roll_evs]))
            return best_action
        
        # Vectorize over all positions
        best_actions = vmap(calculate_roll_ev)(positions_data, market_data)
        return best_actions
    
    def calculate_implied_volatility(self, market_price: jnp.array, S: jnp.array, 
                                   K: jnp.array, T: jnp.array, r: jnp.array, 
                                   option_type: jnp.array) -> jnp.array:
        """
        Calculate implied volatility using Newton-Raphson method
        Vectorized for multiple options
        """
        def iv_objective(sigma, market_price, S, K, T, r, option_type):
            bs_price = self._black_scholes_with_greeks(
                jnp.array([S]), jnp.array([K]), jnp.array([T]), 
                jnp.array([r]), jnp.array([sigma]), jnp.array([option_type])
            )['prices'][0]
            return bs_price - market_price
        
        def iv_gradient(sigma, market_price, S, K, T, r, option_type):
            # Vega is the gradient wrt volatility
            greeks = self._black_scholes_with_greeks(
                jnp.array([S]), jnp.array([K]), jnp.array([T]),
                jnp.array([r]), jnp.array([sigma]), jnp.array([option_type])
            )
            return greeks['vegas'][0] * 100  # Convert to per 1 vol point
        
        # Newton-Raphson iteration
        def newton_step(sigma_guess):
            price_diff = iv_objective(sigma_guess, market_price, S, K, T, r, option_type)
            vega = iv_gradient(sigma_guess, market_price, S, K, T, r, option_type)
            return sigma_guess - price_diff / vega
        
        # Initial guess (historical volatility)
        sigma_guess = jnp.array(0.3)
        
        # Iterate to convergence
        for _ in range(10):  # Max 10 iterations
            sigma_guess = newton_step(sigma_guess)
        
        return sigma_guess
    
    def monte_carlo_probability(self, S: jnp.array, K: jnp.array, T: jnp.array, 
                              sigma: jnp.array, r: jnp.array, n_simulations: int = 10000) -> jnp.array:
        """
        Monte Carlo simulation for probability calculations
        Vectorized for multiple strikes/underlyings
        """
        key = random.PRNGKey(42)  # Fixed seed for reproducibility
        
        def single_simulation(args):
            S_val, K_val, T_val, sigma_val, r_val = args
            # Geometric Brownian Motion
            z = random.normal(key, (n_simulations,))
            ST = S_val * jnp.exp((r_val - 0.5 * sigma_val**2) * T_val + 
                               sigma_val * jnp.sqrt(T_val) * z)
            
            # Probability of finishing in-the-money for calls
            itm_probability = jnp.mean(ST > K_val)
            return itm_probability
        
        # Vectorize over multiple inputs
        probabilities = vmap(single_simulation)(
            (S, K, T, sigma, r)
        )
        return probabilities
    
    def calculate_position_metrics(self, position: Dict) -> PositionMetrics:
        """
        Calculate comprehensive metrics for a single position
        """
        try:
            # Check if position has legs
            if not position.get('legs') or len(position['legs']) == 0:
                self.logger.warning(f"Position has no legs, returning default metrics")
                return PositionMetrics(
                    theoretical_value=0.0,
                    probability_profit=0.5,
                    expected_value=0.0,
                    greeks=GreekMetrics(0.0, 0.0, 0.0, 0.0, 0.0)
                )
            
            # Extract position data
            S = jnp.array(position['underlying_price'])
            strikes = jnp.array([leg['strike'] for leg in position['legs']])
            quantities = jnp.array([leg['quantity'] for leg in position['legs']])
            option_types = jnp.array([leg['option_type'] for leg in position['legs']])
            T = jnp.array(position['dte'] / 365.0)
            r = jnp.array(0.05)  # Assume 5% risk-free rate
            sigma = jnp.array(position['implied_volatility'])
            
            # Calculate Greeks
            greeks_data = self._black_scholes_with_greeks(
                jnp.array([S] * len(strikes)), strikes, 
                jnp.array([T] * len(strikes)), 
                jnp.array([r] * len(strikes)),
                jnp.array([sigma] * len(strikes)),
                option_types
            )
            
            # Aggregate for multi-leg position
            position_delta = jnp.sum(greeks_data['deltas'] * quantities)
            position_gamma = jnp.sum(greeks_data['gammas'] * quantities)
            position_theta = jnp.sum(greeks_data['thetas'] * quantities)
            position_vega = jnp.sum(greeks_data['vegas'] * quantities)
            position_rho = jnp.sum(greeks_data['rhos'] * quantities)
            position_value = jnp.sum(greeks_data['prices'] * quantities)
            
            # Calculate probability of profit
            pop = self._calculate_pop(position, S, strikes, T, sigma, r)
            
            # Calculate expected value
            expected_value = position_value * pop - position['max_loss'] * (1 - pop)
            
            return PositionMetrics(
                theoretical_value=float(position_value),
                probability_profit=float(pop),
                expected_value=float(expected_value),
                greeks=GreekMetrics(
                    delta=float(position_delta),
                    gamma=float(position_gamma),
                    theta=float(position_theta),
                    vega=float(position_vega),
                    rho=float(position_rho)
                )
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating position metrics: {e}")
            # Return default metrics
            return PositionMetrics(
                theoretical_value=0.0,
                probability_profit=0.5,
                expected_value=0.0,
                greeks=GreekMetrics(0.0, 0.0, 0.0, 0.0, 0.0)
            )
    
    def _calculate_pop(self, position: Dict, S: jnp.array, strikes: jnp.array, 
                     T: jnp.array, sigma: jnp.array, r: jnp.array) -> float:
        """Calculate probability of profit for a spread position"""
        try:
            # Check if strikes array is empty
            if len(strikes) == 0:
                self.logger.warning("Empty strikes array, returning default POP")
                return 0.5
            
            if position['strategy_type'] == 'CREDIT_SPREAD':
                # Check if we have at least 2 strikes for a spread
                if len(strikes) < 2:
                    self.logger.warning("Credit spread requires at least 2 strikes")
                    return 0.5
                    
                # For credit spreads, POP = probability stock stays between strikes
                short_strike = strikes[0]  # Assuming first leg is short
                long_strike = strikes[1]   # Second leg is long
                
                # Monte Carlo simulation for probability
                pop = self.monte_carlo_probability(
                    S, jnp.array([short_strike, long_strike]), 
                    T, sigma, r, 5000
                )
                
                # Probability of staying between strikes for credit spreads
                return float(1.0 - (pop[0] + (1 - pop[1])))
                
            else:  # Debit spread
                # For debit spreads, POP = probability of exceeding break-even
                break_even = position['break_even_price']
                pop = self.monte_carlo_probability(S, jnp.array([break_even]), T, sigma, r, 5000)
                return float(pop[0])
                
        except Exception as e:
            self.logger.error(f"Error calculating POP: {e}")
            return 0.5  # Default probability
    
    def scan_universe_opportunities(self, universe_data: Dict) -> jnp.array:
        """
        High-speed scanning of entire universe for opportunities
        Returns scored opportunities array
        """
        try:
            # Convert to JAX arrays
            liquidity_scores = jnp.array(universe_data['liquidity_scores'])
            technical_scores = jnp.array(universe_data['technical_scores'])
            volatility_scores = jnp.array(universe_data['volatility_scores'])
            diversification_scores = jnp.array(universe_data['diversification_scores'])
            
            opportunities_data = {
                'liquidity_scores': liquidity_scores,
                'technical_scores': technical_scores,
                'volatility_scores': volatility_scores,
                'diversification_scores': diversification_scores
            }
            
            # Score all opportunities using instance method (which calls JIT function)
            scores = self._score_opportunities(opportunities_data)
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Error in universe scanning: {e}")
            return jnp.array([])
    
    def optimize_roll_strategy(self, position: Dict, market_conditions: Dict) -> Dict:
        """
        Optimize roll strategy for a position
        """
        try:
            # Prepare data for JAX optimization
            positions_data = self._prepare_roll_data(position, market_conditions)
            market_data = self._prepare_market_data(market_conditions)
            
            # Find optimal roll decision
            best_action = self.roll_optimization(positions_data, market_data)
            
            return {
                'action': int(best_action[0]),
                'confidence': float(best_action[1]),
                'parameters': self._get_roll_parameters(best_action[0], position)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing roll strategy: {e}")
            return {'action': 0, 'confidence': 0.0, 'parameters': {}}
    
    def _prepare_roll_data(self, position: Dict, market_conditions: Dict) -> Dict[str, jnp.array]:
        """Prepare position data for roll optimization"""
        # Implementation depends on specific roll scenarios
        # This is a simplified version
        return {
            'current_value': jnp.array([position['current_value']]),
            'roll_costs': jnp.array([[0.1, 0.15, 0.2]]),  # Example costs for different rolls
            'success_probabilities': jnp.array([[0.7, 0.6, 0.5]]),  # Example probabilities
            'hold_ev': jnp.array([position['expected_value']])
        }
    
    def _prepare_market_data(self, market_conditions: Dict) -> Dict[str, jnp.array]:
        """Prepare market data for optimization"""
        return {
            'volatility': jnp.array([market_conditions.get('vix', 20) / 100.0]),
            'trend': jnp.array([market_conditions.get('trend_strength', 0.5)]),
            'momentum': jnp.array([market_conditions.get('momentum', 0.0)])
        }
    
    
    def _get_roll_parameters(self, action: int, position: Dict) -> Dict:
        """Get parameters for roll action"""
        if action == 0:  # Hold
            return {}
        elif action == 1:  # Roll to same strikes, next expiration
            return {
                'new_expiration': position['expiration'] + 30,  # 30 days later
                'strikes': [leg['strike'] for leg in position['legs']],
                'target_credit': position['credit_received'] * 0.8  # 80% of original
            }
        else:  # Adjust strikes and roll
            return {
                'new_expiration': position['expiration'] + 30,
                'new_strikes': self._calculate_adjusted_strikes(position),
                'target_credit': position['credit_received'] * 0.7
            }
    
    def _calculate_adjusted_strikes(self, position: Dict) -> List[float]:
        """Calculate adjusted strikes for roll with adjustment"""
        current_strikes = [leg['strike'] for leg in position['legs']]
        # Move strikes 5% closer to current price for adjustment
        adjustment_factor = 0.95 if position['strategy_type'] == 'CREDIT_SPREAD' else 1.05
        return [strike * adjustment_factor for strike in current_strikes]