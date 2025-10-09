# UBEC/UBEC_protocol.py
"""
🜁 UBEC (Air) Token Protocol - Gateway & Access
Universal Basic Economic Commons - Entry point to the holonic economy

Element: Air
Principle: Freedom of movement, accessibility, universal access
Role: Gateway token providing entry to the Ubuntu Economic Commons
"""

from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from stellar_sdk import Server, Asset
from config import GlobalConfig, get_logger
from UBEC.config import UBECConfig

logger = get_logger('UBEC')


class UBECProtocol:
    """
    UBEC (Air) Token Protocol Implementation.
    
    The Air element represents freedom, movement, and universal access.
    UBEC serves as the gateway token, providing entry and basic access
    to the Ubuntu Economic Commons ecosystem.
    
    Key Functions:
    - Universal basic access to the economic commons
    - Onboarding and initial distribution
    - Gateway to other elemental tokens
    - Basic transaction capabilities
    """
    
    def __init__(self):
        """Initialize UBEC protocol with Stellar network connection."""
        logger.info("Initializing UBEC (Air) Protocol")
        
        self.server = Server(horizon_url=GlobalConfig.get_horizon_url())
        self.asset = Asset(GlobalConfig.UBEC_CODE, GlobalConfig.UBEC_ISSUER)
        
        logger.info(f"Connected to {GlobalConfig.NETWORK} network")
        logger.info(f"UBEC Asset: {GlobalConfig.UBEC_CODE}:{GlobalConfig.UBEC_ISSUER}")
    
    def health_check(self):
        """
        Perform health check on UBEC protocol.
        
        Returns:
            dict: Health status information
        """
        logger.info("Performing UBEC protocol health check")
        
        try:
            # Check issuer account exists and is accessible
            issuer_account = self.server.accounts().account_id(GlobalConfig.UBEC_ISSUER).call()
            
            # Check asset statistics
            assets = self.server.assets().for_code(GlobalConfig.UBEC_CODE).call()
            
            ubec_asset = None
            for asset in assets['_embedded']['records']:
                if asset['asset_issuer'] == GlobalConfig.UBEC_ISSUER:
                    ubec_asset = asset
                    break
            
            status = {
                'protocol': 'UBEC (Air)',
                'network': GlobalConfig.NETWORK,
                'issuer_active': True,
                'asset_code': GlobalConfig.UBEC_CODE,
                'total_supply': ubec_asset.get('amount', 'unknown') if ubec_asset else 'unknown',
                'num_accounts': ubec_asset.get('num_accounts', 0) if ubec_asset else 0,
                'transaction_fee_rate': float(UBECConfig.TRANSACTION_FEE_RATE),
                'gateway_active': True
            }
            
            logger.info("✓ UBEC protocol health check passed")
            return status
            
        except Exception as e:
            logger.error(f"✗ UBEC protocol health check failed: {e}")
            raise
    
    def get_status(self):
        """
        Get comprehensive status of UBEC token.
        
        Returns:
            dict: Detailed token statistics
        """
        logger.info("Retrieving UBEC token status")
        
        try:
            # Get asset statistics
            assets = self.server.assets()\
                .for_code(GlobalConfig.UBEC_CODE)\
                .for_issuer(GlobalConfig.UBEC_ISSUER)\
                .call()
            
            if not assets['_embedded']['records']:
                raise ValueError("UBEC asset not found")
            
            asset_data = assets['_embedded']['records'][0]
            
            status = {
                'token': 'UBEC',
                'element': 'Air (🜁)',
                'role': 'Gateway & Access',
                'total_supply': asset_data.get('amount', '0'),
                'total_holders': int(asset_data.get('num_accounts', 0)),
                'authorized': int(asset_data.get('num_accounts', 0)),
                'circulation_ratio': self._calculate_circulation_ratio(asset_data),
                'accessibility_score': self._calculate_accessibility_score(asset_data)
            }
            
            logger.info(f"✓ UBEC status retrieved: {status['total_holders']} holders")
            return status
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve UBEC status: {e}")
            raise
    
    def sync_gateway_data(self) -> Dict[str, Any]:
        """
        Synchronize Air (Gateway) protocol data from Stellar blockchain
        
        This method:
        - Syncs all accounts holding UBEC tokens
        - Syncs all transactions involving UBEC
        - Updates balance information
        - Provides gateway access metrics
        
        Returns:
            Dictionary containing sync results with counts and status
        """
        logger.info("Starting Air (UBEC) gateway data synchronization...")
        
        try:
            # Import the synchronizer
            from core.db.ubec_data_synchronizer import UBECDataSynchronizer
            
            # Initialize synchronizer with database connection
            synchronizer = UBECDataSynchronizer()
            
            # Track overall results
            total_accounts = 0
            total_transactions = 0
            total_balances = 0
            errors = []
            
            # Sync accounts for UBEC token
            logger.info("  Syncing UBEC accounts...")
            try:
                accounts_result = synchronizer.sync_account_data(asset_code='UBEC')
                total_accounts = accounts_result.get('synced', 0)
                logger.info(f"    ✓ Synced {total_accounts} accounts")
            except Exception as e:
                error_msg = f"Error syncing accounts: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Sync transactions
            logger.info("  Syncing UBEC transactions...")
            try:
                transactions_result = synchronizer.sync_transaction_data(asset_code='UBEC')
                total_transactions = transactions_result.get('synced', 0)
                logger.info(f"    ✓ Synced {total_transactions} transactions")
            except Exception as e:
                error_msg = f"Error syncing transactions: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Sync balances
            logger.info("  Syncing UBEC balances...")
            try:
                balances_result = synchronizer.sync_balance_data(asset_code='UBEC')
                total_balances = balances_result.get('synced', 0)
                logger.info(f"    ✓ Synced {total_balances} balances")
            except Exception as e:
                error_msg = f"Error syncing balances: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Calculate gateway metrics
            logger.info("  Calculating gateway metrics...")
            gateway_metrics = {
                'total_accounts': total_accounts,
                'active_accounts': total_accounts,  # All accounts with balance > 0
                'total_supply_distributed': total_balances,
                'gateway_accessibility': 1.0 if total_accounts > 0 else 0.0
            }
            
            # Build result
            result = {
                'element': 'air',
                'token': 'UBEC',
                'asset_code': 'UBEC',
                'issuer': self.asset.issuer,
                'accounts_synced': total_accounts,
                'transactions_synced': total_transactions,
                'balances_synced': total_balances,
                'gateway_metrics': gateway_metrics,
                'errors': errors if errors else None,
                'status': 'success' if not errors else 'partial',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"  ✓ Air sync complete: {result['accounts_synced']} accounts, "
                       f"{result['transactions_synced']} transactions, "
                       f"{result['balances_synced']} balances")
            
            if errors:
                logger.warning(f"  ⚠ Sync completed with {len(errors)} errors")
            
            return result
            
        except ImportError as e:
            logger.error(f"  ✗ Cannot import UBECDataSynchronizer: {e}")
            logger.error(f"     Make sure core/db/UBECDataSynchronizer.py exists")
            return {
                'element': 'air',
                'token': 'UBEC',
                'status': 'error',
                'error': 'UBECDataSynchronizer not found - check core/db/ directory',
                'error_detail': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"  ✗ Fatal error syncing Air data: {e}")
            return {
                'element': 'air',
                'token': 'UBEC',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_circulation_ratio(self, asset_data):
        """Calculate what percentage of supply is in circulation."""
        try:
            total = Decimal(asset_data.get('amount', '0'))
            # Assuming issuer holds locked supply
            # This is a simplified calculation
            return float((total / GlobalConfig.TOTAL_SUPPLY) * 100)
        except:
            return 0.0
    
    def _calculate_accessibility_score(self, asset_data):
        """
        Calculate how accessible the token is (0-1 scale).
        Based on number of holders, distribution, etc.
        """
        # Simple calculation based on number of holders
        # More sophisticated metrics could be added
        holders = int(asset_data.get('num_accounts', 0))
        
        if holders < 10:
            return 0.1
        elif holders < 100:
            return 0.3
        elif holders < 1000:
            return 0.5
        elif holders < 10000:
            return 0.7
        else:
            return 0.9
    
    def sync(self):
        """
        Synchronize UBEC data with blockchain.
        
        Returns:
            dict: Sync results
        """
        logger.info("Synchronizing UBEC protocol with blockchain")
        
        try:
            status = self.get_status()
            
            result = {
                'protocol': 'UBEC',
                'sync_status': 'success',
                'holders_synced': status['total_holders'],
                'supply_synced': status['total_supply']
            }
            
            logger.info("✓ UBEC sync complete")
            return result
            
        except Exception as e:
            logger.error(f"✗ UBEC sync failed: {e}")
            raise
    
    def assess_diversity(self) -> Dict[str, Any]:
        """
        Assess diversity principle (Air's ubuntu principle)
        
        Returns:
            Dictionary with diversity assessment
        """
        logger.info("Assessing diversity principle for Air element")
        
        try:
            status = self.get_status()
            
            # Diversity metrics
            total_holders = status.get('total_holders', 0)
            accessibility_score = status.get('accessibility_score', 0)
            
            # Calculate diversity score
            diversity_score = accessibility_score
            
            assessment = {
                'principle': 'diversity',
                'element': 'air',
                'score': diversity_score,
                'total_holders': total_holders,
                'accessibility_score': accessibility_score,
                'status': 'excellent' if diversity_score > 0.7 else 'good' if diversity_score > 0.5 else 'needs_improvement',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"  ✓ Diversity assessment complete: score {diversity_score:.2f}")
            return assessment
            
        except Exception as e:
            logger.error(f"  ✗ Error assessing diversity: {e}")
            return {
                'principle': 'diversity',
                'element': 'air',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def evaluate_holonic(self, account_id):
        """
        Evaluate an account's holonic alignment with UBEC (Air) principles.
        
        Air element focuses on:
        - Freedom of movement (transaction frequency)
        - Accessibility (network connections)
        - Universal participation (inclusivity)
        
        Args:
            account_id: Stellar account ID
        
        Returns:
            dict: Holonic evaluation results
        """
        logger.info(f"Evaluating holonic alignment for account {account_id}")
        
        try:
            # Get account data
            account = self.server.accounts().account_id(account_id).call()
            
            # Get account balances
            ubec_balance = Decimal('0')
            for balance in account['balances']:
                if (balance.get('asset_type') != 'native' and 
                    balance.get('asset_code') == GlobalConfig.UBEC_CODE and
                    balance.get('asset_issuer') == GlobalConfig.UBEC_ISSUER):
                    ubec_balance = Decimal(balance['balance'])
                    break
            
            # Calculate holonic metrics
            metrics = {
                'freedom_of_movement': self._evaluate_movement_freedom(account),
                'accessibility': self._evaluate_accessibility(account),
                'universal_participation': self._evaluate_participation(account, ubec_balance)
            }
            
            # Calculate overall holonic score for UBEC
            holonic_score = (
                metrics['freedom_of_movement'] * 0.4 +
                metrics['accessibility'] * 0.3 +
                metrics['universal_participation'] * 0.3
            )
            
            evaluation = {
                'account_id': account_id,
                'protocol': 'UBEC (Air)',
                'ubec_balance': str(ubec_balance),
                'metrics': metrics,
                'holonic_score': round(holonic_score, 3),
                'alignment_level': self._determine_alignment(holonic_score)
            }
            
            logger.info(f"✓ Holonic evaluation complete: score {holonic_score:.3f}")
            return evaluation
            
        except Exception as e:
            logger.error(f"✗ Holonic evaluation failed: {e}")
            raise
    
    def _evaluate_movement_freedom(self, account):
        """Evaluate freedom of movement through transaction patterns."""
        # Simplified calculation based on account activity
        # Could be enhanced with actual transaction history
        subentry_count = account.get('subentry_count', 0)
        return min(1.0, subentry_count / 10.0)
    
    def _evaluate_accessibility(self, account):
        """Evaluate how accessible/connected the account is."""
        # Based on number of trustlines (connections to other assets)
        num_balances = len(account.get('balances', []))
        return min(1.0, num_balances / 20.0)
    
    def _evaluate_participation(self, account, ubec_balance):
        """Evaluate level of participation in the ecosystem."""
        # Based on balance relative to average
        if ubec_balance == 0:
            return 0.1
        
        # Simple calculation - could be enhanced
        balance_float = float(ubec_balance)
        if balance_float < 100:
            return 0.2
        elif balance_float < 1000:
            return 0.4
        elif balance_float < 10000:
            return 0.6
        elif balance_float < 100000:
            return 0.8
        else:
            return 1.0
    
    def _determine_alignment(self, score):
        """Determine alignment level from score."""
        if score >= 0.9:
            return 'Exemplar'
        elif score >= 0.7:
            return 'Integrator'
        elif score >= 0.5:
            return 'Contributor'
        elif score >= 0.3:
            return 'Participant'
        else:
            return 'Observer'


if __name__ == '__main__':
    # Simple test
    protocol = UBECProtocol()
    print(protocol.health_check())
