# UBECrc/UBECrc_protocol.py
"""
🜄 UBECrc (Water) Token Protocol - Reciprocity Credits
Flow, exchange, and reciprocal relationships

Element: Water (🜄) - Flow, Reciprocity, Adaptability
Function: Reciprocity credit tracking and flow measurement

This protocol implements the Water element of the four-element UBEC system,
tracking reciprocal exchanges and measuring the flow of value through the ecosystem.

Key Responsibilities:
- Track reciprocal relationships
- Reward balanced giving/receiving
- Measure community contribution
- Facilitate mutual exchange
- Flow velocity monitoring

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
from datetime import datetime, timedelta
from typing import Dict, Any, List, Set, Tuple, Optional
from stellar_sdk import ServerAsync, Asset

# Use single config source (Principle 8: No Duplicate Configuration)
from config import settings, get_logger

logger = get_logger('ubec.UBECrc')


class UBECrcProtocol:
    """
    UBECrc (Water) Token Protocol Implementation - Fully Async.
    
    The Water element represents flow, adaptation, and reciprocity.
    UBECrc tracks and rewards reciprocal exchanges, measuring the
    balance of giving and receiving within the ecosystem.
    
    All methods are async for non-blocking I/O operations.
    
    Key Functions:
    - Track reciprocal relationships
    - Reward balanced giving/receiving
    - Measure community contribution
    - Facilitate mutual exchange
    - Monitor flow velocity and patterns
    """
    
    TOKEN_CODE = "UBECrc"
    
    # Credit decay and reward parameters
    CREDIT_DECAY_RATE = Decimal("0.05")  # 5% monthly decay
    BASE_REWARD_PER_DATAPOINT = Decimal("1.0")
    
    # Flow health thresholds
    MIN_FLOW_VELOCITY = 0.1  # Minimum transactions per account
    HEALTHY_RECIPROCITY = 0.3  # 30% bidirectional flows is healthy
    EXCELLENT_RECIPROCITY = 0.5  # 50%+ bidirectional is excellent
    
    def __init__(
        self,
        issuer_public: Optional[str] = None,
        network: Optional[str] = None,
        horizon_url: Optional[str] = None
    ):
        """Initialize UBECrc protocol with Stellar network connection (async-ready)."""
        logger.info("Initializing UBECrc (Water) Protocol")
        
        # Use settings as single config source
        self.issuer_public = issuer_public or settings.UBECrc_ISSUER
        self.issuer = self.issuer_public  # Alias for compatibility
        self.asset_code = self.TOKEN_CODE
        
        # Network configuration
        network = network or self._get_network_from_settings()
        self.horizon_url = horizon_url or settings.HORIZON_URL
        
        # Create async server
        self.server = ServerAsync(horizon_url=self.horizon_url)
        self.asset = Asset(self.TOKEN_CODE, self.issuer_public)
        
        logger.info(f"Connected to {network} network")
        logger.info(f"UBECrc Asset: {self.asset_code}:{self.issuer}")
        logger.info("UBECrc Protocol: Reciprocity Credits System")
    
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
        Perform health check on UBECrc protocol (async).
        
        Returns:
            dict: Health status information
        """
        logger.info("Performing UBECrc protocol health check")
        
        try:
            # Verify issuer account is accessible
            try:
                await self.server.accounts().account_id(self.issuer).call()
                issuer_active = True
            except Exception as e:
                logger.warning(f"Could not verify issuer account: {e}")
                issuer_active = False
            
            status = {
                'protocol': 'UBECrc (Water)',
                'element': 'water',
                'network': self._get_network_from_settings(),
                'asset_code': self.asset_code,
                'issuer': self.issuer,
                'issuer_active': issuer_active,
                'reciprocity_tracking': True,
                'flow_monitoring': True,
                'decay_rate': float(self.CREDIT_DECAY_RATE),
                'base_reward': float(self.BASE_REWARD_PER_DATAPOINT),
                'system_active': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("✓ UBECrc protocol health check passed")
            return status
            
        except Exception as e:
            logger.error(f"✗ UBECrc protocol health check failed: {e}")
            return {
                'protocol': 'UBECrc (Water)',
                'element': 'water',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of UBECrc system (async).
        
        Returns:
            dict: Detailed protocol statistics
        """
        logger.info("Retrieving UBECrc system status")
        
        try:
            # Query blockchain for asset statistics
            reciprocity_health = await self._calculate_reciprocity_health()
            flow_rate = await self._calculate_flow_rate()
            
            status = {
                'protocol': 'UBECrc (Water)',
                'token': 'UBECrc',
                'element': 'Water (🜄)',
                'principle': 'Reciprocity & Flow',
                'role': 'Reciprocity Credits',
                'asset_code': self.asset_code,
                'issuer': self.issuer,
                'network': self._get_network_from_settings(),
                'total_participants': 0,  # Would query from database
                'active_exchanges': 0,
                'reciprocity_health': reciprocity_health,
                'flow_rate': flow_rate,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"✓ UBECrc status retrieved")
            return status
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve UBECrc status: {e}")
            raise
    
    async def _calculate_reciprocity_health(self) -> float:
        """
        Calculate overall reciprocity health (0-1 scale).
        
        Returns:
            float: Reciprocity health score
        """
        # TODO: Implement actual calculation based on transaction patterns
        # Placeholder for now
        return 0.75
    
    async def _calculate_flow_rate(self) -> str:
        """
        Calculate current flow rate of reciprocity credits.
        
        Returns:
            str: Flow rate description
        """
        # TODO: Calculate based on recent transactions
        return "moderate"
    
    # ========================================================================
    # DATA SYNCHRONIZATION (ASYNC)
    # ========================================================================
    
    async def sync_flow_data(self) -> Dict[str, Any]:
        """
        Synchronize Water (Flow) protocol data from Stellar blockchain (async).
        
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
            # TODO: Replace with service registry pattern
            from db.ubec_data_synchronizer import UBECDataSynchronizer
            
            # Initialize synchronizer
            async with UBECDataSynchronizer() as synchronizer:
                
                # Track overall results
                sync_results = {
                    'accounts': 0,
                    'transactions': 0,
                    'balances': 0,
                    'transaction_data': [],
                    'errors': []
                }
                
                # Sync accounts
                await self._sync_accounts(synchronizer, sync_results)
                
                # Sync transactions (flows)
                await self._sync_transactions(synchronizer, sync_results)
                
                # Sync balances
                await self._sync_balances(synchronizer, sync_results)
                
                # Calculate flow metrics
                flow_metrics = self._calculate_flow_metrics(
                    sync_results['transaction_data'],
                    sync_results['accounts']
                )
                
                # Build result
                result = self._build_sync_result(sync_results, flow_metrics)
                
                logger.info(f"  ✓ Water sync complete: {result['transactions_synced']} flows, "
                           f"velocity: {result['flow_velocity']:.2f}")
                
                if sync_results['errors']:
                    logger.warning(f"  ⚠ Sync completed with {len(sync_results['errors'])} errors")
                
                return result
            
        except ImportError as e:
            logger.error(f"  ✗ Cannot import UBECDataSynchronizer: {e}")
            return self._build_error_result('Module import error', str(e))
        except Exception as e:
            logger.error(f"  ✗ Fatal error syncing Water data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._build_error_result('Fatal sync error', str(e))
    
    async def _sync_accounts(self, synchronizer, results: Dict):
        """Sync account data."""
        logger.info("  Syncing UBECrc accounts...")
        try:
            accounts_result = await synchronizer.sync_account_data(asset_code='UBECrc')
            results['accounts'] = accounts_result.get('synced', 0)
            logger.info(f"    ✓ Synced {results['accounts']} accounts")
        except Exception as e:
            error_msg = f"Error syncing accounts: {str(e)}"
            logger.error(f"    ✗ {error_msg}")
            results['errors'].append(error_msg)
    
    async def _sync_transactions(self, synchronizer, results: Dict):
        """Sync transaction data (flows)."""
        logger.info("  Syncing UBECrc transactions...")
        try:
            transactions_result = await synchronizer.sync_transaction_data(asset_code='UBECrc')
            results['transactions'] = transactions_result.get('synced', 0)
            results['transaction_data'] = transactions_result.get('data', [])
            logger.info(f"    ✓ Synced {results['transactions']} flows")
        except Exception as e:
            error_msg = f"Error syncing transactions: {str(e)}"
            logger.error(f"    ✗ {error_msg}")
            results['errors'].append(error_msg)
    
    async def _sync_balances(self, synchronizer, results: Dict):
        """Sync balance data."""
        logger.info("  Syncing UBECrc balances...")
        try:
            balances_result = await synchronizer.sync_balance_data(asset_code='UBECrc')
            results['balances'] = balances_result.get('synced', 0)
            logger.info(f"    ✓ Synced {results['balances']} balances")
        except Exception as e:
            error_msg = f"Error syncing balances: {str(e)}"
            logger.error(f"    ✗ {error_msg}")
            results['errors'].append(error_msg)
    
    def _calculate_flow_metrics(self, transactions: List[Dict], 
                                total_accounts: int) -> Dict[str, Any]:
        """
        Calculate flow velocity and reciprocity metrics.
        
        Args:
            transactions: List of transaction data
            total_accounts: Total number of accounts
            
        Returns:
            Dictionary with flow metrics
        """
        logger.info("  Calculating flow metrics...")
        
        try:
            if not transactions or total_accounts == 0:
                return self._empty_flow_metrics()
            
            # Calculate basic metrics
            flow_velocity = self._calculate_velocity(transactions, total_accounts)
            avg_transaction_size = self._calculate_avg_size(transactions)
            
            # Calculate reciprocity patterns
            reciprocity_data = self._analyze_reciprocity_patterns(transactions)
            
            metrics = {
                'flow_velocity': round(flow_velocity, 2),
                'reciprocity_score': round(reciprocity_data['score'], 2),
                'avg_transaction_size': round(avg_transaction_size, 2),
                'total_flows': reciprocity_data['total_flows'],
                'bidirectional_flows': reciprocity_data['bidirectional_flows']
            }
            
            logger.info(f"    ✓ Flow metrics calculated: velocity={flow_velocity:.2f}, "
                       f"reciprocity={reciprocity_data['score']:.2f}")
            
            return metrics
            
        except Exception as e:
            logger.warning(f"    ⚠ Error calculating flow metrics: {e}")
            return self._empty_flow_metrics()
    
    def _empty_flow_metrics(self) -> Dict[str, float]:
        """Return empty flow metrics."""
        return {
            'flow_velocity': 0.0,
            'reciprocity_score': 0.0,
            'avg_transaction_size': 0.0,
            'total_flows': 0,
            'bidirectional_flows': 0
        }
    
    def _calculate_velocity(self, transactions: List[Dict], 
                           total_accounts: int) -> float:
        """Calculate flow velocity (transactions per account)."""
        if total_accounts == 0:
            return 0.0
        return len(transactions) / total_accounts
    
    def _calculate_avg_size(self, transactions: List[Dict]) -> float:
        """Calculate average transaction size."""
        if not transactions:
            return 0.0
        
        total_amount = sum(
            float(tx.get('amount', 0)) 
            for tx in transactions 
            if 'amount' in tx
        )
        return total_amount / len(transactions)
    
    def _analyze_reciprocity_patterns(self, transactions: List[Dict]) -> Dict[str, Any]:
        """
        Analyze reciprocity patterns in transactions.
        
        Args:
            transactions: List of transaction data
            
        Returns:
            dict: Reciprocity analysis including score and flow counts
        """
        flows: Set[Tuple[str, str]] = set()
        reverse_flows: Set[Tuple[str, str]] = set()
        
        for tx in transactions:
            sender = tx.get('source_account')
            receiver = tx.get('destination_account')
            
            if sender and receiver:
                flows.add((sender, receiver))
                # Check if reverse flow exists
                if (receiver, sender) in flows:
                    reverse_flows.add((sender, receiver))
        
        # Calculate reciprocity score
        reciprocity_score = len(reverse_flows) / len(flows) if flows else 0.0
        
        return {
            'score': reciprocity_score,
            'total_flows': len(flows),
            'bidirectional_flows': len(reverse_flows)
        }
    
    def _build_sync_result(self, sync_results: Dict, 
                          flow_metrics: Dict) -> Dict[str, Any]:
        """Build final sync result dictionary."""
        return {
            'element': 'water',
            'token': 'UBECrc',
            'asset_code': 'UBECrc',
            'issuer': self.issuer,
            'accounts_synced': sync_results['accounts'],
            'transactions_synced': sync_results['transactions'],
            'balances_synced': sync_results['balances'],
            'flow_velocity': flow_metrics.get('flow_velocity', 0.0),
            'reciprocity_score': flow_metrics.get('reciprocity_score', 0.0),
            'avg_transaction_size': flow_metrics.get('avg_transaction_size', 0.0),
            'flow_health': self._determine_flow_health(flow_metrics),
            'errors': sync_results['errors'] if sync_results['errors'] else None,
            'status': 'success' if not sync_results['errors'] else 'partial',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _determine_flow_health(self, flow_metrics: Dict) -> str:
        """Determine flow health status from metrics."""
        velocity = flow_metrics.get('flow_velocity', 0.0)
        reciprocity = flow_metrics.get('reciprocity_score', 0.0)
        
        if velocity >= self.MIN_FLOW_VELOCITY and reciprocity >= self.EXCELLENT_RECIPROCITY:
            return 'EXCELLENT'
        elif velocity >= self.MIN_FLOW_VELOCITY and reciprocity >= self.HEALTHY_RECIPROCITY:
            return 'ACTIVE'
        elif velocity > 0:
            return 'LOW'
        else:
            return 'IDLE'
    
    def _build_error_result(self, error_type: str, error_detail: str) -> Dict[str, Any]:
        """Build error result dictionary."""
        return {
            'element': 'water',
            'token': 'UBECrc',
            'asset_code': self.asset_code,
            'issuer': self.issuer,
            'status': 'error',
            'error': error_type,
            'error_detail': error_detail,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def sync(self) -> Dict[str, Any]:
        """
        Legacy sync method - redirects to sync_flow_data (async).
        
        Returns:
            dict: Sync results
        """
        logger.info("Synchronizing UBECrc protocol with blockchain")
        return await self.sync_flow_data()
    
    # ========================================================================
    # UBUNTU PRINCIPLE ASSESSMENT (ASYNC)
    # ========================================================================
    
    async def assess_reciprocity(self) -> Dict[str, Any]:
        """
        Assess reciprocity principle (Water's ubuntu principle) (async).
        
        Returns:
            Dictionary with reciprocity assessment
        """
        logger.info("Assessing reciprocity principle for Water element")
        
        try:
            status = await self.get_status()
            
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
                'status': self._determine_principle_status(reciprocity_score),
                'interpretation': self._interpret_reciprocity_score(reciprocity_score),
                'recommendations': self._generate_reciprocity_recommendations(reciprocity_score),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"  ✓ Reciprocity assessment complete: score {reciprocity_score:.2f}")
            return assessment
            
        except Exception as e:
            logger.error(f"  ✗ Error assessing reciprocity: {e}")
            return {
                'principle': 'reciprocity',
                'element': 'water',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _determine_principle_status(self, score: float) -> str:
        """Determine principle status from score."""
        if score > 0.7:
            return 'excellent'
        elif score > 0.5:
            return 'good'
        else:
            return 'needs_improvement'
    
    def _interpret_reciprocity_score(self, score: float) -> str:
        """Interpret reciprocity score with context."""
        if score >= 0.8:
            return 'Excellent reciprocity - Strong bidirectional flows and balanced exchange'
        elif score >= 0.6:
            return 'Good reciprocity - Active exchange patterns with room for improvement'
        elif score >= 0.4:
            return 'Fair reciprocity - Some flows exist but balance needs strengthening'
        else:
            return 'Poor reciprocity - Limited bidirectional exchange, intervention needed'
    
    def _generate_reciprocity_recommendations(self, score: float) -> List[str]:
        """Generate recommendations based on reciprocity score."""
        recommendations = []
        
        if score < 0.5:
            recommendations.append("Encourage bidirectional exchange patterns")
            recommendations.append("Implement reciprocity incentives and rewards")
        
        if score < 0.7:
            recommendations.append("Promote balanced giving and receiving")
            recommendations.append("Monitor flow patterns for blockages")
        
        if score < 0.9:
            recommendations.append("Continue fostering healthy reciprocity patterns")
        
        return recommendations if recommendations else ["Maintain current reciprocity levels"]
    
    # ========================================================================
    # HOLONIC EVALUATION (ASYNC)
    # ========================================================================
    
    async def evaluate_holonic(self, account_id: str) -> Dict[str, Any]:
        """
        Evaluate an account's holonic alignment with UBECrc (Water) principles (async).
        
        Water element focuses on:
        - Reciprocity balance (giving vs receiving)
        - Flow participation (transaction patterns)
        - Adaptability (response to ecosystem needs)
        
        Args:
            account_id: Stellar account ID
        
        Returns:
            dict: Holonic evaluation results
        """
        logger.info(f"Evaluating holonic alignment for account {account_id[:8]}...")
        
        try:
            # Get account data
            account = await self.server.accounts().account_id(account_id).call()
            
            # Calculate holonic metrics
            metrics = await self._calculate_holonic_metrics(account_id, account)
            
            # Calculate overall holonic score for UBECrc
            holonic_score = self._calculate_holonic_score(metrics)
            
            evaluation = {
                'account_id': account_id,
                'protocol': 'UBECrc (Water)',
                'element': 'water',
                'principle': 'reciprocity',
                'metrics': metrics,
                'holonic_score': round(holonic_score, 3),
                'alignment_level': self._determine_alignment(holonic_score),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"✓ Holonic evaluation complete: score {holonic_score:.3f}")
            return evaluation
            
        except Exception as e:
            logger.error(f"✗ Holonic evaluation failed: {e}")
            return {
                'account_id': account_id,
                'protocol': 'UBECrc (Water)',
                'element': 'water',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _calculate_holonic_metrics(self, account_id: str, 
                                        account: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate holonic metrics for an account.
        
        Args:
            account_id: Account ID
            account: Account data from Stellar
            
        Returns:
            dict: Holonic metrics
        """
        metrics = {
            'reciprocity_balance': await self._evaluate_reciprocity_balance(account_id),
            'flow_participation': self._evaluate_flow_participation(account),
            'adaptability': await self._evaluate_adaptability(account_id)
        }
        
        return metrics
    
    def _calculate_holonic_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall holonic score from metrics."""
        return (
            metrics['reciprocity_balance'] * 0.5 +
            metrics['flow_participation'] * 0.3 +
            metrics['adaptability'] * 0.2
        )
    
    async def _evaluate_reciprocity_balance(self, account_id: str) -> float:
        """
        Evaluate balance between giving and receiving.
        
        Args:
            account_id: Account ID
            
        Returns:
            float: Reciprocity balance score (0-1)
        """
        # TODO: Analyze transaction patterns from database
        # Placeholder for now
        return 0.7
    
    def _evaluate_flow_participation(self, account: Dict[str, Any]) -> float:
        """
        Evaluate participation in ecosystem flow.
        
        Args:
            account: Account data
            
        Returns:
            float: Flow participation score (0-1)
        """
        # Based on transaction frequency and volume
        # Using subentry count as proxy for activity
        subentry_count = account.get('subentry_count', 0)
        
        # More activity indicates better flow participation
        return min(1.0, subentry_count / 20.0)
    
    async def _evaluate_adaptability(self, account_id: str) -> float:
        """
        Evaluate how account adapts to ecosystem needs.
        
        Args:
            account_id: Account ID
            
        Returns:
            float: Adaptability score (0-1)
        """
        # TODO: Analyze response patterns to ecosystem changes
        # Placeholder for now
        return 0.5
    
    def _determine_alignment(self, score: float) -> str:
        """
        Determine alignment level from holonic score.
        
        Args:
            score: Holonic score
            
        Returns:
            str: Alignment level
        """
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


# ============================================================================
# ASYNC TEST FUNCTION (for development/testing only)
# ============================================================================

async def test_ubecrc_protocol():
    """Test function for UBECrc protocol (async)."""
    print("\n" + "=" * 70)
    print("TESTING UBECrc PROTOCOL (Async Version)")
    print("=" * 70)
    
    async with UBECrcProtocol() as protocol:
        try:
            print(f"\nAsset Code: {protocol.asset_code}")
            print(f"Issuer: {protocol.issuer}")
            
            print("\n1. Health check...")
            health = await protocol.health_check()
            print(f"   Status: {health.get('status', 'ok')}")
            
            print("\n2. Get status...")
            status = await protocol.get_status()
            print(f"   Reciprocity health: {status.get('reciprocity_health', 0):.2f}")
            
            print("\n3. Assess reciprocity...")
            reciprocity = await protocol.assess_reciprocity()
            print(f"   Score: {reciprocity.get('score', 0):.2f}")
            
            print("\n" + "=" * 70)
            print("✓ ALL TESTS COMPLETED!")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    # For testing only - should not be used in production
    # Production execution should be through main.py
    asyncio.run(test_ubecrc_protocol())
