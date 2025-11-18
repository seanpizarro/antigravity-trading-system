# dual_dashboard.py
import logging
from datetime import datetime
from typing import Dict, List

class DualAccountDashboard:
    """Enhanced dashboard for dual account monitoring"""
    
    def __init__(self, deepseek_ai):
        self.deepseek_ai = deepseek_ai
        self.logger = logging.getLogger(__name__)
    
    def generate_dual_account_report(self, positions: Dict, opportunities: List, balances: Dict):
        """Generate comprehensive dual account report"""
        print("\n" + "="*80)
        print("📊 DUAL ACCOUNT TRADING REPORT")
        print("="*80)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Account Balances
        print("💰 ACCOUNT BALANCES")
        print("-" * 40)
        for account_type, balance in balances.items():
            account_name = "Paper Trading" if account_type == 'paper' else "Live Trading"
            print(f"  {account_name}: ${balance:,.2f}")
        print()
        
        # Positions Summary
        print("📈 POSITIONS SUMMARY")
        print("-" * 40)
        total_positions = 0
        for account_type, account_positions in positions.items():
            position_count = len(account_positions)
            total_positions += position_count
            account_name = "Paper" if account_type == 'paper' else "Live"
            print(f"  {account_name}: {position_count} positions")
        print(f"  Total: {total_positions} positions")
        print()
        
        # Top Opportunities
        print("🎯 TOP OPPORTUNITIES")
        print("-" * 40)
        for i, opp in enumerate(opportunities[:5]):
            symbol = opp.get('symbol', 'Unknown')
            option_type = opp.get('option_type', 'call')
            strike = opp.get('strike', 0)
            confidence = opp.get('ai_confidence', 0)
            print(f"  {i+1}. {symbol} {option_type} ${strike} (Confidence: {confidence:.3f})")
        print()
        
        # AI Insights
        print("🤖 AI TRADING INSIGHTS")
        print("-" * 40)
        self._generate_ai_insights(positions, opportunities)
        print("="*80)
    
    def _generate_ai_insights(self, positions: Dict, opportunities: List):
        """Generate AI-powered trading insights"""
        try:
            # Prepare data for AI analysis
            analysis_data = {
                'positions': positions,
                'opportunities': opportunities[:5],
                'timestamp': datetime.now().isoformat()
            }
            
            # Get AI insights
            insights = self.deepseek_ai.analyze_portfolio_health(analysis_data)
            
            if insights:
                print(f"  📈 Market Outlook: {insights.get('market_outlook', 'Neutral')}")
                print(f"  💡 Recommendation: {insights.get('recommendation', 'Hold positions')}")
                print(f"  ⚠️  Risk Level: {insights.get('risk_level', 'Medium')}/10")
            else:
                print("  🔄 AI analysis in progress...")
                
        except Exception as e:
            self.logger.error(f"Error generating AI insights: {e}")
            print("  🔄 AI insights temporarily unavailable")
    
    def send_dual_alert(self, alert, account_type: str):
        """Send alert for specific account"""
        account_name = "PAPER" if account_type == 'paper' else "LIVE"
        print(f"\n🚨 {account_name} ACCOUNT ALERT: {alert.message}")
        print(f"   Level: {alert.alert_level}/10 | Time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Log to file
        self.logger.warning(f"{account_name} Alert - {alert.message} (Level: {alert.alert_level})")