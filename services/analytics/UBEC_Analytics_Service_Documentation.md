# UBEC Analytics Service - Complete Documentation

## Overview

The **UBEC Analytics Service** provides comprehensive, read-only analytics and insights for the UBEC token ecosystem. It analyzes distribution patterns, holder concentration, transaction trends, and ecosystem health across all four UBEC elements (Air, Water, Earth, Fire).

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Design Principles**: All 12 principles followed

---

## Features

### Core Analytics Capabilities

1. **Token Distribution Analysis**
   - Total holders and supply
   - Average/median/min/max balances
   - Top-N holder concentration
   - Gini coefficient (inequality measure)

2. **Holder Concentration**
   - Whale identification
   - Tier analysis (whales, mid-tier, small holders)
   - Percentage of supply by tier
   - Custom threshold support

3. **Transaction Metrics**
   - Transaction velocity (tx/day)
   - Unique sender/receiver counts
   - Volume and turnover analysis
   - Time-period filtering

4. **Liquidity Analysis**
   - Total vs circulating supply
   - Locked supply identification
   - Liquidity ratios
   - Per-token metrics

5. **Ecosystem Health**
   - Overall holder statistics
   - Active account tracking (24h, 7d, 30d)
   - Element balance scoring
   - Transaction activity

6. **Comparative Analytics**
   - Cross-token comparisons
   - Rankings by holders/supply/concentration
   - Element distribution analysis

7. **Export & Reporting**
   - JSON export of all metrics
   - Timestamp tracking
   - Comprehensive summaries

### Technical Features

- ✅ **Fully Async**: All operations use async/await
- ✅ **Built-in Caching**: Configurable TTL (default 5 minutes)
- ✅ **Database-Only**: Single source of truth
- ✅ **Production-Ready**: Comprehensive error handling
- ✅ **Type-Safe**: Full type hints and dataclasses
- ✅ **Well-Documented**: Docstrings and examples

---

## Installation

### Prerequisites

```bash
# Python 3.10+
python3 --version

# Required packages
pip install asyncpg  # Database driver
```

### Directory Structure

```
services/
└── analytics/
    ├── __init__.py
    ├── ubec_analytics_service.py      # Main service
    └── README.md                       # This file

# Optional: examples and tests
examples/
└── ubec_analytics_examples.py        # Usage examples
```

### Setup

1. **Copy Module**
   ```bash
   mkdir -p services/analytics
   cp ubec_analytics_service.py services/analytics/
   ```

2. **Create __init__.py**
   ```python
   # services/analytics/__init__.py
   from .ubec_analytics_service import (
       UBECAnalyticsService,
       TokenDistribution,
       HolderAnalysis,
       TransactionMetrics,
       LiquidityMetrics,
       EcosystemHealth,
       TokenCode,
       ElementType,
       AnalyticsException
   )
   
   __all__ = [
       'UBECAnalyticsService',
       'TokenDistribution',
       'HolderAnalysis',
       'TransactionMetrics',
       'LiquidityMetrics',
       'EcosystemHealth',
       'TokenCode',
       'ElementType',
       'AnalyticsException'
   ]
   ```

3. **Verify Import**
   ```python
   from services.analytics import UBECAnalyticsService
   print("✓ Import successful")
   ```

---

## Quick Start

### Basic Usage

```python
import asyncio
from decimal import Decimal
from core.db.database_manager import AsyncDatabaseManager
from services.analytics import UBECAnalyticsService

async def main():
    # Initialize database
    db = AsyncDatabaseManager({
        'host': 'localhost',
        'database': 'ubec_main',
        'user': 'ubec_user',
        'password': 'your_password'
    })
    await db.initialize()
    
    # Initialize analytics
    analytics = UBECAnalyticsService(db)
    await analytics.initialize()
    
    # Get token distribution
    distribution = await analytics.get_token_distribution('UBEC')
    print(f"UBEC Holders: {distribution.total_holders}")
    print(f"Total Supply: {distribution.total_supply}")
    
    # Cleanup
    await analytics.close()
    await db.close()

asyncio.run(main())
```

---

## API Reference

### Core Methods

#### 1. Token Distribution Analysis

##### `get_token_distribution(token_code, use_cache=True)`

Analyze distribution for a specific token.

**Parameters:**
- `token_code` (str): Token to analyze ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
- `use_cache` (bool): Whether to use cached results

**Returns:** `TokenDistribution` object

**Example:**
```python
dist = await analytics.get_token_distribution('UBEC')

print(f"Token: {dist.token_code}")
print(f"Element: {dist.element}")
print(f"Holders: {dist.total_holders}")
print(f"Supply: {dist.total_supply}")
print(f"Top 10 concentration: {dist.top_10_concentration}%")
print(f"Gini coefficient: {dist.gini_coefficient}")
```

