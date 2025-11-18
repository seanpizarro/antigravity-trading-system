# main_enhanced_paper.py
#!/usr/bin/env python3
"""
ENHANCED PAPER TRADING SYSTEM
Professional paper trading with advanced analytics and strategy tracking
"""

import sys
import threading
import time
import schedule
from datetime import datetime
import logging
from typing import Dict, List, Optional
from dataclasses import asdict

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from config import TradingConfig
from deepseek_analyst import DeepSeekMultiTaskAI
from jax_engine import JAXRealTimeAnalytics
from trade_manager import ActiveTradeManager
from market_utils import is_market_open
from opportunity_scanner import OpportunityScanner
from risk_monitor import AccountRiskMonitor
from tastytrade_api import TastyTradeAPI
from enhanced_paper_dashboard import EnhancedPaperDashboard
from enhanced_paper_trading import EnhancedPaperTradingEngine
from personalization import PersonalizedTradingAI

class EnhancedPaperTradingOrchestrator:
    """
    Enhanced paper trading system with professional analytics
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.setup_logging()
        
        # Initialize core components
        self.deepseek_ai = DeepSeekMultiTaskAI(config.deepseek_api_key)
        self.jax_engine = JAXRealTimeAnalytics()
        
        # 🎯 PAPER TRADING ONLY - Safe mode
        self.tasty_api = TastyTradeAPI(sandbox=True)
        
        # Enhanced components
        self.paper_engine = EnhancedPaperTradingEngine(self.tasty_api)
        self.dashboard = EnhancedPaperDashboard()
        
        # Standard components
        self.trade_manager = ActiveTradeManager(
            self.deepseek_ai, self.jax_engine, self.tasty_api
        )
        self.opportunity_scanner = OpportunityScanner(
            self.jax_engine, self.tasty_api
        )
        self.risk_monitor = AccountRiskMonitor(
            self.tasty_api, self.deepseek_ai, config.risk_parameters
        )
        self.personalizer = PersonalizedTradingAI(self.deepseek_ai)
        
        # System state
        self.is_running = False
        self.open_positions = {}
        self.opportunity_queue = []
        self.performance_update_interval = 3600  # 1 hour
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enhanced_paper_trading.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def start_enhanced_operation(self):
        """Start enhanced paper trading system"""
        self.logger.info("🚀 STARTING ENHANCED PAPER TRADING SYSTEM")
        self.is_running = True
        
        # Show enhanced system info
        self._print_enhanced_system_info()
        
        # Start background threads
        threads = [
            threading.Thread(target=self.enhanced_trade_management_loop, name="EnhancedTradeManager"),
            threading.Thread(target=self.enhanced_opportunity_scanning_loop, name="EnhancedOpportunityScanner"),
            threading.Thread(target=self.enhanced_risk_monitoring_loop, name="EnhancedRiskMonitor"),
            threading.Thread(target=self.enhanced_performance_tracking_loop, name="EnhancedPerformanceTracker"),
            threading.Thread(target=self.personalization_loop, name="Personalizer")
        ]
        
        for thread in threads:
            thread.daemon = True
            thread.start()
            
        # Main coordination loop
        self.enhanced_coordination_loop()
    
    def _print_enhanced_system_info(self):
        """Print enhanced system information with market status"""
        portfolio = self.paper_engine.get_enhanced_portfolio_summary()
        market_open = is_market_open()
        market_status = "🟢 MARKET OPEN" if market_open else "🌙 MARKET CLOSED"
        scanner_mode = 'Optimized (10-15 seconds)' if market_open else 'Enhanced Mock Mode'
        
        status = f"""
