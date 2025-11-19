
import sys
import os
from dataclasses import dataclass
from typing import Dict, Any

# Add current directory to path
sys.path.append(os.getcwd())

from deepseek_analyst import DeepSeekMultiTaskAI, ManagementDecision

# Mock classes
@dataclass
class MockMetrics:
    delta: float = 0.5
    theta: float = -0.1
    gamma: float = 0.05
    vega: float = 0.02
    pop: float = 0.65
    days_since_entry: int = 10

def test_analyze_position_management():
    print("Testing analyze_position_management...")
    
    # Initialize AI with mock key
    ai = DeepSeekMultiTaskAI(api_key="mock_key")
    
    # Mock position data as a dictionary (like from API)
    pos_dict = {
        'symbol': 'SPY',
        'strategy': 'CREDIT_SPREAD',
        'entry_price': 1.50,
        'current_price': 1.20,
        'quantity': 1,
        'entry_time': '2023-01-01T10:00:00'
    }
    
    # Add position_id as trade_manager does
    position_id = "pos_123"
    pos_dict['position_id'] = position_id
    
    # Create object dynamically as trade_manager does
    # trade_manager also adds normalized fields
    pos_dict['ticker'] = pos_dict['symbol']
    pos_dict['strategy_type'] = pos_dict['strategy']
    pos_dict['dte'] = 30
    pos_dict['current_pnl'] = 30.0
    pos_dict['entry_date'] = pos_dict['entry_time']
    
    position_obj = type('Position', (), pos_dict)
    
    metrics = MockMetrics()
    market_conditions = {'vix': 15, 'market_trend': 'bullish'}
    
    try:
        decision = ai.analyze_position_management(position_obj, metrics, market_conditions)
        print(f"✓ Success! Decision: {decision.action_type}")
        print(f"  Confidence: {decision.confidence}")
        print(f"  Rationale: {decision.rationale}")
        
        if decision.position_id == position_id:
            print("✓ Position ID preserved correctly")
        else:
            print(f"✗ Position ID mismatch: {decision.position_id} != {position_id}")
            
    except AttributeError as e:
        print(f"✗ AttributeError: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_analyze_position_management()
