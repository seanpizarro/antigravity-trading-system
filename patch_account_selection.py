"""
Patch script to add interactive account selection menu to main.py
"""

import re

# Read the current main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# First, re-apply the VIX changes
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

# Add account selection function before main()
account_selection_code = '''
def prompt_account_selection():
    """Interactive prompt for account selection at startup"""
    print("\\n" + "="*60)
    print("🤖 DUAL-ACCOUNT AI TRADING SYSTEM")
    print("="*60)
    print("\\nWhich account(s) would you like to activate?\\n")
    print("1. 📄 Paper Trading Only (Simulation)")
    print("2. 💰 Live Trading Only (Real Money)")
    print("3. 🔄 Both Accounts (Paper + Live)")
    print("4. ❌ Cancel\\n")
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\\n✅ Selected: Paper Trading Only")
                return ["paper"]
            elif choice == "2":
                confirm = input("\\n⚠️  WARNING: Live trading uses REAL MONEY. Continue? (yes/no): ").strip().lower()
                if confirm in ["yes", "y"]:
                    print("✅ Selected: Live Trading Only")
                    return ["live"]
                else:
                    print("❌ Cancelled. Returning to menu...\\n")
                    continue
            elif choice == "3":
                confirm = input("\\n⚠️  WARNING: This includes LIVE TRADING with real money. Continue? (yes/no): ").strip().lower()
                if confirm in ["yes", "y"]:
                    print("✅ Selected: Both Accounts (Paper + Live)")
                    return ["paper", "live"]
                else:
                    print("❌ Cancelled. Returning to menu...\\n")
                    continue
            elif choice == "4":
                print("\\n❌ Exiting system...")
                return None
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.\\n")
                
        except KeyboardInterrupt:
            print("\\n\\n❌ Cancelled by user")
            return None

'''

# Insert before "def main():"
content = content.replace('def main():', account_selection_code + 'def main():')

# Replace the main() function body
old_main = '''def main():
    """Main entry point for dual-account system"""
    try:
        # Load configuration
        config = TradingConfig()
        
        # Initialize orchestrator
        orchestrator = DualAccountTradingOrchestrator(config)
        
        # Start the system
        orchestrator.start_continuous_operation()
        
    except KeyboardInterrupt:
        print("\\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")
        logging.error(f"System error: {e}")'''

new_main = '''def main():
    """Main entry point for dual-account system"""
    try:
        # Interactive account selection
        selected_accounts = prompt_account_selection()
        
        if selected_accounts is None:
            print("\\n👋 Goodbye!")
            return
        
        print("\\n" + "="*60)
        print(f"🚀 Starting system with: {', '.join(selected_accounts).upper()}")
        print("="*60 + "\\n")
        
        # Load configuration
        config = TradingConfig()
        
        # Store selected accounts in config (for orchestrator to use)
        config.active_accounts = selected_accounts
        
        # Initialize orchestrator
        orchestrator = DualAccountTradingOrchestrator(config)
        
        # Start the system
        orchestrator.start_continuous_operation()
        
    except KeyboardInterrupt:
        print("\\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")
        logging.error(f"System error: {e}")'''

content = content.replace(old_main, new_main)

# Write the updated content
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully added interactive account selection menu!")
print("")
print("Changes made:")
print("1. Added 'import yfinance as yf' (VIX scanning)")
print("2. Added prompt_account_selection() function")
print("3. Updated main() to call account selection menu")
print("")
print("Next time you run 'python main.py', you'll see:")
print("  1. Interactive menu asking which accounts to activate")
print("  2. Safety confirmation for live trading")
print("  3. System starts with only selected accounts")
