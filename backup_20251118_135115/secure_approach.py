# RECOMMENDED SECURE APPROACH:

# Use environment variables
import os
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')  # Set in your system
TASTYTRADE_USERNAME = os.getenv('TASTYTRADE_USERNAME')
TASTYTRADE_PASSWORD = os.getenv('TASTYTRADE_PASSWORD')

# Or use a config file that's in .gitignore
# config_secrets.py (never commit this)