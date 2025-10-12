# UBEC Analytics - Quick Reference Card

## 📊 Analytics Commands

### Summary Analytics (Ecosystem Overview)
```bash
python main.py --mode analytics --analysis-type summary
```
**Returns:** Health metrics, token summaries, rankings

### Distribution Analytics (Per-Token Details)
```bash
python main.py --mode analytics --analysis-type distribution
```
**Returns:** Holder counts, balances, concentration metrics

### Holder Analytics (Whale Analysis)
```bash
python main.py --mode analytics --analysis-type holders
```
**Returns:** Whale identification, tier analysis

---

## 🔄 Output Formats

### Pretty Print (default)
```bash
python main.py --mode analytics --analysis-type summary
```

### JSON (for scripting)
```bash
python main.py --mode analytics --analysis-type summary --output json
```

### Summary (minimal)
```bash
python main.py --mode analytics --analysis-type summary --output summary
```

---

## 📈 Key Metrics Guide

### Gini Coefficient
- **0.0-0.3:** Very equal ✅
- **0.3-0.5:** Moderate ✅
- **0.5-0.7:** High inequality ⚠️
- **0.7-1.0:** Extreme inequality ❌

### Top 10 Concentration
- **< 20%:** Excellent ✅
- **20-40%:** Good ✅
- **40-60%:** Moderate ⚠️
- **> 60%:** High risk ❌

### Element Balance Score
- **90-100:** Excellent ✅
- **70-90:** Good ✅
- **50-70:** Moderate ⚠️
- **< 50:** Poor ❌

---

## 🚀 One-Liner Examples

```bash
# Total holders across all tokens
python main.py --mode analytics --analysis-type summary --output json | \
  jq '.ecosystem_health.total_holders'

# Whale count per token
python main.py --mode analytics --analysis-type holders --output json | \
  jq '.tokens[].whales.count'

# Top concentrated token
python main.py --mode analytics --analysis-type distribution --output json | \
  jq '.tokens | sort_by(.concentration.top_10) | reverse | .[0] | {token: .token_code, concentration: .concentration.top_10}'

# Active accounts last 24h
python main.py --mode analytics --analysis-type summary --output json | \
  jq '.ecosystem_health.active_accounts_24h'
```

---

## 🔧 Troubleshooting Quick Fixes

### "Analytics service not available"
```bash
ls services/analytics/ubec_analytics_service.py
# If missing, get the file from project repository
```

### "No data returned"
```bash
python main.py --mode sync
# Wait for sync, then retry analytics
```

### Shutdown errors
```bash
# Use the fixed main.py:
cp main_with_analytics.py main.py
```

---

## 📋 Pre-Flight Checklist

Before running analytics:
- [ ] Analytics service file in place
- [ ] Database connection working
- [ ] Data synced (run --mode sync if needed)
- [ ] Using updated main.py

---

## 💾 Export Scripts

### Daily Report
```bash
python main.py --mode analytics --analysis-type summary \
  --output json > daily_$(date +%Y%m%d).json
```

### Weekly Comparison
```bash
python main.py --mode analytics --analysis-type holders \
  --output json > weekly_$(date +%Y%m%d).json
```

### Full Export
```bash
mkdir -p reports/$(date +%Y%m%d)
for type in summary distribution holders; do
  python main.py --mode analytics --analysis-type $type \
    --output json > reports/$(date +%Y%m%d)/${type}.json
done
```

---

## 🎯 Common Use Cases

### Morning Dashboard
```bash
python main.py --mode analytics --analysis-type summary | \
  jq '{
    holders: .ecosystem_health.total_holders,
    active_24h: .ecosystem_health.active_accounts_24h,
    balance_score: .ecosystem_health.element_balance_score
  }'
```

### Whale Watch
```bash
python main.py --mode analytics --analysis-type holders | \
  jq '.tokens[] | select(.whales.percentage > 40) | {
    token: .token_code,
    whale_pct: .whales.percentage,
    whale_count: .whales.count
  }'
```

### Distribution Health
```bash
python main.py --mode analytics --analysis-type distribution | \
  jq '.tokens[] | {
    token: .token_code,
    gini: .concentration.gini,
    top10: .concentration.top_10
  }'
```

---

**Keep this card handy for quick analytics access!**

**Attribution:** This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations.
