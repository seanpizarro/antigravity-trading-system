## Copilot / AI Agent Instructions — Options Trading System

**⚠️ Educational/Paper Trading Only** - This is an AI-powered options trading system using DeepSeek for decisions and JAX for computations.

### Architecture Overview

**Main orchestration:** `main.py` (live+paper) or `main_enhanced_paper.py` (paper-only) coordinates:
- `deepseek_analyst.py` - AI decision engine (returns typed dataclasses, never dicts)
- `jax_engine.py` - GPU-accelerated Greeks/scoring (pure functions only)
- `tastytrade_api.py` / `dual_tastytrade_api.py` - Trading execution (OAuth + rate limiting)
- `trade_manager.py`, `opportunity_scanner.py`, `risk_monitor.py` - Background daemon threads
- `paper_trading.py` - SQLite-backed paper trading with position persistence
- `composer_api.py` - Optional Composer Trade integration (20+ endpoints, MCP bridge support)

**Multi-account support:** `dual_tastytrade_api.py` manages both live and paper accounts simultaneously. Set `TRADING_MODE` env var to `paper`, `live`, or `both`.

### Critical Patterns

**Threading (DO NOT CHANGE):**
All background loops are daemon threads sharing state via instance properties (`self.open_positions`, `self.opportunity_queue`). **No locks used** - be aware of race conditions. Every loop MUST respect `self.is_running` flag:
```python
while self.is_running:
    try:
        # work here
        time.sleep(interval)
    except Exception as e:
        self.logger.error(f"Error: {e}")
        time.sleep(retry_interval)  # Shorter retry sleep
```

**DeepSeek AI Authority:**
DeepSeek is the decision-maker, not a suggestion provider. All AI methods return typed dataclasses (`ManagementDecision`, `Opportunity`, `RiskAssessment`) - never raw dicts. Add `.get()` method to dataclasses for backward compatibility if needed. All DeepSeek calls go through `_call_deepseek_api()` with task-specific prompt builders (`_build_management_prompt()`, etc.).

**JAX Computational Rules (CRITICAL):**
- JIT-compiled functions MUST be pure (no side effects, no instance methods)
- Define as top-level functions in `jax_engine.py`: `@jit def _black_scholes_jit(S, K, T, r, sigma):`
- Instance methods call JIT functions: `self.jax_engine.calculate_position_metrics(position)`
- Always enable 64-bit: `jax.config.update("jax_enable_x64", True)`

### Developer Workflows

**Setup & Run:**
```bash
pip install -r requirements.txt  # JAX, requests, schedule, pandas, yfinance
# Configure .env file (see SETUP.md) - NEVER commit .env
python main.py  # No CLI args - autonomous operation
```

**Testing:** No unit tests - paper trading is the test environment. Run smoke tests:
```bash
python test_deepseek.py    # Test AI connection
python test_auth.py        # Test TastyTrade OAuth
python test_account.py     # Test account data
python test_composer.py    # Test Composer integration
```

**Paper Trading:** Uses SQLite (`paper_trading.db`) for trade journal. Positions persist in `paper_positions.json`. Default $50k balance. See `paper_trading.py` for execution logic.

### Configuration & Security

**Credentials:** All secrets load from `.env` via `config.py`'s `TradingConfig` dataclass with `__post_init__()`:
```bash
DEEPSEEK_API_KEY=your_key
TASTYTRADE_ACCOUNT=account_number
TASTYTRADE_CLIENT_ID=client_id
TASTYTRADE_CLIENT_SECRET=secret
TASTYTRADE_REFRESH_TOKEN=token
TRADING_MODE=paper  # or live, or both
COMPOSER_FIREBASE_TOKEN=token  # Optional
```

**Risk Parameters (tuned for $3k account):**
- `max_risk_per_trade: 30` (1%)
- `max_capital_per_trade: 45` (1.5%)
- `total_daily_risk: 90` (3%)
- `max_open_positions: 5`
Adjust `config.risk_parameters` for different account sizes.

### Integration Points

**TastyTrade API:** OAuth flow in `_authenticate()`, rate limiting (1s min) in `_make_request()`. Key methods: `get_positions()`, `get_account_data()`, `execute_trade()`. All calls wrapped in try/except.