##### `get_all_token_distributions(use_cache=True)`

Get distribution for all 4 tokens.

**Returns:** List of `TokenDistribution` objects

**Example:**
```python
distributions = await analytics.get_all_token_distributions()

for dist in distributions:
    print(f"{dist.token_code}: {dist.total_holders} holders")
```

---

#### 2. Holder Concentration Analysis

##### `analyze_holder_concentration(token_code, whale_threshold, mid_tier_threshold, use_cache=True)`

Analyze holder concentration by tier.

**Parameters:**
- `token_code` (str): Token to analyze
- `whale_threshold` (Decimal): Minimum balance for whale (default: 10,000)
- `mid_tier_threshold` (Decimal): Minimum balance for mid-tier (default: 1,000)
- `use_cache` (bool): Whether to use cached results

**Returns:** `HolderAnalysis` object

**Example:**
```python
analysis = await analytics.analyze_holder_concentration(
    'UBEC',
    whale_threshold=Decimal('50000'),
    mid_tier_threshold=Decimal('5000')
)

print(f"Whales: {analysis.whale_count}")
print(f"Whale holdings: {analysis.whale_holdings}")
print(f"Whale percentage: {analysis.whale_percentage}%")
```

##### `identify_whales(token_code, threshold, limit=100)`

Identify whale accounts above threshold.

**Parameters:**
- `token_code` (str): Token to analyze
- `threshold` (Decimal): Minimum balance for whale
- `limit` (int): Maximum whales to return

**Returns:** List of whale account dictionaries

**Example:**
```python
whales = await analytics.identify_whales(
    'UBEC',
    threshold=Decimal('100000'),
    limit=20
)

for whale in whales:
    print(f"{whale['account_id']}: {whale['balance']} UBEC")
```

---

#### 3. Transaction Metrics

##### `get_transaction_metrics(token_code=None, period_days=30, use_cache=True)`

Analyze transaction patterns over time.

**Parameters:**
- `token_code` (str, optional): Specific token (None for all)
- `period_days` (int): Days to analyze (default: 30)
- `use_cache` (bool): Whether to use cached results

**Returns:** `TransactionMetrics` object

**Example:**
```python
metrics = await analytics.get_transaction_metrics('UBEC', period_days=7)

print(f"Total transactions: {metrics.total_transactions}")
print(f"Unique senders: {metrics.unique_senders}")
print(f"Velocity: {metrics.velocity} tx/day")
```

---

#### 4. Liquidity Analysis

##### `get_liquidity_metrics(token_code, use_cache=True)`

Analyze liquidity for a token.

**Parameters:**
- `token_code` (str): Token to analyze
- `use_cache` (bool): Whether to use cached results

**Returns:** `LiquidityMetrics` object

**Example:**
```python
liquidity = await analytics.get_liquidity_metrics('UBEC')

print(f"Total supply: {liquidity.total_supply}")
print(f"Circulating: {liquidity.circulating_supply}")
print(f"Liquidity ratio: {liquidity.liquidity_ratio}%")
```

---

#### 5. Ecosystem Health

##### `get_ecosystem_health(use_cache=True)`

Get overall ecosystem health metrics.

**Parameters:**
- `use_cache` (bool): Whether to use cached results

**Returns:** `EcosystemHealth` object

**Example:**
```python
health = await analytics.get_ecosystem_health()

print(f"Total holders: {health.total_holders}")
print(f"Active 24h: {health.active_accounts_24h}")
print(f"Element balance: {health.element_balance_score}/100")
```

---

#### 6. Comparative Analysis

##### `compare_tokens(use_cache=True)`

Compare all 4 UBEC tokens.

**Parameters:**
- `use_cache` (bool): Whether to use cached results

**Returns:** Dictionary with comparative analysis

**Example:**
```python
comparison = await analytics.compare_tokens()

# Access token data
for token, data in comparison['tokens'].items():
    print(f"{token}: {data['total_holders']} holders")

# Check rankings
print("Top token by holders:", comparison['rankings']['by_holders'][0])
```

---

#### 7. Export & Reporting

##### `export_analytics_summary()`

Export comprehensive analytics for all tokens.

**Returns:** Dictionary with all metrics

**Example:**
```python
import json

summary = await analytics.export_analytics_summary()

# Save to file
with open('ubec_analytics.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print(f"Exported at: {summary['generated_at']}")
```

---

### Data Structures

#### TokenDistribution

