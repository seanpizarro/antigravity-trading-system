"""
Patch script to add multi-account selection within paper and live categories
Allows user to pick specific accounts if multiple exist
"""

# Read the current main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the prompt_account_selection function with enhanced version
old_function = '''def prompt_account_selection():
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
            return None'''

new_function = '''def get_available_accounts():
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
        return [{'id': 'paper', 'name': 'Paper Trading'}], [{'id': 'live', 'name': 'Live Trading'}]

def select_specific_accounts(account_list, account_type_name):
    """Let user select specific accounts from a list"""
    if len(account_list) == 1:
        return [account_list[0]['id']]
    
    print(f"\\n{account_type_name} Accounts Available:")
    for i, acc in enumerate(account_list, 1):
        print(f"{i}. {acc['name']}")
    print(f"{len(account_list) + 1}. All {account_type_name} Accounts")
    print(f"{len(account_list) + 2}. Cancel\\n")
    
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
            
            print(f"❌ Invalid choice. Please enter 1-{len(account_list) + 2}.\\n")
        except KeyboardInterrupt:
            print("\\n❌ Cancelled")
            return None

def prompt_account_selection():
    """Interactive prompt for account selection at startup with multi-account support"""
    print("\\n" + "="*60)
    print("🤖 DUAL-ACCOUNT AI TRADING SYSTEM")
    print("="*60)
    
    # Get available accounts
    paper_accounts, live_accounts = get_available_accounts()
    
    print("\\nWhich account(s) would you like to activate?\\n")
    print("1. 📄 Paper Trading Only")
    print("2. 💰 Live Trading Only")
    print("3. 🔄 Both Paper & Live")
    print("4. ❌ Cancel\\n")
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                # Paper trading only
                selected = select_specific_accounts(paper_accounts, "Paper")
                if selected:
                    return selected
                else:
                    print("Returning to main menu...\\n")
                    continue
                    
            elif choice == "2":
                # Live trading only
                confirm = input("\\n⚠️  WARNING: Live trading uses REAL MONEY. Continue? (yes/no): ").strip().lower()
                if confirm not in ["yes", "y"]:
                    print("❌ Cancelled. Returning to menu...\\n")
                    continue
                
                selected = select_specific_accounts(live_accounts, "Live")
                if selected:
                    return selected
                else:
                    print("Returning to main menu...\\n")
                    continue
                    
            elif choice == "3":
                # Both paper and live
                confirm = input("\\n⚠️  WARNING: This includes LIVE TRADING with real money. Continue? (yes/no): ").strip().lower()
                if confirm not in ["yes", "y"]:
                    print("❌ Cancelled. Returning to menu...\\n")
                    continue
                
                # Select paper accounts
                print("\\n--- Step 1: Select Paper Account(s) ---")
                paper_selected = select_specific_accounts(paper_accounts, "Paper")
                if not paper_selected:
                    print("Returning to main menu...\\n")
                    continue
                
                # Select live accounts
                print("\\n--- Step 2: Select Live Account(s) ---")
                live_selected = select_specific_accounts(live_accounts, "Live")
                if not live_selected:
                    print("Returning to main menu...\\n")
                    continue
                
                return paper_selected + live_selected
                
            elif choice == "4":
                print("\\n❌ Exiting system...")
                return None
            else:
                print("❌ Invalid choice. Please enter 1-4.\\n")
                
        except KeyboardInterrupt:
            print("\\n\\n❌ Cancelled by user")
            return None'''

content = content.replace(old_function, new_function)

# Write the updated content
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully added multi-account selection!")
print("")
print("New Features:")
print("  1. Detects all available paper and live accounts")
print("  2. If multiple accounts exist, shows sub-menu to select specific ones")
print("  3. Can select individual accounts or 'All' for each category")
print("  4. For 'Both' mode, separately choose paper and live accounts")
print("")
print("Example Flow (multiple paper accounts):")
print("  Choose option 1 (Paper Only)")
print("  → Shows: 1. Paper Account A")
print("           2. Paper Account B")
print("           3. All Paper Accounts")
print("           4. Cancel")
print("  → Pick specific account or all")
