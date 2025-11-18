#!/usr/bin/env python3
"""
Helper script to generate TastyTrade OAuth tokens for LIVE account
"""

import requests
import json
from getpass import getpass

def generate_oauth_token():
    """Generate OAuth refresh token for TastyTrade LIVE account"""
    
    print("=" * 60)
    print("🔑 TASTYTRADE LIVE ACCOUNT OAUTH TOKEN GENERATOR")
    print("=" * 60)
    print()
    print("This will generate a refresh token for your LIVE TastyTrade account.")
    print("⚠️  This is for REAL MONEY trading - use carefully!")
    print()
    
    # Get credentials
    username = input("Enter your TastyTrade username: ").strip()
    password = getpass("Enter your TastyTrade password: ").strip()
    
    print("\nAuthenticating with TastyTrade LIVE API...")
    
    # Step 1: Get session token
    session_url = "https://api.tastytrade.com/sessions"
    session_data = {
        "login": username,
        "password": password
    }
    
    try:
        response = requests.post(session_url, json=session_data)
        
        if response.status_code == 201:
            session_info = response.json()
            session_token = session_info['data']['session-token']
            user_id = session_info['data']['user']['external-id']
            
            print(f"✅ Successfully authenticated!")
            print(f"   User ID: {user_id}")
            print()
            
            # Step 2: Manual instructions for OAuth
            print()
            print("=" * 60)
            print("📋 MANUAL SETUP REQUIRED")
            print("=" * 60)
            print()
            print("TastyTrade requires you to create OAuth apps through their website.")
            print()
            print("Please follow these steps:")
            print()
            print("1. Go to: https://developer.tastytrade.com/")
            print("2. Log in with your credentials")
            print("3. Navigate to 'My Apps' or 'OAuth Applications'")
            print("4. Click 'Create New Application'")
            print("5. Fill in:")
            print("   - Name: Live Trading Bot")
            print("   - Redirect URI: http://localhost:8080/callback")
            print("   - Scopes: read, trade, openid")
            print()
            print("6. After creating, copy the following:")
            print("   - Client ID")
            print("   - Client Secret")
            print("   - Refresh Token (generate one)")
            print()
            print("=" * 60)
            print()
            
            # Get credentials manually
            print("Once you have created the OAuth app, enter the details:")
            print()
            client_id = input("Enter Client ID: ").strip()
            client_secret = input("Enter Client Secret: ").strip()
            refresh_token = input("Enter Refresh Token: ").strip()
            
            if client_id and client_secret and refresh_token:
                print()
                print("=" * 60)
                print("✅ SUCCESS! Your OAuth credentials:")
                print("=" * 60)
                print()
                print(f"Client ID: {client_id}")
                print(f"Client Secret: {client_secret}")
                print(f"Refresh Token: {refresh_token}")
                print()
                print("=" * 60)
                print()
                print("📝 Now add these to your .env file:")
                print()
                print(f"TASTYTRADE_LIVE_CLIENT_ID={client_id}")
                print(f"TASTYTRADE_LIVE_CLIENT_SECRET={client_secret}")
                print(f"TASTYTRADE_LIVE_REFRESH_TOKEN={refresh_token}")
                print()
                print("⚠️  Save these credentials securely!")
                print("=" * 60)
                
                # Offer to update .env automatically
                update = input("\nWould you like me to update your .env file automatically? (yes/no): ").strip().lower()
                if update in ['yes', 'y']:
                    update_env_file(client_id, client_secret, refresh_token)
            else:
                print("❌ Please provide all required credentials.")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def update_env_file(client_id, client_secret, refresh_token):
    """Update .env file with new credentials"""
    try:
        # Read existing .env
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update the live account credentials
        updated_lines = []
        for line in lines:
            if line.startswith('TASTYTRADE_LIVE_CLIENT_ID='):
                updated_lines.append(f'TASTYTRADE_LIVE_CLIENT_ID={client_id}\n')
            elif line.startswith('TASTYTRADE_LIVE_CLIENT_SECRET='):
                updated_lines.append(f'TASTYTRADE_LIVE_CLIENT_SECRET={client_secret}\n')
            elif line.startswith('TASTYTRADE_LIVE_REFRESH_TOKEN='):
                updated_lines.append(f'TASTYTRADE_LIVE_REFRESH_TOKEN={refresh_token}\n')
            else:
                updated_lines.append(line)
        
        # Write back
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ .env file updated successfully!")
        print("   You can now restart main.py to use both accounts.")
        
    except Exception as e:
        print(f"❌ Error updating .env: {e}")
        print("   Please update manually.")

if __name__ == "__main__":
    generate_oauth_token()
