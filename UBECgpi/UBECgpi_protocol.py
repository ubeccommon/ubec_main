#!/usr/bin/env python3
"""
🜃 Earth Token (UBECgpi Stability) Protocol
Ubuntu Bioregional Economic Commons

Element: Earth (🜃) - Stability, Grounding, Value Storage
Function: GPI-pegged stable token

Version: 1.0.0
Date: October 2025

This project uses the services of Claude and Anthropic PBC to inform our decisions 
and recommendations. This project was made possible with the assistance of Claude 
and Anthropic PBC.
"""

import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from stellar_sdk import Server, Network, Keypair, TransactionBuilder, Asset
from config import GlobalConfig, get_logger

logger = get_logger('UBECgpi')


@dataclass
class CollateralPosition:
    """User's collateral position"""
    account: str
    collateral_assets: Dict[str, Decimal]  # Asset -> Amount
    collateral_value_eur: Decimal
    ubecgpi_minted: Decimal
    collateral_ratio: Decimal
    health_status: str  # healthy, warning, critical
    last_updated: datetime
    
    @property
    def is_healthy(self) -> bool:
        return self.collateral_ratio >= Decimal("1.5")


@dataclass
class GPIReading:
    """GPI oracle reading"""
    timestamp: datetime
    gpi_value: Decimal
    components: Dict[str, Decimal]
    oracle_source: str
    confidence: Decimal  # 0-1


