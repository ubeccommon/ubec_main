# UBECrc/config/logging.py
"""
UBECrc Token-Specific Logging Configuration
"""

from config import get_logger as get_global_logger

def get_logger(name=None):
    """
    Get a logger for the UBECrc module.
    
    Args:
        name: Optional sub-module name
    
    Returns:
        logging.Logger: Logger instance
    """
    if name:
        return get_global_logger(f'UBECrc.{name}')
    return get_global_logger('UBECrc')
