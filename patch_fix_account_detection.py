"""
Fix multi-account selection to properly detect TastyTrade and Alpaca paper accounts
"""

# Read the current main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace get_available_accounts function with improved version
old_get_accounts = '''def get_available_accounts():
    """Get list of available paper and live accounts from dual_tasty_api"""
    try:
        from dual_tastytrade_api import dual_tasty_api
        all_accounts = dual_tasty_api.get_all_accounts()
        
        paper_accounts = []
        live_accounts = []
        
        for account_type, account_info in all_accounts.items():
            if 'paper' in account_type.lower() or 'sandbox' in account_type.lower():
                paper_accounts.append({
                    'id': account_type,
                    'name': account_info.name if hasattr(account_info, 'name') else account_type
                })
            else:
                live_accounts.append({
                    'id': account_type,
                    'name': account_info.name if hasattr(account_info, 'name') else account_type
                })
        
        return paper_accounts, live_accounts
    except Exception as e:
        # Fallback to default single accounts
        return [{'id': 'paper', 'name': 'Paper Trading'}], [{'id': 'live', 'name': 'Live Trading'}]'''

new_get_accounts = '''def get_available_accounts():
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
    
    return paper_accounts, live_accounts'''

content = content.replace(old_get_accounts, new_get_accounts)

# Write the updated content
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed multi-account detection!")
print("")
print("Now detects:")
print("  📄 Alpaca Paper (if ALPACA_API_KEY exists)")
print("  📄 TastyTrade Paper (if TASTYTRADE credentials exist)")
print("  💰 TastyTrade Live (if TASTYTRADE_LIVE_ACCOUNT_NUMBER exists)")
print("")
print("Next run, you'll see:")
print("  Paper Trading Only → Sub-menu with both TastyTrade and Alpaca")
print("  (if you have credentials for both)")