**Composer API:** Optional integration with 20+ methods. Uses MCP bridge (`composer_mcp_bridge.py`) for subprocess isolation or direct REST fallback. Check `is_configured()` before using. Non-blocking - system works without Composer.

**Logging:** Each module uses `self.logger = logging.getLogger(__name__)`. Main logs to `trading_system.log` + console.

### Project Conventions

**Strategy Types:** Only `CREDIT_SPREAD` and `DEBIT_SPREAD` (defined-risk). No naked options.

**Error Handling:** All background threads must not crash. Use try/except with retry sleep (see pattern above).

**Data Structures:** Dataclasses for AI responses, positions often come as dicts. Handle both safely with `.get()` and type checks.

**Windows Compatibility:** UTF-8 encoding for emojis in logs:
```python
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
```

### Extending the System

**Add AI Capabilities:** Extend `DeepSeekMultiTaskAI` with new methods returning dataclasses.

**Add Computations:** Write top-level pure functions in `jax_engine.py`, decorate with `@jit`, call from instance methods.

**Add Integrations:** Follow `composer_api.py` pattern - check `is_configured()`, graceful degradation, rate limiting.

### Quick Checklist for AI Agents

1. ✅ Preserve thread loop pattern (`self.is_running`, try/except + sleep)
2. ✅ Keep JAX functions pure and top-level (no JIT on instance methods)
3. ✅ Return dataclasses from AI methods (add `.get()` for compatibility)
4. ✅ Never commit secrets (`.env` in `.gitignore`)
5. ✅ Handle data safely (positions may be dicts, check types)
6. ✅ Test with `python test_*.py` smoke scripts
7. ✅ Respect rate limits (1s for TastyTrade, 1s for Composer)
8. ✅ UTF-8 encoding for Windows emoji support

### Key Files to Reference

- Background loop: `trade_manager.py` lines 1-100
- AI pattern: `deepseek_analyst.py` lines 1-100
- JIT pattern: `jax_engine.py`
- OAuth/rate limit: `tastytrade_api.py`
- Multi-account: `dual_tastytrade_api.py`
- Paper trading: `paper_trading.py`
- Optional integration: `composer_api.py`, `composer_mcp_bridge.py`

See `InstructionsClaude.md` for detailed productionization roadmap.
# AI Agent Instructions - Options Trading System

## Project Overview
This is a **personalized AI-powered options trading system** for paper trading that uses DeepSeek for intelligent decision-making and JAX for high-performance computations. The system runs three simultaneous operations: active trade management, continuous opportunity scanning, and real-time risk monitoring.

**⚠️ Educational/Paper Trading Only** - All code is for learning purposes. **Do not use in production without proper testing and risk management.**

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Configure credentials in .env file (see SETUP.md)
# Never commit .env or hardcode credentials

# Run the complete system
python main.py  # No CLI args - autonomous operation
```

## Architecture

### Multi-threaded Orchestrator Pattern
`main.py` coordinates 4 **daemon threads** that share state through instance properties:
- **TradeManager** (every 5 min) - Reviews positions, makes roll/close/adjust decisions  
- **OpportunityScanner** (every 3 min) - Scans market at different frequencies based on time of day
- **RiskMonitor** (every 60 sec) - Assesses portfolio health, triggers alerts
- **Personalizer** (weekly Mon) - Learns trading patterns from history

**Critical Pattern:** All threads must respect `self.is_running` flag for clean shutdown. Each thread loop uses try/except with error recovery sleep intervals:
```python
while self.is_running:
    try:
        # work here
        time.sleep(interval)
    except Exception as e:
        self.logger.error(f"Error: {e}")
        time.sleep(retry_interval)  # Shorter sleep before retry
