#!/usr/bin/env python3
"""
Async Database Manager for UBEC Protocol - Enhanced Version
============================================================
Provides async database access using asyncpg with comprehensive health monitoring.

This module implements:
- Async connection pooling with automatic schema management
- Query execution with async/await patterns
- Transaction management with context managers
- Automatic parameter placeholder conversion (%s → $1, $2...)
- ISO 8601 datetime string conversion
- Comprehensive health check monitoring
- Connection testing utilities

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ 1.  Modular Design: Self-contained database access module
    ✅ 2.  Service Pattern: Factory function for instantiation
    ✅ 3.  Service Registry: Compatible with centralized registry
    ✅ 4.  Single Source of Truth: Database is authoritative
    ✅ 5.  Strict Async: 100% async/await for all I/O operations
    ✅ 6.  No Sync Fallbacks: Pure async implementation
    ✅ 7.  Per-Asset Monitoring: Health checks with detailed metrics
    ✅ 8.  No Duplicate Config: Single configuration source
    ✅ 9.  Integrated Rate Limiting: Connection pool limits
    ✅ 10. Separation of Concerns: Database logic isolated
    ✅ 11. Comprehensive Documentation: Full docstrings and examples
    ✅ 12. Method Singularity: Single implementation of each method
════════════════════════════════════════════════════════════════════════════

Usage Example:
    ```python
    from core.db.database_manager import AsyncDatabaseManager
    
    # Create and initialize database manager
    db = AsyncDatabaseManager(
        host='localhost',
        port=5432,
        database='ubec',
        schema='ubec_main',
        user='ubec_app',
        password='your_password'
    )
    
    await db.initialize()
    
    # Execute queries (supports both %s and $1 placeholders)
    results = await db.fetch_all(
        "SELECT * FROM accounts WHERE asset_code = %s",
        ('UBEC',)
    )
    
    # Fetch single row
    account = await db.fetch_one(
        "SELECT * FROM accounts WHERE id = $1",
        (account_id,)
    )
    
    # Execute INSERT/UPDATE/DELETE
    status = await db.execute(
        "INSERT INTO logs (message, timestamp) VALUES ($1, $2)",
        ('Test message', datetime.now())
    )
    
    # Transaction support
    async with db.transaction() as tx:
        await tx.execute("INSERT INTO ...", (...))
        await tx.execute("UPDATE ...", (...))
        # Auto-commits on success, rolls back on exception
    
    # Health check
    health = await db.health_check()
    if health['status'] == 'healthy':
        print("Database operational")
    
    # Test connection
    is_connected = await db.test_connection()
    
    # Cleanup
    await db.close()
    ```

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 1.4.0
Date: October 17, 2025
Changes:
    - Added test_connection() method for connectivity checks
    - Enhanced health_check() with comprehensive diagnostics
    - Improved error handling and logging
    - Added connection pool statistics
    - Full compliance with all 12 Design Principles
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple, Union
from contextlib import asynccontextmanager

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    logging.warning("asyncpg not available - install with: pip install asyncpg")


logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def convert_query_placeholders(query: str) -> str:
    """
    Convert psycopg2-style placeholders (%s) to asyncpg-style ($1, $2, etc.).
    
    Implements Principle #12 (Method Singularity): Single placeholder
    conversion implementation for entire system.
    
    Args:
        query: SQL query with %s placeholders
        
    Returns:
        Query with $1, $2, etc. placeholders
        
    Example:
        >>> convert_query_placeholders("SELECT * FROM t WHERE a=%s AND b=%s")
        'SELECT * FROM t WHERE a=$1 AND b=$2'
    """
    if '%s' not in query:
        return query
    
    # Replace %s with incrementing $n
    counter = 1
    def replace_placeholder(match):
        nonlocal counter
        result = f'${counter}'
        counter += 1
        return result
    
    converted = re.sub(r'%s', replace_placeholder, query)
    return converted


def convert_iso8601_to_datetime(value: str) -> datetime:
    """
    Convert ISO 8601 datetime string to Python datetime object.
    
    Handles various ISO 8601 formats:
    - 2024-08-14T11:09:45Z
    - 2024-08-14T11:09:45+00:00
    - 2024-08-14T11:09:45.123456Z
    
    Args:
        value: ISO 8601 formatted datetime string
        
    Returns:
        Python datetime object
        
    Raises:
        ValueError: If string cannot be parsed as datetime
        
    Example:
        >>> dt = convert_iso8601_to_datetime("2024-08-14T11:09:45Z")
        >>> isinstance(dt, datetime)
        True
    """
    try:
        # Handle 'Z' timezone indicator (UTC)
        if value.endswith('Z'):
            value = value[:-1] + '+00:00'
        
        # Parse with timezone support
        return datetime.fromisoformat(value)
    except Exception as e:
        logger.warning(f"Failed to parse datetime string '{value}': {e}")
        raise ValueError(f"Invalid ISO 8601 datetime string: {value}")


def _is_iso8601_datetime(value: str) -> bool:
    """
    Check if a string looks like an ISO 8601 datetime.
    
    Args:
        value: String to check
        
    Returns:
        True if string matches ISO 8601 datetime pattern
        
    Example:
        >>> _is_iso8601_datetime("2024-08-14T11:09:45Z")
        True
        >>> _is_iso8601_datetime("hello")
        False
    """
    # Pattern: YYYY-MM-DDTHH:MM:SS with optional microseconds and timezone
    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
    return bool(re.match(iso_pattern, value))


def convert_params_for_asyncpg(params: Union[Tuple, List, Dict]) -> Union[Tuple, List, Dict]:
    """
    Recursively convert parameter values for asyncpg compatibility.
    
    Converts ISO 8601 datetime strings to Python datetime objects.
    asyncpg requires datetime objects, not ISO strings.
    
    Implements Principle #12 (Method Singularity): Single parameter
    conversion implementation for entire system.
    
    Args:
        params: Query parameters (tuple, list, or dict)
        
    Returns:
        Converted parameters with datetime objects replacing ISO strings
        
    Example:
        >>> params = ("UBEC", "2024-08-14T11:09:45Z")
        >>> converted = convert_params_for_asyncpg(params)
        >>> isinstance(converted[1], datetime)
        True
    """
    if isinstance(params, dict):
        return {
            key: convert_params_for_asyncpg(value) 
            if isinstance(value, (dict, list, tuple)) 
            else convert_iso8601_to_datetime(value) 
            if isinstance(value, str) and _is_iso8601_datetime(value)
            else value
            for key, value in params.items()
        }
    elif isinstance(params, (list, tuple)):
        converted = [
            convert_params_for_asyncpg(item)
            if isinstance(item, (dict, list, tuple))
            else convert_iso8601_to_datetime(item)
            if isinstance(item, str) and _is_iso8601_datetime(item)
            else item
            for item in params
        ]
        # Return same type as input (preserves tuple vs list)
        return type(params)(converted)
    else:
        return params


# ============================================================================
# ASYNC DATABASE MANAGER
# ============================================================================

class AsyncDatabaseManager:
    """
    Async PostgreSQL database manager with connection pooling and health monitoring.
    
    This class provides the primary database interface for all UBEC services,
    implementing all 12 Design Principles.
    
    Features:
    - Connection pooling for efficient resource usage
    - Automatic schema path management
    - Query placeholder conversion (%s → $1)
    - ISO 8601 datetime conversion
    - Transaction support with context managers
    - Comprehensive health monitoring
    - Connection testing utilities
    
    Attributes:
        host (str): Database server host
        port (int): Database server port
        database (str): Database name
        schema (str): Default schema for queries
        user (str): Database user
        min_pool_size (int): Minimum connections in pool
        max_pool_size (int): Maximum connections in pool
        
    Example:
        >>> db = AsyncDatabaseManager(
        ...     host='localhost',
        ...     database='ubec',
        ...     schema='ubec_main'
        ... )
        >>> await db.initialize()
        >>> results = await db.fetch_all("SELECT * FROM accounts", ())
        >>> await db.close()
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 5432,
        database: str = 'ubec',
        schema: str = 'ubec_main',
        user: str = 'ubec_app',
        password: str = '',
        min_pool_size: int = 2,
        max_pool_size: int = 10
    ):
        """
        Initialize database manager.
        
        Does NOT establish connection - call initialize() after creation.
        
        Args:
            host: Database host (default: 'localhost')
            port: Database port (default: 5432)
            database: Database name (default: 'ubec')
            schema: Schema name (default: 'ubec_main')
            user: Database user (default: 'ubec_app')
            password: Database password (default: '')
            min_pool_size: Minimum connections in pool (default: 2)
            max_pool_size: Maximum connections in pool (default: 10)
            
        Raises:
            ImportError: If asyncpg is not installed
        """
        if not ASYNCPG_AVAILABLE:
            raise ImportError(
                "asyncpg is required for AsyncDatabaseManager. "
                "Install with: pip install asyncpg"
            )
        
        self.host = host
        self.port = port
        self.database = database
        self.schema = schema
        self.user = user
        self.password = password
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        
        self._pool: Optional[asyncpg.Pool] = None
        self._initialized = False
        
        logger.info(
            f"AsyncDatabaseManager created for {database}.{schema} "
            f"(pool: {min_pool_size}-{max_pool_size})"
        )
    
    async def initialize(self) -> None:
        """
        Initialize connection pool.
        
        Must be called before using any database operations.
        This method is idempotent - calling it multiple times is safe.
        
        Raises:
            Exception: If connection pool creation fails
            
        Example:
            >>> db = AsyncDatabaseManager()
            >>> await db.initialize()
            >>> # Now ready to use
        """
        if self._initialized:
            logger.warning("Database already initialized")
            return
        
        try:
            # Create connection pool
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=self.min_pool_size,
                max_size=self.max_pool_size,
                command_timeout=60
            )
            
            # Test connection and set schema
            async with self._pool.acquire() as conn:
                await conn.execute(f'SET search_path TO {self.schema}')
                result = await conn.fetchval('SELECT 1')
                if result != 1:
                    raise Exception("Database connection test failed")
            
            self._initialized = True
            logger.info(
                f"Database pool initialized: {self.database}.{self.schema} "
                f"({self.min_pool_size}-{self.max_pool_size} connections)"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self) -> None:
        """
        Close all database connections and release resources.
        
        Should be called during application shutdown.
        After calling this method, initialize() must be called again
        before using the database.
        
        Example:
            >>> db = AsyncDatabaseManager()
            >>> await db.initialize()
            >>> # ... use database ...
            >>> await db.close()
        """
        if self._pool:
            await self._pool.close()
            self._initialized = False
            logger.info("Database pool closed")
    
    async def test_connection(self) -> bool:
        """
        Test if database connection is working.
        
        Performs a simple query to verify database connectivity.
        This method is useful for health checks and diagnostics.
        
        Returns:
            True if connection is working, False otherwise
            
        Example:
            >>> db = AsyncDatabaseManager()
            >>> await db.initialize()
            >>> if await db.test_connection():
            ...     print("Database is accessible")
        """
        try:
            if not self._initialized:
                return False
            
            # Simple query to test connection
            result = await self.fetch_one("SELECT 1 as test", ())
            return result is not None and result.get('test') == 1
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on database connection.
        
        Implements Principle #7 (Per-Asset Monitoring): Provides detailed
        health metrics for monitoring and alerting.
        
        Returns:
            Dictionary with health check results:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'message': str,
                'timestamp': str (ISO format),
                'details': {
                    'initialized': bool,
                    'pool_size': int,
                    'pool_max': int,
                    'connection_test': bool,
                    'response_time_ms': float,
                    'database': str,
                    'schema': str
                }
            }
            
        Example:
            >>> db = AsyncDatabaseManager()
            >>> await db.initialize()
            >>> health = await db.health_check()
            >>> print(f"Status: {health['status']}")
            >>> print(f"Response time: {health['details']['response_time_ms']}ms")
        """
        start_time = datetime.now()
        
        health_info = {
            'status': 'unknown',
            'message': '',
            'timestamp': start_time.isoformat(),
            'details': {
                'initialized': self._initialized,
                'pool_size': 0,
                'pool_max': self.max_pool_size,
                'connection_test': False,
                'response_time_ms': 0.0,
                'database': self.database,
                'schema': self.schema,
                'host': self.host,
                'port': self.port
            }
        }
        
        try:
            # Check if initialized
            if not self._initialized:
                health_info['status'] = 'unhealthy'
                health_info['message'] = 'Database not initialized'
                return health_info
            
            # Check pool status
            if self._pool:
                health_info['details']['pool_size'] = self._pool.get_size()
                health_info['details']['pool_idle'] = self._pool.get_idle_size()
                health_info['details']['pool_used'] = (
                    self._pool.get_size() - self._pool.get_idle_size()
                )
            
            # Test connection with simple query
            test_result = await self.fetch_one("SELECT 1 as test", ())
            
            # Calculate response time
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            health_info['details']['response_time_ms'] = round(response_time, 2)
            
            # Evaluate health status based on test and response time
            if test_result and test_result.get('test') == 1:
                health_info['details']['connection_test'] = True
                
                if response_time < 100:
                    health_info['status'] = 'healthy'
                    health_info['message'] = (
                        f'Database responsive ({response_time:.1f}ms)'
                    )
                elif response_time < 500:
                    health_info['status'] = 'degraded'
                    health_info['message'] = (
                        f'Database slow ({response_time:.1f}ms)'
                    )
                else:
                    health_info['status'] = 'degraded'
                    health_info['message'] = (
                        f'Database very slow ({response_time:.1f}ms)'
                    )
            else:
                health_info['status'] = 'unhealthy'
                health_info['message'] = 'Connection test query failed'
        
        except Exception as e:
            health_info['status'] = 'unhealthy'
            health_info['message'] = f'Health check failed: {str(e)}'
            logger.error(f"Database health check failed: {e}")
        
        return health_info
    
    @asynccontextmanager
    async def _get_connection(self):
        """
        Get a connection from the pool (internal context manager).
        
        Automatically sets the schema path for the connection.
        This is an internal method - use fetch_all, fetch_one, execute instead.
        
        Yields:
            asyncpg.Connection: Database connection
            
        Raises:
            RuntimeError: If database not initialized
        """
        if not self._initialized:
            raise RuntimeError(
                "Database not initialized. Call initialize() first."
            )
        
        async with self._pool.acquire() as conn:
            # Set schema for this connection
            await conn.execute(f'SET search_path TO {self.schema}')
            yield conn
    
    async def fetch_all(
        self,
        query: str,
        params: Tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows from a query.
        
        Implements Principle #5 (Strict Async): Pure async operation.
        Supports both %s and $1 style placeholders.
        Automatically converts ISO 8601 datetime strings to datetime objects.
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple (MUST be tuple, even if empty)
            
        Returns:
            List of dictionaries, one per row
            
        Raises:
            Exception: If query execution fails
            
        Example:
            >>> results = await db.fetch_all(
            ...     "SELECT * FROM accounts WHERE asset_code = %s",
            ...     ('UBEC',)
            ... )
            >>> for row in results:
            ...     print(row['account_id'])
        """
        try:
            # Convert placeholders if needed
            query = convert_query_placeholders(query)
            
            # Convert datetime strings to datetime objects
            params = convert_params_for_asyncpg(params)
            
            async with self._get_connection() as conn:
                rows = await conn.fetch(query, *params)
                # Convert Record objects to dictionaries
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error executing fetch_all: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    async def fetch_one(
        self,
        query: str,
        params: Tuple = ()
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row from a query.
        
        Implements Principle #5 (Strict Async): Pure async operation.
        Supports both %s and $1 style placeholders.
        Automatically converts ISO 8601 datetime strings to datetime objects.
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple (MUST be tuple, even if empty)
            
        Returns:
            Dictionary representing the row, or None if no results
            
        Raises:
            Exception: If query execution fails
            
        Example:
            >>> account = await db.fetch_one(
            ...     "SELECT * FROM accounts WHERE id = $1",
            ...     (account_id,)
            ... )
            >>> if account:
            ...     print(account['balance'])
        """
        try:
            # Convert placeholders if needed
            query = convert_query_placeholders(query)
            
            # Convert datetime strings to datetime objects
            params = convert_params_for_asyncpg(params)
            
            async with self._get_connection() as conn:
                row = await conn.fetchrow(query, *params)
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Error executing fetch_one: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    async def execute(
        self,
        query: str,
        params: Tuple = ()
    ) -> str:
        """
        Execute a query that doesn't return rows (INSERT, UPDATE, DELETE).
        
        Implements Principle #5 (Strict Async): Pure async operation.
        Supports both %s and $1 style placeholders.
        Automatically converts ISO 8601 datetime strings to datetime objects.
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple (MUST be tuple, even if empty)
            
        Returns:
            Status string from the database (e.g., "INSERT 0 1")
            
        Raises:
            Exception: If query execution fails
            
        Example:
            >>> status = await db.execute(
            ...     "INSERT INTO logs (message, timestamp) VALUES ($1, $2)",
            ...     ('Test message', datetime.now())
            ... )
            >>> print(status)  # "INSERT 0 1"
        """
        try:
            # Convert placeholders if needed
            query = convert_query_placeholders(query)
            
            # Convert datetime strings to datetime objects
            params = convert_params_for_asyncpg(params)
            
            async with self._get_connection() as conn:
                status = await conn.execute(query, *params)
                return status
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    async def execute_many(
        self,
        query: str,
        params_list: List[Tuple]
    ) -> None:
        """
        Execute a query multiple times with different parameters.
        
        Efficient for bulk inserts/updates as it uses a single connection.
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params_list: List of parameter tuples
            
        Raises:
            Exception: If query execution fails
            
        Example:
            >>> await db.execute_many(
            ...     "INSERT INTO logs (message) VALUES ($1)",
            ...     [('Message 1',), ('Message 2',), ('Message 3',)]
            ... )
        """
        try:
            # Convert placeholders if needed
            query = convert_query_placeholders(query)
            
            # Convert datetime strings in all parameter sets
            converted_params = [
                convert_params_for_asyncpg(params) 
                for params in params_list
            ]
            
            async with self._get_connection() as conn:
                await conn.executemany(query, converted_params)
                
        except Exception as e:
            logger.error(f"Error executing execute_many: {e}")
            logger.error(f"Query: {query}")
            raise
    
    async def execute_query(
        self,
        query: str,
        params: Tuple = (),
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Any:
        """
        Generic query execution method (for compatibility).
        
        Provides a unified interface for different query types.
        This method is useful for protocols that need a single entry point.
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple
            fetch_one: If True, return single row
            fetch_all: If True, return all rows
            
        Returns:
            Query results based on fetch flags:
            - fetch_one=True: Single row dict or None
            - fetch_all=True: List of row dicts
            - Otherwise: Status string
            
        Example:
            >>> # Fetch one row
            >>> row = await db.execute_query(
            ...     "SELECT * FROM accounts WHERE id = $1",
            ...     (1,),
            ...     fetch_one=True
            ... )
            
            >>> # Fetch all rows
            >>> rows = await db.execute_query(
            ...     "SELECT * FROM accounts",
            ...     (),
            ...     fetch_all=True
            ... )
            
            >>> # Execute non-query
            >>> status = await db.execute_query(
            ...     "INSERT INTO logs (msg) VALUES ($1)",
            ...     ('Test',)
            ... )
        """
        if fetch_one:
            return await self.fetch_one(query, params)
        elif fetch_all:
            return await self.fetch_all(query, params)
        else:
            return await self.execute(query, params)
    
    @asynccontextmanager
    async def transaction(self):
        """
        Context manager for database transactions.
        
        Automatically commits on success or rolls back on exception.
        Provides a TransactionManager instance with fetch/execute methods.
        
        Yields:
            TransactionManager: Transaction manager for this transaction
            
        Example:
            >>> async with db.transaction() as tx:
            ...     await tx.execute(
            ...         "INSERT INTO logs (message) VALUES ($1)",
            ...         ('Starting transaction',)
            ...     )
            ...     await tx.execute(
            ...         "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
            ...         (100, account_id)
            ...     )
            ...     # Auto-commits here if no exception
            
        Raises:
            RuntimeError: If database not initialized
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            await conn.execute(f'SET search_path TO {self.schema}')
            async with conn.transaction():
                # Create a temporary database manager for this transaction
                temp_manager = TransactionManager(conn, self.schema)
                yield temp_manager


# ============================================================================
# TRANSACTION MANAGER
# ============================================================================

class TransactionManager:
    """
    Helper class for transaction context.
    
    Provides the same fetch_all, fetch_one, and execute methods as
    AsyncDatabaseManager but within a transaction context.
    
    This class should not be instantiated directly - use
    AsyncDatabaseManager.transaction() instead.
    """
    
    def __init__(self, conn, schema: str):
        """
        Initialize transaction manager.
        
        Args:
            conn: asyncpg connection
            schema: Database schema
        """
        self.conn = conn
        self.schema = schema
    
    async def fetch_all(
        self, 
        query: str, 
        params: Tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows within transaction.
        
        Args:
            query: SQL query
            params: Query parameters as tuple
            
        Returns:
            List of dictionaries
        """
        query = convert_query_placeholders(query)
        params = convert_params_for_asyncpg(params)
        rows = await self.conn.fetch(query, *params)
        return [dict(row) for row in rows]
    
    async def fetch_one(
        self, 
        query: str, 
        params: Tuple = ()
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch single row within transaction.
        
        Args:
            query: SQL query
            params: Query parameters as tuple
            
        Returns:
            Dictionary or None
        """
        query = convert_query_placeholders(query)
        params = convert_params_for_asyncpg(params)
        row = await self.conn.fetchrow(query, *params)
        return dict(row) if row else None
    
    async def execute(
        self, 
        query: str, 
        params: Tuple = ()
    ) -> str:
        """
        Execute query within transaction.
        
        Args:
            query: SQL query
            params: Query parameters as tuple
            
        Returns:
            Status string
        """
        query = convert_query_placeholders(query)
        params = convert_params_for_asyncpg(params)
        return await self.conn.execute(query, *params)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_database_manager_from_env() -> AsyncDatabaseManager:
    """
    Create database manager from environment variables.
    
    Implements Principle #8 (No Duplicate Config): Centralized configuration
    through environment variables.
    
    Expected environment variables:
        UBEC_DB_HOST (default: 'localhost')
        UBEC_DB_PORT (default: '5432')
        UBEC_DB_NAME (default: 'ubec')
        UBEC_DB_SCHEMA (default: 'ubec_main')
        UBEC_DB_USER (default: 'ubec_app')
        UBEC_DB_PASSWORD (default: '')
        UBEC_DB_MIN_POOL (default: '2')
        UBEC_DB_MAX_POOL (default: '10')
    
    Returns:
        AsyncDatabaseManager instance (not yet initialized)
        
    Example:
        >>> import os
        >>> os.environ['UBEC_DB_HOST'] = 'db.example.com'
        >>> os.environ['UBEC_DB_PASSWORD'] = 'secret'
        >>> 
        >>> db = create_database_manager_from_env()
        >>> await db.initialize()
    """
    import os
    
    return AsyncDatabaseManager(
        host=os.getenv('UBEC_DB_HOST', 'localhost'),
        port=int(os.getenv('UBEC_DB_PORT', '5432')),
        database=os.getenv('UBEC_DB_NAME', 'ubec'),
        schema=os.getenv('UBEC_DB_SCHEMA', 'ubec_main'),
        user=os.getenv('UBEC_DB_USER', 'ubec_app'),
        password=os.getenv('UBEC_DB_PASSWORD', ''),
        min_pool_size=int(os.getenv('UBEC_DB_MIN_POOL', '2')),
        max_pool_size=int(os.getenv('UBEC_DB_MAX_POOL', '10'))
    )


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'AsyncDatabaseManager',
    'TransactionManager',
    'create_database_manager_from_env',
    'convert_query_placeholders',
    'convert_iso8601_to_datetime',
    'convert_params_for_asyncpg'
]
