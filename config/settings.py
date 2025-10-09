# config/settings.py

from decimal import Decimal

# Network configuration
NETWORK = "PUBLIC"  # Use the public Stellar network
HORIZON_URL = "https://horizon.stellar.org"
PUBLIC_NETWORK_PASSPHRASE = "Public Global Stellar Network ; September 2015"

# UBEC token configuration
UBEC_CODE = "UBEC"
UBEC_ISSUER = "GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN"

# Supply configuration
FALLBACK_SUPPLY = Decimal('191766039.00')  # Verified from Stellar.Expert - 191,766,039 UBEC
ALWAYS_LOAD_FROM_NETWORK = True  # Forces dynamic loading of supply from Stellar network

# Distribution targets
TARGET_DISTRIBUTION = {
    'general': Decimal('0.65'),  # 65% for general distribution
    'stewardship': Decimal('0.30'),  # 30% for token ecosystem stewardship
    'administration': Decimal('0.05')  # 5% for administrative responsibilities
}

# Account addresses for different distribution categories
ACCOUNTS = {
    'general': "GDC2ECKYO4WJMD35M4E2JIABPTA4VLHC6L6MU4TIRCLSOPOOIYOYTM74",
    'administration': "GDEQ4KXOL6NV5RGETFTJLMULACO5M5GTYBKOEGTCN2MSSJCOAID5UBEC",
    'stewardship': [
        "GA3I6MN4NSUKZ2NQZBWLUP6MNMPLZFD3ABOA3CMBV23NBDBFRWRUUBEC",  # Management Account
        "GCBT4HZHOXJCCVDQDJHA7KR6IN3RANWBPK3DKCSUPN2R4BMCGBZYUBEC",  # Infrastructure Account
        "GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC"   # Liquidity Pool
    ]
}

# Operation settings
REBALANCE_THRESHOLD = Decimal('0.01')  # 1% deviation threshold for distribution rebalancing
CHECK_INTERVAL = 3600  # Check distribution every hour (in seconds)

# Dynamic supply calculation settings
SUPPLY_CHECK_INTERVAL = 86400  # Check total supply daily (in seconds)
SUPPLY_SAFETY_FACTOR = Decimal('0.02')  # Allow 2% variance before triggering alerts

# Supply calculation methods
SUPPLY_CALCULATION_METHOD = "PRECISE"  # Options: "BASIC", "PRECISE", "ISSUER"
# BASIC - Quick calculation based on monitored accounts
# PRECISE - Comprehensive calculation querying all accounts (resource intensive)
# ISSUER - Calculate based on issued amount minus issuer holdings

# Logging configuration
LOG_FILE = 'ubec_distribution_manager.log'
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
