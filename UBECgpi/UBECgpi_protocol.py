#!/usr/bin/env python3
"""
🜃 Earth Token (UBECgpi Stability) Protocol
Ubuntu Bioregional Economic Commons

Element: Earth (🜃) - Stability, Grounding, Value Storage
Function: GPI-pegged stable token

This protocol implements the Earth element of the four-element UBEC system,
managing stability through collateralization and GPI-pegging mechanisms.

Key Responsibilities:
- Collateralized minting and burning
- GPI oracle integration
- Stability mechanisms and monitoring
- Liquidation protection
- Mutualism principle implementation

Attribution:
This project uses the services of Claude and Anthropic PBC to inform our decisions 
and recommendations. This project was made possible with the assistance of Claude 
and Anthropic PBC.

Author: UBEC Protocol Team
Version: 2.0 (Async Refactor)
Date: 2025-10-10
"""

import asyncio
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from stellar_sdk import ServerAsync, Network, Asset

# Use single config source (Principle 8: No Duplicate Configuration)
from config import settings, get_logger

logger = get_logger('ubec.UBECgpi')


@dataclass
class CollateralPosition:
    """User's collateral position for stability token minting."""
    account: str
    collateral_assets: Dict[str, Decimal]  # Asset -> Amount
    collateral_value_eur: Decimal
    ubecgpi_minted: Decimal
    collateral_ratio: Decimal
    health_status: str  # healthy, warning, critical
    last_updated: datetime
    
    @property
    def is_healthy(self) -> bool:
        """Check if position is healthy (above minimum ratio)."""
        return self.collateral_ratio >= Decimal("1.5")


@dataclass
class GPIReading:
    """GPI oracle reading for peg maintenance."""
    timestamp: datetime
    gpi_value: Decimal
    components: Dict[str, Decimal]
    oracle_source: str
    confidence: Decimal  # 0-1


