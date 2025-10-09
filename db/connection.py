# db/connection.py
"""
PostgreSQL Database Connection Module for UBEC Protocol

This module provides database connection management with support for:
- Multiple user types (app, readonly, sync, admin)
- Schema-aware operations
- Connection pooling configuration
- Transaction management
- CRUD operations with proper error handling

Environment Variables Required:
    UBEC_DB_HOST: Database host (default: localhost)
    UBEC_DB_PORT: Database port (default: 5432)
    UBEC_DB_NAME: Database name (default: ubec)
    UBEC_DB_SCHEMA: Default schema (default: ubec_main)
    UBEC_DB_USER: Application user credentials
    UBEC_DB_PASSWORD: Application user password
    UBEC_DB_READONLY_USER: Read-only user credentials (optional)
    UBEC_DB_READONLY_PASSWORD: Read-only user password (optional)
    UBEC_DB_SYNC_USER: Sync user credentials (optional)
    UBEC_DB_SYNC_PASSWORD: Sync user password (optional)
    UBEC_DB_SSL_MODE: SSL mode (default: prefer)
    UBEC_DB_POOL_MIN: Minimum pool connections (default: 2)
    UBEC_DB_POOL_MAX: Maximum pool connections (default: 20)

Usage Examples:
    # Simple query
    result = execute_query("SELECT * FROM accounts WHERE id = %s", [1], fetch_one=True)
    
    # Using DatabaseManager with schema
    db = DatabaseManager(schema='ubec_main', user_type='app')
    db.create_schema()  # Create schema if needed
    accounts = db.execute_query("SELECT * FROM accounts")
    
    # Insert with returning ID
    account_id = db.insert('accounts', {'name': 'John', 'balance': 100})
    
    # Transaction
    db.execute_transaction([
        ("INSERT INTO accounts (name) VALUES (%s)", ['Alice']),
        ("INSERT INTO balances (account_id, amount) VALUES (%s, %s)", [1, 100])
    ])
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2 import pool
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool = None

def _get_pool_config():
    """Get connection pool configuration from environment."""
    return {
        'minconn': int(os.getenv('UBEC_DB_POOL_MIN', '2')),
        'maxconn': int(os.getenv('UBEC_DB_POOL_MAX', '20')),
    }

def _get_connection_params(database=None, user_type='app'):
    """
    Get database connection parameters based on user type.
    
    Args:
        database (str, optional): Database name to connect to
        user_type (str): Type of user - 'app', 'readonly', 'sync', or 'admin'
        
    Returns:
        dict: Connection parameters
    """
    # Base connection parameters
    params = {
        'host': os.getenv('UBEC_DB_HOST', 'localhost'),
        'port': os.getenv('UBEC_DB_PORT', '5432'),
    }
    
    # Database name
    if database is None:
        params['dbname'] = os.getenv('UBEC_DB_NAME', 'ubec')
    else:
        params['dbname'] = database
    
    # User credentials based on type
    if user_type == 'app':
        params['user'] = os.getenv('UBEC_DB_USER')
        params['password'] = os.getenv('UBEC_DB_PASSWORD')
    elif user_type == 'readonly':
        params['user'] = os.getenv('UBEC_DB_READONLY_USER')
        params['password'] = os.getenv('UBEC_DB_READONLY_PASSWORD')
    elif user_type == 'sync':
        params['user'] = os.getenv('UBEC_DB_SYNC_USER')
        params['password'] = os.getenv('UBEC_DB_SYNC_PASSWORD')
    elif user_type == 'admin':
        # For admin operations, connect to postgres database
        params['dbname'] = 'postgres'
        params['user'] = os.getenv('UBEC_DB_USER')
        params['password'] = os.getenv('UBEC_DB_PASSWORD')
    
    # Check for required credentials
    if not params.get('user') or not params.get('password'):
        raise ValueError(
            f"Database credentials not configured for user_type '{user_type}'. "
            f"Please set UBEC_DB_USER and UBEC_DB_PASSWORD in .env file"
        )
    
    # SSL mode
    ssl_mode = os.getenv('UBEC_DB_SSL_MODE', 'prefer')
    params['sslmode'] = ssl_mode
    
    return params

def get_connection(database=None, user_type='app'):
    """
    Create a connection to the PostgreSQL database.
    
    Args:
        database (str, optional): Database name to connect to. If None, uses UBEC_DB_NAME from env.
        user_type (str): Type of user - 'app', 'readonly', 'sync' (default: 'app')
        
    Returns:
        Connection: PostgreSQL database connection
    """
    try:
        params = _get_connection_params(database, user_type)
        
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
    Get a connection to the default PostgreSQL database (postgres).
    Used for administrative tasks like creating a new database.
    
    Returns:
        Connection: Database connection to postgres database
    """
    try:
        conn = get_connection(database='postgres', user_type='admin')
        # Set autocommit to True for database creation
        conn.autocommit = True
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
        bool: True if successful, False otherwise
    """
    try:
        # Connect to the default postgres database
        conn = get_admin_connection()
        
        # Check if database exists
        check_query = """
        SELECT EXISTS(
            SELECT 1 FROM pg_database WHERE datname = %s
        );
        """
        with conn.cursor() as cur:
            cur.execute(check_query, (db_name,))
            db_exists = cur.fetchone()['exists']
        
        if not db_exists:
            # Create database - use SQL identifier quoting to prevent injection
            # and handle names with special characters
            with conn.cursor() as cur:
                # Use AsIs for identifiers to prevent SQL injection while allowing identifier
                from psycopg2.extensions import AsIs
                cur.execute('CREATE DATABASE %s;', (AsIs(f'"{db_name}"'),))
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
    Execute a query and return the results.
    
    Args:
        query (str): SQL query to execute
        params (tuple or dict): Parameters for the query
        fetch_one (bool): If True, fetch only one result
        fetch_all (bool): If True, fetch all results (ignored if fetch_one is True)
        user_type (str): Type of database user to use
        
    Returns:
        Query results or None for queries that don't return data
    """
    conn = get_connection(user_type=user_type)
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            
            if cur.description:  # Check if query returns data
                if fetch_one:
                    return cur.fetchone()
                elif fetch_all:
                    return cur.fetchall()
                else:
                    return None  # Just execute without fetching
            
            conn.commit()
            
            # Return number of affected rows for non-select queries
            return cur.rowcount
    except Exception as e:
        logger.error(f"Query execution error: {query[:100]}..., {e}")
        raise
    finally:
        conn.close()

