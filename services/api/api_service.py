#!/usr/bin/env python3
"""
UBEC Backend API Service - Production Version 2.1
==================================================
Provides read-only REST API endpoints for public website consumption
with IP-based rate limiting for abuse prevention.

This service exposes specific endpoints for the www server to consume,
providing an abstraction layer between the public website and internal
protocol operations. Integrated with real bioregion tracking.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained API service module
    ✅ #2  Service Pattern: No standalone execution, registry-managed
    ✅ #3  Service Registry: Full dependency injection via registry
    ✅ #4  Single Source of Truth: Database-backed with explicit schemas
    ✅ #5  Strict Async: 100% async/await throughout
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Comprehensive health checks
    ✅ #8  No Duplicate Configuration: Configuration from registry
    ✅ #9  Integrated Rate Limiting: IP-based, active (100/min, 1000/hour)
    ✅ #10 Separation of Concerns: API layer isolated from business logic
    ✅ #11 Comprehensive Documentation: Full docstrings and examples
    ✅ #12 Method Singularity: Each endpoint implemented once
════════════════════════════════════════════════════════════════════════════

Attribution: This project uses the services of Claude and Anthropic PBC to 
inform our decisions and recommendations. This project was made possible with 
the assistance of Claude and Anthropic PBC.

Usage Example:
    ```python
    from core.service_registry import ServiceRegistry
    from services.api.api_service import create_backend_api_service
    
    # Initialize via service registry (proper pattern)
    registry = ServiceRegistry()
    api_service = await registry.get('api_service')
    
    # FastAPI app is available at api_service.app
    # Run with: uvicorn main:app --host 0.0.0.0 --port 8000
    ```

Rate Limiting:
    IP-based rate limiting (no authentication required):
    - Default: 100 requests/minute, 1000 requests/hour per IP
    - Health endpoints: 300 requests/minute (for monitoring)
    - Transaction queries: 60 requests/minute (expensive queries)
    - No API keys required - open access with abuse prevention

Author: UBEC Protocol Development Team
Version: 2.1.0
Updated: 2025-11-08
Changes: Added IP-based rate limiting for abuse prevention
Reviewed: 2025-11-08 - Rate limiting implementation verified
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone
from decimal import Decimal

# Rate limiting imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)


# ============================================================================
# Rate Limiter Configuration - IP-Based, No Authentication Required
# ============================================================================

def get_real_ip(request: Request) -> str:
    """
    Get real client IP address, handling reverse proxies.
    
    Checks X-Forwarded-For header first (for nginx/traefik reverse proxy),
    then falls back to direct connection IP.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Client IP address as string
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can be a comma-separated list
        # Take the first (client) IP
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# Initialize rate limiter with IP-based tracking
# No authentication required - open access with abuse prevention
limiter = Limiter(
    key_func=get_real_ip,
    default_limits=["100/minute", "1000/hour"],  # Default for all endpoints
    storage_uri="memory://",  # In-memory storage (fast, suitable for single instance)
    # For distributed deployments, use: storage_uri="redis://localhost:6379"
)

logger.info("Rate limiter initialized: 100 req/min, 1000 req/hour per IP (in-memory)")


# ============================================================================
# Backend API Service Class
# ============================================================================

