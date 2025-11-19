# dual_tastytrade_api.py
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AccountInfo:
    name: str
    account_number: str
    is_paper: bool
    api_instance: object
    balance: float = 0.0
    positions: List[Dict] = None

class DualTastyTradeAPI:
    """
    Manages both live and paper trading accounts simultaneously
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.accounts = {}
        self.trading_mode = os.getenv('TRADING_MODE', 'paper').lower()
        
        # Local position tracking for paper trades (sandbox doesn't persist)
        self.positions_file = 'paper_positions.json'
        self.history_file = 'paper_history.json'
        self.paper_positions = self._load_positions()
        self.paper_history = self._load_history()
        
        # Initialize accounts based on mode
        self._initialize_accounts()

    def close_position(self, position_id: str, exit_price: float = 0.0):
        """Close a paper position and archive it"""
        if position_id in self.paper_positions:
            position = self.paper_positions[position_id]
            
            # Calculate P&L
            entry_price = position.get('entry_price', 0)
            quantity = position.get('quantity', 1)
            strategy = position.get('strategy', '').upper()
            
            # Determine P&L based on strategy type
            # CREDIT strategies (Short): Profit = Entry (Credit) - Exit (Debit)
            # DEBIT strategies (Long): Profit = Exit (Credit) - Entry (Debit)
            
            is_credit = 'CREDIT' in strategy or 'SHORT' in strategy or 'IRON' in strategy
            
            if is_credit:
                # Short position: We sold to open (received credit), buying to close (paying debit)
                pnl = (entry_price - exit_price) * quantity * 100
            else:
                # Long position: We bought to open (paid debit), selling to close (receiving credit)
                pnl = (exit_price - entry_price) * quantity * 100
            
            # Add exit details
            position['exit_price'] = exit_price
            position['exit_time'] = datetime.now().isoformat()
            position['pnl'] = pnl
            position['status'] = 'CLOSED'
            
            # Archive to history
            self.paper_history.append(position)
            self._save_history()
            
            # Remove from active positions
            del self.paper_positions[position_id]
            self._save_positions()
            
            self.logger.info(f"✅ Closed position: {position_id}, Strategy: {strategy}, P&L: ${pnl:.2f}")
            return True
        return False

    def _load_history(self) -> List[Dict]:
        """Load paper trade history from JSON file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    self.logger.info(f"📂 Loaded {len(history)} historical trades")
                    return history
        except Exception as e:
            self.logger.error(f"❌ Error loading history: {e}")
        return []

    def _save_history(self):
        """Save paper trade history to JSON file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.paper_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"❌ Error saving history: {e}")
            
    def get_history(self) -> List[Dict]:
        """Get trade history"""
        return self.paper_history
        
    def _initialize_accounts(self):
        """Initialize live and/or paper accounts based on configuration"""
        from tastytrade_api import TastyTradeAPI
        from alpaca_api import AlpacaAPI
        
        if self.trading_mode in ['paper', 'both']:
            # Check for Alpaca credentials first for paper trading
            if os.getenv('ALPACA_API_KEY'):
                self.logger.info("🦙 Found Alpaca credentials - Using Alpaca for Paper Trading")
                paper_api = AlpacaAPI(paper=True)
                # Alpaca doesn't have 'access_token' check in the same way, so we assume it's good if initialized
                # But we should check if it connected successfully (it logs it)
                
                self.accounts['paper'] = AccountInfo(
                    name="Alpaca Paper",
                    account_number="ALPACA_PAPER",
                    is_paper=True,
                    api_instance=paper_api,
                    balance=paper_api.get_account_balances().get('net_liquidating_value', 100000.0)
                )
                self.logger.info("✅ Alpaca Paper trading account initialized")
            else:
                # Fallback to TastyTrade Sandbox
                self.logger.info("ℹ️ No Alpaca credentials - Using TastyTrade Sandbox for Paper Trading")
                paper_api = TastyTradeAPI(sandbox=True)
                if paper_api.access_token:
                    paper_account_number = os.getenv('TASTYTRADE_PAPER_ACCOUNT_NUMBER')
                    if not paper_account_number:
                        self.logger.warning("⚠️ TASTYTRADE_PAPER_ACCOUNT_NUMBER not set. Using mock account.")
                        paper_account_number = "MOCK_PAPER_ACCOUNT"
                        
                    self.accounts['paper'] = AccountInfo(
                        name="TastyTrade Paper",
                        account_number=paper_account_number,
                        is_paper=True,
                        api_instance=paper_api,
                        balance=float(os.getenv('TASTYTRADE_PAPER_BALANCE', '100000.00'))
                    )
                    self.logger.info("✅ TastyTrade Paper trading account initialized")
        
        if self.trading_mode in ['live', 'both']:
            # Initialize live account
            try:
                live_api = TastyTradeAPI(sandbox=False)
                if live_api.access_token and live_api.access_token != "sandbox_mock_token":
                    # Get real account balance
                    account_data = live_api.get_account_data()
                    live_account_number = os.getenv('TASTYTRADE_LIVE_ACCOUNT_NUMBER')
                    
                    if not live_account_number:
                         self.logger.error("❌ TASTYTRADE_LIVE_ACCOUNT_NUMBER not set in environment variables")
                         # Don't initialize live account if number is missing to prevent errors
                    else:
                        self.accounts['live'] = AccountInfo(
                            name="Live Trading",
                            account_number=live_account_number,
                            is_paper=False,
                            api_instance=live_api,
                            balance=account_data.total_value
                        )
                        self.logger.info("✅ Live trading account initialized")
                else:
                    self.logger.warning("⚠️ Live account authentication failed - skipping")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not initialize live account: {e}")
        
        if not self.accounts:
            self.logger.error("❌ No accounts could be initialized")
            raise Exception("Failed to initialize trading accounts")
    
    def get_account(self, account_type: str) -> Optional[AccountInfo]:
        """Get specific account by type"""
        return self.accounts.get(account_type)
    
    def get_all_accounts(self) -> Dict[str, AccountInfo]:
        """Get all active accounts"""
        return self.accounts
    
    def execute_trade(self, opportunity, account_type: str = 'paper') -> Dict:
        """Execute trade on specified account - accepts dict or dataclass"""
        account = self.get_account(account_type)
        if not account:
            return {'success': False, 'error': f'Account {account_type} not found'}
        
        try:
            # Handle both dict and dataclass opportunity objects
            if isinstance(opportunity, dict):
                symbol = opportunity.get('symbol', '')
                quantity = opportunity.get('quantity', 1)
                premium = opportunity.get('premium', 0)
            else:
                # Dataclass object - use getattr
                symbol = getattr(opportunity, 'symbol', '')
                quantity = getattr(opportunity, 'quantity', 1)
                premium = getattr(opportunity, 'premium', 0)
            
            if account.is_paper:
                # Use paper trading method
                result = account.api_instance.execute_paper_trade(
                    symbol=symbol,
                    order_type='LIMIT',
                    quantity=quantity,
                    price=premium
                )
                self.logger.info(f"📝 Paper trade result: {result}")
            else:
                # Use live trading method if explicitly enabled
                if os.getenv('ENABLE_LIVE_TRADING', 'false').lower() == 'true':
                    result = account.api_instance.execute_trade(opportunity)
                    self.logger.info(f"🚀 Live trade executed: {result}")
                else:
                    result = {'success': False, 'error': 'Live trading disabled. Set ENABLE_LIVE_TRADING=true to enable.'}
                    self.logger.warning("⚠️ Live trading execution disabled (Safety Lock)")
            
            # Update account balance if trade was successful
            if result.get('success'):
                self.logger.info(f"✅ Trade successful, updating balance and storing position")
                self._update_account_balance(account, opportunity, result)
                
                # Store position locally for paper trades
                if account.is_paper:
                    self.logger.info(f"📝 Storing paper position for {symbol}")
                    self._store_paper_position(opportunity, result)
                    self.logger.info(f"📊 Total paper positions: {len(self.paper_positions)}")
            else:
                self.logger.warning(f"❌ Trade failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Trade execution failed on {account_type}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_account_balance(self, account: AccountInfo, opportunity, result: Dict):
        """Update account balance after trade execution - accepts dict or dataclass"""
        try:
            # Handle both dict and dataclass opportunity objects
            if isinstance(opportunity, dict):
                premium = opportunity.get('premium', 0)
            else:
                # Dataclass object
                premium = getattr(opportunity, 'premium', 0)
            
            trade_cost = premium * result.get('quantity', 0) * 100
            account.balance -= trade_cost
            self.logger.info(f"💰 {account.name} balance updated: ${account.balance:.2f}")
        except Exception as e:
            self.logger.error(f"❌ Error updating account balance: {e}")
    
    def get_account_balances(self) -> Dict[str, float]:
        """Get current balances for all accounts"""
        balances = {}
        for account_type, account in self.accounts.items():
            # For paper, use our tracked balance; for live, fetch from API
            if account.is_paper:
                balances[account_type] = account.balance
            else:
                account_data = account.api_instance.get_account_data()
                balances[account_type] = account_data.total_value
                account.balance = account_data.total_value  # Update cached balance
        
        return balances
    
    def get_positions(self, account_type: str = None) -> Dict:
        """Get positions for specified account or all accounts"""
        if account_type:
            account = self.get_account(account_type)
            if not account:
                return {}
            # Return local positions for paper account
            if account.is_paper:
                return self.paper_positions
            return account.api_instance.get_positions()
        else:
            # Return positions from all accounts
            all_positions = {}
            for acc_type, account in self.accounts.items():
                if account.is_paper:
                    all_positions[acc_type] = self.paper_positions
                else:
                    all_positions[acc_type] = account.api_instance.get_positions()
            return all_positions
    
    def _store_paper_position(self, opportunity, result: Dict):
        """Store paper trade position locally"""
        try:
            # Extract opportunity data
            if isinstance(opportunity, dict):
                symbol = opportunity.get('symbol', '')
                strike = opportunity.get('strike', 0)
                option_type = opportunity.get('option_type', '')
                expiration = opportunity.get('expiration', '')
                strategy = opportunity.get('strategy', '')
            else:
                symbol = getattr(opportunity, 'symbol', '')
                strike = getattr(opportunity, 'strike', 0)
                option_type = getattr(opportunity, 'option_type', '')
                expiration = getattr(opportunity, 'expiration', '')
                strategy = getattr(opportunity, 'strategy', '')
            
            # Create position ID
            position_id = f"{symbol}_{strike}_{option_type}_{int(datetime.now().timestamp())}"
            
            # Store position
            self.paper_positions[position_id] = {
                'symbol': symbol,
                'strike': strike,
                'option_type': option_type,
                'expiration': expiration,
                'strategy': strategy,
                'quantity': result.get('quantity', 1),
                'entry_price': result.get('price', 0),
                'entry_time': datetime.now().isoformat(),
                'order_id': result.get('order_id', ''),
                'underlying_price': getattr(opportunity, 'underlying_price', 0) if not isinstance(opportunity, dict) else opportunity.get('underlying_price', 0)
            }
            
            self.logger.info(f"📝 Stored paper position: {position_id}")
            
            # Save to file for persistence
            self._save_positions()
            
        except Exception as e:
            self.logger.error(f"❌ Error storing paper position: {e}")
    
    def _load_positions(self) -> Dict:
        """Load paper positions from JSON file"""
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'r') as f:
                    positions = json.load(f)
                    self.logger.info(f"📂 Loaded {len(positions)} paper positions from file")
                    return positions
        except Exception as e:
            self.logger.error(f"❌ Error loading positions: {e}")
        return {}
    
    def _save_positions(self):
        """Save paper positions to JSON file"""
        try:
            with open(self.positions_file, 'w') as f:
                json.dump(self.paper_positions, f, indent=2)
            self.logger.debug(f"💾 Saved {len(self.paper_positions)} positions to file")
        except Exception as e:
            self.logger.error(f"❌ Error saving positions: {e}")
    

    
    def switch_mode(self, new_mode: str):
        """Switch trading mode dynamically"""
        valid_modes = ['paper', 'live', 'both']
        if new_mode not in valid_modes:
            raise ValueError(f"Invalid mode. Must be one of: {valid_modes}")
        
        self.trading_mode = new_mode
        self._initialize_accounts()  # Reinitialize with new mode
        self.logger.info(f"🔄 Trading mode switched to: {new_mode}")

# Global instance
dual_tasty_api = DualTastyTradeAPI()