"""
UBEC Protocol - Global Configuration
=====================================
Centralized configuration for all four element protocols

Elements:
🜁 Air (UBEC)      - Gateway & Universal Access
🜄 Water (UBECrc)  - Flow & Exchange
🜃 Earth (UBECgpi) - Stability & Value
🜂 Fire (UBECtt)   - Transformation & Action

Version: 1.0
Date: October 8, 2025
"""

import os
import logging
from decimal import Decimal
from typing import Dict, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GlobalConfig:
    """
    Global configuration for UBEC Protocol Suite
    All element protocols inherit these base settings
    """
    
    # ========================================================================
    # NETWORK CONFIGURATION
    # ========================================================================
    
    # Stellar Network Selection (testnet or mainnet)
    NETWORK = os.getenv('UBEC_NETWORK', 'testnet')
    
    # Horizon API URLs
    HORIZON_URL = {
        'mainnet': 'https://horizon.stellar.org',
        'testnet': 'https://horizon-testnet.stellar.org'
    }
    
    # Network passphrase
    NETWORK_PASSPHRASE = {
        'mainnet': 'Public Global Stellar Network ; September 2015',
        'testnet': 'Test SDF Network ; September 2015'
    }
    
    @classmethod
    def get_horizon_url(cls) -> str:
        """Get the appropriate Horizon URL for the configured network"""
        return cls.HORIZON_URL.get(cls.NETWORK, cls.HORIZON_URL['testnet'])
    
    @classmethod
    def get_network_passphrase(cls) -> str:
        """Get the network passphrase for the configured network"""
        return cls.NETWORK_PASSPHRASE.get(cls.NETWORK, cls.NETWORK_PASSPHRASE['testnet'])
    
    # ========================================================================
    # TOKEN CONFIGURATION
    # ========================================================================
    
    # Element Token Codes
    UBEC_CODE = 'UBEC'          # Air - Gateway
    UBECrc_CODE = 'UBECrc'      # Water - Flow
    UBECgpi_CODE = 'UBECgpi'    # Earth - Stability
    UBECtt_CODE = 'UBECtt'      # Fire - Transformation
    
    # Token Issuer Addresses
    # IMPORTANT: Update these with your actual issuer addresses
    UBEC_ISSUER = os.getenv('UBEC_ISSUER', 'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    UBECrc_ISSUER = os.getenv('UBECrc_ISSUER', 'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    UBECgpi_ISSUER = os.getenv('UBECgpi_ISSUER', 'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    UBECtt_ISSUER = os.getenv('UBECtt_ISSUER', 'GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    
    # Total Supply (shared across all tokens)
    TOTAL_SUPPLY = Decimal('21000000')
    
    # Element to Token Mapping
    ELEMENT_TOKEN_MAP = {
        'air': UBEC_CODE,
        'water': UBECrc_CODE,
        'earth': UBECgpi_CODE,
        'fire': UBECtt_CODE
    }
    
    @classmethod
    def get_token_config(cls, element: str) -> Tuple[str, str]:
        """
        Get token code and issuer for a specific element
        
        Args:
            element: Element type ('air', 'water', 'earth', 'fire')
            
        Returns:
            Tuple of (token_code, issuer_address)
        """
        token_map = {
            'air': (cls.UBEC_CODE, cls.UBEC_ISSUER),
            'water': (cls.UBECrc_CODE, cls.UBECrc_ISSUER),
            'earth': (cls.UBECgpi_CODE, cls.UBECgpi_ISSUER),
            'fire': (cls.UBECtt_CODE, cls.UBECtt_ISSUER)
        }
        return token_map.get(element, token_map['air'])
    
    # ========================================================================
    # DISTRIBUTION RULES (75/20/5)
    # ========================================================================
    
    # Base Distribution Rules
    DISTRIBUTION_RULES = {
        'general_circulation': Decimal('0.75'),    # 75%
        'stewardship': Decimal('0.20'),            # 20%
        'administration': Decimal('0.05')          # 5%
    }
    
    # Element-Specific Distribution Variations
    ELEMENT_DISTRIBUTION = {
        'UBEC': {
            'general_circulation': 75.0,    # Standard
            'stewardship': 20.0,
            'administration': 5.0
        },
        'UBECrc': {
            'general_circulation': 70.0,    # More stewardship (more flow)
            'stewardship': 25.0,
            'administration': 5.0
        },
        'UBECgpi': {
            'general_circulation': 80.0,    # More stable (less stewardship)
            'stewardship': 15.0,
            'administration': 5.0
        },
        'UBECtt': {
            'general_circulation': 65.0,    # More control (transformative)
            'stewardship': 25.0,
            'administration': 10.0
        }
    }
    
    # Distribution Compliance Tolerance (percentage points)
    DISTRIBUTION_TOLERANCE = Decimal('5.0')  # Allow 5% deviation
    
    @classmethod
    def get_distribution_rules(cls, token_code: str) -> Dict[str, float]:
        """
        Get distribution rules for a specific token
        
        Args:
            token_code: Token code (UBEC, UBECrc, UBECgpi, UBECtt)
            
        Returns:
            Dictionary with distribution percentages
        """
        return cls.ELEMENT_DISTRIBUTION.get(token_code, cls.ELEMENT_DISTRIBUTION['UBEC'])
    
    # ========================================================================
    # UBUNTU PRINCIPLES CONFIGURATION
    # ========================================================================
    
    # Ubuntu Principles to Element Mapping
    PRINCIPLE_TO_ELEMENT = {
        'diversity': 'air',         # UBEC - Freedom and variety
        'reciprocity': 'water',     # UBECrc - Flow and exchange
        'mutualism': 'earth',       # UBECgpi - Support and stability
        'regeneration': 'fire',     # UBECtt - Transformation and renewal
        'holism': 'all'             # System-wide integration
    }
    
    # Element to Principle Mapping (reverse)
    ELEMENT_TO_PRINCIPLE = {
        'air': 'diversity',
        'water': 'reciprocity',
        'earth': 'mutualism',
        'fire': 'regeneration'
    }
    
    # Holonic Health Thresholds
    HOLONIC_THRESHOLDS = {
        'excellent': Decimal('0.8'),
        'good': Decimal('0.6'),
        'fair': Decimal('0.4'),
        'poor': Decimal('0.2')
    }
    
    @classmethod
    def get_health_status(cls, score: Decimal) -> str:
        """
        Get health status based on holonic score
        
        Args:
            score: Holonic score (0-1)
            
        Returns:
            Health status string
        """
        if score >= cls.HOLONIC_THRESHOLDS['excellent']:
            return 'excellent'
        elif score >= cls.HOLONIC_THRESHOLDS['good']:
            return 'good'
        elif score >= cls.HOLONIC_THRESHOLDS['fair']:
            return 'fair'
        elif score >= cls.HOLONIC_THRESHOLDS['poor']:
            return 'poor'
        else:
            return 'critical'
    
    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================
    
    # Database Connection Parameters
    DB_HOST = os.getenv('UBEC_DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('UBEC_DB_PORT', '5432'))
    DB_NAME = os.getenv('UBEC_DB_NAME', 'ubec')
    DB_SCHEMA = os.getenv('UBEC_DB_SCHEMA', 'ubec_main')
    
    # Database Users
    DB_USER = os.getenv('UBEC_DB_USER', 'ubec_app')
    DB_PASSWORD = os.getenv('UBEC_DB_PASSWORD', '')
    
    DB_READONLY_USER = os.getenv('UBEC_DB_READONLY_USER', 'ubec_readonly')
    DB_READONLY_PASSWORD = os.getenv('UBEC_DB_READONLY_PASSWORD', '')
    
    DB_SYNC_USER = os.getenv('UBEC_DB_SYNC_USER', 'ubec_sync')
    DB_SYNC_PASSWORD = os.getenv('UBEC_DB_SYNC_PASSWORD', '')
    
    # Connection Pool Settings
    DB_POOL_MIN = int(os.getenv('UBEC_DB_POOL_MIN', '2'))
    DB_POOL_MAX = int(os.getenv('UBEC_DB_POOL_MAX', '20'))
    DB_POOL_TIMEOUT = int(os.getenv('UBEC_DB_POOL_TIMEOUT', '30'))
    
    # SSL Settings
    DB_SSL_MODE = os.getenv('UBEC_DB_SSL_MODE', 'prefer')
    
    @classmethod
    def get_database_url(cls, user_type: str = 'app') -> str:
        """
        Get database connection URL for specified user type
        
        Args:
            user_type: Type of user ('app', 'readonly', 'sync')
            
        Returns:
            PostgreSQL connection URL
        """
        user_map = {
            'app': (cls.DB_USER, cls.DB_PASSWORD),
            'readonly': (cls.DB_READONLY_USER, cls.DB_READONLY_PASSWORD),
            'sync': (cls.DB_SYNC_USER, cls.DB_SYNC_PASSWORD)
        }
        
        user, password = user_map.get(user_type, user_map['app'])
        
        return f"postgresql://{user}:{password}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_database_params(cls, user_type: str = 'app') -> Dict[str, any]:
        """
        Get database connection parameters as dictionary
        
        Args:
            user_type: Type of user ('app', 'readonly', 'sync')
            
        Returns:
            Dictionary of connection parameters
        """
        user_map = {
            'app': (cls.DB_USER, cls.DB_PASSWORD),
            'readonly': (cls.DB_READONLY_USER, cls.DB_READONLY_PASSWORD),
            'sync': (cls.DB_SYNC_USER, cls.DB_SYNC_PASSWORD)
        }
        
        user, password = user_map.get(user_type, user_map['app'])
        
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': user,
            'password': password,
            'options': f'-c search_path={cls.DB_SCHEMA},public'
        }
    
    # ========================================================================
    # SYNCHRONIZATION CONFIGURATION
    # ========================================================================
    
    # Sync intervals (seconds)
    SYNC_INTERVAL_ACCOUNTS = int(os.getenv('SYNC_INTERVAL_ACCOUNTS', '300'))      # 5 minutes
    SYNC_INTERVAL_TRANSACTIONS = int(os.getenv('SYNC_INTERVAL_TRANSACTIONS', '60'))  # 1 minute
    SYNC_INTERVAL_BALANCES = int(os.getenv('SYNC_INTERVAL_BALANCES', '180'))      # 3 minutes
    
    # Sync batch sizes
    SYNC_BATCH_SIZE = int(os.getenv('SYNC_BATCH_SIZE', '200'))
    
    # Retry configuration
    SYNC_MAX_RETRIES = int(os.getenv('SYNC_MAX_RETRIES', '3'))
    SYNC_RETRY_DELAY = int(os.getenv('SYNC_RETRY_DELAY', '5'))  # seconds
    
    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    
    # Log levels
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Log format
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Log file settings
    LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'false').lower() == 'true'
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/ubec_protocol.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # ========================================================================
    # ELEMENT DESCRIPTIONS
    # ========================================================================
    
    ELEMENT_INFO = {
        'air': {
            'token': 'UBEC',
            'symbol': '🜁',
            'name': 'Air Element',
            'role': 'Gateway & Universal Access',
            'principle': 'Diversity',
            'characteristics': [
                'Freedom of movement',
                'Universal accessibility',
                'Entry points to the commons',
                'Variety and distribution'
            ]
        },
        'water': {
            'token': 'UBECrc',
            'symbol': '🜄',
            'name': 'Water Element',
            'role': 'Flow & Exchange',
            'principle': 'Reciprocity',
            'characteristics': [
                'Liquidity and flow',
                'Resource circulation',
                'Exchange balance',
                'Mutual benefit'
            ]
        },
        'earth': {
            'token': 'UBECgpi',
            'symbol': '🜃',
            'name': 'Earth Element',
            'role': 'Stability & Value',
            'principle': 'Mutualism',
            'characteristics': [
                'Value stability',
                'Distribution compliance',
                'Grounding and support',
                'Collaborative networks'
            ]
        },
        'fire': {
            'token': 'UBECtt',
            'symbol': '🜂',
            'name': 'Fire Element',
            'role': 'Transformation & Action',
            'principle': 'Regeneration',
            'characteristics': [
                'Catalytic action',
                'Transformative power',
                'Community impact',
                'Renewal and growth'
            ]
        }
    }
    
    @classmethod
    def get_element_info(cls, element: str) -> Dict:
        """Get detailed information about an element"""
        return cls.ELEMENT_INFO.get(element, {})


# ============================================================================
# LOGGING SETUP
# ============================================================================

def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger for a module
    
    Args:
        name: Logger name (typically module name)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = getattr(logging, GlobalConfig.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        GlobalConfig.LOG_FORMAT,
        datefmt=GlobalConfig.LOG_DATE_FORMAT
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if GlobalConfig.LOG_TO_FILE:
        from logging.handlers import RotatingFileHandler
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(GlobalConfig.LOG_FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = RotatingFileHandler(
            GlobalConfig.LOG_FILE_PATH,
            maxBytes=GlobalConfig.LOG_MAX_BYTES,
            backupCount=GlobalConfig.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_config() -> bool:
    """
    Validate configuration settings
    
    Returns:
        True if configuration is valid, False otherwise
    """
    logger = get_logger('config')
    errors = []
    
    # Check issuer addresses
    if GlobalConfig.UBEC_ISSUER.startswith('GX'):
        errors.append("UBEC_ISSUER not configured (using placeholder)")
    
    if GlobalConfig.UBECrc_ISSUER.startswith('GX'):
        errors.append("UBECrc_ISSUER not configured (using placeholder)")
    
    if GlobalConfig.UBECgpi_ISSUER.startswith('GX'):
        errors.append("UBECgpi_ISSUER not configured (using placeholder)")
    
    if GlobalConfig.UBECtt_ISSUER.startswith('GX'):
        errors.append("UBECtt_ISSUER not configured (using placeholder)")
    
    # Check database password
    if not GlobalConfig.DB_PASSWORD:
        errors.append("UBEC_DB_PASSWORD not configured")
    
    if not GlobalConfig.DB_SYNC_PASSWORD:
        errors.append("UBEC_DB_SYNC_PASSWORD not configured")
    
    # Check network
    if GlobalConfig.NETWORK not in ['testnet', 'mainnet']:
        errors.append(f"Invalid NETWORK: {GlobalConfig.NETWORK}")
    
    # Report errors
    if errors:
        logger.warning("Configuration validation found issues:")
        for error in errors:
            logger.warning(f"  - {error}")
        return False
    
    logger.info("Configuration validation passed")
    return True


# ============================================================================
# CONFIGURATION DISPLAY
# ============================================================================

def display_config():
    """Display current configuration (for debugging)"""
    logger = get_logger('config')
    
    logger.info("=" * 70)
    logger.info("UBEC Protocol Configuration")
    logger.info("=" * 70)
    logger.info(f"Network: {GlobalConfig.NETWORK}")
    logger.info(f"Horizon URL: {GlobalConfig.get_horizon_url()}")
    logger.info(f"Database: {GlobalConfig.DB_HOST}:{GlobalConfig.DB_PORT}/{GlobalConfig.DB_NAME}")
    logger.info(f"Schema: {GlobalConfig.DB_SCHEMA}")
    logger.info("")
    logger.info("Element Tokens:")
    logger.info(f"  🜁 Air (UBEC):      {GlobalConfig.UBEC_CODE}")
    logger.info(f"  🜄 Water (UBECrc):  {GlobalConfig.UBECrc_CODE}")
    logger.info(f"  🜃 Earth (UBECgpi): {GlobalConfig.UBECgpi_CODE}")
    logger.info(f"  🜂 Fire (UBECtt):   {GlobalConfig.UBECtt_CODE}")
    logger.info("=" * 70)


# ============================================================================
# INITIALIZE ON IMPORT
# ============================================================================

# Validate configuration when module is imported
if __name__ != '__main__':
    validate_config()


# ============================================================================
# MODULE TEST
# ============================================================================

if __name__ == '__main__':
    """Test configuration module"""
    print("\n" + "=" * 70)
    print("UBEC Configuration Module Test")
    print("=" * 70 + "\n")
    
    # Display configuration
    display_config()
    
    # Test element info
    print("\nElement Information:")
    for element in ['air', 'water', 'earth', 'fire']:
        info = GlobalConfig.get_element_info(element)
        print(f"\n{info['symbol']} {info['name']}:")
        print(f"  Token: {info['token']}")
        print(f"  Role: {info['role']}")
        print(f"  Principle: {info['principle']}")
    
    # Test token config
    print("\n\nToken Configurations:")
    for element in ['air', 'water', 'earth', 'fire']:
        token_code, issuer = GlobalConfig.get_token_config(element)
        print(f"  {element.capitalize()}: {token_code} → {issuer[:10]}...")
    
    # Test distribution rules
    print("\n\nDistribution Rules:")
    for token in ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']:
        rules = GlobalConfig.get_distribution_rules(token)
        print(f"  {token}:")
        print(f"    General: {rules['general_circulation']}%")
        print(f"    Stewardship: {rules['stewardship']}%")
        print(f"    Administration: {rules['administration']}%")
    
    # Test database URLs
    print("\n\nDatabase Connection URLs:")
    print(f"  App: {GlobalConfig.get_database_url('app')}")
    print(f"  ReadOnly: {GlobalConfig.get_database_url('readonly')}")
    print(f"  Sync: {GlobalConfig.get_database_url('sync')}")
    
    # Validate
    print("\n\nValidation:")
    is_valid = validate_config()
    print(f"  Configuration valid: {is_valid}")
    
    print("\n" + "=" * 70)
    print("Configuration test complete!")
    print("=" * 70 + "\n")
