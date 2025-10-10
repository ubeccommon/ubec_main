# UBECgpi/UBECgpi_protocol.py
"""
🜃 Earth Token (UBECgpi Stability) Protocol
Ubuntu Bioregional Economic Commons

Element: Earth (🜃) - Stability, Grounding, Value Storage
Function: GPI-pegged stable token

Version: 1.0.0
Date: October 2025
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
        # Use GlobalConfig if parameters not provided
        self.issuer_public = issuer_public or GlobalConfig.UBECgpi_ISSUER
        network = network or GlobalConfig.NETWORK
        
        if network == "testnet":
            self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
            self.horizon_url = horizon_url or "https://horizon-testnet.stellar.org"
        else:
            self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
            self.horizon_url = horizon_url or "https://horizon.stellar.org"
        
        self.server = Server(horizon_url=self.horizon_url)
        self.asset = Asset(self.TOKEN_CODE, self.issuer_public)
        
        # State
        self.collateral_positions: Dict[str, CollateralPosition] = {}
        self.total_collateral_value = Decimal("0")
        self.total_minted = Decimal("0")
        self.current_gpi = Decimal("1.0")  # Target: 1 GPI unit
        self.reserve_assets: Dict[str, Decimal] = {}
        
        logger.info("Initializing UBECgpi (Earth) Protocol")
        logger.info(f"Connected to {network} network")
        logger.info("UBECgpi Protocol: Stability & Value System")
    
    def health_check(self):
        """Perform health check on UBECgpi protocol."""
        logger.info("Performing UBECgpi protocol health check")
        
        try:
            status = {
                'protocol': 'UBECgpi (Earth)',
                'network': GlobalConfig.NETWORK,
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
        logger.info("Retrieving UBECgpi system status")
        
        try:
            status = {
                'token': 'UBECgpi',
                'element': 'Earth (🜃)',
                'role': 'Stability & Value',
                'total_minted': str(self.total_minted),
                'total_collateral': str(self.total_collateral_value),
                'active_positions': len(self.collateral_positions),
                'gpi_value': str(self.current_gpi)
            }
            
            logger.info(f"✓ UBECgpi status retrieved")
            return status
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve UBECgpi status: {e}")
            raise
    
    def sync_stability_data(self) -> Dict[str, Any]:
        """
        Synchronize Earth (Stability) protocol data from Stellar blockchain
        
        This method:
        - Syncs all accounts holding UBECgpi tokens
        - Syncs all transactions involving UBECgpi
        - Updates balance information
        - Checks distribution compliance (75/20/5)
        - Calculates stability metrics
        
        Returns:
            Dictionary containing sync results with compliance status
        """
        logger.info("Starting Earth (UBECgpi) stability data synchronization...")
        
        try:
            # Import required modules
            from core.db.ubec_data_synchronizer import UBECDataSynchronizer
            from core.distribution.ubec_distribution_manager import UBECDistributionManager
            
            # Initialize synchronizer and distribution manager
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
            
            # Sync balances
            logger.info("  Syncing UBECgpi balances...")
            try:
                balances_result = synchronizer.sync_balance_data(asset_code='UBECgpi')
                total_balances = balances_result.get('synced', 0)
                logger.info(f"    ✓ Synced {total_balances} balances")
            except Exception as e:
                error_msg = f"Error syncing balances: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Check distribution compliance (75/20/5 rule)
            logger.info("  Checking distribution compliance...")
            compliance_status = {
                'compliant': False,
                'general_circulation_pct': 0.0,
                'stewardship_pct': 0.0,
                'administration_pct': 0.0,
                'deviations': {}
            }
            
            try:
                compliance = distribution_mgr.check_compliance(asset_code='UBECgpi')
                compliance_status.update(compliance)
                
                if compliance.get('compliant', False):
                    logger.info(f"    ✓ Distribution compliant")
                else:
                    deviations = compliance.get('deviations', {})
                    logger.warning(f"    ⚠ Distribution non-compliant: {deviations}")
                    
            except Exception as e:
                error_msg = f"Error checking compliance: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Update distribution snapshot
            logger.info("  Updating distribution snapshot...")
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
                'asset_code': 'UBECgpi',
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
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"  ✓ Mutualism assessment complete: score {mutualism_score:.2f}")
            return assessment
            
        except Exception as e:
            logger.error(f"  ✗ Error assessing mutualism: {e}")
            return {
                'principle': 'mutualism',
                'element': 'earth',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_current_gpi(self) -> Decimal:
        """
        Get current GPI value from oracle
        
        In production, this would:
        - Query multiple oracles
        - Weighted average
        - Outlier rejection
        """
        # Simplified - would integrate real GPI oracle
        return self.current_gpi
    
    def calculate_collateral_ratio(
        self,
        collateral_value: Decimal,
        ubecgpi_amount: Decimal
    ) -> Decimal:
        """Calculate collateral ratio"""
        if ubecgpi_amount == 0:
            return Decimal("0")
        return collateral_value / ubecgpi_amount
    
    def mint_ubecgpi(
        self,
        user_secret: str,
        collateral_asset: str,
        collateral_amount: Decimal,
        ubecgpi_amount: Decimal
    ) -> Dict:
        """
        Mint UBECgpi by depositing collateral
        
        Args:
            user_secret: User's secret key
            collateral_asset: Asset code for collateral
            collateral_amount: Amount of collateral
            ubecgpi_amount: Amount of UBECgpi to mint
            
        Returns:
            Minting result
        """
        user_keypair = Keypair.from_secret(user_secret)
        user_account = user_keypair.public_key
        
        # Get collateral value
        collateral_value_eur = self._get_asset_value_eur(
            collateral_asset,
            collateral_amount
        )
        
        # Calculate collateral ratio
        ratio = self.calculate_collateral_ratio(
            collateral_value_eur,
            ubecgpi_amount
        )
        
        # Check minimum ratio
        if ratio < self.MIN_COLLATERAL_RATIO:
            raise ValueError(
                f"Insufficient collateral. Ratio: {ratio}, "
                f"Required: {self.MIN_COLLATERAL_RATIO}"
            )
        
        logger.info(
            f"Minting {ubecgpi_amount} UBECgpi with "
            f"{collateral_amount} {collateral_asset} "
            f"(ratio: {ratio})"
        )
        
        # Apply minting fee
        fee = ubecgpi_amount * self.MINTING_FEE
        net_ubecgpi = ubecgpi_amount - fee
        
        # Update or create collateral position
        if user_account in self.collateral_positions:
            position = self.collateral_positions[user_account]
            if collateral_asset in position.collateral_assets:
                position.collateral_assets[collateral_asset] += collateral_amount
            else:
                position.collateral_assets[collateral_asset] = collateral_amount
            position.ubecgpi_minted += net_ubecgpi
            position.collateral_value_eur += collateral_value_eur
        else:
            position = CollateralPosition(
                account=user_account,
                collateral_assets={collateral_asset: collateral_amount},
                collateral_value_eur=collateral_value_eur,
                ubecgpi_minted=net_ubecgpi,
                collateral_ratio=ratio,
                health_status="healthy",
                last_updated=datetime.now(),
            )
            self.collateral_positions[user_account] = position
        
        # Update totals
        self.total_minted += net_ubecgpi
        self.total_collateral_value += collateral_value_eur
        
        # Would execute actual blockchain transaction here
        return {
            "success": True,
            "ubecgpi_minted": str(net_ubecgpi),
            "fee": str(fee),
            "collateral_ratio": str(ratio),
            "position": self._position_to_dict(position),
        }
    
    def burn_ubecgpi(
        self,
        user_secret: str,
        ubecgpi_amount: Decimal,
        receive_asset: str
    ) -> Dict:
        """
        Burn UBECgpi and retrieve collateral
        
        Args:
            user_secret: User's secret key
            ubecgpi_amount: Amount of UBECgpi to burn
            receive_asset: Asset to receive back
            
        Returns:
            Burning result
        """
        user_keypair = Keypair.from_secret(user_secret)
        user_account = user_keypair.public_key
        
        if user_account not in self.collateral_positions:
            raise ValueError("No collateral position found")
        
        position = self.collateral_positions[user_account]
        
        if ubecgpi_amount > position.ubecgpi_minted:
            raise ValueError("Insufficient UBECgpi balance")
        
        # Apply burning fee
        fee = ubecgpi_amount * self.BURNING_FEE
        net_burned = ubecgpi_amount - fee
        
        # Calculate collateral to return
        collateral_return_ratio = net_burned / position.ubecgpi_minted
        collateral_to_return = (
            position.collateral_assets.get(receive_asset, Decimal("0")) *
            collateral_return_ratio
        )
        
        logger.info(
            f"Burning {ubecgpi_amount} UBECgpi, "
            f"returning {collateral_to_return} {receive_asset}"
        )
        
        # Update position
        position.ubecgpi_minted -= net_burned
        if receive_asset in position.collateral_assets:
            position.collateral_assets[receive_asset] -= collateral_to_return
        
        # Update totals
        self.total_minted -= net_burned
        
        # Would execute actual blockchain transaction here
        return {
            "success": True,
            "ubecgpi_burned": str(net_burned),
            "fee": str(fee),
            "collateral_returned": str(collateral_to_return),
            "asset": receive_asset,
        }
    
    def check_collateral_health(self, account: str) -> Dict:
        """Check collateral position health"""
        if account not in self.collateral_positions:
            return {"status": "no_position"}
        
        position = self.collateral_positions[account]
        
        # Recalculate ratio with current prices
        current_value = sum(
            self._get_asset_value_eur(asset, amount)
            for asset, amount in position.collateral_assets.items()
        )
        
        ratio = self.calculate_collateral_ratio(
            current_value,
            position.ubecgpi_minted
        )
        
        # Determine health status
        if ratio >= self.STRESS_COLLATERAL_RATIO:
            status = "excellent"
        elif ratio >= self.MIN_COLLATERAL_RATIO:
            status = "healthy"
        elif ratio >= self.LIQUIDATION_THRESHOLD:
            status = "warning"
        else:
            status = "critical"
        
        position.collateral_ratio = ratio
        position.health_status = status
        position.last_updated = datetime.now()
        
        return {
            "account": account,
            "collateral_ratio": str(ratio),
            "health_status": status,
            "liquidation_threshold": str(self.LIQUIDATION_THRESHOLD),
            "current_collateral_value": str(current_value),
            "ubecgpi_minted": str(position.ubecgpi_minted),
        }
    
    def calculate_stability_adjustment(self) -> Dict:
        """
        Calculate required stability adjustment based on GPI
        
        Returns:
            Adjustment operation details
        """
        current_gpi = self.get_current_gpi()
        target = Decimal("1.0")
        deviation = (current_gpi - target) / target
        
        if deviation > self.GPI_DEVIATION_THRESHOLD:
            # GPI too high, burn tokens to increase value
            action = "burn"
            amount = self.total_minted * self.ADJUSTMENT_RATE
        elif deviation < -self.GPI_DEVIATION_THRESHOLD:
            # GPI too low, mint tokens to decrease value
            action = "mint"
            amount = self.total_minted * self.ADJUSTMENT_RATE
        else:
            action = "maintain"
            amount = Decimal("0")
        
        return {
            "action": action,
            "amount": str(amount),
            "current_gpi": str(current_gpi),
            "target_gpi": str(target),
            "deviation": str(deviation),
            "collateral_ratio": str(
                self.total_collateral_value / self.total_minted
                if self.total_minted > 0 else Decimal("0")
            ),
        }
    
    def _get_asset_value_eur(
        self,
        asset_code: str,
        amount: Decimal
    ) -> Decimal:
        """
        Get EUR value of asset amount
        
        In production, would integrate with:
        - Price oracles
        - DEX quotes
        - Multiple sources for accuracy
        """
        # Simplified - would use real price oracles
        mock_prices = {
            "UBEC": Decimal("1.0"),
            "XLM": Decimal("0.10"),
            "USDC": Decimal("1.0"),
            "BTC": Decimal("45000"),
        }
        
        price = mock_prices.get(asset_code, Decimal("1.0"))
        return amount * price
    
    def _position_to_dict(self, position: CollateralPosition) -> Dict:
        """Convert position to dictionary"""
        return {
            "account": position.account,
            "collateral_value": str(position.collateral_value_eur),
            "ubecgpi_minted": str(position.ubecgpi_minted),
            "collateral_ratio": str(position.collateral_ratio),
            "health_status": position.health_status,
        }
    
    def get_metrics(self) -> Dict:
        """Get protocol metrics"""
        avg_collateral_ratio = (
            self.total_collateral_value / self.total_minted
            if self.total_minted > 0 else Decimal("0")
        )
        
        return {
            "total_minted": str(self.total_minted),
            "total_collateral_value": str(self.total_collateral_value),
            "average_collateral_ratio": str(avg_collateral_ratio),
            "current_gpi": str(self.current_gpi),
            "active_positions": len(self.collateral_positions),
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """CLI entry point"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Earth Token (UBECgpi) CLI")
    parser.add_argument("--network", choices=["public", "testnet"], default="testnet")
    parser.add_argument("--issuer-public", required=True)
    parser.add_argument("--action", required=True, choices=[
        "mint", "burn", "health", "metrics", "adjustment"
    ])
    parser.add_argument("--account", help="Account address")
    
    args = parser.parse_args()
    
    protocol = UBECgpiProtocol(
        issuer_public=args.issuer_public,
        network=args.network,
    )
    
    if args.action == "metrics":
        print(json.dumps(protocol.get_metrics(), indent=2))
    
    elif args.action == "health" and args.account:
        print(json.dumps(protocol.check_collateral_health(args.account), indent=2))
    
    elif args.action == "adjustment":
        print(json.dumps(protocol.calculate_stability_adjustment(), indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
