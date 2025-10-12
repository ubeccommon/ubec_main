#!/usr/bin/env python3
"""
Async Database Manager for UBEC Protocol
=========================================
Provides async database access using asyncpg.

This module implements:
- Async connection pooling
- Query execution with async/await
- Transaction management
- Error handling and retries
- Automatic parameter placeholder conversion

Design Principles Compliance:
- ✅ Strict Async: All operations use async/await
- ✅ Single Source of Truth: Database is authoritative
- ✅ No Sync Fallbacks: Pure async implementation

Usage:
    from core.db.database_manager import AsyncDatabaseManager
    
    db = AsyncDatabaseManager(
        host='localhost',
        port=5432,
        database='ubec',
        schema='ubec_main',
        user='ubec_app',
        password='your_password'
    )
    
    # Initialize connection pool
    await db.initialize()
    
    # Execute query (supports both %s and $1 placeholders)
    results = await db.fetch_all(
        "SELECT * FROM accounts WHERE asset_code = %s",
        ('UBEC',)
    )
    
    # Close connections
    await db.close()

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Version: 1.2.0
Date: October 11, 2025
Changes:
    - Added automatic ISO 8601 datetime string to Python datetime conversion
    - Ensures asyncpg compatibility by converting datetime strings transparently
    - Implements Method Singularity principle: one conversion method system-wide
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


def convert_query_placeholders(query: str) -> str:
    """
    Convert psycopg2-style placeholders (%s) to asyncpg-style ($1, $2, etc.).
    
    Args:
        query: SQL query with %s placeholders
        
    Returns:
        Query with $1, $2, etc. placeholders
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
    
    Handles formats:
    - 2024-08-14T11:09:45Z
    - 2024-08-14T11:09:45+00:00
    - 2024-08-14T11:09:45.123Z
    
    Args:
        value: ISO 8601 formatted datetime string
        
    Returns:
        Python datetime object
    """
    try:
        # Handle 'Z' timezone indicator
        if value.endswith('Z'):
            value = value[:-1] + '+00:00'
        
        # Try parsing with timezone
        return datetime.fromisoformat(value)
    except Exception as e:
        logger.warning(f"Failed to parse datetime string '{value}': {e}")
        raise


def convert_params_for_asyncpg(params: Union[Tuple, List, Dict]) -> Union[Tuple, List, Dict]:
    """
    Recursively convert parameter values for asyncpg compatibility.
    
    Converts ISO 8601 datetime strings to Python datetime objects.
    asyncpg expects datetime objects, not strings.
    
    Args:
        params: Query parameters (tuple, list, or dict)
        
    Returns:
        Converted parameters with datetime objects
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
        # Return same type as input
        return type(params)(converted)
    else:
        return params


def _is_iso8601_datetime(value: str) -> bool:
    """
    Check if a string looks like an ISO 8601 datetime.
    
    Args:
        value: String to check
        
    Returns:
        True if string matches ISO 8601 datetime pattern
    """
    # Pattern: YYYY-MM-DDTHH:MM:SS with optional microseconds and timezone
    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
    return bool(re.match(iso_pattern, value))


class AsyncDatabaseManager:
    """
    Async PostgreSQL database manager.
    
    Provides connection pooling and query execution for UBEC protocols.
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
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            schema: Schema name
            user: Database user
            password: Database password
            min_pool_size: Minimum connections in pool
            max_pool_size: Maximum connections in pool
        """
        if not ASYNCPG_AVAILABLE:
            raise ImportError("asyncpg is required. Install with: pip install asyncpg")
        
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
        
        logger.info(f"AsyncDatabaseManager created for {database}.{schema}")
    
    async def initialize(self) -> None:
        """
        Initialize connection pool.
        Must be called before using the database.
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
            logger.info(f"Database pool initialized: {self.database}.{self.schema}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self) -> None:
        """Close all database connections"""
        if self._pool:
            await self._pool.close()
            self._initialized = False
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def _get_connection(self):
        """Get a connection from the pool (context manager)"""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
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
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple
            
        Returns:
            List of dictionaries, one per row
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
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple
            
        Returns:
            Dictionary representing the row, or None if no results
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
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters as tuple
            
        Returns:
            Status string from the database
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
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params_list: List of parameter tuples
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
        Generic query execution (for compatibility with Fire protocol).
        
        Args:
            query: SQL query (supports both %s and $1 placeholders)
            params: Query parameters
            fetch_one: If True, return single row
            fetch_all: If True, return all rows
            
        Returns:
            Query results based on fetch flags
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
        Context manager for transactions.
        
        Usage:
            async with db.transaction():
                await db.execute("INSERT ...", (...))
                await db.execute("UPDATE ...", (...))
            # Auto-commits on success, rolls back on exception
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized")
        
        async with self._pool.acquire() as conn:
            await conn.execute(f'SET search_path TO {self.schema}')
            async with conn.transaction():
                # Create a temporary database manager for this transaction
                temp_manager = TransactionManager(conn, self.schema)
                yield temp_manager


class TransactionManager:
    """Helper class for transaction context"""
    
    def __init__(self, conn, schema: str):
        self.conn = conn
        self.schema = schema
    
    async def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all within transaction"""
        query = convert_query_placeholders(query)
        params = convert_params_for_asyncpg(params)
        rows = await self.conn.fetch(query, *params)
        return [dict(row) for row in rows]
    
    async def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch one within transaction"""
        query = convert_query_placeholders(query)
        params = convert_params_for_asyncpg(params)
        row = await self.conn.fetchrow(query, *params)
        return dict(row) if row else None
    
    async def execute(self, query: str, params: Tuple = ()) -> str:
        """Execute within transaction"""
        query = convert_query_placeholders(query)
        params = convert_params_for_asyncpg(params)
        return await self.conn.execute(query, *params)


# ==================== CONFIGURATION HELPER ====================

def create_database_manager_from_env() -> AsyncDatabaseManager:
    """
    Create database manager from environment variables.
    
    Expects:
        UBEC_DB_HOST
        UBEC_DB_PORT
        UBEC_DB_NAME
        UBEC_DB_SCHEMA
        UBEC_DB_USER
        UBEC_DB_PASSWORD
    """
    import os
    
    return AsyncDatabaseManager(
        host=os.getenv('UBEC_DB_HOST', 'localhost'),
        port=int(os.getenv('UBEC_DB_PORT', '5432')),
        database=os.getenv('UBEC_DB_NAME', 'ubec'),
        schema=os.getenv('UBEC_DB_SCHEMA', 'ubec_main'),
        user=os.getenv('UBEC_DB_USER', 'ubec_app'),
        password=os.getenv('UBEC_DB_PASSWORD', '')
    )


# ==================== MODULE EXPORTS ====================

__all__ = [
    'AsyncDatabaseManager',
    'create_database_manager_from_env',
    'convert_query_placeholders',
    'convert_iso8601_to_datetime',
    'convert_params_for_asyncpg'
]