def execute_transaction(queries_and_params, user_type='app'):
    """
    Execute multiple queries in a transaction.
    
    Args:
        queries_and_params (list): List of (query, params) tuples
        user_type (str): Type of database user to use
        
    Returns:
        bool: True if successful
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
        user_type (str): Type of database user to use
        
    Returns:
        The returned value if specified, otherwise the number of rows affected
    """
    columns = list(data.keys())
    values = list(data.values())
    
    placeholders = [f'%s' for _ in columns]
    
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
    
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
        logger.error(f"Insert error: {query[:100]}..., {e}")
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
        user_type (str): Type of database user to use
        
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
        logger.error(f"Update error: {query[:100]}..., {e}")
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
        user_type (str): Type of database user to use
        
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
        logger.error(f"Delete error: {query[:100]}..., {e}")
        raise
    finally:
        conn.close()

def call_procedure(procedure_name, params=None, fetch_results=False, user_type='app'):
    """
    Call a PostgreSQL stored procedure.
    
    Args:
        procedure_name (str): Name of the procedure
        params (list): Parameters for the procedure
        fetch_results (bool): Whether to fetch results
        user_type (str): Type of database user to use
        
    Returns:
        Procedure results if fetch_results is True, otherwise None
    """
    params_str = ', '.join(['%s' for _ in (params or [])])
    query = f"CALL {procedure_name}({params_str})"
    
    if fetch_results:
        return execute_query(query, params, user_type=user_type)
    else:
        conn = get_connection(user_type=user_type)
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return None
        except Exception as e:
            conn.rollback()
            logger.error(f"Procedure call error: {query[:100]}..., {e}")
            raise
        finally:
            conn.close()

