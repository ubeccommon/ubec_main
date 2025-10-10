# UBEC/UBEC_protocol.py
"""
🜁 UBEC (Air) Token Protocol - Gateway & Access
Universal Basic Economic Commons - Entry point to the holonic economy

Element: Air
Principle: Freedom of movement, accessibility, universal access
Role: Gateway token providing entry to the Ubuntu Economic Commons

This protocol implements the Air element of the four-element UBEC system,
serving as the universal gateway and access point for the economic commons.

Key Responsibilities:
- Universal basic access to the economic commons
- Onboarding and initial distribution
- Gateway to other elemental tokens
- Basic transaction capabilities
- Freedom of movement and accessibility metrics

Attribution:
This project uses the services of Claude and Anthropic PBC to inform our decisions 
and recommendations. This project was made possible with the assistance of Claude 
and Anthropic PBC.

Author: UBEC Protocol Team
Version: 3.0 (Async Refactor)
Date: 2025-10-10
"""

import asyncio
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional
from stellar_sdk import ServerAsync, Asset

# Use single config source (Principle 8: No Duplicate Configuration)
from config import settings, get_logger

logger = get_logger('ubec.UBEC')


class UBECProtocol:
    """
    UBEC (Air) Token Protocol Implementation - Fully Async.
    
    The Air element represents freedom, movement, and universal access.
    UBEC serves as the gateway token, providing entry and basic access
    to the Ubuntu Economic Commons ecosystem.
    
    All methods are async for non-blocking I/O operations.
    
    Key Functions:
    - Universal basic access to the economic commons
    - Onboarding and initial distribution
    - Gateway to other elemental tokens
    - Basic transaction capabilities
    - Freedom of movement metrics
    """
    
    def __init__(self):
        """Initialize UBEC protocol with Stellar network connection."""
        logger.info("Initializing UBEC (Air) Protocol")
        
        # Use async server
        self.server = ServerAsync(horizon_url=settings.HORIZON_URL)
        self.asset = Asset(settings.UBEC_CODE, settings.UBEC_ISSUER)
        
        # Store configuration
        self.asset_code = settings.UBEC_CODE
        self.issuer = settings.UBEC_ISSUER
        self.network = settings.PUBLIC_NETWORK_PASSPHRASE
        
        logger.info(f"Connected to {self._get_network_name()} network")
        logger.info(f"UBEC Protocol: Gateway & Universal Access System")
    
    def _get_network_name(self) -> str:
        """Get friendly network name."""
        if 'testnet' in self.network.lower():
            return 'testnet'
        elif 'public' in self.network.lower():
            return 'mainnet'
        else:
            return 'custom'
    
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
    # HEALTH & STATUS METHODS
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on UBEC protocol (async).
        
        Returns:
            dict: Health status information
        """
        logger.info("Performing UBEC protocol health check")
        
        try:
            # Check issuer account exists and is accessible
            issuer_account = await self.server.accounts().account_id(self.issuer).call()
            
            # Check asset statistics
            assets_response = await self.server.assets().for_code(self.asset_code).call()
            
            ubec_asset = None
            for asset in assets_response['_embedded']['records']:
                if asset['asset_issuer'] == self.issuer:
                    ubec_asset = asset
                    break
            
            status = {
                'protocol': 'UBEC (Air)',
                'element': 'air',
                'network': self._get_network_name(),
                'issuer_active': True,
                'asset_code': self.asset_code,
                'total_supply': ubec_asset.get('amount', 'unknown') if ubec_asset else 'unknown',
                'num_accounts': ubec_asset.get('num_accounts', 0) if ubec_asset else 0,
                'gateway_active': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("✓ UBEC protocol health check passed")
            return status
            
        except Exception as e:
            logger.error(f"✗ UBEC protocol health check failed: {e}")
            return {
                'protocol': 'UBEC (Air)',
                'element': 'air',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of UBEC token (async).
        
        Returns:
            dict: Detailed token statistics
        """
        logger.info("Retrieving UBEC token status")
        
        try:
            # Get asset statistics
            assets = await self.server.assets()\
                .for_code(self.asset_code)\
                .for_issuer(self.issuer)\
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
                'accessibility_score': self._calculate_accessibility_score(asset_data),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"✓ UBEC status retrieved: {status['total_holders']} holders")
            return status
            
        except Exception as e:
            logger.error(f"✗ Failed to retrieve UBEC status: {e}")
            raise
    
    # ========================================================================
    # DATA SYNCHRONIZATION
    # ========================================================================
    
    async def sync_gateway_data(self) -> Dict[str, Any]:
        """
        Synchronize Air (Gateway) protocol data from Stellar blockchain (async).
        
        This method:
        - Syncs all accounts holding UBEC tokens
        - Syncs all transactions involving UBEC
        - Updates balance information
        - Provides gateway access metrics
        
        Note: Currently calls sync methods from UBECDataSynchronizer.
        TODO: Migrate to service registry pattern (Principle 3)
        
        Returns:
            Dictionary containing sync results with counts and status
        """
        logger.info("Starting Air (UBEC) gateway data synchronization...")
        
        try:
            # Import the synchronizer
            # TODO: Replace with service registry pattern
            from db.ubec_data_synchronizer import UBECDataSynchronizer
            
            # Initialize synchronizer with database connection
            async with UBECDataSynchronizer() as synchronizer:
                
                # Track overall results
                total_accounts = 0
                total_transactions = 0
                total_balances = 0
                errors = []
                
                # Sync accounts for UBEC token
                logger.info("  Syncing UBEC accounts...")
                try:
                    accounts_result = await synchronizer.sync_account_data(asset_code='UBEC')
                    total_accounts = accounts_result.get('synced', 0)
                    logger.info(f"    ✓ Synced {total_accounts} accounts")
                except Exception as e:
                    error_msg = f"Error syncing accounts: {str(e)}"
                    logger.error(f"    ✗ {error_msg}")
                    errors.append(error_msg)
                
                # Sync transactions
                logger.info("  Syncing UBEC transactions...")
                try:
                    transactions_result = await synchronizer.sync_transaction_data(asset_code='UBEC')
                    total_transactions = transactions_result.get('synced', 0)
                    logger.info(f"    ✓ Synced {total_transactions} transactions")
                except Exception as e:
                    error_msg = f"Error syncing transactions: {str(e)}"
                    logger.error(f"    ✗ {error_msg}")
                    errors.append(error_msg)
                
                # Sync balances
                logger.info("  Syncing UBEC balances...")
                try:
                    balances_result = await synchronizer.sync_balance_data(asset_code='UBEC')
                    total_balances = balances_result.get('synced', 0)
                    logger.info(f"    ✓ Synced {total_balances} balances")
                except Exception as e:
                    error_msg = f"Error syncing balances: {str(e)}"
                    logger.error(f"    ✗ {error_msg}")
                    errors.append(error_msg)
                
                # Calculate gateway metrics
                logger.info("  Calculating gateway metrics...")
                gateway_metrics = await self._calculate_gateway_metrics(
                    total_accounts, 
                    total_balances
                )
                
                # Build result
                result = {
                    'element': 'air',
                    'token': 'UBEC',
                    'asset_code': 'UBEC',
                    'issuer': self.issuer,
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
            logger.error(f"     Make sure db/ubec_data_synchronizer.py exists")
            return {
                'element': 'air',
                'token': 'UBEC',
                'status': 'error',
                'error': 'UBECDataSynchronizer not found - check db/ directory',
                'error_detail': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"  ✗ Fatal error syncing Air data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'element': 'air',
                'token': 'UBEC',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _calculate_gateway_metrics(self, total_accounts: int, 
                                        total_balances: int) -> Dict[str, Any]:
        """
        Calculate gateway-specific metrics.
        
        Args:
            total_accounts: Number of accounts synced
            total_balances: Number of balances synced
            
        Returns:
            dict: Gateway metrics
        """
        return {
            'total_accounts': total_accounts,
            'active_accounts': total_accounts,  # All accounts with balance > 0
            'total_supply_distributed': total_balances,
            'gateway_accessibility': 1.0 if total_accounts > 0 else 0.0,
            'movement_freedom_index': self._calculate_movement_index(total_accounts)
        }
    
    def _calculate_movement_index(self, account_count: int) -> float:
        """
        Calculate freedom of movement index based on account distribution.
        
        Args:
            account_count: Number of accounts
            
        Returns:
            float: Movement index (0-1)
        """
        if account_count == 0:
            return 0.0
        elif account_count < 10:
            return 0.2
        elif account_count < 100:
            return 0.4
        elif account_count < 1000:
            return 0.6
        elif account_count < 10000:
            return 0.8
        else:
            return 1.0
    
    async def sync(self) -> Dict[str, Any]:
        """
        Legacy sync method - redirects to sync_gateway_data (async).
        
        Returns:
            dict: Sync results
        """
        logger.info("Synchronizing UBEC protocol with blockchain")
        return await self.sync_gateway_data()
    
    # ========================================================================
    # UBUNTU PRINCIPLE ASSESSMENT
    # ========================================================================
    
    async def assess_diversity(self) -> Dict[str, Any]:
        """
        Assess diversity principle (Air's ubuntu principle) (async).
        
        Air element embodies diversity through:
        - Universal accessibility
        - Freedom of movement
        - Inclusive participation
        
        Returns:
            Dictionary with diversity assessment
        """
        logger.info("Assessing diversity principle for Air element")
        
        try:
            status = await self.get_status()
            
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
                'status': self._determine_principle_status(diversity_score),
                'recommendations': self._generate_diversity_recommendations(diversity_score),
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
    
    def _determine_principle_status(self, score: float) -> str:
        """Determine principle status from score."""
        if score > 0.8:
            return 'excellent'
        elif score > 0.6:
            return 'good'
        elif score > 0.4:
            return 'adequate'
        else:
            return 'needs_improvement'
    
    def _generate_diversity_recommendations(self, score: float) -> list:
        """Generate recommendations based on diversity score."""
        recommendations = []
        
        if score < 0.5:
            recommendations.append("Increase onboarding efforts to expand holder base")
            recommendations.append("Improve accessibility through educational initiatives")
        
        if score < 0.7:
            recommendations.append("Enhance gateway visibility and ease of entry")
            recommendations.append("Promote freedom of movement through reduced friction")
        
        if score < 0.9:
            recommendations.append("Continue expanding universal access programs")
        
        return recommendations if recommendations else ["Maintain current diversity levels"]
    
    # ========================================================================
    # HOLONIC EVALUATION
    # ========================================================================
    
    async def evaluate_holonic(self, account_id: str) -> Dict[str, Any]:
        """
        Evaluate an account's holonic alignment with UBEC (Air) principles (async).
        
        Air element focuses on:
        - Freedom of movement (transaction frequency)
        - Accessibility (network connections)
        - Universal participation (inclusivity)
        
        Args:
            account_id: Stellar account ID
        
        Returns:
            dict: Holonic evaluation results
        """
        logger.info(f"Evaluating holonic alignment for account {account_id[:8]}...")
        
        try:
            # Get account data
            account = await self.server.accounts().account_id(account_id).call()
            
            # Get account UBEC balance
            ubec_balance = await self._get_ubec_balance(account)
            
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
                'element': 'air',
                'ubec_balance': str(ubec_balance),
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
                'protocol': 'UBEC (Air)',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _get_ubec_balance(self, account: Dict[str, Any]) -> Decimal:
        """
        Extract UBEC balance from account data.
        
        Args:
            account: Account data from Stellar
            
        Returns:
            Decimal: UBEC balance
        """
        ubec_balance = Decimal('0')
        for balance in account['balances']:
            if (balance.get('asset_type') != 'native' and 
                balance.get('asset_code') == self.asset_code and
                balance.get('asset_issuer') == self.issuer):
                ubec_balance = Decimal(balance['balance'])
                break
        return ubec_balance
    
    def _evaluate_movement_freedom(self, account: Dict[str, Any]) -> float:
        """
        Evaluate freedom of movement through transaction patterns.
        
        Args:
            account: Account data
            
        Returns:
            float: Movement freedom score (0-1)
        """
        # Based on account activity and trustlines
        subentry_count = account.get('subentry_count', 0)
        num_signers = len(account.get('signers', []))
        
        # More subentries and signers indicate more activity/connections
        activity_score = min(1.0, subentry_count / 10.0)
        signer_score = min(1.0, num_signers / 5.0)
        
        return (activity_score * 0.7 + signer_score * 0.3)
    
    def _evaluate_accessibility(self, account: Dict[str, Any]) -> float:
        """
        Evaluate how accessible/connected the account is.
        
        Args:
            account: Account data
            
        Returns:
            float: Accessibility score (0-1)
        """
        # Based on number of trustlines (connections to other assets)
        num_balances = len(account.get('balances', []))
        
        # More diverse holdings indicate better accessibility
        return min(1.0, num_balances / 20.0)
    
    def _evaluate_participation(self, account: Dict[str, Any], 
                               ubec_balance: Decimal) -> float:
        """
        Evaluate level of participation in the ecosystem.
        
        Args:
            account: Account data
            ubec_balance: UBEC balance
            
        Returns:
            float: Participation score (0-1)
        """
        if ubec_balance == 0:
            return 0.1
        
        # Based on balance tiers
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
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _calculate_circulation_ratio(self, asset_data: Dict[str, Any]) -> float:
        """
        Calculate what percentage of supply is in circulation.
        
        Args:
            asset_data: Asset data from Stellar
            
        Returns:
            float: Circulation ratio (0-100)
        """
        try:
            total = Decimal(asset_data.get('amount', '0'))
            # This is a simplified calculation
            # In production, would check issuer's locked supply
            if hasattr(settings, 'TOTAL_SUPPLY'):
                return float((total / Decimal(str(settings.TOTAL_SUPPLY))) * 100)
            return 0.0
        except Exception as e:
            logger.warning(f"Error calculating circulation ratio: {e}")
            return 0.0
    
    def _calculate_accessibility_score(self, asset_data: Dict[str, Any]) -> float:
        """
        Calculate how accessible the token is (0-1 scale).
        Based on number of holders, distribution, etc.
        
        Args:
            asset_data: Asset data from Stellar
            
        Returns:
            float: Accessibility score
        """
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


# ============================================================================
# ASYNC TEST FUNCTION (for development/testing only)
# ============================================================================

async def test_ubec_protocol():
    """Test function for UBEC protocol (async)."""
    print("\n" + "=" * 70)
    print("TESTING UBEC PROTOCOL (Async Version)")
    print("=" * 70)
    
    async with UBECProtocol() as protocol:
        try:
            print("\n1. Health check...")
            health = await protocol.health_check()
            print(f"   Result: {health}")
            
            print("\n2. Get status...")
            status = await protocol.get_status()
            print(f"   Result: {status}")
            
            print("\n3. Assess diversity...")
            diversity = await protocol.assess_diversity()
            print(f"   Result: {diversity}")
            
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
    asyncio.run(test_ubec_protocol())
