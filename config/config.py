#!/usr/bin/env python3
# config/config.py
"""
UBEC Protocol - Configuration Compatibility Wrapper
====================================================
Provides property-style access wrapper around ConfigurationService.

This module bridges the gap between the database-backed ConfigurationService
(which uses dictionary-style access) and code expecting property-style access.

The ConfigurationService from settings.py is the actual implementation.
This module provides a property-based interface for backward compatibility.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅  All 12 principles - delegates to ConfigurationService
    ✅  Principle #7: Health check properly exposed via async method
    ✅  Principle #11: Comprehensive documentation
    ✅  Principle #12: Single wrapper, no duplication
════════════════════════════════════════════════════════════════════════════

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.

Version: 3.1.0 (Compatibility Wrapper + Health Check Fix)
Date: October 16, 2025

Key Changes:
    - Wraps ConfigurationService for property-style access
    - Properly exposes async health_check() method
    - Maintains backward compatibility with GlobalConfig
    - All actual config logic in settings.py (single source)
"""

import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from config.settings import ConfigurationService, get_system_config

logger = logging.getLogger(__name__)


class Config:
    """
    Property-style configuration wrapper around ConfigurationService.
    
    This class provides property-based access to configuration while
    delegating to the database-backed ConfigurationService.
    
    The ConfigurationService is the actual implementation that loads
    from the database. This is just a compatibility wrapper.
    
    Design Pattern:
        - ConfigurationService (settings.py): Actual implementation
        - Config (this file): Property-style wrapper
        - Registry discovers health_check() on this wrapper
    
    Usage:
        # Via factory (creates ConfigurationService internally)
        config = await create_config_service(db_manager)
        
        # Property access
        url = config.HORIZON_URL
        issuer = config.UBEC_ISSUER
        
        # Health check (async)
        health = await config.health_check()
    """
    
    def __init__(self, config_service: ConfigurationService):
        """
        Initialize config wrapper.
        
        Args:
            config_service: Initialized ConfigurationService instance
        """
        self._config = config_service
        logger.debug("Config property wrapper initialized")
    
    # ========================================================================
    # NETWORK PROPERTIES
    # ========================================================================
    
    @property
    def NETWORK(self) -> str:
        """Stellar network: 'mainnet' or 'testnet'."""
        return self._config.get('network', 'mainnet')
    
    @property
    def HORIZON_URL(self) -> str:
        """Horizon API URL."""
        return self._config.get('horizon_url', 'https://horizon.stellar.org')
    
    @property
    def horizon_url(self) -> str:
        """Alias for HORIZON_URL (backward compatibility)."""
        return self.HORIZON_URL
    
    # ========================================================================
    # UBEC TOKEN PROPERTIES
    # ========================================================================
    
    @property
    def UBEC_CODE(self) -> str:
        """UBEC token code."""
        return self._config.get('ubec_code', 'UBEC')
    
    @property
    def UBEC_ISSUER(self) -> str:
        """UBEC issuer address."""
        return self._config.get('ubec_issuer', '')
    
    # ========================================================================
    # SUPPLY PROPERTIES
    # ========================================================================
    
    @property
    def FALLBACK_SUPPLY(self) -> Decimal:
        """Fallback supply value."""
        val = self._config.get('fallback_supply', '191766039.00')
        return Decimal(str(val))
    
    @property
    def ALWAYS_LOAD_FROM_NETWORK(self) -> bool:
        """Whether to always load from network."""
        return self._config.get('always_load_from_network', True)
    
    # ========================================================================
    # DISTRIBUTION PROPERTIES
    # ========================================================================
    
    @property
    def TARGET_DISTRIBUTION(self) -> Dict[str, Decimal]:
        """Target distribution percentages."""
        return {
            'general': Decimal('0.65'),
            'stewardship': Decimal('0.30'),
            'administration': Decimal('0.05')
        }
    
    @property
    def ACCOUNTS(self) -> Dict[str, Any]:
        """Managed accounts."""
        return {}
    
    # ========================================================================
    # OPERATION PROPERTIES
    # ========================================================================
    
    @property
    def REBALANCE_THRESHOLD(self) -> Decimal:
        """Rebalance threshold."""
        val = self._config.get('rebalance_threshold', '0.01')
        return Decimal(str(val))
    
    @property
    def CHECK_INTERVAL(self) -> int:
        """Check interval in seconds."""
        return int(self._config.get('check_interval', 3600))
    
    # ========================================================================
    # SUPPLY CALCULATION PROPERTIES
    # ========================================================================
    
    @property
    def SUPPLY_CHECK_INTERVAL(self) -> int:
        """Supply check interval."""
        return int(self._config.get('supply_check_interval', 86400))
    
    @property
    def SUPPLY_SAFETY_FACTOR(self) -> Decimal:
        """Supply safety factor."""
        val = self._config.get('supply_safety_factor', '0.02')
        return Decimal(str(val))
    
    @property
    def SUPPLY_CALCULATION_METHOD(self) -> str:
        """Supply calculation method."""
        return self._config.get('supply_calculation_method', 'PRECISE')
    
    # ========================================================================
    # DATABASE PROPERTIES
    # ========================================================================
    
    @property
    def DATABASE_URL(self) -> str:
        """Database connection URL."""
        return self._config.get('database_url', '')
    
    # ========================================================================
    # RATE LIMITING PROPERTIES
    # ========================================================================
    
    @property
    def RATE_LIMIT_CALLS(self) -> int:
        """Rate limit calls."""
        return int(self._config.get('rate_limit_calls', 100))
    
    @property
    def RATE_LIMIT_PERIOD(self) -> int:
        """Rate limit period."""
        return int(self._config.get('rate_limit_period', 60))
    
    # ========================================================================
    # SYNC PROPERTIES
    # ========================================================================
    
    @property
    def SYNC_BATCH_SIZE(self) -> int:
        """Sync batch size."""
        return int(self._config.get('sync_batch_size', 200))
    
    @property
    def SYNC_BATCH_DELAY(self) -> float:
        """Sync batch delay."""
        return float(self._config.get('sync_batch_delay', 1.0))
    
    @property
    def SYNC_MAX_ACCOUNTS(self) -> int:
        """Max accounts to sync."""
        return int(self._config.get('sync_max_accounts', 1000))
    
    # ========================================================================
    # HOLONIC PROPERTIES
    # ========================================================================
    
    @property
    def HOLONIC_WEIGHTS(self) -> Dict[str, float]:
        """Holonic evaluation weights."""
        return {
            'autonomy_integration': 0.25,
            'multi_scale': 0.20,
            'regenerative': 0.25,
            'network': 0.15,
            'ubuntu': 0.15
        }
    
    # ========================================================================
    # LOGGING PROPERTIES
    # ========================================================================
    
    @property
    def LOG_LEVEL(self) -> str:
        """Log level."""
        return self._config.get('log_level', 'INFO')
    
    @property
    def LOG_FORMAT(self) -> str:
        """Log format."""
        return self._config.get('log_format', 
                               '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    @property
    def LOG_FILE(self) -> str:
        """Log file path."""
        return self._config.get('log_file', 'ubec_protocol.log')
    
    # ========================================================================
    # PUBLIC METHODS
    # ========================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with optional default.
        
        Args:
            key: Configuration key
            default: Default value if not found
        
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def get_token_config(self, token_code: str) -> Dict[str, Any]:
        """
        Get token configuration.
        
        Returns a dict with token info since ConfigurationService
        doesn't have TokenConfig objects.
        
        Args:
            token_code: Token code (e.g., 'UBEC', 'UBECrc')
        
        Returns:
            Dict with 'code' and 'issuer' keys
        
        Example:
            cfg = config.get_token_config('UBEC')
            print(cfg['issuer'])
        """
        issuer_key = f'{token_code.lower()}_issuer'
        return {
            'code': token_code,
            'issuer': self._config.get(issuer_key, self.UBEC_ISSUER)
        }
    
    # ========================================================================
    # HEALTH CHECK (Principle #7: Per-Asset Monitoring)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on configuration service.
        
        This is an ASYNC method that delegates to ConfigurationService.
        It will be discovered by the service registry health check.
        
        Implements Principle #7 (Per-Asset Monitoring).
        
        Returns:
            Health status dictionary:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'timestamp': str,
                'details': {...}
            }
        
        Example:
            health = await config.health_check()
            if health['status'] == 'healthy':
                print("Config is loaded and valid")
        """
        # Delegate to ConfigurationService health_check
        return await self._config.health_check()
    
    async def reload(self) -> None:
        """
        Reload configuration from database.
        
        Example:
            # After database update
            await config.reload()
        """
        await self._config.reload()
    
    async def close(self) -> None:
        """
        Close configuration service.
        
        ConfigurationService doesn't need explicit cleanup,
        but we provide this for consistency with other services.
        """
        # No-op for config, but maintains interface consistency
        pass


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

class GlobalConfig:
    """
    Legacy GlobalConfig class for backward compatibility.
    
    This wraps the Config wrapper which wraps ConfigurationService.
    It's kept for any legacy code that imports GlobalConfig.
    
    DEPRECATED: Use Config via service registry instead.
    """
    
    def __init__(self):
        """Initialize GlobalConfig."""
        self._config: Optional[Config] = None
        logger.warning(
            "GlobalConfig is deprecated. "
            "Use: config = await registry.get('config')"
        )
    
    def _ensure_config(self):
        """Ensure config is set."""
        if self._config is None:
            raise RuntimeError(
                "GlobalConfig not initialized. "
                "Use Config via service registry instead."
            )
    
    def __getattr__(self, name: str) -> Any:
        """Delegate all attribute access to Config."""
        self._ensure_config()
        return getattr(self._config, name)


# ============================================================================
# SERVICE FACTORY (Principle #2: Service Pattern)
# ============================================================================

async def create_config_service(db_manager: Any) -> Config:
    """
    Factory function to create Config wrapper.
    
    This creates a ConfigurationService from settings.py and wraps it
    in a Config object for property-style access.
    
    Following Principle #2 (Service Pattern) - factory-based instantiation.
    
    Args:
        db_manager: AsyncDatabaseManager instance
    
    Returns:
        Config wrapper around ConfigurationService
    
    Example:
        # Via service registry (preferred)
        from core.service_registry import registry
        config = await registry.get('config')
        
        # Direct instantiation
        config = await create_config_service(db_manager)
        
        # Use with properties
        url = config.HORIZON_URL
        issuer = config.UBEC_ISSUER
        
        # Health check works!
        health = await config.health_check()
        print(f"Status: {health['status']}")
    
    Note:
        The actual configuration loading is done by ConfigurationService
        from settings.py. This wrapper just provides property-style access.
    """
    logger.info("Creating config service...")
    
    # Create ConfigurationService (actual implementation)
    config_service = await get_system_config(db_manager)
    
    # Wrap it for property access
    config_wrapper = Config(config_service)
    
    logger.info("✓ Config service created (ConfigurationService + property wrapper)")
    
    return config_wrapper


# ============================================================================
# PUBLIC INTERFACE
# ============================================================================

__all__ = [
    'Config',
    'GlobalConfig',  # Backward compatibility
    'create_config_service',
]


# ============================================================================
# STANDALONE EXECUTION PREVENTION (Principle #2: Service Pattern)
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("UBEC Configuration Wrapper")
    print("=" * 80)
    print("\nThis module provides property-style access to ConfigurationService.")
    print("The actual configuration is loaded from database via settings.py")
    print("\nUsage:")
    print("  config = await create_config_service(db_manager)")
    print("  url = config.HORIZON_URL  # Property access")
    print("  health = await config.health_check()  # Async health check")
    print("\nThe health_check() method will be discovered by service registry.")
    print("=" * 80)
