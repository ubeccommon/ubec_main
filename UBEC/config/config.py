# UBEC/config/config.py
"""
UBEC (Air) Token-Specific Configuration
Gateway & Access parameters
"""

from decimal import Decimal

class UBECConfig:
    """Configuration specific to UBEC (Air) token protocol."""
    
    # Transaction Parameters
    TRANSACTION_FEE_RATE = Decimal('0.003')  # 0.3% transaction fee
    MIN_TRANSACTION_AMOUNT = Decimal('0.01')  # Minimum transaction
    
    # Gateway Parameters
    ONBOARDING_AMOUNT = Decimal('100')  # Initial UBEC for new users
    GATEWAY_THRESHOLD = Decimal('10')   # Minimum to access other tokens
    
    # Accessibility Multipliers
    ACCESSIBILITY_BONUS = Decimal('1.2')  # 20% bonus for high accessibility
    MOVEMENT_REWARD_RATE = Decimal('0.01')  # Reward for active movement
    
    # Holonic Thresholds (Air-specific)
    FREEDOM_THRESHOLD = Decimal('0.6')  # Minimum freedom score
    CONNECTION_THRESHOLD = 5  # Minimum connections
    ACTIVITY_THRESHOLD = 10  # Minimum transactions per month