```

**Shared State Access:** Threads access shared state (`self.open_positions`, `self.opportunity_queue`, `self.risk_alerts`) without explicit locks - this is a known limitation. Be aware of potential race conditions when modifying.

### AI-First Philosophy
**DeepSeek is the decision engine**, not a suggestion provider. All trading decisions (position management, opportunity prioritization, risk assessment) flow through `DeepSeekMultiTaskAI` methods that return **structured dataclasses** (never raw dicts):
- `analyze_position_management(position, metrics, market_conditions)` → `ManagementDecision`
- `prioritize_opportunities(opportunities, open_positions, risk_params)` → `List[Opportunity]`
- `assess_portfolio_risk(positions, account_data, risk_params)` → `RiskAssessment`

**Don't replace AI decisions with hardcoded rules** - extend `DeepSeekMultiTaskAI` if you need new capabilities. All DeepSeek API calls go through `_call_deepseek_api()` private method with task-specific prompt builders (`_build_management_prompt()`, etc.).

### JAX Computational Engine
`jax_engine.py` provides GPU-accelerated vectorized calculations. **All financial computations use JAX** (Greeks, probabilities, opportunity scoring) with JIT-compiled pure functions for performance.

**Critical Constraints:**
- JIT requires **pure functions** (no side effects, no instance methods)
- Top-level functions like `_score_opportunities_jit` are JIT-compiled
- Instance methods call JIT functions: `self.jax_engine.calculate_position_metrics(position)`
- Enable 64-bit precision: `jax.config.update("jax_enable_x64", True)`

Example pattern:
```python
# Top-level pure function for JIT
@jit
def _black_scholes_jit(S, K, T, r, sigma):
    # Pure calculation, no external state
    return price

# Instance method calls JIT function
def calculate_position_metrics(self, position):
    price = _black_scholes_jit(S, K, T, r, sigma)
    return PositionMetrics(...)
```

## Key Workflows

### Running the System
```bash
python main.py  # Starts all threads and main coordination loop
```

The system has **no CLI commands** - it runs autonomously once started. Stop with Ctrl+C (sets `self.is_running = False`).

### Configuration & Credentials
**Critical Security Pattern:** All credentials load from `.env` file (never commit!):
```bash
# .env file structure
DEEPSEEK_API_KEY=your_key_here
TASTYTRADE_ACCOUNT=your_account
TASTYTRADE_CLIENT_ID=your_client_id
TASTYTRADE_CLIENT_SECRET=your_secret
TASTYTRADE_REFRESH_TOKEN=your_token
```

`config.py` uses `TradingConfig` dataclass with `__post_init__()` that loads from `os.getenv()`:
```python
from config import TradingConfig
config = TradingConfig()  # Auto-loads from environment
```

**Risk Parameters:** Tuned for **$3,000 account**:
- `max_risk_per_trade: 30` (1% of account)
- `max_capital_per_trade: 45` (1.5%)
- `total_daily_risk: 90` (3%)
- `max_open_positions: 5`
- Adjust `config.risk_parameters` for different account sizes

### Testing & Debugging
Run individual test files to verify components:
```bash
python test_deepseek.py   # Test AI connection
python test_auth.py       # Test TastyTrade auth
python test_account.py    # Test account data
```

**No unit tests exist** - paper trading is the test environment. System makes real API calls to TastyTrade sandbox.

### Adding New Features
1. **AI capabilities:** Extend `DeepSeekMultiTaskAI` with new methods + dataclass responses
2. **Computations:** Add JIT-compiled pure functions to `jax_engine.py` (not instance methods)
3. **Background loops:** Follow thread pattern with try/except, sleep intervals, `self.is_running` checks
4. **API integration:** Add methods to `tastytrade_api.py` with rate limiting via `_make_request()`

## Code Conventions

### Dataclasses for Structured Data
All AI responses and metrics use typed dataclasses (not dicts). See `deepseek_analyst.py`:
```python
@dataclass
class ManagementDecision:
    position_id: str
    action_type: str  # HOLD, CLOSE, ROLL, ADJUST
    confidence: float
    rationale: str
    parameters: Dict[str, Any]
```

### Logging Pattern
Every module initializes logger: `self.logger = logging.getLogger(__name__)`. Main orchestrator configures logging to both file (`trading_system.log`) and console.

### Error Handling in Loops
Background threads must not crash. Pattern:
```python
while self.is_running:
    try:
        # work here
        time.sleep(interval)
    except Exception as e:
        self.logger.error(f"Error: {e}")
        time.sleep(retry_interval)  # Shorter sleep before retry
