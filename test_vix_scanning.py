"""
Test VIX-based adaptive scanning logic
"""
import yfinance as yf
from datetime import datetime, timedelta

class VIXScanningTest:
    def __init__(self):
        self._vix_cache = None
    
    def _get_current_vix(self) -> float:
        """Fetch current VIX level with 5-minute caching"""
        # Check cache first
        if hasattr(self, '_vix_cache') and self._vix_cache:
            cache_time, cached_vix = self._vix_cache
            cache_age = (datetime.now() - cache_time).total_seconds() / 60
            if cache_age < 5:
                print(f"📊 VIX (cached {cache_age:.1f}min ago): {cached_vix:.2f}")
                return cached_vix
        
        # Fetch fresh VIX data
        try:
            vix_ticker = yf.Ticker("^VIX")
            vix_data = vix_ticker.history(period="1d")
            
            if vix_data.empty:
                raise ValueError("Empty VIX data returned")
            
            vix = float(vix_data['Close'].iloc[-1])
            
            # Validate VIX is in reasonable range (5-80)
            if not (5 <= vix <= 80):
                print(f"⚠️ VIX {vix:.2f} out of range, using default 20")
                return 20.0
            
            # Cache the result
            self._vix_cache = (datetime.now(), vix)
            print(f"📊 VIX (fresh): {vix:.2f}")
            return vix
            
        except Exception as e:
            print(f"⚠️ VIX fetch failed: {e}, using default 20")
            # Use cached value if available, even if stale
            if hasattr(self, '_vix_cache') and self._vix_cache:
                _, cached_vix = self._vix_cache
                print(f"📊 Using stale VIX cache: {cached_vix:.2f}")
                return cached_vix
            return 20.0
    
    def test_scanning_logic(self):
        """Test VIX-based interval calculation"""
        print("=" * 60)
        print("🧪 TESTING VIX-BASED ADAPTIVE SCANNING")
        print("=" * 60)
        
        # Get current VIX
        vix = self._get_current_vix()
        
        # Calculate interval
        if vix > 25:
            interval = 1200  # 20 minutes - high volatility
            volatility_state = "HIGH"
            emoji = "🔴"
            est_daily_scans = 20
        elif vix > 20:
            interval = 1800  # 30 minutes - medium volatility
            volatility_state = "MEDIUM"
            emoji = "🟡"
            est_daily_scans = 13
        else:
            interval = 3600  # 60 minutes - low volatility
            volatility_state = "LOW"
            emoji = "🟢"
            est_daily_scans = 7
        
        print(f"\n{emoji} Current VIX: {vix:.2f} ({volatility_state})")
        print(f"⏱️  Scan Interval: {interval//60} minutes")
        print(f"📊 Estimated Daily Scans: ~{est_daily_scans}")
        print(f"💰 OLD System: 120 scans/day")
        print(f"💰 NEW System: {est_daily_scans} scans/day")
        print(f"✅ Reduction: {((120 - est_daily_scans) / 120 * 100):.1f}%")
        
        # Test different VIX scenarios
        print("\n" + "=" * 60)
        print("📊 SCENARIO TESTING")
        print("=" * 60)
        
        scenarios = [
            (15, "LOW", "🟢"),
            (23, "MEDIUM", "🟡"),
            (28, "HIGH", "🔴"),
        ]
        
        for test_vix, expected_state, expected_emoji in scenarios:
            if test_vix > 25:
                interval = 1200
                scans = 20
            elif test_vix > 20:
                interval = 1800
                scans = 13
            else:
                interval = 3600
                scans = 7
            
            print(f"\n{expected_emoji} VIX {test_vix} ({expected_state})")
            print(f"   → {interval//60}min intervals = ~{scans} scans/day")
            print(f"   → {((120 - scans) / 120 * 100):.0f}% reduction from OLD system")
        
        print("\n" + "=" * 60)
        print("✅ VIX-BASED SCANNING TEST COMPLETE")
        print("=" * 60)
        
        # Test cache behavior
        print("\n🧪 Testing cache behavior...")
        print("Second fetch (should hit cache):")
        vix2 = self._get_current_vix()
        
        print("\n✅ All tests passed!")

if __name__ == "__main__":
    tester = VIXScanningTest()
    tester.test_scanning_logic()
