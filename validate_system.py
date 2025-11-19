#!/usr/bin/env python3
"""
SYSTEM VALIDATION SCRIPT
Comprehensive checks for configuration, API connections, and system integrity
"""

import os
import sys
import logging
from typing import Dict, List, Tuple
from config import TradingConfig

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemValidator:
    """Validates entire trading system configuration and connections"""
    
    def __init__(self):
        self.config = TradingConfig()
        self.errors = []
        self.warnings = []
        self.passed = []
        
    def validate_all(self) -> bool:
        """Run all validation checks"""
        logger.info("🔍 Starting comprehensive system validation...")
        
        checks = [
            ("Environment Variables", self.validate_env_vars),
            ("DeepSeek API", self.validate_deepseek),
            ("TastyTrade Credentials", self.validate_tastytrade),
            ("Alpaca Credentials", self.validate_alpaca),
            ("Multi-Broker API", self.validate_multi_broker),
            ("Risk Parameters", self.validate_risk_params),
            ("File Integrity", self.validate_files),
        ]
        
        for check_name, check_func in checks:
            logger.info(f"\n{'='*60}")
            logger.info(f"Checking: {check_name}")
            logger.info(f"{'='*60}")
            try:
                check_func()
            except Exception as e:
                self.errors.append(f"{check_name}: {str(e)}")
                logger.error(f"❌ {check_name} failed: {e}")
        
        self._print_summary()
        return len(self.errors) == 0
    
    def validate_env_vars(self):
        """Validate environment variables are loaded"""
        required_vars = ['DEEPSEEK_API_KEY']
        optional_vars = [
            'TASTYTRADE_PAPER_REFRESH_TOKEN',
            'TASTYTRADE_LIVE_REFRESH_TOKEN',
            'ALPACA_API_KEY',
            'ALPACA_API_SECRET'
        ]
        
        for var in required_vars:
            val = os.getenv(var)
            if not val or val == 'YOUR_DEEPSEEK_API_KEY_HERE':
                self.errors.append(f"Missing required env var: {var}")
            else:
                self.passed.append(f"Required env var set: {var}")
        
        for var in optional_vars:
            val = os.getenv(var)
            if val:
                self.passed.append(f"Optional env var set: {var}")
            else:
                self.warnings.append(f"Optional env var not set: {var}")
    
    def validate_deepseek(self):
        """Validate DeepSeek API connection"""
        if not self.config.deepseek_api_key or self.config.deepseek_api_key == 'YOUR_DEEPSEEK_API_KEY_HERE':
            self.errors.append("DeepSeek API key not configured")
            return
        
        try:
            from deepseek_analyst import DeepSeekMultiTaskAI
            ai = DeepSeekMultiTaskAI(self.config.deepseek_api_key)
            # Don't make actual API call to save credits, just validate initialization
            self.passed.append("DeepSeek API initialized successfully")
        except Exception as e:
            self.errors.append(f"DeepSeek initialization failed: {e}")
    
    def validate_tastytrade(self):
        """Validate TastyTrade credentials"""
        creds = self.config.tastytrade_credentials
        
        if not creds:
            self.warnings.append("TastyTrade credentials not configured")
            return
        
        required_keys = ['client_id', 'client_secret']
        for key in required_keys:
            if not creds.get(key):
                self.warnings.append(f"TastyTrade {key} not set")
        
        # Check for both paper and live tokens
        paper_token = os.getenv('TASTYTRADE_PAPER_REFRESH_TOKEN')
        live_token = os.getenv('TASTYTRADE_LIVE_REFRESH_TOKEN')
        
        if paper_token:
            self.passed.append("TastyTrade paper account configured")
        else:
            self.warnings.append("TastyTrade paper account not configured")
        
        if live_token:
            self.passed.append("TastyTrade live account configured")
        else:
            self.warnings.append("TastyTrade live account not configured (recommended for testing)")
    
    def validate_alpaca(self):
        """Validate Alpaca credentials"""
        creds = self.config.alpaca_credentials
        
        if not creds:
            self.warnings.append("Alpaca credentials not configured")
            return
        
        required_keys = ['api_key', 'api_secret']
        for key in required_keys:
            if not creds.get(key):
                self.errors.append(f"Alpaca {key} not set")
            else:
                self.passed.append(f"Alpaca {key} configured")
        
        # Validate base URL
        if creds.get('base_url'):
            if 'paper' in creds['base_url']:
                self.passed.append("Alpaca configured for paper trading")
            else:
                self.warnings.append("Alpaca configured for LIVE trading - use with caution")
    
    def validate_multi_broker(self):
        """Validate multi-broker API functionality"""
        try:
            from multi_broker_api import MultiBrokerAPI
            api = MultiBrokerAPI()
            
            brokers = api.get_available_brokers()
            if not brokers:
                self.warnings.append("No brokers available in multi-broker API")
            else:
                self.passed.append(f"Multi-broker API initialized with: {', '.join(brokers)}")
            
            active = api.get_active_broker()
            if active:
                self.passed.append(f"Active broker: {active}")
            else:
                self.warnings.append("No active broker selected")
                
        except Exception as e:
            self.errors.append(f"Multi-broker API validation failed: {e}")
    
    def validate_risk_params(self):
        """Validate risk parameters"""
        params = self.config.risk_parameters
        
        if not params:
            self.errors.append("Risk parameters not configured")
            return
        
        required_params = [
            'account_size', 'max_risk_per_trade', 'max_capital_per_trade',
            'total_daily_risk', 'max_open_positions'
        ]
        
        for param in required_params:
            if param not in params:
                self.errors.append(f"Missing risk parameter: {param}")
            else:
                self.passed.append(f"Risk parameter configured: {param} = {params[param]}")
        
        # Validate values are reasonable
        if params.get('max_risk_per_trade', 0) > params.get('account_size', 0) * 0.05:
            self.warnings.append("max_risk_per_trade exceeds 5% of account (risky)")
        
        if params.get('max_open_positions', 0) > 10:
            self.warnings.append("max_open_positions > 10 (may be hard to manage)")
    
    def validate_files(self):
        """Validate critical files exist"""
        required_files = [
            'config.py', 'deepseek_analyst.py', 'jax_engine.py',
            'trade_manager.py', 'opportunity_scanner.py', 'risk_monitor.py',
            'alpaca_api.py', 'multi_broker_api.py'
        ]
        
        optional_files = [
            '.env', 'paper_positions.json', 'trading_system.log'
        ]
        
        for file in required_files:
            if os.path.exists(file):
                self.passed.append(f"Required file exists: {file}")
            else:
                self.errors.append(f"Missing required file: {file}")
        
        for file in optional_files:
            if os.path.exists(file):
                self.passed.append(f"Optional file exists: {file}")
            else:
                self.warnings.append(f"Optional file missing: {file}")
    
    def _print_summary(self):
        """Print validation summary"""
        logger.info(f"\n{'='*60}")
        logger.info("VALIDATION SUMMARY")
        logger.info(f"{'='*60}\n")
        
        logger.info(f"✅ PASSED: {len(self.passed)} checks")
        for item in self.passed[:5]:  # Show first 5
            logger.info(f"  • {item}")
        if len(self.passed) > 5:
            logger.info(f"  ... and {len(self.passed) - 5} more")
        
        if self.warnings:
            logger.info(f"\n⚠️  WARNINGS: {len(self.warnings)} issues")
            for item in self.warnings:
                logger.warning(f"  • {item}")
        
        if self.errors:
            logger.info(f"\n❌ ERRORS: {len(self.errors)} critical issues")
            for item in self.errors:
                logger.error(f"  • {item}")
        
        logger.info(f"\n{'='*60}")
        if self.errors:
            logger.info("❌ VALIDATION FAILED - Fix errors above")
            logger.info(f"{'='*60}\n")
        elif self.warnings:
            logger.info("⚠️  VALIDATION PASSED WITH WARNINGS")
            logger.info(f"{'='*60}\n")
        else:
            logger.info("✅ VALIDATION PASSED - All systems OK")
            logger.info(f"{'='*60}\n")

def main():
    """Run validation"""
    validator = SystemValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
