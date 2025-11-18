
import pytest
import jax.numpy as jnp
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jax_engine import JAXRealTimeAnalytics

@pytest.fixture
def jax_engine():
    return JAXRealTimeAnalytics()

def test_black_scholes_call_price(jax_engine):
    """Test Black-Scholes call pricing"""
    # Simple case: S=100, K=100, T=1, r=0.05, sigma=0.2
    # Expected price approx 10.45
    
    S = jnp.array([100.0])
    K = jnp.array([100.0])
    T = jnp.array([1.0])
    r = jnp.array([0.05])
    sigma = jnp.array([0.2])
    option_type = jnp.array([1.0]) # 1.0 for Call
    
    result = jax_engine._black_scholes_with_greeks(S, K, T, r, sigma, option_type)
    price = float(result['prices'][0])
    
    assert 10.4 < price < 10.5

def test_black_scholes_put_price(jax_engine):
    """Test Black-Scholes put pricing"""
    # Simple case: S=100, K=100, T=1, r=0.05, sigma=0.2
    # Put price should be Call - S + K*exp(-rT) (Put-Call Parity)
    # 10.45 - 100 + 100*exp(-0.05) = 10.45 - 100 + 95.12 = 5.57 approx
    
    S = jnp.array([100.0])
    K = jnp.array([100.0])
    T = jnp.array([1.0])
    r = jnp.array([0.05])
    sigma = jnp.array([0.2])
    option_type = jnp.array([-1.0]) # -1.0 for Put
    
    result = jax_engine._black_scholes_with_greeks(S, K, T, r, sigma, option_type)
    price = float(result['prices'][0])
    
    assert 5.5 < price < 5.7

def test_greeks_calculation(jax_engine):
    """Test Greeks calculation"""
    S = jnp.array([100.0])
    K = jnp.array([100.0])
    T = jnp.array([0.5])
    r = jnp.array([0.01])
    sigma = jnp.array([0.3])
    option_type = jnp.array([1.0]) # 1.0 for Call
    
    result = jax_engine._black_scholes_with_greeks(S, K, T, r, sigma, option_type)
    
    delta = float(result['deltas'][0])
    gamma = float(result['gammas'][0])
    vega = float(result['vegas'][0])
    theta = float(result['thetas'][0])
    
    # ATM Call Delta should be approx 0.5
    assert 0.4 < delta < 0.6
    # Gamma should be positive
    assert gamma > 0
    # Vega should be positive
    assert vega > 0
    # Theta should be negative (time decay)
    assert theta < 0

def test_calculate_spread_greeks(jax_engine):
    """Test spread Greeks aggregation"""
    # Bull Call Spread: Long 100 Call, Short 105 Call
    spread_data = {
        'underlying_price': jnp.array([100.0, 100.0]),
        'strikes': jnp.array([100.0, 105.0]),
        'expirations': jnp.array([0.1, 0.1]),
        'volatilities': jnp.array([0.2, 0.2]),
        'rates': jnp.array([0.01, 0.01]),
        'option_types': jnp.array([1.0, 1.0]), # 1.0 for Call
        'quantities': jnp.array([1.0, -1.0])
    }
    
    result = jax_engine.calculate_spread_greeks(spread_data)
    
    # Net delta should be positive but less than long leg alone
    assert result['delta'] > 0
    # Net gamma should be small (long gamma at 100, short at 105)
    
    # Value should be positive (debit spread)
    assert result['value'] > 0
