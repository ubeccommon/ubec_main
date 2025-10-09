# db/connection.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def get_connection(database=None):
    """
    Create a connection to the PostgreSQL database.
    
    Args:
        database (str, optional): Database name to connect to. If None, uses DB_NAME from env.
        
    Returns:
        Connection: PostgreSQL database connection
    """
    try:
        # If database parameter is not provided, get from environment
        if database is None:
            database = os.getenv('DB_NAME', 'ubec_recipro')
            
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            dbname=database,
            user=os.getenv('DB_USER', 'recipro'),
            password=os.getenv('DB_PASSWORD', 'password'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def get_admin_connection():
    """
    Get a connection to the default PostgreSQL database (postgres).
    Used for administrative tasks like creating a new database.
    
    Returns:
        Connection: Database connection to postgres database
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            dbname="postgres",  # Connect to default postgres database
            user=os.getenv('DB_USER', 'recipro'),
            password=os.getenv('DB_PASSWORD', 'password'),
            cursor_factory=RealDictCursor
        )
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
                cur.execute(f'CREATE DATABASE "{db_name}";')
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """
    Execute a query and return the results.
    
    Args:
        query (str): SQL query to execute
        params (tuple or dict): Parameters for the query
        fetch_one (bool): If True, fetch only one result
        fetch_all (bool): If True, fetch all results (ignored if fetch_one is True)
        
    Returns:
        Query results or None for queries that don't return data
    """
    conn = get_connection()
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
        logger.error(f"Query execution error: {query}, {e}")
        raise
    finally:
        conn.close()

def execute_transaction(queries_and_params):
    """
    Execute multiple queries in a transaction.
    
    Args:
        queries_and_params (list): List of (query, params) tuples
        
    Returns:
        None
    """
    conn = get_connection()
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

def insert_record(table, data, returning=None):
    """
    Insert a record into a table.
    
    Args:
        table (str): Table name
        data (dict): Column-value pairs to insert
        returning (str): Optional column to return (e.g., 'id')
        
    Returns:
        The returned value if specified, otherwise the number of rows affected
    """
    columns = list(data.keys())
    values = list(data.values())
    
    placeholders = [f'%s' for _ in columns]
    
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
    
    if returning:
        query += f" RETURNING {returning}"
        
    conn = get_connection()
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
        logger.error(f"Insert error: {query}, {e}")
        raise
    finally:
        conn.close()

def update_record(table, data, condition, condition_params):
    """
    Update records in a table.
    
    Args:
        table (str): Table name
        data (dict): Column-value pairs to update
        condition (str): WHERE condition (e.g., "id = %s")
        condition_params (list): Parameters for the condition
        
    Returns:
        Number of rows affected
    """
    set_expressions = [f"{column} = %s" for column in data.keys()]
    values = list(data.values()) + list(condition_params)
    
    query = f"UPDATE {table} SET {', '.join(set_expressions)} WHERE {condition}"
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, values)
            conn.commit()
            return cur.rowcount
    except Exception as e:
        conn.rollback()
        logger.error(f"Update error: {query}, {e}")
        raise
    finally:
        conn.close()

def delete_record(table, condition, condition_params):
    """
    Delete records from a table.
    
    Args:
        table (str): Table name
        condition (str): WHERE condition (e.g., "id = %s")
        condition_params (list): Parameters for the condition
        
    Returns:
        Number of rows affected
    """
    query = f"DELETE FROM {table} WHERE {condition}"
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, condition_params)
            conn.commit()
            return cur.rowcount
    except Exception as e:
        conn.rollback()
        logger.error(f"Delete error: {query}, {e}")
        raise
    finally:
        conn.close()

def call_procedure(procedure_name, params=None, fetch_results=False):
    """
    Call a PostgreSQL stored procedure.
    
    Args:
        procedure_name (str): Name of the procedure
        params (list): Parameters for the procedure
        fetch_results (bool): Whether to fetch results
        
    Returns:
        Procedure results if fetch_results is True, otherwise None
    """
    params_str = ', '.join(['%s' for _ in (params or [])])
    query = f"CALL {procedure_name}({params_str})"
    
    if fetch_results:
        return execute_query(query, params)
    else:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return None
        except Exception as e:
            conn.rollback()
            logger.error(f"Procedure call error: {query}, {e}")
            raise
        finally:
            conn.close()

def call_function(function_name, params=None, fetch_one=False):
    """
    Call a PostgreSQL function.
    
    Args:
        function_name (str): Name of the function
        params (list): Parameters for the function
        fetch_one (bool): Whether to fetch one result or all
        
    Returns:
        Function results
    """
    params_str = ', '.join(['%s' for _ in (params or [])])
    query = f"SELECT * FROM {function_name}({params_str})"
    
    return execute_query(query, params, fetch_one=fetch_one)

# Compatibility function to simulate the DatabaseManager class interface
class DatabaseManager:
    """
    Compatibility class to provide an object-oriented interface 
    to the database functions.
    """
    
    def __init__(self, schema='ubec_recipro'):
        self.schema = schema
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=True):
        # Set schema first if specified
        if self.schema:
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(f"SET search_path TO {self.schema}, public")
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
                logger.error(f"Query execution error: {query}, {e}")
                raise
            finally:
                conn.close()
        else:
            # Use the global function if no schema specified
            return execute_query(query, params, fetch_one, fetch_all)
    
    def execute_transaction(self, queries_and_params):
        return execute_transaction(queries_and_params)
    
    def insert(self, table, data, return_id=True):
        if return_id:
            return insert_record(table, data, returning='id')
        else:
            return insert_record(table, data)
    
    def update(self, table, data, condition, condition_params):
        return update_record(table, data, condition, condition_params)
    
    def delete(self, table, condition, condition_params):
        return delete_record(table, condition, condition_params)
    
    def call_function(self, function_name, params=None, fetch_one=False):
        return call_function(function_name, params, fetch_one)
    
    def get_by_id(self, table, id_value, id_field='id'):
        query = f"SELECT * FROM {table} WHERE {id_field} = %s"
        return self.execute_query(query, [id_value], fetch_one=True)
