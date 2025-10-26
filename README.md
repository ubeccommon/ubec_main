# UBEC Protocol Suite
## Ubuntu Bioregional Economic Commons

> "As we learn to think like a plant, we discover that technology and nature are not opposites but complementary expressions of the same creative forces that shape our world."

---

[![Project Status](https://img.shields.io/badge/status-operational-green)]()
[![Completion](https://img.shields.io/badge/completion-85--90%25-brightgreen)]()
[![Network](https://img.shields.io/badge/network-Stellar%20Mainnet-blue)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-see%20docs-lightgrey)]()

---

## 📋 Table of Contents

- [Overview](#overview)
- [The Four Elements](#the-four-elements)
- [Current Status](#current-status)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Technology Stack](#technology-stack)
- [Contributing](#contributing)
- [Attribution](#attribution)

---

## Overview

The **UBEC Protocol Suite** is a blockchain-based economic system built on the Stellar network that implements the Ubuntu philosophy ("I am because we are") through four interconnected tokens. Each token represents a classical element and embodies a specific Ubuntu principle, creating a holistic economic ecosystem that combines ancient wisdom with modern blockchain technology.

### Core Principle

The system embodies Ubuntu philosophy by treating economic participants as **holons** - entities that are simultaneously whole in themselves and part of a larger whole. This creates an economic model based on:

- **Interconnectedness** - All participants are part of the larger ecosystem
- **Mutual Benefit** - Success is measured collectively, not individually
- **Regeneration** - The system creates positive feedback loops
- **Natural Harmony** - Economic tools mirror natural processes

### Key Features

✅ **Four-Element Token Ecosystem** - Air, Water, Earth, Fire tokens each serving specific functions  
✅ **Ubuntu Principle Assessment** - Holonic evaluation of network participants  
✅ **Stellar Blockchain Integration** - Built on proven, scalable blockchain technology  
✅ **Real-time Synchronization** - Live blockchain data synchronized to local database  
✅ **Comprehensive Analytics** - Deep insights into network health and token distribution  
✅ **Service-Oriented Architecture** - Modular, maintainable, and scalable design

---

## The Four Elements

### 🌬️ Air (UBEC) - Gateway & Universal Access
**Ubuntu Principle:** Diversity

- **Issuer:** `GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCCSIKELEH7ORUCX5UB2VN`
- **Function:** Entry point to ecosystem, ensures universal access
- **Status:** ✅ Live on Stellar Mainnet

### 💧 Water (UBECrc) - Flow & Exchange
**Ubuntu Principle:** Reciprocity

- **Issuer:** `GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC`
- **Function:** Facilitates mutual exchange, tracks reciprocal relationships
- **Status:** ✅ Live on Stellar Mainnet

### 🌍 Earth (UBECgpi) - Stability & Value
**Ubuntu Principle:** Mutualism

- **Issuer:** `GCPU3LUGRIYLWMPOQEEGIL2HI5Z637PQVK42Z5PYRRQMPFDTNT5SUBEC`
- **Function:** Provides stable value reference, community foundation
- **Status:** ✅ Live on Stellar Mainnet

### 🔥 Fire (UBECtt) - Transformation & Action
**Ubuntu Principle:** Regeneration

- **Issuer:** `GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC`
- **Function:** Catalyzes community transformation, rewards action
- **Status:** ✅ Live on Stellar Mainnet

---

## Current Status

### Project Completion: 85-90% ✅

| Component | Status | Details |
|-----------|--------|---------|
| **Core Architecture** | ✅ Complete | Service registry, async operations, modular design |
| **Database Infrastructure** | ✅ Complete | 32 tables, 78,367+ records, full schema |
| **Token Deployment** | ✅ Complete | All 4 tokens live on Stellar mainnet |
| **Core Modules** | ✅ Complete | Sync, evaluation, distribution, audit |
| **Visualization** | ✅ Complete | Charts, reports, analytics dashboards |
| **Data Population** | 🔄 In Progress | 15% complete, active synchronization |
| **Testing** | 🔄 In Progress | 60% coverage, comprehensive suite planned |
| **Documentation** | 🔄 In Progress | 80% complete, user guides in development |
| **Production Hardening** | 🔜 Planned | Security audit, monitoring setup |

**Target Production Date:** November 30, 2025

### Recent Achievements

- ✅ **October 21, 2025:** All four tokens successfully deployed to Stellar mainnet
- ✅ **October 22, 2025:** Design principles compliance verified (100%)
- ✅ **October 23, 2025:** Service registry v3.0 operational
- ✅ **October 24, 2025:** Holonic visualizer enhanced with 10 chart types

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15.13
- Access to Stellar network
- 4GB RAM minimum

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd UBEC

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Initialize database
psql -U postgres -f database/schema/ubec_main_schema.sql

# 6. Verify installation
python main.py health
```

### Basic Usage

```bash
# Check system health
python main.py health

# View system status
python main.py status

# Discover UBEC token holders
python main.py discover --max-accounts 100

# Synchronize blockchain data
python main.py sync --sync-type all

# Check protocol status
python main.py protocol-health

# Generate analytics report
python main.py analytics --analysis-type distribution

# Generate visualizations
python main.py visualize --action report --include-advanced
```

### Quick Reference

For a complete command reference, see [docs/MAIN_PY_QUICK_REFERENCE.md](docs/MAIN_PY_QUICK_REFERENCE.md)

---

## Architecture

### Design Principles

The UBEC Protocol Suite adheres to 12 core design principles:

1. **Modular Design** - Self-contained components
2. **Service Pattern** - Single orchestrator (main.py)
3. **Service Registry** - Central dependency management
4. **Single Source of Truth** - Database as authority
5. **Strict Async Operations** - 100% async/await
6. **No Sync Fallbacks** - Pure async implementation
7. **Per-Asset Monitoring** - Individual tracking
8. **No Duplicate Configuration** - Single definition
9. **Integrated Rate Limiting** - Built-in protection
10. **Separation of Concerns** - Clear layer boundaries
11. **Comprehensive Documentation** - Full docstrings
12. **Method Singularity** - Zero code duplication

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    main.py (SOLE ENTRY)                     │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │           Service Registry (Central Hub)              │ │
│  │                                                       │ │
│  │  Infrastructure:        Protocols:       Operations: │ │
│  │  • database            • air            • analytics  │ │
│  │  • stellar_client      • water          • audit      │ │
│  │  • config              • earth          • visualizer │ │
│  │                        • fire                        │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Layers:                                                    │
│  ┌──────────────┬────────────────┬─────────────────┐      │
│  │ Data Layer   │ Protocol Layer │ System Layer    │      │
│  │ discover     │ evaluate       │ health          │      │
│  │ sync         │ protocols      │ status          │      │
│  │ analytics    │                │                 │      │
│  └──────────────┴────────────────┴─────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

**Primary Schema:** `ubec_main`

- **32 Tables** - Complete data model
- **78,367+ Records** - Active dataset
- **308 Indexes** - Optimized queries
- **79 Functions** - PostgreSQL utilities

**Key Table Categories:**
- Stellar Integration (7 tables)
- Token Management (4 tables)
- Holonic Evaluation (3 tables)
- Element-Specific (16 tables)
- System & Audit (2 tables)

---

## Documentation

### Essential Reading

- **[Comprehensive Status Report](docs/UBEC_COMPREHENSIVE_STATUS_REPORT_2025.md)** - Complete project overview
- **[Quick Reference Guide](docs/MAIN_PY_QUICK_REFERENCE.md)** - Command cheat sheet
- **[Design Principles](docs/DESIGN_PRINCIPLES.md)** - Architectural guidelines
- **[Migration Guides](docs/MIGRATION_TO_UNIFIED.md)** - Version upgrade paths

### Technical Documentation

- **[Service Registry](docs/README_SERVICE_REGISTRY.md)** - Registry architecture and usage
- **[Database Schema](docs/DATABASE_SCHEMA.md)** - Complete schema reference
- **[API Reference](docs/API_REFERENCE.md)** - Function and method documentation
- **[Protocol Specifications](docs/protocols/)** - Element protocol details

### Operational Guides

- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Data Loading](docs/DATA_LOADING_GUIDE.md)** - Data synchronization guide
- **[Analytics Guide](docs/ANALYTICS_INTEGRATION_GUIDE.md)** - Analytics usage

### Development

- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - How to contribute
- **[Code Style](docs/CODE_STYLE.md)** - Coding standards
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Test procedures
- **[Changelog](CHANGELOG.md)** - Version history

---

## Technology Stack

### Core Technologies

**Blockchain:**
- **Network:** Stellar (Mainnet)
- **SDK:** stellar-sdk (Python)
- **API:** Stellar Horizon REST API

**Database:**
- **System:** PostgreSQL 15.13
- **Driver:** asyncpg (async)
- **Extensions:** PostGIS (spatial data)

**Backend:**
- **Language:** Python 3.11+
- **Async:** asyncio, aiohttp
- **Architecture:** Service-oriented

### Key Dependencies

```
stellar-sdk>=9.0.0
asyncpg>=0.28.0
psycopg2-binary>=2.9.0
aiohttp>=3.8.0
python-dotenv>=1.0.0
matplotlib>=3.7.0
numpy>=1.24.0
scipy>=1.10.0
seaborn>=0.12.0
networkx>=3.1
```

For complete dependencies, see `requirements.txt`

---

## Project Structure

```
UBEC/
├── main.py                    # Main orchestrator (sole entry point)
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .env.example              # Environment configuration template
│
├── config/                    # Configuration
│   ├── __init__.py
│   ├── config.py             # Global configuration
│   ├── logging.py            # Logging setup
│   └── settings.py           # Application settings
│
├── core/                      # Core system components
│   ├── __init__.py
│   ├── service_registry.py   # Central service registry
│   ├── db/                   # Database components
│   ├── evaluation/           # Evaluation systems
│   ├── holonic/              # Holonic evaluation
│   ├── protocols/            # Element protocols
│   └── utils/                # Utilities
│
├── services/                  # Service modules
│   ├── analytics/            # Analytics service
│   ├── audit/                # Audit service
│   ├── distribution/         # Distribution management
│   ├── market/               # Market data service
│   └── monitoring/           # Monitoring service
│
├── docs/                      # Documentation
│   ├── UBEC_COMPREHENSIVE_STATUS_REPORT_2025.md
│   ├── MAIN_PY_QUICK_REFERENCE.md
│   ├── protocols/            # Protocol specifications
│   └── visualization/        # Visualization guides
│
├── database/                  # Database files
│   ├── schema/               # Schema definitions
│   └── migrations/           # Migration scripts
│
├── logs/                      # Log files
├── reports/                   # Generated reports
└── phenom/                    # Phenomenological extensions
```

---

## Contributing

We welcome contributions to the UBEC Protocol Suite! Here's how to get started:

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Contribution Guidelines

- Follow the 12 design principles
- Write comprehensive docstrings
- Add tests for new features
- Update documentation
- Ensure async/await patterns
- No code duplication
- Include attribution

For detailed guidelines, see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=services --cov-report=html

# Run specific test file
pytest tests/test_synchronizer.py

# Run with verbose output
pytest -v
```

### Test Coverage

Current test coverage: **60%**  
Target coverage: **80%+**

---

## Performance

### System Capabilities

| Metric | Performance | Status |
|--------|-------------|--------|
| Database Query | <10ms avg | ✅ Excellent |
| Stellar API | 100-500ms | ✅ Normal |
| Cache Hit Rate | >90% | ✅ Excellent |
| Concurrent Ops | 50-100/sec | ✅ Good |
| Memory Usage | ~50MB base | ✅ Efficient |

### Scalability

**Current Capacity:**
- 10,000+ accounts
- 100,000+ transactions
- 1,000,000+ operations
- 4 token types

**Future Expansion:**
- Horizontal scaling via database replication
- Load balancing across instances
- Distributed caching (Redis)
- Message queue integration

---

## Roadmap

### Completed ✅

- [x] Core architecture implementation
- [x] Database schema design and deployment
- [x] All four tokens deployed to mainnet
- [x] Service registry v3.0
- [x] Holonic evaluation system
- [x] Visualization and reporting
- [x] Analytics integration
- [x] Design principles compliance

### In Progress 🔄

- [ ] Complete data population (15%)
- [ ] Comprehensive testing suite (60%)
- [ ] User documentation (80%)
- [ ] Production monitoring setup

### Planned 🔜

- [ ] Security audit and penetration testing
- [ ] Community governance implementation
- [ ] User onboarding system
- [ ] Mobile application
- [ ] API v2.0 with GraphQL
- [ ] Advanced analytics dashboard

**Production Target:** November 30, 2025

---

## Support

### Getting Help

- **Documentation:** Browse `docs/` directory
- **Issues:** Report bugs via issue tracker
- **Questions:** Check FAQ or ask in discussions
- **Email:** [Contact information]

### Common Issues

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for solutions to common problems.

---

## License

[License information - see LICENSE file]

---

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Project Information

- **Version:** 1.0.0 (Production Preparation)
- **Status:** 85-90% Complete
- **Target Launch:** November 30, 2025
- **Last Updated:** October 25, 2025
- **Maintained By:** UBEC Development Team

---

## Acknowledgments

This project embodies the Ubuntu philosophy and honors:

- The wisdom of Ubuntu: "I am because we are"
- The Stellar Development Foundation
- The open-source community
- Claude and Anthropic PBC for AI assistance
- All contributors and supporters

---

**"When technology and nature dance together, we create systems that nurture all beings."**

---

*For detailed project status, see [UBEC_COMPREHENSIVE_STATUS_REPORT_2025.md](docs/UBEC_COMPREHENSIVE_STATUS_REPORT_2025.md)*
