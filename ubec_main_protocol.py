#!/usr/bin/env python3
# ubec_main_protocol.py
"""
UBEC Main Protocol - Four Element Coordinator
==============================================
Main orchestrator for Air, Water, Earth, and Fire protocols

Usage:
    python ubec_main_protocol.py [--action ACTION] [--account ACCOUNT] [--output OUTPUT]

Examples:
    python ubec_main_protocol.py                    # Default: health check
    python ubec_main_protocol.py --action health    # System health check
    python ubec_main_protocol.py --action status    # All element statuses
    python ubec_main_protocol.py --action sync      # Sync all elements
    python ubec_main_protocol.py --action evaluate  # Holonic evaluation

Version: 1.0
Date: October 8, 2025
"""

import sys
import argparse
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Import configuration (network comes from .env)
from config import GlobalConfig, get_logger

# Import element protocols
from UBEC import UBECProtocol
from UBECrc import UBECrcProtocol
from UBECgpi import UBECgpiProtocol
from UBECtt import UBECttProtocol

# Setup logging
logger = get_logger('MainProtocol')


class UBECMainProtocol:
    """
    Main UBEC Protocol Coordinator
    Manages all four element protocols and provides unified interface
    """
    
    def __init__(self):
        """Initialize main protocol with all elements"""
        logger.info("=" * 70)
        logger.info("Initializing UBEC Main Protocol")
        logger.info("=" * 70)
        logger.info(f"Network: {GlobalConfig.NETWORK}")
        logger.info(f"Horizon URL: {GlobalConfig.get_horizon_url()}")
        logger.info("")
        
        try:
            # Initialize all element protocols
            logger.info("Initializing element protocols...")
            
            self.air = UBECProtocol()          # 🜁 Gateway
            logger.info("  ✓ Air (UBEC) protocol initialized")
            
            self.water = UBECrcProtocol()      # 🜄 Flow
            logger.info("  ✓ Water (UBECrc) protocol initialized")
            
            self.earth = UBECgpiProtocol()     # 🜃 Stability
            logger.info("  ✓ Earth (UBECgpi) protocol initialized")
            
            self.fire = UBECttProtocol()       # 🜂 Transformation
            logger.info("  ✓ Fire (UBECtt) protocol initialized")
            
            logger.info("")
            logger.info("All element protocols initialized successfully")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Failed to initialize protocols: {e}")
            raise
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health across all elements
        
        Returns:
            Dictionary containing health status for all elements
        """
        logger.info("Getting system-wide health status...")
        
        try:
            health = {
                'timestamp': datetime.utcnow().isoformat(),
                'network': GlobalConfig.NETWORK,
                'air_health': self.air.health_check(),
                'water_health': self.water.health_check(),
                'earth_health': self.earth.health_check(),
                'fire_health': self.fire.health_check(),
                'overall_status': None
            }
            
            # Calculate overall status
            health['overall_status'] = self._calculate_overall_status(health)
            
            logger.info(f"System health: {health['overall_status']}")
            return health
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'overall_status': 'ERROR'
            }
    
    def get_all_statuses(self) -> Dict[str, Any]:
        """
        Get status of all element protocols
        
        Returns:
            Dictionary containing status for all elements
        """
        logger.info("Getting all element statuses...")
        
        try:
            statuses = {
                'timestamp': datetime.utcnow().isoformat(),
                'network': GlobalConfig.NETWORK,
                'air': self.air.get_status(),
                'water': self.water.get_status(),
                'earth': self.earth.get_status(),
                'fire': self.fire.get_status(),
                'system': {
                    'total_supply': str(GlobalConfig.TOTAL_SUPPLY),
                    'elements_active': 4
                }
            }
            
            logger.info("All statuses retrieved successfully")
            return statuses
            
        except Exception as e:
            logger.error(f"Error getting statuses: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def sync_all_elements(self) -> Dict[str, Any]:
        """
        Synchronize all element protocols
        
        Returns:
            Dictionary containing sync results for all elements
        """
        logger.info("Starting synchronization of all elements...")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'network': GlobalConfig.NETWORK,
            'results': {}
        }
        
        # Sync each element
        elements = [
            ('air', self.air, 'sync_gateway_data'),
            ('water', self.water, 'sync_flow_data'),
            ('earth', self.earth, 'sync_stability_data'),
            ('fire', self.fire, 'sync_transformation_data')
        ]
        
        for name, protocol, method_name in elements:
            try:
                logger.info(f"  Syncing {name}...")
                if hasattr(protocol, method_name):
                    result = getattr(protocol, method_name)()
                    results['results'][name] = {
                        'status': 'success',
                        'result': result
                    }
                    logger.info(f"  ✓ {name.capitalize()} synced successfully")
                else:
                    results['results'][name] = {
                        'status': 'skipped',
                        'reason': f'Method {method_name} not implemented'
                    }
                    logger.warning(f"  ⚠ {name.capitalize()} sync method not found")
            except Exception as e:
                logger.error(f"  ✗ Error syncing {name}: {e}")
                results['results'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        results['elements_synced'] = sum(
            1 for r in results['results'].values() 
            if r['status'] == 'success'
        )
        
        logger.info(f"Sync complete: {results['elements_synced']}/4 elements synced")
        return results
    
    def evaluate_holonic_health(self) -> Dict[str, Any]:
        """
        Get Ubuntu principles health across all elements
        
        Returns:
            Dictionary containing holonic health metrics
        """
        logger.info("Evaluating holonic health...")
        
        try:
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'network': GlobalConfig.NETWORK,
                'principles': {}
            }
            
            # Get principle assessment for each element
            elements = [
                ('air', self.air, 'assess_diversity'),
                ('water', self.water, 'assess_reciprocity'),
                ('earth', self.earth, 'assess_mutualism'),
                ('fire', self.fire, 'assess_regeneration')
            ]
            
            for name, protocol, method_name in elements:
                try:
                    if hasattr(protocol, method_name):
                        assessment = getattr(protocol, method_name)()
                        metrics['principles'][name] = assessment
                        logger.info(f"  ✓ {name.capitalize()}: {assessment.get('score', 'N/A')}")
                    else:
                        logger.warning(f"  ⚠ {name.capitalize()}: Method not implemented")
                        metrics['principles'][name] = {
                            'status': 'not_implemented'
                        }
                except Exception as e:
                    logger.error(f"  ✗ Error evaluating {name}: {e}")
                    metrics['principles'][name] = {
                        'error': str(e)
                    }
            
            logger.info("Holonic evaluation complete")
            return metrics
            
        except Exception as e:
            logger.error(f"Error in holonic evaluation: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _calculate_overall_status(self, health: Dict) -> str:
        """Calculate overall system status from element health"""
        try:
            # Check if all elements are healthy by looking at their active flags
            element_checks = {
                'air_health': ['gateway_active', 'issuer_active'],
                'water_health': ['system_active', 'reciprocity_tracking', 'flow_monitoring'],
                'earth_health': ['system_active', 'stability_monitoring', 'asset_backing'],
                'fire_health': ['system_active', 'transformation_tracking', 'burn_mechanism']
            }
            
            active_elements = 0
            degraded_elements = []
            
            for element, checks in element_checks.items():
                if element in health and isinstance(health[element], dict):
                    # Check if any of the key flags are true
                    is_active = any(health[element].get(check, False) for check in checks)
                    
                    if is_active:
                        active_elements += 1
                    else:
                        degraded_elements.append(element.replace('_health', ''))
            
            # Determine overall status
            if active_elements == 4:
                return 'EXCELLENT - All 4 elements operational'
            elif active_elements >= 3:
                return f'GOOD - {active_elements}/4 elements operational'
            elif active_elements >= 2:
                return f'DEGRADED - Only {active_elements}/4 elements operational'
            elif active_elements >= 1:
                return f'CRITICAL - Only {active_elements}/4 elements operational'
            else:
                return 'SYSTEM DOWN - No elements operational'
            
        except Exception as e:
            logger.error(f"Error calculating overall status: {e}")
            return 'ERROR'


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='UBEC Main Protocol - Four Element Coordinator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ubec_main_protocol.py                    # Default: health check
  python ubec_main_protocol.py --action health    # System health check
  python ubec_main_protocol.py --action status    # All element statuses
  python ubec_main_protocol.py --action sync      # Sync all elements
  python ubec_main_protocol.py --action evaluate  # Holonic evaluation

Network configuration is read from .env file (UBEC_NETWORK variable).
        """
    )
    
    parser.add_argument(
        '--action',
        type=str,
        choices=['health', 'status', 'sync', 'evaluate'],
        default='health',
        help='Action to perform (default: health)'
    )
    
    parser.add_argument(
        '--account',
        type=str,
        help='Specific account to query (optional)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        choices=['json', 'pretty', 'summary'],
        default='pretty',
        help='Output format (default: pretty)'
    )
    
    parser.add_argument(
        '--network',
        type=str,
        choices=['testnet', 'mainnet'],
        help='Override network from .env (optional - not recommended)'
    )
    
    return parser.parse_args()


