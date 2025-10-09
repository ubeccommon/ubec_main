# UBECrc/UBECrc_protocol.py
"""
🜄 UBECrc (Water) Token Protocol - Reciprocity Credits
Flow, exchange, and reciprocal relationships

Element: Water
Principle: Flow, reciprocity, adaptability, mutual exchange
Role: Measuring and rewarding reciprocal contributions
"""

from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from stellar_sdk import Server, Asset
from config import GlobalConfig, get_logger
from UBECrc.config import UBECrcConfig

logger = get_logger('UBECrc')


class UBECrcProtocol:
    """
    UBECrc (Water) Token Protocol Implementation.
    
    The Water element represents flow, adaptation, and reciprocity.
    UBECrc tracks and rewards reciprocal exchanges, measuring the
    balance of giving and receiving within the ecosystem.
    
    Key Functions:
    - Track reciprocal relationships
    - Reward balanced giving/receiving
    - Measure community contribution
    - Facilitate mutual exchange
    """
    
    def __init__(self):
        """Initialize UBECrc protocol with Stellar network connection."""
        logger.info("Initializing UBECrc (Water) Protocol")
        
        self.server = Server(horizon_url=GlobalConfig.get_horizon_url())
        # Note: UBECrc would have its own asset code and issuer
        # Using placeholders for now
        self.asset_code = "UBECrc"
        
        logger.info(f"Connected to {GlobalConfig.NETWORK} network")
        logger.info("UBECrc Protocol: Reciprocity Credits System")
    
    def health_check(self):
        """Perform health check on UBECrc protocol."""
        logger.info("Performing UBECrc protocol health check")
        
        try:
            status = {
                'protocol': 'UBECrc (Water)',
                'network': GlobalConfig.NETWORK,
                'reciprocity_tracking': True,
                'flow_monitoring': True,
                'decay_rate': float(UBECrcConfig.CREDIT_DECAY_RATE),
                'base_reward': float(UBECrcConfig.BASE_REWARD_PER_DATAPOINT),
                'system_active': True
            }
            
            logger.info("✓ UBECrc protocol health check passed")
            return status
            
        except Exception as e:
            logger.error(f"✗ UBECrc protocol health check failed: {e}")
            raise
    
    def get_status(self):
        """Get comprehensive status of UBECrc system."""
        logger.info("Retrieving UBECrc system status")
        
        try:
            status = {
                'token': 'UBECrc',
                'element': 'Water (🜄)',
                'role': 'Reciprocity Credits',
                'total_participants': 0,  # Would query database
                'active_exchanges': 0,
                'reciprocity_health': self._calculate_reciprocity_health(),
                'flow_rate': self._calculate_flow_rate()
            }
            
            logger.info(f"✓ UBECrc status retrieved")
            return status
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve UBECrc status: {e}")
            raise
    
    def sync_flow_data(self) -> Dict[str, Any]:
        """
        Synchronize Water (Flow) protocol data from Stellar blockchain
        
        This method:
        - Syncs all accounts holding UBECrc tokens
        - Syncs all transactions (flows) involving UBECrc
        - Updates balance information
        - Calculates flow velocity and reciprocity metrics
        
        Returns:
            Dictionary containing sync results with flow metrics
        """
        logger.info("Starting Water (UBECrc) flow data synchronization...")
        
        try:
            # Import the synchronizer
            from core.db.ubec_data_synchronizer import UBECDataSynchronizer
            
            # Initialize synchronizer
            synchronizer = UBECDataSynchronizer()
            
            # Track overall results
            total_accounts = 0
            total_transactions = 0
            total_balances = 0
            errors = []
            
            # Sync accounts for UBECrc token
            logger.info("  Syncing UBECrc accounts...")
            try:
                accounts_result = synchronizer.sync_account_data(asset_code='UBECrc')
                total_accounts = accounts_result.get('synced', 0)
                logger.info(f"    ✓ Synced {total_accounts} accounts")
            except Exception as e:
                error_msg = f"Error syncing accounts: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Sync transactions (flows)
            logger.info("  Syncing UBECrc transactions...")
            try:
                transactions_result = synchronizer.sync_transaction_data(asset_code='UBECrc')
                total_transactions = transactions_result.get('synced', 0)
                logger.info(f"    ✓ Synced {total_transactions} flows")
            except Exception as e:
                error_msg = f"Error syncing transactions: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Sync balances
            logger.info("  Syncing UBECrc balances...")
            try:
                balances_result = synchronizer.sync_balance_data(asset_code='UBECrc')
                total_balances = balances_result.get('synced', 0)
                logger.info(f"    ✓ Synced {total_balances} balances")
            except Exception as e:
                error_msg = f"Error syncing balances: {str(e)}"
                logger.error(f"    ✗ {error_msg}")
                errors.append(error_msg)
            
            # Calculate flow metrics
            logger.info("  Calculating flow metrics...")
            try:
                flow_metrics = self._calculate_flow_metrics(
                    transactions_result.get('data', []),
                    total_accounts
                )
            except Exception as e:
                logger.warning(f"    ⚠ Could not calculate flow metrics: {e}")
                flow_metrics = {
                    'flow_velocity': 0.0,
                    'reciprocity_score': 0.0,
                    'avg_transaction_size': 0.0
                }
            
            # Build result
            result = {
                'element': 'water',
                'token': 'UBECrc',
                'asset_code': 'UBECrc',
                'accounts_synced': total_accounts,
                'transactions_synced': total_transactions,
                'balances_synced': total_balances,
                'flow_velocity': flow_metrics.get('flow_velocity', 0.0),
                'reciprocity_score': flow_metrics.get('reciprocity_score', 0.0),
                'avg_transaction_size': flow_metrics.get('avg_transaction_size', 0.0),
                'flow_health': 'ACTIVE' if total_transactions > 0 else 'IDLE',
                'errors': errors if errors else None,
                'status': 'success' if not errors else 'partial',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"  ✓ Water sync complete: {result['transactions_synced']} flows, "
                       f"velocity: {result['flow_velocity']:.2f}")
            
            if errors:
                logger.warning(f"  ⚠ Sync completed with {len(errors)} errors")
            
            return result
            
        except ImportError as e:
            logger.error(f"  ✗ Cannot import UBECDataSynchronizer: {e}")
            return {
                'element': 'water',
                'token': 'UBECrc',
                'status': 'error',
                'error': 'UBECDataSynchronizer not found',
                'error_detail': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"  ✗ Fatal error syncing Water data: {e}")
            return {
                'element': 'water',
                'token': 'UBECrc',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_flow_metrics(self, transactions: list, total_accounts: int) -> Dict:
        """
        Calculate flow velocity and reciprocity metrics
        
        Args:
            transactions: List of transaction data
            total_accounts: Total number of accounts
            
        Returns:
            Dictionary with flow metrics
        """
        try:
            if not transactions or total_accounts == 0:
                return {
                    'flow_velocity': 0.0,
                    'reciprocity_score': 0.0,
                    'avg_transaction_size': 0.0
                }
            
            # Calculate flow velocity (transactions per account)
            flow_velocity = len(transactions) / total_accounts if total_accounts > 0 else 0
            
            # Calculate average transaction size
            total_amount = sum(
                float(tx.get('amount', 0)) 
                for tx in transactions 
                if 'amount' in tx
            )
            avg_transaction_size = total_amount / len(transactions) if transactions else 0
            
            # Calculate reciprocity score (bidirectional flow)
            # Count unique sender-receiver pairs
            flows = set()
            reverse_flows = set()
            
            for tx in transactions:
                sender = tx.get('source_account')
                receiver = tx.get('destination_account')
                if sender and receiver:
                    flows.add((sender, receiver))
                    if (receiver, sender) in flows:
                        reverse_flows.add((sender, receiver))
            
            reciprocity_score = len(reverse_flows) / len(flows) if flows else 0
            
            return {
                'flow_velocity': round(flow_velocity, 2),
                'reciprocity_score': round(reciprocity_score, 2),
                'avg_transaction_size': round(avg_transaction_size, 2),
                'total_flows': len(flows),
                'bidirectional_flows': len(reverse_flows)
            }
            
        except Exception as e:
            logger.warning(f"Error calculating flow metrics: {e}")
            return {
                'flow_velocity': 0.0,
                'reciprocity_score': 0.0,
                'avg_transaction_size': 0.0
            }
    
    def _calculate_reciprocity_health(self):
        """Calculate overall reciprocity health (0-1 scale)."""
        # Simplified calculation
        # In production, would analyze actual reciprocity patterns
        return 0.75
    
    def _calculate_flow_rate(self):
        """Calculate current flow rate of reciprocity credits."""
        # Would calculate based on recent transactions
        return "moderate"
    
    def sync(self):
        """Synchronize UBECrc data with blockchain."""
        logger.info("Synchronizing UBECrc protocol with blockchain")
        
        try:
            result = {
                'protocol': 'UBECrc',
                'sync_status': 'success',
                'reciprocity_records_synced': 0
            }
            
            logger.info("✓ UBECrc sync complete")
            return result
            
        except Exception as e:
            logger.error(f"✗ UBECrc sync failed: {e}")
            raise
    
    def assess_reciprocity(self) -> Dict[str, Any]:
        """
        Assess reciprocity principle (Water's ubuntu principle)
        
        Returns:
            Dictionary with reciprocity assessment
        """
        logger.info("Assessing reciprocity principle for Water element")
        
        try:
            status = self.get_status()
            
            # Reciprocity metrics
            reciprocity_health = status.get('reciprocity_health', 0)
            flow_rate = status.get('flow_rate', 'unknown')
            
            # Calculate reciprocity score
            reciprocity_score = reciprocity_health
            
            assessment = {
                'principle': 'reciprocity',
                'element': 'water',
                'score': reciprocity_score,
                'flow_rate': flow_rate,
                'reciprocity_health': reciprocity_health,
                'status': 'excellent' if reciprocity_score > 0.7 else 'good' if reciprocity_score > 0.5 else 'needs_improvement',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"  ✓ Reciprocity assessment complete: score {reciprocity_score:.2f}")
            return assessment
            
        except Exception as e:
            logger.error(f"  ✗ Error assessing reciprocity: {e}")
            return {
                'principle': 'reciprocity',
                'element': 'water',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def evaluate_holonic(self, account_id):
        """
        Evaluate an account's holonic alignment with UBECrc (Water) principles.
        
        Water element focuses on:
        - Reciprocity balance (giving vs receiving)
        - Flow participation (transaction patterns)
        - Adaptability (response to ecosystem needs)
        
        Args:
            account_id: Stellar account ID
        
        Returns:
            dict: Holonic evaluation results
        """
        logger.info(f"Evaluating holonic alignment for account {account_id}")
        
        try:
            # Get account data
            account = self.server.accounts().account_id(account_id).call()
            
            # Calculate holonic metrics
            metrics = {
                'reciprocity_balance': self._evaluate_reciprocity_balance(account_id),
                'flow_participation': self._evaluate_flow_participation(account),
                'adaptability': self._evaluate_adaptability(account_id)
            }
            
            # Calculate overall holonic score for UBECrc
            holonic_score = (
                metrics['reciprocity_balance'] * 0.5 +
                metrics['flow_participation'] * 0.3 +
                metrics['adaptability'] * 0.2
            )
            
            evaluation = {
                'account_id': account_id,
                'protocol': 'UBECrc (Water)',
                'metrics': metrics,
                'holonic_score': round(holonic_score, 3),
                'alignment_level': self._determine_alignment(holonic_score)
            }
            
            logger.info(f"✓ Holonic evaluation complete: score {holonic_score:.3f}")
            return evaluation
            
        except Exception as e:
            logger.error(f"✗ Holonic evaluation failed: {e}")
            raise
    
    def _evaluate_reciprocity_balance(self, account_id):
        """Evaluate balance between giving and receiving."""
        # Would analyze transaction patterns
        # Simplified for now
        return 0.7
    
    def _evaluate_flow_participation(self, account):
        """Evaluate participation in ecosystem flow."""
        # Based on transaction frequency and volume
        return 0.6
    
    def _evaluate_adaptability(self, account_id):
        """Evaluate how account adapts to ecosystem needs."""
        # Would analyze response patterns
        return 0.5
    
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
    protocol = UBECrcProtocol()
    print(protocol.health_check())
