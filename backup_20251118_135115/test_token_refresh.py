#!/usr/bin/env python3
"""
Test script to verify TastyTrade OAuth token and get a NEW refresh token
"""

import requests
import json

# Your credentials
CLIENT_ID = "fa651888-974c-4789-a7a8-f03484b21051"
CLIENT_SECRET = "c13b8d53502218d7d55f32773beb09d72ca2752d"
REFRESH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6InJ0K2p3dCIsImtpZCI6IlQ0X1p6WjI1ZnptSjBuWnljWmtERU9iU05XUDVTT0hSMFh1WDFSOVJhRHciLCJqa3UiOiJodHRwczovL2ludGVyaW9yLWFwaS5jaDIudGFzdHl3b3Jrcy5jb20vb2F1dGgvandrcyJ9.eyJpc3MiOiJodHRwczovL2FwaS50YXN0eXRyYWRlLmNvbSIsInN1YiI6IlUwMDAwNzgzMTE2IiwiaWF0IjoxNzYzMDEwNzQxLCJhdWQiOiJmYTY1MTg4OC05NzRjLTQ3ODktYTdhOC1mMDM0ODRiMjEwNTEiLCJncmFudF9pZCI6Ikc3ODc5Yjk3Ni0yNjM4LTQ1N2UtYTQyZC0yNWQ4MWYzNWU0YzMiLCJzY29wZSI6InJlYWQgdHJhZGUgb3BlbmlkIn0.2Nyp4rNLzm3r_JxYKBz3XDzNtkecwgVlz8vYL3snDnA1NeKqIj1-DzEoI-AarWUlH1YJp2oE3kCtTU3JlZlPAw"

print("="*70)
print("🔑 TESTING TASTYTRADE OAUTH TOKEN")
print("="*70)
print()

# Try authentication
auth_url = "https://api.tastyworks.com/oauth/token"
payload = {
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

print(f"📡 Attempting authentication with TastyTrade...")
print(f"   URL: {auth_url}")
print(f"   Grant Type: refresh_token")
print()

try:
    response = requests.post(auth_url, json=payload, timeout=10)
    
    print(f"📊 Response Status: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ SUCCESS! Token is valid!")
        print("="*70)
        print()
        print("📋 RESPONSE DATA:")
        print(json.dumps(data, indent=2))
        print()
        print("="*70)
        
        if 'access_token' in data:
            print(f"✅ Access Token: {data['access_token'][:30]}...")
        
        if 'refresh_token' in data:
            print(f"🔄 NEW Refresh Token: {data['refresh_token'][:30]}...")
            print()
            print("⚠️  IMPORTANT: Save this NEW refresh token!")
            print("   The old one is now invalid.")
            print()
            print("NEW REFRESH TOKEN:")
            print(data['refresh_token'])
        else:
            print("⚠️  No new refresh token in response")
            
    else:
        print("❌ AUTHENTICATION FAILED!")
        print("="*70)
        print()
        print("Response:")
        print(response.text)
        print()
        print("="*70)
        print()
        print("💡 SOLUTION:")
        print("   1. Go to: https://developer.tastytrade.com/")
        print("   2. Log in with your credentials")
        print("   3. Find your OAuth app")
        print("   4. Click 'Regenerate Refresh Token'")
        print("   5. Copy the NEW token and update .env file")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print()
print("="*70)
