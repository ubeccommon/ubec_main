# UBEC Main.py - Quick Reference Card

## 🚀 Most Common Commands

### Daily Operations

```bash
# 1. Check system health (recommended daily)
python main.py --mode health

# 2. Sync blockchain data
python main.py --mode sync

# 3. Get system status
python main.py --mode status

# 4. Discover new holders
python main.py --mode discover --max-accounts 500
```

---

## 📋 All Available Modes

### Data Operations
| Command | Description | Example |
|---------|-------------|---------|
| `discover` | Find new UBEC holders | `--mode discover --max-accounts 500` |
| `sync` | Sync blockchain to DB | `--mode sync --asset-code UBEC` |
| `monitor` | Continuous monitoring | `--mode monitor --interval 300` |

### Protocol Operations
| Command | Description | Example |
|---------|-------------|---------|
| `protocol-health` | Check protocol health | `--mode protocol-health` |
| `protocol-status` | Get protocol status | `--mode protocol-status` |
| `protocol-sync` | Sync all protocols | `--mode protocol-sync` |
| `evaluate` | Holonic evaluation | `--mode evaluate` |

### System Operations
| Command | Description | Example |
|---------|-------------|---------|
| `health` | Full system health | `--mode health` |
| `status` | Full system status | `--mode status` |

---

## ⚙️ Common Options

```bash
# Specify asset code
--asset-code UBEC

# Set max accounts for discovery
--max-accounts 1000

# Set monitoring interval (seconds)
--interval 300

# Evaluate specific account
--account GXXX...

# Set log level
--log-level DEBUG

# Set output format
--output json
```

---

## 💡 Common Workflows

### Morning Routine
```bash
# 1. Check health
python main.py --mode health

# 2. Sync data if healthy
python main.py --mode sync

# 3. Run evaluation
python main.py --mode evaluate
```

### New Deployment Setup
```bash
# 1. Discover initial holders
python main.py --mode discover --max-accounts 1000

# 2. Initial sync
python main.py --mode sync

# 3. Verify health
python main.py --mode health

# 4. Start monitoring
python main.py --mode monitor --interval 300
```

### Troubleshooting
```bash
# 1. Check health with verbose logging
python main.py --mode health --log-level DEBUG

# 2. Get detailed status
python main.py --mode status --output json

# 3. Check protocol health specifically
python main.py --mode protocol-health
```

### Production Monitoring
```bash
# Run continuous monitor (recommended)
python main.py --mode monitor --interval 300

# This will check every 5 minutes:
# - Database health
# - Stellar connection
# - System resources
```

---

## 🔧 Configuration Quick Check

```bash
# View current configuration
cat .env | grep UBEC

# Test database connection
python main.py --mode health | grep database

# Test Stellar connection
python main.py --mode health | grep stellar
```

---

## 📊 Output Examples

### Health Check
```
Overall Status: healthy
Infrastructure:
  Database: ✓ Healthy
  Stellar: ✓ Connected
Protocols:
  Air: ✓ healthy
  Water: ✓ healthy
  Earth: ✓ healthy
  Fire: ✓ healthy
```

### Sync Result
```
Asset: UBEC
Accounts synced: 1247
Balances synced: 1247
Transactions synced: 3456
Duration: 45.2s
```

### Discovery Result
```
New accounts discovered: 47
Total accounts: 1294
Time taken: 23.1s
```

---

## 🚨 Quick Troubleshooting

| Problem | Check | Solution |
|---------|-------|----------|
| Connection error | `.env` file | Verify credentials |
| No data synced | Issuer address | Check token issuer |
| Slow performance | Rate limit | Adjust `UBEC_RATE_LIMIT` |
| Protocol unavailable | Protocol files | Ensure protocols initialized |

---

## 📝 Exit Codes

```bash
0   = Success
1   = Error/Failure
130 = User interrupted (Ctrl+C)
```

```bash
# Check exit code
python main.py --mode health
echo $?
```

---

## 🎯 Production Deployment

### 1. Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Test configuration
python main.py --mode health
```

### 2. First Run
```bash
# Discover all holders
python main.py --mode discover --max-accounts 5000

# Initial sync
python main.py --mode sync

# Verify
python main.py --mode status
```

### 3. Ongoing Operations
```bash
# Start monitor (in screen/tmux)
screen -S ubec-monitor
python main.py --mode monitor --interval 300

# Detach: Ctrl+A, then D
# Reattach: screen -r ubec-monitor
```

### 4. Daily Maintenance
```bash
# Morning: Check health
python main.py --mode health

# Sync new data
python main.py --mode sync

# Evening: Run evaluation
python main.py --mode evaluate
```

---

## 🔗 Quick Links

- **Full Documentation**: `MAIN_PY_UPDATE_GUIDE.md`
- **Design Principles**: Project README
- **Service Registry**: `core/service_registry.py`
- **Configuration**: `.env` file

---

## 🙏 Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

**Version**: 3.2  
**Date**: October 11, 2025  
**Status**: ✅ Production Ready
