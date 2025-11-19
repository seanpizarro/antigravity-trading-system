# Example: API call snippet
import requests

def get_data(url, headers=None):
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()
