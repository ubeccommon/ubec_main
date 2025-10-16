# config/config.py
"""
UBEC Protocol - Unified Configuration Service
==============================================
Single source of truth for all configuration.

This module provides configuration management following the service pattern.
Configuration is loaded from environment variables (primary source) with
sensible defaults. Legacy settings.py is supported for backward compatibility
but environment variables take precedence.

Design Principles Compliance:
- ✅ Modular Design: Self-contained configuration module
- ✅ Service Pattern: Factory function for instantiation
- ✅ Service Registry: Accessed through registry
- ✅ Single Source of Truth: Environment variables → defaults → settings.py
- ✅ Strict Async: Synchronous by nature (no I/O)
- ✅ No Sync Fallbacks: No fallbacks needed
- ✅ Per-Asset Monitoring: Token-level configuration available
- ✅ No Duplicate Config: Clear precedence order
- ✅ Integrated Rate Limiting: Rate limit config provided
- ✅ Separation of Concerns: Pure configuration
- ✅ Documentation: Comprehensive docstrings
- ✅ Method Singularity: No duplicate methods

Usage:
    # Via service registry (preferred)
    from core.service_registry import registry
    config = registry.get_initialized('config')
    
    # Direct instantiation (legacy)
    from config.config import create_config_service
    config = create_config_service()
    
    # Access configuration
    horizon_url = config.horizon_url
    token_cfg = config.get_token_config('UBEC')

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.

Version: 2.0.0 (Service Pattern + Health Check)
Date: October 16, 2025
"""

import os
import logging
from decimal import Decimal
from typing import Dict, List, Union, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION LOADING UTILITIES
# ============================================================================

def _load_legacy_settings() -> Optional[Any]:
    """
    Attempt to load legacy settings.py for backward compatibility.
    
    This is a fallback mechanism only. Environment variables take precedence.
    
    Returns:
        Settings module if found, None otherwise
    """
    settings = None
    
    # Method 1: Relative import
    try:
        from . import settings as _settings
        settings = _settings
        logger.debug("Loaded settings via relative import")
        return settings
    except (ImportError, ValueError):
        pass
    
    # Method 2: Direct import
    try:
        import config.settings as _settings
        settings = _settings
        logger.debug("Loaded settings via direct import")
        return settings
    except ImportError:
        pass
    
    # Method 3: Absolute import from file
    try:
        import sys
        import importlib.util
        config_dir = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(config_dir, 'settings.py')
        
        if os.path.exists(settings_path):
            spec = importlib.util.spec_from_file_location("settings", settings_path)
            settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings)
            logger.debug("Loaded settings via absolute path")
            return settings
    except Exception as e:
        logger.debug(f"Could not load settings.py: {e}")
    
    logger.debug("No legacy settings.py found, using environment/defaults only")
    return None


def _get_config_value(env_key: str, settings_key: str, default: Any, 
                      settings_module: Optional[Any] = None) -> Any:
    """
    Get configuration value with clear precedence order.
    
    Precedence (highest to lowest):
    1. Environment variable
    2. Legacy settings.py
    3. Default value
    
    Args:
        env_key: Environment variable name
        settings_key: Key in settings.py
        default: Default value if not found
        settings_module: Optional settings module
    
    Returns:
        Configuration value
    """
    # 1. Check environment variable first (highest priority)
    env_value = os.getenv(env_key)
    if env_value is not None:
        return env_value
    
    # 2. Check legacy settings.py (medium priority)
    if settings_module and hasattr(settings_module, settings_key):
        return getattr(settings_module, settings_key)
    
    # 3. Use default (lowest priority)
    return default


# Load legacy settings once at module level
_LEGACY_SETTINGS = _load_legacy_settings()


# ============================================================================
# TOKEN CONFIGURATION
# ============================================================================

