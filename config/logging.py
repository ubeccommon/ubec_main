"""
UBEC Protocol - Logging Configuration
======================================
Centralized logging setup for all protocols

Version: 1.0
Date: October 8, 2025
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    name: str = 'ubec',
    log_level: str = None,
    log_file: str = None,
    log_to_file: bool = None
) -> logging.Logger:
    """
    Setup and configure logger for UBEC protocols
    
    Args:
        name: Logger name (default: 'ubec')
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        log_to_file: Enable file logging (optional)
        
    Returns:
        Configured logger instance
    """
    # Import here to avoid circular imports
    from config.config import GlobalConfig
    
    # Use config values if not provided
    log_level = log_level or GlobalConfig.LOG_LEVEL
    log_file = log_file or GlobalConfig.LOG_FILE_PATH
    log_to_file = log_to_file if log_to_file is not None else GlobalConfig.LOG_TO_FILE
    
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        GlobalConfig.LOG_FORMAT,
        datefmt=GlobalConfig.LOG_DATE_FORMAT
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file and log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=GlobalConfig.LOG_MAX_BYTES,
            backupCount=GlobalConfig.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger for a module
    
    Args:
        name: Logger name (typically module name)
        
    Returns:
        Configured logger instance
    """
    # Check if root logger is already configured
    root_logger = logging.getLogger('ubec')
    if not root_logger.handlers:
        # Setup root logger first
        setup_logging('ubec')
    
    # Return child logger
    return logging.getLogger(f'ubec.{name}')


# Configure root logger when module is imported
_logger = setup_logging()


if __name__ == '__main__':
    """Test logging configuration"""
    print("Testing UBEC Logging Configuration\n")
    
    # Test different loggers
    logger = get_logger('test')
    
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    # Test module-specific loggers
    air_logger = get_logger('UBEC')
    air_logger.info("Air protocol logger test")
    
    water_logger = get_logger('UBECrc')
    water_logger.info("Water protocol logger test")
    
    earth_logger = get_logger('UBECgpi')
    earth_logger.info("Earth protocol logger test")
    
    fire_logger = get_logger('UBECtt')
    fire_logger.info("Fire protocol logger test")
    
    print("\nLogging test complete!")