```

### Strategy Types
System only trades **defined-risk strategies**: `CREDIT_SPREAD` and `DEBIT_SPREAD`. No naked options, no undefined risk. This is enforced in risk monitoring and opportunity scanning.

## Dependencies

Install via: `pip install -r requirements.txt`

Key libraries:
- **jax/jaxlib** - GPU-accelerated numerics (requires proper GPU setup for full performance)
- **requests** - API communication (DeepSeek, TastyTrade)
- **schedule** - Time-based task scheduling (daily reports)

## Integration Points

### TastyTrade API (`tastytrade_api.py`)
Handles OAuth authentication, rate limiting (1 sec between requests), and order execution:
- **Authentication:** Uses OAuth refresh token flow in `_authenticate()`. Stores `self.access_token`.
- **Rate Limiting:** `_make_request()` enforces `min_request_interval = 1.0` with time-based throttling.
- **Key Methods:**
  - `get_positions()` → Returns dict of current positions
  - `get_account_data()` → Returns `AccountData` dataclass  
  - `execute_trade(opportunity)` → Places orders, returns `TradeResult`

**Error Handling:** All API calls wrapped in try/except. Failed auth raises exception and stops system.

### DeepSeek API Communication
All DeepSeek calls centralized through `_call_deepseek_api()` in `deepseek_analyst.py`:
1. Task-specific prompt builders: `_build_management_prompt()`, `_build_prioritization_prompt()`, `_build_risk_prompt()`
2. API call with retry logic (handles rate limits)
3. Response parsing into typed dataclasses (never raw dicts)

**API Configuration:**
```python
self.base_url = "https://api.deepseek.com/v1"
self.headers = {"Authorization": f"Bearer {api_key}"}
```

### Personalization Learning
`personalization.py` learns patterns from trade history:
- **Runs weekly** (every Monday in `personalization_loop()`)
- Updates `self.trading_style` profile with success patterns
- Influences scanning criteria and opportunity prioritization
- Uses DeepSeek to analyze trade history and extract learnings

## Important Constraints

- **$3,000 account size** - All risk calculations assume this. Adjust `risk_parameters` in config for different sizes.
- **Conservative risk tolerance** - 1% per trade, 3% daily, 10% max drawdown triggers actions.
- **Scanning universe limited** - 17 tickers in default config (ETFs + tech + financials + energy). Large universes impact scan performance.
- **Paper trading only** - No production deployment considerations yet (see `InstructionsClaude.md` for productionization roadmap).

## File Relationships

```
main.py (orchestrator)
  ├── Creates: deepseek_ai, jax_engine, tasty_api instances
  ├── Uses: trade_manager, opportunity_scanner, risk_monitor (pass shared instances)
  └── Coordinates: dashboard, personalizer

deepseek_analyst.py (AI brain)
  └── Called by: trade_manager, opportunity_scanner, risk_monitor, personalizer

jax_engine.py (compute engine)
  └── Called by: trade_manager, opportunity_scanner, risk_monitor

tastytrade_api.py (execution layer)
  └── Called by: main, trade_manager, risk_monitor
```

## When Working on This Codebase

- **Test changes with paper trading** - System makes real API calls to TastyTrade sandbox
- **Monitor thread safety** - Shared state (`open_positions`, etc.) is accessed from multiple threads without explicit locks
- **Respect rate limits** - TastyTrade API enforces limits; `_make_request()` handles this
- **Preserve AI decision authority** - Don't replace DeepSeek decisions with hardcoded rules
- **Keep JAX functions pure** - JIT compilation requires pure functions (no side effects)
- **Check `InstructionsClaude.md`** for productionization requirements if deploying

## Testing Approach

**No unit tests exist** - paper trading is the test environment. System makes real API calls to TastyTrade sandbox.

When adding tests:
- Mock TastyTrade API responses (see `tastytrade_api.py` structure)
- Mock DeepSeek API for deterministic AI responses
- Use JAX's `jax.random.PRNGKey` for reproducible random computations
