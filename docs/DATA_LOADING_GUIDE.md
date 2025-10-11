# UBEC Protocol - Data Loading Guide 📊

## Overview

Your database tables are ready, now it's time to fill them with live data from the Stellar blockchain! This guide shows you how to populate all four elements with real transaction data.

---

## 🚀 Quick Start (60 seconds)

### Step 1: Copy the Data Loading Script

```bash
cd ~/UBEC/projects/UBEC
cp /mnt/user-data/outputs/load_data.py .
```

### Step 2: Run Your First Data Load

```bash
# Quick load (recent data, ~2-5 minutes)
python load_data.py --mode quick

# OR Full load (30 days history, ~10-20 minutes)
python load_data.py --mode full
```

### Step 3: Verify Data Loaded

```bash
python ubec_main_protocol.py --action sync
```

You should now see actual numbers instead of zeros! 🎉

---

## 📋 Loading Modes Explained

### 1. **Quick Mode** (Recommended for testing)
```bash
python load_data.py --mode quick
```
- Loads last 7 days of transactions
- Limits to 200 accounts per token
- Fastest option (~2-5 minutes)
- **Use for**: Testing, development, quick updates

### 2. **Full Mode** (Recommended for production)
```bash
python load_data.py --mode full
```
- Loads last 30 days of transactions
- Loads up to 1000 accounts per token
- More comprehensive (~10-20 minutes)
- **Use for**: Initial setup, complete data sync

### 3. **Element-Specific Loading**

Load data for just one element:

```bash
# Air (UBEC) - Gateway accounts
python load_data.py --mode air --limit 500

# Water (UBECrc) - Transaction flows
python load_data.py --mode water --days 14

# Earth (UBECgpi) - Stability data
python load_data.py --mode earth

# Fire (UBECtt) - Transformation data
python load_data.py --mode fire
```

### 4. **Monitor Mode** (Continuous syncing)
```bash
# Sync every 5 minutes (300 seconds)
python load_data.py --mode monitor --interval 300

# Sync every hour
python load_data.py --mode monitor --interval 3600
```

---

## 🔄 What Gets Loaded

### 🌬️ **Air Element (UBEC)** - Gateway Data

**Source**: Stellar network account discovery  
**Destination**: `gateway_accounts` table

**What's loaded:**
- All accounts holding UBEC tokens
- Current balances
- Trustline status
- Last activity timestamps
- Transaction counts

**Command:**
```bash
python load_data.py --mode air
```

### 💧 **Water Element (UBECrc)** - Flow Data

**Source**: Stellar transaction history  
**Destination**: `flow_transactions` table

**What's loaded:**
- Payment transactions
- From/to account pairs
- Transaction amounts
- Transaction timestamps
- Memo data

**Command:**
```bash
python load_data.py --mode water --days 30
```

### 🌍 **Earth Element (UBECgpi)** - Stability Data

**Source**: Balance analysis & transaction patterns  
**Destination**: `distribution_state`, `account_balances`, `mutualism_relationships` tables

**What's loaded:**
- Account balances for distribution analysis
- Distribution compliance (75/20/5)
- Total supply calculations
- Mutualism relationships (accounts that transact with each other)
- Holder counts and median balances

**Command:**
```bash
python load_data.py --mode earth
```

### 🔥 **Fire Element (UBECtt)** - Transformation Data

**Source**: Stellar account sync  
**Destination**: Primarily `transformation_phases` (event-driven)

**What's loaded:**
- Account holders of UBECtt
- Baseline for transformation tracking

**Note:** Fire element is event-driven, most data comes from protocol actions

**Command:**
```bash
python load_data.py --mode fire
```

---

## 📊 Expected Results

### Before Loading Data
```
✅ Air synced successfully - 0 accounts
✅ Water synced successfully - 0 transactions
✅ Earth synced successfully - 0 relationships
✅ Fire synced successfully - 0 actions
```

### After Loading Data
```
✅ Air synced successfully - 150 accounts
  - Total accounts: 150
  - Active accounts: 48
  - Total balance: 50,000.5 UBEC
  - Diversity index: 0.85

✅ Water synced successfully - 234 transactions
  - 24h volume: 15,430.2 UBECrc
  - 24h transactions: 45
  - Circulation velocity: 0.72

✅ Earth synced successfully - 23 relationships
  - Holder count: 87
  - Distribution compliance: COMPLIANT
  - Stability index: 0.89

✅ Fire synced successfully - 12 actions
  - Transformation phases: 2 active
  - UBECtt distributed: 450.0
```

---

## 🔧 Advanced Options

### Custom Account Limits
```bash
# Load only 100 most active accounts
python load_data.py --mode air --limit 100

# Load 2000 accounts
python load_data.py --mode full --limit 2000
```

### Custom Time Ranges
```bash
# Load last 90 days of transactions
python load_data.py --mode water --days 90

# Load just today's transactions
python load_data.py --mode water --days 1
```

### Continuous Monitoring
```bash
# Check for new data every 5 minutes
python load_data.py --mode monitor --interval 300

# Quick sync every hour
python load_data.py --mode monitor --interval 3600
```

---

## 🤖 Automated Syncing (Production Setup)

### Option 1: Systemd Service (Linux)

Create `/etc/systemd/system/ubec-sync.service`:

