# Educational Purpose Only - Paper Trading
"""
DEEPSEEK MULTI-TASK AI ANALYST - Handles trade management, scanning, and risk assessment
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class ManagementDecision:
    """Trade management decision from DeepSeek"""
    position_id: str
    action_type: str  # HOLD, CLOSE, ROLL, ADJUST
    confidence: float
    rationale: str
    parameters: Dict[str, Any]

@dataclass
class Opportunity:
    """Trading opportunity identified by DeepSeek"""
    ticker: str
    strategy_type: str  # CREDIT_SPREAD, DEBIT_SPREAD
    confidence: float
    priority: int
    rationale: str
    parameters: Dict[str, Any]

@dataclass
class RiskAssessment:
    """Risk assessment from DeepSeek"""
    alert_level: int  # 0-10 scale
    message: str
    concerns: List[str]
    recommendations: List[str]
    
    def get(self, key, default=None):
        """Provide dictionary-like access for backward compatibility"""
        if hasattr(self, key):
            return getattr(self, key)
        return default
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'alert_level': self.alert_level,
            'message': self.message,
            'concerns': self.concerns,
            'recommendations': self.recommendations
        }

class DeepSeekMultiTaskAI:
    """
    Multi-task AI that simultaneously:
    1. Manages open positions
    2. Evaluates new opportunities  
    3. Assesses portfolio risk
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
        
        # Conversation context for personalized responses
        self.conversation_context = {
            "trading_style": "defined_risk_options",
            "account_size": 100000,
            "risk_tolerance": "conservative",
            "preferred_strategies": ["credit_spreads", "debit_spreads"]
        }
    
    def analyze_position_management(self, position: Dict, metrics: Dict, 
                                  market_conditions: Dict) -> ManagementDecision:
        """
        DeepSeek decides when to roll, close, or adjust positions
        """
        prompt = self._build_management_prompt(position, metrics, market_conditions)
        
        response = self._call_deepseek_api(prompt, "position_management")
        
        return ManagementDecision(
            position_id=position.position_id,
            action_type=response.get('action', 'HOLD'),
            confidence=response.get('confidence', 0.5),
            rationale=response.get('rationale', 'No rationale provided'),
            parameters=response.get('parameters', {})
        )
    
    def prioritize_opportunities(self, opportunities: List[Dict], 
                               open_positions: Dict,
                               risk_params: Dict) -> List[Opportunity]:
        """
        DeepSeek evaluates and prioritizes new trading opportunities
        """
        prompt = self._build_prioritization_prompt(opportunities, open_positions, risk_params)
        
        response = self._call_deepseek_api(prompt, "opportunity_prioritization")
        
        prioritized_opportunities = []
        for opp_data in response.get('opportunities', []):
            prioritized_opportunities.append(Opportunity(
                ticker=opp_data['ticker'],
                strategy_type=opp_data['strategy_type'],
                confidence=opp_data['confidence'],
                priority=opp_data['priority'],
                rationale=opp_data['rationale'],
                parameters=opp_data['parameters']
            ))
            
        return sorted(prioritized_opportunities, key=lambda x: x.priority)
    
    def assess_portfolio_risk(self, portfolio_data: Dict, 
                            market_conditions: Dict,
                            open_positions: Dict) -> RiskAssessment:
        """
        DeepSeek provides real-time portfolio risk assessment
        """
        prompt = self._build_risk_assessment_prompt(portfolio_data, market_conditions, open_positions)
        
        response = self._call_deepseek_api(prompt, "risk_assessment")
        
        return RiskAssessment(
            alert_level=response.get('alert_level', 0),
            message=response.get('message', 'No issues detected'),
            concerns=response.get('concerns', []),
            recommendations=response.get('recommendations', [])
        )
    
    def generate_daily_report(self, open_positions: Dict, opportunity_queue: List) -> Dict:
        """
        Generate comprehensive daily trading report
        """
        prompt = self._build_daily_report_prompt(open_positions, opportunity_queue)
        
        return self._call_deepseek_api(prompt, "daily_reporting")
    
    def _build_management_prompt(self, position: Dict, metrics: Dict, market_conditions: Dict) -> str:
        """Build prompt for position management decisions"""
        return f"""
        POSITION MANAGEMENT ANALYSIS - DEFINED RISK OPTIONS
        
        CURRENT POSITION:
        - Ticker: {position.ticker}
        - Strategy: {position.strategy_type}
        - DTE: {position.dte}
        - Current P&L: {position.current_pnl}
        - Entry Date: {position.entry_date}
        
        CURRENT METRICS:
        - Delta: {metrics.delta}
        - Theta: {metrics.theta}
        - Gamma: {metrics.gamma}
        - Vega: {metrics.vega}
        - Probability of Profit: {metrics.pop}
        - Days Since Entry: {metrics.days_since_entry}
        
        MARKET CONDITIONS:
        - VIX: {market_conditions.get('vix')}
        - Market Trend: {market_conditions.get('market_trend')}
        - Sector Performance: {market_conditions.get('sector_performance')}
        - Volatility Regime: {market_conditions.get('volatility_regime')}
        
        ACCOUNT CONTEXT:
        - Account Size: ${self.conversation_context['account_size']}
        - Risk Tolerance: {self.conversation_context['risk_tolerance']}
        
        MANAGEMENT DECISION NEEDED:
        Should we HOLD, CLOSE, ROLL, or ADJUST this position?
        
        CONSIDERATIONS:
        1. Probability of Profit changes
        2. Time decay (theta) acceleration points
        3. Volatility changes impact
        4. Portfolio correlation and diversification
        5. Risk-adjusted returns
        6. Market regime alignment
        
        For ROLL decisions, specify:
        - Target DTE
        - Strike adjustments
        - Credit/Debit targets
        
        For CLOSE decisions, specify:
        - Profit target achievement
        - Loss threshold breach
        - Thesis invalidation
        
        Respond with JSON format:
        {{
            "action": "HOLD|CLOSE|ROLL|ADJUST",
            "confidence": 0.0-1.0,
            "rationale": "Detailed reasoning",
            "parameters": {{ ... action-specific parameters ... }}
        }}
        """
    
    def _build_prioritization_prompt(self, opportunities: List[Dict], 
                                   open_positions: Dict, risk_params: Dict) -> str:
        """Build prompt for opportunity prioritization"""
        return f"""
        OPPORTUNITY PRIORITIZATION - DEFINED RISK OPTIONS
        
        NEW OPPORTUNITIES TO EVALUATE:
        {json.dumps(opportunities, indent=2)}
        
        CURRENT PORTFOLIO:
        - Total Positions: {len(open_positions)}
        - Positions by Sector: {self._get_sector_breakdown(open_positions)}
        - Current Greeks: {self._get_portfolio_greeks(open_positions)}
        
        RISK PARAMETERS:
        - Max Risk per Trade: ${risk_params.get('max_risk_per_trade')}
        - Max Open Positions: {risk_params.get('max_open_positions')}
        - Sector Limits: {risk_params.get('sector_limits')}
        
        PRIORITIZATION CRITERIA:
        1. Risk-Adjusted Return Potential
        2. Portfolio Diversification Benefit
        3. Probability of Success
        4. Market Regime Alignment
        5. Liquidity and Execution Quality
        6. Current Portfolio Gaps
        
        ACCOUNT CONTEXT:
        - Size: ${self.conversation_context['account_size']}
        - Style: {self.conversation_context['trading_style']}
        - Risk: {self.conversation_context['risk_tolerance']}
        
        TASK:
        Rank these opportunities from 1 (highest) to {len(opportunities)} (lowest)
        Provide confidence scores and specific parameters for execution.
        
        Respond with JSON format:
        {{
            "opportunities": [
                {{
                    "ticker": "SPY",
                    "strategy_type": "CREDIT_SPREAD",
                    "confidence": 0.85,
                    "priority": 1,
                    "rationale": "Why this is a good opportunity",
                    "parameters": {{
                        "width": 3,
                        "dte": 45,
                        "credit_target": 0.50,
                        "pop_min": 0.70
                    }}
                }}
            ]
        }}
        """
    
    def _build_risk_assessment_prompt(self, portfolio_data, 
                                    market_conditions: Dict, open_positions: Dict) -> str:
        """Build prompt for risk assessment"""
        # Handle both dict and dataclass
        if hasattr(portfolio_data, 'total_value'):
            total_value = portfolio_data.total_value
            buying_power = portfolio_data.buying_power
            margin_usage = portfolio_data.margin_usage * 100
            max_drawdown = portfolio_data.max_drawdown
            net_delta = portfolio_data.portfolio_greeks.get('delta', 0)
            net_gamma = portfolio_data.portfolio_greeks.get('gamma', 0)
            net_theta = portfolio_data.portfolio_greeks.get('theta', 0)
            net_vega = portfolio_data.portfolio_greeks.get('vega', 0)
        else:
            total_value = portfolio_data.get('total_value', 0)
            buying_power = portfolio_data.get('buying_power', 0)
            margin_usage = portfolio_data.get('margin_usage', 0)
            max_drawdown = portfolio_data.get('max_drawdown', 0)
            net_delta = portfolio_data.get('net_delta', 0)
            net_gamma = portfolio_data.get('net_gamma', 0)
            net_theta = portfolio_data.get('net_theta', 0)
            net_vega = portfolio_data.get('net_vega', 0)
            
        return f"""
        PORTFOLIO RISK ASSESSMENT - DEFINED RISK OPTIONS
        
        PORTFOLIO DATA:
        - Total Value: ${total_value}
        - Buying Power: ${buying_power}
        - Margin Usage: {margin_usage:.1f}%
        - Max Drawdown: {max_drawdown:.1f}%
        
        PORTFOLIO GREEKS:
        - Net Delta: {net_delta}
        - Net Gamma: {net_gamma}
        - Net Theta: {net_theta}
        - Net Vega: {net_vega}
        
        MARKET CONDITIONS:
        - VIX: {market_conditions.get('vix')}
        - Market Trend: {market_conditions.get('market_trend')}
        - Economic Events: {market_conditions.get('economic_events')}
        - Sector Rotation: {market_conditions.get('sector_rotation')}
        
        OPEN POSITIONS:
        - Count: {len(open_positions)}
        - Sector Concentration: {self._get_sector_concentration(open_positions)}
        - Strategy Mix: {self._get_strategy_mix(open_positions)}
        
        RISK ASSESSMENT REQUESTED:
        1. Overall Risk Level (0-10 scale)
        2. Key Concerns and Vulnerabilities
        3. Recommended Protective Actions
        4. Portfolio Optimization Suggestions
        
        Alert Level Guide:
        0-3: Normal - No action needed
        4-6: Caution - Monitor closely
        7-8: Warning - Consider adjustments
        9-10: Critical - Take immediate action
        
        Respond with JSON format:
        {{
            "alert_level": 5,
            "message": "Summary risk assessment",
            "concerns": ["Risk factor 1", "Risk factor 2"],
            "recommendations": ["Action 1", "Action 2"]
        }}
        """
    
    def _build_daily_report_prompt(self, open_positions: Dict, opportunity_queue: List) -> str:
        """Build prompt for daily reporting"""
        return f"""
        DAILY TRADING REPORT - DEFINED RISK OPTIONS
        
        Please provide a comprehensive daily report covering:
        
        1. PORTFOLIO PERFORMANCE:
           - Daily P&L summary
           - Best/worst performing positions
           - Overall portfolio health assessment
        
        2. TRADE MANAGEMENT SUMMARY:
           - Positions managed today (closed/rolled/adjusted)
           - Management decisions and rationale
           - Current position status
        
        3. OPPORTUNITY ANALYSIS:
           - New opportunities identified
           - Trades executed today
           - Top opportunities in queue
        
        4. RISK ASSESSMENT:
           - Current portfolio risk level
           - Concerns or vulnerabilities
           - Recommended risk management actions
        
        5. TOMORROW'S OUTLOOK:
           - Market expectations and key levels
           - Positions requiring close monitoring
           - Recommended scanning focus areas
        
        6. PERSONALIZED INSIGHTS:
           - Pattern observations from recent trades
           - Style alignment assessment
           - Improvement suggestions
        
        PORTFOLIO CONTEXT:
        - Account Size: ${self.conversation_context['account_size']}
        - Open Positions: {len(open_positions)}
        - Opportunities in Queue: {len(opportunity_queue)}
        - Trading Style: {self.conversation_context['trading_style']}
        
        Format as a professional trader's daily briefing with specific,
        actionable insights. Focus on defined-risk options strategies.
        """
    
    def _call_deepseek_api(self, prompt: str, task_type: str) -> Dict[str, Any]:
        """
        Make API call to DeepSeek with error handling and rate limiting
        """
        try:
            messages = [
                {
                    "role": "system", 
                    "content": self._get_system_prompt(task_type)
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.1,  # Low temperature for consistency
                    "max_tokens": 2000  # Reduced from 4000 for faster responses
                },
                timeout=60  # Increased from 30 to handle slow API responses
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                
                # Try to parse JSON response
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Fallback: extract JSON from text response
                    return self._extract_json_from_text(content)
                    
            else:
                self.logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(task_type)
                
        except requests.exceptions.Timeout:
            self.logger.error("DeepSeek API timeout")
            return self._get_fallback_response(task_type)
        except Exception as e:
            self.logger.error(f"DeepSeek API exception: {e}")
            return self._get_fallback_response(task_type)
        finally:
            # Rate limiting
            time.sleep(1)
    
    def _get_system_prompt(self, task_type: str) -> str:
        """Get system prompt for different task types"""
        base_prompt = """
        You are an expert options trading analyst specializing in defined-risk strategies 
        for a $3,000 account. Your expertise includes credit spreads, debit spreads, 
        and risk management for small accounts.
        
        Key Principles:
        - Always prioritize defined risk (know worst-case upfront)
        - Favor high probability setups (70%+ for credits)
        - Maintain strict position sizing (1% risk per trade max)
        - Consider portfolio diversification and correlation
        - Avoid earnings announcements and major catalysts
        - Focus on liquid underlyings with tight spreads
        
        Response must be in valid JSON format.
        """
        
        if task_type == "position_management":
            return base_prompt + """
            Focus on optimal trade management: when to hold, close, roll, or adjust
            based on probability changes, time decay, and market conditions.
            """
        elif task_type == "opportunity_prioritization":
            return base_prompt + """
            Focus on identifying highest probability, best risk-adjusted opportunities
            that complement the current portfolio.
            """
        elif task_type == "risk_assessment":
            return base_prompt + """
            Focus on portfolio-level risk: Greeks exposure, concentration, 
            market regime alignment, and protective actions.
            """
        else:
            return base_prompt
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text response as fallback"""
        try:
            # Look for JSON pattern in text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except:
            pass
            
        return self._get_fallback_response("general")
    
    def _get_fallback_response(self, task_type: str) -> Dict[str, Any]:
        """Provide fallback responses when API fails"""
        if task_type == "position_management":
            return {
                "action": "HOLD",
                "confidence": 0.5,
                "rationale": "Fallback: Holding due to API issue",
                "parameters": {}
            }
        elif task_type == "opportunity_prioritization":
            return {"opportunities": []}
        elif task_type == "risk_assessment":
            return {
                "alert_level": 0,
                "message": "Fallback: No risk assessment available",
                "concerns": ["API connectivity issue"],
                "recommendations": ["Check API connection"]
            }
        else:
            return {"status": "error", "message": "API unavailable"}
    
    # Helper methods for prompt building
    def _get_sector_breakdown(self, positions: Dict) -> Dict[str, int]:
        breakdown = {}
        for position in positions.values():
            sector = getattr(position, 'sector', 'unknown')
            breakdown[sector] = breakdown.get(sector, 0) + 1
        return breakdown
    
    def _get_portfolio_greeks(self, positions: Dict) -> Dict[str, float]:
        greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
        for position in positions.values():
            for greek in greeks:
                greeks[greek] += position.get(greek, 0)
        return greeks
    
    def _get_sector_concentration(self, positions: Dict) -> Dict[str, float]:
        sector_values = {}
        total_value = sum(pos.get('value', 0) for pos in positions.values())
        
        if total_value == 0:
            return {}
            
        for position in positions.values():
            sector = getattr(position, 'sector', 'unknown')
            sector_values[sector] = sector_values.get(sector, 0) + getattr(position, 'value', 0)
        
        return {sector: value/total_value for sector, value in sector_values.items()}
    
    def _get_strategy_mix(self, positions: Dict) -> Dict[str, int]:
        mix = {}
        for position in positions.values():
            strategy = getattr(position, 'strategy_type', 'unknown')
            mix[strategy] = mix.get(strategy, 0) + 1
        return mix