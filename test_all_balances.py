#!/usr/bin/env python3
"""Test script to check all account balances."""

import sys
from dual_tastytrade_api import DualTastyTradeAPI

def main():
    """Test all account balances."""
    print("\n" + "=" * 60)
    print("🔍 TESTING ALL ACCOUNT BALANCES")
    print("=" * 60 + "\n")
    
    # Initialize the API
    api = DualTastyTradeAPI()
    
    # Get all account balances
    balances = api.get_account_balances()
    
    print("\n📊 Account Balances:")
    print("-" * 60)
    for account_type, balance in balances.items():
        print(f"  {account_type}: ${balance:,.2f}")
    
    # Get account details
    print("\n\n📋 Account Details:")
    print("-" * 60)
    for account_type in api.accounts.keys():
        account = api.accounts[account_type]
        print(f"\n  {account_type}:")
        print(f"    Name: {account.name}")
        print(f"    Account Number: {account.account_number}")
        print(f"    Is Paper: {account.is_paper}")
        print(f"    Balance (cached): ${account.balance:,.2f}")
        
        # Get fresh account data
        try:
            if account.api_instance:
                account_data = account.api_instance.get_account_data()
                print(f"    Balance (API): ${account_data.total_value:,.2f}")
                print(f"    Buying Power: ${account_data.buying_power:,.2f}")
                print(f"    Cash: ${account_data.cash_balance:,.2f}")
        except Exception as e:
            print(f"    Error fetching API data: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
