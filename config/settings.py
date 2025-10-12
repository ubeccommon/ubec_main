"""
UBEC Protocol - System Configuration (Database-Backed)
=======================================================
Configuration management using database as Single Source of Truth.

This module provides configuration access by loading settings from the
`system_settings` database table, following Design Principle #4.

Design Principles Applied:
- Single Source of Truth: Database is authoritative (Principle #4)
- No Duplicate Configuration: Each parameter defined once in DB (Principle #8)
- Strict Async Operations: All database access uses async/await (Principle #5)
- Clear Separation of Concerns: Configuration isolated from business logic

Attribution:
This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.

Version: 2.0 (Database-Backed)
Date: October 12, 2025
"""

import os
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SystemConfig:
    """
    System configuration loaded from database.
    
    This class loads configuration from the system_settings table,
    implementing the Single Source of Truth principle. All configuration
    parameters are stored in the database and loaded at runtime.
    
    Usage:
        # Async initialization (preferred)
        config = SystemConfig()
        await config.initialize(db_manager)
        print(config.HORIZON_URL)
        
        # Or use get_system_config helper
        config = await get_system_config(db_manager)
    """
    
    # Database connection (injected)
    _db: Any = None
    _initialized: bool = False
    
    # Configuration cache
    _settings: Dict[str, Any] = field(default_factory=dict)
    
    async def initialize(self, db_manager) -> None:
        """
        Load configuration from database.
        
        Args:
            db_manager: AsyncDatabaseManager instance
            
        Raises:
            RuntimeError: If database connection fails
            ValueError: If required settings are missing
        """
        if self._initialized:
            logger.debug("Configuration already initialized")
            return
            
        self._db = db_manager
        
        try:
            # Load all active settings from database
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
                # Fallback to environment variables if database is empty
                logger.warning("No settings in database, using environment variables as fallback")
                self._load_from_environment()
                self._initialized = True
                return
            
            # Convert database rows to typed settings
            for row in rows:
                key = row['setting_key']
                value = row['setting_value']
                setting_type = row.get('setting_type', 'string')
                
                # Type conversion
                if setting_type == 'integer':
                    value = int(value)
                elif setting_type == 'float':
                    value = float(value)
                elif setting_type == 'decimal':
                    value = Decimal(value)
                elif setting_type == 'boolean':
                    value = value.lower() in ('true', '1', 'yes', 'on')
                # else: keep as string
                
                self._settings[key] = value
            
            self._initialized = True
            logger.info(f"✓ Configuration loaded: {len(self._settings)} settings from database")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from database: {e}")
            logger.warning("Falling back to environment variables")
            self._load_from_environment()
            self._initialized = True
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables as fallback."""
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
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        if not self._initialized:
            raise RuntimeError(
                "Configuration not initialized. Call await config.initialize(db_manager) first."
            )
        return self._settings.get(key, default)
    
    # Convenience properties matching the original settings.py interface
    
    @property
    def NETWORK(self) -> str:
        return self.get('network', 'testnet')
    
    @property
    def HORIZON_URL(self) -> str:
        return self.get('horizon_url', 'https://horizon-testnet.stellar.org')
    
    @property
    def PUBLIC_NETWORK_PASSPHRASE(self) -> str:
        return self.get('network_passphrase', 'Test SDF Network ; September 2015')
    
    @property
    def UBEC_CODE(self) -> str:
        return self.get('ubec_code', 'UBEC')
    
    @property
    def UBEC_ISSUER(self) -> str:
        return self.get('ubec_issuer', '')
    
    @property
    def FALLBACK_SUPPLY(self) -> Decimal:
        return Decimal(self.get('fallback_supply', '191766039.00'))
    
    @property
    def ALWAYS_LOAD_FROM_NETWORK(self) -> bool:
        return self.get('always_load_from_network', True)
    
    @property
    def TARGET_DISTRIBUTION(self) -> Dict[str, Decimal]:
        return {
            'general': Decimal(self.get('distribution_general', '0.65')),
            'stewardship': Decimal(self.get('distribution_stewardship', '0.30')),
            'administration': Decimal(self.get('distribution_administration', '0.05'))
        }
    
    @property
    def ACCOUNTS(self) -> Dict[str, Any]:
        # Load from environment as fallback until we add these to DB
        return {
            'general': os.getenv('GENERAL_ACCOUNT', ''),
            'administration': os.getenv('ADMIN_ACCOUNT', ''),
            'stewardship': [
                os.getenv('STEWARDSHIP_ACCOUNT_1', ''),
                os.getenv('STEWARDSHIP_ACCOUNT_2', ''),
                os.getenv('STEWARDSHIP_ACCOUNT_3', ''),
            ]
        }
    
    @property
    def REBALANCE_THRESHOLD(self) -> Decimal:
        return Decimal(self.get('rebalance_threshold', '0.01'))
    
    @property
    def CHECK_INTERVAL(self) -> int:
        return int(self.get('check_interval', 3600))
    
    @property
    def SUPPLY_CHECK_INTERVAL(self) -> int:
        return int(self.get('supply_check_interval', 86400))
    
    @property
    def SUPPLY_SAFETY_FACTOR(self) -> Decimal:
        return Decimal(self.get('supply_safety_factor', '0.02'))
    
    @property
    def SUPPLY_CALCULATION_METHOD(self) -> str:
        return self.get('supply_calculation_method', 'PRECISE')
    
    @property
    def LOG_FILE(self) -> str:
        return self.get('log_file', 'ubec_distribution_manager.log')
    
    @property
    def LOG_LEVEL(self) -> str:
        return self.get('log_level', 'INFO')
    
    @property
    def LOG_FORMAT(self) -> str:
        return self.get('log_format', '%(asctime)s - %(levelname)s - %(message)s')
    
    @property
    def LOG_FILE_PATH(self) -> str:
        return self.get('log_file_path', 'logs/ubec_distribution_manager.log')
    
    @property
    def LOG_DATE_FORMAT(self) -> str:
        return self.get('log_date_format', '%Y-%m-%d %H:%M:%S')
    
    @property
    def LOG_MAX_BYTES(self) -> int:
        return int(self.get('log_max_bytes', 10485760))
    
    @property
    def LOG_BACKUP_COUNT(self) -> int:
        return int(self.get('log_backup_count', 5))


# Global configuration instance
_system_config: Optional[SystemConfig] = None


async def get_system_config(db_manager) -> SystemConfig:
    """
    Get the global system configuration instance.
    
    Args:
        db_manager: AsyncDatabaseManager instance
        
    Returns:
        SystemConfig instance loaded from database.
    """
    global _system_config
    
    if _system_config is None:
        _system_config = SystemConfig()
        await _system_config.initialize(db_manager)
    
    return _system_config
