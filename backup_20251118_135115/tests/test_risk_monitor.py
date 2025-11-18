
import pytest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_monitor import AccountRiskMonitor, RiskAssessment, RiskLevel

@pytest.fixture
def mock_tasty_api():
    return MagicMock()

@pytest.fixture
def mock_deepseek():
    return MagicMock()

@pytest.fixture
def risk_monitor(mock_tasty_api, mock_deepseek):
    risk_params = {
        'max_open_positions': 5,
        'max_risk_per_trade': 100,
        'sector_limits': {'technology': 2}
    }
    return AccountRiskMonitor(mock_tasty_api, mock_deepseek, risk_params)

def test_assess_portfolio_risk_empty_bullish(risk_monitor):
    """Test risk assessment for empty portfolio in bullish market"""
    with patch.object(risk_monitor, '_get_vix_level', return_value=15.0):
        assessment = risk_monitor.assess_portfolio_risk({})
        
        assert assessment.alert_level == 1
        assert "Bullish market" in assessment.message
        assert "No open positions" in assessment.concerns

def test_assess_portfolio_risk_empty_high_vix(risk_monitor):
    """Test risk assessment for empty portfolio in high VIX environment"""
    with patch.object(risk_monitor, '_get_vix_level', return_value=35.0):
        # Mock market trend to be bearish or neutral to avoid bullish logic
        with patch.object(risk_monitor, '_get_market_conditions', return_value={'vix': 35.0, 'market_trend': 'bearish'}):
            assessment = risk_monitor.assess_portfolio_risk({})
            
            assert assessment.alert_level == 0
            assert "Portfolio is empty" in assessment.message

def test_check_position_limits(risk_monitor):
    """Test position limit checks"""
    current_positions = {'pos1': {}, 'pos2': {}, 'pos3': {}, 'pos4': {}, 'pos5': {}}
    assert risk_monitor._check_position_limits(current_positions) == False
    
    current_positions = {'pos1': {}}
    assert risk_monitor._check_position_limits(current_positions) == True

def test_approve_trade_mock_data(risk_monitor):
    """Test that mock data trades are always approved"""
    opportunity = MagicMock()
    opportunity.data_source = 'mock_data'
    opportunity.symbol = 'TEST'
    
    assert risk_monitor.approve_trade(opportunity, {}) == True

def test_get_vix_level_fallback(risk_monitor):
    """Test VIX retrieval fallback mechanism"""
    # Simulate yfinance error
    with patch('yfinance.Ticker', side_effect=Exception("API Error")):
        vix = risk_monitor._get_vix_level()
        assert vix == 18.5

def test_calculate_risk_score(risk_monitor):
    """Test internal risk score calculation"""
    greeks = {'delta': 50, 'gamma': 10, 'vega': 100}
    sector_conc = {'tech': 0.5}
    margin_usage = 0.6
    
    # Should be high risk due to concentration (0.5 > 0.3) and margin (0.6 > 0.5)
    score = risk_monitor._calculate_risk_score(greeks, sector_conc, margin_usage, 3)
    assert score > 0.5

def test_analyze_market_condition(risk_monitor):
    """Test market condition analysis"""
    # Bullish case
    with patch.object(risk_monitor, '_get_market_conditions', return_value={'vix': 15, 'market_trend': 'bullish'}):
        assert risk_monitor._analyze_market_condition() == 'bullish'
    
    # Bearish case
    with patch.object(risk_monitor, '_get_market_conditions', return_value={'vix': 35, 'market_trend': 'bearish'}):
        assert risk_monitor._analyze_market_condition() == 'bearish'
