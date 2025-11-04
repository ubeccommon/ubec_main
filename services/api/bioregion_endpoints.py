"""
Bioregion API Endpoints - Add these to services/api/api_service.py

These endpoints expose bioregion_manager functionality via REST API.

Attribution: This project uses the services of Claude and Anthropic PBC to 
inform our decisions and recommendations. This project was made possible with 
the assistance of Claude and Anthropic PBC.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models for API Responses
# ============================================================================

class BioregionSummary(BaseModel):
    """Summary statistics for all bioregions"""
    total_count: int
    total_members: int
    average_size: float
    max_size: int
    largest_bioregion: Optional[str]
    average_autonomy: float
    average_integration: float
    total_area_km2: float

class BioregionDetail(BaseModel):
    """Detailed information about a specific bioregion"""
    id: int
    name: str
    type: str
    member_count: int
    asset_count: int
    autonomy_score: float
    integration_score: float
    area_km2: Optional[float]
    age_days: int
    emerged_at: Optional[str]
    stable_from: Optional[str]
    dissolved_at: Optional[str]
    status: str
    ubuntu_scores: Dict[str, Any]
    emergent_properties: Dict[str, Any]
    health_rating: str

class BioregionListItem(BaseModel):
    """Simplified bioregion info for lists"""
    id: int
    name: str
    member_count: int
    autonomy_score: float
    integration_score: float
    health_rating: str
    status: str

# ============================================================================
# Router Setup (Add to your API service)
# ============================================================================

def create_bioregion_routes(bioregion_manager) -> APIRouter:
    """
    Create bioregion API routes.
    
    Usage in api_service.py:
        bioregion_router = create_bioregion_routes(self.bioregion_manager)
        self.app.include_router(bioregion_router, prefix="/api/v1", tags=["bioregions"])
    """
    router = APIRouter()
    
    @router.get("/bioregions/count", response_model=Dict[str, int])
    async def get_bioregion_count():
        """
        Get total count of active bioregions.
        
        Returns:
            {"count": 12}
        """
        try:
            count = await bioregion_manager.get_bioregion_count()
            return {"count": count}
        except Exception as e:
            logger.error(f"Error getting bioregion count: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/bioregions/summary", response_model=BioregionSummary)
    async def get_bioregion_summary():
        """
        Get summary statistics for all bioregions.
        
        Returns aggregate metrics including:
        - Total bioregion count
        - Total members across all bioregions
        - Average autonomy and integration scores
        - Largest bioregion name
        """
        try:
            summary = await bioregion_manager.get_bioregion_summary()
            return summary
        except Exception as e:
            logger.error(f"Error getting bioregion summary: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/bioregions", response_model=List[BioregionListItem])
    async def list_bioregions(
        include_dissolved: bool = False,
        min_members: int = 1
    ):
        """
        List all bioregions with filtering options.
        
        Query Parameters:
        - include_dissolved: Include dissolved/inactive bioregions (default: False)
        - min_members: Minimum member count to include (default: 1)
        
        Returns list of bioregions with key metrics.
        """
        try:
            bioregions = await bioregion_manager.get_all_bioregions(
                include_dissolved=include_dissolved,
                min_members=min_members
            )
            return bioregions
        except Exception as e:
            logger.error(f"Error listing bioregions: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/bioregions/{bioregion_id}", response_model=BioregionDetail)
    async def get_bioregion(bioregion_id: int):
        """
        Get detailed information about a specific bioregion.
        
        Path Parameters:
        - bioregion_id: Unique identifier of the bioregion
        
        Returns complete bioregion details including:
        - Member and asset counts
        - Ubuntu principle scores
        - Geographic data
        - Lifecycle information
        - Emergent properties
        """
        try:
            bioregion = await bioregion_manager.get_bioregion_by_id(bioregion_id)
            if bioregion is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Bioregion {bioregion_id} not found"
                )
            return bioregion
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting bioregion {bioregion_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/bioregions/{bioregion_id}/health")
    async def get_bioregion_health(bioregion_id: int):
        """
        Get health rating and metrics for a specific bioregion.
        
        Returns health assessment based on:
        - Integration score
        - Autonomy score
        - Member count
        - Ubuntu alignment
        """
        try:
            bioregion = await bioregion_manager.get_bioregion_by_id(bioregion_id)
            if bioregion is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Bioregion {bioregion_id} not found"
                )
            
            return {
                "bioregion_id": bioregion_id,
                "bioregion_name": bioregion["name"],
                "health_rating": bioregion["health_rating"],
                "autonomy_score": bioregion["autonomy_score"],
                "integration_score": bioregion["integration_score"],
                "member_count": bioregion["member_count"]
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting bioregion health: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router


# ============================================================================
# Integration Instructions
# ============================================================================
"""
To integrate these endpoints into your API service:

1. In services/api/api_service.py, add this import:
   from .bioregion_api_endpoints import create_bioregion_routes

2. In the BackendAPIService.__init__ method, after creating self.app:
   
   # Add bioregion routes
   bioregion_router = create_bioregion_routes(self.bioregion_manager)
   self.app.include_router(
       bioregion_router,
       prefix="/api/v1",
       tags=["bioregions"]
   )

3. Make sure bioregion_manager is accessible:
   self.bioregion_manager = await registry.get('bioregion_manager')

4. Test the endpoints:
   curl http://localhost:8000/api/v1/bioregions/count
   curl http://localhost:8000/api/v1/bioregions/summary
   curl http://localhost:8000/api/v1/bioregions

5. View in Swagger docs:
   http://localhost:8000/docs
"""
