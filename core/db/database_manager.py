# core/db/database_manager.py
"""
Async Database Manager for UBEC Protocol
ALL database operations are async

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import asyncpg
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from config import config, get_logger

logger = get_logger(__name__)


class AsyncDatabaseManager:
    """
    Async database connection manager
    Provides connection pooling and query execution
    """
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.config = config
    
    async def initialize(self) -> None:
        """Initialize connection pool"""
        if self.pool is not None:
            return
        
        logger.info("Initializing database connection pool")
        
        self.pool = await asyncpg.create_pool(
            dsn=self.config.DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        logger.info("Database pool initialized")
    
    async def close(self) -> None:
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def connection(self):
        """Get database connection from pool"""
        if self.pool is None:
            await self.initialize()
        
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args) -> str:
        """Execute INSERT/UPDATE/DELETE query"""
        async with self.connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> List[Dict]:
        """Fetch multiple rows"""
        async with self.connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Fetch single row"""
        async with self.connection() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetchval(self, query: str, *args) -> Any:
        """Fetch single value"""
        async with self.connection() as conn:
            return await conn.fetchval(query, *args)


# Global instance
db_manager = AsyncDatabaseManager()
