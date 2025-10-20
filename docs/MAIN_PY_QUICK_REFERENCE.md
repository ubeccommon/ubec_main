# UBEC Protocol main.py - Quick Reference Card

**Version:** 13.0.0  
**Status:** Production Ready ✅  
**Design Principles:** 12/12 Perfect Compliance ✅

---

## 🚀 Quick Start

```bash
# Health check (always run first!)
python main.py --mode health

# System status
python main.py --mode status

# Get help
python main.py --help
```

---

## 📋 Common Operations

### System Operations

```bash
# Full health check
python main.py --mode health

# System status with statistics
python main.py --mode status
```

### Data Operations

```bash
# Discover token holders (limit 100)
python main.py --mode discover --max-accounts 100

# Sync all data
python main.py --mode sync --sync-type all

# Sync only balances for UBEC
python main.py --mode sync --sync-type balances --asset-code UBEC

# Run analytics summary
python main.py --mode analytics --analysis-type summary

# Distribution analysis
python main.py --mode analytics --analysis-type distribution
```

### Protocol Operations

```bash
# Check protocol health
python main.py --mode protocol-health

# Get protocol status
python main.py --mode protocol-status

# Evaluate specific account
python main.py --mode evaluate --account GXXXXXXXXXXX
```

### Visualization Operations

```bash
# Generate single chart
python main.py --mode visualize --action chart --chart-type radar

# Generate comprehensive HTML report
python main.py --mode visualize --action report --format html

# Generate HTML report with advanced analytics
python main.py --mode visualize --action report --format html --include-advanced

# Generate all visualizations
python main.py --mode visualize --action all --output-dir ./viz

# Available chart types:
#   radar, score_distribution, category_distribution,
#   time_series, correlation, comparative, network
```

### Distribution Operations

```bash
# Check distribution compliance
python main.py --mode distribution --action check-compliance

# Run comprehensive audit
python main.py --mode distribution --action audit

# Dry run (simulate only)
python main.py --mode distribution --action audit --dry-run
```

---

## 🔧 Command Line Options

### Core Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--mode` | See modes below | Required | Operation mode |
| `--log-level` | DEBUG, INFO, WARNING, ERROR | INFO | Logging level |
| `--output-format` | json, pretty | pretty | Output format |

### Mode Values

**System:** `health`, `status`  
**Data:** `discover`, `sync`, `analytics`  
**Protocol:** `protocol-health`, `protocol-status`, `evaluate`  
**Other:** `visualize`, `distribution`

### Data Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--max-accounts` | Integer | 100 | Max accounts to discover |
| `--sync-type` | all, accounts, balances, transactions | all | Sync type |
| `--asset-code` | UBEC, UBECrc, UBECgpi, UBECtt | UBEC | Asset code |
| `--analysis-type` | summary, distribution, holders | summary | Analysis type |

### Protocol Options

| Option | Description |
|--------|-------------|
| `--account` | Stellar account ID for evaluation |

### Visualization Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--action` | chart, report, all | - | Visualization action |
| `--chart-type` | See chart types | - | Chart to generate |
| `--format` | png, svg, html, json | png | Output format |
| `--output-dir` | Path | visualizations | Output directory |
| `--include-advanced` | Flag | False | Include advanced analytics |

### Distribution Options

| Option | Values | Description |
|--------|--------|-------------|
| `--action` | check-compliance, audit | Action to perform |
| `--dry-run` | Flag | Simulate without changes |

---

## 🔍 Troubleshooting

### Check Logs

```bash
# View main log
tail -f logs/ubec_main.log

# View with debug level
python main.py --mode health --log-level DEBUG

# View specific service logs
tail -f logs/ubec_synchronizer.log
tail -f logs/ubec_visualizer.log
```

### Common Issues

#### Services Not Starting

```bash
# Check service registration
python main.py --mode health --log-level DEBUG

# Verify database connection
# (Check logs for connection errors)
```

#### Data Not Loading

```bash
# Check database
python main.py --mode status

# Run sync
python main.py --mode sync --sync-type all

# Verify data exists
# (Check status for account/balance counts)
```

#### Visualizations Incomplete

```bash
# Ensure data is loaded
python main.py --mode status

# Run discovery if needed
python main.py --mode discover --max-accounts 200

# Regenerate visualizations
python main.py --mode visualize --action all
```

---

## 📊 Output Formats

### JSON Output

```bash
python main.py --mode health --output-format json
```

