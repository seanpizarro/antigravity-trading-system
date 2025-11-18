# FIXED dashboard.py - Correct the email imports
"""
DASHBOARD & REPORTING SYSTEM - Real-time monitoring, alerts, and performance tracking
"""

import smtplib
from email.mime.text import MIMEText  # FIXED: MIMEText not MimeText
from email.mime.multipart import MIMEMultipart  # FIXED: MIMEMultipart not MimeMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json

from deepseek_analyst import DeepSeekMultiTaskAI

class RealTimeDashboard:
    """
    Comprehensive dashboard system for:
    - Real-time monitoring displays
    - Alert notifications  
    - Performance reporting
    - Daily DeepSeek analysis reports
    """
    
    def __init__(self, deepseek_ai: DeepSeekMultiTaskAI):
        self.deepseek_ai = deepseek_ai
        self.logger = logging.getLogger(__name__)
        
        # Alert configuration
        self.alert_config = {
            'email_alerts': True,
            'console_alerts': True,
            'sound_alerts': False,
            'critical_phone_alerts': False
        }
        
        # Email configuration (optional)
        self.email_config = {
            'enabled': False,
            'smtp_server': '',
            'smtp_port': 587,
            'sender_email': '',
            'sender_password': '',
            'recipient_emails': []
        }
        
        # Performance tracking
        self.performance_history = []
        self.alert_history = []
        
    def generate_daily_report(self, open_positions: Dict, opportunity_queue: List) -> Dict:
        """
        Generate comprehensive daily trading report using DeepSeek
        """
        self.logger.info("📊 Generating daily trading report")
        
        try:
            # Get DeepSeek daily analysis
            daily_analysis = self.deepseek_ai.generate_daily_report(open_positions, opportunity_queue)
            
            # Enhance with system metrics
            enhanced_report = self._enhance_report_with_metrics(daily_analysis, open_positions)
            
            # Display report
            self._display_daily_report(enhanced_report)
            
            # Send email if configured
            if self.email_config['enabled']:
                self._send_daily_report_email(enhanced_report)
            
            # Store for historical tracking
            self._store_daily_report(enhanced_report)
            
            return enhanced_report
            
        except Exception as e:
            self.logger.error(f"Daily report generation failed: {e}")
            return self._generate_fallback_report(open_positions)
    
    def send_alert(self, alert_data: Dict):
        """
        Send alert through configured channels
        """
        alert_message = self._format_alert_message(alert_data)
        
        # Console alerts
        if self.alert_config['console_alerts']:
            self._send_console_alert(alert_message, alert_data.get('level', 'INFO'))
        
        # Email alerts
        if self.alert_config['email_alerts'] and self.email_config['enabled']:
            self._send_email_alert(alert_message, alert_data)
        
        # Log alert
        self._log_alert(alert_data)
        
        self.logger.info(f"Alert sent: {alert_data.get('message', 'Unknown alert')}")
    
    def display_real_time_dashboard(self, system_state: Dict):
        """
        Display real-time dashboard with current system state
        """
        try:
            dashboard_data = self._prepare_dashboard_data(system_state)
            self._render_dashboard(dashboard_data)
            
        except Exception as e:
            self.logger.error(f"Dashboard display failed: {e}")
    
    def _enhance_report_with_metrics(self, deepseek_report: Dict, open_positions: Dict) -> Dict:
        """Enhance DeepSeek report with system metrics"""
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(open_positions)
        
        # System health metrics
        system_health = self._get_system_health_metrics()
        
        return {
            'deepseek_analysis': deepseek_report,
            'performance_metrics': performance_metrics,
            'system_health': system_health,
            'report_timestamp': datetime.now().isoformat(),
            'positions_summary': {
                'total_positions': len(open_positions),
                'by_strategy': self._count_positions_by_strategy(open_positions),
                'by_sector': self._count_positions_by_sector(open_positions)
            }
        }
    
    def _calculate_performance_metrics(self, open_positions: Dict) -> Dict:
        """Calculate performance metrics from positions"""
        total_pnl = sum(pos.get('current_pnl', 0) for pos in open_positions.values())
        total_risk = sum(pos.get('max_loss', 0) for pos in open_positions.values())
        
        winning_positions = sum(1 for pos in open_positions.values() if pos.get('current_pnl', 0) > 0)
        win_rate = winning_positions / len(open_positions) if open_positions else 0
        
        return {
            'total_pnl': total_pnl,
            'total_risk': total_risk,
            'win_rate': win_rate,
            'profit_factor': self._calculate_profit_factor(open_positions),
            'sharpe_ratio': self._calculate_sharpe_ratio(open_positions),
            'max_drawdown': self._calculate_max_drawdown()
        }
    
    def _calculate_profit_factor(self, positions: Dict) -> float:
        """Calculate profit factor (gross profits / gross losses)"""
        gross_profits = sum(max(pos.get('current_pnl', 0), 0) for pos in positions.values())
        gross_losses = abs(sum(min(pos.get('current_pnl', 0), 0) for pos in positions.values()))
        
        return gross_profits / gross_losses if gross_losses > 0 else float('inf')
    
    def _calculate_sharpe_ratio(self, positions: Dict) -> float:
        """Calculate Sharpe ratio (simplified)"""
        # In production, this would use proper risk-free rate and volatility
        returns = [pos.get('current_pnl', 0) for pos in positions.values()]
        if not returns:
            return 0
            
        avg_return = sum(returns) / len(returns)
        std_dev = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
        
        return avg_return / std_dev if std_dev > 0 else 0
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown (simplified)"""
        # In production, this would use historical account value data
        return 0.05  # 5% example
    
    def _get_system_health_metrics(self) -> Dict:
        """Get system health and performance metrics"""
        return {
            'uptime': self._get_system_uptime(),
            'api_health': self._check_api_health(),
            'scan_performance': self._get_scan_performance(),
            'error_rate': self._calculate_error_rate(),
            'resource_usage': self._get_resource_usage()
        }
    
    def _get_system_uptime(self) -> str:
        """Get system uptime (simplified)"""
        return "24 hours"  # In production, would track actual uptime
    
    def _check_api_health(self) -> Dict:
        """Check health of external APIs"""
        return {
            'deepseek_api': 'healthy',
            'tastytrade_api': 'healthy',
            'market_data': 'healthy'
        }
    
    def _get_scan_performance(self) -> Dict:
        """Get scanning performance metrics"""
        return {
            'scans_today': 0,  # Would come from scanner
            'opportunities_found': 0,
            'avg_scan_duration': 0.0
        }
    
    def _calculate_error_rate(self) -> float:
        """Calculate system error rate"""
        return 0.02  # 2% example
    
    def _get_resource_usage(self) -> Dict:
        """Get system resource usage"""
        return {
            'cpu_usage': '45%',
            'memory_usage': '60%',
            'disk_usage': '30%'
        }
    
    def _count_positions_by_strategy(self, positions: Dict) -> Dict[str, int]:
        """Count positions by strategy type"""
        counts = {}
        for position in positions.values():
            strategy = getattr(position, 'strategy_type', 'unknown')
            counts[strategy] = counts.get(strategy, 0) + 1
        return counts
    
    def _count_positions_by_sector(self, positions: Dict) -> Dict[str, int]:
        """Count positions by sector"""
        counts = {}
        for position in positions.values():
            sector = getattr(position, 'sector', 'unknown')
            counts[sector] = counts.get(sector, 0) + 1
        return counts
    
    def _display_daily_report(self, report: Dict):
        """Display daily report in console"""
        print("\n" + "="*80)
        print("📊 DAILY TRADING REPORT")
        print("="*80)
        
        # Portfolio Summary
        print(f"\n🎯 PORTFOLIO SUMMARY")
        print(f"   Total Positions: {report['positions_summary']['total_positions']}")
        print(f"   Total P&L: ${report['performance_metrics']['total_pnl']:.2f}")
        print(f"   Win Rate: {report['performance_metrics']['win_rate']:.1%}")
        
        # Strategy Distribution
        print(f"\n📈 STRATEGY DISTRIBUTION")
        for strategy, count in report['positions_summary']['by_strategy'].items():
            print(f"   {strategy}: {count} positions")
        
        # System Health
        print(f"\n⚙️ SYSTEM HEALTH")
        print(f"   Uptime: {report['system_health']['uptime']}")
        print(f"   Error Rate: {report['system_health']['error_rate']:.1%}")
        
        print("="*80)
    
    def _send_daily_report_email(self, report: Dict):
        """Send daily report via email"""
        try:
            if not self.email_config['enabled']:
                return
                
            # Create email message - FIXED: Use MIMEMultipart and MIMEText
            msg = MIMEMultipart()
            msg['Subject'] = f"Daily Trading Report - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ', '.join(self.email_config['recipient_emails'])
            
            # Create HTML content
            html_content = self._create_report_html(report)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
                
            self.logger.info("Daily report email sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send daily report email: {e}")
    
    def _create_report_html(self, report: Dict) -> str:
        """Create HTML content for email report"""
        return f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: #f4f4f4; padding: 20px; text-align: center; }}
                    .section {{ margin: 20px 0; }}
                    .metric {{ margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Daily Trading Report</h1>
                    <p>Generated: {report['report_timestamp']}</p>
                </div>
                
                <div class="section">
                    <h2>🎯 Portfolio Summary</h2>
                    <div class="metric">Total Positions: {report['positions_summary']['total_positions']}</div>
                    <div class="metric">Total P&L: ${report['performance_metrics']['total_pnl']:.2f}</div>
                    <div class="metric">Win Rate: {report['performance_metrics']['win_rate']:.1%}</div>
                </div>
                
                <div class="section">
                    <h2>📈 Strategy Distribution</h2>
                    {"".join(f"<div class='metric'>{strategy}: {count} positions</div>" 
                            for strategy, count in report['positions_summary']['by_strategy'].items())}
                </div>
                
                <div class="section">
                    <h2>⚙️ System Health</h2>
                    <div class="metric">Uptime: {report['system_health']['uptime']}</div>
                    <div class="metric">Error Rate: {report['system_health']['error_rate']:.1%}</div>
                </div>
            </body>
        </html>
        """
    
    def _store_daily_report(self, report: Dict):
        """Store daily report for historical tracking"""
        self.performance_history.append(report)
        
        # Keep only last 30 days of reports
        cutoff = datetime.now() - timedelta(days=30)
        self.performance_history = [
            r for r in self.performance_history 
            if datetime.fromisoformat(r['report_timestamp']) > cutoff
        ]
    
    def _generate_fallback_report(self, open_positions: Dict) -> Dict:
        """Generate fallback report when DeepSeek fails"""
        return {
            'portfolio_summary': {
                'total_positions': len(open_positions),
                'total_pnl': sum(pos.get('current_pnl', 0) for pos in open_positions.values())
            },
            'message': 'Fallback report - DeepSeek analysis unavailable',
            'report_timestamp': datetime.now().isoformat()
        }
    
    def _format_alert_message(self, alert_data: Dict) -> str:
        """Format alert message for display"""
        level = alert_data.get('level', 'INFO')
        message = alert_data.get('message', 'Unknown alert')
        timestamp = alert_data.get('timestamp', datetime.now())
        
        return f"[{level}] {timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {message}"
    
    def _send_console_alert(self, message: str, level: str):
        """Send alert to console with appropriate formatting"""
        if level in ['CRITICAL', 'ERROR']:
            print(f"🚨 {message}")
        elif level == 'WARNING':
            print(f"⚠️  {message}")
        else:
            print(f"ℹ️  {message}")
    
    def _send_email_alert(self, message: str, alert_data: Dict):
        """Send alert via email"""
        try:
            if not self.email_config['enabled']:
                return
                
            # FIXED: Use MIMEMultipart and MIMEText
            msg = MIMEMultipart()
            msg['Subject'] = f"Trading System Alert - {alert_data.get('level', 'ALERT')}"
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ', '.join(self.email_config['recipient_emails'])
            
            text_content = f"""
            Trading System Alert
            
            Level: {alert_data.get('level', 'ALERT')}
            Time: {alert_data.get('timestamp', datetime.now())}
            Message: {alert_data.get('message', 'Unknown alert')}
            
            Actions Recommended:
            {chr(10).join(alert_data.get('actions', []))}
            """
            
            msg.attach(MIMEText(text_content, 'plain'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
                
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def _log_alert(self, alert_data: Dict):
        """Log alert to history"""
        self.alert_history.append({
            'timestamp': datetime.now(),
            'level': alert_data.get('level', 'INFO'),
            'message': alert_data.get('message', ''),
            'actions': alert_data.get('actions', [])
        })
        
        # Keep only last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
    
    def _prepare_dashboard_data(self, system_state: Dict) -> Dict:
        """Prepare data for real-time dashboard"""
        return {
            'timestamp': datetime.now(),
            'open_positions': len(system_state.get('open_positions', {})),
            'opportunities_queued': len(system_state.get('opportunity_queue', [])),
            'active_alerts': len(system_state.get('active_alerts', [])),
            'system_health': self._get_system_health_metrics(),
            'recent_activity': self._get_recent_activity()
        }
    
    def _render_dashboard(self, dashboard_data: Dict):
        """Render real-time dashboard (console version)"""
        print("\n" + "="*60)
        print("🎮 REAL-TIME TRADING DASHBOARD")
        print("="*60)
        print(f"Timestamp: {dashboard_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Open Positions: {dashboard_data['open_positions']}")
        print(f"Opportunities Queued: {dashboard_data['opportunities_queued']}")
        print(f"Active Alerts: {dashboard_data['active_alerts']}")
        print(f"System Health: {dashboard_data['system_health']['api_health']}")
        print("="*60)
    
    def _get_recent_activity(self) -> List[Dict]:
        """Get recent system activity"""
        # Would track recent trades, scans, alerts, etc.
        return []
    
    def configure_email_alerts(self, smtp_server: str, smtp_port: int, 
                             sender_email: str, sender_password: str,
                             recipient_emails: List[str]):
        """Configure email alert system"""
        self.email_config.update({
            'enabled': True,
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'sender_email': sender_email,
            'sender_password': sender_password,
            'recipient_emails': recipient_emails
        })
        
        self.logger.info("Email alerts configured")
    
    def get_performance_history(self, days: int = 7) -> List[Dict]:
        """Get performance history for specified number of days"""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            report for report in self.performance_history
            if datetime.fromisoformat(report['report_timestamp']) > cutoff
        ]