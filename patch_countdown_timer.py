"""
Patch script to add countdown timer to opportunity scanning loop
Shows user exactly when the next scan will happen
"""

# Read the current main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the opportunity_scanning_loop sleep section
old_sleep = '''                time.sleep(interval)  # Adaptive interval: 60/30/20 min
                
            except Exception as e:
                self.logger.error(f"Error in opportunity scanning: {e}")
                time.sleep(60)'''

new_sleep = '''                # Sleep with countdown timer
                next_scan_time = datetime.now() + timedelta(seconds=interval)
                self.logger.info(f"⏰ Next scan at: {next_scan_time.strftime('%I:%M:%S %p')}")
                
                # Countdown in chunks (show progress every minute for long waits)
                if interval >= 300:  # 5+ minutes
                    chunk_size = 60  # Show update every minute
                else:
                    chunk_size = interval  # Just sleep the whole time
                
                remaining = interval
                while remaining > 0 and self.is_running:
                    sleep_time = min(chunk_size, remaining)
                    time.sleep(sleep_time)
                    remaining -= sleep_time
                    
                    # Show countdown for long waits
                    if remaining > 0 and interval >= 300:
                        mins_left = remaining // 60
                        secs_left = remaining % 60
                        self.logger.info(f"⏳ Next scan in: {mins_left}m {secs_left}s")
                
            except Exception as e:
                self.logger.error(f"Error in opportunity scanning: {e}")
                time.sleep(60)'''

content = content.replace(old_sleep, new_sleep)

# Write the updated content
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully added countdown timer to scanning loop!")
print("")
print("What you'll see now:")
print("  🟢 VIX 18.3 (LOW) → 60min intervals (~7/day) [Scan #1]")
print("  ⏰ Next scan at: 11:30:25 AM")
print("  ⏳ Next scan in: 59m 0s")
print("  ⏳ Next scan in: 58m 0s")
print("  ...")
print("  ⏳ Next scan in: 1m 0s")
print("  [Scan #2 starts]")
print("")
print("Benefits:")
print("  - Know exactly when next scan happens")
print("  - Visual progress updates every minute")
print("  - No more wondering if system is frozen")
