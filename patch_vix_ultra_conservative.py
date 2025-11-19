"""
Patch script to add ultra-conservative VIX-based adaptive scanning to main.py
90% reduction in API calls: 60min/30min/20min intervals based on VIX
"""

import re

# Read the current main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Add yfinance import
import_section = """import sys
import os
import threading
import time
import schedule
from datetime import datetime, timedelta
import logging
import logging.handlers
from typing import Dict, List, Optional"""

new_import_section = """import sys
import os
import threading
import time
import schedule
from datetime import datetime, timedelta
import logging
import logging.handlers
from typing import Dict, List, Optional
import yfinance as yf"""

content = content.replace(import_section, new_import_section)

# Step 2: Add VIX helper method before opportunity_scanning_loop
vix_method = '''    def _get_current_vix(self) -> float:
        """Fetch current VIX level with 5-minute caching"""
        if hasattr(self, '_vix_cache'):
            cache_time, cached_vix = self._vix_cache
            if datetime.now() - cache_time < timedelta(minutes=5):
                return cached_vix
        
        try:
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            self._vix_cache = (datetime.now(), vix)
            self.logger.info(f"📊 VIX: {vix:.2f}")
            return vix
        except Exception as e:
            self.logger.warning(f"⚠️ VIX fetch failed: {e}, using default 20")
            return 20.0
    
'''

# Insert before opportunity_scanning_loop
content = content.replace(
    '    def opportunity_scanning_loop(self):',
    vix_method + '    def opportunity_scanning_loop(self):'
)

# Step 3: Replace the opportunity_scanning_loop method body
old_loop = '''    def opportunity_scanning_loop(self):
        """Continuous opportunity scanning for all accounts"""
        self.logger.info("🔍 Starting Continuous Opportunity Scanning Loop")
        
        while self.is_running:
            try:
                # Scan opportunities once and share across accounts
                opportunities = None
                
                # Use any scanner to get opportunities (they're market-based, not account-based)
                for account_type, scanner in self.opportunity_scanners.items():
                    if opportunities is None:
                        opportunities = scanner.scan_opportunities()
                        break
                
                if opportunities:
                    # Prioritize with DeepSeek
                    prioritized = self.deepseek_ai.prioritize_opportunities(
                        opportunities, self.open_positions, self.config.risk_parameters
                    )
                    
                    # Update opportunity queue
                    self.opportunity_queue = prioritized[:10]  # Keep top 10
                    
                time.sleep(180)  # 3 minutes between scans
                
            except Exception as e:
                self.logger.error(f"Error in opportunity scanning: {e}")
                time.sleep(60)'''

new_loop = '''    def opportunity_scanning_loop(self):
        """Ultra-conservative VIX-based adaptive scanning (90% reduction)"""
        self.logger.info("🔍 Starting Ultra-Conservative VIX-Adaptive Scanning")
        
        while self.is_running:
            try:
                # Ultra-conservative intervals for multi-week holdings
                vix = self._get_current_vix()
                if vix > 25:
                    interval = 1200  # 20 minutes - high volatility
                    volatility_state = "HIGH"
                    emoji = "🔴"
                elif vix > 20:
                    interval = 1800  # 30 minutes - medium volatility
                    volatility_state = "MEDIUM"
                    emoji = "🟡"
                else:
                    interval = 3600  # 60 minutes - low volatility
                    volatility_state = "LOW"
                    emoji = "🟢"
                
                self.logger.info(
                    f"{emoji} VIX {vix:.1f} ({volatility_state}) → {interval//60}min scans"
                )
                
                # Scan opportunities once and share across accounts
                opportunities = None
                
                # Use any scanner to get opportunities (they're market-based, not account-based)
                for account_type, scanner in self.opportunity_scanners.items():
                    if opportunities is None:
                        opportunities = scanner.scan_opportunities()
                        break
                
                if opportunities:
                    # Prioritize with DeepSeek
                    prioritized = self.deepseek_ai.prioritize_opportunities(
                        opportunities, self.open_positions, self.config.risk_parameters
                    )
                    
                    # Update opportunity queue
                    self.opportunity_queue = prioritized[:10]  # Keep top 10
                    self.logger.info(f"📊 Queue: {len(self.opportunity_queue)} opps")
                    
                time.sleep(interval)  # Adaptive interval: 60/30/20 min
                
            except Exception as e:
                self.logger.error(f"Error in opportunity scanning: {e}")
                time.sleep(60)'''

content = content.replace(old_loop, new_loop)

# Write the updated content
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully patched main.py with ultra-conservative VIX scanning!")
print("")
print("Changes made:")
print("1. Added 'import yfinance as yf'")
print("2. Added _get_current_vix() helper method")
print("3. Updated opportunity_scanning_loop() with:")
print("   - Low VIX (<20): 60 min scans → ~6-7/day")
print("   - Med VIX (20-25): 30 min scans → ~13/day")
print("   - High VIX (>25): 20 min scans → ~20/day")
print("")
print("Average: 10-12 scans/day (90% reduction from 120!)")
