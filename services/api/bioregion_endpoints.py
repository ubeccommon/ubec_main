#!/usr/bin/env python3
"""
Bioregion API Endpoints - FastAPI Router for Bioregion Data
============================================================
Exposes bioregion_manager functionality via REST API endpoints.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Separate router module for bioregion endpoints
    ✅ #2  Service Pattern: Used by API service only, no standalone execution
    ✅ #3  Service Registry: Uses injected bioregion_manager
    ✅ #4  Single Source of Truth: Data from bioregion_manager/database
    ✅ #5  Strict Async: 100% async/await throughout
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Individual endpoint rate limits
    ✅ #8  No Duplicate Configuration: Single limiter instance passed
    ✅ #9  Integrated Rate Limiting: All endpoints have @limiter.limit()
    ✅ #10 Separation of Concerns: Router logic separated from business logic
    ✅ #11 Comprehensive Documentation: Full docstrings
    ✅ #12 Method Singularity: Each route implemented once
════════════════════════════════════════════════════════════════════════════

Attribution: This project uses the services of Claude and Anthropic PBC to 
inform our decisions and recommendations. This project was made possible with 
the assistance of Claude and Anthropic PBC.

Usage in api_service.py:
    ```python
    from .bioregion_endpoints import create_bioregion_router
    
    # In BackendAPIService._setup_routes():
    bioregion_router = create_bioregion_router(
        self.bioregion_manager,
        limiter
    )
    self.app.include_router(
        bioregion_router,
        prefix="/api/v1",
        tags=["bioregions"]
    )
    ```

Author: UBEC Protocol Development Team
Version: 1.0.0
Created: 2025-11-09
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Router Factory Function
# ============================================================================

def create_bioregion_router(bioregion_manager, limiter) -> APIRouter:
    """
    Create and configure bioregion API router with rate limiting.
    
    This function is called by BackendAPIService during initialization
    to create a router with all bioregion endpoints.
    
    Args:
        bioregion_manager: BioregionManager service instance (injected)
        limiter: SlowAPI Limiter instance for rate limiting (injected)
        
    Returns:
        Configured APIRouter with all bioregion endpoints
        
    Design Notes:
        - Principle #2: No standalone execution, used by API service only
        - Principle #3: Dependencies injected, not imported
        - Principle #5: All operations are async
        - Principle #9: Rate limiting applied to all endpoints
    """
    router = APIRouter()
    
    # ========================================================================
    # Endpoint 1: Bioregion Count
    # ========================================================================
    
    @router.get("/bioregions/count", response_model=Dict[str, Any])
    @limiter.limit("100/minute")
    async def get_bioregion_count(request: Request) -> Dict[str, Any]:
        """
        Get total count of active bioregions.
        
        Rate limit: 100 requests/minute per IP
        
        Returns:
            {
                "count": 12,
                "timestamp": "2025-11-09T10:30:00Z"
            }
        
        Example:
            curl http://localhost:8000/api/v1/bioregions/count
        """
        try:
            count = await bioregion_manager.get_bioregion_count()
            
            response = {
                'count': count,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✓ Retrieved bioregion count: {count}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting bioregion count: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail=f"Error retrieving bioregion count: {str(e)}"
            )
    
    # ========================================================================
    # Endpoint 2: Bioregion Summary Statistics
    # ========================================================================
    
    @router.get("/bioregions/summary", response_model=Dict[str, Any])
    @limiter.limit("100/minute")
    async def get_bioregion_summary(request: Request) -> Dict[str, Any]:
        """
        Get summary statistics for all bioregions.
        
        Rate limit: 100 requests/minute per IP
        
        Returns comprehensive statistics including:
        - Total count and member count
        - Average autonomy and integration scores
        - Size metrics (average, max, largest)
        - Total geographic area
        
        Example:
            curl http://localhost:8000/api/v1/bioregions/summary
        """
        try:
            summary = await bioregion_manager.get_bioregion_summary()
            
            # Add timestamp to response
            summary['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            logger.info(
                f"✓ Retrieved bioregion summary: "
                f"{summary.get('total_count', 0)} bioregions"
            )
            return summary
            
        except Exception as e:
            logger.error(f"Error getting bioregion summary: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving bioregion summary: {str(e)}"
            )
    
    # ========================================================================
    # Endpoint 3: All Bioregions List
    # ========================================================================
    
    @router.get("/bioregions", response_model=Dict[str, Any])
    @limiter.limit("100/minute")
    async def get_all_bioregions(
        request: Request,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        include_dissolved: bool = False,
        min_members: int = 1
    ) -> Dict[str, Any]:
        """
        Get detailed list of all bioregions with optional filtering and pagination.
        
        Rate limit: 100 requests/minute per IP
        
        Query Parameters:
            limit: Maximum number of results (1-100, default: 50)
            offset: Pagination offset (default: 0)
            status: Filter by status ('active', 'forming', 'dissolved')
            include_dissolved: If True, include dissolved bioregions (default: False)
            min_members: Minimum number of members to include bioregion (default: 1)
        
        Returns:
            {
                "bioregions": [...],
                "count": 50,
                "total": 150,
                "limit": 50,
                "offset": 0,
                "timestamp": "2025-11-09T10:30:00Z"
            }
        
        Example:
            curl "http://localhost:8000/api/v1/bioregions?limit=10&status=active"
        """
        try:
            # Validate and constrain limit
            limit = max(1, min(100, limit))
            offset = max(0, offset)
            
            # Get bioregions from manager
            bioregions = await bioregion_manager.get_all_bioregions(
                include_dissolved=include_dissolved,
                min_members=min_members
            )
            
            # Apply status filter if specified
            if status:
                bioregions = [
                    b for b in bioregions 
                    if b.get('status', '').lower() == status.lower()
                ]
            
            # Get total before pagination
            total = len(bioregions)
            
            # Apply pagination
            paginated = bioregions[offset:offset + limit]
            
            response = {
                'bioregions': paginated,
                'count': len(paginated),
                'total': total,
                'limit': limit,
                'offset': offset,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(
                f"✓ Retrieved {len(paginated)} bioregions "
                f"(total: {total}, offset: {offset})"
            )
            return response
            
        except Exception as e:
            logger.error(f"Error getting bioregions: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving bioregions: {str(e)}"
            )
    
    # ========================================================================
    # Endpoint 4: Specific Bioregion Details
    # ========================================================================
    
    @router.get("/bioregions/{bioregion_id}", response_model=Dict[str, Any])
    @limiter.limit("100/minute")
    async def get_bioregion_by_id(
        request: Request,
        bioregion_id: int
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific bioregion.
        
        Rate limit: 100 requests/minute per IP
        
        Path Parameters:
            bioregion_id: Bioregion ID (integer)
        
        Returns:
            Detailed bioregion information including:
            - Member and asset counts
            - Autonomy and integration scores
            - Ubuntu principle scores
            - Geographic data (area, boundaries)
            - Lifecycle information (emerged, stable, dissolved dates)
            - Emergent properties and collective behavior
        
        Raises:
            404: Bioregion not found
            500: Server error
        
        Example:
            curl http://localhost:8000/api/v1/bioregions/1
        """
        try:
            bioregion = await bioregion_manager.get_bioregion_by_id(bioregion_id)
            
            if not bioregion:
                raise HTTPException(
                    status_code=404,
                    detail=f"Bioregion {bioregion_id} not found"
                )
            
            # Add timestamp
            bioregion['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"✓ Retrieved bioregion {bioregion_id}: {bioregion.get('name')}")
            return bioregion
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error getting bioregion {bioregion_id}: {e}", 
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving bioregion: {str(e)}"
            )
    
    # ========================================================================
    # Endpoint 5: Bioregion Health Assessment
    # ========================================================================
    
    @router.get("/bioregions/{bioregion_id}/health", response_model=Dict[str, Any])
    @limiter.limit("100/minute")
    async def get_bioregion_health(
        request: Request,
        bioregion_id: int
    ) -> Dict[str, Any]:
        """
        Get health rating and metrics for a specific bioregion.
        
        Rate limit: 100 requests/minute per IP
        
        Path Parameters:
            bioregion_id: Bioregion ID (integer)
        
        Returns health assessment based on:
        - Integration score (community cohesion)
        - Autonomy score (self-sufficiency)
        - Member count (community size)
        - Ubuntu alignment (principle adherence)
        
        Health Ratings:
        - excellent: Composite score >= 0.8
        - good: Composite score >= 0.6
        - fair: Composite score >= 0.4
        - poor: Composite score < 0.4
        
        Raises:
            404: Bioregion not found
            500: Server error
        
        Example:
            curl http://localhost:8000/api/v1/bioregions/1/health
        """
        try:
            bioregion = await bioregion_manager.get_bioregion_by_id(bioregion_id)
            
            if not bioregion:
                raise HTTPException(
                    status_code=404,
                    detail=f"Bioregion {bioregion_id} not found"
                )
            
            response = {
                'bioregion_id': bioregion_id,
                'bioregion_name': bioregion['name'],
                'health_rating': bioregion['health_rating'],
                'autonomy_score': bioregion['autonomy_score'],
                'integration_score': bioregion['integration_score'],
                'member_count': bioregion['member_count'],
                'status': bioregion['status'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(
                f"✓ Retrieved health for bioregion {bioregion_id}: "
                f"{bioregion['health_rating']}"
            )
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error getting bioregion health {bioregion_id}: {e}", 
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving bioregion health: {str(e)}"
            )
    
    return router


# ============================================================================
# Integration Instructions
# ============================================================================
"""
INTEGRATION STEPS FOR services/api/api_service.py:

1. Add import at top of file:
   ───────────────────────────────────────────────────────────────────────
   from .bioregion_endpoints import create_bioregion_router

2. In BackendAPIService.initialize() method:
   ───────────────────────────────────────────────────────────────────────
   # Get bioregion manager from registry
   try:
       self.bioregion_manager = await self.registry.get('bioregion_manager')
       self.logger.info("✓ BioregionManager connected to API service")
   except Exception as e:
       self.logger.warning(f"BioregionManager not available: {e}")
       self.bioregion_manager = None

3. In BackendAPIService._setup_routes() method (at end):
   ───────────────────────────────────────────────────────────────────────
   # Bioregion Endpoints Integration
   if self.bioregion_manager:
       try:
           bioregion_router = create_bioregion_router(
               self.bioregion_manager,
               limiter
           )
           
           self.app.include_router(
               bioregion_router,
               prefix="/api/v1",
               tags=["bioregions"]
           )
           
           self.logger.info("✓ Bioregion endpoints registered")
           
       except Exception as e:
           self.logger.error(f"Failed to register bioregion endpoints: {e}")
   else:
       self.logger.warning("Bioregion endpoints skipped - manager not available")

4. In BackendAPIService.__init__() method:
   ───────────────────────────────────────────────────────────────────────
   self.bioregion_manager = None  # Will be set in initialize()

5. Test endpoints:
   ───────────────────────────────────────────────────────────────────────
   curl http://localhost:8000/api/v1/bioregions/count
   curl http://localhost:8000/api/v1/bioregions/summary
   curl http://localhost:8000/api/v1/bioregions
   curl http://localhost:8000/api/v1/bioregions/1
   curl http://localhost:8000/api/v1/bioregions/1/health

6. View Swagger documentation:
   ───────────────────────────────────────────────────────────────────────
   http://localhost:8000/docs
   
   Should show "bioregions" tag with 5 endpoints.

7. Verify rate limiting:
   ───────────────────────────────────────────────────────────────────────
   # Test rate limit (100 requests/minute)
   for i in {1..101}; do
     curl -s http://localhost:8000/api/v1/bioregions/count > /dev/null
     echo "Request $i"
   done
   # Expected: First 100 succeed, 101st returns 429 Too Many Requests

CRITICAL REMINDERS:
- ALL endpoints require 'request: Request' parameter for rate limiting
- ALL endpoints must have @limiter.limit() decorator AFTER @router.get()
- Limiter must be passed to create_bioregion_router() function
- All responses include timestamp for consistency
- Use Dict[str, Any] for response_model (flexible dict responses)
"""