def format_output(data: Dict, output_format: str) -> str:
    """Format output based on specified format"""
    if output_format == 'json':
        return json.dumps(data, indent=2, default=str)
    
    elif output_format == 'summary':
        # Brief summary
        lines = []
        lines.append(f"Timestamp: {data.get('timestamp', 'N/A')}")
        lines.append(f"Network: {data.get('network', 'N/A')}")
        
        if 'overall_status' in data:
            lines.append(f"Status: {data['overall_status']}")
        
        return '\n'.join(lines)
    
    else:  # pretty
        return json.dumps(data, indent=2, default=str)


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Override network if specified (not recommended)
    if args.network:
        logger.warning(f"Overriding network from .env: {GlobalConfig.NETWORK} → {args.network}")
        GlobalConfig.NETWORK = args.network
    
    try:
        # Initialize main protocol
        protocol = UBECMainProtocol()
        
        # Execute requested action
        if args.action == 'health':
            result = protocol.get_system_health()
        elif args.action == 'status':
            result = protocol.get_all_statuses()
        elif args.action == 'sync':
            result = protocol.sync_all_elements()
        elif args.action == 'evaluate':
            result = protocol.evaluate_holonic_health()
        else:
            logger.error(f"Unknown action: {args.action}")
            sys.exit(1)
        
        # Output result
        output = format_output(result, args.output)
        print("\n" + "=" * 70)
        print(f"UBEC Protocol - {args.action.upper()} Result")
        print("=" * 70)
        print(output)
        print("=" * 70 + "\n")
        
        # Exit with appropriate code
        if 'error' in result or 'ERROR' in result.get('overall_status', ''):
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
