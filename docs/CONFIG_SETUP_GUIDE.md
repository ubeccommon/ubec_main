# Configuration Setup Guide

**Files Created:**
- `config.py` - Main configuration module
- `.env.example` - Example environment variables file

---

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install python-dotenv psycopg2-binary stellar-sdk
```

### 2. Create Project Structure

```bash
# Create the config directory
mkdir -p ~/UBEC/projects/UBEC/config

# Copy the config file
cp config.py ~/UBEC/projects/UBEC/config/

# Make it a Python package
touch ~/UBEC/projects/UBEC/config/__init__.py
```

### 3. Create Your .env File

```bash
# Copy the example
cp .env.example ~/UBEC/projects/UBEC/.env

# Edit with your values
nano ~/UBEC/projects/UBEC/.env

# Secure the file
chmod 600 ~/UBEC/projects/UBEC/.env
```

### 4. Update .env with Your Values

Edit `.env` and update:

```bash
# Set network (testnet for development)
UBEC_NETWORK=testnet

# Add your Stellar issuer addresses (from your Stellar account)
UBEC_ISSUER=GD...your_actual_address...
UBECrc_ISSUER=GD...your_actual_address...
UBECgpi_ISSUER=GD...your_actual_address...
UBECtt_ISSUER=GD...your_actual_address...

# Update database passwords (use the ones you set earlier)
UBEC_DB_PASSWORD=YourSecureAppP@ssw0rd!2025
UBEC_DB_READONLY_PASSWORD=YourSecureRe@dP@ssw0rd!2025
UBEC_DB_SYNC_PASSWORD=YourSecureSyncP@ssw0rd!2025
```

### 5. Add .env to .gitignore

```bash
echo ".env" >> ~/UBEC/projects/UBEC/.gitignore
echo ".env.*" >> ~/UBEC/projects/UBEC/.gitignore
echo "!.env.example" >> ~/UBEC/projects/UBEC/.gitignore
```

---

## ✅ Test the Configuration

Create a test script:

```python
# test_config.py
from config.config import GlobalConfig, get_logger, validate_config, display_config

# Display configuration
display_config()

# Validate
is_valid = validate_config()
print(f"\nConfiguration valid: {is_valid}")

# Test database connection
print(f"\nDatabase URL: {GlobalConfig.get_database_url('app')}")

# Test element info
air_info = GlobalConfig.get_element_info('air')
print(f"\nAir Token: {air_info['token']} ({air_info['symbol']})")
```

Run the test:

```bash
cd ~/UBEC/projects/UBEC
python test_config.py
```

---

## 📋 Configuration Module Features

### 1. Network Configuration

```python
from config.config import GlobalConfig

# Get Horizon URL
horizon_url = GlobalConfig.get_horizon_url()

# Get network passphrase
passphrase = GlobalConfig.get_network_passphrase()

# Check current network
print(f"Network: {GlobalConfig.NETWORK}")
```

### 2. Token Configuration

```python
# Get token info for an element
token_code, issuer = GlobalConfig.get_token_config('air')
print(f"Air token: {token_code}")
print(f"Issuer: {issuer}")

# Get all token codes
print(f"UBEC: {GlobalConfig.UBEC_CODE}")
print(f"UBECrc: {GlobalConfig.UBECrc_CODE}")
print(f"UBECgpi: {GlobalConfig.UBECgpi_CODE}")
print(f"UBECtt: {GlobalConfig.UBECtt_CODE}")
```

### 3. Database Configuration

```python
# Get database connection URL
app_url = GlobalConfig.get_database_url('app')
readonly_url = GlobalConfig.get_database_url('readonly')
sync_url = GlobalConfig.get_database_url('sync')

# Get connection parameters
params = GlobalConfig.get_database_params('app')
print(params)
# {'host': 'localhost', 'port': 5432, 'database': 'ubec', ...}
```

### 4. Distribution Rules

```python
# Get distribution rules for a token
ubec_rules = GlobalConfig.get_distribution_rules('UBEC')
print(f"General: {ubec_rules['general_circulation']}%")
print(f"Stewardship: {ubec_rules['stewardship']}%")
print(f"Administration: {ubec_rules['administration']}%")
```

### 5. Ubuntu Principles

```python
# Get principle for an element
principle = GlobalConfig.ELEMENT_TO_PRINCIPLE['air']
print(f"Air principle: {principle}")  # diversity

