"""
UBEC Protocol Configuration Package

Root configuration for the UBEC protocol suite.
"""

from .config import UBECConfig
from .logging import setup_logging, get_logger

__all__ = ['UBECConfig', 'setup_logging', 'get_logger']