def call_function(function_name, params=None, fetch_one=False, user_type='app'):
    """
    Call a PostgreSQL function.
    
    Args:
        function_name (str): Name of the function
        params (list): Parameters for the function
        fetch_one (bool): Whether to fetch one result or all
        user_type (str): Type of database user to use
        
    Returns:
        Function results
    """
    params_str = ', '.join(['%s' for _ in (params or [])])
    query = f"SELECT * FROM {function_name}({params_str})"
    
    return execute_query(query, params, fetch_one=fetch_one, user_type=user_type)

def create_schema_if_not_exists(schema_name):
    """
    Create a schema if it doesn't exist.
    
    Args:
        schema_name (str): Name of the schema to create
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection(user_type='app')
        
        # Check if schema exists
        check_query = """
        SELECT EXISTS(
            SELECT 1 FROM information_schema.schemata WHERE schema_name = %s
        );
        """
        with conn.cursor() as cur:
            cur.execute(check_query, (schema_name,))
            schema_exists = cur.fetchone()['exists']
        
        if not schema_exists:
            # Create schema - use SQL identifier quoting to prevent injection
            with conn.cursor() as cur:
                from psycopg2.extensions import AsIs
                cur.execute('CREATE SCHEMA %s;', (AsIs(f'"{schema_name}"'),))
                conn.commit()
            logger.info(f"Schema '{schema_name}' created successfully")
        else:
            logger.info(f"Schema '{schema_name}' already exists")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to create schema: {e}")
        return False

def test_connection():
    """
    Test database connection and return connection info.
    
    Returns:
        dict: Connection status and database info
    """
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()['version']
            cur.execute("SELECT current_database();")
            database = cur.fetchone()['current_database']
            cur.execute("SELECT current_user;")
            user = cur.fetchone()['current_user']
            cur.execute("SELECT current_schema();")
            schema = cur.fetchone()['current_schema']
        conn.close()
        
        return {
            'success': True,
            'database': database,
            'schema': schema,
            'user': user,
            'version': version
        }
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def validate_database_setup():
    """
    Validate that the database and schema are properly configured.
    
    Returns:
        dict: Validation results with details
    """
    results = {
        'database_exists': False,
        'schema_exists': False,
        'user_has_permissions': False,
        'connection_successful': False,
        'errors': []
    }
    
    try:
        # Test basic connection
        conn_test = test_connection()
        if conn_test['success']:
            results['connection_successful'] = True
            results['database_exists'] = True
        else:
            results['errors'].append(f"Connection failed: {conn_test.get('error')}")
            return results
        
        # Check if configured schema exists
        schema_name = os.getenv('UBEC_DB_SCHEMA', 'ubec_main')
        conn = get_connection()
        
        with conn.cursor() as cur:
            # Check schema existence
            cur.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.schemata 
                    WHERE schema_name = %s
                );
            """, (schema_name,))
            results['schema_exists'] = cur.fetchone()['exists']
            
            # Test create table permission in schema
            try:
                cur.execute(f"SET search_path TO {schema_name}, public")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS _connection_test (
                        id SERIAL PRIMARY KEY,
                        test_field VARCHAR(50)
                    );
                """)
                cur.execute("DROP TABLE IF EXISTS _connection_test;")
                conn.commit()
                results['user_has_permissions'] = True
            except Exception as e:
                results['errors'].append(f"Permission test failed: {e}")
                conn.rollback()
        
        conn.close()
        
    except Exception as e:
        results['errors'].append(f"Validation error: {e}")
    
    return results

# Compatibility class to simulate the DatabaseManager class interface
class DatabaseManager:
    """
    Compatibility class to provide an object-oriented interface 
    to the database functions.
    """
    
    def __init__(self, schema=None, user_type='app'):
        """
        Initialize DatabaseManager.
        
        The schema is determined in this priority order:
        1. Explicitly passed 'schema' parameter
        2. UBEC_DB_SCHEMA environment variable from .env
        3. Default value: 'ubec_main'
        
        Args:
            schema (str, optional): Schema to use. If None, reads from UBEC_DB_SCHEMA 
                                   environment variable, defaults to 'ubec_main'
            user_type (str): Type of database user - 'app', 'readonly', or 'sync'
                           Defaults to 'app'
        
        Example:
            # Recommended: Let it read from environment
            db = DatabaseManager()  # Uses UBEC_DB_SCHEMA from .env
            
            # Or explicitly specify
            db = DatabaseManager(schema='custom_schema')
            
            # Or read environment explicitly in your code
            import os
            schema = os.getenv('UBEC_DB_SCHEMA', 'ubec_main')
            db = DatabaseManager(schema=schema)
        """
        # Priority: parameter > environment variable > default
        self.schema = schema or os.getenv('UBEC_DB_SCHEMA', 'ubec_main')
        self.user_type = user_type
        
        logger.debug(
            f"DatabaseManager initialized: schema='{self.schema}', "
            f"user_type='{user_type}', "
            f"source={'parameter' if schema else 'environment'}"
        )
    
    def create_schema(self):
        """
        Create the configured schema if it doesn't exist.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.schema:
            return create_schema_if_not_exists(self.schema)
        return False
    
    def _get_connection_with_schema(self):
        """Get a connection and set the search path to the configured schema."""
        conn = get_connection(user_type=self.user_type)
        if self.schema:
            try:
                with conn.cursor() as cur:
                    cur.execute(f"SET search_path TO {self.schema}, public")
            except Exception as e:
                logger.error(f"Error setting schema search path: {e}")
                conn.close()
                raise
        return conn
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=True):
        """Execute a query with optional schema context."""
        conn = self._get_connection_with_schema()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                
                if cur.description:  # Check if query returns data
                    if fetch_one:
                        return cur.fetchone()
                    elif fetch_all:
                        return cur.fetchall()
                    else:
                        return None  # Just execute without fetching
                
                conn.commit()
                
                # Return number of affected rows for non-select queries
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Query execution error: {query[:100]}..., {e}")
            raise
        finally:
            conn.close()
    
    def execute_transaction(self, queries_and_params):
        """Execute multiple queries in a transaction with schema context."""
        conn = self._get_connection_with_schema()
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
    
    def insert(self, table, data, return_id=True):
        """Insert a record and optionally return the ID."""
        columns = list(data.keys())
        values = list(data.values())
        
        placeholders = [f'%s' for _ in columns]
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        if return_id:
            query += " RETURNING id"
        
        conn = self._get_connection_with_schema()
        try:
            with conn.cursor() as cur:
                cur.execute(query, values)
                
                if return_id:
                    result = cur.fetchone()
                    conn.commit()
                    return result['id']
                
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Insert error: {query[:100]}..., {e}")
            raise
        finally:
            conn.close()
    
    def update(self, table, data, condition, condition_params):
        """Update records."""
        set_expressions = [f"{column} = %s" for column in data.keys()]
        values = list(data.values()) + list(condition_params)
        
        query = f"UPDATE {table} SET {', '.join(set_expressions)} WHERE {condition}"
        
        conn = self._get_connection_with_schema()
        try:
            with conn.cursor() as cur:
                cur.execute(query, values)
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Update error: {query[:100]}..., {e}")
            raise
        finally:
            conn.close()
    
    def delete(self, table, condition, condition_params):
        """Delete records."""
        query = f"DELETE FROM {table} WHERE {condition}"
        
        conn = self._get_connection_with_schema()
        try:
            with conn.cursor() as cur:
                cur.execute(query, condition_params)
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Delete error: {query[:100]}..., {e}")
            raise
        finally:
            conn.close()
    
    def call_function(self, function_name, params=None, fetch_one=False):
        """Call a database function."""
        params_str = ', '.join(['%s' for _ in (params or [])])
        query = f"SELECT * FROM {function_name}({params_str})"
        
        return self.execute_query(query, params, fetch_one=fetch_one)
    
    def get_by_id(self, table, id_value, id_field='id'):
        """Get a record by ID."""
        query = f"SELECT * FROM {table} WHERE {id_field} = %s"
        return self.execute_query(query, [id_value], fetch_one=True)
    
    def test_connection(self):
        """Test the database connection."""
        return test_connection()
    
    def validate_setup(self):
        """
        Validate that the database and schema are properly configured.
        
        Returns:
            dict: Validation results with details
        """
        return validate_database_setup()
