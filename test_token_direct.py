import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Test the paper account token directly
refresh_token = os.getenv('TASTYTRADE_PAPER_REFRESH_TOKEN')
client_id = os.getenv('TASTYTRADE_PAPER_CLIENT_ID')
client_secret = os.getenv('TASTYTRADE_PAPER_CLIENT_SECRET')

print(f"Testing with:")
print(f"  Client ID: {client_id}")
print(f"  Refresh Token (first 50 chars): {refresh_token[:50]}...")

auth_url = "https://api.cert.tastyworks.com/oauth/token"
payload = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
    "client_id": client_id,
    "client_secret": client_secret
}

print(f"\nCalling: {auth_url}")
response = requests.post(auth_url, json=payload, timeout=10)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Body: {response.text}")

if response.status_code == 200:
    print("\n✅ Authentication SUCCESS!")
    token_data = response.json()
    print(f"Access Token (first 50 chars): {token_data.get('access_token', '')[:50]}...")
else:
    print("\n❌ Authentication FAILED!")