```ini
[Unit]
Description=UBEC Protocol Data Sync
After=network.target postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/home/your_user/UBEC/projects/UBEC
Environment="PATH=/home/your_user/.local/bin:/usr/local/bin:/usr/bin"
ExecStart=/usr/bin/python3 load_data.py --mode monitor --interval 300
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ubec-sync.service
sudo systemctl start ubec-sync.service
sudo systemctl status ubec-sync.service
```

### Option 2: Cron Job

Edit crontab:
```bash
crontab -e
```

Add line to sync every 5 minutes:
```
*/5 * * * * cd /home/your_user/UBEC/projects/UBEC && python load_data.py --mode quick >> /var/log/ubec-sync.log 2>&1
```

Or hourly:
```
0 * * * * cd /home/your_user/UBEC/projects/UBEC && python load_data.py --mode quick >> /var/log/ubec-sync.log 2>&1
```

### Option 3: Screen/tmux Session

```bash
# Start persistent session
screen -S ubec-monitor

# Inside screen, run monitor
cd ~/UBEC/projects/UBEC
python load_data.py --mode monitor --interval 300

# Detach: Ctrl+A, then D
# Reattach: screen -r ubec-monitor
```

---

## 🔍 Verifying Data

### 1. Check Sync Results
```bash
python ubec_main_protocol.py --action sync
```

### 2. Query Database Directly
```bash
# Count accounts by element
psql -U ubec_app -d ubec -c "SELECT asset_code, COUNT(*) FROM ubec_main.gateway_accounts GROUP BY asset_code;"

# Check transaction volume
psql -U ubec_app -d ubec -c "SELECT asset_code, COUNT(*) as tx_count, SUM(amount) as total_volume FROM ubec_main.flow_transactions GROUP BY asset_code;"

# Check distribution compliance
psql -U ubec_app -d ubec -c "SELECT * FROM ubec_main.distribution_state WHERE asset_code = 'UBECgpi';"

# View mutualism relationships
psql -U ubec_app -d ubec -c "SELECT COUNT(*) as relationships FROM ubec_main.mutualism_relationships WHERE relationship_strength > 0.5;"
```

### 3. Check Table Sizes
```bash
psql -U ubec_app -d ubec -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup as rows
FROM pg_stat_user_tables
WHERE schemaname = 'ubec_main'
    AND tablename IN ('gateway_accounts', 'flow_transactions', 'account_balances', 'mutualism_relationships')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

---

## 🐛 Troubleshooting

### "No accounts found" / "No transactions found"

**Possible causes:**
1. Your tokens don't have any holders yet on Stellar mainnet
2. Issuer address is incorrect
3. Network connectivity issues

**Solutions:**
```bash
# Check your token issuers
grep "UBEC_ISSUER" .env

# Test Stellar connection
python -c "from stellar_sdk import Server; s = Server('https://horizon.stellar.org'); print(s.accounts().limit(1).call())"

# Check if your tokens exist on Stellar
# Visit: https://stellar.expert/explorer/public/asset/UBEC-YOUR_ISSUER_ADDRESS
```

### "Rate limited by Stellar Horizon"

**Solution:** Add delays between batches (already handled in synchronizer)

```bash
# Use smaller limits and longer sync periods
python load_data.py --mode air --limit 100
```

### "Database connection failed"

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check .env file has correct credentials
cat .env | grep UBEC_DB

# Test connection
psql -U ubec_app -d ubec -c "SELECT 1"
```

### "ModuleNotFoundError: No module named 'stellar_sdk'"

**Solution:**
```bash
pip install stellar-sdk
```

---

## 📈 Performance Tips

### For Faster Initial Loads
1. **Start with quick mode** to test everything works
2. **Load elements in parallel** (open multiple terminals)
3. **Use smaller time windows** first, expand later
4. **Monitor database performance** during large loads

### For Production
1. **Use monitor mode** with 5-10 minute intervals
2. **Set up database indexes** (already done in migration)
3. **Monitor disk space** - logs and data grow over time
4. **Regular database maintenance**:
   ```bash
   psql -U ubec_app -d ubec -c "VACUUM ANALYZE;"
   ```

---

## 🎯 Next Steps After Loading Data

### 1. Analyze Your Protocol
```bash
# Check compliance metrics
python ubec_main_protocol.py --action sync

# Generate reports (if available)
python ubec_main_protocol.py --action report
```

### 2. Monitor Health
Set up monitoring to track:
- Distribution compliance (75/20/5)
- Transaction velocity
- Account growth
- Relationship strength

### 3. Optimize Syncing
Based on your usage:
- High activity → sync every 5 minutes
- Medium activity → sync every 30 minutes  
- Low activity → sync every few hours

---

## 📚 Additional Resources

- **Stellar Horizon API**: https://developers.stellar.org/api
- **stellar-sdk Documentation**: https://stellar-sdk.readthedocs.io/
- **UBEC Project Docs**: Check `/docs` folder in your project

---

## ✅ Checklist

- [ ] Copied `load_data.py` to project root
- [ ] Ran initial data load (`--mode quick` or `--mode full`)
- [ ] Verified data in sync results (non-zero metrics)
- [ ] Set up automated syncing (cron/systemd/monitor mode)
- [ ] Tested element-specific syncing
- [ ] Configured monitoring interval for your needs
- [ ] Documented your token issuers in `.env`

---

**Attribution**: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

**Ready to load data?** Start with: `python load_data.py --mode quick`
