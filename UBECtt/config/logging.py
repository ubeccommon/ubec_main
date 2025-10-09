# UBECtt/config/logging.py
"""
UBECtt Token-Specific Logging Configuration
"""

from config import get_logger as get_global_logger

def get_logger(name=None):
    """
    Get a logger for the UBECtt module.
    
    Args:
        name: Optional sub-module name
    
    Returns:
        logging.Logger: Logger instance
    """
    if name:
        return get_global_logger(f'UBECtt.{name}')
    return get_global_logger('UBECtt')