class UBECgpiProtocol:
    """
    Earth Token (UBECgpi) Protocol - Fully Async
    
    Manages GPI-pegged stability token with:
    - Collateralized minting/burning
    - Oracle integration for GPI tracking
    - Stability mechanisms and monitoring
    - Liquidation protection for undercollateralized positions
    - Mutualism principle embodiment
    
    All methods are async for non-blocking I/O operations.
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
        issuer_public: Optional[str] = None,
        network: Optional[str] = None,
        horizon_url: Optional[str] = None
    ):
        """Initialize Earth Token Protocol (async)."""
        logger.info("Initializing UBECgpi (Earth) Protocol")
        
        # Use settings as single config source
        self.issuer_public = issuer_public or settings.UBECgpi_ISSUER
        self.issuer = self.issuer_public  # Alias for compatibility
        
        # Network configuration
        network = network or self._get_network_from_settings()
        
        if network == "testnet":
            self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
            self.horizon_url = horizon_url or "https://horizon-testnet.stellar.org"
        else:
            self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
            self.horizon_url = horizon_url or settings.HORIZON_URL
        
        # Set asset code and create Asset object
        self.asset_code = self.TOKEN_CODE
        self.server = ServerAsync(horizon_url=self.horizon_url)
        self.asset = Asset(self.TOKEN_CODE, self.issuer_public)
        
        # State management
        self.collateral_positions: Dict[str, CollateralPosition] = {}
        self.total_collateral_value = Decimal("0")
        self.total_minted = Decimal("0")
        self.current_gpi = Decimal("1.0")  # Target: 1 GPI unit
        self.reserve_assets: Dict[str, Decimal] = {}
        
        logger.info(f"Connected to {network} network")
        logger.info(f"UBECgpi Asset: {self.asset_code}:{self.issuer}")
        logger.info("UBECgpi Protocol: Stability & Value System")
    
    def _get_network_from_settings(self) -> str:
        """Get network name from settings."""
        if hasattr(settings, 'PUBLIC_NETWORK_PASSPHRASE'):
            if 'testnet' in settings.PUBLIC_NETWORK_PASSPHRASE.lower():
                return 'testnet'
        return 'mainnet'
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close server connection."""
        if self.server:
            await self.server.close()
    
    # ========================================================================
    # HEALTH & STATUS METHODS (ASYNC)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on UBECgpi protocol (async).
        
        Returns:
            dict: Health status information
        """
        logger.info("Performing UBECgpi protocol health check")
        
        try:
            # Verify issuer account is accessible
            try:
                await self.server.accounts().account_id(self.issuer).call()
                issuer_active = True
            except Exception as e:
                logger.warning(f"Could not verify issuer account: {e}")
                issuer_active = False
            
            status = {
                'protocol': 'UBECgpi (Earth)',
                'element': 'earth',
                'network': self._get_network_from_settings(),
                'asset_code': self.asset_code,
                'issuer': self.issuer,
                'issuer_active': issuer_active,
                'stability_monitoring': True,
                'asset_backing': True,
                'backing_ratio': float(self.MIN_COLLATERAL_RATIO),
                'stability_threshold': float(self.GPI_DEVIATION_THRESHOLD),
                'system_active': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("✓ UBECgpi protocol health check passed")
            return status
            
        except Exception as e:
            logger.error(f"✗ UBECgpi protocol health check failed: {e}")
            return {
                'protocol': 'UBECgpi (Earth)',
                'element': 'earth',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of UBECgpi system (async).
        
        Returns:
            dict: Detailed protocol statistics
        """
        logger.info("Getting UBECgpi protocol status")
        
        try:
            # Calculate basic statistics
            total_positions = len(self.collateral_positions)
            total_minted_float = float(self.total_minted)
            total_collateral_float = float(self.total_collateral_value)
            
            # Calculate system collateral ratio
            system_ratio = await self._calculate_system_ratio()
            
            status = {
                'protocol': 'UBECgpi (Earth)',
                'element': 'Earth (🜃)',
                'principle': 'Mutualism & Stability',
                'role': 'Value Stability Token',
                'asset_code': self.asset_code,
                'issuer': self.issuer,
                'network': self._get_network_from_settings(),
                
                'total_positions': total_positions,
                'total_minted': total_minted_float,
                'total_collateral_value': total_collateral_float,
                'system_collateral_ratio': float(system_ratio),
                'current_gpi_peg': float(self.current_gpi),
                
                'min_collateral_ratio': float(self.MIN_COLLATERAL_RATIO),
                'liquidation_threshold': float(self.LIQUIDATION_THRESHOLD),
                
                'system_healthy': system_ratio >= self.MIN_COLLATERAL_RATIO if self.total_minted > 0 else True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"✓ UBECgpi status retrieved: {total_positions} positions")
            return status
            
        except Exception as e:
            logger.error(f"✗ Error getting UBECgpi status: {e}")
            raise
    
    async def _calculate_system_ratio(self) -> Decimal:
        """
        Calculate system-wide collateral ratio.
        
        Returns:
            Decimal: System collateral ratio
        """
        if self.total_minted > 0:
            return self.total_collateral_value / self.total_minted
        return Decimal("0")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get Earth protocol metrics for holonic evaluation (async).
        
        Returns:
            Dictionary with stability metrics
        """
        logger.info("Calculating Earth metrics")
        
        try:
            # Count positions by health status
            position_stats = self._count_positions_by_health()
            
            # Calculate average collateral ratio
            avg_ratio = self._calculate_average_ratio()
            
            # Calculate system health score
            health_score = await self._calculate_health_score()
            
            metrics = {
                'element': 'earth',
                'token': 'UBECgpi',
                'principle': 'mutualism',
                
                'active_positions': len(self.collateral_positions),
                'healthy_positions': position_stats['healthy'],
                'warning_positions': position_stats['warning'],
                'critical_positions': position_stats['critical'],
                
                'total_minted': str(self.total_minted),
                'total_collateral_value': str(self.total_collateral_value),
                'average_collateral_ratio': str(avg_ratio),
                
                'system_health_score': health_score,
                'gpi_stability': float(self.current_gpi),
                
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"✓ Earth metrics calculated: health score {health_score:.2f}")
            return metrics
            
        except Exception as e:
            logger.error(f"✗ Error calculating Earth metrics: {e}")
            return {
                'element': 'earth',
                'token': 'UBECgpi',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _count_positions_by_health(self) -> Dict[str, int]:
        """Count positions by health status."""
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
        
        return {
            'healthy': healthy_count,
            'warning': warning_count,
            'critical': critical_count
        }
    
    def _calculate_average_ratio(self) -> Decimal:
        """Calculate average collateral ratio across all positions."""
        if self.collateral_positions:
            total_ratio = sum(p.collateral_ratio for p in self.collateral_positions.values())
            return total_ratio / len(self.collateral_positions)
        return Decimal("0")
    
    async def _calculate_health_score(self) -> float:
        """
        Calculate system health score (0-1).
        
        Returns:
            float: Health score
        """
        if self.total_minted == 0:
            return 1.0
        
        system_ratio = await self._calculate_system_ratio()
        
        if system_ratio >= self.STRESS_COLLATERAL_RATIO:
            return 1.0
        elif system_ratio >= self.MIN_COLLATERAL_RATIO:
            return 0.7
        else:
            return 0.4
    
    # ========================================================================
    # DATA SYNCHRONIZATION (ASYNC)
    # ========================================================================
    
    async def sync_stability_data(self) -> Dict[str, Any]:
        """
        Synchronize Earth (stability) distribution data (async).
        
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
            # TODO: Replace with service registry pattern
            from db.ubec_data_synchronizer import UBECDataSynchronizer
            from core.distribution.ubec_distribution_manager import UBECDistributionManager
            
            # Initialize modules
            async with UBECDataSynchronizer() as synchronizer:
                
                # Track overall results
                sync_results = {
                    'accounts': 0,
                    'transactions': 0,
                    'balances': 0,
                    'errors': []
                }
                
                # Sync accounts
                await self._sync_accounts(synchronizer, sync_results)
                
                # Sync transactions
                await self._sync_transactions(synchronizer, sync_results)
                
                # Sync balances
                await self._sync_balances(synchronizer, sync_results)
                
                # Check distribution compliance
                compliance_status = await self._check_distribution_compliance()
                
                # Create snapshot
                snapshot_id = await self._create_distribution_snapshot()
                
                # Calculate stability metrics
                stability_metrics = self._calculate_stability_metrics(
                    sync_results['accounts'],
                    sync_results['balances'],
                    compliance_status
                )
                
                # Build result
                result = self._build_sync_result(
                    sync_results,
                    compliance_status,
                    stability_metrics,
                    snapshot_id
                )
                
                logger.info(f"  ✓ Earth sync complete: {result['accounts_synced']} accounts, "
                           f"compliance: {result['distribution_compliant']}")
                
                if sync_results['errors']:
                    logger.warning(f"  ⚠ Sync completed with {len(sync_results['errors'])} errors")
                
                return result
            
        except ImportError as e:
            logger.error(f"  ✗ Cannot import required modules: {e}")
            return self._build_error_result('Module import error', str(e))
        except Exception as e:
            logger.error(f"  ✗ Fatal error syncing Earth data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._build_error_result('Fatal sync error', str(e))
    
    async def _sync_accounts(self, synchronizer, results: Dict):
        """Sync account data."""
        logger.info("  Syncing UBECgpi accounts...")
        try:
            accounts_result = await synchronizer.sync_account_data(asset_code='UBECgpi')
            results['accounts'] = accounts_result.get('synced', 0)
            logger.info(f"    ✓ Synced {results['accounts']} accounts")
        except Exception as e:
            error_msg = f"Error syncing accounts: {str(e)}"
            logger.error(f"    ✗ {error_msg}")
            results['errors'].append(error_msg)
    
    async def _sync_transactions(self, synchronizer, results: Dict):
        """Sync transaction data."""
        logger.info("  Syncing UBECgpi transactions...")
        try:
            transactions_result = await synchronizer.sync_transaction_data(asset_code='UBECgpi')
            results['transactions'] = transactions_result.get('synced', 0)
            logger.info(f"    ✓ Synced {results['transactions']} transactions")
        except Exception as e:
            error_msg = f"Error syncing transactions: {str(e)}"
            logger.error(f"    ✗ {error_msg}")
            results['errors'].append(error_msg)
    
    async def _sync_balances(self, synchronizer, results: Dict):
        """Sync balance data."""
        logger.info("  Syncing UBECgpi balances...")
        try:
            balances_result = await synchronizer.sync_balance_data(asset_code='UBECgpi')
            results['balances'] = balances_result.get('synced', 0)
            logger.info(f"    ✓ Synced {results['balances']} balances")
        except Exception as e:
            error_msg = f"Error syncing balances: {str(e)}"
            logger.error(f"    ✗ {error_msg}")
            results['errors'].append(error_msg)
    
    async def _check_distribution_compliance(self) -> Dict[str, Any]:
        """Check distribution compliance."""
        logger.info("  Checking distribution compliance...")
        try:
            from core.distribution.ubec_distribution_manager import UBECDistributionManager
            distribution_mgr = UBECDistributionManager()
            
            compliance_status = distribution_mgr.check_compliance(asset_code='UBECgpi')
            is_compliant = compliance_status.get('compliant', False)
            logger.info(f"    {'✓' if is_compliant else '⚠'} Compliance: {is_compliant}")
            return compliance_status
        except Exception as e:
            error_msg = f"Error checking compliance: {str(e)}"
            logger.error(f"    ✗ {error_msg}")
            return {'compliant': False, 'error': str(e)}
    
    async def _create_distribution_snapshot(self) -> Optional[int]:
        """Create distribution snapshot."""
        logger.info("  Creating distribution snapshot...")
        try:
            from core.distribution.ubec_distribution_manager import UBECDistributionManager
            distribution_mgr = UBECDistributionManager()
            
            snapshot_id = distribution_mgr.snapshot_distribution(asset_code='UBECgpi')
            if snapshot_id:
                logger.info(f"    ✓ Snapshot created with ID: {snapshot_id}")
            return snapshot_id
        except Exception as e:
            error_msg = f"Error creating snapshot: {str(e)}"
            logger.error(f"    ✗ {error_msg}")
            return None
    
    def _calculate_stability_metrics(self, accounts: int, balances: int, 
                                     compliance: Dict) -> Dict:
        """
        Calculate stability metrics for Earth protocol.
        
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
            deviation = self._calculate_distribution_deviation(compliance)
            
            # Stability score (1.0 = perfect, 0.0 = maximum deviation)
            stability_score = max(0.0, 1.0 - (deviation / 15.0))
            
            # Determine distribution health
            distribution_health = self._determine_distribution_health(is_compliant, deviation)
            
            return {
                'stability_score': round(stability_score, 2),
                'distribution_health': distribution_health,
                'total_deviation': round(deviation, 2),
                'compliant': is_compliant
            }
            
        except Exception as e:
            logger.warning(f"Error calculating stability metrics: {e}")
            return {
                'stability_score': 0.0,
                'distribution_health': 'ERROR'
            }
    
    def _calculate_distribution_deviation(self, compliance: Dict) -> float:
        """Calculate total deviation from target distribution."""
        target_general = 75.0
        target_stewardship = 20.0
        target_admin = 5.0
        
        actual_general = compliance.get('general_circulation_pct', 0.0)
        actual_stewardship = compliance.get('stewardship_pct', 0.0)
        actual_admin = compliance.get('administration_pct', 0.0)
        
        return (
            abs(actual_general - target_general) +
            abs(actual_stewardship - target_stewardship) +
            abs(actual_admin - target_admin)
        )
    
    def _determine_distribution_health(self, is_compliant: bool, deviation: float) -> str:
        """Determine distribution health status."""
        if is_compliant:
            return 'STABLE'
        elif deviation < 10.0:
            return 'MINOR_DEVIATION'
        elif deviation < 20.0:
            return 'MODERATE_DEVIATION'
        else:
            return 'MAJOR_DEVIATION'
    
    def _build_sync_result(self, sync_results: Dict, compliance: Dict,
                          stability: Dict, snapshot_id: Optional[int]) -> Dict[str, Any]:
        """Build final sync result dictionary."""
        return {
            'element': 'earth',
            'token': 'UBECgpi',
            'asset_code': self.asset_code,
            'issuer': self.issuer,
            'accounts_synced': sync_results['accounts'],
            'transactions_synced': sync_results['transactions'],
            'balances_synced': sync_results['balances'],
            'distribution_compliant': compliance.get('compliant', False),
            'general_circulation_pct': compliance.get('general_circulation_pct', 0.0),
            'stewardship_pct': compliance.get('stewardship_pct', 0.0),
            'administration_pct': compliance.get('administration_pct', 0.0),
            'stability_score': stability.get('stability_score', 0.0),
            'distribution_health': stability.get('distribution_health', 'UNKNOWN'),
            'snapshot_id': snapshot_id,
            'errors': sync_results['errors'] if sync_results['errors'] else None,
            'status': 'success' if not sync_results['errors'] else 'partial',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _build_error_result(self, error_type: str, error_detail: str) -> Dict[str, Any]:
        """Build error result dictionary."""
        return {
            'element': 'earth',
            'token': 'UBECgpi',
            'asset_code': self.asset_code,
            'issuer': self.issuer,
            'status': 'error',
            'error': error_type,
            'error_detail': error_detail,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # ========================================================================
    # UBUNTU PRINCIPLE ASSESSMENT (ASYNC)
    # ========================================================================
    
    async def assess_mutualism(self) -> Dict[str, Any]:
        """
        Assess mutualism principle (Earth's ubuntu principle) (async).
        
        Returns:
            Dictionary with mutualism assessment
        """
        logger.info("Assessing mutualism principle for Earth element")
        
        try:
            metrics = await self.get_metrics()
            
            # Extract mutualism metrics
            avg_collateral_ratio = Decimal(metrics.get('average_collateral_ratio', '0'))
            active_positions = metrics.get('active_positions', 0)
            
            # Calculate mutualism score
            mutualism_score = self._calculate_mutualism_score(avg_collateral_ratio)
            
            assessment = {
                'principle': 'mutualism',
                'element': 'earth',
                'score': mutualism_score,
                'avg_collateral_ratio': str(avg_collateral_ratio),
                'active_positions': active_positions,
                'status': self._determine_principle_status(mutualism_score),
                'interpretation': self._interpret_mutualism_score(mutualism_score),
                'recommendations': self._generate_mutualism_recommendations(mutualism_score),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"  ✓ Mutualism assessment complete: score {mutualism_score:.2f}")
            return assessment
            
        except Exception as e:
            logger.error(f"  ✗ Error assessing mutualism: {e}")
            return {
                'principle': 'mutualism',
                'element': 'earth',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_mutualism_score(self, avg_collateral_ratio: Decimal) -> float:
        """Calculate mutualism score from collateral ratio."""
        if avg_collateral_ratio > Decimal('1.75'):
            return 0.9
        elif avg_collateral_ratio > Decimal('1.5'):
            return 0.7
        elif avg_collateral_ratio > Decimal('1.4'):
            return 0.5
        else:
            return 0.3
    
    def _determine_principle_status(self, score: float) -> str:
        """Determine principle status from score."""
        if score > 0.7:
            return 'excellent'
        elif score > 0.5:
            return 'good'
        else:
            return 'needs_improvement'
    
    def _interpret_mutualism_score(self, score: float) -> str:
        """Interpret mutualism score with context."""
        if score >= 0.8:
            return 'Excellent mutualism - Strong stable ecosystem with healthy backing'
        elif score >= 0.6:
            return 'Good mutualism - System is stable with adequate collateralization'
        elif score >= 0.4:
            return 'Fair mutualism - Some positions need strengthening'
        else:
            return 'Poor mutualism - System stability at risk, intervention needed'
    
    def _generate_mutualism_recommendations(self, score: float) -> List[str]:
        """Generate recommendations based on mutualism score."""
        recommendations = []
        
        if score < 0.5:
            recommendations.append("Increase collateral requirements to improve system stability")
            recommendations.append("Implement position monitoring and early warning systems")
        
        if score < 0.7:
            recommendations.append("Encourage participants to strengthen collateral positions")
            recommendations.append("Review liquidation thresholds")
        
        if score < 0.9:
            recommendations.append("Continue monitoring system-wide collateral health")
        
        return recommendations if recommendations else ["Maintain current mutualism levels"]
    
    # ========================================================================
    # HOLONIC EVALUATION (ASYNC)
    # ========================================================================
    
    async def evaluate_holonic(self, participant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate holonic alignment for Earth protocol (async).
        
        Earth represents the mutualism principle - the ability to support and be
        supported, creating stable mutual benefit relationships.
        
        Args:
            participant_id: Optional account to evaluate. If None, evaluates system-wide.
            
        Returns:
            Dictionary with holonic evaluation
        """
        logger.info(f"Evaluating holonic alignment for Earth protocol" + 
                   (f" - account {participant_id[:8]}..." if participant_id else " - system-wide"))
        
        try:
            if participant_id:
                return await self._evaluate_participant(participant_id)
            else:
                return await self._evaluate_system()
            
        except Exception as e:
            logger.error(f"✗ Error evaluating holonic alignment: {e}")
            return {
                'element': 'earth',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _evaluate_participant(self, participant_id: str) -> Dict[str, Any]:
        """Evaluate individual participant."""
        if participant_id in self.collateral_positions:
            position = self.collateral_positions[participant_id]
            
            # Calculate holonic score based on position health
            holonic_score, status = self._calculate_participant_score(position)
            
            return {
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
            return {
                'participant_id': participant_id,
                'element': 'earth',
                'error': 'Participant not found in Earth protocol',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_participant_score(self, position: CollateralPosition) -> Tuple[float, str]:
        """Calculate participant holonic score and status."""
        if position.collateral_ratio >= self.STRESS_COLLATERAL_RATIO:
            return 0.9, 'excellent'
        elif position.collateral_ratio >= self.MIN_COLLATERAL_RATIO:
            return 0.7, 'good'
        elif position.collateral_ratio >= self.LIQUIDATION_THRESHOLD:
            return 0.4, 'at_risk'
        else:
            return 0.2, 'critical'
    
    async def _evaluate_system(self) -> Dict[str, Any]:
        """Evaluate system-wide holonic alignment."""
        metrics = await self.get_metrics()
        system_health = metrics.get('system_health_score', 0.0)
        
        return {
            'scope': 'system',
            'element': 'earth',
            'principle': 'mutualism',
            'holonic_score': system_health,
            'active_positions': metrics.get('active_positions', 0),
            'avg_collateral_ratio': metrics.get('average_collateral_ratio', '0'),
            'status': self._determine_health_status(Decimal(str(system_health))),
            'interpretation': 'System-wide mutualism reflects overall stability and mutual support',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _determine_health_status(self, score: Decimal) -> str:
        """Determine health status from score."""
        if score >= Decimal('0.8'):
            return 'excellent'
        elif score >= Decimal('0.6'):
            return 'good'
        elif score >= Decimal('0.4'):
            return 'adequate'
        else:
            return 'needs_attention'
    
    # ========================================================================
    # COLLATERAL MANAGEMENT (PLACEHOLDER - Future Implementation)
    # ========================================================================
    
    async def deposit_collateral(self, account: str, asset_code: str, 
                                amount: Decimal) -> bool:
        """
        Deposit collateral assets (async).
        
        Args:
            account: Account ID
            asset_code: Asset to deposit
            amount: Amount to deposit
            
        Returns:
            bool: Success status
        """
        # TODO: Implement collateral deposit logic
        logger.info(f"Collateral deposit: {account[:8]}... - {amount} {asset_code}")
        return False
    
    async def withdraw_collateral(self, account: str, asset_code: str, 
                                 amount: Decimal) -> bool:
        """
        Withdraw collateral (if ratio allows) (async).
        
        Args:
            account: Account ID
            asset_code: Asset to withdraw
            amount: Amount to withdraw
            
        Returns:
            bool: Success status
        """
        # TODO: Implement collateral withdrawal logic
        logger.info(f"Collateral withdrawal: {account[:8]}... - {amount} {asset_code}")
        return False
    
    async def mint_ubecgpi(self, account: str, amount: Decimal) -> Tuple[bool, str]:
        """
        Mint UBECgpi tokens against collateral (async).
        
        Args:
            account: Account ID
            amount: Amount to mint
            
        Returns:
            Tuple of (success, message)
        """
        # TODO: Implement minting logic
        logger.info(f"Minting UBECgpi: {account[:8]}... - {amount}")
        return False, "Not yet implemented"
    
    async def burn_ubecgpi(self, account: str, amount: Decimal) -> Tuple[bool, str]:
        """
        Burn UBECgpi and release collateral (async).
        
        Args:
            account: Account ID
            amount: Amount to burn
            
        Returns:
            Tuple of (success, message)
        """
        # TODO: Implement burning logic
        logger.info(f"Burning UBECgpi: {account[:8]}... - {amount}")
        return False, "Not yet implemented"
    
    async def liquidate_position(self, account: str) -> Tuple[bool, str]:
        """
        Liquidate undercollateralized position (async).
        
        Args:
            account: Account ID
            
        Returns:
            Tuple of (success, message)
        """
        # TODO: Implement liquidation logic
        logger.info(f"Liquidating position: {account[:8]}...")
        return False, "Not yet implemented"
    
    async def update_gpi_value(self, new_gpi: Decimal, source: str) -> bool:
        """
        Update GPI value from oracle (async).
        
        Args:
            new_gpi: New GPI value
            source: Oracle source
            
        Returns:
            bool: Success status
        """
        # TODO: Implement GPI update logic
        logger.info(f"Updating GPI value: {new_gpi} from {source}")
        self.current_gpi = new_gpi
        return True


# ============================================================================
# ASYNC TEST FUNCTION (for development/testing only)
# ============================================================================

async def test_ubecgpi_protocol():
    """Test function for UBECgpi protocol (async)."""
    print("\n" + "=" * 70)
    print("TESTING UBECgpi PROTOCOL (Async Version)")
    print("=" * 70)
    
    async with UBECgpiProtocol() as protocol:
        try:
            print(f"\nAsset Code: {protocol.asset_code}")
            print(f"Issuer: {protocol.issuer}")
            
            print("\n1. Health check...")
            health = await protocol.health_check()
            print(f"   Status: {health.get('status', 'unknown')}")
            
            print("\n2. Get status...")
            status = await protocol.get_status()
            print(f"   Positions: {status.get('total_positions', 0)}")
            print(f"   System healthy: {status.get('system_healthy', False)}")
            
            print("\n3. Assess mutualism...")
            mutualism = await protocol.assess_mutualism()
            print(f"   Score: {mutualism.get('score', 0):.2f}")
            
            print("\n" + "=" * 70)
            print("✓ ALL TESTS COMPLETED!")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # For testing only - should not be used in production
    # Production execution should be through main.py
    asyncio.run(test_ubecgpi_protocol())
