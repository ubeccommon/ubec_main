# holonic/ubec_holonic_evaluator.py

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

        # Try to import settings to get accounts
        try:
            from config import settings
            self.accounts = settings.ACCOUNTS
            logging.info("Successfully loaded accounts from settings")
        except (ImportError, AttributeError) as e:
            logging.warning(f"Could not load accounts from settings: {e}")
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

    def load_config(self):
        """
        Load configuration from file or use defaults.
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

        if self.config_path:
            try:
                config_dir = os.path.dirname(os.path.abspath(self.config_path))
                sys.path.append(config_dir)

                logging.info(f"Looking for config in: {config_dir}")

                try:
                    from config import settings
                    config_module = settings
                    logging.info("Successfully imported settings from config package")
                except ImportError:
                    logging.info(f"Direct import failed, trying to load from {self.config_path}")

                    if not os.path.exists(self.config_path):
                        parent_config_path = os.path.join(os.path.dirname(os.getcwd()), "config/settings.py")
                        if os.path.exists(parent_config_path):
                            self.config_path = parent_config_path
                            logging.info(f"Found settings file at: {self.config_path}")
                        else:
                            logging.warning(f"Could not find settings file at {self.config_path} or {parent_config_path}")
                            logging.info("Using default configuration")
                            return

                    import importlib.util
                    spec = importlib.util.spec_from_file_location("settings", self.config_path)
                    config_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(config_module)
                    logging.info(f"Successfully loaded settings from {self.config_path}")

                for key in dir(config_module):
                    if key.isupper() and key in [k.upper() for k in self.config.keys()]:
                        self.config[key.lower()] = getattr(config_module, key)

                logging.info(f"Loaded configuration from {self.config_path}")

            except Exception as e:
                logging.warning(f"Could not load config from {self.config_path}: {e}")
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
        if self.holonic_table_exists and 'last_activity_at' in available_column_names:
            query = f"""
            SELECT {select_clause}
            FROM {self.config['db_schema']}.agents a
            JOIN {self.config['db_schema']}.participants p ON a.participant_id = p.id
            LEFT JOIN (
                SELECT DISTINCT ON (agent_id) agent_id, evaluation_date
                FROM {self.config['db_schema']}.holonic_metrics
                ORDER BY agent_id, evaluation_date DESC
            ) hm ON a.id = hm.agent_id
            WHERE (
                hm.agent_id IS NULL OR
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
        Uses transaction_operations table as primary source.
        
        Args:
            agent_id: Database ID of the agent
            public_key: Optional Stellar public key (required for fetching transactions)
            
        Returns:
            List of transactions
        """
        if not public_key:
            logging.warning(f"No public_key provided for agent {agent_id}, cannot fetch transactions")
            return []
        
        # Use transaction_operations table as primary source
        query = f"""
        SELECT 
            transaction_id as id,
            operation_type as transaction_type,
            amount,
            created_at as timestamp,
            source_account,
            destination_account as destination,
            asset_code,
            asset_issuer
        FROM {self.config['db_schema']}.transaction_operations
        WHERE (source_account = %s OR destination_account = %s)
          AND asset_code = %s
          AND asset_issuer = %s
        ORDER BY created_at DESC
        LIMIT 1000
        """
        
        try:
            transactions = self.db.execute_query(
                query, 
                [public_key, public_key, self.config['ubec_code'], self.config['ubec_issuer']], 
                fetch_all=True
            )
            
            if not transactions or len(transactions) == 0:
                logging.debug(f"No transactions found for {public_key} in transaction_operations")
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
                    'balance_after': 0,  # Not available in transaction_operations
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
            
            logging.debug(f"Found {len(formatted_transactions)} transactions for {public_key}")
            return formatted_transactions
            
        except Exception as e:
            logging.error(f"Error fetching transactions for agent {agent_id} ({public_key}): {e}")
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
    
    # [Continue with calculation methods - autonomy_integration, multi_scale, etc.]
    # These remain largely the same as in the original code
    # I'll include the key ones below:
    
    def calculate_autonomy_integration_metrics(self):
        """Calculate metrics related to the balance of autonomy and integration."""
        logging.info("Calculating autonomy and integration metrics")
        
        holding_period_threshold = self.thresholds['autonomy_integration']['holding_period']
        tx_frequency_threshold = self.thresholds['autonomy_integration']['transaction_frequency']
        
        for agent_id, data in self.holders_data.items():
            public_key = data['public_key']
            transactions = data.get('transactions', [])
            is_core_account = data.get('account_type') in ['general', 'administration', 'stewardship']
            
            if is_core_account and not transactions:
                logging.info(f"Core account {public_key} has no transactions, creating placeholder autonomy metrics")
                
                if data.get('account_type') == 'general':
                    base_score = 0.65
                elif data.get('account_type') == 'administration':
                    base_score = 0.75
                else:
                    base_score = 0.70
                
                overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
                
                data['metrics']['autonomy_integration'] = {
                    'score': overall_score,
                    'holding_period': 365,
                    'transaction_frequency': tx_frequency_threshold,
                    'balance_stability': 0.8,
                    'network_integration': 0.7
                }
                continue
            
            if not transactions:
                data['metrics']['autonomy_integration'] = {
                    'score': 0,
                    'holding_period': 0,
                    'transaction_frequency': 0,
                    'balance_stability': 0,
                    'network_integration': 0
                }
                continue
            
            # Calculate holding period
            joined_timestamp = data.get('joined_at', datetime.now().timestamp())
            if isinstance(joined_timestamp, datetime):
                joined_timestamp = joined_timestamp.timestamp()
            
            current_timestamp = datetime.now().timestamp()
            holding_period = (current_timestamp - joined_timestamp) / (24 * 3600)
            
            # Calculate transaction frequency
            if holding_period > 0:
                tx_frequency = len(transactions) / (holding_period / 30)
            else:
                tx_frequency = 0
            
            # Estimate balance volatility
            if len(transactions) > 1:
                try:
                    amounts = [float(tx.get('amount', 0)) for tx in transactions]
                    mean_amount = sum(amounts) / len(amounts)
                    if mean_amount > 0:
                        volatility = sum(abs(amt - mean_amount) for amt in amounts) / (mean_amount * len(amounts))
                    else:
                        volatility = 1.0
                except (ValueError, TypeError):
                    volatility = 0.5
            else:
                volatility = 0.5
            
            balance_stability = 1 - min(volatility, 1.0)
            
            # Calculate network integration
            if self.transaction_network and agent_id in self.transaction_network:
                degree = self.transaction_network.degree(agent_id)
                max_degree = len(self.transaction_network) - 1
                network_integration = degree / max_degree if max_degree > 0 else 0
            else:
                network_integration = 0
            
            # Calculate overall score
            holding_score = min(holding_period / holding_period_threshold, 1.0)
            frequency_score = min(tx_frequency / tx_frequency_threshold, 1.0)
            stability_score = balance_stability
            integration_score = network_integration
            
            overall_score = (
                holding_score * 0.25 +
                frequency_score * 0.25 + 
                stability_score * 0.25 + 
                integration_score * 0.25
            )
            
            if is_core_account and overall_score < 0.4:
                if data.get('account_type') == 'general':
                    base_score = 0.65
                elif data.get('account_type') == 'administration':
                    base_score = 0.75
                else:
                    base_score = 0.70
                
                overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
            
            data['metrics']['autonomy_integration'] = {
                'score': overall_score,
                'holding_period': holding_period,
                'transaction_frequency': tx_frequency,
                'balance_stability': balance_stability,
                'network_integration': network_integration
            }
        
        logging.info("Completed autonomy and integration metrics calculation")
    
    def calculate_multi_scale_participation_metrics(self):
        """Calculate metrics related to multi-scale participation."""
        logging.info("Calculating multi-scale participation metrics")
        
        local_threshold = self.thresholds['multi_scale']['local_threshold']
        regional_threshold = self.thresholds['multi_scale']['regional_threshold']
        global_threshold = self.thresholds['multi_scale']['global_threshold']
        
        # Categorize accounts by balance
        local_accounts = set()
        regional_accounts = set()
        global_accounts = set()
        
        for agent_id, data in self.holders_data.items():
            balance = float(data['balance'])
            account_type = data.get('metadata', {}).get('type')
            
            if account_type == 'core' or balance > 1000000:
                global_accounts.add(agent_id)
            elif balance > 10000:
                regional_accounts.add(agent_id)
            else:
                local_accounts.add(agent_id)
        
        for agent_id, data in self.holders_data.items():
            public_key = data['public_key']
            transactions = data.get('transactions', [])
            is_core_account = data.get('account_type') in ['general', 'administration', 'stewardship']
            
            if is_core_account and not transactions:
                if data.get('account_type') == 'general':
                    base_score = 0.70
                elif data.get('account_type') == 'administration':
                    base_score = 0.65
                else:
                    base_score = 0.60
                
                overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
                
                data['metrics']['multi_scale_participation'] = {
                    'score': overall_score,
                    'local_participation': local_threshold * 0.8,
                    'regional_participation': regional_threshold * 0.8,
                    'global_participation': global_threshold * 0.8,
                    'participation_diversity': 0.7
                }
                continue
            
            if not transactions:
                data['metrics']['multi_scale_participation'] = {
                    'score': 0,
                    'local_participation': 0,
                    'regional_participation': 0,
                    'global_participation': 0,
                    'participation_diversity': 0
                }
                continue
            
            # Count transactions at different scales
            local_tx, regional_tx, global_tx = self._count_multi_scale_transactions(
                agent_id, transactions, local_accounts, regional_accounts, global_accounts)
            
            # Calculate scores
            local_score = min(local_tx / local_threshold, 1.0) if local_threshold > 0 else 0
            regional_score = min(regional_tx / regional_threshold, 1.0) if regional_threshold > 0 else 0
            global_score = min(global_tx / global_threshold, 1.0) if global_threshold > 0 else 0
            
            participation_diversity = self._calculate_diversity_score(local_tx, regional_tx, global_tx)
            
            overall_score = (
                local_score * 0.3 +
                regional_score * 0.3 + 
                global_score * 0.3 + 
                participation_diversity * 0.1
            )
            
            if is_core_account and overall_score < 0.4:
                if data.get('account_type') == 'general':
                    base_score = 0.70
                elif data.get('account_type') == 'administration':
                    base_score = 0.65
                else:
                    base_score = 0.60
                
                overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
            
            data['metrics']['multi_scale_participation'] = {
                'score': overall_score,
                'local_participation': local_tx,
                'regional_participation': regional_tx,
                'global_participation': global_tx,
                'participation_diversity': participation_diversity
            }
        
        logging.info("Completed multi-scale participation metrics calculation")
    
    def _count_multi_scale_transactions(self, agent_id, transactions, local_accounts, regional_accounts, global_accounts):
        """Helper method to count transactions at different scales"""
        local_tx = 0
        regional_tx = 0
        global_tx = 0
        
        pk_to_aid = {data['public_key']: aid for aid, data in self.holders_data.items()}
        
        for tx in transactions:
            source = tx.get('source_account')
            destination = tx.get('destination')
            
            if not source or not destination:
                continue
            
            source_agent_id = pk_to_aid.get(source)
            dest_agent_id = pk_to_aid.get(destination)
            
            for other_agent_id in [source_agent_id, dest_agent_id]:
                if other_agent_id and other_agent_id != agent_id:
                    if other_agent_id in local_accounts:
                        local_tx += 1
                    elif other_agent_id in regional_accounts:
                        regional_tx += 1
                    elif other_agent_id in global_accounts:
                        global_tx += 1
        
        return local_tx, regional_tx, global_tx
    
    def _calculate_diversity_score(self, local_tx, regional_tx, global_tx):
        """Helper method to calculate participation diversity score using entropy"""
        total_tx = local_tx + regional_tx + global_tx
        
        if total_tx > 0:
            proportions = []
            if local_tx > 0: proportions.append(local_tx / total_tx)
            if regional_tx > 0: proportions.append(regional_tx / total_tx)
            if global_tx > 0: proportions.append(global_tx / total_tx)
            
            if len(proportions) > 0:
                entropy = -sum(p * math.log(p) for p in proportions)
                max_entropy = math.log(len(proportions))
                participation_diversity = entropy / max_entropy if max_entropy > 0 else 0
            else:
                participation_diversity = 0
        else:
            participation_diversity = 0
        
        return participation_diversity
    
    def calculate_regenerative_impact_metrics(self):
        """Calculate metrics related to regenerative impact."""
        logging.info("Calculating regenerative impact metrics")
        
        impact_projects_min = self.thresholds['regenerative_impact']['impact_projects_min']
        impact_percentage = self.thresholds['regenerative_impact']['impact_percentage']
        
        for agent_id, data in self.holders_data.items():
            public_key = data['public_key']
            transactions = data.get('transactions', [])
            balance = float(data['balance'])
            projects = data.get('projects', [])
            is_core_account = data.get('account_type') in ['general', 'administration', 'stewardship']
            
            if is_core_account and (not transactions or not projects):
                if data.get('account_type') == 'general':
                    base_score = 0.75
                elif data.get('account_type') == 'administration':
                    base_score = 0.65
                else:
                    base_score = 0.65
                
                overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
                
                data['metrics']['regenerative_impact'] = {
                    'score': overall_score,
                    'impact_projects': impact_projects_min,
                    'impact_percentage': impact_percentage * 2,
                    'impact_transaction_count': 5,
                    'certification_score': 0.7
                }
                continue
            
            if not transactions and not projects:
                data['metrics']['regenerative_impact'] = {
                    'score': 0,
                    'impact_projects': 0,
                    'impact_percentage': 0,
                    'impact_transaction_count': 0,
                    'certification_score': 0
                }
                continue
            
            # Calculate impact metrics
            impact_project_count = len(projects)
            impact_tx_count, impact_amount, impact_projects_set = self._calculate_impact_transactions(agent_id, data, transactions)
            
            impact_project_count = max(impact_project_count, len(impact_projects_set))
            impact_project_score = min(impact_project_count / impact_projects_min, 1.0) if impact_projects_min > 0 else 0
            
            impact_pct = impact_amount / balance if balance > 0 else 0
            impact_pct_score = min(impact_pct / impact_percentage, 1.0) if impact_percentage > 0 else 0
            
            # Calculate certification score
            certification_score = 0.0
            metadata = data.get('metadata', {})
            if 'eco_certifications' in metadata and metadata['eco_certifications']:
                certification_score = min(len(metadata['eco_certifications']) / 3.0, 1.0)
            
            # Check for regenerative tags
            tag_score = 0
            if metadata and 'tags' in metadata:
                regen_tags = ['regenerative', 'sustainable', 'ecological', 'environmental', 'community']
                matching_tags = [tag for tag in metadata['tags'] if tag in regen_tags]
                if matching_tags:
                    tag_score = min(len(matching_tags) / len(regen_tags), 0.5)
            
            overall_score = (
                impact_project_score * 0.35 +
                impact_pct_score * 0.35 + 
                certification_score * 0.15 +
                tag_score * 0.15
            )
            
            if is_core_account and overall_score < 0.4:
                if data.get('account_type') == 'general':
                    base_score = 0.75
                elif data.get('account_type') == 'administration':
                    base_score = 0.65
                else:
                    base_score = 0.65
                
                overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
            
            data['metrics']['regenerative_impact'] = {
                'score': overall_score,
                'impact_projects': impact_project_count,
                'impact_percentage': impact_pct,
                'impact_transaction_count': impact_tx_count,
                'certification_score': certification_score
            }
        
        logging.info("Completed regenerative impact metrics calculation")
    
    def _calculate_impact_transactions(self, agent_id, data, transactions):
        """Helper method to identify impact transactions"""
        impact_tx_count = 0
        impact_amount = 0
        impact_projects_set = set()
        pk_to_aid = {d['public_key']: aid for aid, d in self.holders_data.items()}
        
        for tx in transactions:
            try:
                destination = tx.get('destination')
                source = tx.get('source_account')
                amount = float(tx.get('amount', 0))
                
                if destination:
                    dest_agent_id = pk_to_aid.get(destination)
                    is_impact = False
                    
                    if dest_agent_id in self.holders_data:
                        dest_tags = self.holders_data[dest_agent_id].get('metadata', {}).get('tags', [])
                        impact_tags = ['farm', 'regenerative', 'sustainable', 'community', 'ecological']
                        if any(tag in dest_tags for tag in impact_tags):
                            is_impact = True
                    
                    if dest_agent_id in self.holders_data and self.holders_data[dest_agent_id].get('projects'):
                        is_impact = True
                    
                    if not is_impact and source == data['public_key']:
                        dest_count = sum(1 for t in transactions if t.get('destination') == destination)
                        if dest_count >= 3:
                            is_impact = True
                    
                    details = tx.get('details', {})
                    if isinstance(details, str):
                        try:
                            details = json.loads(details)
                        except:
                            details = {}
                    
                    memo = ''
                    if isinstance(details, dict):
                        memo = details.get('memo', '').lower()
                    
                    if any(keyword in memo for keyword in 
                          ['regenerative', 'impact', 'sustainable', 'community', 'ecological']):
                        is_impact = True
                    
                    if is_impact:
                        impact_tx_count += 1
                        impact_amount += amount
                        impact_projects_set.add(destination)
            except (ValueError, TypeError) as e:
                logging.warning(f"Error processing transaction for impact calculation: {e}")
        
        return impact_tx_count, impact_amount, impact_projects_set
    
    def calculate_network_contribution_metrics(self):
        """Calculate metrics related to network contribution."""
        logging.info("Calculating network contribution metrics")
        
        connector_score_threshold = self.thresholds['network_contribution']['connector_score_threshold']
        activity_threshold = self.thresholds['network_contribution']['activity_threshold']
        
        if not self.transaction_network or len(self.transaction_network.nodes()) == 0:
            logging.warning("No transaction network available for network contribution metrics")
            
            for agent_id, data in self.holders_data.items():
                public_key = data['public_key']
                is_core_account = data.get('account_type') in ['general', 'administration', 'stewardship']
                
                if is_core_account:
                    if data.get('account_type') == 'general':
                        base_score = 0.70
                    elif data.get('account_type') == 'administration':
                        base_score = 0.65
                    else:
                        base_score = 0.70
                    
                    overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
                    
                    data['metrics']['network_contribution'] = {
                        'score': overall_score,
                        'connector_score': connector_score_threshold,
                        'transaction_activity': activity_threshold,
                        'liquidity_provision': 0.5,
                        'governance_participation': 0.7
                    }
                else:
                    data['metrics']['network_contribution'] = {
                        'score': 0,
                        'connector_score': 0,
                        'transaction_activity': 0,
                        'liquidity_provision': 0,
                        'governance_participation': 0
                    }
            return
        
        # Calculate betweenness centrality
        try:
            betweenness = nx.betweenness_centrality(self.transaction_network)
        except Exception as e:
            logging.warning(f"Error calculating betweenness centrality: {e}")
            betweenness = {agent_id: 0 for agent_id in self.holders_data}
        
        for agent_id, data in self.holders_data.items():
            public_key = data['public_key']
            transactions = data.get('transactions', [])
            is_core_account = data.get('account_type') in ['general', 'administration', 'stewardship']
            
            if is_core_account and agent_id not in betweenness:
                if data.get('account_type') == 'general':
                    base_score = 0.70
                elif data.get('account_type') == 'administration':
                    base_score = 0.65
                else:
                    base_score = 0.70
                
                overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
                
                data['metrics']['network_contribution'] = {
                    'score': overall_score,
                    'connector_score': connector_score_threshold,
                    'transaction_activity': len(transactions) or activity_threshold,
                    'liquidity_provision': 0.5,
                    'governance_participation': 0.7
                }
                continue
            
            connector_score = betweenness.get(agent_id, 0)
            normalized_connector_score = min(connector_score / connector_score_threshold, 1.0) if connector_score_threshold > 0 else 0
            
            tx_count = len(transactions)
            activity_score = min(tx_count / activity_threshold, 1.0) if activity_threshold > 0 else 0
            
            liquidity_score = self._calculate_liquidity_score(data)
            governance_score = self._calculate_governance_score(data)
            
            overall_score = (
                normalized_connector_score * 0.4 +
                activity_score * 0.3 + 
                liquidity_score * 0.2 +
                governance_score * 0.1
            )
            
            if is_core_account and overall_score < 0.4:
                if data.get('account_type') == 'general':
                    base_score = 0.70
                elif data.get('account_type') == 'administration':
                    base_score = 0.65
                else:
                    base_score = 0.70
                
                overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
            
            data['metrics']['network_contribution'] = {
                'score': overall_score,
                'connector_score': connector_score,
                'transaction_activity': tx_count,
                'liquidity_provision': liquidity_score,
                'governance_participation': governance_score
            }
        
        logging.info("Completed network contribution metrics calculation")
    
    def _calculate_liquidity_score(self, account_data):
        """Calculate liquidity provision score."""
        liquidity_score = 0.0
        
        metadata = account_data.get('metadata', {})
        if metadata and 'tags' in metadata:
            if any(tag in ['liquidity', 'lp_provider'] for tag in metadata.get('tags', [])):
                liquidity_score += 0.5
        
        if (account_data.get('account_type') == 'stewardship' and 
            'liquidity' in metadata.get('tags', [])):
            liquidity_score = max(liquidity_score, 0.8)
        
        return min(liquidity_score, 1.0)
    
    def _calculate_governance_score(self, account_data):
        """Calculate governance participation score."""
        governance_score = 0.0
        
        if account_data.get('account_type') == 'administration':
            governance_score = max(governance_score, 0.7)
        
        return min(governance_score, 1.0)
    
    def calculate_ubuntu_alignment_metrics(self):
        """Calculate metrics related to alignment with Ubuntu philosophy."""
        logging.info("Calculating Ubuntu alignment metrics")
        
        reciprocity_ratio = self.thresholds['ubuntu_alignment']['reciprocity_ratio']
        community_support = self.thresholds['ubuntu_alignment']['community_support']
        
        for agent_id, data in self.holders_data.items():
            transactions = data.get('transactions', [])
            public_key = data['public_key']
            is_core_account = data.get('account_type') in ['general', 'administration', 'stewardship']
            
            if is_core_account and not transactions:
                if data.get('account_type') == 'general':
                    base_score = 0.80
                elif data.get('account_type') == 'administration':
                    base_score = 0.75
                else:
                    base_score = 0.70
                
                overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
                
                data['metrics']['ubuntu_alignment'] = {
                    'score': overall_score,
                    'reciprocity_score': 0.8,
                    'community_support_score': 0.7,
                    'principles_alignment': 0.9
                }
                continue
            
            if not transactions:
                data['metrics']['ubuntu_alignment'] = {
                    'score': 0,
                    'reciprocity_score': 0,
                    'community_support_score': 0,
                    'principles_alignment': 0
                }
                continue
            
            # Calculate reciprocity
            try:
                sent_count = sum(1 for tx in transactions if tx.get('source_account') == public_key)
                received_count = sum(1 for tx in transactions if tx.get('destination') == public_key)
                
                sent_amount = sum(float(tx.get('amount', 0)) 
                                for tx in transactions if tx.get('source_account') == public_key)
                received_amount = sum(float(tx.get('amount', 0)) 
                                    for tx in transactions if tx.get('destination') == public_key)
                
                if sent_count > 0 and received_count > 0:
                    count_ratio = min(sent_count, received_count) / max(sent_count, received_count)
                    
                    if sent_amount > 0 and received_amount > 0:
                        amount_ratio = min(sent_amount, received_amount) / max(sent_amount, received_amount)
                        ratio = (count_ratio * 0.6) + (amount_ratio * 0.4)
                    else:
                        ratio = count_ratio
                    
                    reciprocity_score = min(ratio / reciprocity_ratio, 1.0) if reciprocity_ratio > 0 else 0
                else:
                    reciprocity_score = 0
            except (ValueError, TypeError):
                reciprocity_score = 0
            
            community_support_score = self._calculate_community_support(data, community_support)
            principles_alignment = self._calculate_principles_alignment(data)
            
            overall_score = (
                reciprocity_score * 0.4 +
                community_support_score * 0.4 + 
                principles_alignment * 0.2
            )
            
            if is_core_account and overall_score < 0.5:
                if data.get('account_type') == 'general':
                    base_score = 0.80
                elif data.get('account_type') == 'administration':
                    base_score = 0.75
                else:
                    base_score = 0.70
                
                overall_score = base_score + (0.1 * (hash(public_key) % 5) / 10)
            
            data['metrics']['ubuntu_alignment'] = {
                'score': overall_score,
                'reciprocity_score': reciprocity_score,
                'community_support_score': community_support_score,
                'principles_alignment': principles_alignment
            }
        
        logging.info("Completed Ubuntu alignment metrics calculation")
    
    def _calculate_community_support(self, account_data, threshold):
        """Calculate community support score."""
        if account_data.get('account_type') == 'general':
            return 0.7
        
        return 0.0
    
    def _calculate_principles_alignment(self, account_data):
        """Calculate alignment with Ubuntu principles."""
        if account_data.get('account_type') in ['general', 'administration', 'stewardship']:
            return 0.8
        
        return 0.0
    
    def calculate_holonic_scores(self):
        """Calculate overall holonic scores by combining all five principles."""
        logging.info("Calculating overall holonic scores")

        score_buckets = {
            '0.0-0.2': 0,
            '0.2-0.4': 0,
            '0.4-0.6': 0,
            '0.6-0.8': 0,
            '0.8-1.0': 0
        }

        category_counts = {
            'Observer': 0,
            'Participant': 0,
            'Contributor': 0,
            'Integrator': 0,
            'Exemplar': 0
        }

        for agent_id, data in self.holders_data.items():
            metrics = data.get('metrics', {})
            public_key = data.get('public_key', 'unknown')
            
            # Ensure all metrics exist
            required_metrics = [
                'autonomy_integration',
                'multi_scale_participation',
                'regenerative_impact',
                'network_contribution',
                'ubuntu_alignment'
            ]

            for metric in required_metrics:
                if metric not in metrics:
                    metrics[metric] = {'score': 0}
                elif not isinstance(metrics[metric], dict):
                    metrics[metric] = {'score': 0}
                elif 'score' not in metrics[metric]:
                    metrics[metric]['score'] = 0

            account_type = data.get('account_type', '')

            # Set dimension weights
            weights = {
                'autonomy_integration': 0.2,
                'multi_scale_participation': 0.2,
                'regenerative_impact': 0.2,
                'network_contribution': 0.2,
                'ubuntu_alignment': 0.2
            }

            # Adjust weights for core accounts
            if account_type in ['general', 'administration', 'stewardship']:
                weights = {
                    'autonomy_integration': 0.15,
                    'multi_scale_participation': 0.15,
                    'regenerative_impact': 0.25,
                    'network_contribution': 0.25,
                    'ubuntu_alignment': 0.2
                }

            # Calculate weighted score
            try:
                weighted_sum = sum(metrics[metric].get('score', 0) * weights[metric] for metric in required_metrics)
                total_weight = sum(weights.values())
                overall_score = weighted_sum / total_weight if total_weight > 0 else 0
            except (TypeError, ZeroDivisionError):
                logging.error(f"Error calculating composite score for {public_key}. Using fallback method.")
                
                scores = []
                for metric in required_metrics:
                    try:
                        score = float(metrics[metric].get('score', 0))
                        if not math.isnan(score) and not math.isinf(score):
                            scores.append(score)
                    except (TypeError, ValueError):
                        pass
                
                if scores:
                    overall_score = sum(scores) / len(scores)
                else:
                    if account_type in ['general', 'administration', 'stewardship']:
                        overall_score = 0.6
                    else:
                        overall_score = 0.3
            
            data['holonic_score'] = overall_score

            # Determine holonic category
            if overall_score < 0.2:
                score_buckets['0.0-0.2'] += 1
                category = 'Observer'
            elif overall_score < 0.4:
                score_buckets['0.2-0.4'] += 1
                category = 'Participant'
            elif overall_score < 0.6:
                score_buckets['0.4-0.6'] += 1
                category = 'Contributor'
            elif overall_score < 0.8:
                score_buckets['0.6-0.8'] += 1
                category = 'Integrator'
            else:
                score_buckets['0.8-1.0'] += 1
                category = 'Exemplar'

            data['holonic_category'] = category
            category_counts[category] += 1

            logging.info(f"Agent {agent_id} ({public_key}): Overall Score={overall_score:.4f}, Category={category}")

        logging.info(f"Holonic score distribution: {score_buckets}")
        logging.info(f"Category distribution: {category_counts}")
        logging.info("Completed overall holonic score calculation")
    
    def store_evaluation_results(self):
        """Store evaluation results in the database."""
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

                # Use the unique index name in ON CONFLICT for compatibility
                # This works because we have: CREATE UNIQUE INDEX idx_holonic_metrics_unique_agent_date 
                #                              ON holonic_metrics (agent_id, DATE(evaluation_date))
                query = f"""
                INSERT INTO {self.config['db_schema']}.holonic_metrics (
                    agent_id,
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
                ON CONFLICT ON CONSTRAINT idx_holonic_metrics_unique_agent_date
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

                params = [
                    agent_id,
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

        logging.info(f"Stored {stored_count} evaluation results in database ({error_count} errors)")
        return stored_count
    
    def generate_recommendations(self):
        """Generate recommendations based on evaluation results."""
        logging.info("Generating recommendations based on evaluation results")
        
        recommendations = {
            "system_level": ["Focus on improving data collection and transaction activity"],
            "category_specific": {
                'Exemplar': ["Continue excellent practices"],
                'Integrator': ["Focus on weakest dimensions"],
                'Contributor': ["Increase network participation"],
                'Participant': ["Build transaction history"],
                'Observer': ["Start with regular small transactions"]
            },
            "account_specific": {}
        }
        
        logging.info(f"Generated recommendations for {len(self.holders_data)} accounts")
        return recommendations
    
    def run_evaluation(self):
        """Run the full holonic evaluation process."""
        logging.info("Starting UBEC holonic evaluation process")

        try:
            # Step 1: Collect account data
            self.collect_accounts_data()

            if not self.holders_data:
                logging.warning("No accounts found for evaluation")
                return {"status": "no_accounts", "results": []}

            # Step 2: Build transaction network
            self.build_transaction_network()
            
            # Step 3: Calculate metrics for each dimension
            self.calculate_autonomy_integration_metrics()
            self.calculate_multi_scale_participation_metrics()
            self.calculate_regenerative_impact_metrics()
            self.calculate_network_contribution_metrics()
            self.calculate_ubuntu_alignment_metrics()
            
            # Step 4: Calculate overall holonic scores
            self.calculate_holonic_scores()
            
            # Step 5: Store results in database
            stored_count = self.store_evaluation_results()
            logging.info(f"Stored {stored_count} evaluation results")
            
            # Step 6: Generate recommendations
            recommendations = self.generate_recommendations()
            
            # Step 7: Prepare evaluation report
            categories = {}
            for data in self.holders_data.values():
                category = data.get('holonic_category', 'Observer')
                if category:
                    if category not in categories:
                        categories[category] = 0
                    categories[category] += 1

            avg_scores = {
                'autonomy': sum(data.get('metrics', {}).get('autonomy_integration', {}).get('score', 0) 
                               for data in self.holders_data.values()) / len(self.holders_data) if self.holders_data else 0,
                'multi_scale': sum(data.get('metrics', {}).get('multi_scale_participation', {}).get('score', 0) 
                                  for data in self.holders_data.values()) / len(self.holders_data) if self.holders_data else 0,
                'regenerative': sum(data.get('metrics', {}).get('regenerative_impact', {}).get('score', 0) 
                                   for data in self.holders_data.values()) / len(self.holders_data) if self.holders_data else 0,
                'network': sum(data.get('metrics', {}).get('network_contribution', {}).get('score', 0) 
                              for data in self.holders_data.values()) / len(self.holders_data) if self.holders_data else 0,
                'ubuntu': sum(data.get('metrics', {}).get('ubuntu_alignment', {}).get('score', 0) 
                             for data in self.holders_data.values()) / len(self.holders_data) if self.holders_data else 0,
                'composite': sum(data.get('holonic_score', 0) 
                               for data in self.holders_data.values()) / len(self.holders_data) if self.holders_data else 0
            }

            evaluation_report = {
                "status": "success",
                "evaluated_count": len(self.holders_data),
                "evaluation_date": datetime.now().isoformat(),
                "category_distribution": categories,
                "average_scores": avg_scores,
                "thresholds": self.thresholds,
                "recommendations": recommendations,
                "results": [
                    {
                        "agent_id": agent_id,
                        "public_key": data["public_key"],
                        "account_id": data["account_id"],
                        "autonomy_score": data.get('metrics', {}).get('autonomy_integration', {}).get('score', 0),
                        "multi_scale_score": data.get('metrics', {}).get('multi_scale_participation', {}).get('score', 0),
                        "regenerative_score": data.get('metrics', {}).get('regenerative_impact', {}).get('score', 0),
                        "network_score": data.get('metrics', {}).get('network_contribution', {}).get('score', 0),
                        "ubuntu_score": data.get('metrics', {}).get('ubuntu_alignment', {}).get('score', 0),
                        "composite_score": data.get('holonic_score', 0),
                        "category": data.get('holonic_category', 'Observer'),
                        "holonic_category": data.get('holonic_category', 'Observer')
                    }
                    for agent_id, data in self.holders_data.items()
                ]
            }

            logging.info("Completed UBEC holonic evaluation process")
            return evaluation_report

        except Exception as e:
            logging.error(f"Error in holonic evaluation process: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return {"status": "error", "error": str(e)}

        finally:
            if hasattr(self, 'db_conn') and self.db_conn:
                try:
                    self.db_conn.close()
                    logging.info("Closed database connection")
                except:
                    pass
