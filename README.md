# UBEC Protocol Suite

**"You never change things by fighting the existing reality. To change something, build a new model that makes the existing model obsolete."** - R. Buckminster Fuller

**"I am because we are"** - Ubuntu 🌍

---

## Overview

The Ubuntu Basic Economic Commons (UBEC) Protocol Suite implements a holonic economic ecosystem built on four elemental tokens, each representing fundamental principles of sustainable economics:

- 🜁 **UBEC (Air)** - Gateway & Universal Access
- 🜄 **UBECrc (Water)** - Reciprocity & Flow
- 🜃 **UBECgpi (Earth)** - Stability & Value
- 🜂 **UBECtt (Fire)** - Transformation & Change

## Project Structure

```
UBEC_project_root/
├── config/                         # Global Configuration
│   ├── __init__.py
│   ├── config.py                   # GlobalConfig class
│   └── logging.py                  # Centralized logging
│
├── ubec_main_protocol.py          # Main Protocol Orchestrator
│
├── UBEC/                           # 🜁 Air Token Module
│   ├── __init__.py
│   ├── UBEC_protocol.py            # Protocol implementation
│   ├── UBEC_Protocol.md            # Documentation
│   └── config/
│       ├── __init__.py
│       ├── config.py                # UBEC-specific config
│       └── logging.py               # UBEC logging
│
├── UBECrc/                         # 🜄 Water Token Module
│   ├── __init__.py
│   ├── UBECrc_protocol.py          # Protocol implementation
│   ├── UBECrc_Protocol.md          # Documentation
│   └── config/
│       ├── __init__.py
│       ├── config.py                # UBECrc-specific config
│       └── logging.py               # UBECrc logging
│
├── UBECgpi/                        # 🜃 Earth Token Module
│   ├── __init__.py
│   ├── UBECgpi_protocol.py         # Protocol implementation
│   ├── UBECgpi_Protocol.md         # Documentation
│   └── config/
│       ├── __init__.py
│       ├── config.py                # UBECgpi-specific config
│       └── logging.py               # UBECgpi logging
│
└── UBECtt/                         # 🜂 Fire Token Module
    ├── __init__.py
    ├── UBECtt_protocol.py          # Protocol implementation
    ├── UBECtt_Protocol.md          # Documentation
    └── config/
        ├── __init__.py
        ├── config.py                # UBECtt-specific config
        └── logging.py               # UBECtt logging
```

## Quick Start

### Installation

```bash
# Install dependencies
pip install stellar-sdk

# Optional: Set up virtual environment first
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install stellar-sdk
```

### Basic Usage

#### 1. Health Check All Protocols

```bash
python ubec_main_protocol.py --network PUBLIC --action health
```

#### 2. Get Ecosystem Status

```bash
python ubec_main_protocol.py --action status --output status.json
```

#### 3. Sync All Protocols

```bash
python ubec_main_protocol.py --action sync
```

#### 4. Evaluate Account Holonic Alignment

```bash
python ubec_main_protocol.py --action evaluate --account GXXXX...
```

#### 5. Use Testnet

```bash
python ubec_main_protocol.py --network TESTNET --action health
```

### Individual Token Protocols

Each token can also be used independently:

```python
from UBEC import UBECProtocol
from UBECrc import UBECrcProtocol
from UBECgpi import UBECgpiProtocol
from UBECtt import UBECttProtocol

# Initialize individual protocols
ubec = UBECProtocol()
ubecrc = UBECrcProtocol()
ubecgpi = UBECgpiProtocol()
ubectt = UBECttProtocol()

# Use protocol functions
status = ubec.health_check()
evaluation = ubecrc.evaluate_holonic("GXXXX...")
```

## The Four Elements

### 🜁 UBEC (Air) - Gateway & Access
- **Role:** Universal entry point to the ecosystem
- **Principles:** Freedom, accessibility, universal participation
- **Functions:** Onboarding, basic transactions, gateway access
- **Documentation:** [UBEC/UBEC_Protocol.md](UBEC/UBEC_Protocol.md)

