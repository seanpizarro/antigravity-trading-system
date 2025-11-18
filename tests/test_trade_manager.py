import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from trade_manager import ActiveTradeManager, ManagementAction
from deepseek_analyst import DeepSeekMultiTaskAI, ManagementDecision
from jax_engine import JAXRealTimeAnalytics, PositionMetrics, GreekMetrics

@pytest.fixture
def mock_deepseek():
    ai = MagicMock(spec=DeepSeekMultiTaskAI)
    ai.analyze_position_management.return_value = ManagementDecision(
        position_id="test_pos",
        action_type="HOLD",
        confidence=0.5,
        rationale="Test rationale",
        parameters={}
    )
    return ai

@pytest.fixture
def mock_jax():
    engine = MagicMock(spec=JAXRealTimeAnalytics)
    engine.calculate_position_metrics.return_value = PositionMetrics(
        theoretical_value=100.0,
        probability_profit=0.6,
        expected_value=50.0,
        greeks=GreekMetrics(0.1, 0.01, -0.05, 0.02, 0.0)
    )
    return engine

@pytest.fixture
def mock_tasty():
    return MagicMock()

@pytest.fixture
def trade_manager(mock_deepseek, mock_jax, mock_tasty):
    return ActiveTradeManager(mock_deepseek, mock_jax, mock_tasty)

def test_manage_all_positions_empty(trade_manager):
    actions = trade_manager.manage_all_positions({})
    assert actions == []

def test_manage_all_positions_too_new(trade_manager):
    # Position created just now
    positions = {
        'pos1': {
            'symbol': 'SPY',
            'entry_time': datetime.now().isoformat(),
            'underlying_price': 450,
            'legs': [{'strike': 450, 'option_type': 'call', 'quantity': 1}]
        }
    }
    actions = trade_manager.manage_all_positions(positions)
    assert actions == []  # Should be skipped

def test_manage_all_positions_valid(trade_manager, mock_deepseek):
    # Position created 5 hours ago (valid for management)
    entry_time = (datetime.now() - timedelta(hours=5)).isoformat()
    positions = {
        'pos1': {
            'symbol': 'SPY',
            'entry_time': entry_time,
            'underlying_price': 450,
            'legs': [{'strike': 450, 'option_type': 'call', 'quantity': 1}],
            'current_pnl': 10,
            'max_loss': 100,
            'strategy_type': 'credit_spread',
            'dte': 30,
            'entry_underlying_price': 445
        }
    }
    
    # Mock DeepSeek to return CLOSE action
    mock_deepseek.analyze_position_management.return_value = ManagementDecision(
        position_id="pos1",
        action_type="CLOSE",
        confidence=0.9,
        rationale="Profit target hit",
        parameters={}
    )
    
    actions = trade_manager.manage_all_positions(positions)
    assert len(actions) == 1
    assert actions[0].action_type == "CLOSE"
    assert actions[0].confidence == 0.9

def test_emergency_close(trade_manager):
    # Position at max loss
    entry_time = (datetime.now() - timedelta(hours=5)).isoformat()
    positions = {
        'pos1': {
            'symbol': 'SPY',
            'entry_time': entry_time,
            'underlying_price': 450,
            'legs': [{'strike': 450, 'option_type': 'call', 'quantity': 1}],
            'current_pnl': -90, # 90% loss
            'max_loss': 100,
            'strategy_type': 'credit_spread',
            'dte': 30,
            'entry_underlying_price': 445
        }
    }
    
    actions = trade_manager.manage_all_positions(positions)
    assert len(actions) == 1
    assert actions[0].action_type == "CLOSE"
    assert "approaching maximum loss" in actions[0].rationale
