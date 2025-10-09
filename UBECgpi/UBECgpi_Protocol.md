# 🜃 Earth Token (UBECgpi Stability) Protocol
## Ubuntu Bioregional Economic Commons

**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** October 2025  
**Element:** Earth (🜃) - Stability, Grounding, Value Storage

---

## Executive Summary

The **UBECgpi Stability Token (Earth)** is the first prosperity-pegged stablecoin, maintaining value against the Genuine Progress Indicator (GPI) rather than fiat currency. Representing the grounding element of Earth, UBECgpi provides stable purchasing power that actually reflects true economic well-being and prosperity.

**Core Innovation:** Stability pegged to prosperity, not inflation

**Functions:**
- Store of value (GPI-pegged)
- Stable medium of exchange
- Inflation-resistant savings
- Purchasing power preservation

---

## Protocol Specification

### Token Details

| Parameter | Value |
|-----------|-------|
| **Token Code** | `UBECgpi` |
| **Element** | Earth (🜃) |
| **Peg** | GPI (Genuine Progress Indicator) |
| **Collateral Ratio** | 150% minimum |
| **Supply** | Algorithmic (mint/burn) |
| **Oracle Update** | Daily GPI adjustment |

### GPI Pegging Mechanism

**Target:** 1 UBECgpi = 1 GPI Unit

**GPI Basket Components:**
- Economic wellbeing (30%)
- Environmental health (25%)
- Social capital (20%)
- Education & knowledge (15%)
- Infrastructure quality (10%)

**Oracle Sources:**
- Regional GPI calculators
- Environmental sensors
- Community health metrics
- Education indices
- Infrastructure assessments

---

## Economic Architecture

### Collateralization

**Reserve Composition:**
```
Multi-Asset Reserve:
- UBEC tokens: 40%
- Fiat (EUR/USD): 30%
- Precious metals: 15%
- Real assets: 10%
- Crypto (BTC/ETH): 5%
```

**Minimum Collateral Ratio:** 150%
```
For every 100 UBECgpi:
Minimum reserve value: 150 EUR equivalent
```

### Minting & Burning

**Mint Process:**
1. User deposits collateral (150%+ value)
2. Smart contract locks collateral
3. UBECgpi tokens minted
4. Tokens transferred to user

**Burn Process:**
1. User returns UBECgpi
2. Tokens burned
3. Collateral released (minus fees)
4. User receives reserve assets

**Fees:**
- Minting: 0.5%
- Burning: 0.3%
- Both go to reserve strengthening

---

## Stability Mechanisms

### Algorithmic Adjustment

**Daily GPI Tracking:**
```python
def calculate_adjustment():
    current_gpi = get_oracle_gpi()
    target_peg = 1.0
    deviation = (current_gpi - target_peg) / target_peg
    
    if deviation > 0.02:  # >2% deviation
        action = "burn"  # GPI too high, reduce supply
        amount = circulating_supply * 0.01
    elif deviation < -0.02:  # <-2% deviation
        action = "mint"  # GPI too low, increase supply
        amount = circulating_supply * 0.01
    else:
        action = "maintain"
```

### Collateral Management

**Dynamic Ratio:**
- Healthy system: 150% ratio
- Under stress: Increase to 175%
- Crisis mode: 200% ratio

**Reserve Rebalancing:**
- Weekly automatic rebalancing
- Maintain target asset mix
- Risk-adjusted based on volatility

### Arbitrage Opportunities

**Price Discovery:**
- Decentralized exchanges
- Liquidity pools
- Arbitrage bots incentivized
- Market-driven stability

---

## Use Cases

### Personal Savings
**Scenario:** Protect savings from inflation  
**Flow:**
1. Convert EUR to UBEC
2. Mint UBECgpi with UBEC collateral
3. Hold as GPI tracks real prosperity
4. Maintain purchasing power over time

**vs Traditional Savings:**
```
Traditional (EUR):
Year 0: €10,000 → Buys X goods
Year 5: €10,000 → Buys 0.85X goods (-15% inflation)

UBECgpi:
Year 0: 10,000 UBECgpi → Buys X goods
Year 5: 10,000 UBECgpi → Buys X goods (maintained)
```

### Business Operations
**Scenario:** Stable pricing for local economy  
**Flow:**
1. Price goods in UBECgpi
2. Maintain consistent real value
3. Customers experience stable prices
4. Business planning simplified

### Cross-Border Value Transfer
**Scenario:** Send value across regions  
**Flow:**
1. Convert local currency to UBECgpi
2. Transfer internationally (low cost)
3. Recipient redeems to local currency
4. Value preserved against real prosperity

---

## Risk Management

### Oracle Risk
**Mitigation:**
- Multiple independent oracles
- Weighted averaging
- Outlier rejection
- Manual override (DAO governance)

### Collateral Risk
**Mitigation:**
- Diversified reserve
- Conservative ratios
- Automated liquidation
- Insurance fund

### Market Risk
**Mitigation:**
- Deep liquidity pools
- Circuit breakers
- Emergency DAO controls
- Gradual adjustments

---

## Governance Parameters

**Adjustable via DAO:**

| Parameter | Current | Range | Vote Required |
|-----------|---------|-------|---------------|
| Collateral Ratio | 150% | 120%-200% | Supermajority |
| Minting Fee | 0.5% | 0.1%-2% | Simple majority |
| Burning Fee | 0.3% | 0%-1% | Simple majority |
| GPI Deviation Threshold | 2% | 1%-5% | Simple majority |
| Oracle Update Frequency | Daily | Hourly-Weekly | Simple majority |
| Reserve Composition | See above | DAO decides | Supermajority |

---

## Integration Guidelines

### Minting UBECgpi

```python
from ubec_sdk import EarthTokenProtocol

earth = EarthTokenProtocol(account_secret)

# Mint with UBEC collateral
mint_result = earth.mint_ubecgpi(
    collateral_asset="UBEC",
    collateral_amount=150,  # 150 UBEC
    ubecgpi_amount=100,     # Mint 100 UBECgpi
)
```

### Burning UBECgpi

```python
burn_result = earth.burn_ubecgpi(
    ubecgpi_amount=100,
    receive_asset="UBEC",  # Get UBEC back
)
```

### Checking Collateral Health

```python
health = earth.check_collateral_health(account)
# Returns: {
#   "collateral_ratio": 165%,
#   "health_status": "healthy",
#   "liquidation_threshold": 140%
# }
```

---

## Performance Metrics

**Target KPIs:**
```
Peg Stability: ±2% of GPI
Collateral Ratio: >150% always
Liquidity Depth: €1M+ per major pair
Daily Volume: €100K+
User Adoption: 5,000+ holders Year 1
```

---

## Roadmap

### Phase 1: Launch (Q4 2025) ✅
- Basic minting/burning
- Single oracle
- Conservative collateral ratio
- Limited pairs

### Phase 2: Enhancement (Q1-Q2 2026)
- Multiple oracles
- Expanded collateral types
- Automated rebalancing
- Advanced liquidity

### Phase 3: Maturity (Q3-Q4 2026)
- Decentralized oracles
- AI-assisted management
- Cross-chain bridges
- Institutional adoption

---

**Document Control:**
- Version: 1.0.0
- Classification: Public
- Maintained by: UBEC Technical Team

---

*"Like Earth beneath our feet, providing stable ground for all life to flourish."* 🜃

**"I am because we are" - Ubuntu** 🌍