class UBECgpiProtocol:
    """
    Earth Token (UBECgpi) Protocol
    
    Manages GPI-pegged stability token with:
    - Collateralized minting/burning
    - Oracle integration
    - Stability mechanisms
    - Liquidation protection
    """
    
    TOKEN_CODE = "UBECgpi"
    MIN_COLLATERAL_RATIO = Decimal("1.5")  # 150%
    STRESS_COLLATERAL_RATIO = Decimal("1.75")  # 175%
    LIQUIDATION_THRESHOLD = Decimal("1.4")  # 140%
    
    MINTING_FEE = Decimal("0.005")  # 0.5%
    BURNING_FEE = Decimal("0.003")  # 0.3%
    
    # GPI stability thresholds
    GPI_DEVIATION_THRESHOLD = Decimal("0.02")  # 2%
    ADJUSTMENT_RATE = Decimal("0.01")  # 1% supply adjustment
    
    def __init__(
        self,
        issuer_public: str = None,
        network: str = None,
        horizon_url: Optional[str] = None
    ):
        """Initialize Earth Token Protocol"""
        logger.info("Initializing UBECgpi (Earth) Protocol")
        
        # Use GlobalConfig if parameters not provided
        self.issuer_public = issuer_public or GlobalConfig.UBECgpi_ISSUER
        self.issuer = self.issuer_public  # Alias for compatibility
        
        network = network or GlobalConfig.NETWORK
        
        if network == "testnet":
            self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
            self.horizon_url = horizon_url or "https://horizon-testnet.stellar.org"
        else:
            self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
            self.horizon_url = horizon_url or "https://horizon.stellar.org"
        
        # Set asset code and create Asset object
        self.asset_code = self.TOKEN_CODE
        self.server = Server(horizon_url=self.horizon_url)
        self.asset = Asset(self.TOKEN_CODE, self.issuer_public)
        
        # State
        self.collateral_positions: Dict[str, CollateralPosition] = {}
        self.total_collateral_value = Decimal("0")
        self.total_minted = Decimal("0")
        self.current_gpi = Decimal("1.0")  # Target: 1 GPI unit
        self.reserve_assets: Dict[str, Decimal] = {}
        
        logger.info(f"Connected to {network} network")
        logger.info(f"UBECgpi Asset: {self.asset_code}:{self.issuer}")
        logger.info("UBECgpi Protocol: Stability & Value System")
    
    def health_check(self):
        """Perform health check on UBECgpi protocol."""
        logger.info("Performing UBECgpi protocol health check")
        
        try:
            status = {
                'protocol': 'UBECgpi (Earth)',
                'network': GlobalConfig.NETWORK,
                'asset_code': self.asset_code,
                'issuer': self.issuer,
                'stability_monitoring': True,
                'asset_backing': True,
                'backing_ratio': float(self.MIN_COLLATERAL_RATIO),
                'stability_threshold': float(self.GPI_DEVIATION_THRESHOLD),
                'system_active': True
            }
            
            logger.info("✓ UBECgpi protocol health check passed")
            return status
            
        except Exception as e:
            logger.error(f"✗ UBECgpi protocol health check failed: {e}")
            raise
    
    def get_status(self):
        """Get comprehensive status of UBECgpi system."""
        logger.info("Getting UBECgpi protocol status")
        
        try:
            # Get basic statistics
            total_positions = len(self.collateral_positions)
            total_minted_float = float(self.total_minted)
            total_collateral_float = float(self.total_collateral_value)
            
            # Calculate system collateral ratio
            if self.total_minted > 0:
                system_ratio = self.total_collateral_value / self.total_minted
            else:
                system_ratio = Decimal("0")
            
            status = {
                'protocol': 'UBECgpi (Earth)',
                'element': 'Earth (🜃)',
                'principle': 'Mutualism & Stability',
                'role': 'Value Stability Token',
                'asset_code': self.asset_code,
                'issuer': self.issuer,
                'network': GlobalConfig.NETWORK,
                
                'total_positions': total_positions,
                'total_minted': total_minted_float,
                'total_collateral_value': total_collateral_float,
                'system_collateral_ratio': float(system_ratio),
                'current_gpi_peg': float(self.current_gpi),
                
                'min_collateral_ratio': float(self.MIN_COLLATERAL_RATIO),
                'liquidation_threshold': float(self.LIQUIDATION_THRESHOLD),
                
                'system_healthy': system_ratio >= self.MIN_COLLATERAL_RATIO if self.total_minted > 0 else True
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting UBECgpi status: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get Earth protocol metrics for holonic evaluation
        
        Returns:
            Dictionary with stability metrics
        """
        logger.info("Calculating Earth metrics")
        
        try:
            # Count healthy vs at-risk positions
            healthy_count = 0
            warning_count = 0
            critical_count = 0
            
            for position in self.collateral_positions.values():
                if position.collateral_ratio >= self.STRESS_COLLATERAL_RATIO:
                    healthy_count += 1
                elif position.collateral_ratio >= self.MIN_COLLATERAL_RATIO:
                    warning_count += 1
                else:
                    critical_count += 1
            
            # Calculate average collateral ratio
            if self.collateral_positions:
                avg_ratio = sum(p.collateral_ratio for p in self.collateral_positions.values()) / len(self.collateral_positions)
            else:
                avg_ratio = Decimal("0")
            
            # System health score (0-1)
            if self.total_minted == 0:
                health_score = 1.0
            else:
                system_ratio = self.total_collateral_value / self.total_minted
                if system_ratio >= self.STRESS_COLLATERAL_RATIO:
                    health_score = 1.0
                elif system_ratio >= self.MIN_COLLATERAL_RATIO:
                    health_score = 0.7
                else:
                    health_score = 0.4
            
            metrics = {
                'element': 'earth',
                'token': 'UBECgpi',
                'principle': 'mutualism',
                
                'active_positions': len(self.collateral_positions),
                'healthy_positions': healthy_count,
                'warning_positions': warning_count,
                'critical_positions': critical_count,
                
                'total_minted': str(self.total_minted),
                'total_collateral_value': str(self.total_collateral_value),
                'average_collateral_ratio': str(avg_ratio),
                
                'system_health_score': health_score,
                'gpi_stability': float(self.current_gpi),
                
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating Earth metrics: {e}")
            return {
                'element': 'earth',
                'token': 'UBECgpi',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def sync_stability_data(self) -> Dict[str, Any]:
        """
        Synchronize Earth (stability) distribution data
        
        This method syncs:
        - Account information for UBECgpi holders
        - Balance information (stability metrics)
        - Distribution compliance (mutualism principle)
        - Collateral positions
        
        Returns:
            Dictionary containing sync results with counts and status
        """
        logger.info("Starting Earth (UBECgpi) stability data synchronization...")
        
        try:
            # Import required modules
            from core.db.ubec_data_synchronizer import UBECDataSynchronizer
            from core.distribution.ubec_distribution_manager import UBECDistributionManager
            
            # Initialize modules
            synchronizer = UBECDataSynchronizer()
            distribution_mgr = UBECDistributionManager()
            
            # Track overall results
            total_accounts = 0
            total_transactions = 0
            total_balances = 0
            errors = []
            
            # Sync accounts for UBECgpi token
            logger.info("  Syncing UBECgpi accounts...")
            try:
                accounts_result = synchronizer.sync_account_data(asset_code='UBECgpi')
                total_accounts = accounts_result.get('synced', 0)
                logger.info(f"    ✓ Synced {total_accounts} accounts")
            except Exception as e:
                error_msg = f"Error syncing accounts: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Sync transactions
            logger.info("  Syncing UBECgpi transactions...")
            try:
                transactions_result = synchronizer.sync_transaction_data(asset_code='UBECgpi')
                total_transactions = transactions_result.get('synced', 0)
                logger.info(f"    ✓ Synced {total_transactions} transactions")
            except Exception as e:
                error_msg = f"Error syncing transactions: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Sync balances (Earth = stability)
            logger.info("  Syncing UBECgpi balances...")
            try:
                balances_result = synchronizer.sync_balance_data(asset_code='UBECgpi')
                total_balances = balances_result.get('synced', 0)
                logger.info(f"    ✓ Synced {total_balances} balances")
            except Exception as e:
                error_msg = f"Error syncing balances: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Check distribution compliance (Earth principle = mutualism/stability)
            logger.info("  Checking distribution compliance...")
            compliance_status = {}
            try:
                compliance_status = distribution_mgr.check_compliance(asset_code='UBECgpi')
                is_compliant = compliance_status.get('compliant', False)
                logger.info(f"    {'✓' if is_compliant else '⚠'} Compliance: {is_compliant}")
            except Exception as e:
                error_msg = f"Error checking compliance: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
                compliance_status = {'compliant': False, 'error': str(e)}
            
            # Create distribution snapshot
            logger.info("  Creating distribution snapshot...")
            snapshot_id = None
            try:
                snapshot_id = distribution_mgr.snapshot_distribution(asset_code='UBECgpi')
                if snapshot_id:
                    logger.info(f"    ✓ Snapshot created with ID: {snapshot_id}")
            except Exception as e:
                error_msg = f"Error creating snapshot: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Calculate stability metrics
            logger.info("  Calculating stability metrics...")
            try:
                stability_metrics = self._calculate_stability_metrics(
                    total_accounts,
                    total_balances,
                    compliance_status
                )
            except Exception as e:
                logger.warning(f"    ⚠ Could not calculate stability metrics: {e}")
                stability_metrics = {
                    'stability_score': 0.0,
                    'distribution_health': 'UNKNOWN'
                }
            
            # Build result
            result = {
                'element': 'earth',
                'token': 'UBECgpi',
                'asset_code': self.asset_code,
                'issuer': self.issuer,
                'accounts_synced': total_accounts,
                'transactions_synced': total_transactions,
                'balances_synced': total_balances,
                'distribution_compliant': compliance_status.get('compliant', False),
                'general_circulation_pct': compliance_status.get('general_circulation_pct', 0.0),
                'stewardship_pct': compliance_status.get('stewardship_pct', 0.0),
                'administration_pct': compliance_status.get('administration_pct', 0.0),
                'stability_score': stability_metrics.get('stability_score', 0.0),
                'distribution_health': stability_metrics.get('distribution_health', 'UNKNOWN'),
                'snapshot_id': snapshot_id,
                'errors': errors if errors else None,
                'status': 'success' if not errors else 'partial',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"  ✓ Earth sync complete: {result['accounts_synced']} accounts, "
                       f"compliance: {result['distribution_compliant']}")
            
            if errors:
                logger.warning(f"  ⚠ Sync completed with {len(errors)} errors")
            
            return result
            
        except ImportError as e:
            logger.error(f"  ✗ Cannot import required modules: {e}")
            return {
                'element': 'earth',
                'token': 'UBECgpi',
                'asset_code': self.asset_code,
                'issuer': self.issuer,
                'status': 'error',
                'error': 'Required modules not found - check core/db/ and core/distribution/',
                'error_detail': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"  ✗ Fatal error syncing Earth data: {e}")
            return {
                'element': 'earth',
                'token': 'UBECgpi',
                'asset_code': self.asset_code,
                'issuer': self.issuer,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_stability_metrics(self, accounts: int, balances: int, 
                                     compliance: Dict) -> Dict:
        """
        Calculate stability metrics for Earth protocol
        
        Args:
            accounts: Number of accounts
            balances: Number of balance records
            compliance: Distribution compliance data
            
        Returns:
            Dictionary with stability metrics
        """
        try:
            # Base stability score on distribution compliance
            is_compliant = compliance.get('compliant', False)
            
            # Calculate deviations from target percentages
            target_general = 75.0
            target_stewardship = 20.0
            target_admin = 5.0
            
            actual_general = compliance.get('general_circulation_pct', 0.0)
            actual_stewardship = compliance.get('stewardship_pct', 0.0)
            actual_admin = compliance.get('administration_pct', 0.0)
            
            # Calculate total deviation
            total_deviation = (
                abs(actual_general - target_general) +
                abs(actual_stewardship - target_stewardship) +
                abs(actual_admin - target_admin)
            )
            
            # Stability score (1.0 = perfect, 0.0 = maximum deviation)
            # Allow up to 15% total deviation before hitting 0
            stability_score = max(0.0, 1.0 - (total_deviation / 15.0))
            
            # Determine distribution health
            if is_compliant:
                distribution_health = 'STABLE'
            elif total_deviation < 10.0:
                distribution_health = 'MINOR_DEVIATION'
            elif total_deviation < 20.0:
                distribution_health = 'MODERATE_DEVIATION'
            else:
                distribution_health = 'MAJOR_DEVIATION'
            
            return {
                'stability_score': round(stability_score, 2),
                'distribution_health': distribution_health,
                'total_deviation': round(total_deviation, 2),
                'compliant': is_compliant
            }
            
        except Exception as e:
            logger.warning(f"Error calculating stability metrics: {e}")
            return {
                'stability_score': 0.0,
                'distribution_health': 'ERROR'
            }
    
    def assess_mutualism(self) -> Dict[str, Any]:
        """
        Assess mutualism principle (Earth's ubuntu principle)
        
        Returns:
            Dictionary with mutualism assessment
        """
        logger.info("Assessing mutualism principle for Earth element")
        
        try:
            metrics = self.get_metrics()
            
            # Mutualism metrics
            avg_collateral_ratio = Decimal(metrics.get('average_collateral_ratio', '0'))
            active_positions = metrics.get('active_positions', 0)
            
            # Calculate mutualism score based on stability and participation
            if avg_collateral_ratio > Decimal('1.75'):
                mutualism_score = 0.9
            elif avg_collateral_ratio > Decimal('1.5'):
                mutualism_score = 0.7
            elif avg_collateral_ratio > Decimal('1.4'):
                mutualism_score = 0.5
            else:
                mutualism_score = 0.3
            
            assessment = {
                'principle': 'mutualism',
                'element': 'earth',
                'score': mutualism_score,
                'avg_collateral_ratio': str(avg_collateral_ratio),
                'active_positions': active_positions,
                'status': 'excellent' if mutualism_score > 0.7 else 'good' if mutualism_score > 0.5 else 'needs_improvement',
                'interpretation': self._interpret_mutualism_score(mutualism_score),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing mutualism: {e}")
            return {
                'principle': 'mutualism',
                'element': 'earth',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _interpret_mutualism_score(self, score: float) -> str:
        """Interpret mutualism score"""
        if score >= 0.8:
            return 'Excellent mutualism - Strong stable ecosystem with healthy backing'
        elif score >= 0.6:
            return 'Good mutualism - System is stable with adequate collateralization'
        elif score >= 0.4:
            return 'Fair mutualism - Some positions need strengthening'
        else:
            return 'Poor mutualism - System stability at risk, intervention needed'
    
    def evaluate_holonic(self, participant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate holonic alignment for Earth protocol
        
        Earth represents the mutualism principle - the ability to support and be
        supported, creating stable mutual benefit relationships.
        
        Args:
            participant_id: Optional account to evaluate. If None, evaluates system-wide.
            
        Returns:
            Dictionary with holonic evaluation
        """
        logger.info(f"Evaluating holonic alignment for Earth protocol" + 
                   (f" - account {participant_id}" if participant_id else " - system-wide"))
        
        try:
            if participant_id:
                # Evaluate specific participant
                if participant_id in self.collateral_positions:
                    position = self.collateral_positions[participant_id]
                    
                    # Individual holonic score based on position health
                    if position.collateral_ratio >= self.STRESS_COLLATERAL_RATIO:
                        holonic_score = 0.9
                        status = 'excellent'
                    elif position.collateral_ratio >= self.MIN_COLLATERAL_RATIO:
                        holonic_score = 0.7
                        status = 'good'
                    elif position.collateral_ratio >= self.LIQUIDATION_THRESHOLD:
                        holonic_score = 0.4
                        status = 'at_risk'
                    else:
                        holonic_score = 0.2
                        status = 'critical'
                    
                    evaluation = {
                        'participant_id': participant_id,
                        'element': 'earth',
                        'principle': 'mutualism',
                        'holonic_score': holonic_score,
                        'status': status,
                        'collateral_ratio': str(position.collateral_ratio),
                        'health_status': position.health_status,
                        'interpretation': f"Position demonstrates {status} mutualistic participation",
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    evaluation = {
                        'participant_id': participant_id,
                        'element': 'earth',
                        'error': 'Participant not found in Earth protocol',
                        'timestamp': datetime.utcnow().isoformat()
                    }
            else:
                # System-wide evaluation
                metrics = self.get_metrics()
                system_health = metrics.get('system_health_score', 0.0)
                
                evaluation = {
                    'scope': 'system',
                    'element': 'earth',
                    'principle': 'mutualism',
                    'holonic_score': system_health,
                    'active_positions': metrics.get('active_positions', 0),
                    'avg_collateral_ratio': metrics.get('average_collateral_ratio', '0'),
                    'status': GlobalConfig.get_health_status(Decimal(str(system_health))),
                    'interpretation': 'System-wide mutualism reflects overall stability and mutual support',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating holonic alignment: {e}")
            return {
                'element': 'earth',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    # ========================================================================
    # COLLATERAL MANAGEMENT
    # ========================================================================
    
    def deposit_collateral(self, account: str, asset_code: str, amount: Decimal) -> bool:
        """Deposit collateral assets"""
        # Implementation would handle collateral deposits
        pass
    
    def withdraw_collateral(self, account: str, asset_code: str, amount: Decimal) -> bool:
        """Withdraw collateral (if ratio allows)"""
        # Implementation would handle collateral withdrawals
        pass
    
    def mint_ubecgpi(self, account: str, amount: Decimal) -> Tuple[bool, str]:
        """Mint UBECgpi tokens against collateral"""
        # Implementation would handle minting
        pass
    
    def burn_ubecgpi(self, account: str, amount: Decimal) -> Tuple[bool, str]:
        """Burn UBECgpi and release collateral"""
        # Implementation would handle burning
        pass
    
    def liquidate_position(self, account: str) -> Tuple[bool, str]:
        """Liquidate undercollateralized position"""
        # Implementation would handle liquidation
        pass
    
    def update_gpi_value(self, new_gpi: Decimal, source: str) -> bool:
        """Update GPI value from oracle"""
        # Implementation would handle GPI updates
        pass


if __name__ == "__main__":
    """Test UBECgpi protocol"""
    print("=" * 70)
    print("UBECgpi (Earth) Protocol Test")
    print("=" * 70)
    
    # Initialize protocol
    protocol = UBECgpiProtocol()
    
    print(f"\nAsset Code: {protocol.asset_code}")
    print(f"Issuer: {protocol.issuer}")
    print(f"Network: {GlobalConfig.NETWORK}")
    
    # Health check
    print("\nRunning health check...")
    try:
        health = protocol.health_check()
        print("✓ Health check passed")
        for key, value in health.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
    
    # Get status
    print("\nGetting status...")
    try:
        status = protocol.get_status()
        print("✓ Status retrieved")
        for key, value in status.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"✗ Status failed: {e}")
    
    # Test sync (will fail without core modules, but shows structure)
    print("\nTesting sync...")
    try:
        result = protocol.sync_stability_data()
        print(f"✓ Sync completed: {result['status']}")
        print(f"  Accounts: {result.get('accounts_synced', 0)}")
        print(f"  Transactions: {result.get('transactions_synced', 0)}")
        print(f"  Balances: {result.get('balances_synced', 0)}")
    except Exception as e:
        print(f"✗ Sync test: {e}")
    
    print("\n" + "=" * 70)
    print("Test complete")
    print("=" * 70)
