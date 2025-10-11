# holonic/ubec_holonic_evaluator.py

"""
UBEC Holonic Evaluator - Ubuntu Philosophy Implementation

This module evaluates UBEC token holders based on holonic principles, measuring:
1. Balance of Autonomy and Integration
2. Multi-scale Participation  
3. Regenerative Impact
4. Network Contribution
5. Alignment with Ubuntu Philosophy

UPDATED: October 11, 2025
- Updated to use NEW config standard (GlobalConfig first, settings fallback)
- Uses stellar_operations table directly (NEW standard, no compatibility layers)
- Enhanced error handling for database queries
- Improved logging for debugging
- Simplified schema validation (NEW standard only)

This project uses the services of Claude and Anthropic PBC to inform our decisions 
and recommendations. This project was made possible with the assistance of Claude 
and Anthropic PBC.
"""

import os
import sys
import logging
import json
import math
from datetime import datetime, timedelta, date
from decimal import Decimal, getcontext
import networkx as nx
import psycopg2
from psycopg2.extras import DictCursor

# Import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import from core.db first (new structure), then fallback to db (legacy)
try:
    from core.db.connection import DatabaseManager, get_connection
except ImportError:
    from db.connection import DatabaseManager, get_connection

# Configure precision for decimal calculations
getcontext().prec = 10

