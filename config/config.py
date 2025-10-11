# config/config.py
"""
UBEC Protocol - Unified Configuration
======================================
Single source of truth for all configuration.

Imports from settings.py and provides both:
- Config dataclass (new style)
- GlobalConfig class (for legacy compatibility)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import os
from decimal import Decimal
from typing import Dict, List, Union
from dataclasses import dataclass, field

# Import from settings.py to preserve existing values
# Try multiple import methods to ensure we find it
HAS_SETTINGS = False
settings = None

# Method 1: Relative import (if imported as package)
try:
    from . import settings
    HAS_SETTINGS = True
except (ImportError, ValueError):
    pass

# Method 2: Direct import (if config is in sys.path)
if not HAS_SETTINGS:
    try:
        import config.settings as settings
        HAS_SETTINGS = True
    except ImportError:
        pass

# Method 3: Absolute import from current location
if not HAS_SETTINGS:
    try:
        import sys
        import os
        # Get the directory where this config.py file is located
        config_dir = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(config_dir, 'settings.py')
        
        if os.path.exists(settings_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("settings", settings_path)
            settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings)
            HAS_SETTINGS = True
    except Exception:
        pass

# Load from environment
from dotenv import load_dotenv
load_dotenv()


@dataclass
class TokenConfig:
    """Configuration for a single token"""
    code: str
    issuer: str
    minimum_transaction: Decimal = Decimal('10.0')
    distribution_general: Decimal = Decimal('0.75')
    distribution_stewardship: Decimal = Decimal('0.20')
    distribution_admin: Decimal = Decimal('0.05')


@dataclass
class Config:
    """
    Single source of truth for all configuration.
    Dataclass style for new code.
    """
    
    # Network (from settings.py or env)
    NETWORK: str = field(default_factory=lambda: 
        getattr(settings, 'NETWORK', None) if HAS_SETTINGS 
        else os.getenv('STELLAR_NETWORK', 'mainnet')
    )
    
    # Horizon URL
    HORIZON_URL: str = field(default_factory=lambda:
        getattr(settings, 'HORIZON_URL', None) if HAS_SETTINGS
        else os.getenv('STELLAR_HORIZON_URL', 'https://horizon.stellar.org')
    )
    
    # UBEC Token (from settings.py or env)
    UBEC_CODE: str = field(default_factory=lambda:
        getattr(settings, 'UBEC_CODE', 'UBEC') if HAS_SETTINGS else 'UBEC'
    )
    
    UBEC_ISSUER: str = field(default_factory=lambda:
        getattr(settings, 'UBEC_ISSUER', None) if HAS_SETTINGS
        else os.getenv('UBEC_ISSUER', '')
    )
    
    # Supply (from settings.py)
    FALLBACK_SUPPLY: Decimal = field(default_factory=lambda:
        getattr(settings, 'FALLBACK_SUPPLY', Decimal('191766039.00')) if HAS_SETTINGS
        else Decimal('191766039.00')
    )
    
    ALWAYS_LOAD_FROM_NETWORK: bool = field(default_factory=lambda:
        getattr(settings, 'ALWAYS_LOAD_FROM_NETWORK', True) if HAS_SETTINGS else True
    )
    
    # Distribution (from settings.py)
    TARGET_DISTRIBUTION: Dict[str, Decimal] = field(default_factory=lambda:
        getattr(settings, 'TARGET_DISTRIBUTION', {
            'general': Decimal('0.65'),
            'stewardship': Decimal('0.30'),
            'administration': Decimal('0.05')
        }) if HAS_SETTINGS else {
            'general': Decimal('0.65'),
            'stewardship': Decimal('0.30'),
            'administration': Decimal('0.05')
        }
    )
    
    # Accounts (from settings.py)
    ACCOUNTS: Dict[str, Union[str, List[str]]] = field(default_factory=lambda:
        getattr(settings, 'ACCOUNTS', {}) if HAS_SETTINGS else {}
    )
    
    # Operation settings (from settings.py)
    REBALANCE_THRESHOLD: Decimal = field(default_factory=lambda:
        getattr(settings, 'REBALANCE_THRESHOLD', Decimal('0.01')) if HAS_SETTINGS
        else Decimal('0.01')
    )
    
    CHECK_INTERVAL: int = field(default_factory=lambda:
        getattr(settings, 'CHECK_INTERVAL', 3600) if HAS_SETTINGS else 3600
    )
    
    # Supply calculation (from settings.py)
    SUPPLY_CHECK_INTERVAL: int = field(default_factory=lambda:
        getattr(settings, 'SUPPLY_CHECK_INTERVAL', 86400) if HAS_SETTINGS else 86400
    )
    
    SUPPLY_SAFETY_FACTOR: Decimal = field(default_factory=lambda:
        getattr(settings, 'SUPPLY_SAFETY_FACTOR', Decimal('0.02')) if HAS_SETTINGS
        else Decimal('0.02')
    )
    
    SUPPLY_CALCULATION_METHOD: str = field(default_factory=lambda:
        getattr(settings, 'SUPPLY_CALCULATION_METHOD', 'PRECISE') if HAS_SETTINGS
        else 'PRECISE'
    )
    
    # Tokens configuration
    TOKENS: Dict[str, TokenConfig] = field(default_factory=lambda: {
        'UBEC': TokenConfig(
            code='UBEC',
            issuer=os.getenv('UBEC_ISSUER', 'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN'),
            minimum_transaction=Decimal('10.0'),
            distribution_general=Decimal('0.65'),
            distribution_stewardship=Decimal('0.30'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECrc': TokenConfig(
            code='UBECrc',
            issuer=os.getenv('UBECrc_ISSUER', 'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC'),
            minimum_transaction=Decimal('5.0'),
            distribution_general=Decimal('0.70'),
            distribution_stewardship=Decimal('0.25'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECgpi': TokenConfig(
            code='UBECgpi',
            issuer=os.getenv('UBECgpi_ISSUER', 'GCPU3LUGRIYLWMPOQEEGIL2HI5Z637PQVK42Z5PYRRQMPFDTNT5SUBEC'),
            minimum_transaction=Decimal('100.0'),
            distribution_general=Decimal('0.80'),
            distribution_stewardship=Decimal('0.15'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECtt': TokenConfig(
            code='UBECtt',
            issuer=os.getenv('UBECtt_ISSUER', 'GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC'),
            minimum_transaction=Decimal('1.0'),
            distribution_general=Decimal('0.75'),
            distribution_stewardship=Decimal('0.20'),
            distribution_admin=Decimal('0.05')
        )
    })
    
    # Database
    DATABASE_URL: str = field(default_factory=lambda:
        os.getenv('DATABASE_URL', 'postgresql://ubec_app:App252010!@#@localhost/ubec')
    )
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # Sync Settings
    SYNC_BATCH_SIZE: int = 200
    SYNC_BATCH_DELAY: float = 1.0
    SYNC_MAX_ACCOUNTS: int = 1000
    
    # Holonic Weights
    HOLONIC_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        'autonomy_integration': 0.25,
        'multi_scale': 0.20,
        'regenerative': 0.25,
        'network': 0.15,
        'ubuntu': 0.15
    })
    
    # Logging (from settings.py or env)
    LOG_LEVEL: str = field(default_factory=lambda:
        getattr(settings, 'LOG_LEVEL', None) if HAS_SETTINGS
        else os.getenv('LOG_LEVEL', 'INFO')
    )
    
    LOG_FORMAT: str = field(default_factory=lambda:
        getattr(settings, 'LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
        if HAS_SETTINGS
        else '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    LOG_FILE: str = field(default_factory=lambda:
        getattr(settings, 'LOG_FILE', 'ubec_protocol.log') if HAS_SETTINGS
        else 'ubec_protocol.log'
    )
    
    @property
    def horizon_url(self) -> str:
        """Get Horizon URL for current network"""
        return self.HORIZON_URL
    
    def get_token_config(self, token_code: str) -> TokenConfig:
        """Get configuration for specific token"""
        if token_code not in self.TOKENS:
            raise ValueError(f"Unknown token: {token_code}")
        return self.TOKENS[token_code]


class GlobalConfig:
    """
    Legacy-style configuration class for compatibility.
    
    Provides the same interface as Config but as a class instead of dataclass.
    Used by holonic evaluator and other legacy modules.
    """
    
    def __init__(self):
        """Initialize GlobalConfig by creating a Config instance"""
        self._config = Config()
    
    # Network
    @property
    def NETWORK(self) -> str:
        return self._config.NETWORK
    
    @property
    def HORIZON_URL(self) -> str:
        return self._config.HORIZON_URL
    
    @property
    def horizon_url(self) -> str:
        return self._config.horizon_url
    
    # UBEC Token
    @property
    def UBEC_CODE(self) -> str:
        return self._config.UBEC_CODE
    
    @property
    def UBEC_ISSUER(self) -> str:
        return self._config.UBEC_ISSUER
    
    # Supply
    @property
    def FALLBACK_SUPPLY(self) -> Decimal:
        return self._config.FALLBACK_SUPPLY
    
    @property
    def ALWAYS_LOAD_FROM_NETWORK(self) -> bool:
        return self._config.ALWAYS_LOAD_FROM_NETWORK
    
    # Distribution
    @property
    def TARGET_DISTRIBUTION(self) -> Dict[str, Decimal]:
        return self._config.TARGET_DISTRIBUTION
    
    @property
    def ACCOUNTS(self) -> Dict[str, Union[str, List[str]]]:
        return self._config.ACCOUNTS
    
    # Operations
    @property
    def REBALANCE_THRESHOLD(self) -> Decimal:
        return self._config.REBALANCE_THRESHOLD
    
    @property
    def CHECK_INTERVAL(self) -> int:
        return self._config.CHECK_INTERVAL
    
    # Supply calculation
    @property
    def SUPPLY_CHECK_INTERVAL(self) -> int:
        return self._config.SUPPLY_CHECK_INTERVAL
    
    @property
    def SUPPLY_SAFETY_FACTOR(self) -> Decimal:
        return self._config.SUPPLY_SAFETY_FACTOR
    
    @property
    def SUPPLY_CALCULATION_METHOD(self) -> str:
        return self._config.SUPPLY_CALCULATION_METHOD
    
    # Tokens
    @property
    def TOKENS(self) -> Dict[str, TokenConfig]:
        return self._config.TOKENS
    
    # Database
    @property
    def DATABASE_URL(self) -> str:
        return self._config.DATABASE_URL
    
    # Rate limiting
    @property
    def RATE_LIMIT_CALLS(self) -> int:
        return self._config.RATE_LIMIT_CALLS
    
    @property
    def RATE_LIMIT_PERIOD(self) -> int:
        return self._config.RATE_LIMIT_PERIOD
    
    # Sync
    @property
    def SYNC_BATCH_SIZE(self) -> int:
        return self._config.SYNC_BATCH_SIZE
    
    @property
    def SYNC_BATCH_DELAY(self) -> float:
        return self._config.SYNC_BATCH_DELAY
    
    @property
    def SYNC_MAX_ACCOUNTS(self) -> int:
        return self._config.SYNC_MAX_ACCOUNTS
    
    # Holonic
    @property
    def HOLONIC_WEIGHTS(self) -> Dict[str, float]:
        return self._config.HOLONIC_WEIGHTS
    
    # Logging
    @property
    def LOG_LEVEL(self) -> str:
        return self._config.LOG_LEVEL
    
    @property
    def LOG_FORMAT(self) -> str:
        return self._config.LOG_FORMAT
    
    @property
    def LOG_FILE(self) -> str:
        return self._config.LOG_FILE
    
    @property
    def LOG_FILE_PATH(self) -> str:
        """Alias for LOG_FILE for backward compatibility"""
        return self._config.LOG_FILE
    
    def get_token_config(self, token_code: str) -> TokenConfig:
        """Get configuration for specific token"""
        return self._config.get_token_config(token_code)


# SINGLE GLOBAL INSTANCES
config = Config()
global_config = GlobalConfig()

def validate_config() -> bool:
    """
    Validate configuration is complete and correct.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    # Check critical configuration
    if not config.UBEC_ISSUER:
        return False
    
    if not config.HORIZON_URL:
        return False
    
    # Configuration is valid
    return True


def display_config() -> Dict[str, str]:
    """
    Display current configuration values.
    
    Returns:
        dict: Current configuration as a dictionary
    """
    return {
        'NETWORK': config.NETWORK,
        'HORIZON_URL': config.HORIZON_URL,
        'UBEC_CODE': config.UBEC_CODE,
        'UBEC_ISSUER': config.UBEC_ISSUER,
        'ACCOUNTS': str(config.ACCOUNTS),
        'LOG_LEVEL': config.LOG_LEVEL,
    }


# For backward compatibility - both names work
__all__ = [
    'Config', 'GlobalConfig', 'TokenConfig', 
    'config', 'global_config', 
    'validate_config', 'display_config'
]