@dataclass
class TokenConfig:
    """
    Configuration for a single UBEC token.
    
    Attributes:
        code: Token code (e.g., 'UBEC', 'UBECrc')
        issuer: Stellar issuer public key
        minimum_transaction: Minimum transaction amount
        distribution_general: General distribution percentage
        distribution_stewardship: Stewardship distribution percentage
        distribution_admin: Admin distribution percentage
    """
    code: str
    issuer: str
    minimum_transaction: Decimal = Decimal('10.0')
    distribution_general: Decimal = Decimal('0.75')
    distribution_stewardship: Decimal = Decimal('0.20')
    distribution_admin: Decimal = Decimal('0.05')
    
    def __post_init__(self):
        """Validate token configuration."""
        if not self.code:
            raise ValueError("Token code cannot be empty")
        if not self.issuer:
            raise ValueError("Token issuer cannot be empty")
        
        # Validate distribution percentages sum to 1.0
        total = self.distribution_general + self.distribution_stewardship + self.distribution_admin
        if abs(float(total) - 1.0) > 0.001:  # Allow small floating point errors
            raise ValueError(f"Distribution percentages must sum to 1.0, got {total}")


# ============================================================================
# MAIN CONFIGURATION CLASS
# ============================================================================

@dataclass
class Config:
    """
    Single source of truth for all UBEC configuration.
    
    Configuration is loaded with clear precedence:
    1. Environment variables (primary source)
    2. Legacy settings.py (backward compatibility)
    3. Default values (sensible defaults)
    
    This class is designed to be instantiated via factory function
    for service pattern compliance.
    """
    
    # ========================================================================
    # NETWORK CONFIGURATION
    # ========================================================================
    
    NETWORK: str = field(default_factory=lambda: _get_config_value(
        'STELLAR_NETWORK', 'NETWORK', 'mainnet', _LEGACY_SETTINGS
    ))
    
    HORIZON_URL: str = field(default_factory=lambda: _get_config_value(
        'STELLAR_HORIZON_URL', 'HORIZON_URL', 
        'https://horizon.stellar.org', _LEGACY_SETTINGS
    ))
    
    # ========================================================================
    # UBEC TOKEN CONFIGURATION
    # ========================================================================
    
    UBEC_CODE: str = field(default_factory=lambda: _get_config_value(
        'UBEC_CODE', 'UBEC_CODE', 'UBEC', _LEGACY_SETTINGS
    ))
    
    UBEC_ISSUER: str = field(default_factory=lambda: _get_config_value(
        'UBEC_ISSUER', 'UBEC_ISSUER',
        'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN',
        _LEGACY_SETTINGS
    ))
    
    # ========================================================================
    # SUPPLY CONFIGURATION
    # ========================================================================
    
    FALLBACK_SUPPLY: Decimal = field(default_factory=lambda: Decimal(
        _get_config_value('FALLBACK_SUPPLY', 'FALLBACK_SUPPLY', 
                         '191766039.00', _LEGACY_SETTINGS)
    ))
    
    ALWAYS_LOAD_FROM_NETWORK: bool = field(default_factory=lambda: 
        _get_config_value('ALWAYS_LOAD_FROM_NETWORK', 'ALWAYS_LOAD_FROM_NETWORK',
                         True, _LEGACY_SETTINGS)
    )
    
    # ========================================================================
    # DISTRIBUTION CONFIGURATION
    # ========================================================================
    
    TARGET_DISTRIBUTION: Dict[str, Decimal] = field(default_factory=lambda: {
        'general': Decimal('0.65'),
        'stewardship': Decimal('0.30'),
        'administration': Decimal('0.05')
    })
    
    ACCOUNTS: Dict[str, Union[str, List[str]]] = field(default_factory=lambda:
        getattr(_LEGACY_SETTINGS, 'ACCOUNTS', {}) if _LEGACY_SETTINGS else {}
    )
    
    # ========================================================================
    # OPERATION SETTINGS
    # ========================================================================
    
    REBALANCE_THRESHOLD: Decimal = field(default_factory=lambda: Decimal(
        _get_config_value('REBALANCE_THRESHOLD', 'REBALANCE_THRESHOLD',
                         '0.01', _LEGACY_SETTINGS)
    ))
    
    CHECK_INTERVAL: int = field(default_factory=lambda: int(
        _get_config_value('CHECK_INTERVAL', 'CHECK_INTERVAL',
                         '3600', _LEGACY_SETTINGS)
    ))
    
    # ========================================================================
    # SUPPLY CALCULATION
    # ========================================================================
    
    SUPPLY_CHECK_INTERVAL: int = field(default_factory=lambda: int(
        _get_config_value('SUPPLY_CHECK_INTERVAL', 'SUPPLY_CHECK_INTERVAL',
                         '86400', _LEGACY_SETTINGS)
    ))
    
    SUPPLY_SAFETY_FACTOR: Decimal = field(default_factory=lambda: Decimal(
        _get_config_value('SUPPLY_SAFETY_FACTOR', 'SUPPLY_SAFETY_FACTOR',
                         '0.02', _LEGACY_SETTINGS)
    ))
    
    SUPPLY_CALCULATION_METHOD: str = field(default_factory=lambda:
        _get_config_value('SUPPLY_CALCULATION_METHOD', 'SUPPLY_CALCULATION_METHOD',
                         'PRECISE', _LEGACY_SETTINGS)
    )
    
    # ========================================================================
    # TOKENS CONFIGURATION
    # ========================================================================
    
    TOKENS: Dict[str, TokenConfig] = field(default_factory=lambda: {
        'UBEC': TokenConfig(
            code='UBEC',
            issuer=os.getenv('UBEC_ISSUER', 
                           'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN'),
            minimum_transaction=Decimal('10.0'),
            distribution_general=Decimal('0.65'),
            distribution_stewardship=Decimal('0.30'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECrc': TokenConfig(
            code='UBECrc',
            issuer=os.getenv('UBECrc_ISSUER',
                           'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC'),
            minimum_transaction=Decimal('5.0'),
            distribution_general=Decimal('0.70'),
            distribution_stewardship=Decimal('0.25'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECgpi': TokenConfig(
            code='UBECgpi',
            issuer=os.getenv('UBECgpi_ISSUER',
                           'GCPU3LUGRIYLWMPOQEEGIL2HI5Z637PQVK42Z5PYRRQMPFDTNT5SUBEC'),
            minimum_transaction=Decimal('100.0'),
            distribution_general=Decimal('0.80'),
            distribution_stewardship=Decimal('0.15'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECtt': TokenConfig(
            code='UBECtt',
            issuer=os.getenv('UBECtt_ISSUER',
                           'GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC'),
            minimum_transaction=Decimal('1.0'),
            distribution_general=Decimal('0.75'),
            distribution_stewardship=Decimal('0.20'),
            distribution_admin=Decimal('0.05')
        )
    })
    
    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================
    
    DATABASE_URL: str = field(default_factory=lambda: os.getenv(
        'DATABASE_URL',
        'postgresql://ubec_app:App252010!@#@localhost/ubec'
    ))
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    RATE_LIMIT_CALLS: int = field(default_factory=lambda: int(
        os.getenv('RATE_LIMIT_CALLS', '100')
    ))
    
    RATE_LIMIT_PERIOD: int = field(default_factory=lambda: int(
        os.getenv('RATE_LIMIT_PERIOD', '60')
    ))
    
    # ========================================================================
    # SYNC SETTINGS
    # ========================================================================
    
    SYNC_BATCH_SIZE: int = field(default_factory=lambda: int(
        os.getenv('SYNC_BATCH_SIZE', '200')
    ))
    
    SYNC_BATCH_DELAY: float = field(default_factory=lambda: float(
        os.getenv('SYNC_BATCH_DELAY', '1.0')
    ))
    
    SYNC_MAX_ACCOUNTS: int = field(default_factory=lambda: int(
        os.getenv('SYNC_MAX_ACCOUNTS', '1000')
    ))
    
    # ========================================================================
    # HOLONIC EVALUATION
    # ========================================================================
    
    HOLONIC_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        'autonomy_integration': 0.25,
        'multi_scale': 0.20,
        'regenerative': 0.25,
        'network': 0.15,
        'ubuntu': 0.15
    })
    
    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    
    LOG_LEVEL: str = field(default_factory=lambda: _get_config_value(
        'LOG_LEVEL', 'LOG_LEVEL', 'INFO', _LEGACY_SETTINGS
    ))
    
    LOG_FORMAT: str = field(default_factory=lambda: _get_config_value(
        'LOG_FORMAT', 'LOG_FORMAT',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        _LEGACY_SETTINGS
    ))
    
    LOG_FILE: str = field(default_factory=lambda: _get_config_value(
        'LOG_FILE', 'LOG_FILE', 'ubec_protocol.log', _LEGACY_SETTINGS
    ))
    
    # ========================================================================
    # COMPUTED PROPERTIES
    # ========================================================================
    
    @property
    def horizon_url(self) -> str:
        """
        Get Horizon URL for current network.
        
        Returns:
            str: Horizon URL
        """
        return self.HORIZON_URL
    
    # ========================================================================
    # PUBLIC METHODS
    # ========================================================================
    
    def get_token_config(self, token_code: str) -> TokenConfig:
        """
        Get configuration for a specific token.
        
        Args:
            token_code: Token code (e.g., 'UBEC', 'UBECrc')
        
        Returns:
            TokenConfig: Token configuration
        
        Raises:
            ValueError: If token code is unknown
        
        Example:
            config = Config()
            ubec_cfg = config.get_token_config('UBEC')
            print(f"Issuer: {ubec_cfg.issuer}")
        """
        if token_code not in self.TOKENS:
            available = ', '.join(self.TOKENS.keys())
            raise ValueError(
                f"Unknown token: {token_code}. Available tokens: {available}"
            )
        return self.TOKENS[token_code]
    
    def validate(self) -> bool:
        """
        Validate that configuration is complete and correct.
        
        Returns:
            bool: True if configuration is valid
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Check critical configuration
        if not self.UBEC_ISSUER:
            raise ValueError("UBEC_ISSUER is not configured")
        
        if not self.HORIZON_URL:
            raise ValueError("HORIZON_URL is not configured")
        
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not configured")
        
        # Validate token configurations
        for token_code, token_cfg in self.TOKENS.items():
            if not token_cfg.issuer:
                raise ValueError(f"Token {token_code} has no issuer configured")
        
        logger.info("Configuration validation passed")
        return True
    
    def display(self) -> Dict[str, Any]:
        """
        Display current configuration values (safe for logging).
        
        Returns:
            dict: Configuration as dictionary (sensitive values masked)
        """
        return {
            'NETWORK': self.NETWORK,
            'HORIZON_URL': self.HORIZON_URL,
            'UBEC_CODE': self.UBEC_CODE,
            'UBEC_ISSUER': self.UBEC_ISSUER[:10] + '...' if self.UBEC_ISSUER else 'None',
            'TOKEN_COUNT': len(self.TOKENS),
            'TOKENS': list(self.TOKENS.keys()),
            'LOG_LEVEL': self.LOG_LEVEL,
            'DATABASE_CONFIGURED': bool(self.DATABASE_URL),
            'RATE_LIMIT_CALLS': self.RATE_LIMIT_CALLS,
            'RATE_LIMIT_PERIOD': self.RATE_LIMIT_PERIOD,
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check configuration service health.
        
        This is a synchronous health check since config has no I/O operations.
        
        Returns:
            dict: Health status with configuration validation
        
        Example:
            config = Config()
            health = config.health_check()
            if health['status'] == 'healthy':
                print("Configuration is valid")
        """
        from datetime import datetime
        
        health = {
            'status': 'healthy',
            'message': 'config operational',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'initialized': True,
                'config_loaded': True,
                'num_tokens': len(self.TOKENS),
                'tokens_configured': list(self.TOKENS.keys()),
                'database_configured': bool(self.DATABASE_URL),
                'network': self.NETWORK,
                'horizon_configured': bool(self.HORIZON_URL),
            }
        }
        
        # Perform validation checks
        try:
            self.validate()
            health['details']['validation'] = 'passed'
        except ValueError as e:
            health['status'] = 'unhealthy'
            health['message'] = f'config validation failed: {str(e)}'
            health['details']['validation'] = 'failed'
            health['details']['validation_error'] = str(e)
        
        return health


