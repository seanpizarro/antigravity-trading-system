"""Test DeepSeek API authentication"""
from config import TradingConfig
from deepseek_analyst import DeepSeekMultiTaskAI

try:
    config = TradingConfig()
    print(f"DeepSeek API Key loaded: {config.deepseek_api_key[:10]}...")
    
    ai = DeepSeekMultiTaskAI(config.deepseek_api_key)
    print("✓ DeepSeek AI initialized successfully!")
    
    # Try a simple test call
    test_assessment = ai.assess_portfolio_risk({}, {}, {})
    print(f"✓ DeepSeek API call successful!")
    print(f"  Response: {test_assessment.message[:50]}...")
    
except Exception as e:
    print(f"✗ Error: {e}")