```python
@dataclass
class TokenDistribution:
    token_code: str                      # UBEC, UBECrc, etc
    element: str                         # air, water, earth, fire
    total_holders: int                   # Number of holders
    total_supply: Decimal                # Total token supply
    average_balance: Decimal             # Average holder balance
    median_balance: Decimal              # Median holder balance
    min_balance: Decimal                 # Smallest balance
    max_balance: Decimal                 # Largest balance (whale)
    top_10_concentration: Decimal        # % held by top 10
    top_100_concentration: Decimal       # % held by top 100
    gini_coefficient: Optional[Decimal]  # Inequality (0-1)
```

#### HolderAnalysis

```python
@dataclass
class HolderAnalysis:
    token_code: str              # Token analyzed
    total_holders: int           # Total holders
    whale_count: int             # Holders ≥ whale_threshold
    whale_holdings: Decimal      # Total whale holdings
    whale_percentage: Decimal    # % of supply whales hold
    mid_tier_count: int          # Mid-tier holders
    mid_tier_holdings: Decimal   # Total mid-tier holdings
    small_holder_count: int      # Small holders
    small_holder_holdings: Decimal  # Total small holdings
```

#### TransactionMetrics

```python
@dataclass
class TransactionMetrics:
    token_code: str                    # Token analyzed
    period_days: int                   # Analysis period
    total_transactions: int            # Total tx count
    unique_senders: int                # Unique sending accounts
    unique_receivers: int              # Unique receiving accounts
    total_volume: Decimal              # Total transaction volume
    average_transaction_size: Decimal  # Avg tx size
    median_transaction_size: Decimal   # Median tx size
    velocity: Decimal                  # Transactions per day
    turnover_ratio: Decimal            # Volume / Supply
```

#### LiquidityMetrics

```python
@dataclass
class LiquidityMetrics:
    token_code: str              # Token analyzed
    total_supply: Decimal        # Total token supply
    circulating_supply: Decimal  # Circulating supply
    locked_supply: Decimal       # Locked/vesting supply
    available_liquidity: Decimal # Available for trading
    liquidity_ratio: Decimal     # Available / Total %
```

#### EcosystemHealth

```python
@dataclass
class EcosystemHealth:
    timestamp: datetime              # Report timestamp
    total_holders: int               # Total unique holders
    total_accounts: int              # Total accounts
    total_transactions: int          # All-time transactions
    total_supply_all_tokens: Decimal # Sum of all 4 tokens
    active_accounts_24h: int         # Active last 24 hours
    active_accounts_7d: int          # Active last 7 days
    active_accounts_30d: int         # Active last 30 days
    element_balance_score: Decimal   # Balance score (0-100)
```

---

## Cache Management

### Understanding Cache

The analytics service includes intelligent caching to reduce database load:

- **Default TTL**: 5 minutes
- **Automatic expiration**: Stale data auto-removed
- **Per-method caching**: Each analysis cached separately
- **Cache keys**: Include all parameters

### Cache Methods

```python
# Clear all cached data
analytics.clear_cache()

# Bypass cache for fresh data
distribution = await analytics.get_token_distribution('UBEC', use_cache=False)

# Configure cache TTL (in seconds)
analytics._cache_ttl_seconds = 600  # 10 minutes
```

### When to Clear Cache

- After major sync operations
- Before generating reports
- When real-time data needed
- After configuration changes

---

## Performance Considerations

### Query Optimization

The service uses optimized SQL queries:
- Window functions for rankings
- CTEs for complex analysis
- Indexed columns for fast lookups
- Aggregations at database level

### Best Practices

1. **Use Caching**: Enable caching for repeated queries
   ```python
   # Good - uses cache
   for i in range(10):
       dist = await analytics.get_token_distribution('UBEC')
   ```

2. **Batch Operations**: Get all tokens at once
   ```python
   # Good - single query
   all_dists = await analytics.get_all_token_distributions()
   
   # Bad - four separate queries
   ubec = await analytics.get_token_distribution('UBEC')
   ubecrc = await analytics.get_token_distribution('UBECrc')
   # ...
   ```

3. **Export for Reports**: Use export for multiple metrics
   ```python
   # Good - comprehensive export
   summary = await analytics.export_analytics_summary()
   
   # Bad - many separate calls
   dist = await analytics.get_token_distribution('UBEC')
   holders = await analytics.analyze_holder_concentration('UBEC')
   # ...
   ```

---

## Common Use Cases

### Use Case 1: Daily Report Generation

```python
async def generate_daily_report():
    analytics = UBECAnalyticsService(db)
    await analytics.initialize()
    
    # Clear cache for fresh data
    analytics.clear_cache()
    
    # Get comprehensive summary
    summary = await analytics.export_analytics_summary()
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d')
    with open(f'daily_report_{timestamp}.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    await analytics.close()
```

