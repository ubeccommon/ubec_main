# UBECgpi/config/config.py
"""
UBECgpi (Earth) Token-Specific Configuration
Stability & Value parameters
"""

from decimal import Decimal

class UBECgpiConfig:
    """Configuration specific to UBECgpi (Earth) token protocol."""
    
    # Stability Parameters
    STABILITY_THRESHOLD = Decimal('0.02')  # 2% max volatility
    ASSET_BACKING_RATIO = Decimal('1.0')  # 100% backed
    
    # Rebalancing Parameters
    REBALANCE_FREQUENCY = 86400  # Daily rebalancing (seconds)
    REBALANCE_THRESHOLD = Decimal('0.01')  # 1% deviation triggers rebalance
    
    # Long-term Holding Parameters
    MIN_HOLDING_PERIOD = 30  # Days for stability rewards
    STABILITY_BONUS = Decimal('1.3')  # 30% bonus for stable holders
    
    # Holonic Thresholds (Earth-specific)
    VOLATILITY_MAX = Decimal('0.05')  # Maximum acceptable volatility
    HOLDING_SCORE_THRESHOLD = 60  # Minimum holding days