# ============================================================================
# LEGACY COMPATIBILITY CLASS
# ============================================================================

class GlobalConfig:
    """
    Legacy-style configuration class for backward compatibility.
    
    This class provides the same interface as Config but wraps the Config
    dataclass. Used by legacy modules that expect a class-based config.
    
    New code should use Config directly via the service registry.
    """
    
    def __init__(self):
        """Initialize GlobalConfig by wrapping a Config instance."""
        self._config = Config()
        logger.debug("GlobalConfig initialized (legacy compatibility mode)")
    
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
        """Alias for LOG_FILE for backward compatibility."""
        return self._config.LOG_FILE
    
    # Methods
    def get_token_config(self, token_code: str) -> TokenConfig:
        """Get configuration for specific token."""
        return self._config.get_token_config(token_code)
    
    def validate(self) -> bool:
        """Validate configuration."""
        return self._config.validate()
    
    def display(self) -> Dict[str, Any]:
        """Display configuration."""
        return self._config.display()
    
    def health_check(self) -> Dict[str, Any]:
        """Check configuration health."""
        return self._config.health_check()


# ============================================================================
# SERVICE FACTORY (Principle #2: Service Pattern)
# ============================================================================

def create_config_service(**kwargs) -> Config:
    """
    Factory function to create configuration service instance.
    
    This is the PREFERRED way to instantiate the config service,
    following Principle #2 (Service Pattern).
    
    Args:
        **kwargs: Optional configuration overrides (not typically used)
    
    Returns:
        Config: Configured instance
    
    Example:
        # Via service registry (preferred)
        from core.service_registry import registry
        config = registry.get_initialized('config')
        
        # Direct instantiation
        from config.config import create_config_service
        config = create_config_service()
    
    Note:
        Configuration is loaded from environment variables and .env file.
        Make sure your .env file is properly configured before calling.
    """
    config_instance = Config()
    logger.info("Config service created via factory")
    return config_instance