### Use Case 2: Whale Monitoring

```python
async def monitor_whales():
    analytics = UBECAnalyticsService(db)
    await analytics.initialize()
    
    # Check all tokens for whales
    for token in ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']:
        whales = await analytics.identify_whales(
            token,
            threshold=Decimal('100000')
        )
        
        if whales:
            print(f"⚠️ {len(whales)} whales detected in {token}")
            # Send alert, update dashboard, etc.
    
    await analytics.close()
```

### Use Case 3: Health Dashboard

```python
async def update_dashboard():
    analytics = UBECAnalyticsService(db)
    await analytics.initialize()
    
    # Get key metrics
    health = await analytics.get_ecosystem_health()
    comparison = await analytics.compare_tokens()
    
    dashboard_data = {
        'health': {
            'holders': health.total_holders,
            'transactions': health.total_transactions,
            'active_24h': health.active_accounts_24h,
            'element_balance': float(health.element_balance_score)
        },
        'tokens': comparison['tokens'],
        'rankings': comparison['rankings']
    }
    
    # Update your dashboard with dashboard_data
    
    await analytics.close()
```

---

## Troubleshooting

### Issue 1: Import Error

**Problem:**
```python
ModuleNotFoundError: No module named 'services.analytics'
```

**Solution:**
```bash
# Verify file structure
ls -la services/analytics/

# Check __init__.py exists
cat services/analytics/__init__.py

# Verify PYTHONPATH
export PYTHONPATH=/path/to/project:$PYTHONPATH
```

### Issue 2: Database Connection Failed

**Problem:**
```
AnalyticsException: Failed to verify database connection
```

**Solution:**
```python
# Test database connectivity
async def test_connection():
    db = AsyncDatabaseManager(config)
    await db.initialize()
    result = await db.fetch_one("SELECT 1")
    print("✓ Database connected")
    await db.close()
```

### Issue 3: No Data Found

**Problem:**
```
AnalyticsException: No data found for token UBEC
```

**Solution:**
```sql
-- Verify data exists
SELECT token_code, COUNT(*) 
FROM ubec_balances 
WHERE balance > 0 
GROUP BY token_code;

-- If empty, run sync first
```

### Issue 4: Gini Coefficient is None

**Problem:** `distribution.gini_coefficient` returns None

**Cause:** Not enough data points or calculation error

**Solution:**
- Verify at least 10 holders exist
- Check for data quality issues
- Review logs for warnings

---

## Integration Examples

### With Monitoring Service

```python
from services.analytics import UBECAnalyticsService
from services.monitoring import UBECMonitoringService

async def integrated_monitoring():
    analytics = UBECAnalyticsService(db)
    monitoring = UBECMonitoringService(db, analytics)
    
    await analytics.initialize()
    await monitoring.initialize()
    
    # Use analytics in monitoring
    health = await analytics.get_ecosystem_health()
    
    if health.active_accounts_24h < 10:
        await monitoring.alert("Low activity detected")
    
    await analytics.close()
    await monitoring.close()
```

### With Trading Service

```python
from services.analytics import UBECAnalyticsService
from services.trading import UBECTradingService

async def informed_trading():
    analytics = UBECAnalyticsService(db)
    trading = UBECTradingService(db)
    
    await analytics.initialize()
    await trading.initialize()
    
    # Use analytics to inform trading decisions
    liquidity = await analytics.get_liquidity_metrics('UBEC')
    
    if liquidity.liquidity_ratio > 80:
        # High liquidity - safe to trade
        await trading.execute_trade(...)
    
    await analytics.close()
    await trading.close()
```

---

## Design Principles Compliance

| Principle | Status | Implementation |
|-----------|--------|----------------|
| 1. Modular Design | ✅ | Self-contained service |
| 2. Service Pattern | ✅ | No standalone execution |
| 3. Service Registry | ✅ | Used through registry |
| 4. Single Source of Truth | ✅ | Database only |
| 5. Strict Async | ✅ | All I/O async |
| 6. No Sync Fallbacks | ✅ | Pure async |
| 7. Per-Asset Monitoring | ✅ | Individual token tracking |
| 8. No Duplicate Configuration | ✅ | No duplication |
| 9. Integrated Rate Limiting | ✅ | N/A (read-only) |
| 10. Separation of Concerns | ✅ | Analytics only |
| 11. Comprehensive Documentation | ✅ | Full docs |
| 12. Method Singularity | ✅ | No redundancy |

---

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Support & Contribution

**Documentation**: This file  
**Examples**: `ubec_analytics_examples.py`  
**Issues**: Check logs for `[services.analytics]` entries

---

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: October 11, 2025
