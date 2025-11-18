#!/usr/bin/env python3
"""
Test Composer Trade API Integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from composer_api import ComposerTradeAPI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_composer_connection():
    """Test basic Composer API connection"""
    try:
        logger.info("Testing Composer API connection...")
        logger.info("Note: Composer uses Firebase authentication per OpenAPI spec")
        logger.info("Make sure to set COMPOSER_FIREBASE_TOKEN in .env, or use COMPOSER_API_KEY + COMPOSER_API_SECRET")

        composer = ComposerTradeAPI()

        # Test connection
        if composer.test_connection():
            logger.info("✅ Composer API connection successful!")

            # Test basic endpoints (uncomment as needed)
            # accounts = composer.get_accounts_list()
            # logger.info(f"Accounts: {accounts}")

            # Note: Most endpoints require specific account IDs
            # Example: holdings = composer.get_account_holdings('your-account-id')

        else:
            logger.error("❌ Composer API connection failed")
            logger.info("💡 Next steps:")
            logger.info("   1. Get Firebase token from Composer Trade dashboard")
            logger.info("   2. Set COMPOSER_FIREBASE_TOKEN in .env")
            logger.info("   3. Or use API key/secret authentication")
            logger.info("   4. Verify base URL is correct (currently: https://app.composer.trade)")

    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.info("💡 Make sure authentication credentials are set in your .env file")
        logger.info("   Either: COMPOSER_FIREBASE_TOKEN")
        logger.info("   Or both: COMPOSER_API_KEY and COMPOSER_API_SECRET")
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        logger.info("Note: This may be expected if the API endpoints need adjustment")

def test_basic_request():
    """Test basic request to see what response we get"""
    import requests

    # Try different base URLs
    base_urls = [
        "https://api.composer.trade",
        "https://app.composer.trade",
        "https://composer.trade/api",
        "https://investcomposer.com/api"
    ]

    endpoint = "/api/v0.1/accounts/list"

    headers = {
        'Authorization': 'Bearer 897fb2d3-fe63-4eb4-bf4a-992b442c0ea9',
        'X-API-Secret': '417bca0e-a9c1-440c-b7f2-7fe614011f26',
        'Content-Type': 'application/json',
        'User-Agent': 'AI-Options-Trading-System/1.0'
    }

    for base_url in base_urls:
        try:
            url = f"{base_url}{endpoint}"
            logger.info(f"\n🔍 Testing: {url}")

            response = requests.get(url, headers=headers, timeout=10)
            logger.info(f"Status: {response.status_code}")

            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        logger.info(f"✅ JSON Response found at {base_url}")
                        logger.info(f"Response: {data}")
                        return base_url  # Return working base URL
                    except:
                        logger.info(f"❌ HTML response at {base_url}")
                        logger.info(f"Content: {response.text[:200]}...")
                else:
                    logger.info(f"❌ Not JSON content-type: {content_type}")
            else:
                logger.info(f"❌ HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Failed {base_url}: {e}")

    logger.error("❌ No working API endpoint found")
    return None

if __name__ == "__main__":
    test_basic_request()
    # test_composer_connection()