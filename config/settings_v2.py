#!/usr/bin/env python3
"""
UBEC Protocol - System Configuration (Database-Backed)
=======================================================
Configuration management using database as Single Source of Truth.

This module provides configuration access by loading settings from the
`system_settings` database table, following Design Principle #4.

Design Principles Applied:
- ✅ Principle #4: Single Source of Truth (Database is authoritative)
- ✅ Principle #5: Strict Async Operations (All DB access uses async/await)
- ✅ Principle #7: Per-Asset Monitoring (Health checks included)
- ✅ Principle #8: No Duplicate Configuration (Each parameter defined once in DB)
- ✅ Principle #11: Comprehensive Documentation (Full docstrings)
- ✅ Principle #12: Method Singularity (One factory function)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our 
    decisions and recommendations. This project was made possible with the 
    assistance of Claude and Anthropic PBC.

Version: 2.1.0
Date: October 16, 2025
"""

import os
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SystemConfig:
    """
    System configuration loaded from database.
    
    This class loads configuration from the system_settings table,
    implementing the Single Source of Truth principle (Principle #4).
    All configuration parameters are stored in the database and loaded
    at runtime with caching support.
    
    Features:
    - Async initialization from database
    - 5-minute cache with TTL
    - Health check monitoring (Principle #7)
    - Fallback to environment variables
    - Type conversion (string, integer, decimal, boolean)
    
    Usage:
        # Via factory function (recommended)
        config = await get_system_config(db_manager)
        print(config.HORIZON_URL)
        
        # Direct instantiation
        config = SystemConfig(db_manager)
        await config.initialize()
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize configuration manager.
        
        Args:
            db_manager: AsyncDatabaseManager instance (optional)
        """
        self._db = db_manager
        self._initialized = False
        self._settings: Dict[str, Any] = {}
        self._last_loaded: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
    
    async def initialize(self) -> None:
        """
        Load configuration from database.
        
        This is the ONLY method that loads configuration.
        Implements Principle #12: Method Singularity.
        
        Raises:
            RuntimeError: If database connection fails critically
        """
        if self._initialized and self._cache_valid():
            logger.debug("Configuration cache still valid")
            return
        
        try:
            if self._db:
                await self._load_from_database()
            else:
                logger.warning("No database manager provided - loading from environment")
                self._load_from_environment()
            
            self._initialized = True
            self._last_loaded = datetime.now()
            logger.info(f"✓ Configuration loaded: {len(self._settings)} settings")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.warning("Falling back to environment variables")
            self._load_from_environment()
            self._initialized = True
            self._last_loaded = datetime.now()
    
    def _cache_valid(self) -> bool:
        """Check if configuration cache is still valid."""
        if not self._last_loaded:
            return False
        return datetime.now() - self._last_loaded < self._cache_ttl
    
    async def _load_from_database(self) -> None:
        """
        Load configuration from database (SINGLE SOURCE OF TRUTH).
        
        Implements Principle #4: Database as authoritative source.
        """
        logger.info("Loading configuration from database...")
        
        # Load all active settings
        query = """
            SELECT 
                setting_key, 
                setting_value, 
                setting_type,
                category
            FROM system_settings
            WHERE is_active = TRUE
            ORDER BY category, setting_key
        """
        
        rows = await self._db.fetch_all(query)
        
        if not rows:
            raise ValueError("No active settings found in database")
        
        # Convert database rows to typed settings
        for row in rows:
            key = row['setting_key']
            value = row['setting_value']
            setting_type = row.get('setting_type', 'string')
            
            # Type conversion based on setting_type
            try:
                if setting_type == 'integer':
                    value = int(value)
                elif setting_type == 'float':
                    value = float(value)
                elif setting_type == 'decimal':
                    value = Decimal(value)
                elif setting_type == 'boolean':
                    value = str(value).lower() in ('true', '1', 'yes', 'on')
                # else: keep as string
                
                self._settings[key] = value
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to convert setting {key}={value} to {setting_type}: {e}")
                self._settings[key] = value  # Keep as string
        
        logger.info(f"Loaded {len(self._settings)} configuration settings from database")
    
    def _load_from_environment(self) -> None:
        """
        Load configuration from environment variables as fallback.
        
        Only used when database is unavailable (emergency fallback).
        """
        logger.warning("Loading configuration from environment (fallback mode)")
        
        self._settings = {
            # Network
            'network': os.getenv('UBEC_NETWORK', 'testnet'),
            'horizon_url': os.getenv('HORIZON_URL', 'https://horizon-testnet.stellar.org'),
            'network_passphrase': os.getenv('NETWORK_PASSPHRASE', 'Test SDF Network ; September 2015'),
            
            # Tokens
            'ubec_code': os.getenv('UBEC_CODE', 'UBEC'),
            'ubec_issuer': os.getenv('UBEC_ISSUER', ''),
            'ubecrc_code': os.getenv('UBECRC_CODE', 'UBECrc'),
            'ubecrc_issuer': os.getenv('UBECRC_ISSUER', ''),
            'ubecgpi_code': os.getenv('UBECGPI_CODE', 'UBECgpi'),
            'ubecgpi_issuer': os.getenv('UBECGPI_ISSUER', ''),
            'ubectt_code': os.getenv('UBECTT_CODE', 'UBECtt'),
            'ubectt_issuer': os.getenv('UBECTT_ISSUER', ''),
            
            # Supply
            'fallback_supply': Decimal('191766039.00'),
            'always_load_from_network': True,
            
            # Distribution
            'distribution_general': Decimal('0.65'),
            'distribution_stewardship': Decimal('0.30'),
            'distribution_administration': Decimal('0.05'),
            'rebalance_threshold': Decimal('0.01'),
            'check_interval': 3600,
            
            # Monitoring
            'supply_check_interval': 86400,
            'supply_safety_factor': Decimal('0.02'),
            'supply_calculation_method': 'PRECISE',
            
            # Logging
            'log_file': 'ubec_distribution_manager.log',
            'log_level': 'INFO',
            'log_format': '%(asctime)s - %(levelname)s - %(message)s',
            'log_file_path': 'logs/ubec_distribution_manager.log',
            'log_date_format': '%Y-%m-%d %H:%M:%S',
            'log_max_bytes': 10485760,
            'log_backup_count': 5,
        }
    
    async def reload(self) -> None:
        """
        Force reload configuration from database.
        
        Useful for picking up configuration changes without restarting.
        """
        self._last_loaded = None
        await self.initialize()
    
    # ========================================================================
    # CONFIGURATION ACCESS
    # ========================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self._initialized:
            raise RuntimeError(
                "Configuration not initialized. Call await config.initialize() first."
            )
        return self._settings.get(key, default)
    
    def __getattr__(self, name: str) -> Any:
        """
        Allow attribute-style access to settings.
        
        Supports both UPPER_CASE and lower_case keys.
        Example: config.HORIZON_URL or config.horizon_url
        """
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
        # Try exact match first
        if name in self._settings:
            return self._settings[name]
        
        # Try lowercase version
        lower_name = name.lower()
        if lower_name in self._settings:
            return self._settings[lower_name]
        
        # Try with underscore converted to dot
        alt_name = name.replace('_', '.')
        if alt_name in self._settings:
            return self._settings[alt_name]
        
        raise AttributeError(f"Configuration setting '{name}' not found")
    
    # ========================================================================
    # PROPERTY ACCESSORS (for backward compatibility)
    # ========================================================================
    
    @property
    def NETWORK(self) -> str:
        """Get Stellar network (testnet or mainnet)."""
        return self.get('network', 'testnet')
    
    @property
    def HORIZON_URL(self) -> str:
        """Get Horizon API endpoint URL."""
        return self.get('horizon_url', 'https://horizon-testnet.stellar.org')
    
    @property
    def PUBLIC_NETWORK_PASSPHRASE(self) -> str:
        """Get Stellar network passphrase."""
        return self.get('network_passphrase', 'Test SDF Network ; September 2015')
    
    @property
    def UBEC_CODE(self) -> str:
        """Get UBEC token code."""
        return self.get('ubec_code', 'UBEC')
    
    @property
    def UBEC_ISSUER(self) -> str:
        """Get UBEC token issuer address."""
        return self.get('ubec_issuer', '')
    
    @property
    def UBECrc_CODE(self) -> str:
        """Get UBECrc (Water) token code."""
        return self.get('ubecrc_code', 'UBECrc')
    
    @property
    def UBECrc_ISSUER(self) -> str:
        """Get UBECrc token issuer address."""
        return self.get('ubecrc_issuer', '')
    
    @property
    def UBECgpi_CODE(self) -> str:
        """Get UBECgpi (Earth) token code."""
        return self.get('ubecgpi_code', 'UBECgpi')
    
    @property
    def UBECgpi_ISSUER(self) -> str:
        """Get UBECgpi token issuer address."""
        return self.get('ubecgpi_issuer', '')
    
    @property
    def UBECtt_CODE(self) -> str:
        """Get UBECtt (Fire) token code."""
        return self.get('ubectt_code', 'UBECtt')
    
    @property
    def UBECtt_ISSUER(self) -> str:
        """Get UBECtt token issuer address."""
        return self.get('ubectt_issuer', '')
    
    @property
    def FALLBACK_SUPPLY(self) -> Decimal:
        """Get fallback supply if network unavailable."""
        return Decimal(self.get('fallback_supply', '191766039.00'))
    
    @property
    def ALWAYS_LOAD_FROM_NETWORK(self) -> bool:
        """Get flag for always loading supply from network."""
        return self.get('always_load_from_network', True)
    
    @property
    def TARGET_DISTRIBUTION(self) -> Dict[str, Decimal]:
        """Get target distribution percentages."""
        return {
            'general': Decimal(self.get('distribution_general', '0.65')),
            'stewardship': Decimal(self.get('distribution_stewardship', '0.30')),
            'administration': Decimal(self.get('distribution_administration', '0.05'))
        }
    
    @property
    def ACCOUNTS(self) -> Dict[str, Any]:
        """
        Get account addresses.
        
        Note: Currently loads from environment as fallback.
        TODO: Move to database when account management is implemented.
        """
        return {
            'general': os.getenv('GENERAL_PUBLIC_KEY', ''),
            'administration': os.getenv('ADMIN_PUBLIC_KEY', ''),
            'stewardship': [
                os.getenv('STEWARD_MGMT_PUBLIC_KEY', ''),
                os.getenv('STEWARD_INFRA_PUBLIC_KEY', ''),
                os.getenv('STEWARD_LIQUIDITY_PUBLIC_KEY', ''),
            ]
        }
    
    @property
    def REBALANCE_THRESHOLD(self) -> Decimal:
        """Get distribution rebalance threshold."""
        return Decimal(self.get('rebalance_threshold', '0.01'))
    
    @property
    def CHECK_INTERVAL(self) -> int:
        """Get check interval in seconds."""
        return int(self.get('check_interval', 3600))
    
    @property
    def SUPPLY_CHECK_INTERVAL(self) -> int:
        """Get supply check interval in seconds."""
        return int(self.get('supply_check_interval', 86400))
    
    @property
    def SUPPLY_SAFETY_FACTOR(self) -> Decimal:
        """Get supply calculation safety factor."""
        return Decimal(self.get('supply_safety_factor', '0.02'))
    
    @property
    def SUPPLY_CALCULATION_METHOD(self) -> str:
        """Get supply calculation method (PRECISE or ESTIMATED)."""
        return self.get('supply_calculation_method', 'PRECISE')
    
    @property
    def LOG_FILE(self) -> str:
        """Get log file name."""
        return self.get('log_file', 'ubec_distribution_manager.log')
    
    @property
    def LOG_LEVEL(self) -> str:
        """Get logging level."""
        return self.get('log_level', 'INFO')
    
    @property
    def LOG_FORMAT(self) -> str:
        """Get log format string."""
        return self.get('log_format', '%(asctime)s - %(levelname)s - %(message)s')
    
    @property
    def LOG_FILE_PATH(self) -> str:
        """Get log file path."""
        return self.get('log_file_path', 'logs/ubec_distribution_manager.log')
    
    @property
    def LOG_DATE_FORMAT(self) -> str:
        """Get log date format."""
        return self.get('log_date_format', '%Y-%m-%d %H:%M:%S')
    
    @property
    def LOG_MAX_BYTES(self) -> int:
        """Get log file max size in bytes."""
        return int(self.get('log_max_bytes', 10485760))
    
    @property
    def LOG_BACKUP_COUNT(self) -> int:
        """Get number of log backup files to keep."""
        return int(self.get('log_backup_count', 5))
    
    # ========================================================================
    # HEALTH CHECK (Principle #7: Per-Asset Monitoring)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check configuration service health.
        
        Implements Principle #7: Per-Asset Monitoring with health checks.
        
        Returns:
            Health status dictionary with:
            - status: 'healthy' | 'degraded' | 'unhealthy'
            - message: Human-readable status message
            - details: Additional health metrics
        """
        return {
            'status': 'healthy' if self._initialized else 'unhealthy',
            'message': 'Configuration loaded' if self._initialized else 'Not initialized',
            'details': {
                'initialized': self._initialized,
                'settings_count': len(self._settings),
                'source': 'database' if self._db else 'environment',
                'cache_valid': self._cache_valid(),
                'last_loaded': self._last_loaded.isoformat() if self._last_loaded else None,
                'cache_ttl_minutes': self._cache_ttl.total_seconds() / 60,
                'has_ubec_code': 'ubec_code' in self._settings,
                'has_horizon_url': 'horizon_url' in self._settings,
                'has_ubec_issuer': 'ubec_issuer' in self._settings and bool(self._settings.get('ubec_issuer'))
            }
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def validate(self) -> bool:
        """
        Validate configuration is complete and correct.
        
        Returns:
            True if configuration is valid
        """
        if not self._initialized:
            logger.error("Configuration not initialized")
            return False
        
        # Check critical settings
        required = ['ubec_issuer', 'horizon_url', 'ubec_code']
        
        for key in required:
            if key not in self._settings or not self._settings[key]:
                logger.error(f"Missing required configuration: {key}")
                return False
        
        return True
    
    def display(self) -> Dict[str, Any]:
        """
        Display current configuration (safe for logging).
        
        Returns:
            Dictionary of configuration values (sensitive data redacted)
        """
        return {
            'network': self.get('network', 'unknown'),
            'horizon_url': self.get('horizon_url', 'unknown'),
            'ubec_code': self.get('ubec_code', 'unknown'),
            'ubec_issuer': self.get('ubec_issuer', 'unknown')[:10] + '...' 
                if self.get('ubec_issuer') else 'not set',
            'log_level': self.get('log_level', 'INFO'),
            'settings_count': len(self._settings),
            'initialized': self._initialized,
            'source': 'database' if self._db else 'environment',
            'cache_valid': self._cache_valid()
        }


# ============================================================================
# FACTORY FUNCTION (Principle #12: Method Singularity)
# ============================================================================

async def get_system_config(db_manager) -> SystemConfig:
    """
    Factory function to create and initialize system configuration.
    
    This is the ONLY way to create a SystemConfig instance properly.
    Implements Principle #12: Method Singularity.
    
    Args:
        db_manager: AsyncDatabaseManager instance
        
    Returns:
        Initialized SystemConfig instance
        
    Usage:
        # In service registry factory
        config = await get_system_config(db_manager)
        
    Note:
        This function creates a new instance each time. If you need
        a singleton pattern, manage it at the service registry level.
    """
    config = SystemConfig(db_manager)
    await config.initialize()
    
    if not config.validate():
        logger.error("Configuration validation failed")
        # Don't raise - allow fallback mode to work
    
    return config


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'SystemConfig',
    'get_system_config',
]
