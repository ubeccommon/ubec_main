"""
Stellar Client Service - Production Implementation

Wraps stellar_sdk.ServerAsync with comprehensive health monitoring.

Design Principles Applied:
- ✅ Principle #2: Service Pattern (no standalone execution)
- ✅ Principle #5: Strict Async Operations (all methods async)
- ✅ Principle #7: Per-Asset Monitoring (uses ServiceHealthCheck)
- ✅ Principle #11: Comprehensive Documentation
- ✅ Principle #12: Method Singularity (single health check method)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our 
    decisions and recommendations. This project was made possible with the 
    assistance of Claude and Anthropic PBC.

Version: 1.0.0
Date: October 18, 2025
"""

from typing import Dict, Any, Optional
from stellar_sdk import ServerAsync
import logging

logger = logging.getLogger(__name__)


class StellarClientService:
    """
    Stellar blockchain client with health monitoring.
    
    Wraps stellar_sdk.ServerAsync to provide:
    - Standardized health checks (Principle #7)
    - Async-only operations (Principle #5)
    - Proper service lifecycle management
    
    Usage:
        client = StellarClientService(horizon_url="https://horizon.stellar.org")
        health = await client.health_check()
        account = await client.accounts().account_id(address).call()
        await client.close()
    """
    
    def __init__(self, horizon_url: str):
        """
        Initialize Stellar client service.
        
        Args:
            horizon_url: Horizon server URL (mainnet or testnet)
        """
        self.horizon_url = horizon_url
        self._client = ServerAsync(horizon_url=horizon_url)
        self._initialized = True
        self._request_count = 0
        self._error_count = 0
        self._last_error: Optional[str] = None
        self._last_error_time: Optional[str] = None
        
        logger.info(f"Stellar client initialized: {horizon_url}")
    
    # ========================================================================
    # PROXY TO UNDERLYING CLIENT (Principle #12: Single Implementation)
    # ========================================================================
    
    def __getattr__(self, name):
        """
        Proxy all stellar_sdk methods to underlying client.
        
        This allows transparent access to all ServerAsync methods while
        maintaining our wrapper for health checks.
        """
        return getattr(self._client, name)
    
    # ========================================================================
    # HEALTH CHECK (Principle #7: Per-Asset Monitoring)
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check using standardized utility.
        
        Follows Principle #7: Per-Asset Monitoring with execution minimums.
        Uses ServiceHealthCheck utility for consistency.
        
        Returns:
            Health status dictionary with standardized format
        """
        from core.utils.service_health import ServiceHealthCheck
        
        return await ServiceHealthCheck.stellar_client_health(
            client=self,
            horizon_url=self.horizon_url,
            initialized=self._initialized,
            request_count=self._request_count,
            error_count=self._error_count,
            last_error=self._last_error,
            last_error_time=self._last_error_time
        )
    
    # ========================================================================
    # ASYNC OPERATIONS (Principle #5: Strict Async)
    # ========================================================================
    
    async def test_connection(self) -> bool:
        """
        Test Stellar network connectivity.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            await self._client.root().call()
            self._request_count += 1
            return True
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            from datetime import datetime
            self._last_error_time = datetime.now().isoformat()
            logger.error(f"Stellar connection test failed: {e}")
            return False
    
    async def get_network_info(self) -> Dict[str, Any]:
        """
        Get Stellar network information.
        
        Returns:
            Network details (passphrase, version, etc.)
        """
        try:
            response = await self._client.root().call()
            self._request_count += 1
            return {
                'network_passphrase': response.get('network_passphrase'),
                'horizon_version': response.get('horizon_version'),
                'core_version': response.get('core_version'),
                'protocol_version': response.get('current_protocol_version')
            }
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            from datetime import datetime
            self._last_error_time = datetime.now().isoformat()
            logger.error(f"Failed to get network info: {e}")
            return {}
    
    # ========================================================================
    # LIFECYCLE MANAGEMENT
    # ========================================================================
    
    async def close(self) -> None:
        """
        Close Stellar client connection.
        
        Follows async cleanup pattern (Principle #5).
        """
        try:
            if hasattr(self._client, 'close'):
                await self._client.close()
            logger.info("Stellar client closed")
        except Exception as e:
            logger.error(f"Error closing Stellar client: {e}")


# ============================================================================
# FACTORY FUNCTION (Principle #2: Service Pattern)
# ============================================================================

async def create_stellar_client_service(horizon_url: str) -> StellarClientService:
    """
    Factory function for creating Stellar client service.
    
    Follows Principle #2: Service Pattern with factory creation.
    
    Args:
        horizon_url: Horizon server URL
    
    Returns:
        Initialized StellarClientService instance
    
    Example:
        client = await create_stellar_client_service(
            horizon_url="https://horizon.stellar.org"
        )
    """
    return StellarClientService(horizon_url=horizon_url)


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    'StellarClientService',
    'create_stellar_client_service'
]
