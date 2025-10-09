# UBECrc/config/config.py
"""
UBECrc (Water) Token-Specific Configuration
Reciprocity & Flow parameters
"""

from decimal import Decimal

class UBECrcConfig:
    """Configuration specific to UBECrc (Water) token protocol."""
    
    # Credit Parameters
    CREDIT_DECAY_RATE = Decimal('0.01')  # 1% monthly decay
    BASE_REWARD_PER_DATAPOINT = Decimal('7.14')  # Base reward amount
    
    # Reciprocity Parameters
    RECIPROCITY_BONUS_MULTIPLIER = Decimal('1.5')  # 50% bonus
    MIN_RECIPROCITY_SCORE = Decimal('0.3')  # Minimum score
    
    # Flow Parameters
    FLOW_THRESHOLD = 100  # Min transactions for flow bonus
    FLOW_BONUS_RATE = Decimal('0.05')  # 5% bonus for active flow
    
    # Holonic Thresholds (Water-specific)
    BALANCE_THRESHOLD = Decimal('0.7')  # Minimum balance score
    EXCHANGE_FREQUENCY = 5  # Minimum exchanges per month