Output:
```json
{
  "success": true,
  "timestamp": "2025-10-19T10:30:00",
  "data": {
    "overall_status": "healthy",
    "services": {...}
  }
}
```

### Pretty Output (Default)

```bash
python main.py --mode health
```

Output:
```
======================================================================
UBEC Protocol - HEALTH Result
======================================================================
{
  "success": true,
  "timestamp": "2025-10-19T10:30:00",
  "data": {
    "overall_status": "healthy",
    ...
  }
}
======================================================================
```

---

## 🎯 Design Principles Quick Reference

### The 12 Principles (All Implemented ✅)

1. **Modular Design** - Clear module boundaries
2. **Service Pattern** - main.py is sole orchestrator
3. **Service Registry** - Centralized dependency management
4. **Single Source of Truth** - Database for data, registry for services
5. **Strict Async** - ALL I/O uses async/await
6. **No Sync Fallbacks** - Pure async implementation
7. **Per-Asset Monitoring** - Individual tracking supported
8. **No Duplicate Config** - Single configuration source
9. **Integrated Rate Limiting** - Built into services
10. **Separation of Concerns** - Data/Protocol/System layers
11. **Comprehensive Docs** - Full docstrings throughout
12. **Method Singularity** - Zero code duplication

### When Writing Code

✅ **DO:**
- Use async/await for ALL I/O
- Get services from registry
- Document with docstrings
- Handle errors comprehensively
- Log important operations
- Return standardized responses

❌ **DON'T:**
- Use synchronous I/O
- Import services directly
- Duplicate code
- Hard-code configuration
- Skip error handling
- Mix concerns

---

## 🏗️ Architecture Reminder

```
main.py (SOLE ENTRY POINT)
    ↓
Service Registry (CENTRAL HUB)
    ↓
┌──────────────┬────────────────┬──────────────┐
│ Data Layer   │ Protocol Layer │ System Layer │
├──────────────┼────────────────┼──────────────┤
│ • discover   │ • evaluate     │ • health     │
│ • sync       │ • protocols    │ • status     │
│ • analytics  │                │              │
└──────────────┴────────────────┴──────────────┘
```

---

## 💡 Pro Tips

### Performance

```bash
# Use JSON output for scripts
python main.py --mode status --output-format json | jq '.data'

# Limit discovery for testing
python main.py --mode discover --max-accounts 10

# Use dry-run for audits
python main.py --mode distribution --action audit --dry-run
```

### Automation

```bash
# Cron job example (hourly sync)
0 * * * * cd /path/to/ubec && python main.py --mode sync --sync-type all >> /var/log/ubec_sync.log 2>&1

# Health check every 30 minutes
*/30 * * * * cd /path/to/ubec && python main.py --mode health >> /var/log/ubec_health.log 2>&1
```

### Debugging

```bash
# Enable debug logging
python main.py --mode health --log-level DEBUG

# Check specific service
# (Review logs for service-specific issues)

# Verify all services registered
python main.py --mode status --log-level DEBUG | grep "Registered"
```

---

## 📞 Quick Help

### Get Full Help

```bash
python main.py --help
```

### Check Version

```bash
python main.py --mode health | grep -i version
# Version: 13.0.0
```

### Verify Installation

```bash
# Quick verification
python main.py --mode health && \
python main.py --mode status && \
echo "✓ Installation verified"
```

---

## 🎉 Success Indicators

### Healthy System

```bash
# Run health check
python main.py --mode health

# Should show:
# ✓ overall_status: "healthy"
# ✓ All services: "healthy"
# ✓ No errors in output
```

### Data Synced

```bash
# Check status
python main.py --mode status

# Should show:
# ✓ accounts > 0
# ✓ balances > 0
# ✓ last_sync: recent timestamp
```

### Visualizations Working

```bash
# Generate report
python main.py --mode visualize --action report --format html

# Should create:
# ✓ visualizations/holonic_report_YYYYMMDD_HHMMSS.html
# ✓ File size > 100KB
# ✓ All charts embedded
```

---

## 📚 Related Documentation

- **Full Guide:** `MAIN_PY_MODERNIZATION_GUIDE.md`
- **Design Principles:** Project root (12 principles document)
- **Service Registry:** `docs/README_SERVICE_REGISTRY.md`
- **Migration:** `docs/MIGRATION_TO_UNIFIED.md`

---

## 📝 Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

**Version:** 13.0.0  
**Date:** October 19, 2025  
**Status:** Production Ready ✅  
**Need Help?** Check logs first, then review full documentation!
