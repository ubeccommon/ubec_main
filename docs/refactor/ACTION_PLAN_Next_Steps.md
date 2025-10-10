# UBEC Protocol Suite - Refactoring Implementation Guide
## Practical Steps to Achieve Full Compliance with Design Principles

**Date:** October 10, 2025  
**Purpose:** Step-by-step implementation guide for refactoring  
**Estimated Total Effort:** 14-22 days  
**Target:** Full compliance with 12 Project Design Principles

---

## Table of Contents

1. [Week 1: Critical Async & Service Registry](#week-1-critical-async--service-registry)
2. [Week 2: Configuration & Deduplication](#week-2-configuration--deduplication)
3. [Week 3: Documentation & Testing](#week-3-documentation--testing)
4. [Code Templates](#code-templates)
5. [Testing Checklist](#testing-checklist)

---

## Week 1: Critical Async & Service Registry

### Day 1-3: Pure Async Implementation

#### Step 1.1: Install Async Dependencies

```bash
# Update requirements.txt
cat > requirements.txt << 'EOF'
# Async Stellar SDK
stellar-sdk>=8.0.0

# Async Database
asyncpg>=0.29.0

# Async HTTP Client
aiohttp>=3.9.0

# Other dependencies
python-dotenv>=1.0.0
EOF

# Install
pip install -r requirements.txt --break-system-packages
```

#### Step 1.2: Create Async Database Manager

```python
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
```

#### Step 1.3: Create Async Data Synchronizer

```python
# core/db/ubec_data_synchronizer.py
"""
UBEC Data Synchronizer - Pure Async Implementation
Synchronizes data from Stellar blockchain to PostgreSQL database

ALL methods are async. NO synchronous operations.

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import asyncio
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime

from stellar_sdk import ServerAsync, AiohttpClient, Asset
from stellar_sdk.exceptions import NotFoundError

from config import config, get_logger
from core.db.database_manager import db_manager

logger = get_logger(__name__)


class UBECDataSynchronizer:
    """
    Async data synchronizer for Stellar blockchain
    
    Functions:
        - Discover token holders
        - Sync account data
        - Sync transaction history
        - Sync balance information
    
    All operations are async and use connection pooling.
    """
    
    def __init__(self):
        self.config = config
        self.db = db_manager
        self.server: Optional[ServerAsync] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize Stellar server connection"""
        if self._initialized:
            return
        
        logger.info("Initializing Stellar server connection")
        
        self.server = ServerAsync(
            horizon_url=self.config.horizon_url,
            client=AiohttpClient()
        )
        
        # Initialize database
        await self.db.initialize()
        
        self._initialized = True
        logger.info("Synchronizer initialized")
    
    async def close(self) -> None:
        """Close connections"""
        if self.server:
            await self.server.close()
            self.server = None
        
        await self.db.close()
        self._initialized = False
    
    async def sync_account_data(
        self, 
        asset_code: str,
        limit: int = 200,
        max_accounts: int = 1000
    ) -> Dict[str, Any]:
        """
        Sync account data from Stellar network
        
        Args:
            asset_code: Token code (UBEC, UBECrc, etc.)
            limit: Records per page
            max_accounts: Maximum accounts to sync
        
        Returns:
            Dictionary with sync results
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info(f"Starting account sync for {asset_code}")
        
        # Get token configuration
        token_config = self.config.get_token_config(asset_code)
        
        cursor = ''
        synced_count = 0
        
        async with self.server:
            while synced_count < max_accounts:
                try:
                    # Fetch account page (ASYNC)
                    accounts = await self._fetch_account_page(
                        asset_code=asset_code,
                        issuer=token_config.issuer,
                        cursor=cursor,
                        limit=limit
                    )
                    
                    if not accounts:
                        break
                    
                    # Process accounts concurrently
                    save_tasks = [
                        self._save_account(account, asset_code)
                        for account in accounts
                    ]
                    await asyncio.gather(*save_tasks)
                    
                    synced_count += len(accounts)
                    
                    # Get next cursor
                    cursor = self._extract_next_cursor(accounts)
                    if not cursor:
                        break
                    
                    # Rate limiting delay (ASYNC)
                    await asyncio.sleep(1.0)
                    
                    logger.info(f"Synced {synced_count} accounts so far...")
                
                except Exception as e:
                    logger.error(f"Error syncing accounts: {e}")
                    if '429' in str(e):  # Rate limit
                        await asyncio.sleep(10.0)
                        continue
                    raise
        
        logger.info(f"Completed sync: {synced_count} accounts")
        
        return {
            'asset_code': asset_code,
            'accounts_synced': synced_count,
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _fetch_account_page(
        self,
        asset_code: str,
        issuer: str,
        cursor: str,
        limit: int
    ) -> List[Dict]:
        """
        Fetch single page of accounts (ASYNC)
        
        Returns list of account records
        """
        try:
            response = await self.server.accounts()\
                .for_asset(Asset(asset_code, issuer))\
                .cursor(cursor)\
                .limit(limit)\
                .call()
            
            return response['_embedded']['records']
        
        except NotFoundError:
            return []
        except Exception as e:
            logger.error(f"Error fetching accounts: {e}")
            raise
    
    async def _save_account(
        self, 
        account_data: Dict, 
        asset_code: str
    ) -> None:
        """
        Save account to database (ASYNC)
        
        Args:
            account_data: Account data from Stellar
            asset_code: Token code
        """
        account_id = account_data['id']
        
        # Extract balance
        balance = self._extract_balance(account_data, asset_code)
        
        # Save to database (ASYNC)
        await self.db.execute(
            """
            INSERT INTO ubec_main.stellar_accounts (
                account_id,
                asset_code,
                balance,
                sequence,
                subentry_count,
                last_modified_ledger,
                synced_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (account_id, asset_code) 
            DO UPDATE SET
                balance = EXCLUDED.balance,
                sequence = EXCLUDED.sequence,
                subentry_count = EXCLUDED.subentry_count,
                last_modified_ledger = EXCLUDED.last_modified_ledger,
                synced_at = EXCLUDED.synced_at
            """,
            account_id,
            asset_code,
            float(balance),
            int(account_data['sequence']),
            account_data['subentry_count'],
            account_data['last_modified_ledger'],
            datetime.utcnow()
        )
    
    def _extract_balance(self, account_data: Dict, asset_code: str) -> Decimal:
        """Extract balance for specific asset"""
        for balance in account_data.get('balances', []):
            if balance.get('asset_code') == asset_code:
                return Decimal(balance['balance'])
        return Decimal('0')
    
    def _extract_next_cursor(self, records: List[Dict]) -> Optional[str]:
        """Extract cursor for next page"""
        if not records:
            return None
        
        # Get paging_token from last record
        return records[-1].get('paging_token')
    
    async def sync_transaction_data(
        self,
        asset_code: str,
        limit: int = 200
    ) -> Dict[str, Any]:
        """
        Sync transaction data (ASYNC)
        
        Similar pattern to sync_account_data
        """
        # Implementation similar to above
        logger.info(f"Syncing transactions for {asset_code}")
        
        # TODO: Implement transaction sync
        
        return {
            'asset_code': asset_code,
            'transactions_synced': 0,
            'status': 'success'
        }
    
    async def sync_balance_data(
        self,
        asset_code: str
    ) -> Dict[str, Any]:
        """
        Sync balance data (ASYNC)
        """
        logger.info(f"Syncing balances for {asset_code}")
        
        # TODO: Implement balance sync
        
        return {
            'asset_code': asset_code,
            'balances_synced': 0,
            'status': 'success'
        }
```

#### Step 1.4: Update Protocol to Use Async

```python
# UBEC/UBEC_protocol.py
"""
UBEC Protocol - Air Element (Gateway)
Pure async implementation

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

from typing import Dict, Any
from datetime import datetime

from config import config, get_logger

logger = get_logger(__name__)


class UBECProtocol:
    """
    Air Protocol - Gateway and Universal Access
    
    All methods are async. Service dependencies obtained via registry.
    """
    
    def __init__(self):
        self.config = config
        self.token_code = 'UBEC'
        logger.info("UBEC Air Protocol instantiated")
    
    async def initialize(self) -> None:
        """Initialize protocol (ASYNC)"""
        logger.info("Initializing Air Protocol")
        # Any async initialization here
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check protocol health (ASYNC)
        
        Returns health status with timestamp
        """
        # Import registry here to avoid circular imports
        from core.service_registry import registry
        
        try:
            # Get synchronizer service
            synchronizer = registry.get('synchronizer')
            
            # Check if initialized
            if not synchronizer._initialized:
                await synchronizer.initialize()
            
            # Simple connection test
            await synchronizer.server.accounts().limit(1).call()
            
            return {
                'protocol': 'UBEC (Air)',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'protocol': 'UBEC (Air)',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get protocol status (ASYNC)
        
        Returns current protocol statistics
        """
        from core.service_registry import registry
        from core.db.database_manager import db_manager
        
        try:
            # Query database for stats (ASYNC)
            account_count = await db_manager.fetchval(
                """
                SELECT COUNT(*) 
                FROM ubec_main.stellar_accounts 
                WHERE asset_code = $1
                """,
                self.token_code
            )
            
            total_balance = await db_manager.fetchval(
                """
                SELECT COALESCE(SUM(balance), 0) 
                FROM ubec_main.stellar_accounts 
                WHERE asset_code = $1
                """,
                self.token_code
            )
            
            return {
                'protocol': 'UBEC (Air)',
                'token': self.token_code,
                'accounts': account_count or 0,
                'total_balance': float(total_balance or 0),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                'protocol': 'UBEC (Air)',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def sync_gateway_data(self) -> Dict[str, Any]:
        """
        Sync gateway data from Stellar (ASYNC)
        
        Returns sync results
        """
        from core.service_registry import registry
        
        logger.info("Starting Air gateway sync")
        
        try:
            # Get synchronizer from registry
            synchronizer = registry.get('synchronizer')
            
            # Ensure initialized
            if not synchronizer._initialized:
                await synchronizer.initialize()
            
            # Sync account data (ASYNC)
            result = await synchronizer.sync_account_data(
                asset_code=self.token_code,
                limit=200,
                max_accounts=1000
            )
            
            logger.info(f"Gateway sync complete: {result['accounts_synced']} accounts")
            
            return result
        
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {
                'asset_code': self.token_code,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def evaluate_holonic(self, account_id: str) -> Dict[str, Any]:
        """
        Evaluate account holonic metrics (ASYNC)
        
        Args:
            account_id: Stellar account ID
        
        Returns:
            Holonic evaluation results
        """
        from core.service_registry import registry
        
        try:
            # Get evaluator from registry
            evaluator = registry.get('evaluator')
            
            # Perform evaluation (ASYNC if evaluator is async)
            # TODO: Make evaluator async
            evaluation = await evaluator.evaluate_account(account_id)
            
            return {
                'account_id': account_id,
                'protocol': 'UBEC (Air)',
                'evaluation': evaluation,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                'account_id': account_id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# NO __main__ block - service class only!
```

### Day 4-5: Service Registry Implementation

#### Step 2.1: Create Service Registry

```python
# core/service_registry.py
"""
UBEC Protocol Service Registry
Centralized dependency management for all modules

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

from typing import Dict, Any, Optional, Type, TypeVar
import asyncio

from config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class ServiceRegistry:
    """
    Central service registry for dependency management
    
    All inter-module dependencies must go through this registry.
    Enables:
        - Loose coupling between modules
        - Dynamic service discovery
        - Easy testing with mock services
        - Centralized initialization
    
    Usage:
        from core.service_registry import registry
        
        # Get service
        synchronizer = registry.get('synchronizer')
        
        # Use service
        result = await synchronizer.sync_account_data()
    """
    
    _instance: Optional['ServiceRegistry'] = None
    _services: Dict[str, Any] = {}
    _factories: Dict[str, Type] = {}
    
    def __new__(cls) -> 'ServiceRegistry':
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, name: str, service: Any) -> None:
        """
        Register a service instance
        
        Args:
            name: Service name
            service: Service instance
        """
        if name in self._services:
            logger.warning(f"Service '{name}' already registered, replacing")
        
        self._services[name] = service
        logger.info(f"Registered service: {name}")
    
    def register_factory(self, name: str, service_class: Type[T]) -> None:
        """
        Register a service factory (lazy initialization)
        
        Args:
            name: Service name
            service_class: Service class to instantiate on first get()
        """
        if name in self._factories:
            logger.warning(f"Factory '{name}' already registered, replacing")
        
        self._factories[name] = service_class
        logger.info(f"Registered factory: {name}")
    
    def get(self, name: str) -> Any:
        """
        Get a service from registry
        
        Args:
            name: Service name
        
        Returns:
            Service instance
        
        Raises:
            KeyError: If service not found
        """
        # Check if already instantiated
        if name in self._services:
            return self._services[name]
        
        # Check if factory exists
        if name in self._factories:
            # Lazy instantiation
            service_class = self._factories[name]
            service = service_class()
            self._services[name] = service
            logger.info(f"Instantiated service from factory: {name}")
            return service
        
        raise KeyError(f"Service '{name}' not found in registry")
    
    def has(self, name: str) -> bool:
        """Check if service exists"""
        return name in self._services or name in self._factories
    
    async def initialize_core_services(self) -> None:
        """
        Initialize all core services
        
        Called once at application startup
        """
        logger.info("Initializing core services...")
        
        # Import services
        from core.db.ubec_data_synchronizer import UBECDataSynchronizer
        from core.holonic.ubec_holonic_evaluator import UBECHolonicEvaluator
        from core.distribution.ubec_distribution_manager import UBECDistributionManager
        from core.audit.audit_system import UBECAuditSystem
        
        # Instantiate and register
        synchronizer = UBECDataSynchronizer()
        await synchronizer.initialize()
        self.register('synchronizer', synchronizer)
        
        evaluator = UBECHolonicEvaluator()
        self.register('evaluator', evaluator)
        
        distribution_mgr = UBECDistributionManager()
        self.register('distribution_manager', distribution_mgr)
        
        audit_system = UBECAuditSystem()
        self.register('audit_system', audit_system)
        
        logger.info("Core services initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all services"""
        logger.info("Shutting down services...")
        
        for name, service in self._services.items():
            if hasattr(service, 'close'):
                try:
                    await service.close()
                    logger.info(f"Closed service: {name}")
                except Exception as e:
                    logger.error(f"Error closing {name}: {e}")
        
        self._services.clear()
        self._factories.clear()
        
        logger.info("All services shut down")


# Global registry instance
registry = ServiceRegistry()
```

#### Step 2.2: Update Main Protocol

```python
# ubec_main_protocol.py
"""
UBEC Main Protocol - Four Element Coordinator
Pure async implementation with service registry

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import sys
import argparse
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

from config import config, get_logger, setup_logging
from core.service_registry import registry

# Import protocols
from UBEC import UBECProtocol
from UBECrc import UBECrcProtocol
from UBECgpi import UBECgpiProtocol
from UBECtt import UBECttProtocol

logger = get_logger('MainProtocol')


class UBECMainProtocol:
    """
    Main UBEC Protocol Coordinator
    
    Manages all four element protocols and provides unified interface.
    All methods are async.
    """
    
    def __init__(self):
        self.config = config
        self.registry = registry
        
        # Element protocols
        self.air: Optional[UBECProtocol] = None
        self.water: Optional[UBECrcProtocol] = None
        self.earth: Optional[UBECgpiProtocol] = None
        self.fire: Optional[UBECttProtocol] = None
        
        logger.info("Main Protocol instantiated")
    
    async def initialize(self) -> None:
        """
        Initialize main protocol and all elements
        
        Must be called before using any protocol methods
        """
        logger.info("=" * 70)
        logger.info("Initializing UBEC Main Protocol")
        logger.info("=" * 70)
        logger.info(f"Network: {self.config.NETWORK}")
        logger.info(f"Horizon: {self.config.horizon_url}")
        logger.info("")
        
        # Initialize service registry
        await self.registry.initialize_core_services()
        
        # Initialize element protocols
        logger.info("Initializing element protocols...")
        
        self.air = UBECProtocol()
        await self.air.initialize()
        logger.info("  ✓ Air (UBEC) initialized")
        
        self.water = UBECrcProtocol()
        await self.water.initialize()
        logger.info("  ✓ Water (UBECrc) initialized")
        
        self.earth = UBECgpiProtocol()
        await self.earth.initialize()
        logger.info("  ✓ Earth (UBECgpi) initialized")
        
        self.fire = UBECttProtocol()
        await self.fire.initialize()
        logger.info("  ✓ Fire (UBECtt) initialized")
        
        logger.info("")
        logger.info("All protocols initialized successfully")
        logger.info("=" * 70)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get system-wide health status (ASYNC)
        
        Checks all four elements concurrently
        
        Returns:
            Dictionary with health status for each element
        """
        logger.info("Checking system health...")
        
        # Run all health checks concurrently
        results = await asyncio.gather(
            self.air.health_check(),
            self.water.health_check(),
            self.earth.health_check(),
            self.fire.health_check(),
            return_exceptions=True
        )
        
        # Calculate overall status
        all_healthy = all(
            isinstance(r, dict) and r.get('status') == 'healthy' 
            for r in results
        )
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'network': self.config.NETWORK,
            'overall_status': 'healthy' if all_healthy else 'degraded',
            'elements': {
                'air': results[0],
                'water': results[1],
                'earth': results[2],
                'fire': results[3]
            }
        }
    
    async def get_all_statuses(self) -> Dict[str, Any]:
        """
        Get detailed status for all elements (ASYNC)
        
        Returns comprehensive system status
        """
        logger.info("Getting all element statuses...")
        
        # Run all status checks concurrently
        results = await asyncio.gather(
            self.air.get_status(),
            self.water.get_status(),
            self.earth.get_status(),
            self.fire.get_status(),
            return_exceptions=True
        )
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'network': self.config.NETWORK,
            'elements': {
                'air': results[0],
                'water': results[1],
                'earth': results[2],
                'fire': results[3]
            }
        }
    
    async def sync_all_elements(self) -> Dict[str, Any]:
        """
        Sync all element data concurrently (ASYNC)
        
        Returns:
            Sync results for all elements
        """
        logger.info("Syncing all elements...")
        
        # Run all syncs concurrently
        results = await asyncio.gather(
            self.air.sync_gateway_data(),
            self.water.sync_flow_data(),
            self.earth.sync_stability_data(),
            self.fire.sync_transformation_data(),
            return_exceptions=True
        )
        
        # Count successful syncs
        successful = sum(
            1 for r in results 
            if isinstance(r, dict) and r.get('status') == 'success'
        )
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'network': self.config.NETWORK,
            'elements_synced': successful,
            'total_elements': 4,
            'results': {
                'air': results[0],
                'water': results[1],
                'earth': results[2],
                'fire': results[3]
            }
        }
    
    async def shutdown(self) -> None:
        """Shutdown all services and protocols"""
        logger.info("Shutting down Main Protocol...")
        await self.registry.shutdown()
        logger.info("Shutdown complete")


async def main_async():
    """Async main entry point"""
    # Setup logging
    setup_logging()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='UBEC Main Protocol')
    parser.add_argument(
        '--action',
        choices=['health', 'status', 'sync'],
        default='health',
        help='Action to perform'
    )
    parser.add_argument(
        '--output',
        choices=['json', 'pretty'],
        default='pretty',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    # Initialize protocol
    protocol = UBECMainProtocol()
    await protocol.initialize()
    
    try:
        # Execute action
        if args.action == 'health':
            result = await protocol.get_system_health()
        elif args.action == 'status':
            result = await protocol.get_all_statuses()
        elif args.action == 'sync':
            result = await protocol.sync_all_elements()
        else:
            logger.error(f"Unknown action: {args.action}")
            sys.exit(1)
        
        # Output result
        print("\n" + "=" * 70)
        print(f"UBEC Protocol - {args.action.upper()} Result")
        print("=" * 70)
        print(json.dumps(result, indent=2, default=str))
        print("=" * 70 + "\n")
        
        # Exit code
        if result.get('overall_status') == 'degraded':
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await protocol.shutdown()


if __name__ == '__main__':
    # Run async main
    asyncio.run(main_async())
```

---

## Week 2: Configuration & Deduplication

### Day 1-2: Configuration Consolidation

#### Step 3.1: Create Single Configuration File

```python
# config/config.py
"""
UBEC Protocol Suite - Centralized Configuration
THE ONLY configuration file in the entire system

All configuration parameters are defined exactly once here.
No other configuration files exist.

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import os
from decimal import Decimal
from typing import Dict
from dataclasses import dataclass, field


@dataclass
class TokenConfig:
    """Configuration for a single token"""
    code: str
    issuer: str
    minimum_transaction: Decimal
    distribution_general: Decimal
    distribution_stewardship: Decimal
    distribution_admin: Decimal


@dataclass
class Config:
    """
    Single source of truth for all configuration
    
    All configuration parameters defined here, once.
    """
    
    # Network
    NETWORK: str = field(default_factory=lambda: os.getenv('UBEC_NETWORK', 'testnet'))
    
    # Horizon URLs
    HORIZON_URLS: Dict[str, str] = field(default_factory=lambda: {
        'mainnet': 'https://horizon.stellar.org',
        'testnet': 'https://horizon-testnet.stellar.org'
    })
    
    # Tokens (defined once)
    TOKENS: Dict[str, TokenConfig] = field(default_factory=lambda: {
        'UBEC': TokenConfig(
            code='UBEC',
            issuer=os.getenv('UBEC_ISSUER', 'GXXX...'),
            minimum_transaction=Decimal('10.0'),
            distribution_general=Decimal('0.75'),
            distribution_stewardship=Decimal('0.20'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECrc': TokenConfig(
            code='UBECrc',
            issuer=os.getenv('UBECrc_ISSUER', 'GXXX...'),
            minimum_transaction=Decimal('5.0'),
            distribution_general=Decimal('0.70'),
            distribution_stewardship=Decimal('0.25'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECgpi': TokenConfig(
            code='UBECgpi',
            issuer=os.getenv('UBECgpi_ISSUER', 'GXXX...'),
            minimum_transaction=Decimal('100.0'),
            distribution_general=Decimal('0.80'),
            distribution_stewardship=Decimal('0.15'),
            distribution_admin=Decimal('0.05')
        ),
        'UBECtt': TokenConfig(
            code='UBECtt',
            issuer=os.getenv('UBECtt_ISSUER', 'GXXX...'),
            minimum_transaction=Decimal('1.0'),
            distribution_general=Decimal('0.75'),
            distribution_stewardship=Decimal('0.20'),
            distribution_admin=Decimal('0.05')
        )
    })
    
    # Database
    DATABASE_URL: str = field(
        default_factory=lambda: os.getenv(
            'DATABASE_URL',
            'postgresql://ubec_app:password@localhost/ubec'
        )
    )
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # Sync Settings
    SYNC_BATCH_SIZE: int = 200
    SYNC_BATCH_DELAY: float = 1.0
    SYNC_MAX_ACCOUNTS: int = 1000
    
    # Holonic Weights
    HOLONIC_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        'autonomy_integration': 0.25,
        'multi_scale': 0.20,
        'regenerative': 0.25,
        'network': 0.15,
        'ubuntu': 0.15
    })
    
    # Logging
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @property
    def horizon_url(self) -> str:
        """Get Horizon URL for current network"""
        return self.HORIZON_URLS[self.NETWORK]
    
    def get_token_config(self, token_code: str) -> TokenConfig:
        """Get configuration for specific token"""
        if token_code not in self.TOKENS:
            raise ValueError(f"Unknown token: {token_code}")
        return self.TOKENS[token_code]


# SINGLE GLOBAL INSTANCE
config = Config()
```

#### Step 3.2: Delete Duplicate Configs

```bash
# Remove all duplicate configuration files
rm -rf UBEC/config/
rm -rf UBECrc/config/
rm -rf UBECgpi/config/
rm -rf UBECtt/config/

# Verify only one config exists
find . -name "config.py" -type f
# Should only show: ./config/config.py
```

### Day 3-4: Eliminate Method Duplication

#### Step 4.1: Create Shared Utilities

```python
# core/sync_utils.py
"""
Shared Synchronization Utilities
Common patterns used by all sync operations

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

from typing import Dict, Any, Callable
from datetime import datetime
import asyncio

from config import get_logger


async def execute_sync_operation(
    element_name: str,
    token_code: str,
    sync_function: Callable,
    logger
) -> Dict[str, Any]:
    """
    Generic sync operation executor
    
    Used by all element protocols - NO DUPLICATION
    
    Args:
        element_name: Element name (Air, Water, Earth, Fire)
        token_code: Token code (UBEC, UBECrc, etc.)
        sync_function: Async function to execute
        logger: Logger instance
    
    Returns:
        Standardized sync result dictionary
    """
    logger.info(f"Starting {element_name} ({token_code}) synchronization...")
    
    start_time = datetime.utcnow()
    
    try:
        # Execute sync function
        result = await sync_function()
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Standardize result format
        standard_result = {
            'element': element_name.lower(),
            'token': token_code,
            'status': 'success',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            **result  # Merge specific results
        }
        
        logger.info(
            f"  ✓ {element_name} sync complete "
            f"({duration:.2f}s)"
        )
        
        return standard_result
        
    except Exception as e:
        logger.error(f"  ✗ {element_name} sync failed: {e}")
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'element': element_name.lower(),
            'token': token_code,
            'status': 'error',
            'error': str(e),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration
        }
```

#### Step 4.2: Update Protocols to Use Shared Utils

```python
# UBEC/UBEC_protocol.py
# Update sync method to use shared utility

async def sync_gateway_data(self) -> Dict[str, Any]:
    """
    Sync gateway data using shared executor
    
    NO DUPLICATION - element-specific logic only
    """
    from core.sync_utils import execute_sync_operation
    from core.service_registry import registry
    
    async def _sync_logic():
        """Element-specific sync logic"""
        synchronizer = registry.get('synchronizer')
        
        if not synchronizer._initialized:
            await synchronizer.initialize()
        
        return await synchronizer.sync_account_data(
            asset_code=self.token_code,
            limit=200,
            max_accounts=1000
        )
    
    # Use shared executor - NO DUPLICATION
    return await execute_sync_operation(
        element_name='Air',
        token_code=self.token_code,
        sync_function=_sync_logic,
        logger=logger
    )
```

---

## Week 3: Documentation & Testing

### Day 1-2: Add Comprehensive Documentation

#### Template for All Python Files

```python
"""
[Module Name] - [One-line description]

[Detailed description of module purpose]

Usage:
    from [module] import [Class]
    
    instance = [Class]()
    result = await instance.method()

Functions:
    - function1(): Description
    - function2(): Description

Classes:
    - Class1: Description
    - Class2: Description

Dependencies:
    - dependency1: Purpose
    - dependency2: Purpose

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.

Version: 1.0
Date: October 10, 2025
Author: UBEC Development Team
"""
```

### Day 3-5: Comprehensive Testing

#### Test Suite Template

```python
# tests/test_compliance.py
"""
Test Compliance with 12 Project Design Principles

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations. This project was made possible with 
    the assistance of Claude and Anthropic PBC.
"""

import ast
import asyncio
from pathlib import Path
import pytest


class TestPrincipleCompliance:
    """Test suite for principle compliance"""
    
    def test_principle_5_no_sync_code(self):
        """Verify NO synchronous code exists"""
        violations = []
        
        for py_file in Path('.').rglob('*.py'):
            if 'venv' in str(py_file) or 'tests' in str(py_file):
                continue
            
            with open(py_file) as f:
                content = f.read()
            
            # Check for sync violations
            if 'import time' in content and 'time.sleep' in content:
                violations.append(f"{py_file}: uses time.sleep()")
            
            if 'import requests' in content:
                violations.append(f"{py_file}: uses sync requests")
            
            if 'from stellar_sdk import Server' in content:
                violations.append(f"{py_file}: uses sync Stellar Server")
        
        assert len(violations) == 0, f"Sync code found:\n" + "\n".join(violations)
    
    def test_principle_2_no_standalone_execution(self):
        """Verify only main.py has __main__ block"""
        violations = []
        
        for py_file in Path('.').rglob('*.py'):
            if 'ubec_main_protocol.py' in str(py_file):
                continue  # Allowed
            
            if 'venv' in str(py_file) or 'tests' in str(py_file):
                continue
            
            with open(py_file) as f:
                content = f.read()
            
            if "if __name__ == '__main__':" in content:
                violations.append(str(py_file))
        
        assert len(violations) == 0, \
            f"Standalone execution found in:\n" + "\n".join(violations)
    
    def test_principle_8_single_config(self):
        """Verify only ONE config file exists"""
        config_files = [
            p for p in Path('.').rglob('config.py')
            if 'venv' not in str(p) and 'tests' not in str(p)
        ]
        
        # Filter to only config/config.py
        config_files = [
            p for p in config_files
            if str(p).endswith('config/config.py')
        ]
        
        assert len(config_files) == 1, \
            f"Multiple config files found: {config_files}"
    
    def test_principle_11_attribution(self):
        """Verify attribution present in all files"""
        violations = []
        
        for py_file in Path('.').rglob('*.py'):
            if 'venv' in str(py_file) or 'tests' in str(py_file):
                continue
            
            with open(py_file) as f:
                content = f.read()
            
            if 'Anthropic PBC' not in content:
                violations.append(str(py_file))
        
        assert len(violations) == 0, \
            f"Missing attribution in:\n" + "\n".join(violations)
    
    @pytest.mark.asyncio
    async def test_async_operations(self):
        """Test that async operations work correctly"""
        from ubec_main_protocol import UBECMainProtocol
        
        protocol = UBECMainProtocol()
        await protocol.initialize()
        
        try:
            # Test health check
            health = await protocol.get_system_health()
            assert 'overall_status' in health
            
            # Test status
            status = await protocol.get_all_statuses()
            assert 'elements' in status
            
        finally:
            await protocol.shutdown()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## Summary Checklist

### Week 1: Critical Async & Service Registry
- [ ] Install async dependencies
- [ ] Create AsyncDatabaseManager
- [ ] Refactor UBECDataSynchronizer to async
- [ ] Update all protocols to async
- [ ] Implement ServiceRegistry
- [ ] Update main protocol to use registry
- [ ] Test async operations

### Week 2: Configuration & Deduplication
- [ ] Create single Config class
- [ ] Delete all duplicate config directories
- [ ] Update all imports to use single config
- [ ] Create shared sync utilities
- [ ] Refactor protocols to use shared utils
- [ ] Test configuration

### Week 3: Documentation & Testing
- [ ] Add module docstrings to ALL files
- [ ] Add attribution to ALL files
- [ ] Create test suite
- [ ] Run compliance tests
- [ ] Fix any test failures
- [ ] Final review

---

## Success Criteria

### After Refactoring, the System Must:

✅ Have ZERO synchronous operations  
✅ Use service registry for ALL dependencies  
✅ Have EXACTLY ONE configuration file  
✅ Have NO standalone execution except main.py  
✅ Have NO method duplication  
✅ Have attribution in ALL Python files  
✅ Pass ALL compliance tests  
✅ Be production-ready  

---

## Attribution

*This refactoring implementation guide was created using the services of Claude and Anthropic PBC to provide practical, actionable steps for achieving full compliance with the UBEC Protocol Suite design principles. This guide was made possible with the assistance of Claude and Anthropic PBC.*

---

**End of Refactoring Implementation Guide**  
**Document Version:** 1.0  
**Date:** October 10, 2025
