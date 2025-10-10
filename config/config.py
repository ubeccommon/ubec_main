# config/config.py
"""
UBEC Protocol Suite - Centralized Configuration
THE ONLY configuration file in the entire system

All configuration parameters are defined exactly once here.
No other configuration files exist.

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import os
from decimal import Decimal
from typing import Dict
from dataclasses import dataclass, field


@dataclass
class TokenConfig:
    """Configuration for a single token"""
    code: str
    issuer: str
    minimum_transaction: Decimal
    distribution_general: Decimal
    distribution_stewardship: Decimal
    distribution_admin: Decimal


@dataclass
class Config:
    """
    Single source of truth for all configuration
    
    All configuration parameters defined here, once.
    """
    
    # Network
    NETWORK: str = field(default_factory=lambda: os.getenv('UBEC_NETWORK', 'testnet'))
    
    # Horizon URLs
    HORIZON_URLS: Dict[str, str] = field(default_factory=lambda: {
        'mainnet': 'https://horizon.stellar.org',
        'testnet': 'https://horizon-testnet.stellar.org'
    })
    
    # Tokens (defined once)
    TOKENS: Dict[str, TokenConfig] = field(default_factory=lambda: {
        'UBEC': TokenConfig(
            code='UBEC',
            issuer=os.getenv('UBEC_ISSUER', 'GXXX...'),
            minimum_transaction=Decimal('10.0'),
            distribution_general=Decimal('0.75'),
            distribution_stewardship=Decimal('0.20'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECrc': TokenConfig(
            code='UBECrc',
            issuer=os.getenv('UBECrc_ISSUER', 'GXXX...'),
            minimum_transaction=Decimal('5.0'),
            distribution_general=Decimal('0.70'),
            distribution_stewardship=Decimal('0.25'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECgpi': TokenConfig(
            code='UBECgpi',
            issuer=os.getenv('UBECgpi_ISSUER', 'GXXX...'),
            minimum_transaction=Decimal('100.0'),
            distribution_general=Decimal('0.80'),
            distribution_stewardship=Decimal('0.15'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECtt': TokenConfig(
            code='UBECtt',
            issuer=os.getenv('UBECtt_ISSUER', 'GXXX...'),
            minimum_transaction=Decimal('1.0'),
            distribution_general=Decimal('0.75'),
            distribution_stewardship=Decimal('0.20'),
            distribution_admin=Decimal('0.05')
        )
    })
    
    # Database
    DATABASE_URL: str = field(
        default_factory=lambda: os.getenv(
            'DATABASE_URL',
            'postgresql://ubec_app:password@localhost/ubec'
        )
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
    
    # Logging
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @property
    def horizon_url(self) -> str:
        """Get Horizon URL for current network"""
        return self.HORIZON_URLS[self.NETWORK]
    
    def get_token_config(self, token_code: str) -> TokenConfig:
        """Get configuration for specific token"""
        if token_code not in self.TOKENS:
            raise ValueError(f"Unknown token: {token_code}")
        return self.TOKENS[token_code]


# SINGLE GLOBAL INSTANCE
config = Config()