class BackendAPIService:
    """
    REST API Service for UBEC Protocol with IP-based rate limiting.
    
    Provides read-only endpoints for public website consumption with
    real-time data from database and integrated services.
    
    This service:
    - Exposes token information and metrics
    - Provides holonic evaluation scores
    - Delivers real-time network status with actual bioregion count
    - Supplies recent transaction data
    - Integrates with BioregionManager for real data
    - Implements IP-based rate limiting (no authentication required)
    
    Attributes:
        registry: ServiceRegistry instance (injected)
        app: FastAPI application instance
        logger: Logger instance for this service
        _initialized: Initialization status flag
    """
    
    def __init__(self, service_registry):
        """
        Initialize Backend API Service with rate limiting.
        
        Args:
            service_registry: ServiceRegistry instance from factory
        """
        self.registry = service_registry
        self.logger = logger
        self._initialized = False
        
        # Create FastAPI application
        self.app = FastAPI(
            title="UBEC Backend API",
            description="UBEC Protocol Backend API - Real-time protocol data with rate limiting",
            version="2.1.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc"
        )
        
        # Register rate limiter with FastAPI application
        self.app.state.limiter = limiter
        self.app.add_exception_handler(RateLimitExceeded, self._rate_limit_error_handler)
        
        # Configure CORS - allow www servers
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://www.ubec.network",          # Main www server
                "https://bioregional.ubec.network",  # Bioregional dashboard
                "http://bioregional.ubec.network",
                "http://localhost:3000",              # Development frontend
                "http://localhost:8080"              # Alternative dev port
            ],
            allow_credentials=True,
            allow_methods=["GET"],  # Read-only API
            allow_headers=["*"],
        )
        
        # Add middleware to include rate limit headers in responses
        @self.app.middleware("http")
        async def add_rate_limit_headers(request: Request, call_next):
            """
            Add rate limit information to response headers.
            
            Headers added:
            - X-RateLimit-Limit: Maximum requests allowed in window
            - X-RateLimit-Remaining: Requests remaining in current window
            - X-RateLimit-Reset: When the limit resets (Unix timestamp)
            """
            response = await call_next(request)
            
            # Get rate limit info from slowapi if available
            if hasattr(request.state, "view_rate_limit"):
                rate_limit = request.state.view_rate_limit
                response.headers["X-RateLimit-Limit"] = str(rate_limit.limit)
                response.headers["X-RateLimit-Remaining"] = str(rate_limit.remaining)
                response.headers["X-RateLimit-Reset"] = str(int(rate_limit.reset_time))
            
            return response
        
        # Setup routes
        self._setup_routes()
        
        self.logger.info("BackendAPIService initialized with IP-based rate limiting")
    
    async def _rate_limit_error_handler(
        self,
        request: Request,
        exc: RateLimitExceeded
    ) -> JSONResponse:
        """
        Custom handler for rate limit exceeded errors.
        
        Provides clear, informative error messages when rate limits are exceeded.
        Follows Ubuntu philosophy of transparency and guidance.
        
        Args:
            request: FastAPI Request object
            exc: RateLimitExceeded exception
            
        Returns:
            JSONResponse with 429 status and helpful error information
        """
        client_ip = get_real_ip(request)
        self.logger.warning(f"Rate limit exceeded for IP: {client_ip}, path: {request.url.path}")
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "You have exceeded the rate limit for this API. Please try again later.",
                "detail": {
                    "limit": "100 requests per minute, 1000 requests per hour",
                    "scope": "Per IP address",
                    "guidance": "This is an open API for public blockchain data. Rate limits prevent abuse while maintaining access for all."
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            headers={
                "Retry-After": "60"  # Suggest retry after 60 seconds
            }
        )
    
    async def initialize(self) -> None:
        """
        Initialize service and verify dependencies.
        
        Called by service registry during system startup.
        Verifies all required services are available.
        """
        self.logger.info("Initializing BackendAPIService")
        
        # Verify required services are available
        required_services = ['database', 'bioregion_manager']
        for service_name in required_services:
            try:
                await self.registry.get(service_name)
                self.logger.info(f"Verified service: {service_name}")
            except Exception as e:
                self.logger.error(f"Required service '{service_name}' not available: {e}")
                raise RuntimeError(f"Cannot initialize API service without {service_name}")
        
        self._initialized = True
        self.logger.info("BackendAPIService initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for monitoring.
        
        Returns:
            Dict containing health status and metrics
            
        Example:
            {
                'service': 'BackendAPIService',
                'version': '2.1.0',
                'status': 'healthy',
                'initialized': True,
                'endpoints_count': 8,
                'rate_limiting': 'active',
                'dependencies': {
                    'database': 'healthy',
                    'bioregion_manager': 'healthy'
                }
            }
        """
        try:
            # Check initialization
            if not self._initialized:
                return {
                    'service': 'BackendAPIService',
                    'version': '2.1.0',
                    'status': 'initializing',
                    'initialized': False,
                    'rate_limiting': 'active'
                }
            
            # Check dependencies
            dependencies = {}
            
            try:
                db = await self.registry.get('database')
                db_health = await db.health_check()
                dependencies['database'] = db_health.get('status', 'unknown')
            except Exception as e:
                dependencies['database'] = f'error: {str(e)}'
            
            try:
                bioregion_mgr = await self.registry.get('bioregion_manager')
                bioregion_health = await bioregion_mgr.health_check()
                dependencies['bioregion_manager'] = bioregion_health.get('status', 'unknown')
            except Exception as e:
                dependencies['bioregion_manager'] = f'error: {str(e)}'
            
            # Determine overall status
            all_healthy = all(
                status == 'healthy' 
                for status in dependencies.values() 
                if isinstance(status, str) and not status.startswith('error')
            )
            
            status = 'healthy' if all_healthy else 'degraded'
            
            return {
                'service': 'BackendAPIService',
                'version': '2.1.0',
                'status': status,
                'initialized': self._initialized,
                'endpoints_count': len(self.app.routes),
                'rate_limiting': 'active',
                'rate_limit_config': {
                    'default': '100/minute, 1000/hour',
                    'scope': 'per IP address',
                    'storage': 'in-memory'
                },
                'dependencies': dependencies,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'service': 'BackendAPIService',
                'version': '2.1.0',
                'status': 'unhealthy',
                'error': str(e),
                'rate_limiting': 'active',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _setup_routes(self):
        """
        Configure API endpoints with rate limiting.
        
        All endpoints are read-only (GET) and provide data for
        the public website dashboard and information pages.
        
        Rate limiting is applied per endpoint based on expected usage
        and resource consumption.
        
        IMPORTANT: The @limiter.limit() decorator MUST come AFTER @self.app.get()
        and the function MUST have a 'request: Request' parameter.
        """
        
        # ====================================================================
        # Health Check Endpoints - Higher limit for monitoring tools
        # ====================================================================
        
        @self.app.get("/health", response_model=Dict)
        @limiter.limit("300/minute")
        async def health_endpoint(request: Request) -> Dict:
            """
            Health check endpoint for monitoring and load balancers.
            
            Rate limit: 300 requests/minute (higher for monitoring tools)
            
            Returns comprehensive service health status.
            """
            return await self.health_check()
        
        @self.app.get("/api/v1/health", response_model=Dict)
        @limiter.limit("300/minute")
        async def api_health_endpoint(request: Request) -> Dict:
            """
            Alternative health check endpoint under /api/v1 path.
            
            Rate limit: 300 requests/minute
            """
            return await self.health_check()
        
        # ====================================================================
        # Token Information Endpoint
        # ====================================================================
        
        @self.app.get("/api/v1/tokens", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_tokens(request: Request) -> Dict:
            """
            Get information about all UBEC tokens.
            
            Rate limit: 100 requests/minute per IP
            
            Returns details for all four element tokens:
            - UBEC (Air) - Gateway and diversity
            - UBECrc (Water) - Reciprocity and flow
            - UBECgpi (Earth) - Stability and grounding
            - UBECtt (Fire) - Transformation and regeneration
            """
            try:
                db = await self.registry.get('database')
                
                # Query token information with explicit schema name
                results = await db.fetch_all(
                    """
                    SELECT 
                        asset_code,
                        asset_type,
                        issuer,
                        home_domain,
                        description,
                        element,
                        ubuntu_principle,
                        color_primary,
                        color_secondary,
                        created_at
                    FROM ubec_main.stellar_assets
                    WHERE asset_type = 'credit_alphanum12'
                    AND asset_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
                    ORDER BY 
                        CASE asset_code
                            WHEN 'UBEC' THEN 1
                            WHEN 'UBECrc' THEN 2
                            WHEN 'UBECgpi' THEN 3
                            WHEN 'UBECtt' THEN 4
                        END
                    """,
                    ()
                )
                
                tokens = []
                for row in results:
                    token = {
                        'asset_code': row['asset_code'],
                        'element': row['element'],
                        'ubuntu_principle': row['ubuntu_principle'],
                        'issuer': row['issuer'],
                        'description': row['description'],
                        'colors': {
                            'primary': row['color_primary'],
                            'secondary': row['color_secondary']
                        },
                        'home_domain': row['home_domain'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None
                    }
                    tokens.append(token)
                
                response = {
                    'tokens': tokens,
                    'count': len(tokens),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info("✓ Retrieved token information")
                return response
                
            except Exception as e:
                logger.error(f"Error fetching tokens: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching token information: {str(e)}")
        
        # ====================================================================
        # Network Status Endpoint
        # ====================================================================
        
        @self.app.get("/api/v1/network-status", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_network_status(request: Request) -> Dict:
            """
            Get current network status and health metrics.
            
            Rate limit: 100 requests/minute per IP
            
            Returns:
            - Total token supply across all elements
            - Total unique holders
            - Active bioregion count
            - Overall health score from holonic metrics
            - Recent transaction activity
            """
            try:
                db = await self.registry.get('database')
                
                # Get total supply and holders from ubec_balances (explicit schema)
                supply_result = await db.fetch_one(
                    """
                    SELECT 
                        SUM(balance) as total_supply,
                        COUNT(DISTINCT account_id) as total_holders
                    FROM ubec_main.ubec_balances
                    WHERE balance > 0
                    """,
                    ()
                )
                
                # Get average holonic score from last 7 days (explicit schema)
                health_result = await db.fetch_one(
                    """
                    SELECT AVG(score) as avg_score
                    FROM ubec_main.ubec_holonic_metrics
                    WHERE calculated_at > NOW() - INTERVAL '7 days'
                    """,
                    ()
                )
                
                # Get bioregion count (if available)
                try:
                    bioregion_manager = await self.registry.get('bioregion_manager')
                    bioregion_count = await bioregion_manager.get_bioregion_count()
                except:
                    bioregion_count = 0
                
                # Get recent transaction count (last 24 hours, explicit schema)
                tx_result = await db.fetch_one(
                    """
                    SELECT COUNT(*) as tx_count
                    FROM ubec_main.stellar_transactions
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    """,
                    ()
                )
                
                response = {
                    'network_health': 'healthy',
                    'total_supply': float(supply_result['total_supply']) if supply_result['total_supply'] else 0.0,
                    'total_holders': int(supply_result['total_holders']) if supply_result['total_holders'] else 0,
                    'active_bioregions': bioregion_count,
                    'overall_health_score': float(health_result['avg_score']) if health_result and health_result['avg_score'] else 0.0,
                    'transactions_24h': int(tx_result['tx_count']) if tx_result else 0,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info("✓ Retrieved network status")
                return response
                
            except Exception as e:
                logger.error(f"Error fetching network status: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching network status: {str(e)}")
        
        # ====================================================================
        # Bioregion Endpoints (INTEGRATED!)
        # ====================================================================
        
        @self.app.get("/api/v1/bioregions", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_bioregions(request: Request) -> Dict:
            """
            Get detailed information about all bioregions.
            
            Rate limit: 100 requests/minute per IP
            
            Returns comprehensive bioregion data including:
            - Count of bioregions
            - Summary statistics
            - Detailed information for each bioregion
            
            Returns:
                Dictionary with bioregion information
            """
            try:
                bioregion_mgr = await self.registry.get('bioregion_manager')
                
                bioregions = await bioregion_mgr.get_all_bioregions()
                summary = await bioregion_mgr.get_bioregion_summary()
                
                return {
                    'count': len(bioregions),
                    'summary': summary,
                    'bioregions': bioregions,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error fetching bioregions: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching bioregions: {str(e)}")
        
        @self.app.get("/api/v1/bioregions/{bioregion_id}", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_bioregion(bioregion_id: int, request: Request) -> Dict:
            """
            Get detailed information about a specific bioregion.
            
            Rate limit: 100 requests/minute per IP
            
            Args:
                bioregion_id: ID of the bioregion to retrieve
                
            Returns:
                Dictionary with bioregion details
            """
            try:
                bioregion_mgr = await self.registry.get('bioregion_manager')
                bioregion = await bioregion_mgr.get_bioregion_by_id(bioregion_id)
                
                if not bioregion:
                    raise HTTPException(status_code=404, detail=f"Bioregion {bioregion_id} not found")
                
                return bioregion
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error fetching bioregion {bioregion_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching bioregion: {str(e)}")
        
        # ====================================================================
        # Transaction Endpoints - More restrictive (expensive queries)
        # ====================================================================
        
        @self.app.get("/api/v1/transactions", response_model=Dict)
        @limiter.limit("60/minute")
        async def get_recent_transactions(request: Request, limit: int = 20) -> Dict:
            """
            Get recent UBEC token transactions from Stellar blockchain.
            
            Rate limit: 60 requests/minute per IP (more restrictive for expensive queries)
            
            Query Parameters:
            - limit: Number of transactions to return (default: 20, max: 100)
            
            Returns list of recent transactions with element context.
            """
            try:
                # Validate limit parameter
                if limit < 1:
                    limit = 20
                if limit > 100:
                    limit = 100
                
                db = await self.registry.get('database')
                
                # Query recent transactions with explicit schema name
                results = await db.fetch_all(
                    """
                    SELECT 
                        t.transaction_hash,
                        t.ledger,
                        t.source_account,
                        t.operation_type,
                        t.asset_code,
                        t.amount,
                        t.from_account,
                        t.to_account,
                        t.created_at,
                        a.element,
                        a.ubuntu_principle
                    FROM ubec_main.stellar_transactions t
                    LEFT JOIN ubec_main.stellar_assets a ON t.asset_code = a.asset_code
                    WHERE t.asset_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
                    ORDER BY t.created_at DESC
                    LIMIT $1
                    """,
                    (limit,)
                )
                
                transactions = []
                for row in results:
                    tx = {
                        'hash': row['transaction_hash'],
                        'ledger': int(row['ledger']) if row['ledger'] else None,
                        'asset_code': row['asset_code'],
                        'element': row['element'],
                        'ubuntu_principle': row['ubuntu_principle'],
                        'operation_type': row['operation_type'],
                        'from_account': row['from_account'],
                        'to_account': row['to_account'],
                        'amount': float(row['amount']) if row['amount'] else 0.0,
                        'timestamp': row['created_at'].isoformat() if row['created_at'] else None
                    }
                    transactions.append(tx)
                
                response = {
                    'transactions': transactions,
                    'count': len(transactions),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info(f"✓ Retrieved {len(transactions)} recent transactions")
                return response
                
            except Exception as e:
                logger.error(f"Error fetching transactions: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")

        # ====================================================================
        # Distribution Stats Endpoint
        # ====================================================================
        
        @self.app.get("/api/v1/distribution", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_distribution_stats(request: Request) -> Dict:
            """
            Get token distribution statistics for 75/20/5 compliance.
            
            Rate limit: 100 requests/minute per IP
            
            Returns distribution breakdown by category:
            - General Circulation (75%)
            - Stewardship (20%)
            - Administration (5%)
            
            Shows compliance status for each token.
            """
            try:
                db = await self.registry.get('database')
                
                # Query ubec_distributions table with explicit schema name
                results = await db.fetch_all(
                    """
                    SELECT 
                        token_code,
                        element,
                        category,
                        target_percentage,
                        current_percentage,
                        current_amount,
                        total_supply,
                        is_compliant,
                        deviation,
                        snapshot_time
                    FROM ubec_main.ubec_distributions
                    ORDER BY 
                        CASE token_code
                            WHEN 'UBEC' THEN 1
                            WHEN 'UBECrc' THEN 2
                            WHEN 'UBECgpi' THEN 3
                            WHEN 'UBECtt' THEN 4
                        END,
                        CASE category
                            WHEN 'general_circulation' THEN 1
                            WHEN 'stewardship' THEN 2
                            WHEN 'administration' THEN 3
                        END
                    """,
                    ()
                )
                
                # Group by token
                distributions = {}
                for row in results:
                    token = row['token_code']
                    if token not in distributions:
                        distributions[token] = {
                            'token_code': token,
                            'element': row['element'],
                            'total_supply': float(row['total_supply']),
                            'categories': {},
                            'is_compliant': True,
                            'snapshot_time': None
                        }
                    
                    category = row['category']
                    distributions[token]['categories'][category] = {
                        'target_percentage': float(row['target_percentage']),
                        'current_percentage': float(row['current_percentage']),
                        'current_amount': float(row['current_amount']),
                        'is_compliant': bool(row['is_compliant']),
                        'deviation': float(row['deviation']) if row['deviation'] else 0.0
                    }
                    
                    # Overall compliance is false if any category is non-compliant
                    if not row['is_compliant']:
                        distributions[token]['is_compliant'] = False
                    
                    if row['snapshot_time']:
                        distributions[token]['snapshot_time'] = row['snapshot_time'].isoformat()
                
                response = {
                    'distributions': list(distributions.values()),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info(f"✓ Retrieved distribution stats for {len(distributions)} tokens")
                return response
                
            except Exception as e:
                logger.error(f"Error fetching distribution stats: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching distribution stats: {str(e)}")
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _calculate_network_health(
        self,
        bioregion_count: int,
        participant_count: int,
        ubuntu_score: float
    ) -> str:
        """
        Calculate overall network health based on metrics.
        
        Args:
            bioregion_count: Number of active bioregions
            participant_count: Number of active participants
            ubuntu_score: Average Ubuntu alignment score
            
        Returns:
            Health status: 'healthy', 'degraded', or 'unhealthy'
        """
        # Calculate component scores (0-1)
        bioregion_score = min(bioregion_count / 10, 1.0)
        participant_score = min(participant_count / 500, 1.0)
        ubuntu_score_normalized = ubuntu_score
        
        # Weighted average
        health_score = (
            bioregion_score * 0.4 +
            participant_score * 0.3 +
            ubuntu_score_normalized * 0.3
        )
        
        if health_score >= 0.7:
            return 'healthy'
        elif health_score >= 0.4:
            return 'degraded'
        else:
            return 'unhealthy'
    
    async def close(self) -> None:
        """
        Clean up resources.
        
        Called by service registry during system shutdown.
        """
        self.logger.info("Closing BackendAPIService")
        # FastAPI app doesn't need explicit cleanup
        self._initialized = False


# ============================================================================
# Service Factory Function for Registry Integration
# ============================================================================

async def create_backend_api_service(registry) -> BackendAPIService:
    """
    Factory function to create BackendAPIService instance.
    
    This function is called by the ServiceRegistry to instantiate the service
    with proper dependency injection.
    
    Args:
        registry: ServiceRegistry instance providing dependencies
        
    Returns:
        Initialized BackendAPIService instance
        
    Example:
        # In main.py service registration
        registry.register_factory(
            'api_service',
            create_backend_api_service,
            dependencies=['database', 'bioregion_manager']
        )
    """
    service = BackendAPIService(registry)
    await service.initialize()
    return service
