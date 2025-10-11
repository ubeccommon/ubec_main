# core/db/connection.py
"""
PostgreSQL Database Connection Module for UBEC Protocol

Single database connection implementation matching exact .env configuration.
Supports three user types:
- ubec_app: Main application operations (default)
- ubec_readonly: Read-only access for reporting
- ubec_sync: Blockchain synchronization operations

Environment Variables Required (from .env):
    DB_HOST: Database host
    DB_PORT: Database port
    DB_NAME: Database name
    DB_SCHEMA: Default schema
    DB_USER: Application user
    DB_PASSWORD: Application user password
    DB_READONLY_USER: Read-only user (optional)
    DB_READONLY_PASSWORD: Read-only user password (optional)
    DB_SYNC_USER: Sync user (optional)
    DB_SYNC_PASSWORD: Sync user password (optional)
    DB_SSL_MODE: SSL mode (default: prefer)
    DB_POOL_MIN: Minimum pool connections (default: 2)
    DB_POOL_MAX: Maximum pool connections (default: 20)

Usage:
    # Simple connection
    conn = get_connection()
    
    # With specific user type
    conn = get_connection(user_type='readonly')
    
    # Using DatabaseConnection class
    db = DatabaseConnection()
    
    # Using DatabaseManager with schema
    db = DatabaseManager(schema='ubec_main')
    result = db.execute_query("SELECT * FROM accounts")

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def _get_connection_params(user_type='app'):
    """
    Get database connection parameters for specified user type.
    
    Args:
        user_type (str): Type of user - 'app', 'readonly', or 'sync'
        
    Returns:
        dict: Connection parameters
        
    Raises:
        ValueError: If credentials not configured for user type
    """
    # Base parameters (same for all users)
    params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'dbname': os.getenv('DB_NAME', 'ubec'),
        'sslmode': os.getenv('DB_SSL_MODE', 'prefer')
    }
    
    # User-specific credentials
    if user_type == 'app':
        params['user'] = os.getenv('DB_USER')
        params['password'] = os.getenv('DB_PASSWORD')
    elif user_type == 'readonly':
        params['user'] = os.getenv('DB_READONLY_USER')
        params['password'] = os.getenv('DB_READONLY_PASSWORD')
    elif user_type == 'sync':
        params['user'] = os.getenv('DB_SYNC_USER')
        params['password'] = os.getenv('DB_SYNC_PASSWORD')
    else:
        raise ValueError(f"Invalid user_type: {user_type}. Must be 'app', 'readonly', or 'sync'")
    
    # Validate credentials are configured
    if not params.get('user') or not params.get('password'):
        raise ValueError(
            f"Database credentials not configured for user_type '{user_type}'. "
            f"Please set DB_{user_type.upper()}_USER and DB_{user_type.upper()}_PASSWORD in .env file"
        )
    
    return params


def get_connection(user_type='app'):
    """
    Create a connection to the PostgreSQL database.
    
    This is the primary connection function. Always creates a fresh connection.
    For production use with connection pooling, use DatabaseManager.
    
    Args:
        user_type (str): Type of database user - 'app', 'readonly', or 'sync'
                        Defaults to 'app' for main application operations
        
    Returns:
        Connection: PostgreSQL database connection with RealDictCursor
        
    Raises:
        ValueError: If credentials not configured
        psycopg2.Error: If connection fails
        
    Example:
        # Main application connection
        conn = get_connection()
        
        # Read-only connection for reporting
        conn = get_connection(user_type='readonly')
        
        # Sync connection for blockchain operations
        conn = get_connection(user_type='sync')
    """
    try:
        params = _get_connection_params(user_type)
        
        logger.debug(
            f"Connecting to database: host={params['host']}, "
            f"database={params['dbname']}, user={params['user']}"
        )
        
        conn = psycopg2.connect(
            cursor_factory=RealDictCursor,
            **params
        )
        
        return conn
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating database connection: {e}")
        raise


def get_admin_connection():
    """
    Get a connection to the postgres database for administrative tasks.
    
    Uses the main app credentials but connects to 'postgres' database
    for operations like creating databases or roles.
    
    Returns:
        Connection: PostgreSQL connection to postgres database
        
    Example:
        conn = get_admin_connection()
        with conn.cursor() as cur:
            cur.execute("CREATE DATABASE new_db")
    """
    try:
        params = _get_connection_params('app')
        params['dbname'] = 'postgres'  # Connect to default postgres database
        
        conn = psycopg2.connect(
            cursor_factory=RealDictCursor,
            **params
        )
        conn.autocommit = True  # Required for database creation
        
        return conn
        
    except Exception as e:
        logger.error(f"Admin database connection error: {e}")
        raise


def create_database_if_not_exists(db_name):
    """
    Create a database if it doesn't exist.
    
    Args:
        db_name (str): Name of the database to create
        
    Returns:
        bool: True if successful or database exists, False on error
    """
    try:
        conn = get_admin_connection()
        
        # Check if database exists
        with conn.cursor() as cur:
            cur.execute(
                "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = %s)",
                (db_name,)
            )
            db_exists = cur.fetchone()['exists']
        
        if not db_exists:
            with conn.cursor() as cur:
                cur.execute(f'CREATE DATABASE "{db_name}"')
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False


def execute_query(query, params=None, fetch_one=False, fetch_all=True, user_type='app'):
    """
    Execute a query and return results.
    
    Args:
        query (str): SQL query to execute
        params (tuple/dict): Parameters for the query
        fetch_one (bool): If True, fetch only one result
        fetch_all (bool): If True, fetch all results (ignored if fetch_one is True)
        user_type (str): Database user type to use
        
    Returns:
        Query results or row count for non-SELECT queries
    """
    conn = get_connection(user_type=user_type)
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            
            if cur.description:  # Query returns data
                if fetch_one:
                    return cur.fetchone()
                elif fetch_all:
                    return cur.fetchall()
                else:
                    return None
            
            conn.commit()
            return cur.rowcount
            
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise
    finally:
        conn.close()


def execute_transaction(queries_and_params, user_type='app'):
    """
    Execute multiple queries in a transaction.
    
    Args:
        queries_and_params (list): List of (query, params) tuples
        user_type (str): Database user type to use
        
    Returns:
        bool: True if successful
        
    Example:
        execute_transaction([
            ("INSERT INTO accounts (name) VALUES (%s)", ['Alice']),
            ("INSERT INTO balances (account_id, amount) VALUES (%s, %s)", [1, 100])
        ])
    """
    conn = get_connection(user_type=user_type)
    try:
        with conn.cursor() as cur:
            for query, params in queries_and_params:
                cur.execute(query, params)
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Transaction execution error: {e}")
        raise
    finally:
        conn.close()


def insert_record(table, data, returning=None, user_type='app'):
    """
    Insert a record into a table.
    
    Args:
        table (str): Table name
        data (dict): Column-value pairs to insert
        returning (str): Optional column to return (e.g., 'id')
        user_type (str): Database user type to use
        
    Returns:
        The returned value if specified, otherwise row count
    """
    columns = list(data.keys())
    values = list(data.values())
    placeholders = ', '.join(['%s'] * len(columns))
    
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    
    if returning:
        query += f" RETURNING {returning}"
    
    conn = get_connection(user_type=user_type)
    try:
        with conn.cursor() as cur:
            cur.execute(query, values)
            
            if returning:
                result = cur.fetchone()
                conn.commit()
                return result[returning]
            
            conn.commit()
            return cur.rowcount
    except Exception as e:
        conn.rollback()
        logger.error(f"Insert error: {e}")
        raise
    finally:
        conn.close()


def update_record(table, data, condition, condition_params, user_type='app'):
    """
    Update records in a table.
    
    Args:
        table (str): Table name
        data (dict): Column-value pairs to update
        condition (str): WHERE condition (e.g., "id = %s")
        condition_params (list): Parameters for the condition
        user_type (str): Database user type to use
        
    Returns:
        Number of rows affected
    """
    set_expressions = [f"{column} = %s" for column in data.keys()]
    values = list(data.values()) + list(condition_params)
    
    query = f"UPDATE {table} SET {', '.join(set_expressions)} WHERE {condition}"
    
    conn = get_connection(user_type=user_type)
    try:
        with conn.cursor() as cur:
            cur.execute(query, values)
            conn.commit()
            return cur.rowcount
    except Exception as e:
        conn.rollback()
        logger.error(f"Update error: {e}")
        raise
    finally:
        conn.close()


def delete_record(table, condition, condition_params, user_type='app'):
    """
    Delete records from a table.
    
    Args:
        table (str): Table name
        condition (str): WHERE condition (e.g., "id = %s")
        condition_params (list): Parameters for the condition
        user_type (str): Database user type to use
        
    Returns:
        Number of rows affected
    """
    query = f"DELETE FROM {table} WHERE {condition}"
    
    conn = get_connection(user_type=user_type)
    try:
        with conn.cursor() as cur:
            cur.execute(query, condition_params)
            conn.commit()
            return cur.rowcount
    except Exception as e:
        conn.rollback()
        logger.error(f"Delete error: {e}")
        raise
    finally:
        conn.close()


class DatabaseConnection:
    """
    Simple database connection wrapper.
    
    Provides a connection object that can be used by modules expecting
    a connection instance (like UBECHolonicEvaluator).
    
    Example:
        db = DatabaseConnection()
        if db.conn:
            # Use db.conn for queries
            pass
        db.close()
    """
    
    def __init__(self, user_type='app'):
        """
        Initialize database connection.
        
        Args:
            user_type (str): Database user type - 'app', 'readonly', or 'sync'
        """
        self.user_type = user_type
        try:
            self.conn = get_connection(user_type=user_type)
            logger.debug(f"DatabaseConnection initialized with user_type={user_type}")
        except Exception as e:
            logger.error(f"Failed to initialize DatabaseConnection: {e}")
            self.conn = None
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed")


class DatabaseManager:
    """
    Database manager with schema support and transaction handling.
    
    Provides a high-level interface for database operations with automatic
    schema handling and proper resource management.
    
    Example:
        db = DatabaseManager(schema='ubec_main')
        
        # Query
        accounts = db.execute_query("SELECT * FROM accounts")
        
        # Insert
        account_id = db.insert('accounts', {'name': 'Alice'})
        
        # Transaction
        db.execute_transaction([
            ("INSERT INTO accounts (name) VALUES (%s)", ['Bob']),
            ("UPDATE balances SET amount = %s WHERE account_id = %s", [100, 1])
        ])
    """
    
    def __init__(self, schema=None, user_type='app'):
        """
        Initialize DatabaseManager.
        
        Args:
            schema (str): Schema to use. If None, uses DB_SCHEMA from environment
            user_type (str): Database user type - 'app', 'readonly', or 'sync'
        """
        self.schema = schema or os.getenv('DB_SCHEMA', 'ubec_main')
        self.user_type = user_type
        
        logger.debug(
            f"DatabaseManager initialized: schema='{self.schema}', "
            f"user_type='{user_type}'"
        )
    
    def _execute_with_schema(self, operation, *args, **kwargs):
        """Execute an operation with schema context."""
        conn = get_connection(user_type=self.user_type)
        try:
            with conn.cursor() as cur:
                # Set schema search path
                cur.execute(f"SET search_path TO {self.schema}, public")
                
                # Execute the actual operation
                result = operation(conn, cur, *args, **kwargs)
                
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation error: {e}")
            raise
        finally:
            conn.close()
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=True):
        """Execute a query with schema context."""
        def _query(conn, cur, query, params, fetch_one, fetch_all):
            cur.execute(query, params)
            
            if cur.description:  # Query returns data
                if fetch_one:
                    return cur.fetchone()
                elif fetch_all:
                    return cur.fetchall()
                else:
                    return None
            
            return cur.rowcount
        
        return self._execute_with_schema(_query, query, params, fetch_one, fetch_all)
    
    def execute_transaction(self, queries_and_params):
        """Execute multiple queries in a transaction with schema context."""
        def _transaction(conn, cur, queries_and_params):
            for query, params in queries_and_params:
                cur.execute(query, params)
            return True
        
        return self._execute_with_schema(_transaction, queries_and_params)
    
    def insert(self, table, data, return_id=True):
        """Insert a record and optionally return the ID."""
        if return_id:
            return insert_record(table, data, returning='id', user_type=self.user_type)
        else:
            return insert_record(table, data, user_type=self.user_type)
    
    def update(self, table, data, condition, condition_params):
        """Update records in a table."""
        return update_record(table, data, condition, condition_params, user_type=self.user_type)
    
    def delete(self, table, condition, condition_params):
        """Delete records from a table."""
        return delete_record(table, condition, condition_params, user_type=self.user_type)
    
    def get_by_id(self, table, id_value, id_field='id'):
        """Get a record by ID."""
        query = f"SELECT * FROM {table} WHERE {id_field} = %s"
        return self.execute_query(query, [id_value], fetch_one=True)
