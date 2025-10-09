"""
UBEC Protocol - Configuration Package
======================================
Global configuration and logging for all protocols

Version: 1.0
Date: October 8, 2025
"""

from config.config import (
    GlobalConfig,
    validate_config,
    display_config
)

from config.logging import (
    get_logger,
    setup_logging
)

__all__ = [
    'GlobalConfig',
    'validate_config',
    'display_config',
    'get_logger',
    'setup_logging'
]

__version__ = '1.0.0'
