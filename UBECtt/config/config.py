# UBECtt/config/config.py
"""
UBECtt (Fire) Token-Specific Configuration
Transformation & Change parameters
"""

from decimal import Decimal

class UBECttConfig:
    """Configuration specific to UBECtt (Fire) token protocol."""
    
    # Transformation Parameters
    TRANSFORMATION_FEE = Decimal('0.005')  # 0.5% transformation fee
    MIN_TRANSFORMATION_THRESHOLD = Decimal('100')  # Minimum for transformation
    
    # Innovation Parameters
    INNOVATION_BONUS = Decimal('2.0')  # 2x bonus for innovation
    INNOVATION_THRESHOLD = 3  # Minimum innovations per quarter
    
    # Burn Mechanism
    BURN_RATE = Decimal('0.001')  # 0.1% burn per transformation
    CATALYST_MULTIPLIER = Decimal('1.5')  # Catalyst bonus
    
    # Holonic Thresholds (Fire-specific)
    CHANGE_PARTICIPATION_MIN = 5  # Minimum change initiatives
    INNOVATION_SCORE_THRESHOLD = Decimal('0.5')  # Minimum innovation score
