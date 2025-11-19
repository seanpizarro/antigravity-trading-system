# main.py - UPDATED FOR DUAL ACCOUNTS
#!/usr/bin/env python3
"""
MAIN ORCHESTRATOR - Dual Account Trading System
Supports both live and paper trading simultaneously
"""

import sys
import os
import threading
import time
import schedule
from datetime import datetime, timedelta
import logging
import logging.handlers
from typing import Dict, List, Optional
import yfinance as yf
import yfinance as yf

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from config import TradingConfig
from deepseek_analyst import DeepSeekMultiTaskAI
from jax_engine import JAXRealTimeAnalytics
from trade_manager import ActiveTradeManager
from opportunity_scanner import OpportunityScanner
from risk_monitor import AccountRiskMonitor
from dual_tastytrade_api import dual_tasty_api  # 🎯 NEW: Dual account API
from dashboard import RealTimeDashboard
from personalization import PersonalizedTradingAI

class DualAccountTradingOrchestrator:
    """
    Main coordinator that manages both live and paper trading accounts
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.setup_logging()
        
        # Initialize core components
        self.deepseek_ai = DeepSeekMultiTaskAI(config.deepseek_api_key)
        self.jax_engine = JAXRealTimeAnalytics()
        
        # 🎯 DUAL ACCOUNT: Use the dual API instead of single
        self.tasty_api = dual_tasty_api
        
        # Initialize specialized systems for each account type
        self.trade_managers = {}
        self.opportunity_scanners = {}
        self.risk_monitors = {}
        
        self._initialize_account_systems()
        
        self.dashboard = RealTimeDashboard(self.deepseek_ai)
        self.personalizer = PersonalizedTradingAI(self.deepseek_ai)
        
        # System state
        self.is_running = False
        self.open_positions = {}  # Nested: {'paper': {}, 'live': {}}
        self.opportunity_queue = []
        self.risk_alerts = []
        self.current_trading_mode = os.getenv('TRADING_MODE', 'paper')
        
    def _initialize_account_systems(self):
        """Initialize trading systems for only selected active accounts"""
        accounts = self.tasty_api.get_all_accounts()
        active_accounts = set(getattr(self.config, 'active_accounts', []))
        for account_type, account_info in accounts.items():
            if account_type not in active_accounts:
                continue
            # Create trade manager for this account
            self.trade_managers[account_type] = ActiveTradeManager(
                self.deepseek_ai, self.jax_engine, account_info.api_instance
            )
            # Create opportunity scanner for this account
            self.opportunity_scanners[account_type] = OpportunityScanner(
                self.jax_engine, account_info.api_instance
            )
            # Create risk monitor for this account
            self.risk_monitors[account_type] = AccountRiskMonitor(
                account_info.api_instance, self.deepseek_ai, self.config.risk_parameters
            )
            self.logger.info(f"✅ Initialized systems for {account_info.name}")
    
    def setup_logging(self):
        """Setup comprehensive logging with rotation"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.handlers.RotatingFileHandler(
                    'trading_system.log', 
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                ),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def start_continuous_operation(self):
        """Start all systems for both accounts"""
        self.logger.info("🚀 Starting Dual-Account Trading System")
        self.is_running = True
        
        # Load existing positions for all accounts
        self.open_positions = self.tasty_api.get_positions()
        self.logger.info(f"📊 Loaded positions: {self._format_positions_summary()}")
        
        # Show system configuration
        self._print_system_info()
        
        # Start background threads
        threads = [
            threading.Thread(target=self.trade_management_loop, name="TradeManager"),
            threading.Thread(target=self.opportunity_scanning_loop, name="OpportunityScanner"),
            threading.Thread(target=self.risk_monitoring_loop, name="RiskMonitor"),
            threading.Thread(target=self.personalization_loop, name="Personalizer"),
            threading.Thread(target=self.account_monitoring_loop, name="AccountMonitor")  # 🎯 NEW
        ]
        
        for thread in threads:
            thread.daemon = True
            thread.start()
            
        # Main coordination loop
        self.main_coordination_loop()
    
    def _print_system_info(self):
        """Print system configuration for only selected accounts, separated"""
        accounts = self.tasty_api.get_all_accounts()
        balances = self.tasty_api.get_account_balances()
        active_accounts = set(getattr(self.config, 'active_accounts', []))
        print("\n" + "="*60)
        print("🤖 DUAL-ACCOUNT AI TRADING SYSTEM")
        print("="*60)
        print(f"🔧 Trading Mode: {self.current_trading_mode.upper()}")
        print(f"⚡ Scanner: Optimized (10-15 seconds)")
        print(f"🤖 AI Engine: DeepSeek + JAX")
        print(f"📊 Active Systems: {len(self.trade_managers)} account(s)")
        print("="*60)
        for account_type in active_accounts:
            account_info = accounts.get(account_type)
            balance = balances.get(account_type, 0)
            print(f"\n--- {account_type.upper()} ACCOUNT ---")
            if account_info and hasattr(account_info, 'name'):
                print(f"💼 {account_info.name}: ${balance:,.2f}")
            else:
                print(f"💼 {account_type}: ${balance:,.2f}")
            positions = self.open_positions.get(account_type, {})
            print(f"📊 Positions: {len(positions)}")
        print("="*60 + "\n")
    
    def _format_positions_summary(self) -> str:
        """Format positions summary for logging, separated by active accounts"""
        active_accounts = set(getattr(self.config, 'active_accounts', []))
        summary = []
        for account_type in active_accounts:
            positions = self.open_positions.get(account_type, {})
            summary.append(f"{account_type}: {len(positions)} positions")
        return ", ".join(summary) if summary else "No positions"
    
    def account_monitoring_loop(self):
        """🎯 NEW: Monitor account balances and status (only selected accounts)"""
        self.logger.info("💰 Starting Account Monitoring Loop")
        active_accounts = set(getattr(self.config, 'active_accounts', []))
        while self.is_running:
            try:
                # Update account balances every 5 minutes
                balances = self.tasty_api.get_account_balances()
                for account_type, balance in balances.items():
                    if account_type in active_accounts:
                        self.logger.info(f"💰 {account_type.upper()} Balance: ${balance:,.2f}")
                time.sleep(300)  # 5 minutes
            except Exception as e:
                self.logger.error(f"Error in account monitoring: {e}")
                time.sleep(60)
    
    def trade_management_loop(self):
        """Continuous trade management for all accounts"""
        self.logger.info("🔄 Starting Active Trade Management Loop")
        
        while self.is_running:
            try:
                # Manage positions for each account
                for account_type, trade_manager in self.trade_managers.items():
                    account_positions = self.open_positions.get(account_type, {})
                    
                    management_actions = trade_manager.manage_all_positions(account_positions)
                    
                    # Store actions for main thread execution
                    for action in management_actions:
                        action.account_type = account_type  # 🎯 Track which account
                        self.execute_management_action(action)
                    
                time.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in trade management: {e}")
                time.sleep(60)
    
    def _get_current_vix(self) -> float:
        """Fetch current VIX level with 5-minute caching"""
        # Check cache first
        if hasattr(self, '_vix_cache'):
            cache_time, cached_vix = self._vix_cache
            cache_age = (datetime.now() - cache_time).total_seconds() / 60
            if cache_age < 5:
                self.logger.debug(f"📊 VIX (cached {cache_age:.1f}min ago): {cached_vix:.2f}")
                return cached_vix
        
        # Fetch fresh VIX data
        try:
            vix_ticker = yf.Ticker("^VIX")
            vix_data = vix_ticker.history(period="1d")
            
            if vix_data.empty:
                raise ValueError("Empty VIX data returned")
            
            vix = float(vix_data['Close'].iloc[-1])
            
            # Validate VIX is in reasonable range (5-80)
            if not (5 <= vix <= 80):
                self.logger.warning(f"⚠️ VIX {vix:.2f} out of range, using default 20")
                return 20.0
            
            # Cache the result
            self._vix_cache = (datetime.now(), vix)
            self.logger.info(f"📊 VIX (fresh): {vix:.2f}")
            return vix
            
        except Exception as e:
            self.logger.warning(f"⚠️ VIX fetch failed: {e}, using default 20")
            # Use cached value if available, even if stale
            if hasattr(self, '_vix_cache'):
                _, cached_vix = self._vix_cache
                self.logger.info(f"📊 Using stale VIX cache: {cached_vix:.2f}")
                return cached_vix
            return 20.0
    
    def opportunity_scanning_loop(self):
        """Ultra-conservative VIX-based adaptive scanning (90% reduction)"""
        self.logger.info("🔍 Starting Ultra-Conservative VIX-Adaptive Scanning")
        scan_count = 0
        
        while self.is_running:
            try:
                scan_count += 1
                scan_start = datetime.now()
                
                # Ultra-conservative intervals for multi-week holdings
                vix = self._get_current_vix()
                if vix > 25:
                    interval = 1200  # 20 minutes - high volatility
                    volatility_state = "HIGH"
                    emoji = "🔴"
                    est_daily_scans = 20
                elif vix > 20:
                    interval = 1800  # 30 minutes - medium volatility
                    volatility_state = "MEDIUM"
                    emoji = "🟡"
                    est_daily_scans = 13
                else:
                    interval = 3600  # 60 minutes - low volatility
                    volatility_state = "LOW"
                    emoji = "🟢"
                    est_daily_scans = 7
                
                self.logger.info(
                    f"{emoji} VIX {vix:.1f} ({volatility_state}) → {interval//60}min intervals "
                    f"(~{est_daily_scans}/day) [Scan #{scan_count}]"
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
                    
                # Sleep with countdown timer
                next_scan_time = datetime.now() + timedelta(seconds=interval)
                self.logger.info(f"⏰ Next scan at: {next_scan_time.strftime('%I:%M:%S %p')}")
                
                # Countdown in chunks (show progress every minute for long waits)
                if interval >= 300:  # 5+ minutes
                    chunk_size = 60  # Show update every minute
                else:
                    chunk_size = interval  # Just sleep the whole time
                
                remaining = interval
                while remaining > 0 and self.is_running:
                    sleep_time = min(chunk_size, remaining)
                    time.sleep(sleep_time)
                    remaining -= sleep_time
                    
                    # Show countdown for long waits
                    if remaining > 0 and interval >= 300:
                        mins_left = remaining // 60
                        secs_left = remaining % 60
                        self.logger.info(f"⏳ Next scan in: {mins_left}m {secs_left}s")
                
            except Exception as e:
                self.logger.error(f"Error in opportunity scanning: {e}")
                time.sleep(60)
    
    def risk_monitoring_loop(self):
        """Continuous risk monitoring for all accounts"""
        self.logger.info("🛡️ Starting Real-time Risk Monitoring Loop")
        
        while self.is_running:
            try:
                # Monitor risk for each account
                for account_type, risk_monitor in self.risk_monitors.items():
                    account_positions = self.open_positions.get(account_type, {})
                    
                    risk_assessment = risk_monitor.assess_portfolio_risk(account_positions)
                    
                    # Trigger alerts if needed
                    if risk_assessment.alert_level > 0:
                        risk_assessment.account_type = account_type  # 🎯 Track which account
                        self.risk_alerts.append(risk_assessment)
                        self.handle_risk_alert(risk_assessment)
                    
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in risk monitoring: {e}")
                time.sleep(30)
    
    def personalization_loop(self):
        """Continuous learning of trading style"""
        self.logger.info("🎯 Starting Personalization Learning Loop")
        
        while self.is_running:
            try:
                # Learn from recent trades weekly
                if datetime.now().weekday() == 0:  # Every Monday
                    self.personalizer.learn_from_recent_trades()
                    
                time.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error in personalization: {e}")
                time.sleep(3600)
    
    def main_coordination_loop(self):
        """Main thread coordination and execution"""
        self.logger.info("🎮 Starting Main Coordination Loop")
        
        # Schedule daily reports
        schedule.every().day.at("18:00").do(self.generate_daily_report)
        
        last_opportunity_check = datetime.now()
        
        while self.is_running:
            try:
                # Check for new high-priority opportunities
                current_time = datetime.now()
                if (current_time - last_opportunity_check).seconds >= 30:
                    self.process_opportunity_queue()
                    last_opportunity_check = current_time
                
                # Process any risk alerts
                self.process_risk_alerts()
                
                # Run scheduled tasks
                schedule.run_pending()
                
                # User command interface
                self.check_user_commands()
                
                time.sleep(5)  # 5 second heartbeat
                
            except Exception as e:
                self.logger.error(f"Error in main coordination: {e}")
                time.sleep(10)
    
    def process_opportunity_queue(self):
        """Execute top opportunities across appropriate accounts"""
        if not self.opportunity_queue:
            return
            
        # Get top opportunities
        top_opportunities = self.opportunity_queue[:3]
        
        for opportunity in top_opportunities:
            # Determine which account(s) to execute on
            target_accounts = self._select_target_accounts(opportunity)
            
            for account_type in target_accounts:
                # Risk check for this specific account
                risk_monitor = self.risk_monitors.get(account_type)
                if risk_monitor and risk_monitor.approve_trade(opportunity, self.open_positions.get(account_type, {})):
                    
                    # Execute trade
                    execution_result = self.tasty_api.execute_trade(opportunity, account_type)
                    
                    if execution_result.get('success'):
                        # Handle both dict and dataclass opportunity objects
                        symbol = opportunity.get('symbol', 'UNKNOWN') if isinstance(opportunity, dict) else getattr(opportunity, 'symbol', 'UNKNOWN')
                        self.logger.info(f"✅ Executed trade on {account_type}: {symbol}")
                        
                        # Update positions
                        position_id = execution_result.get('position_id', f"{symbol}_{datetime.now().timestamp()}")
                        if account_type not in self.open_positions:
                            self.open_positions[account_type] = {}
                        self.open_positions[account_type][position_id] = execution_result
                        
                        # Remove from queue after successful execution
                        if account_type == 'live':  # Only remove if executed on live account
                            self.opportunity_queue.remove(opportunity)
                            break
    
    def _select_target_accounts(self, opportunity) -> List[str]:
        """Select which accounts should execute this opportunity"""
        target_accounts = []
        confidence = getattr(opportunity, 'ai_confidence', 0)
        
        # Strategy: Use paper for testing, live for high-confidence opportunities
        if confidence >= 0.8 and 'live' in self.trade_managers:
            target_accounts.append('live')
        
        # Always include paper for tracking and validation
        if 'paper' in self.trade_managers:
            target_accounts.append('paper')
            
        return target_accounts
    
    def process_risk_alerts(self):
        """Handle any active risk alerts"""
        while self.risk_alerts:
            alert = self.risk_alerts.pop(0)
            self.handle_risk_alert(alert)
    
    def handle_risk_alert(self, alert):
        """Take action on risk alerts for specific account"""
        account_type = getattr(alert, 'account_type', 'unknown')
        self.logger.warning(f"🚨 {account_type.upper()} Risk Alert: {alert.message} - Level: {alert.alert_level}")
        
        # Convert RiskAssessment dataclass to dict for dashboard
        alert_dict = {
            'level': alert.alert_level,
            'message': alert.message,
            'concerns': alert.concerns,
            'recommendations': alert.recommendations,
            'account_type': account_type
        }
        
        # Send notification
        self.dashboard.send_alert(alert_dict)
        
        # Take automatic actions for high-level alerts
        if alert.alert_level >= 8:
            self.logger.critical(f"🛑 CRITICAL RISK on {account_type} - Taking protective actions")
            risk_monitor = self.risk_monitors.get(account_type)
            if risk_monitor:
                protective_actions = risk_monitor.get_protective_actions(alert)
                for action in protective_actions:
                    action.account_type = account_type
                    self.execute_management_action(action)
    
    def execute_management_action(self, action):
        """Execute trade management actions on specific account"""
        try:
            account_type = getattr(action, 'account_type', 'paper')
            account_api = self.tasty_api.get_account(account_type)
            
            if not account_api:
                self.logger.error(f"❌ Account {account_type} not found for action")
                return
            
            if action.action_type == "CLOSE":
                result = account_api.api_instance.close_position(action.position_id)
            elif action.action_type == "ROLL":
                result = account_api.api_instance.roll_position(action.position_id, action.new_params)
            elif action.action_type == "ADJUST":
                result = account_api.api_instance.adjust_position(action.position_id, action.adjustments)
            else:
                self.logger.warning(f"Unknown action type: {action.action_type}")
                return
                
            if result.success:
                self.logger.info(f"✅ Executed {action.action_type} on {account_type} - {action.position_id}")
                
                # Update positions
                if action.action_type == "CLOSE":
                    self.open_positions.get(account_type, {}).pop(action.position_id, None)
                else:
                    self.open_positions.get(account_type, {})[action.position_id] = result.updated_position
                    
        except Exception as e:
            self.logger.error(f"Error executing management action on {account_type}: {e}")
    
    def generate_daily_report(self):
        """Generate and display daily report for all accounts"""
        self.logger.info("📊 Generating daily trading report")
        
        balances = self.tasty_api.get_account_balances()
        self.dashboard.generate_dual_account_report(self.open_positions, self.opportunity_queue, balances)
    
    def check_user_commands(self):
        """Check for user commands (future enhancement)"""
        # Placeholder for user interaction interface
        # Could include commands like: switch mode, force scan, etc.
        pass
    
    def switch_trading_mode(self, new_mode: str):
        """Dynamically switch trading mode"""
        try:
            self.tasty_api.switch_mode(new_mode)
            self.current_trading_mode = new_mode
            self._initialize_account_systems()  # Reinitialize systems
            self.logger.info(f"🔄 Trading mode switched to: {new_mode}")
        except Exception as e:
            self.logger.error(f"❌ Failed to switch trading mode: {e}")
    
    def stop_system(self):
        """Gracefully stop the system"""
        self.logger.info("🛑 Stopping dual-account trading system...")
        self.is_running = False


def get_available_accounts():
    """Get list of available paper and live accounts"""
    paper_accounts = []
    live_accounts = []
    
    # Check for Alpaca paper credentials
    if os.getenv('ALPACA_API_KEY'):
        paper_accounts.append({
            'id': 'alpaca_paper',
            'name': 'Alpaca Paper Trading'
        })
    
    # Check for TastyTrade paper credentials
    if os.getenv('TASTYTRADE_PAPER_ACCOUNT_NUMBER') or os.getenv('TASTYTRADE_REFRESH_TOKEN'):
        paper_accounts.append({
            'id': 'tastytrade_paper',
            'name': 'TastyTrade Paper (Sandbox)'
        })
    
    # Check for TastyTrade live credentials
    if os.getenv('TASTYTRADE_LIVE_ACCOUNT_NUMBER'):
        live_accounts.append({
            'id': 'tastytrade_live',
            'name': 'TastyTrade Live'
        })
    
    # Fallback if no accounts detected
    if not paper_accounts:
        paper_accounts = [{'id': 'paper', 'name': 'Paper Trading (Default)'}]
    if not live_accounts:
        live_accounts = [{'id': 'live', 'name': 'Live Trading (Default)'}]
    
    return paper_accounts, live_accounts

def select_specific_accounts(account_list, account_type_name):
    """Let user select specific accounts from a list"""
    if len(account_list) == 1:
        return [account_list[0]['id']]
    
    print(f"\n{account_type_name} Accounts Available:")
    for i, acc in enumerate(account_list, 1):
        print(f"{i}. {acc['name']}")
    print(f"{len(account_list) + 1}. All {account_type_name} Accounts")
    print(f"{len(account_list) + 2}. Cancel\n")
    
    while True:
        try:
            choice = input(f"Select {account_type_name} account (1-{len(account_list) + 2}): ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(account_list):
                    selected = account_list[choice_num - 1]
                    print(f"✅ Selected: {selected['name']}")
                    return [selected['id']]
                elif choice_num == len(account_list) + 1:
                    print(f"✅ Selected: All {account_type_name} Accounts")
                    return [acc['id'] for acc in account_list]
                elif choice_num == len(account_list) + 2:
                    return None
            
            print(f"❌ Invalid choice. Please enter 1-{len(account_list) + 2}.\n")
        except KeyboardInterrupt:
            print("\n❌ Cancelled")
            return None

def prompt_account_selection():
    """Interactive prompt for account selection at startup with multi-account support"""
    print("\n" + "="*60)
    print("🤖 DUAL-ACCOUNT AI TRADING SYSTEM")
    print("="*60)
    
    # Get available accounts
    paper_accounts, live_accounts = get_available_accounts()
    
    print("\nWhich account(s) would you like to activate?\n")
    print("1. 📄 Paper Trading Only")
    print("2. 💰 Live Trading Only")
    print("3. 🔄 Both Paper & Live")
    print("4. ❌ Cancel\n")
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                # Paper trading only
                selected = select_specific_accounts(paper_accounts, "Paper")
                if selected:
                    return selected
                else:
                    print("Returning to main menu...\n")
                    continue
                    
            elif choice == "2":
                # Live trading only
                confirm = input("\n⚠️  WARNING: Live trading uses REAL MONEY. Continue? (yes/no): ").strip().lower()
                if confirm not in ["yes", "y"]:
                    print("❌ Cancelled. Returning to menu...\n")
                    continue
                
                selected = select_specific_accounts(live_accounts, "Live")
                if selected:
                    return selected
                else:
                    print("Returning to main menu...\n")
                    continue
                    
            elif choice == "3":
                # Both paper and live
                confirm = input("\n⚠️  WARNING: This includes LIVE TRADING with real money. Continue? (yes/no): ").strip().lower()
                if confirm not in ["yes", "y"]:
                    print("❌ Cancelled. Returning to menu...\n")
                    continue
                
                # Select paper accounts
                print("\n--- Step 1: Select Paper Account(s) ---")
                paper_selected = select_specific_accounts(paper_accounts, "Paper")
                if not paper_selected:
                    print("Returning to main menu...\n")
                    continue
                
                # Select live accounts
                print("\n--- Step 2: Select Live Account(s) ---")
                live_selected = select_specific_accounts(live_accounts, "Live")
                if not live_selected:
                    print("Returning to main menu...\n")
                    continue
                
                return paper_selected + live_selected
                
            elif choice == "4":
                print("\n❌ Exiting system...")
                return None
            else:
                print("❌ Invalid choice. Please enter 1-4.\n")
                
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user")
            return None

def main():
    """Main entry point for dual-account system"""
    try:
        # Interactive account selection
        selected_accounts = prompt_account_selection()
        
        if selected_accounts is None:
            print("\n👋 Goodbye!")
            return
        
        print("\n" + "="*60)
        print(f"🚀 Starting system with: {', '.join(selected_accounts).upper()}")
        print("="*60 + "\n")
        
        # Load configuration
        config = TradingConfig()
        
        # Store selected accounts in config (for orchestrator to use)
        config.active_accounts = selected_accounts
        
        # Initialize orchestrator
        orchestrator = DualAccountTradingOrchestrator(config)
        
        # Start the system
        orchestrator.start_continuous_operation()
        
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")
        logging.error(f"System error: {e}")

if __name__ == "__main__":
    main()