======================================================================
🤖 ENHANCED PAPER TRADING SYSTEM - PROFESSIONAL MODE
================================================================
======
💰 Paper Balance: ${portfolio.get('total_value', 0):,.2f}
💼 Open Positions: {portfolio.get('open_positions', 0)}
📈 Market Status: {market_status}
⚡ Scanner: {scanner_mode}
🤖 AI Engine: DeepSeek + JAX
📊 Enhanced Analytics: Active
🎯 Strategy Tracking: Enabled
======================================================================
💡 This is a PROFESSIONAL PAPER TRADING environment
💡 Perfect for strategy development and testing
💡 Zero financial risk - Maximum learning opportunity
======================================================================
"""
        print(status)
    
    def _check_market_hours(self) -> bool:
        """Check if market is currently open"""
        try:
            import pytz
            from datetime import time as dt_time
            eastern = pytz.timezone('US/Eastern')
            now = datetime.now(eastern)
            
            market_open = dt_time(9, 30)
            market_close = dt_time(16, 0)
            
            is_open = (market_open <= now.time() <= market_close and 
                      now.weekday() < 5)
            
            return is_open
        except Exception as e:
            self.logger.warning(f"⚠️ Error checking market hours: {e}")
            return False  # Assume closed if error
    
    
    def enhanced_trade_management_loop(self):
        """Enhanced trade management with strategy tracking"""
        self.logger.info("🔄 Starting Enhanced Trade Management Loop")
        
        while self.is_running:
            try:
                # Manage positions with enhanced tracking
                management_actions = self.trade_manager.manage_all_positions(self.open_positions)
                
                for action in management_actions:
                    self.execute_enhanced_management_action(action)
                    
                time.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in enhanced trade management: {e}")
                time.sleep(60)
    
    def enhanced_opportunity_scanning_loop(self):
        """Enhanced opportunity scanning with strategy classification"""
        self.logger.info("🔍 Starting Enhanced Opportunity Scanning Loop")
        
        while self.is_running:
            try:
                # Run enhanced scan
                opportunities = self.opportunity_scanner.scan_opportunities()
                
                if opportunities:
                    # Enhanced prioritization with strategy consideration
                    prioritized = self.deepseek_ai.prioritize_opportunities(
                        opportunities, self.open_positions, self.config.risk_parameters
                    )
                    
                    # Add strategy classification to opportunities
                    enhanced_opportunities = []
                    for opp in prioritized[:10]:
                        # Convert dataclass to dict
                        enhanced_opp = asdict(opp)
                        enhanced_opp['strategy_type'] = self.paper_engine._classify_strategy(enhanced_opp)
                        enhanced_opp['risk_level'] = self.paper_engine._assess_risk_level(enhanced_opp)
                        enhanced_opportunities.append(enhanced_opp)
                    
                    self.opportunity_queue = enhanced_opportunities
                    
                time.sleep(180)  # 3 minutes
                
            except Exception as e:
                self.logger.error(f"Error in enhanced opportunity scanning: {e}")
                time.sleep(60)
    
    def enhanced_risk_monitoring_loop(self):
        """Enhanced risk monitoring with strategy-aware limits"""
        self.logger.info("🛡️ Starting Enhanced Risk Monitoring Loop")
        
        while self.is_running:
            try:
                # Enhanced risk assessment
                risk_assessment = self.risk_monitor.assess_portfolio_risk(self.open_positions)
                
                # Strategy-aware risk limits
                portfolio_summary = self.paper_engine.get_enhanced_portfolio_summary()
                strategy_breakdown = portfolio_summary.get('strategy_breakdown', {})
                
                # Check strategy concentration risk
                for strategy, data in strategy_breakdown.items():
                    strategy_exposure = (data['value'] / portfolio_summary['total_value']) * 100
                    if strategy_exposure > 25:  # Max 25% per strategy
                        self.logger.warning(f"⚠️ High concentration in {strategy}: {strategy_exposure:.1f}%")
                
                if risk_assessment.alert_level > 0:
                    self.handle_enhanced_risk_alert(risk_assessment)
                    
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in enhanced risk monitoring: {e}")
                time.sleep(30)
    
    def enhanced_performance_tracking_loop(self):
        """Enhanced performance tracking and analytics"""
        self.logger.info("📊 Starting Enhanced Performance Tracking Loop")
        
        while self.is_running:
            try:
                # Update performance metrics
                self.dashboard.update_performance_metrics()
                
                # Generate periodic performance report
                if datetime.now().hour % 4 == 0:  # Every 4 hours
                    self.dashboard.generate_performance_report()
                
                time.sleep(self.performance_update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in performance tracking: {e}")
                time.sleep(3600)  # Retry in 1 hour
    
    def personalization_loop(self):
        """Continuous learning loop"""
        self.logger.info("🎯 Starting Personalization Learning Loop")
        
        while self.is_running:
            try:
                # Weekly learning
                if datetime.now().weekday() == 0:  # Every Monday
                    self.personalizer.learn_from_recent_trades()
                    
                time.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"Error in personalization: {e}")
                time.sleep(3600)
    
    def enhanced_coordination_loop(self):
        """Enhanced main coordination loop"""
        self.logger.info("🎮 Starting Enhanced Coordination Loop")
        
        # Enhanced scheduling
        schedule.every().day.at("09:00").do(self.dashboard.generate_performance_report)
        schedule.every().day.at("18:00").do(self.dashboard.generate_performance_report)
        
        last_opportunity_check = datetime.now()
        last_performance_display = datetime.now()
        
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Process opportunities every 30 seconds
                if (current_time - last_opportunity_check).seconds >= 30:
                    self.process_enhanced_opportunity_queue()
                    last_opportunity_check = current_time
                
                # Display performance every 15 minutes
                if (current_time - last_performance_display).seconds >= 900:
                    self.show_live_performance_update()
                    last_performance_display = current_time
                
                # Run scheduled tasks
                schedule.run_pending()
                
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Error in enhanced coordination: {e}")
                time.sleep(10)
    
    def process_enhanced_opportunity_queue(self):
        """Process enhanced opportunity queue with PROPER data handling"""
        if not self.opportunity_queue:
            return
            
        top_opportunities = self.opportunity_queue[:3]
        
        for opportunity in top_opportunities:
            # Enhanced risk approval
            if self.risk_monitor.approve_trade(opportunity, self.open_positions):
                # Execute enhanced paper trade
                execution_result = self.paper_engine.execute_paper_trade(opportunity)
                
                if execution_result.get('success'):
                    # 🎯 CRITICAL: Store COMPLETE position data
                    position_data = execution_result.get('position_data', {})
                    position_id = position_data.get('position_id', execution_result.get('trade_id'))
                    
                    if position_id and position_data:
                        self.open_positions[position_id] = position_data
                        self.logger.info(f"✅ ENHANCED TRADE: {opportunity['symbol']} ({execution_result['strategy_type']})")
                        
                        # Show immediate performance impact
                        self.show_trade_execution_summary(execution_result)
                    else:
                        self.logger.error("❌ Missing position data in execution result")
    
    def show_live_performance_update(self):
        """Show live performance update"""
        portfolio = self.paper_engine.get_enhanced_portfolio_summary()
        basic_stats = self.dashboard._get_basic_stats()
        
        print(f"\n📈 LIVE UPDATE: Balance: ${portfolio['total_value']:,.2f} | "
              f"Trades: {basic_stats['total_trades']} | "
              f"Win Rate: {basic_stats['win_rate']:.1f}% | "
              f"P&L: ${basic_stats['total_pnl']:,.2f}")
    
    def show_trade_execution_summary(self, execution_result: Dict):
        """Show trade execution summary"""
        symbol = execution_result.get('symbol')
        strategy = execution_result.get('strategy_type')
        quantity = execution_result.get('quantity')
        price = execution_result.get('entry_price')
        
        print(f"   🎯 {symbol} | {strategy.upper()} | {quantity} @ ${price} | "
              f"Total: ${quantity * price * 100:,.2f}")
    
    def execute_enhanced_management_action(self, action):
        """Execute enhanced management actions"""
        try:
            if action.action_type == "CLOSE":
                result = self.tasty_api.close_position(action.position_id)
                if result.success:
                    # Record closed trade in enhanced system
                    self._record_closed_trade(action.position_id, result)
                    
            # ... other action types
            
        except Exception as e:
            self.logger.error(f"Error executing enhanced management action: {e}")
    
    def _record_closed_trade(self, position_id: str, result):
        """Record closed trade in enhanced system"""
        try:
            cursor = self.paper_engine.db_conn.cursor()
            cursor.execute('''
                UPDATE enhanced_trades 
                SET status = 'CLOSED', exit_time = ?, exit_price = ?, pnl = ?
                WHERE trade_id = ?
            ''', (datetime.now(), result.fill_price, result.pnl, position_id))
            self.paper_engine.db_conn.commit()
        except Exception as e:
            self.logger.error(f"Error recording closed trade: {e}")
    
    def handle_enhanced_risk_alert(self, alert):
        """Handle enhanced risk alerts"""
        self.logger.warning(f"🚨 ENHANCED RISK ALERT: {alert.message}")
        self.dashboard.send_dual_alert(alert, 'paper')
    
    def stop_enhanced_system(self):
        """Gracefully stop enhanced system"""
        self.logger.info("🛑 Stopping enhanced paper trading system...")
        self.is_running = False
        
        # Generate final performance report
        self.dashboard.generate_performance_report()

def main():
    """Main entry point for enhanced paper trading"""
    try:
        config = TradingConfig()
        orchestrator = EnhancedPaperTradingOrchestrator(config)
        orchestrator.start_enhanced_operation()
        
    except KeyboardInterrupt:
        print("\n🛑 Enhanced system stopped by user")
    except Exception as e:
        print(f"❌ Enhanced system error: {e}")
        logging.error(f"Enhanced system error: {e}")

if __name__ == "__main__":
    main()

    def handle_enhanced_risk_alert(self, alert):
        """Handle enhanced risk alerts with proper error handling"""
        try:
            self.logger.warning(f"🚨 ENHANCED RISK ALERT: {alert.message}")
            
            # 🎯 FIXED: Use the correct method name
            if hasattr(self.dashboard, 'send_dual_alert'):
                self.dashboard.send_dual_alert(alert, 'paper')
            else:
                # Fallback to basic alert
                print(f"🚨 RISK ALERT: {alert.message} (Level: {alert.alert_level})")
                
        except Exception as e:
            self.logger.error(f"❌ Error handling risk alert: {e}")
            # Don't break the system on alert errors
    
    def enhanced_risk_monitoring_loop(self):
        """Enhanced risk monitoring with better error handling"""
        self.logger.info("🛡️ Starting Enhanced Risk Monitoring Loop")
        
        
        while self.is_running:
            try:
                # Enhanced risk assessment
                risk_assessment = self.risk_monitor.assess_portfolio_risk(self.open_positions)
                
                # Only handle meaningful alerts (level 2+)
                if risk_assessment.alert_level >= 2:
                    self.handle_enhanced_risk_alert(risk_assessment)
                    
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"❌ Error in enhanced risk monitoring: {e}")
                time.sleep(30)