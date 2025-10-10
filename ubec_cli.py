#!/usr/bin/env python3
# ubec_cli.py
"""
UBEC Command Line Interface
---------------------------

A unified CLI for managing UBEC token data synchronization, holonic evaluation,
and visualization.

This CLI combines the functionality of the previous sync_cli.py and ubec_holonic_cli.py
into a single entry point with subcommands for different operations.
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

# Ensure the parent directory is in the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


def setup_logging(log_level='INFO', log_file=None):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: File to log to (in addition to console)
    """
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    logging.info(f"Logging initialized at {log_level} level")


def create_output_dir(output_dir):
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir: Directory path to create
        
    Returns:
        str: The created directory path
    """
    if not output_dir:
        # Create a timestamped directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"ubec_output_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Output directory created: {output_dir}")
    return output_dir


def sync_command(args):
    """
    Handle the 'sync' subcommand functionality.
    
    Args:
        args: Parsed command-line arguments
    """
    from db.ubec_data_synchronizer import UBECDataSynchronizer
    
    logging.info("Starting UBEC data synchronization")
    
    try:
        # Initialize synchronizer
        syncer = UBECDataSynchronizer(config_path=args.config)
        
        if args.setup:
            # Set up core accounts and scheduled jobs
            logging.info("Setting up core accounts and scheduled jobs")
            core_count = syncer.setup_core_accounts()
            job_success = syncer.setup_scheduled_jobs()
            logging.info(f"Setup completed: {core_count} core accounts configured, jobs setup: {job_success}")
        
        if args.find_all_holders:
            # Find all UBEC holders from the Stellar network
            logging.info(f"Finding all UBEC holders from Stellar network (max {args.max_accounts} accounts, batch size {args.batch_size})")
            count = syncer.find_all_holders_from_network(
                batch_size=args.batch_size,
                max_accounts=args.max_accounts
            )
            logging.info(f"Find all holders completed: {count} holders found and saved")
        
        if args.discover:
            # Discover new UBEC holders
            logging.info(f"Discovering new UBEC holders (looking back {args.days} days)")
            new_count = syncer.discover_new_holders(days_back=args.days)
            logging.info(f"Discovery completed: {new_count} new holders found")
        
        if args.sync_all:
            # Sync all UBEC holders
            min_balance = args.min_balance if hasattr(args, 'min_balance') else 0
            max_accounts = args.max_accounts if hasattr(args, 'max_accounts') else 100
            
            logging.info(f"Syncing all UBEC holders with balance >= {min_balance} "
                        f"(looking back {args.days} days, max {max_accounts} accounts)")
            
            count = syncer.sync_all_holders(
                min_balance=min_balance, 
                days_back=args.days,
                max_accounts=max_accounts
            )
            
            logging.info(f"Sync completed: {count} accounts with new transactions")
        
        if args.account:
            # Sync a specific account
            logging.info(f"Syncing account {args.account} (looking back {args.days} days)")
            count = syncer.sync_account_transactions(args.account, days_back=args.days)
            logging.info(f"Sync completed: {count} new transactions for {args.account}")
        
        if args.run_jobs:
            # Run scheduled jobs once
            logging.info("Running all scheduled jobs")
            count = syncer.run_scheduled_jobs()
            logging.info(f"Jobs completed: {count} jobs executed")
        
        if args.continuous:
            # Run continuous synchronization
            logging.info(f"Starting continuous synchronization (interval: {args.interval} seconds)")
            syncer.run_continuous_sync(check_interval_seconds=args.interval)
        
        return 0
        
    except Exception as e:
        logging.error(f"Synchronization error: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        return 1


def inspect_account(args):
    """
    Inspect account data in the database.
    
    Args:
        args: Parsed command-line arguments
    """
    try:
        from db.connection import DatabaseManager
        db = DatabaseManager(schema='ubec_recipro')
        
        account_id = args.account
        limit = args.limit if hasattr(args, 'limit') else 10
        
        # Get asset holder info
        asset_query = """
        SELECT ah.account_id, ah.balance, ah.classification, 
               ah.last_updated_at, ah.is_active
        FROM ubec_recipro.asset_holders ah
        WHERE ah.account_id = %s AND asset_code = %s AND asset_issuer = %s
        """
        
        try:
            from config import settings
            ubec_code = settings.UBEC_CODE
            ubec_issuer = settings.UBEC_ISSUER
        except ImportError:
            # Fallback values if settings can't be imported
            ubec_code = "UBEC"
            ubec_issuer = "GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN"
        
        account_info = db.execute_query(asset_query, [account_id, ubec_code, ubec_issuer], fetch_one=True)
        
        if not account_info:
            print(f"Account {account_id} not found in asset_holders table")
        else:
            print("\n=== ACCOUNT INFORMATION ===")
            print(f"Account ID: {account_info['account_id']}")
            print(f"Balance: {account_info['balance']} UBEC")
            print(f"Classification: {account_info['classification']}")
            print(f"Last Updated: {account_info['last_updated_at']}")
            print(f"Active: {account_info['is_active']}")
        
        # Get participant information
        part_query = """
        SELECT p.id, p.account_id, p.account_type, p.joined_at, p.last_activity_at
        FROM ubec_recipro.participants p
        WHERE p.account_id = %s
        """
        
        participant = db.execute_query(part_query, [account_id], fetch_one=True)
        
        if participant:
            print("\n=== PARTICIPANT INFORMATION ===")
            print(f"ID: {participant['id']}")
            print(f"Account Type: {participant['account_type']}")
            print(f"Joined: {participant['joined_at']}")
            print(f"Last Activity: {participant['last_activity_at']}")
            
            # Get agent information if participant exists
            agent_query = """
            SELECT a.id, a.role, a.tier, a.reciprocity_score, a.reciprocity_credits,
                   a.last_activity_timestamp
            FROM ubec_recipro.agents a
            WHERE a.participant_id = %s
            """
            
            agent = db.execute_query(agent_query, [participant['id']], fetch_one=True)
            
            if agent:
                print("\n=== AGENT INFORMATION ===")
                print(f"Agent ID: {agent['id']}")
                print(f"Role: {agent['role']}")
                print(f"Tier: {agent['tier']}")
                print(f"Reciprocity Score: {agent['reciprocity_score']}")
                print(f"Reciprocity Credits: {agent['reciprocity_credits']}")
                last_activity = datetime.fromtimestamp(agent['last_activity_timestamp']) if agent['last_activity_timestamp'] else "Never"
                print(f"Last Activity: {last_activity}")
        else:
            print(f"Account {account_id} not found in participants table")
        
        # Get sync status
        sync_query = """
        SELECT last_sync, last_transaction_id, sync_count, status, error_count, last_error
        FROM ubec_recipro.sync_status
        WHERE account_id = %s
        """
        
        sync_status = db.execute_query(sync_query, [account_id], fetch_one=True)
        
        if sync_status:
            print("\n=== SYNC STATUS ===")
            print(f"Last Sync: {sync_status['last_sync']}")
            print(f"Sync Count: {sync_status['sync_count']}")
            print(f"Status: {sync_status['status']}")
            print(f"Error Count: {sync_status['error_count']}")
            if sync_status['last_error']:
                print(f"Last Error: {sync_status['last_error']}")
        
        # Get transactions
        tx_query = """
        SELECT operation_id, transaction_id, created_at, operation_type, 
               source_account, destination_account, amount, asset_code
        FROM ubec_recipro.transaction_operations 
        WHERE (source_account = %s OR destination_account = %s)
        ORDER BY created_at DESC
        LIMIT %s
        """
        
        transactions = db.execute_query(tx_query, [account_id, account_id, limit])
        
        print(f"\n=== RECENT TRANSACTIONS (Top {limit}) ===")
        if not transactions:
            print("No transactions found")
        else:
            for tx in transactions:
                direction = "OUT" if tx['source_account'] == account_id else "IN"
                asset = tx.get('asset_code', 'UBEC')
                print(f"{tx['created_at']} | {direction} | {tx.get('amount', 'N/A')} {asset} | {tx['operation_type']}")
                print(f"  Transaction: {tx['transaction_id']}")
                if direction == "OUT":
                    print(f"  Destination: {tx['destination_account']}")
                else:
                    print(f"  Source: {tx['source_account']}")
                
        return 0
        
    except Exception as e:
        print(f"Error inspecting account: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        return 1


def evaluate_command(args):
    """
    Handle the 'evaluate' subcommand functionality.
    """
    from holonic.ubec_holonic_evaluator import UBECHolonicEvaluator
    
    logging.info("Starting UBEC holonic evaluation")
    
    try:
        # Create evaluator with the specified config
        evaluator = UBECHolonicEvaluator(config_path=args.config)
        
        # Log default thresholds if DEBUG logging is enabled
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug(f"Default composite thresholds: {evaluator.thresholds.get('composite', {})}")
            logging.debug(f"Default autonomy thresholds: {evaluator.thresholds.get('autonomy_integration', {})}")
        
        # Customize thresholds if needed
        if args.thresholds:
            try:
                logging.info(f"Loading custom thresholds from {args.thresholds}")
                with open(args.thresholds, 'r') as f:
                    custom_thresholds = json.load(f)
                
                # Output the loaded thresholds for debugging
                logging.info(f"Custom thresholds loaded: {json.dumps(custom_thresholds, indent=2)}")
                
                # Update thresholds
                for category, values in custom_thresholds.items():
                    if category in evaluator.thresholds:
                        logging.info(f"Updating {category} thresholds with {values}")
                        evaluator.thresholds[category].update(values)
                    else:
                        logging.warning(f"Unknown threshold category: {category}")
                
                # Log updated thresholds
                if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
                    logging.debug(f"Updated composite thresholds: {evaluator.thresholds.get('composite', {})}")
                    logging.debug(f"Updated autonomy thresholds: {evaluator.thresholds.get('autonomy_integration', {})}")
                
                logging.info(f"Custom thresholds successfully applied")
            except Exception as e:
                logging.error(f"Error loading thresholds file: {e}")
                import traceback
                logging.error(traceback.format_exc())
        
        # Run the evaluation
        logging.info("Starting holonic evaluation with current thresholds")
        evaluation_report = evaluator.run_evaluation()
        
        # Create output directory if needed
        output_dir = create_output_dir(args.output_dir)
        
        # Save the report
        if args.output:
            output_file = args.output
        else:
            # Generate a timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"ubec_holonic_report_{timestamp}.json")
        
        with open(output_file, 'w') as f:
            json.dump(evaluation_report, f, indent=2)
        
        logging.info(f"Evaluation report saved to {output_file}")
        
        # Log summary of category distribution for verification
        if 'category_distribution' in evaluation_report:
            logging.info(f"Category distribution summary: {evaluation_report['category_distribution']}")
        
        # Auto-enable visualize if any visualization flags are set
        if args.all_viz or args.score_dist or args.radar or args.category_dist or args.network or args.html_report:
            args.visualize = True
            logging.info("Visualization automatically enabled based on visualization flags")
        
        # If visualizations are requested, generate them
        if args.visualize:
            logging.info("Starting visualization process")
            visualize_args = argparse.Namespace(
                report=output_file,
                all_viz=args.all_viz,
                score_dist=args.score_dist,
                radar=args.radar,
                category_dist=args.category_dist,
                network=args.network,
                html_report=args.html_report,
                viz_output=output_dir,
                log_level=args.log_level if hasattr(args, 'log_level') else 'INFO',
                log_file=args.log_file if hasattr(args, 'log_file') else None,
                config=args.config
            )
            
            visualize_command(visualize_args, evaluator)
        
        return 0
        
    except Exception as e:
        logging.error(f"Evaluation error: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        return 1

def visualize_command(args, evaluator=None):
    """
    Handle the 'visualize' subcommand functionality.
    """
    from holonic.ubec_holonic_visualizer import UBECHolonicVisualizer
    import matplotlib
    matplotlib.use('Agg')  # Force non-interactive backend
    
    logging.info("Starting UBEC visualization")
    
    try:
        # Create output directory if needed
        output_dir = create_output_dir(args.viz_output)
        
        # Verify the report file exists
        if not os.path.exists(args.report):
            logging.error(f"Report file not found: {args.report}")
            return 1
        
        # Check if the report has content
        try:
            with open(args.report, 'r') as f:
                report_data = json.load(f)
                
            result_count = len(report_data.get('results', []))
            logging.info(f"Report loaded with {result_count} results")
            
            if result_count == 0:
                logging.warning("Report contains no results - visualizations may be empty")
        except Exception as e:
            logging.error(f"Error reading report file: {e}")
            return 1
        
        # Create visualizer
        logging.info(f"Creating visualizer for report: {args.report}")
        visualizer = UBECHolonicVisualizer(report_file=args.report)
        
        # If we have the evaluator, add the transaction network to the visualizer
        if evaluator and hasattr(evaluator, 'transaction_network'):
            logging.info("Adding transaction network to visualizer")
            visualizer.transaction_network = evaluator.transaction_network
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Handle HTML report generation separately with detailed error logging
        if args.html_report:
            try:
                logging.info(f"Generating HTML report in directory: {output_dir}")
                html_report = visualizer.generate_html_report(output_dir=output_dir)
                
                if html_report and os.path.exists(html_report):
                    logging.info(f"HTML report successfully generated: {html_report}")
                else:
                    logging.error(f"HTML report generation failed: file not created")
            except Exception as e:
                logging.error(f"Error generating HTML report: {e}")
                import traceback
                logging.error(traceback.format_exc())
        
        # Generate the other requested visualizations
        if args.all_viz or args.score_dist:
            try:
                score_dist_file = os.path.join(output_dir, f"score_distribution_{timestamp}.png")
                logging.info(f"Creating score distribution chart: {score_dist_file}")
                visualizer.create_score_distribution_chart(score_dist_file)
                logging.info(f"Score distribution chart saved to {score_dist_file}")
            except Exception as e:
                logging.error(f"Error creating score distribution chart: {e}")
                import traceback
                logging.error(traceback.format_exc())
        
        if args.all_viz or args.radar:
            try:
                radar_file = os.path.join(output_dir, f"radar_chart_{timestamp}.png")
                logging.info(f"Creating radar chart: {radar_file}")
                visualizer.create_radar_chart(output_file=radar_file)
                logging.info(f"Radar chart saved to {radar_file}")
            except Exception as e:
                logging.error(f"Error creating radar chart: {e}")
                import traceback
                logging.error(traceback.format_exc())
        
        if args.all_viz or args.category_dist:
            try:
                category_file = os.path.join(output_dir, f"category_distribution_{timestamp}.png")
                logging.info(f"Creating category distribution chart: {category_file}")
                visualizer.create_category_distribution_chart(category_file)
                logging.info(f"Category distribution chart saved to {category_file}")
            except Exception as e:
                logging.error(f"Error creating category distribution chart: {e}")
                import traceback
                logging.error(traceback.format_exc())
        
        if (args.all_viz or args.network) and hasattr(visualizer, 'transaction_network'):
            try:
                network_file = os.path.join(output_dir, f"network_visualization_{timestamp}.png")
                logging.info(f"Creating network visualization: {network_file}")
                visualizer.create_network_visualization(network_file)
                logging.info(f"Network visualization saved to {network_file}")
            except Exception as e:
                logging.error(f"Error creating network visualization: {e}")
                import traceback
                logging.error(traceback.format_exc())
        
        return 0
        
    except Exception as e:
        logging.error(f"Visualization error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return 1

def audit_command(args):
    """
    Handle the 'audit' subcommand functionality.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    from audit.ubec_token_audit import UBECTokenAudit
    
    logging.info("Starting UBEC token audit")
    
    try:
        # Initialize auditor
        auditor = UBECTokenAudit(
            config_path=args.config, 
            data_source=args.source,
            include_holonic=args.include_holonic
        )
        
        # Perform audit
        audit_report = auditor.perform_audit()
        
        # Create output directory if needed
        output_dir = create_output_dir(args.output_dir)
        
        # Generate recommendations if requested
        if args.recommendations:
            auditor.add_transfer_recommendations()
        
        # Save audit report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_dir, f"ubec_audit_report_{timestamp}.json")
        
        with open(report_file, 'w') as f:
            # Convert Decimal values to strings for JSON serialization
            json.dump(audit_report, f, indent=2, default=str)
        
        logging.info(f"Audit report saved to {report_file}")
        
        # Save account lists if requested
        if args.save_accounts:
            output_files = auditor.save_ubec_account_lists(output_dir)
            logging.info(f"Account lists saved to {output_dir}")
            
            # Create a readme file with file descriptions
            readme_path = os.path.join(output_dir, "ACCOUNT_FILES_README.txt")
            with open(readme_path, 'w') as f:
                f.write("UBEC TOKEN HOLDER ACCOUNT FILES\n")
                f.write("==============================\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for file_type, file_path in output_files.items():
                    file_name = os.path.basename(file_path)
                    f.write(f"{file_type}:\n")
                    f.write(f"  {file_name}\n\n")
        
        # Print summary to console
        compliance = audit_report["tokenomics_compliance"]["overall"]
        general_balance = float(audit_report["accounts"]["general"]["balance"])
        admin_balance = float(audit_report["accounts"]["administration"]["balance"])
        steward_balance = float(audit_report["accounts"]["stewardship"]["total_with_pools"])
        total_monitored = float(audit_report["total_monitored"])
        total_supply = float(audit_report["total_supply"])
        
        print("\n=== UBEC TOKEN AUDIT SUMMARY ===")
        print(f"Tokenomics compliance: {'Yes' if compliance else 'No'}")
        print(f"Total supply: {total_supply:,.2f} UBEC")
        print(f"Monitored supply: {total_monitored:,.2f} UBEC ({total_monitored/total_supply*100:.2f}%)")
        print("\nCurrent Distribution:")
        print(f"  General: {general_balance:,.2f} UBEC ({general_balance/total_monitored*100:.2f}% of monitored)")
        print(f"  Administration: {admin_balance:,.2f} UBEC ({admin_balance/total_supply*100:.2f}% of total supply)")
        print(f"  Stewardship: {steward_balance:,.2f} UBEC ({steward_balance/total_supply*100:.2f}% of total supply)")
        print("\nTarget Distribution:")
        print(f"  Administration: 5.00% of total supply")
        print(f"  Stewardship: 30.00% of total supply")
        print(f"\nFor full details, see: {report_file}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Audit error: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        return 1


def distribute_command(args):
    """
    Handle the 'distribute' subcommand functionality.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    from ubec_distribution_manager import UBECDistributionManager
    
    logging.info("Starting UBEC distribution management")
    
    try:
        # Initialize distribution manager
        manager = UBECDistributionManager(data_source=args.source)
        
        if args.check:
            # Check if rebalance is needed
            needs_rebalance, distribution = manager.is_rebalance_needed()
            
            if needs_rebalance:
                logging.info("Rebalance is needed")
                print("\n=== UBEC DISTRIBUTION CHECK ===")
                print("Rebalance is NEEDED")
                print("\nCurrent Distribution:")
                for category, percentage in distribution.items():
                    print(f"  {category.capitalize()}: {float(percentage)*100:.2f}%")
            else:
                logging.info("No rebalance needed")
                print("\n=== UBEC DISTRIBUTION CHECK ===")
                print("Distribution is COMPLIANT - no rebalance needed")
                print("\nCurrent Distribution:")
                for category, percentage in distribution.items():
                    print(f"  {category.capitalize()}: {float(percentage)*100:.2f}%")
            
            return 0
        
        if args.rebalance:
            # Perform rebalance
            logging.info("Performing rebalance")
            manager.perform_rebalance()
            
            # Check new distribution after rebalance
            _, new_distribution = manager.is_rebalance_needed()
            
            print("\n=== UBEC DISTRIBUTION REBALANCE ===")
            print("Rebalance completed")
            print("\nNew Distribution:")
            for category, percentage in new_distribution.items():
                print(f"  {category.capitalize()}: {float(percentage)*100:.2f}%")
            
            return 0
        
        if args.daemon:
            # Run distribution manager as a daemon
            logging.info(f"Starting distribution manager daemon (interval: {args.interval} seconds)")
            manager.check_interval = args.interval
            manager.run()
            return 0
        
        # If no specific action is requested, just print the current distribution
        _, distribution = manager.is_rebalance_needed()
        
        print("\n=== UBEC CURRENT DISTRIBUTION ===")
        for category, percentage in distribution.items():
            print(f"  {category.capitalize()}: {float(percentage)*100:.2f}%")
        
        return 0
        
    except Exception as e:
        logging.error(f"Distribution error: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        return 1


def main():
    """
    Main entry point for the UBEC CLI.
    """
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="UBEC Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync data from blockchain to database
  python ubec_cli.py sync --discover --sync-all
  
  # Find all UBEC holders on the Stellar network
  python ubec_cli.py sync --find-all-holders --max-accounts 1000
  
  # Run holonic evaluation and generate HTML report
  python ubec_cli.py evaluate --all-viz --html-report
  
  # Run holonic evaluation with custom thresholds
  python ubec_cli.py evaluate --thresholds custom_thresholds.json --all-viz
  
  # Visualize an existing report
  python ubec_cli.py visualize --report report.json --all-viz
  
  # Run a token audit with recommendations
  python ubec_cli.py audit --recommendations --save-accounts
  
  # Perform a token distribution rebalance
  python ubec_cli.py distribute --rebalance
  
  # Inspect account data in the database
  python ubec_cli.py inspect --account GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN
        """
    )
    
    # Global arguments
    parser.add_argument('--config', default='config/settings.py',
                      help='Path to config/settings.py file')
    parser.add_argument('--log-level', default='INFO',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Logging level')
    parser.add_argument('--log-file', 
                      help='Log to file (in addition to console)')
    
    # Create subparsers for different command groups
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # === SYNC command ===
    sync_parser = subparsers.add_parser('sync', help='Synchronize data from Stellar blockchain to database')
    sync_parser.add_argument('--setup', action='store_true', 
                          help='Set up core accounts and scheduled jobs')
    sync_parser.add_argument('--discover', action='store_true',
                          help='Discover new UBEC holders from recent transactions')
    sync_parser.add_argument('--find-all-holders', action='store_true',
                          help='Find all UBEC holders from the Stellar network')
    sync_parser.add_argument('--sync-all', action='store_true',
                          help='Sync all UBEC holders')
    sync_parser.add_argument('--account',
                          help='Sync a specific account')
    sync_parser.add_argument('--run-jobs', action='store_true',
                          help='Run all scheduled jobs once')
    sync_parser.add_argument('--continuous', action='store_true',
                          help='Run as a daemon process')
    sync_parser.add_argument('--days', type=int, default=30,
                          help='Number of days to look back')
    sync_parser.add_argument('--interval', type=int, default=300,
                          help='Check interval for continuous mode (seconds)')
    sync_parser.add_argument('--min-balance', type=float, default=0,
                          help='Minimum balance to consider an account active')
    sync_parser.add_argument('--max-accounts', type=int, default=100,
                          help='Maximum number of accounts to process in one run')
    sync_parser.add_argument('--batch-size', type=int, default=100,
                          help='Batch size for API requests when finding holders')
    sync_parser.add_argument('--force', action='store_true',
                          help='Force update regardless of last sync time')
    sync_parser.set_defaults(func=sync_command)
    
    # === INSPECT command ===
    inspect_parser = subparsers.add_parser('inspect', help='Inspect account data in the database')
    inspect_parser.add_argument('--account', required=True, 
                             help='Account ID to inspect')
    inspect_parser.add_argument('--limit', type=int, default=10,
                             help='Maximum number of transactions to display')
    inspect_parser.set_defaults(func=inspect_account)
    
    # === EVALUATE command ===
    eval_parser = subparsers.add_parser('evaluate', help='Run holonic evaluation')
    eval_parser.add_argument('--output', 
                          help='Output filename for the evaluation report')
    eval_parser.add_argument('--thresholds',
                          help='JSON file with custom metric thresholds')
    eval_parser.add_argument('--output-dir',
                          help='Directory for output files')
    
    # Visualization options for evaluate command
    eval_parser.add_argument('--visualize', action='store_true',
                          help='Generate visualizations after evaluation')
    eval_parser.add_argument('--all-viz', action='store_true',
                          help='Generate all visualizations')
    eval_parser.add_argument('--score-dist', action='store_true',
                          help='Generate score distribution chart')
    eval_parser.add_argument('--radar', action='store_true',
                          help='Generate radar chart')
    eval_parser.add_argument('--category-dist', action='store_true',
                          help='Generate category distribution chart')
    eval_parser.add_argument('--network', action='store_true',
                          help='Generate network visualization')
    eval_parser.add_argument('--html-report', action='store_true',
                          help='Generate HTML report')
    eval_parser.set_defaults(func=evaluate_command)
    
    # === VISUALIZE command ===
    viz_parser = subparsers.add_parser('visualize', help='Generate visualizations from an existing report')
    viz_parser.add_argument('--report', required=True,
                          help='Path to evaluation report JSON file')
    viz_parser.add_argument('--all-viz', action='store_true',
                          help='Generate all visualizations')
    viz_parser.add_argument('--score-dist', action='store_true',
                          help='Generate score distribution chart')
    viz_parser.add_argument('--radar', action='store_true',
                          help='Generate radar chart')
    viz_parser.add_argument('--category-dist', action='store_true',
                          help='Generate category distribution chart')
    viz_parser.add_argument('--network', action='store_true',
                          help='Generate network visualization')
    viz_parser.add_argument('--html-report', action='store_true',
                          help='Generate HTML report')
    viz_parser.add_argument('--viz-output',
                          help='Directory for visualization outputs')
    viz_parser.set_defaults(func=visualize_command)
    
    # === AUDIT command ===
    audit_parser = subparsers.add_parser('audit', help='Audit UBEC token distribution')
    audit_parser.add_argument('--source', choices=['db', 'stellar', 'hybrid'], default='hybrid',
                            help='Data source (database, Stellar, or hybrid)')
    audit_parser.add_argument('--include-holonic', action='store_true',
                            help='Include holonic evaluation in audit')
    audit_parser.add_argument('--recommendations', action='store_true',
                            help='Generate transfer recommendations')
    audit_parser.add_argument('--save-accounts', action='store_true',
                            help='Save account lists to files')
    audit_parser.add_argument('--output-dir',
                            help='Directory for output files')
    audit_parser.set_defaults(func=audit_command)
    
    # === DISTRIBUTE command ===
    dist_parser = subparsers.add_parser('distribute', help='Manage UBEC token distribution')
    dist_parser.add_argument('--source', choices=['db', 'stellar', 'hybrid'], default='hybrid',
                           help='Data source (database, Stellar, or hybrid)')
    dist_parser.add_argument('--check', action='store_true',
                           help='Check if rebalance is needed')
    dist_parser.add_argument('--rebalance', action='store_true',
                           help='Perform rebalance if needed')
    dist_parser.add_argument('--daemon', action='store_true',
                           help='Run as a daemon process')
    dist_parser.add_argument('--interval', type=int, default=3600,
                           help='Check interval for daemon mode (seconds)')
    dist_parser.set_defaults(func=distribute_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # If no command provided, show help
    if not args.command:
        parser.print_help()
        return 1
    
    # Run the appropriate function based on the subcommand
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