class UBECHolonicEvaluator:
    """
    Evaluates UBEC token holders based on holonic principles.
    
    This evaluator analyzes account activity and metrics to assess:
    1. Balance of Autonomy and Integration: How well account holders maintain individual 
       agency while contributing to collective goals
    2. Multi-scale Participation: Whether account holders engage at multiple levels 
       (local, regional, global)
    3. Regenerative Impact: How account holders create positive environmental and social impacts
    4. Network Contribution: How account holders strengthen the network through participation
    5. Alignment with Ubuntu Philosophy: How account holders embody "I am because we are"
    
    This project uses the services of Claude and Anthropic PBC to inform our decisions 
    and recommendations. This project was made possible with the assistance of Claude 
    and Anthropic PBC.
    """
    
    def __init__(self, config_path="../config/settings.py", db_connection=None):
        """
        Initialize the holonic evaluator using settings from the config file.

        Args:
            config_path: Path to the settings file
            db_connection: Optional database connection
        """
        logging.info(f"Initializing UBEC Holonic Evaluator with config path: {config_path}")

        self.config_path = config_path
        self.load_config()

        self.db_conn = db_connection
        if self.db_conn is None:
            try:
                self.db_conn = get_connection()
                logging.info("Created new database connection")
            except Exception as e:
                logging.error(f"Error creating database connection: {e}")
                raise

        try:
            self.db = DatabaseManager(schema=self.config['db_schema'])
            logging.info(f"Initialized database manager with schema: {self.config['db_schema']}")
        except Exception as e:
            logging.error(f"Error initializing database manager: {e}")
            raise

        self.holders_data = None
        self.transaction_network = None

        # Load accounts from NEW config standard
        try:
            from config.config import GlobalConfig
            global_config = GlobalConfig()
            self.accounts = global_config.ACCOUNTS
            logging.info("✓ Loaded accounts from NEW config standard (GlobalConfig)")
        except (ImportError, AttributeError) as e:
            logging.debug(f"GlobalConfig not available, trying settings: {e}")
            try:
                from config import settings
                self.accounts = settings.ACCOUNTS
                logging.info("✓ Loaded accounts from settings (fallback)")
            except (ImportError, AttributeError) as e2:
                logging.info(f"Using default accounts: {e2}")
                self.accounts = {
                    'general': "GDC2ECKYO4WJMD35M4E2JIABPTA4VLHC6L6MU4TIRCLSOPOOIYOYTM74",
                    'administration': "GDEQ4KXOL6NV5RGETFTJLMULACO5M5GTYBKOEGTCN2MSSJCOAID5UBEC",
                    'stewardship': [
                        "GA3I6MN4NSUKZ2NQZBWLUP6MNMPLZFD3ABOA3CMBV23NBDBFRWRUUBEC",  # Management Account
                        "GCBT4HZHOXJCCVDQDJHA7KR6IN3RANWBPK3DKCSUPN2R4BMCGBZYUBEC",  # Infrastructure Account
                        "GCFJCAHHHDI5XNK3CABHPN565DIPAXP2MPQXCQVYV7IDYQLA6G4JUBEC"   # Liquidity Pool
                    ]
                }

        self.thresholds = {
            'autonomy_integration': {
                'holding_period': 90,
                'transaction_frequency': 5,
                'balance_stability': 0.2,
            },
            'multi_scale': {
                'local_threshold': 10,
                'regional_threshold': 5,
                'global_threshold': 2,
            },
            'regenerative_impact': {
                'impact_projects_min': 1,
                'impact_percentage': 0.05,
            },
            'network_contribution': {
                'connector_score_threshold': 0.3,
                'activity_threshold': 10,
            },
            'ubuntu_alignment': {
                'reciprocity_ratio': 0.8,
                'community_support': 0.1,
            },
            'composite': {
                'Observer': 0.2,
                'Participant': 0.4,
                'Contributor': 0.6,
                'Integrator': 0.8,
                'Exemplar': 0.9
            }
        }

        # Check if holonic_metrics table exists and create if needed
        self._ensure_holonic_tables_exist()
        
        # Validate database schema
        self._validate_database_schema()

        logging.info("UBEC Holonic Evaluator initialized successfully")

    def _ensure_holonic_tables_exist(self):
        """Check if holonic_metrics table exists, and log a warning if it doesn't."""
        try:
            check_query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = '{self.config['db_schema']}'
                AND table_name = 'holonic_metrics'
            );
            """
            result = self.db.execute_query(check_query, fetch_one=True)
            
            if result and not result.get('exists', False):
                logging.warning(
                    f"Table {self.config['db_schema']}.holonic_metrics does not exist. "
                    "Please run the create_holonic_tables.sql script to create it. "
                    "The evaluator will continue but won't be able to store results properly."
                )
                self.holonic_table_exists = False
            else:
                logging.info("Holonic metrics table exists and is ready")
                self.holonic_table_exists = True
        except Exception as e:
            logging.warning(f"Could not check for holonic_metrics table existence: {e}")
            self.holonic_table_exists = False

    def _validate_database_schema(self):
        """
        Validate that the database schema has the required tables.
        
        NEW STANDARD: Only checks for stellar_operations table.
        No backward compatibility checks.
        """
        try:
            # Check for stellar_operations table (the actual data source)
            check_table = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = '{self.config['db_schema']}'
                AND table_name = 'stellar_operations'
            );
            """
            result = self.db.execute_query(check_table, fetch_one=True)
            
            if result and result.get('exists', False):
                # Check row count
                count_query = f"SELECT COUNT(*) as count FROM {self.config['db_schema']}.stellar_operations"
                count_result = self.db.execute_query(count_query, fetch_one=True)
                operation_count = count_result.get('count', 0) if count_result else 0
                
                if operation_count > 0:
                    logging.info(f"✅ stellar_operations table has {operation_count} records")
                else:
                    logging.warning("⚠️  stellar_operations table is empty. Run sync to populate.")
            else:
                logging.error("❌ stellar_operations table not found in schema")
                
        except Exception as e:
            logging.warning(f"Schema validation failed: {e}")

    def load_config(self):
        """
        Load configuration from NEW config standard or use defaults.
        """
        self.config = {
            "db_schema": "ubec_main",
            "batch_size": 50,
            "min_activity": 1,
            "min_reciprocity_score": 0,
            "evaluation_interval_days": 30,
            "max_evaluations": 500,
            "ubec_code": "UBEC",
            "ubec_issuer": "GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN"
        }

        # Try NEW config standard first (GlobalConfig)
        try:
            from config.config import GlobalConfig
            global_config = GlobalConfig()
            
            # Load config values from GlobalConfig if they exist
            if hasattr(global_config, 'UBEC_CODE'):
                self.config['ubec_code'] = global_config.UBEC_CODE
            if hasattr(global_config, 'UBEC_ISSUER'):
                self.config['ubec_issuer'] = global_config.UBEC_ISSUER
            
            logging.info("✓ Loaded config from NEW config standard (GlobalConfig)")
            return
            
        except (ImportError, AttributeError) as e:
            logging.debug(f"GlobalConfig not available: {e}")

        # Fallback: Try to load from settings file
        if self.config_path:
            try:
                config_dir = os.path.dirname(os.path.abspath(self.config_path))
                sys.path.append(config_dir)

                logging.debug(f"Looking for config in: {config_dir}")

                try:
                    from config import settings
                    config_module = settings
                    logging.info("✓ Loaded config from settings module")
                except ImportError:
                    logging.debug(f"Direct import failed, trying to load from {self.config_path}")

                    if not os.path.exists(self.config_path):
                        parent_config_path = os.path.join(os.path.dirname(os.getcwd()), "config/settings.py")
                        if os.path.exists(parent_config_path):
                            self.config_path = parent_config_path
                            logging.debug(f"Found settings file at: {self.config_path}")
                        else:
                            logging.debug(f"Could not find settings file at {self.config_path} or {parent_config_path}")
                            logging.info("Using default configuration")
                            return

                    import importlib.util
                    spec = importlib.util.spec_from_file_location("settings", self.config_path)
                    config_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(config_module)
                    logging.info(f"✓ Loaded config from {self.config_path}")

                # Update config with values from settings
                for key in dir(config_module):
                    if key.isupper() and key in [k.upper() for k in self.config.keys()]:
                        self.config[key.lower()] = getattr(config_module, key)

                logging.info(f"✓ Configuration loaded successfully")

            except Exception as e:
                logging.debug(f"Could not load config from {self.config_path}: {e}")
                logging.info("Using default configuration")
    
    def get_accounts_for_evaluation(self):
        """
        Get accounts that need holonic evaluation from the database.
        
        Returns:
            List of account records that need evaluation
        """
        logging.info("Fetching accounts for evaluation from database")
        
        # First, check what columns exist in the agents table
        try:
            column_check_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = '{self.config['db_schema']}'
              AND table_name = 'agents'
            """
            available_columns = self.db.execute_query(column_check_query, fetch_all=True)
            available_column_names = [col['column_name'] for col in available_columns] if available_columns else []
            logging.debug(f"Available columns in agents table: {available_column_names}")
        except Exception as e:
            logging.warning(f"Could not check agents table columns: {e}")
            available_column_names = []
        
        # Build query based on available columns
        select_parts = [
            "a.id AS agent_id",
            "COALESCE(a.agent_id, p.account_id) AS public_key",
            "p.account_id"
        ]
        
        # Optional columns with fallbacks
        if 'last_activity_at' in available_column_names:
            select_parts.append("EXTRACT(EPOCH FROM a.last_activity_at) AS last_activity_timestamp")
        else:
            select_parts.append("EXTRACT(EPOCH FROM NOW()) AS last_activity_timestamp")
        
        select_parts.extend([
            "COALESCE(a.reciprocity_score, 0) as reciprocity_score",
            "0 as reciprocity_credits",
            "COALESCE(a.loyalty_tier, 'basic') as tier",
            "'regular' as role",
            "COALESCE(p.created_at, NOW()) as joined_at"
        ])
        
        select_clause = ", ".join(select_parts)
        
        # Build WHERE clause
        where_conditions = []
        if 'reciprocity_score' in available_column_names:
            where_conditions.append(f"(a.reciprocity_score > {self.config['min_reciprocity_score']})")
        
        if not where_conditions:
            if 'status' in available_column_names:
                where_clause = "a.status = 'active'"
            else:
                where_clause = "TRUE"
        else:
            where_clause = " OR ".join(where_conditions)
        
        # Try the full query with holonic_metrics join if table exists
        # NOTE: After V8 migration, holonic_metrics uses account_id, not agent_id
        if self.holonic_table_exists and 'last_activity_at' in available_column_names:
            query = f"""
            SELECT {select_clause}
            FROM {self.config['db_schema']}.agents a
            JOIN {self.config['db_schema']}.participants p ON a.participant_id = p.id
            LEFT JOIN (
                SELECT DISTINCT ON (account_id) account_id, evaluation_date
                FROM {self.config['db_schema']}.holonic_metrics
                ORDER BY account_id, evaluation_date DESC
            ) hm ON p.account_id = hm.account_id
            WHERE (
                hm.account_id IS NULL OR
                a.last_activity_at > hm.evaluation_date OR
                (NOW() - hm.evaluation_date) > INTERVAL '{self.config['evaluation_interval_days']} days'
            )
            AND ({where_clause})
            ORDER BY a.id DESC
            LIMIT {self.config['max_evaluations']}
            """
        else:
            query = f"""
            SELECT {select_clause}
            FROM {self.config['db_schema']}.agents a
            JOIN {self.config['db_schema']}.participants p ON a.participant_id = p.id
            WHERE {where_clause}
            ORDER BY a.id DESC
            LIMIT {self.config['max_evaluations']}
            """
        
        try:
            accounts = self.db.execute_query(query, fetch_all=True)
            logging.info(f"Found {len(accounts) if accounts else 0} accounts using reciprocity criteria")
            
            if not accounts or len(accounts) == 0:
                logging.info("No accounts match standard criteria. Using UBEC balance criteria instead.")

                inclusive_select_parts = [
                    "a.id AS agent_id",
                    "COALESCE(a.agent_id, p.account_id) AS public_key",
                    "p.account_id"
                ]
                
                if 'last_activity_at' in available_column_names:
                    inclusive_select_parts.append("EXTRACT(EPOCH FROM a.last_activity_at) AS last_activity_timestamp")
                else:
                    inclusive_select_parts.append("EXTRACT(EPOCH FROM NOW()) AS last_activity_timestamp")
                
                inclusive_select_parts.extend([
                    "COALESCE(a.reciprocity_score, 0) as reciprocity_score",
                    "0 as reciprocity_credits",
                    "'regular' as role",
                    "COALESCE(a.loyalty_tier, 'basic') as tier",
                    "COALESCE(p.created_at, NOW()) as joined_at"
                ])
                
                inclusive_select = ", ".join(inclusive_select_parts)
                
                inclusive_query = f"""
                SELECT {inclusive_select}
                FROM {self.config['db_schema']}.agents a
                JOIN {self.config['db_schema']}.participants p ON a.participant_id = p.id
                JOIN {self.config['db_schema']}.asset_holders ah ON p.account_id = ah.account_id
                WHERE ah.asset_code = '{self.config['ubec_code']}'
                  AND ah.asset_issuer = '{self.config['ubec_issuer']}'
                  AND ah.balance > 0
                ORDER BY ah.balance DESC
                LIMIT {self.config['max_evaluations']}
                """

                accounts = self.db.execute_query(inclusive_query, fetch_all=True)
                logging.info(f"Found {len(accounts) if accounts else 0} accounts using UBEC balance criteria")
                
                # If still no accounts, add core accounts directly
                if not accounts or len(accounts) == 0:
                    logging.warning("No accounts found from database queries. Adding core accounts manually.")
                    
                    accounts = []
                    
                    # Add administration account
                    if 'administration' in self.accounts:
                        accounts.append({
                            'agent_id': 1,
                            'public_key': self.accounts['administration'],
                            'account_id': self.accounts['administration'],
                            'last_activity_timestamp': int(datetime.now().timestamp()),
                            'reciprocity_score': 0.5,
                            'reciprocity_credits': 100,
                            'role': 'administration',
                            'tier': 'core',
                            'joined_at': datetime.now() - timedelta(days=365)
                        })
                    
                    # Add general account
                    if 'general' in self.accounts:
                        accounts.append({
                            'agent_id': 2,
                            'public_key': self.accounts['general'],
                            'account_id': self.accounts['general'],
                            'last_activity_timestamp': int(datetime.now().timestamp()),
                            'reciprocity_score': 0.5,
                            'reciprocity_credits': 100,
                            'role': 'general',
                            'tier': 'core',
                            'joined_at': datetime.now() - timedelta(days=365)
                        })
                    
                    # Add stewardship accounts
                    if 'stewardship' in self.accounts:
                        for i, account in enumerate(self.accounts['stewardship']):
                            accounts.append({
                                'agent_id': 3 + i,
                                'public_key': account,
                                'account_id': account,
                                'last_activity_timestamp': int(datetime.now().timestamp()),
                                'reciprocity_score': 0.5,
                                'reciprocity_credits': 100,
                                'role': 'stewardship',
                                'tier': 'core',
                                'joined_at': datetime.now() - timedelta(days=365)
                            })
                    
                    logging.info(f"Added {len(accounts)} core accounts manually")
            
            return accounts
        except Exception as e:
            logging.error(f"Error fetching accounts for evaluation: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return []
    
    def collect_accounts_data(self):
        """
        Collect comprehensive data for UBEC account holders using the database.
        
        Returns:
            dict: Data for all account holders
        """
        logging.info("Collecting comprehensive data for UBEC account holders from database")
        
        accounts = self.get_accounts_for_evaluation()
        
        if not accounts or len(accounts) == 0:
            logging.warning("No accounts found for data collection")
            return {}
        
        holders_data = {}
        
        for i, account in enumerate(accounts):
            agent_id = account['agent_id']
            public_key = account['public_key']
            
            logging.info(f"Processing account {i+1}/{len(accounts)}: {public_key}")
            
            # Initialize metrics dictionary
            metrics = {
                'autonomy_integration': {
                    'score': 0,
                    'holding_period': 0,
                    'transaction_frequency': 0,
                    'balance_stability': 0,
                    'network_integration': 0
                },
                'multi_scale_participation': {
                    'score': 0,
                    'local_participation': 0,
                    'regional_participation': 0,
                    'global_participation': 0,
                    'participation_diversity': 0
                },
                'regenerative_impact': {
                    'score': 0,
                    'impact_projects': 0,
                    'impact_percentage': 0,
                    'impact_transaction_count': 0,
                    'certification_score': 0
                },
                'network_contribution': {
                    'score': 0,
                    'connector_score': 0,
                    'transaction_activity': 0,
                    'liquidity_provision': 0,
                    'governance_participation': 0
                },
                'ubuntu_alignment': {
                    'score': 0,
                    'reciprocity_score': 0,
                    'community_support_score': 0,
                    'principles_alignment': 0
                }
            }
            
            # Get transaction history
            transactions = self.get_agent_transactions(agent_id, public_key)
            
            # Get activities (with safe fallback)
            activities = self.get_agent_activities(agent_id)
            
            # Get contributions (with safe fallback)
            contributions = self.get_agent_contributions(agent_id)
            
            # Get benefits (with safe fallback)
            benefits = self.get_agent_benefits(agent_id)
            
            # Get holons (with safe fallback)
            holons = self.get_agent_holons(agent_id)
            
            # Get projects (with safe fallback)
            projects = self.get_regenerative_projects(agent_id)
            
            # Get asset balance
            balance = self.get_agent_balance(public_key)
            
            # Get account metadata
            metadata = self.get_account_metadata(account)
            
            # Determine account type
            if public_key == self.accounts.get('general'):
                account_type = 'general'
            elif public_key == self.accounts.get('administration'):
                account_type = 'administration'
            elif public_key in self.accounts.get('stewardship', []):
                account_type = 'stewardship'
            else:
                account_type = 'regular'
            
            holders_data[agent_id] = {
                'public_key': public_key,
                'account_id': account['account_id'],
                'balance': Decimal(balance) if balance else Decimal('0'),
                'transactions': transactions or [],
                'activities': activities or {},
                'contributions': contributions or [],
                'benefits': benefits or [],
                'holons': holons or [],
                'projects': projects or [],
                'role': account['role'] or 'regular',
                'tier': account['tier'] or 'basic',
                'account_type': account_type,
                'joined_at': account.get('joined_at', datetime.now().timestamp()),
                'reciprocity_score': account['reciprocity_score'] if account['reciprocity_score'] is not None else 0,
                'metadata': metadata or {},
                'metrics': metrics
            }
            
        self.holders_data = holders_data
        logging.info(f"Collected data for {len(holders_data)} UBEC account holders")
        
        core_count = sum(1 for data in holders_data.values() if data['account_type'] in ['general', 'administration', 'stewardship'])
        tx_count = sum(len(data.get('transactions', [])) for data in holders_data.values())
        
        logging.info(f"Data summary: {len(holders_data)} total accounts, {core_count} core accounts, {tx_count} total transactions")
        
        return holders_data
    
    def get_agent_transactions(self, agent_id, public_key=None):
        """
        Retrieve transaction data for a specific agent from the database.
        
        UPDATED: October 11, 2025
        - Uses stellar_operations table directly (NEW standard)
        - No backward compatibility layers
        - Enhanced error handling and logging
        
        Args:
            agent_id: Database ID of the agent
            public_key: Stellar public key (required for fetching transactions)
            
        Returns:
            List of transactions
        """
        if not public_key:
            logging.warning(f"No public_key provided for agent {agent_id}, cannot fetch transactions")
            return []
        
        # Use stellar_operations table directly (NEW standard)
        query = f"""
        SELECT 
            transaction_id as id,
            operation_type as transaction_type,
            amount,
            created_at as timestamp,
            from_account as source_account,
            to_account as destination,
            asset_code,
            asset_issuer
        FROM {self.config['db_schema']}.stellar_operations
        WHERE (from_account = %s OR to_account = %s)
          AND asset_code = %s
          AND asset_issuer = %s
        ORDER BY created_at DESC
        LIMIT 1000
        """
        
        try:
            logging.debug(f"Querying transactions for {public_key[:10]}...")
            
            transactions = self.db.execute_query(
                query, 
                [public_key, public_key, self.config['ubec_code'], self.config['ubec_issuer']], 
                fetch_all=True
            )
            
            if not transactions or len(transactions) == 0:
                logging.debug(f"No transactions found for {public_key}")
                return []
            
            # Format transactions
            formatted_transactions = []
            for tx in transactions:
                # Convert timestamp if needed
                timestamp = tx.get('timestamp')
                if isinstance(timestamp, datetime):
                    timestamp = int(timestamp.timestamp())
                elif timestamp is None:
                    timestamp = int(datetime.now().timestamp())
                
                formatted_tx = {
                    'id': tx.get('id', ''),
                    'transaction_type': 'CREDIT' if tx.get('destination') == public_key else 'DEBIT',
                    'amount': float(tx.get('amount', 0)),
                    'balance_after': 0,  # Calculated separately if needed
                    'timestamp': timestamp,
                    'source_account': tx.get('source_account'),
                    'destination': tx.get('destination'),
                    'details': {
                        'asset_code': tx.get('asset_code'),
                        'asset_issuer': tx.get('asset_issuer'),
                        'operation_type': tx.get('transaction_type', 'payment')
                    }
                }
                formatted_transactions.append(formatted_tx)
            
            logging.debug(f"✅ Found {len(formatted_transactions)} transactions for {public_key[:10]}...")
            return formatted_transactions
            
        except Exception as e:
            logging.error(f"❌ Error fetching transactions for agent {agent_id} ({public_key[:10]}...): {e}")
            logging.debug(f"Query that failed: {query[:200]}...")
            return []
    
    def get_agent_activities(self, agent_id):
        """
        Retrieve activity history for a specific agent from the database.
        
        Args:
            agent_id: Database ID of the agent
            
        Returns:
            Dict of activities by type
        """
        # Check if table exists
        try:
            check_query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = '{self.config['db_schema']}'
                AND table_name = 'agent_activity_history'
            );
            """
            result = self.db.execute_query(check_query, fetch_one=True)
            
            if not result or not result.get('exists', False):
                logging.debug(f"Table agent_activity_history does not exist, skipping activities for agent {agent_id}")
                return {}
        except Exception as e:
            logging.debug(f"Could not check for agent_activity_history table: {e}")
            return {}
        
        query = f"""
        SELECT activity_type, score_impact, timestamp, details
        FROM {self.config['db_schema']}.agent_activity_history
        WHERE agent_id = %s
        ORDER BY timestamp DESC
        """
        
        try:
            activities = self.db.execute_query(query, [agent_id], fetch_all=True)
            
            if not activities:
                return {}
            
            # Group by activity type
            activity_types = {}
            for activity in activities:
                activity_type = activity['activity_type']
                if activity_type not in activity_types:
                    activity_types[activity_type] = []
                activity_types[activity_type].append(activity)
            
            return activity_types
        except Exception as e:
            logging.debug(f"Error fetching activities for agent {agent_id}: {e}")
            return {}
    
    def get_agent_contributions(self, agent_id):
        """
        Retrieve contribution history for a specific agent from the database.
        
        Args:
            agent_id: Database ID of the agent
            
        Returns:
            List of contributions
        """
        # Check if table exists
        try:
            check_query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = '{self.config['db_schema']}'
                AND table_name = 'agent_contribution_history'
            );
            """
            result = self.db.execute_query(check_query, fetch_one=True)
            
            if not result or not result.get('exists', False):
                logging.debug(f"Table agent_contribution_history does not exist")
                return []
        except Exception as e:
            logging.debug(f"Could not check for agent_contribution_history table: {e}")
            return []
        
        query = f"""
        SELECT contribution_type, amount, timestamp, details
        FROM {self.config['db_schema']}.agent_contribution_history
        WHERE agent_id = %s
        ORDER BY timestamp DESC
        """
        
        try:
            contributions = self.db.execute_query(query, [agent_id], fetch_all=True)
            return contributions or []
        except Exception as e:
            logging.debug(f"Error fetching contributions for agent {agent_id}: {e}")
            return []
    
    def get_agent_benefits(self, agent_id):
        """
        Retrieve benefit history for a specific agent from the database.
        
        Args:
            agent_id: Database ID of the agent
            
        Returns:
            List of benefits
        """
        # Check if table exists
        try:
            check_query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = '{self.config['db_schema']}'
                AND table_name = 'agent_benefit_history'
            );
            """
            result = self.db.execute_query(check_query, fetch_one=True)
            
            if not result or not result.get('exists', False):
                logging.debug(f"Table agent_benefit_history does not exist")
                return []
        except Exception as e:
            logging.debug(f"Could not check for agent_benefit_history table: {e}")
            return []
        
        query = f"""
        SELECT benefit_type, amount, timestamp, details
        FROM {self.config['db_schema']}.agent_benefit_history
        WHERE agent_id = %s
        ORDER BY timestamp DESC
        """
        
        try:
            benefits = self.db.execute_query(query, [agent_id], fetch_all=True)
            return benefits or []
        except Exception as e:
            logging.debug(f"Error fetching benefits for agent {agent_id}: {e}")
            return []
    
    def get_agent_holons(self, agent_id):
        """
        Retrieve holon memberships for a specific agent from the database.
        
        Args:
            agent_id: Database ID of the agent
            
        Returns:
            List of holon memberships
        """
        # Check if tables exist
        try:
            check_query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = '{self.config['db_schema']}'
                AND table_name = 'agent_holon_memberships'
            );
            """
            result = self.db.execute_query(check_query, fetch_one=True)
            
            if not result or not result.get('exists', False):
                logging.debug(f"Table agent_holon_memberships does not exist")
                return []
        except Exception as e:
            logging.debug(f"Could not check for agent_holon_memberships table: {e}")
            return []
        
        query = f"""
        SELECT h.holon_id, h.holon_name, h.holon_type, h.description,
               ahm.role_in_holon, ahm.contribution_score, ahm.joined_at
        FROM {self.config['db_schema']}.agent_holon_memberships ahm
        JOIN {self.config['db_schema']}.holons h ON ahm.holon_id = h.id
        WHERE ahm.agent_id = %s AND ahm.status = 'active'
        """
        
        try:
            holons = self.db.execute_query(query, [agent_id], fetch_all=True)
            return holons or []
        except Exception as e:
            logging.debug(f"Error fetching holons for agent {agent_id}: {e}")
            return []
    
    def get_regenerative_projects(self, agent_id):
        """
        Retrieve regenerative projects for a specific agent from the database.
        
        Args:
            agent_id: Database ID of the agent
            
        Returns:
            List of regenerative projects
        """
        # Check if table exists
        try:
            check_query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = '{self.config['db_schema']}'
                AND table_name = 'regenerative_projects'
            );
            """
            result = self.db.execute_query(check_query, fetch_one=True)
            
            if not result or not result.get('exists', False):
                logging.debug(f"Table regenerative_projects does not exist")
                return []
        except Exception as e:
            logging.debug(f"Could not check for regenerative_projects table: {e}")
            return []
        
        query = f"""
        SELECT project_name, description, project_type, verification_status,
               verification_date, impact_metrics
        FROM {self.config['db_schema']}.regenerative_projects
        WHERE agent_id = %s
        """
        
        try:
            projects = self.db.execute_query(query, [agent_id], fetch_all=True)
            return projects or []
        except Exception as e:
            logging.debug(f"Error fetching regenerative projects for agent {agent_id}: {e}")
            return []
    
    def get_agent_balance(self, public_key):
        """
        Get the UBEC token balance for an agent.
        
        Args:
            public_key: Stellar public key of the agent
            
        Returns:
            Decimal: Token balance
        """
        query = f"""
        SELECT balance
        FROM {self.config['db_schema']}.asset_holders
        WHERE account_id = %s AND asset_code = %s AND asset_issuer = %s
        """
        
        try:
            result = self.db.execute_query(query, [public_key, self.config['ubec_code'], self.config['ubec_issuer']], fetch_one=True)
            
            if result and result['balance'] is not None:
                return result['balance']
            
            # For core accounts not in database, use placeholder balances
            if (public_key == self.accounts.get('general') or 
                public_key == self.accounts.get('administration') or
                public_key in self.accounts.get('stewardship', [])):
                logging.warning(f"Core account {public_key} not found in asset_holders. Using placeholder balance.")
                
                if public_key == self.accounts.get('general'):
                    return 5000000
                elif public_key == self.accounts.get('administration'):
                    return 1000000
                else:
                    try:
                        idx = self.accounts.get('stewardship', []).index(public_key)
                        balances = [2000000, 1500000, 1200000]
                        return balances[idx] if idx < len(balances) else 1000000
                    except ValueError:
                        return 1000000
            
            return 0
        except Exception as e:
            logging.error(f"Error fetching balance for agent {public_key}: {e}")
            return 0
    
    def get_account_metadata(self, account):
        """
        Get metadata for a specific account from the database.
        
        Args:
            account: Account record
            
        Returns:
            dict: Metadata for the account
        """
        metadata = {
            'name': None,
            'type': None,
            'location': None,
            'tags': [],
            'profile': None,
            'eco_certifications': [],
            'projects': []
        }
        
        try:
            metadata['name'] = account.get('account_id')
            metadata['type'] = account.get('role', 'regular')
            
            # Check if account has metadata in the database
            query = f"""
            SELECT metadata
            FROM {self.config['db_schema']}.participants
            WHERE account_id = %s
            """
            
            result = self.db.execute_query(query, [account.get('public_key')], fetch_one=True)
            
            if result and result['metadata']:
                db_metadata = result['metadata']
                
                if isinstance(db_metadata, str):
                    try:
                        db_metadata = json.loads(db_metadata)
                    except:
                        db_metadata = {}
                
                if isinstance(db_metadata, dict):
                    for key in ['name', 'type', 'location', 'tags', 'profile', 'eco_certifications', 'projects']:
                        if key in db_metadata and db_metadata[key]:
                            metadata[key] = db_metadata[key]
            
            # Add role and tier to tags
            if account.get('role') and account.get('role') not in metadata['tags']:
                metadata['tags'].append(account.get('role'))
            
            if account.get('tier') and account.get('tier') not in metadata['tags']:
                metadata['tags'].append(account.get('tier').lower())
            
            # For core accounts, ensure appropriate tags
            public_key = account.get('public_key')
            
            if public_key == self.accounts.get('general'):
                metadata['tags'].extend(['core', 'general'])
                metadata['type'] = 'core'
                metadata['name'] = 'General Distribution'
                
            elif public_key == self.accounts.get('administration'):
                metadata['tags'].extend(['core', 'administration'])
                metadata['type'] = 'core'
                metadata['name'] = 'Administration'
                
            elif public_key in self.accounts.get('stewardship', []):
                metadata['tags'].extend(['core', 'stewardship'])
                metadata['type'] = 'core'
                
                if len(self.accounts.get('stewardship', [])) >= 3:
                    idx = self.accounts.get('stewardship', []).index(public_key)
                    if idx == 0:
                        metadata['tags'].append('management')
                        metadata['name'] = 'Stewardship Management'
                    elif idx == 1:
                        metadata['tags'].append('infrastructure')
                        metadata['name'] = 'Stewardship Infrastructure'
                    elif idx == 2:
                        metadata['tags'].append('liquidity')
                        metadata['name'] = 'Stewardship Liquidity'
            
            metadata['tags'] = list(set(metadata['tags']))
            
        except Exception as e:
            logging.warning(f"Error getting metadata for account {account.get('public_key')}: {e}")
        
        return metadata
    
    def build_transaction_network(self):
        """
        Build a transaction network from the collected account data.
        
        Returns:
            networkx.DiGraph: Transaction network
        """
        logging.info("Building UBEC transaction network from database")
        
        G = nx.DiGraph()
        
        if not self.holders_data:
            logging.warning("No holder data available for network building")
            return G
        
        # Add accounts as nodes
        for agent_id, data in self.holders_data.items():
            G.add_node(agent_id, 
                       public_key=data['public_key'],
                       balance=float(data['balance']), 
                       transaction_count=len(data.get('transactions', [])),
                       reciprocity_score=float(data['reciprocity_score']))
            
            for key, value in data.get('metadata', {}).items():
                if value:
                    G.nodes[agent_id][key] = value
        
        logging.debug(f"Added {len(G.nodes())} nodes to transaction network")
        
        # Map of public keys to agent IDs
        pk_to_aid = {data['public_key']: aid for aid, data in self.holders_data.items()}
        
        # Add transactions as edges
        for agent_id, data in self.holders_data.items():
            for tx in data.get('transactions', []):
                if not tx.get('source_account') or not tx.get('destination'):
                    continue
                
                source = tx.get('source_account')
                destination = tx.get('destination')
                
                try:
                    amount = float(tx.get('amount', 0))
                    if amount <= 0:
                        continue
                except (ValueError, TypeError):
                    continue
                
                if source and destination:
                    source_agent_id = pk_to_aid.get(source)
                    dest_agent_id = pk_to_aid.get(destination)
                    
                    if source_agent_id and dest_agent_id:
                        if G.has_edge(source_agent_id, dest_agent_id):
                            G[source_agent_id][dest_agent_id]['weight'] += amount
                            G[source_agent_id][dest_agent_id]['count'] += 1
                        else:
                            G.add_edge(source_agent_id, dest_agent_id, weight=amount, count=1)
        
        self.transaction_network = G
        logging.info(f"Built transaction network with {len(G.nodes())} nodes and {len(G.edges())} edges")
        
        # Add placeholder connections for empty networks
        if len(G.edges()) < 3:
            logging.warning("Transaction network has very few edges, adding placeholder connections for core accounts")
            
            core_ids = []
            for agent_id, data in self.holders_data.items():
                if data.get('account_type') in ['general', 'administration', 'stewardship']:
                    core_ids.append(agent_id)
            
            if len(core_ids) >= 2:
                for i in range(len(core_ids)):
                    for j in range(i+1, len(core_ids)):
                        if not G.has_edge(core_ids[i], core_ids[j]):
                            G.add_edge(core_ids[i], core_ids[j], weight=1000, count=10)
                        if not G.has_edge(core_ids[j], core_ids[i]):
                            G.add_edge(core_ids[j], core_ids[i], weight=1000, count=10)
            
            logging.info(f"Added placeholder connections, network now has {len(G.edges())} edges")
        
        return G
    
    # ... [Continue with all the calculation methods - they remain unchanged] ...
    # calculate_autonomy_integration_metrics()
    # calculate_multi_scale_participation_metrics()
    # calculate_regenerative_impact_metrics()
    # calculate_network_contribution_metrics()
    # calculate_ubuntu_alignment_metrics()
    # calculate_holonic_scores()
    
    # [Note: Including all those methods would make this file too long, so I'm indicating where they go]
    # The calculation methods remain the same as in your original file
    
    def store_evaluation_results(self):
        """
        Store evaluation results in the database.
        
        UPDATED FOR V8 MIGRATION:
        - Uses account_id (Stellar address) instead of agent_id (database ID)
        - Uses extract_date_immutable() function in ON CONFLICT clause
        """
        logging.info("Storing holonic evaluation results in database")

        if not self.holonic_table_exists:
            logging.warning("holonic_metrics table does not exist. Skipping storage. Please run create_holonic_tables.sql")
            return 0

        stored_count = 0
        error_count = 0

        for agent_id, data in self.holders_data.items():
            try:
                if 'holonic_score' not in data or 'holonic_category' not in data:
                    logging.warning(f"Skipping storage for agent {agent_id}: missing holonic score or category")
                    continue

                metrics = data.get('metrics', {})
                
                # Final validation
                for metric_name in ['autonomy_integration', 'multi_scale_participation', 
                                   'regenerative_impact', 'network_contribution', 
                                   'ubuntu_alignment']:
                    if metric_name not in metrics:
                        metrics[metric_name] = {'score': 0}
                    elif not isinstance(metrics[metric_name], dict):
                        metrics[metric_name] = {'score': 0}
                    elif 'score' not in metrics[metric_name]:
                        metrics[metric_name]['score'] = 0

                # UPDATED: Now uses account_id instead of agent_id
                # The unique index is: idx_holonic_metrics_account_date_unique
                # ON holonic_metrics (account_id, extract_date_immutable(evaluation_date))
                query = f"""
                INSERT INTO {self.config['db_schema']}.holonic_metrics (
                    account_id,
                    evaluation_date,
                    autonomy_integration_score,
                    multi_scale_score,
                    regenerative_impact_score,
                    network_contribution_score,
                    ubuntu_alignment_score,
                    composite_score,
                    holonic_category,
                    raw_metrics
                ) VALUES (
                    %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (account_id, {self.config['db_schema']}.extract_date_immutable(evaluation_date))
                DO UPDATE SET
                    autonomy_integration_score = EXCLUDED.autonomy_integration_score,
                    multi_scale_score = EXCLUDED.multi_scale_score,
                    regenerative_impact_score = EXCLUDED.regenerative_impact_score,
                    network_contribution_score = EXCLUDED.network_contribution_score,
                    ubuntu_alignment_score = EXCLUDED.ubuntu_alignment_score,
                    composite_score = EXCLUDED.composite_score,
                    holonic_category = EXCLUDED.holonic_category,
                    raw_metrics = EXCLUDED.raw_metrics,
                    updated_at = NOW()
                """

                # UPDATED: Now passes account_id (Stellar address) instead of agent_id (database ID)
                params = [
                    data['account_id'],  # Stellar public key (e.g., 'GABC...')
                    metrics.get('autonomy_integration', {}).get('score', 0),
                    metrics.get('multi_scale_participation', {}).get('score', 0),
                    metrics.get('regenerative_impact', {}).get('score', 0),
                    metrics.get('network_contribution', {}).get('score', 0),
                    metrics.get('ubuntu_alignment', {}).get('score', 0),
                    data['holonic_score'],
                    data['holonic_category'],
                    json.dumps({
                        'autonomy_integration': metrics.get('autonomy_integration', {}),
                        'multi_scale_participation': metrics.get('multi_scale_participation', {}),
                        'regenerative_impact': metrics.get('regenerative_impact', {}),
                        'network_contribution': metrics.get('network_contribution', {}),
                        'ubuntu_alignment': metrics.get('ubuntu_alignment', {})
                    })
                ]

                self.db.execute_query(query, params)
                stored_count += 1

                if stored_count % 50 == 0:
                    logging.info(f"Stored {stored_count} evaluation results so far")

            except Exception as e:
                error_count += 1
                logging.error(f"Error storing evaluation result for agent {agent_id}: {e}")
                import traceback
                logging.error(traceback.format_exc())

        logging.info(f"Stored {stored_count} evaluation results in database ({error_count} errors)")
        return stored_count
    
    # ... [Continue with remaining methods] ...
    # generate_recommendations()
    # run_evaluation()


# [NOTE: Due to character limits, I'm showing the key updated sections]
# The full file would include all calculation methods unchanged from your original
# The critical updates are:
# 1. _validate_database_schema() - NEW method
# 2. get_agent_transactions() - UPDATED with better error handling and documentation
# 3. store_evaluation_results() - Already V8 compliant in your version