# Get element for a principle
element = GlobalConfig.PRINCIPLE_TO_ELEMENT['reciprocity']
print(f"Reciprocity element: {element}")  # water
```

### 6. Element Information

```python
# Get detailed element info
air_info = GlobalConfig.get_element_info('air')
print(f"Name: {air_info['name']}")
print(f"Symbol: {air_info['symbol']}")
print(f"Role: {air_info['role']}")
print(f"Principle: {air_info['principle']}")
print(f"Characteristics: {air_info['characteristics']}")
```

### 7. Logging

```python
from config.config import get_logger

# Get logger for your module
logger = get_logger('my_module')

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### 8. Health Status

```python
from decimal import Decimal

# Get health status from score
score = Decimal('0.85')
status = GlobalConfig.get_health_status(score)
print(f"Status: {status}")  # excellent
```

---

## 🔧 Using in Your Protocols

### Example: Air Protocol

```python
# elements/air/UBEC_protocol.py
from stellar_sdk import Server, Asset
from config.config import GlobalConfig, get_logger

logger = get_logger('UBEC')

class UBECProtocol:
    def __init__(self):
        logger.info("Initializing UBEC (Air) Protocol")
        
        # Get Stellar configuration
        self.server = Server(horizon_url=GlobalConfig.get_horizon_url())
        
        # Get token configuration
        token_code, issuer = GlobalConfig.get_token_config('air')
        self.asset = Asset(token_code, issuer)
        
        logger.info(f"Connected to {GlobalConfig.NETWORK} network")
        logger.info(f"Asset: {token_code}:{issuer}")
```

### Example: Database Connection

```python
import psycopg2
from config.config import GlobalConfig

# Connect using app user
conn = psycopg2.connect(**GlobalConfig.get_database_params('app'))

# Or using URL
conn = psycopg2.connect(GlobalConfig.get_database_url('app'))
```

---

## 📁 Expected File Structure

After setup, your structure should look like:

```
UBEC/projects/UBEC/
├── .env                          # Your actual configuration (NOT in git)
├── .env.example                  # Example template (in git)
├── .gitignore                    # Includes .env
│
├── config/
│   ├── __init__.py
│   └── config.py                 # Main configuration module
│
├── core/                         # Copy from Ubuntu_EcoCoin (next step)
│   ├── db/
│   ├── holonic/
│   ├── distribution/
│   └── audit/
│
├── elements/                     # Create next (Week 2)
│   ├── air/
│   ├── water/
│   ├── earth/
│   └── fire/
│
└── protocol/                     # Create later (Week 2)
    └── ubec_main_protocol.py
```

---

## ⚠️ Important Notes

### Security

1. **Never commit .env to git**
   ```bash
   # Always in .gitignore
   .env
   .env.*
   !.env.example
   ```

2. **Use strong passwords**
   - Minimum 16 characters
   - Mix of letters, numbers, symbols
   - Different for each user

3. **Rotate passwords regularly**
   - Every 90 days minimum
   - After any security incident

### Development vs Production

**Development (.env):**
```bash
UBEC_NETWORK=testnet
LOG_LEVEL=DEBUG
DEBUG=true
LOG_TO_FILE=false
```

**Production (.env):**
```bash
UBEC_NETWORK=mainnet
LOG_LEVEL=INFO
DEBUG=false
LOG_TO_FILE=true
UBEC_DB_SSL_MODE=require
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] `config.py` copied to `config/` directory
- [ ] `__init__.py` created in `config/` directory
- [ ] `.env` file created from `.env.example`
- [ ] All issuer addresses updated in `.env`
- [ ] All database passwords updated in `.env`
- [ ] `.env` file permissions set to 600
- [ ] `.env` added to `.gitignore`
- [ ] Test script runs without errors
- [ ] Configuration validation passes

---

## 🎯 Next Steps

After configuration is set up:

1. **Copy existing modules** from Ubuntu_EcoCoin:
   ```bash
   cd ~/UBEC/projects/UBEC
   mkdir -p core
   cp -r ~/Ubuntu_EcoCoin/db ./core/
   cp -r ~/Ubuntu_EcoCoin/holonic ./core/
   cp -r ~/Ubuntu_EcoCoin/audit ./core/
   mkdir -p core/distribution
   cp ~/Ubuntu_EcoCoin/ubec_distribution_manager.py ./core/distribution/
   ```

2. **Create first element protocol** (Air - UBEC)
   - Use code from `INTEGRATION_GUIDE_Practical_Code_Examples.md`

3. **Test database connection**
   ```python
   from config.config import GlobalConfig
   import psycopg2
   
   conn = psycopg2.connect(**GlobalConfig.get_database_params('app'))
   print("✓ Database connection successful!")
   ```

---

**Configuration Status:** ✅ Ready to use

**Next Module:** Copy existing Ubuntu_EcoCoin modules to `core/`
