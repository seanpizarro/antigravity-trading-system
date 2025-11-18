"""Test position persistence"""
import os
import json
from dual_tastytrade_api import dual_tasty_api

# Test 1: Check if positions file exists
print("📁 Checking for positions file...")
if os.path.exists('paper_positions.json'):
    print("✅ paper_positions.json exists")
    with open('paper_positions.json', 'r') as f:
        data = json.load(f)
        print(f"📊 Current positions: {len(data)}")
        for pos_id, pos in data.items():
            print(f"  - {pos_id}: {pos.get('symbol')} {pos.get('strike')}")
else:
    print("❌ paper_positions.json does not exist")

# Test 2: Check current positions in memory
print("\n💾 Checking in-memory positions...")
positions = dual_tasty_api.get_positions('paper')
print(f"📊 Paper positions count: {len(positions)}")
for pos_id, pos in positions.items():
    print(f"  - {pos_id}: {pos}")

# Test 3: Try to manually save positions
print("\n💾 Testing manual save...")
try:
    dual_tasty_api._save_positions()
    print("✅ Manual save successful")
except Exception as e:
    print(f"❌ Manual save failed: {e}")

# Test 4: Check file again
if os.path.exists('paper_positions.json'):
    print("✅ File created after manual save")
    print(f"📄 File size: {os.path.getsize('paper_positions.json')} bytes")
else:
    print("❌ File still doesn't exist")