def create_legacy_config_service(**kwargs) -> GlobalConfig:
    """
    Factory function to create legacy GlobalConfig instance.
    
    Use this for backward compatibility with legacy code that expects
    GlobalConfig instead of Config.
    
    Args:
        **kwargs: Optional configuration overrides
    
    Returns:
        GlobalConfig: Legacy-style config instance
    """
    config_instance = GlobalConfig()
    logger.info("Legacy config service created via factory")
    return config_instance


# ============================================================================
# MODULE-LEVEL INSTANCES (For backward compatibility)
# ============================================================================

# Global instances for legacy code
# New code should use the factory function and service registry
config = Config()
global_config = GlobalConfig()

logger.info(f"Configuration loaded: {config.NETWORK} network, {len(config.TOKENS)} tokens")


# ============================================================================
# PUBLIC INTERFACE
# ============================================================================

__all__ = [
    # Main classes
    'Config',
    'GlobalConfig',
    'TokenConfig',
    # Factory functions (preferred)
    'create_config_service',
    'create_legacy_config_service',
    # Legacy instances (backward compatibility)
    'config',
    'global_config',
]


# ============================================================================
# STANDALONE EXECUTION PREVENTION (Principle #2: Service Pattern)
# ============================================================================

if __name__ == "__main__":
    # Allow validation when run directly
    print("=" * 80)
    print("UBEC Configuration Service")
    print("=" * 80)
    
    try:
        test_config = Config()
        test_config.validate()
        
        print("\n✓ Configuration validation PASSED")
        print("\nConfiguration details:")
        for key, value in test_config.display().items():
            print(f"  {key}: {value}")
        
        print("\nHealth check:")
        health = test_config.health_check()
        print(f"  Status: {health['status']}")
        print(f"  Message: {health['message']}")
        
    except Exception as e:
        print(f"\n✗ Configuration validation FAILED: {e}")
        exit(1)