### 🜄 UBECrc (Water) - Reciprocity & Flow
- **Role:** Measure and reward reciprocal exchange
- **Principles:** Flow, adaptability, mutual exchange
- **Functions:** Reciprocity tracking, credit system, community health
- **Documentation:** [UBECrc/UBECrc_Protocol.md](UBECrc/UBECrc_Protocol.md)

### 🜃 UBECgpi (Earth) - Stability & Value
- **Role:** Provide stable, asset-backed value
- **Principles:** Stability, grounding, material value
- **Functions:** Asset backing, value preservation, volatility management
- **Documentation:** [UBECgpi/UBECgpi_Protocol.md](UBECgpi/UBECgpi_Protocol.md)

### 🜂 UBECtt (Fire) - Transformation & Change
- **Role:** Catalyze transformation and innovation
- **Principles:** Energy, transformation, catalytic change
- **Functions:** Innovation rewards, transformation tracking, burn mechanism
- **Documentation:** [UBECtt/UBECtt_Protocol.md](UBECtt/UBECtt_Protocol.md)

## Configuration

### Global Configuration
Edit `config/config.py` to adjust:
- Network settings (PUBLIC/TESTNET)
- Supply parameters
- Distribution targets
- Holonic weights and thresholds

### Token-Specific Configuration
Each token has its own config in `{TOKEN}/config/config.py`:
- **UBEC:** Transaction fees, gateway thresholds
- **UBECrc:** Decay rates, reciprocity bonuses
- **UBECgpi:** Stability thresholds, backing ratios
- **UBECtt:** Transformation fees, innovation bonuses

## Holonic Principles

The UBEC Protocol Suite is built on five holonic principles:

1. **Autonomy & Integration Balance** (25%)
   - Balance individual freedom with collective connection

2. **Multi-Scale Participation** (20%)
   - Engage at local, regional, and global scales

3. **Regenerative Impact** (25%)
   - Create positive environmental and social outcomes

4. **Network Contribution** (15%)
   - Strengthen the overall network

5. **Ubuntu Alignment** (15%)
   - Embody "I am because we are"

### Holonic Categories

Based on composite scores, participants are categorized:
- **Exemplar** (0.9+): Leading by example
- **Integrator** (0.8-0.9): Balancing all dimensions
- **Contributor** (0.6-0.8): Regular valuable contributions
- **Participant** (0.4-0.6): Active engagement
- **Observer** (0.2-0.4): Beginning the journey

## Development

### Project Architecture

The project follows a modular architecture:
- **Global Config**: Shared settings and holonic parameters
- **Token Modules**: Independent, self-contained protocols
- **Main Orchestrator**: Coordinates all token protocols
- **Logging**: Centralized logging infrastructure

### Adding New Features

1. Update relevant configuration in `config/` or `{TOKEN}/config/`
2. Modify protocol implementation in `{TOKEN}/{TOKEN}_protocol.py`
3. Update documentation in `{TOKEN}/{TOKEN}_Protocol.md`
4. Test changes thoroughly

### Testing

```python
# Test individual protocol
python -m UBEC.UBEC_protocol

# Test main orchestrator
python ubec_main_protocol.py --action health
```

## Dependencies

- **Python 3.7+**
- **stellar-sdk**: Stellar blockchain integration

Optional:
- **psycopg2-binary**: Database support
- **networkx**: Network analysis
- **matplotlib**: Visualization

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Specify your license here]

## Support

For questions and support:
- Documentation: See individual protocol docs
- Community: [Community forum/channel]
- Issues: [Issue tracker]

## Acknowledgments

Built with the philosophy of Ubuntu - "I am because we are" - and inspired by Buckminster Fuller's vision of building new models rather than fighting existing reality.

---

## Key Concepts

### Holonic Economics
A holonic system balances individual autonomy with collective integration. Each token operates independently while contributing to the whole ecosystem.

### Four Elements Philosophy
The four elemental tokens mirror natural patterns:
- **Air** provides freedom and access
- **Water** creates flow and reciprocity
- **Earth** grounds with stability
- **Fire** catalyzes transformation

### Ubuntu Philosophy
"I am because we are" - emphasizing interconnectedness and collective well-being as the foundation of the economic system.

---

**Version:** 1.0.0  
**Status:** Active Development  
**Network:** Stellar Blockchain
