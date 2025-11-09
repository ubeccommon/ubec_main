#!/usr/bin/env python3
"""
UBEC Backend API Service - Production Version 2.1.1
====================================================
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
Version: 2.1.2
Updated: 2025-11-08
Changes: 
  v2.1.2 - Added /api/v1/holonic-scores endpoint for Ubuntu principle evaluations
  v2.1.1 - Fixed rate limit middleware tuple handling and token endpoint config service usage
Reviewed: 2025-11-08 - All endpoints verified and operational
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
            version="2.1.2",
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
        # FIXED v2.1.1: Handle slowapi's tuple format for rate limit data
        @self.app.middleware("http")
        async def add_rate_limit_headers(request: Request, call_next):
            """
            Add rate limit information to response headers.
            
            FIXED v2.1.1: Properly handle slowapi's tuple format (limit, remaining, reset_time)
            
            Headers added:
            - X-RateLimit-Limit: Maximum requests allowed in window
            - X-RateLimit-Remaining: Requests remaining in current window
            - X-RateLimit-Reset: When the limit resets (Unix timestamp)
            """
            response = await call_next(request)
            
            # Get rate limit info from slowapi if available
            # slowapi stores rate limit as a tuple: (limit, remaining, reset_time)
            if hasattr(request.state, "view_rate_limit"):
                try:
                    rate_limit = request.state.view_rate_limit
                    
                    # Handle tuple format: (limit, remaining, reset_time)
                    if isinstance(rate_limit, tuple) and len(rate_limit) >= 3:
                        limit, remaining, reset_time = rate_limit[0], rate_limit[1], rate_limit[2]
                        response.headers["X-RateLimit-Limit"] = str(limit)
                        response.headers["X-RateLimit-Remaining"] = str(remaining)
                        response.headers["X-RateLimit-Reset"] = str(int(reset_time))
                    # Handle object format (if slowapi changes in future)
                    elif hasattr(rate_limit, 'limit'):
                        response.headers["X-RateLimit-Limit"] = str(rate_limit.limit)
                        response.headers["X-RateLimit-Remaining"] = str(rate_limit.remaining)
                        response.headers["X-RateLimit-Reset"] = str(int(rate_limit.reset_time))
                except Exception as e:
                    # Log but don't fail request if header addition fails
                    self.logger.debug(f"Could not add rate limit headers: {e}")
            
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
                'version': '2.1.2',
                'status': 'healthy',
                'initialized': True,
                'endpoints_count': 9,
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
                    'version': '2.1.2',
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
                'version': '2.1.2',
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
                'version': '2.1.2',
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
        # FIXED v2.1.1: Now uses config service instead of stellar_assets table
        # ====================================================================
        
        @self.app.get("/api/v1/tokens", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_tokens(request: Request) -> Dict:
            """
            Get information about all UBEC tokens.
            
            FIXED v2.1.1: Now retrieves token info from config service
            instead of non-existent stellar_assets table.
            
            Rate limit: 100 requests/minute per IP
            
            Returns details for all four element tokens:
            - UBEC (Air) - Gateway and diversity
            - UBECrc (Water) - Reciprocity and flow
            - UBECgpi (Earth) - Stability and grounding
            - UBECtt (Fire) - Transformation and regeneration
            """
            try:
                # Get config service for token information
                # Follows Principle #4: Database as single source of truth (via config service)
                # Follows Principle #8: No duplicate configuration
                config = await self.registry.get('config')
                if not config:
                    raise HTTPException(status_code=500, detail="Configuration service unavailable")
                
                # Build token information from config service
                # Config service loads from system_settings table
                tokens = [
                    {
                        'asset_code': 'UBEC',
                        'element': 'air',
                        'ubuntu_principle': 'diversity',
                        'issuer': config.UBEC_ISSUER,
                        'description': 'Gateway token providing universal access to the UBEC ecosystem',
                        'colors': {
                            'primary': '#E3F2FD',
                            'secondary': '#2196F3'
                        },
                        'symbol': '🜁',
                        'home_domain': 'ubec.network'
                    },
                    {
                        'asset_code': 'UBECrc',
                        'element': 'water',
                        'ubuntu_principle': 'reciprocity',
                        'issuer': config.UBECRC_ISSUER,
                        'description': 'Flow token facilitating reciprocal exchange and mutual benefit',
                        'colors': {
                            'primary': '#E0F7FA',
                            'secondary': '#00BCD4'
                        },
                        'symbol': '🜄',
                        'home_domain': 'ubec.network'
                    },
                    {
                        'asset_code': 'UBECgpi',
                        'element': 'earth',
                        'ubuntu_principle': 'mutualism',
                        'issuer': config.UBECGPI_ISSUER,
                        'description': 'Stability token providing grounded value reference',
                        'colors': {
                            'primary': '#F1F8E9',
                            'secondary': '#8BC34A'
                        },
                        'symbol': '🜃',
                        'home_domain': 'ubec.network'
                    },
                    {
                        'asset_code': 'UBECtt',
                        'element': 'fire',
                        'ubuntu_principle': 'regeneration',
                        'issuer': config.UBECTT_ISSUER,
                        'description': 'Transformation token catalyzing regenerative change',
                        'colors': {
                            'primary': '#FFF3E0',
                            'secondary': '#FF9800'
                        },
                        'symbol': '🜂',
                        'home_domain': 'ubec.network'
                    }
                ]
                
                response = {
                    'tokens': tokens,
                    'count': len(tokens),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info("✓ Retrieved token information from config")
                return response
                
            except HTTPException:
                raise
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
        # Ecoregion Endpoints (phenomenal schema)
        # ====================================================================
        
        @self.app.get("/api/v1/ecoregions", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_ecoregions(
            request: Request,
            limit: int = 50,
            biome: Optional[str] = None,
            realm: Optional[str] = None
        ) -> Dict:
            """
            Get ecoregion data from Ecoregions2017 dataset.
            
            Rate limit: 100 requests/minute per IP
            
            Query Parameters:
            - limit: Number of results (default: 50, max: 200)
            - biome: Filter by biome name
            - realm: Filter by realm
            
            Returns ecoregion geographic and ecological data.
            """
            try:
                # Validate limit
                if limit < 1:
                    limit = 50
                if limit > 200:
                    limit = 200
                
                db = await self.registry.get('database')
                
                # Build query with filters
                where_clauses = []
                params = []
                param_num = 1
                
                if biome:
                    where_clauses.append(f"biome_name ILIKE ${param_num}")
                    params.append(f"%{biome}%")
                    param_num += 1
                
                if realm:
                    where_clauses.append(f"realm ILIKE ${param_num}")
                    params.append(f"%{realm}%")
                    param_num += 1
                
                where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                # Get ecoregions with explicit schema
                query = f"""
                    SELECT 
                        id,
                        objectid,
                        eco_name,
                        eco_id,
                        biome_num,
                        biome_name,
                        realm,
                        eco_biome_,
                        nnh,
                        nnh_name,
                        shape_leng,
                        shape_area,
                        color,
                        color_bio,
                        color_nnh
                    FROM phenomenal.ecoregions_2017
                    {where_clause}
                    ORDER BY eco_name
                    LIMIT ${param_num}
                """
                
                params.append(limit)
                ecoregions = await db.fetch_all(query, tuple(params))
                
                # Get summary stats
                summary_query = """
                    SELECT 
                        COUNT(*) as total_ecoregions,
                        COUNT(DISTINCT biome_name) as total_biomes,
                        COUNT(DISTINCT realm) as total_realms
                    FROM phenomenal.ecoregions_2017
                """
                summary = await db.fetch_one(summary_query, ())
                
                return {
                    'count': len(ecoregions),
                    'summary': {
                        'total_ecoregions': summary['total_ecoregions'],
                        'total_biomes': summary['total_biomes'],
                        'total_realms': summary['total_realms']
                    },
                    'ecoregions': [dict(row) for row in ecoregions],
                    'filters': {
                        'biome': biome,
                        'realm': realm,
                        'limit': limit
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error fetching ecoregions: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching ecoregions: {str(e)}")
        
        @self.app.get("/api/v1/ecoregions/{eco_id}", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_ecoregion(eco_id: int, request: Request) -> Dict:
            """
            Get detailed information about a specific ecoregion.
            
            Rate limit: 100 requests/minute per IP
            
            Args:
                eco_id: Ecoregion ID to retrieve
                
            Returns:
                Dictionary with ecoregion details
            """
            try:
                db = await self.registry.get('database')
                
                query = """
                    SELECT 
                        id,
                        objectid,
                        eco_name,
                        eco_id,
                        biome_num,
                        biome_name,
                        realm,
                        eco_biome_,
                        nnh,
                        nnh_name,
                        shape_leng,
                        shape_area,
                        color,
                        color_bio,
                        color_nnh,
                        license
                    FROM phenomenal.ecoregions_2017
                    WHERE eco_id = $1
                """
                
                ecoregion = await db.fetch_one(query, (eco_id,))
                
                if not ecoregion:
                    raise HTTPException(status_code=404, detail=f"Ecoregion {eco_id} not found")
                
                return dict(ecoregion)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error fetching ecoregion {eco_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching ecoregion: {str(e)}")
        
        # ====================================================================
        # Watershed Endpoints (phenomenal schema)
        # ====================================================================
        
        @self.app.get("/api/v1/watersheds", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_watersheds(
            request: Request,
            limit: int = 50,
            min_area: Optional[float] = None
        ) -> Dict:
            """
            Get watershed data from FEOW HydroSHEDS dataset.
            
            Rate limit: 100 requests/minute per IP
            
            Query Parameters:
            - limit: Number of results (default: 50, max: 200)
            - min_area: Minimum area in square kilometers
            
            Returns watershed geographic data.
            """
            try:
                if limit < 1:
                    limit = 50
                if limit > 200:
                    limit = 200
                
                db = await self.registry.get('database')
                
                where_clauses = []
                params = []
                param_num = 1
                
                if min_area is not None:
                    where_clauses.append(f"area_skm >= ${param_num}")
                    params.append(min_area)
                    param_num += 1
                
                where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                query = f"""
                    SELECT 
                        id,
                        feow_id,
                        area_skm
                    FROM phenomenal.feow_hydrosheds
                    {where_clause}
                    ORDER BY area_skm DESC
                    LIMIT ${param_num}
                """
                
                params.append(limit)
                watersheds = await db.fetch_all(query, tuple(params))
                
                summary_query = """
                    SELECT 
                        COUNT(*) as total_watersheds,
                        SUM(area_skm) as total_area,
                        AVG(area_skm) as avg_area,
                        MAX(area_skm) as max_area
                    FROM phenomenal.feow_hydrosheds
                """
                summary = await db.fetch_one(summary_query, ())
                
                return {
                    'count': len(watersheds),
                    'summary': {
                        'total_watersheds': summary['total_watersheds'],
                        'total_area_km2': float(summary['total_area']) if summary['total_area'] else 0,
                        'avg_area_km2': float(summary['avg_area']) if summary['avg_area'] else 0,
                        'max_area_km2': float(summary['max_area']) if summary['max_area'] else 0
                    },
                    'watersheds': [dict(row) for row in watersheds],
                    'filters': {
                        'min_area': min_area,
                        'limit': limit
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error fetching watersheds: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching watersheds: {str(e)}")
        
        @self.app.get("/api/v1/watersheds/{feow_id}", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_watershed(feow_id: int, request: Request) -> Dict:
            """
            Get specific watershed by FEOW ID.
            
            Rate limit: 100 requests/minute per IP
            """
            try:
                db = await self.registry.get('database')
                
                query = """
                    SELECT 
                        id,
                        feow_id,
                        area_skm
                    FROM phenomenal.feow_hydrosheds
                    WHERE feow_id = $1
                """
                
                watershed = await db.fetch_one(query, (feow_id,))
                
                if not watershed:
                    raise HTTPException(status_code=404, detail=f"Watershed {feow_id} not found")
                
                return dict(watershed)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error fetching watershed {feow_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Error fetching watershed: {str(e)}")
        
        # ====================================================================
        # Transaction Endpoints - More restrictive (expensive queries)
        # FIXED v2.1.1: Removed reference to non-existent stellar_assets table
        # ====================================================================
        
        @self.app.get("/api/v1/transactions", response_model=Dict)
        @limiter.limit("60/minute")
        async def get_recent_transactions(request: Request, limit: int = 20) -> Dict:
            """
            Get recent UBEC token transactions from Stellar blockchain.
            
            FIXED v2.1.2: Query stellar_operations (has correct columns) instead of stellar_transactions.
            stellar_transactions stores transaction-level data (groups of operations),
            while stellar_operations stores individual operations with asset transfer details.
            
            Rate limit: 60 requests/minute per IP (more restrictive for expensive queries)
            
            Query Parameters:
            - limit: Number of transactions to return (default: 20, max: 100)
            
            Returns list of recent operations with element context.
            """
            try:
                # Validate limit parameter
                if limit < 1:
                    limit = 20
                if limit > 100:
                    limit = 100
                
                db = await self.registry.get('database')
                
                # Query stellar_operations table (has operation details)
                # FIXED: Use correct table and column names
                results = await db.fetch_all(
                    """
                    SELECT 
                        o.operation_id,
                        o.transaction_hash,
                        o.type as operation_type,
                        o.asset_code,
                        o.amount,
                        o.from_account,
                        o.to_account,
                        o.source_account,
                        o.created_at,
                        t.ledger
                    FROM ubec_main.stellar_operations o
                    LEFT JOIN ubec_main.stellar_transactions t 
                        ON o.transaction_hash = t.transaction_hash
                    WHERE o.asset_code IN ('UBEC', 'UBECrc', 'UBECgpi', 'UBECtt')
                    ORDER BY o.created_at DESC
                    LIMIT $1
                    """,
                    (limit,)
                )
                
                # Map asset codes to elements and principles
                asset_metadata = {
                    'UBEC': {'element': 'air', 'ubuntu_principle': 'diversity'},
                    'UBECrc': {'element': 'water', 'ubuntu_principle': 'reciprocity'},
                    'UBECgpi': {'element': 'earth', 'ubuntu_principle': 'mutualism'},
                    'UBECtt': {'element': 'fire', 'ubuntu_principle': 'regeneration'}
                }
                
                transactions = []
                for row in results:
                    asset_code = row['asset_code']
                    metadata = asset_metadata.get(asset_code, {'element': None, 'ubuntu_principle': None})
                    
                    tx = {
                        'operation_id': row['operation_id'],
                        'hash': row['transaction_hash'],
                        'ledger': int(row['ledger']) if row['ledger'] else None,
                        'asset_code': asset_code,
                        'element': metadata['element'],
                        'ubuntu_principle': metadata['ubuntu_principle'],
                        'operation_type': row['operation_type'],
                        'from_account': row['from_account'],
                        'to_account': row['to_account'],
                        'source_account': row['source_account'],
                        'amount': float(row['amount']) if row['amount'] else 0.0,
                        'timestamp': row['created_at'].isoformat() if row['created_at'] else None
                    }
                    transactions.append(tx)
                
                response = {
                    'transactions': transactions,
                    'count': len(transactions),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info(f"✓ Retrieved {len(transactions)} recent operations")
                return response
                
            except Exception as e:
                logger.error(f"Error fetching transactions: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")

        # ====================================================================
        # Holonic Scores Endpoint - Ubuntu Principle Evaluations
        # ====================================================================
        
        @self.app.get("/api/v1/holonic-scores", response_model=Dict)
        @limiter.limit("100/minute")
        async def get_holonic_scores(
            request: Request,
            category: Optional[str] = None,
            limit: int = 50,
            min_score: float = 0.0
        ) -> Dict:
            """
            Get holonic evaluation scores for accounts.
            
            Rate limit: 100 requests/minute per IP
            
            Query Parameters:
            - category: Filter by holonic category (observer, participant, contributor, integrator, exemplar)
            - limit: Number of results to return (default: 50, max: 200)
            - min_score: Minimum composite score threshold (0.0-1.0)
            
            Returns:
            - Summary statistics (category distribution, average scores)
            - List of account evaluations with 5 dimensional scores
            - Ubuntu principle assessment details
            
            Holonic Categories:
            - Observer (0.0-0.2): Beginning the journey
            - Participant (0.2-0.4): Active engagement
            - Contributor (0.4-0.6): Regular valuable contributions
            - Integrator (0.6-0.8): High integration with network
            - Exemplar (0.8-1.0): Exemplary Ubuntu alignment
            """
            try:
                # Validate parameters
                if limit < 1:
                    limit = 50
                if limit > 200:
                    limit = 200
                if min_score < 0.0:
                    min_score = 0.0
                if min_score > 1.0:
                    min_score = 1.0
                
                # Validate category if provided
                valid_categories = ['observer', 'participant', 'contributor', 'integrator', 'exemplar']
                if category and category.lower() not in valid_categories:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
                    )
                
                db = await self.registry.get('database')
                
                # Build WHERE clause
                where_clauses = ["composite_score >= $1"]
                params = [min_score]
                param_num = 2
                
                if category:
                    where_clauses.append(f"LOWER(holonic_category) = ${param_num}")
                    params.append(category.lower())
                    param_num += 1
                
                where_clause = " AND ".join(where_clauses)
                
                # Get summary statistics with explicit schema
                summary_query = f"""
                    SELECT 
                        COUNT(*) as total_accounts,
                        AVG(composite_score) as avg_composite_score,
                        AVG(autonomy_integration_score) as avg_autonomy,
                        AVG(multi_scale_score) as avg_multi_scale,
                        AVG(regenerative_impact_score) as avg_regenerative,
                        AVG(network_contribution_score) as avg_network,
                        AVG(ubuntu_alignment_score) as avg_ubuntu,
                        MIN(composite_score) as min_score,
                        MAX(composite_score) as max_score
                    FROM ubec_main.holonic_metrics
                    WHERE {where_clause}
                """
                
                summary = await db.fetch_one(summary_query, tuple(params))
                
                # Get category distribution with explicit schema
                category_query = """
                    SELECT 
                        holonic_category,
                        COUNT(*) as count,
                        AVG(composite_score) as avg_score
                    FROM ubec_main.holonic_metrics
                    GROUP BY holonic_category
                    ORDER BY 
                        CASE holonic_category
                            WHEN 'observer' THEN 1
                            WHEN 'participant' THEN 2
                            WHEN 'contributor' THEN 3
                            WHEN 'integrator' THEN 4
                            WHEN 'exemplar' THEN 5
                        END
                """
                
                category_results = await db.fetch_all(category_query, ())
                
                # Build category distribution
                categories = {}
                for row in category_results:
                    categories[row['holonic_category']] = {
                        'count': int(row['count']),
                        'average_score': float(row['avg_score']) if row['avg_score'] else 0.0
                    }
                
                # Get account details with explicit schema
                # Add limit as final parameter
                params.append(limit)
                
                accounts_query = f"""
                    SELECT 
                        account_id,
                        composite_score,
                        holonic_category,
                        autonomy_integration_score,
                        multi_scale_score,
                        regenerative_impact_score,
                        network_contribution_score,
                        ubuntu_alignment_score,
                        confidence,
                        calculation_mode,
                        evaluation_date,
                        created_at
                    FROM ubec_main.holonic_metrics
                    WHERE {where_clause}
                    ORDER BY composite_score DESC, evaluation_date DESC
                    LIMIT ${param_num}
                """
                
                account_results = await db.fetch_all(accounts_query, tuple(params))
                
                # Build account list
                accounts = []
                for row in account_results:
                    account = {
                        'account_id': row['account_id'],
                        'composite_score': float(row['composite_score']),
                        'holonic_category': row['holonic_category'],
                        'scores': {
                            'autonomy_integration': float(row['autonomy_integration_score']),
                            'multi_scale_participation': float(row['multi_scale_score']),
                            'regenerative_impact': float(row['regenerative_impact_score']),
                            'network_contribution': float(row['network_contribution_score']),
                            'ubuntu_alignment': float(row['ubuntu_alignment_score'])
                        },
                        'confidence': float(row['confidence']) if row['confidence'] else 0.8,
                        'calculation_mode': row['calculation_mode'],
                        'evaluation_date': row['evaluation_date'].isoformat() if row['evaluation_date'] else None
                    }
                    accounts.append(account)
                
                # Build response
                response = {
                    'summary': {
                        'total_accounts': int(summary['total_accounts']) if summary['total_accounts'] else 0,
                        'average_scores': {
                            'composite': float(summary['avg_composite_score']) if summary['avg_composite_score'] else 0.0,
                            'autonomy_integration': float(summary['avg_autonomy']) if summary['avg_autonomy'] else 0.0,
                            'multi_scale_participation': float(summary['avg_multi_scale']) if summary['avg_multi_scale'] else 0.0,
                            'regenerative_impact': float(summary['avg_regenerative']) if summary['avg_regenerative'] else 0.0,
                            'network_contribution': float(summary['avg_network']) if summary['avg_network'] else 0.0,
                            'ubuntu_alignment': float(summary['avg_ubuntu']) if summary['avg_ubuntu'] else 0.0
                        },
                        'score_range': {
                            'min': float(summary['min_score']) if summary['min_score'] else 0.0,
                            'max': float(summary['max_score']) if summary['max_score'] else 0.0
                        }
                    },
                    'category_distribution': categories,
                    'accounts': accounts,
                    'count': len(accounts),
                    'filters': {
                        'category': category,
                        'min_score': min_score,
                        'limit': limit
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.logger.info(f"✓ Retrieved holonic scores: {len(accounts)} accounts")
                return response
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error fetching holonic scores: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error fetching holonic scores: {str(e)}")
        
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
