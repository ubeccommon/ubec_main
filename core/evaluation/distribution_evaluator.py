#!/usr/bin/env python3
"""
UBEC Distribution Evaluator Service

Evaluates and monitors UBEC token distribution compliance across all
managed accounts. Provides analysis and recommendations for maintaining
proper tokenomics ratios.

This service:
- Monitors distribution compliance in real-time
- Generates compliance reports
- Identifies distribution anomalies
- Provides rebalancing recommendations
- Tracks historical compliance trends

Design Compliance:
    ✅ All 12 Design Principles Implemented
    ✅ Pure async service pattern
    ✅ Service registry integration
    ✅ Database as single source of truth
    ✅ Comprehensive documentation
    ✅ No method redundancy
    ✅ Clear separation of concerns

Usage:
    from core.evaluation.distribution_evaluator import create_evaluator_service
    
    evaluator = create_evaluator_service(
        distribution_service=dist_service,
        audit_service=audit_service,
        db_manager=async_db
    )
    
    # Run evaluation
    report = await evaluator.evaluate_distribution()
    
    # Check specific account
    account_eval = await evaluator.evaluate_account('GXXX...')
    
    # Get historical trends
    trends = await evaluator.get_compliance_trends(days=30)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 2.1 (Operations Table Integration)
Date: October 14, 2025

Changelog:
    v2.1 - Updated to use stellar_operations table with correct schema
    v2.0 - Async Service Architecture
"""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class UBECDistributionEvaluator:
    """
    Service for evaluating and monitoring UBEC distribution compliance.
    
    This evaluator provides comprehensive analysis of token distribution,
    identifying issues and providing actionable recommendations.
    
    Attributes:
        distribution_service: Distribution management service
        audit_service: Token audit service
        db_manager: Async database manager
    """
    
    def __init__(
        self,
        distribution_service: Any,
        audit_service: Any,
        db_manager: Any
    ):
        """
        Initialize the distribution evaluator.
        
        Args:
            distribution_service: Distribution management service
            audit_service: Token audit service
            db_manager: Async database manager
        """
        self.distribution_service = distribution_service
        self.audit_service = audit_service
        self.db_manager = db_manager
        
        self.logger = logging.getLogger('UBECDistributionEvaluator')
        self.logger.info("Distribution Evaluator initialized")
    
    # ========================================================================
    # EVALUATION METHODS
    # ========================================================================
    
    async def evaluate_distribution(self) -> Dict[str, Any]:
        """
        Perform comprehensive distribution evaluation.
        
        Returns:
            dict: Complete evaluation report
        """
        self.logger.info("Starting distribution evaluation")
        
        try:
            # Get current status
            status = await self.distribution_service.get_distribution_status()
            
            # Get compliance
            compliance = status.get('compliance', {})
            
            # Analyze deviations
            deviations = await self._analyze_deviations(status)
            
            # Check for pending actions
            pending_transfers = await self._get_pending_transfers()
            
            # Get recommendations
            recommendations = await self._generate_recommendations(
                status, 
                deviations, 
                pending_transfers
            )
            
            # Calculate health score
            health_score = self._calculate_health_score(compliance, deviations)
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'evaluation_type': 'comprehensive',
                'health_score': health_score,
                'health_status': self._get_health_status(health_score),
                'compliance': compliance,
                'deviations': deviations,
                'current_distribution': status.get('distribution_percentages', {}),
                'pending_transfers': pending_transfers,
                'recommendations': recommendations,
                'requires_immediate_action': not compliance.get('overall', False),
                'summary': self._generate_summary(
                    health_score, 
                    compliance, 
                    deviations,
                    pending_transfers
                )
            }
            
            self.logger.info(
                f"Evaluation complete: Health={health_score:.1f}%, "
                f"Status={report['health_status']}"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error during evaluation: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'evaluation_type': 'comprehensive',
                'error': str(e),
                'health_score': 0.0,
                'health_status': 'ERROR'
            }
    
    async def evaluate_account(
        self, 
        account_id: str, 
        account_type: str = 'unknown'
    ) -> Dict[str, Any]:
        """
        Evaluate a specific account's distribution status.
        
        Args:
            account_id: Stellar account ID
            account_type: Type of account (general, administration, stewardship)
            
        Returns:
            dict: Account evaluation report
        """
        self.logger.info(f"Evaluating account: {account_id} ({account_type})")
        
        try:
            # Get account balance
            balance = await self.distribution_service.get_account_balance(account_id)
            
            # Get audit info
            audit_report = await self.audit_service.perform_audit()
            total_supply = Decimal(str(audit_report.get('total_supply', 0)))
            
            # Calculate percentage of total
            percent_of_total = (balance / total_supply * 100) if total_supply > 0 else 0
            
            # Get operation history
            operation_history = await self._get_account_operation_history(
                account_id, 
                limit=10
            )
            
            # Determine expected range for account type
            expected_range = self._get_expected_range_for_type(account_type)
            
            # Check if in expected range
            in_range = (
                expected_range['min'] <= percent_of_total <= expected_range['max']
            ) if expected_range else True
            
            evaluation = {
                'timestamp': datetime.now().isoformat(),
                'account_id': account_id,
                'account_type': account_type,
                'balance': float(balance),
                'percent_of_total_supply': float(percent_of_total),
                'expected_range': expected_range,
                'within_expected_range': in_range,
                'recent_operations': operation_history,
                'status': 'COMPLIANT' if in_range else 'OUT_OF_RANGE',
                'recommendations': []
            }
            
            # Add recommendations if out of range
            if not in_range:
                if percent_of_total > expected_range['max']:
                    evaluation['recommendations'].append({
                        'action': 'REDUCE_BALANCE',
                        'priority': 'HIGH',
                        'description': (
                            f"Account balance ({percent_of_total:.2f}%) exceeds "
                            f"maximum expected ({expected_range['max']:.2f}%)"
                        )
                    })
                else:
                    evaluation['recommendations'].append({
                        'action': 'INCREASE_BALANCE',
                        'priority': 'MEDIUM',
                        'description': (
                            f"Account balance ({percent_of_total:.2f}%) below "
                            f"minimum expected ({expected_range['min']:.2f}%)"
                        )
                    })
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating account {account_id}: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'account_id': account_id,
                'error': str(e),
                'status': 'ERROR'
            }
    
    async def get_compliance_trends(
        self, 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get historical compliance trends.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            dict: Compliance trend analysis
        """
        self.logger.info(f"Analyzing compliance trends for {days} days")
        
        try:
            schema = self.distribution_service.db_schema
            
            # Get historical snapshots
            query = f"""
                SELECT 
                    check_time,
                    general_balance,
                    administration_balance,
                    stewardship_balance,
                    total_supply,
                    rebalance_needed,
                    distribution_data
                FROM {schema}.distribution_history
                WHERE check_time >= NOW() - INTERVAL '{days} days'
                ORDER BY check_time ASC
            """
            
            snapshots = await self.db_manager.fetch_all(query)
            
            if not snapshots:
                return {
                    'days_analyzed': days,
                    'snapshots_found': 0,
                    'message': 'No historical data available'
                }
            
            # Analyze trends
            compliance_over_time = []
            rebalance_events = 0
            
            for snapshot in snapshots:
                total = Decimal(str(snapshot['total_supply']))
                
                if total > 0:
                    admin_pct = (
                        Decimal(str(snapshot['administration_balance'])) / total * 100
                    )
                    steward_pct = (
                        Decimal(str(snapshot['stewardship_balance'])) / total * 100
                    )
                    
                    compliance_over_time.append({
                        'timestamp': snapshot['check_time'].isoformat(),
                        'administration_pct': float(admin_pct),
                        'stewardship_pct': float(steward_pct),
                        'rebalance_needed': snapshot['rebalance_needed']
                    })
                    
                    if snapshot['rebalance_needed']:
                        rebalance_events += 1
            
            # Calculate compliance percentage
            compliant_snapshots = sum(
                1 for s in compliance_over_time 
                if not s['rebalance_needed']
            )
            compliance_percentage = (
                compliant_snapshots / len(compliance_over_time) * 100
            ) if compliance_over_time else 0
            
            return {
                'days_analyzed': days,
                'snapshots_found': len(snapshots),
                'compliance_percentage': compliance_percentage,
                'rebalance_events': rebalance_events,
                'trend_data': compliance_over_time,
                'summary': {
                    'overall_status': (
                        'GOOD' if compliance_percentage >= 80 else 'NEEDS_ATTENTION'
                    ),
                    'avg_admin_pct': (
                        sum(s['administration_pct'] for s in compliance_over_time) / 
                        len(compliance_over_time) if compliance_over_time else 0
                    ),
                    'avg_steward_pct': (
                        sum(s['stewardship_pct'] for s in compliance_over_time) / 
                        len(compliance_over_time) if compliance_over_time else 0
                    )
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing compliance trends: {e}")
            return {
                'days_analyzed': days,
                'error': str(e)
            }
    
    # ========================================================================
    # ANALYSIS HELPERS
    # ========================================================================
    
    async def _analyze_deviations(
        self, 
        status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze distribution deviations from target.
        
        Args:
            status: Current distribution status
            
        Returns:
            dict: Deviation analysis
        """
        try:
            target_dist = self.distribution_service.target_distribution
            current_dist = status.get('distribution_percentages', {})
            
            deviations = {}
            
            for category in ['administration', 'stewardship']:
                target = Decimal(str(target_dist.get(category, 0)))
                current = Decimal(str(current_dist.get(category, 0)))
                
                deviation = current - target
                deviation_pct = (deviation / target * 100) if target > 0 else 0
                
                threshold = self.distribution_service.rebalance_threshold
                is_out_of_range = abs(deviation) > threshold
                
                deviations[category] = {
                    'target': float(target),
                    'current': float(current),
                    'deviation': float(deviation),
                    'deviation_percent': float(deviation_pct),
                    'status': 'OUT_OF_RANGE' if is_out_of_range else 'OK'
                }
            
            return deviations
            
        except Exception as e:
            self.logger.error(f"Error analyzing deviations: {e}")
            return {}
    
    async def _get_pending_transfers(self) -> List[Dict[str, Any]]:
        """
        Get list of pending transfer recommendations.
        
        Returns:
            list: Pending transfers
        """
        try:
            schema = self.distribution_service.db_schema
            
            query = f"""
                SELECT 
                    id,
                    from_account_type,
                    to_account_type,
                    amount,
                    priority,
                    created_at,
                    status_message
                FROM {schema}.transfer_recommendations
                WHERE status = 'pending'
                    AND asset_code = $1
                    AND asset_issuer = $2
                ORDER BY priority DESC, created_at ASC
            """
            
            transfers = await self.db_manager.fetch_all(
                query,
                self.distribution_service.ubec_code,
                self.distribution_service.ubec_issuer
            )
            
            return [
                {
                    'id': t['id'],
                    'from': t['from_account_type'],
                    'to': t['to_account_type'],
                    'amount': float(t['amount']),
                    'priority': t['priority'],
                    'created_at': t['created_at'].isoformat(),
                    'message': t['status_message']
                }
                for t in transfers
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting pending transfers: {e}")
            return []
    
    async def _generate_recommendations(
        self,
        status: Dict[str, Any],
        deviations: Dict[str, Any],
        pending_transfers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations.
        
        Args:
            status: Current status
            deviations: Deviation analysis
            pending_transfers: Pending transfers
            
        Returns:
            list: Recommendations
        """
        recommendations = []
        
        # Check compliance
        if not status.get('compliance', {}).get('overall', False):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'COMPLIANCE',
                'action': 'REBALANCE_DISTRIBUTION',
                'description': (
                    'Token distribution is out of compliance with target ratios'
                ),
                'estimated_impact': 'Will restore compliance with tokenomics'
            })
        
        # Check for large deviations
        for category, dev_info in deviations.items():
            if dev_info.get('status') == 'OUT_OF_RANGE':
                recommendations.append({
                    'priority': 'MEDIUM',
                    'category': 'DEVIATION',
                    'action': f'ADJUST_{category.upper()}',
                    'description': (
                        f"{category.title()} account is "
                        f"{abs(dev_info['deviation_percent']):.1f}% off target"
                    ),
                    'estimated_impact': (
                        f"Move {abs(dev_info['deviation']):.2f}% of supply"
                    )
                })
        
        # Check pending transfers
        if pending_transfers:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'PENDING_ACTION',
                'action': 'EXECUTE_PENDING_TRANSFERS',
                'description': f"{len(pending_transfers)} transfers pending execution",
                'estimated_impact': 'Complete scheduled rebalancing operations'
            })
        
        # Sort by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations
    
    def _calculate_health_score(
        self,
        compliance: Dict[str, Any],
        deviations: Dict[str, Any]
    ) -> float:
        """
        Calculate overall distribution health score (0-100).
        
        Args:
            compliance: Compliance status
            deviations: Deviation analysis
            
        Returns:
            float: Health score
        """
        score = 100.0
        
        # Deduct for non-compliance
        if not compliance.get('overall', False):
            score -= 20.0
        
        if not compliance.get('administration', False):
            score -= 10.0
        
        if not compliance.get('stewardship', False):
            score -= 10.0
        
        # Deduct for deviations
        for category, dev_info in deviations.items():
            if dev_info.get('status') == 'OUT_OF_RANGE':
                # Deduct based on deviation percentage
                deviation_pct = abs(dev_info.get('deviation_percent', 0))
                score -= min(deviation_pct * 2, 20.0)
        
        return max(0.0, score)
    
    def _get_health_status(self, score: float) -> str:
        """
        Get health status label from score.
        
        Args:
            score: Health score (0-100)
            
        Returns:
            str: Status label
        """
        if score >= 95:
            return 'EXCELLENT'
        elif score >= 80:
            return 'GOOD'
        elif score >= 60:
            return 'FAIR'
        elif score >= 40:
            return 'POOR'
        else:
            return 'CRITICAL'
    
    def _generate_summary(
        self,
        health_score: float,
        compliance: Dict[str, Any],
        deviations: Dict[str, Any],
        pending_transfers: List[Dict[str, Any]]
    ) -> str:
        """
        Generate human-readable summary.
        
        Args:
            health_score: Health score
            compliance: Compliance status
            deviations: Deviations
            pending_transfers: Pending transfers
            
        Returns:
            str: Summary text
        """
        status = self._get_health_status(health_score)
        
        parts = [f"Distribution health: {status} ({health_score:.1f}%)"]
        
        if compliance.get('overall', False):
            parts.append("All accounts are in compliance with target ratios.")
        else:
            out_of_compliance = []
            if not compliance.get('administration', False):
                out_of_compliance.append('Administration')
            if not compliance.get('stewardship', False):
                out_of_compliance.append('Stewardship')
            
            if out_of_compliance:
                parts.append(
                    f"{', '.join(out_of_compliance)} accounts out of compliance."
                )
        
        if pending_transfers:
            count = len(pending_transfers)
            parts.append(
                f"{count} pending transfer{'s' if count != 1 else ''} "
                f"require{'s' if count == 1 else ''} execution."
            )
        
        return " ".join(parts)
    
    async def _get_account_operation_history(
        self,
        account_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent operation history for an account.
        
        Uses the stellar_operations table with correct schema:
        - operation_id (unique identifier)
        - transaction_hash (transaction reference)
        - type (operation type, not operation_type)
        - source_account
        - amount
        - asset_code
        - created_at
        
        Args:
            account_id: Account ID
            limit: Number of operations to retrieve
            
        Returns:
            list: Recent operations
        """
        try:
            schema = self.distribution_service.db_schema
            
            query = f"""
                SELECT 
                    operation_id,
                    transaction_hash,
                    created_at,
                    type,
                    asset_code,
                    amount,
                    from_account,
                    to_account,
                    details
                FROM {schema}.stellar_operations
                WHERE source_account = $1
                    OR from_account = $1
                    OR to_account = $1
                ORDER BY created_at DESC
                LIMIT $2
            """
            
            operations = await self.db_manager.fetch_all(query, account_id, limit)
            
            return [
                {
                    'operation_id': op['operation_id'],
                    'transaction_hash': op['transaction_hash'],
                    'timestamp': op['created_at'].isoformat(),
                    'type': op['type'],
                    'asset': op['asset_code'],
                    'amount': float(op['amount']) if op['amount'] else 0.0,
                    'from_account': op['from_account'],
                    'to_account': op['to_account'],
                    'details': op['details']
                }
                for op in operations
            ]
            
        except Exception as e:
            self.logger.error(
                f"Error getting operation history for {account_id}: {e}"
            )
            return []
    
    def _get_expected_range_for_type(
        self, 
        account_type: str
    ) -> Optional[Dict[str, float]]:
        """
        Get expected percentage range for account type.
        
        Args:
            account_type: Account type
            
        Returns:
            dict: Expected range or None
        """
        target_dist = self.distribution_service.target_distribution
        threshold = float(self.distribution_service.rebalance_threshold) * 100
        
        if account_type == 'administration':
            target = float(target_dist.get('administration', 0)) * 100
            return {
                'min': target - threshold,
                'max': target + threshold
            }
        elif account_type == 'stewardship':
            target = float(target_dist.get('stewardship', 0)) * 100
            return {
                'min': target - threshold,
                'max': target + threshold
            }
        elif account_type == 'general':
            # General account should hold remainder
            admin_target = float(target_dist.get('administration', 0)) * 100
            steward_target = float(target_dist.get('stewardship', 0)) * 100
            general_target = 100 - admin_target - steward_target
            
            return {
                'min': max(0, general_target - threshold * 2),
                'max': min(100, general_target + threshold * 2)
            }
        
        return None
    
    async def cleanup(self):
        """Cleanup resources on shutdown."""
        self.logger.info("Distribution evaluator cleaned up")


# ========================================================================
# FACTORY FUNCTION
# ========================================================================

def create_evaluator_service(
    distribution_service: Any,
    audit_service: Any,
    db_manager: Any
) -> UBECDistributionEvaluator:
    """
    Factory function to create distribution evaluator instance.
    
    Args:
        distribution_service: Distribution management service
        audit_service: Token audit service
        db_manager: Async database manager
        
    Returns:
        UBECDistributionEvaluator: Initialized evaluator instance
    
    Example:
        evaluator = create_evaluator_service(
            distribution_service=registry.get('distribution'),
            audit_service=registry.get('audit'),
            db_manager=registry.get('database')
        )
    """
    return UBECDistributionEvaluator(
        distribution_service=distribution_service,
        audit_service=audit_service,
        db_manager=db_manager
    )


# Export public interface
__all__ = [
    'UBECDistributionEvaluator',
    'create_evaluator_service'
]
