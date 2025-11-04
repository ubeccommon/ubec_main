#!/usr/bin/env python3
"""
UBEC Bioregion Manager Service - Production Version 1.0
=========================================================
Tracks and manages bioregional holons representing geographic economic communities.

A bioregion is a geographic area defined by natural characteristics (watersheds,
climate, ecosystems) and local culture. This service identifies, tracks, and
analyzes bioregional economic commons within the UBEC network.

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #1  Modular Design: Self-contained bioregion tracking module
    ✅ #2  Service Pattern: No standalone execution, registry-managed
    ✅ #3  Service Registry: Full dependency injection via registry
    ✅ #4  Single Source of Truth: Database-backed bioregion data
    ✅ #5  Strict Async: 100% async/await throughout
    ✅ #6  No Sync Fallbacks: Pure async implementation
    ✅ #7  Per-Asset Monitoring: Health checks with detailed metrics
    ✅ #8  No Duplicate Configuration: Configuration from registry
    ✅ #9  Integrated Rate Limiting: N/A (database-only operations)
    ✅ #10 Separation of Concerns: Bioregion logic isolated
    ✅ #11 Comprehensive Documentation: Full docstrings
    ✅ #12 Method Singularity: Each method implemented once
════════════════════════════════════════════════════════════════════════════

Attribution: This project uses the services of Claude and Anthropic PBC to 
inform our decisions and recommendations. This project was made possible with 
the assistance of Claude and Anthropic PBC.

Usage Example:
    ```python
    from core.service_registry import ServiceRegistry
    
    # Initialize via service registry (proper pattern)
    registry = ServiceRegistry()
    bioregion_mgr = await registry.get('bioregion_manager')
    
    # Get bioregion count
    count = await bioregion_mgr.get_bioregion_count()
    
    # Get bioregion details
    regions = await bioregion_mgr.get_all_bioregions()
    
    # Create/update bioregion from network analysis
    await bioregion_mgr.identify_and_create_bioregions()
    ```

Author: UBEC Protocol Development Team
Version: 1.0.0
Created: 2025-11-04
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from decimal import Decimal

logger = logging.getLogger(__name__)


class BioregionManager:
    """
    Bioregion Manager Service for UBEC Protocol.
    
    Manages bioregional holons - geographic economic communities defined by
    natural boundaries (watersheds, ecosystems) and cultural characteristics.
    
    A bioregion in UBEC represents:
    - Geographic clustering of economic activity
    - Shared natural resources and boundaries
    - Cultural and local knowledge systems
    - Regenerative economic practices aligned with local ecosystems
    
    This service:
    - Identifies bioregions from network topology and spatial data
    - Tracks bioregion membership and boundaries
    - Calculates bioregion health metrics (autonomy, integration, ubuntu scores)
    - Provides bioregion analytics for dashboard and reporting
    
    Attributes:
        db: Database manager instance (injected via registry)
        logger: Logger instance for this service
        _cache: In-memory cache for performance
        _cache_ttl: Cache time-to-live in seconds
        _last_cache_update: Timestamp of last cache update
    """
    
    def __init__(self, database_manager):
        """
        Initialize Bioregion Manager.
        
        Args:
            database_manager: AsyncDatabaseManager instance from service registry
        """
        self.db = database_manager
        self.logger = logger
        
        # Simple caching for performance
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 60  # seconds
        self._last_cache_update: Optional[datetime] = None
        
        self.logger.info("BioregionManager initialized")
    
    async def initialize(self) -> None:
        """
        Initialize service and verify database connectivity.
        
        Called by service registry during system startup.
        """
        self.logger.info("Initializing BioregionManager service")
        
        # Verify database connectivity
        health = await self.db.health_check()
        if not health.get('connected'):
            raise RuntimeError("Database not connected - cannot initialize BioregionManager")
        
        # Verify phenomenal schema exists
        schema_check = await self.db.fetch_one(
            """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'phenomenal'
            """,
            ()
        )
        
        if not schema_check:
            self.logger.warning("Phenomenal schema not found - bioregion tracking will be limited")
        
        self.logger.info("BioregionManager initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for monitoring.
        
        Returns:
            Dict containing health status and metrics
            
        Example:
            {
                'service': 'BioregionManager',
                'status': 'healthy',
                'database_connected': True,
                'bioregion_count': 12,
                'cache_age_seconds': 45,
                'last_update': '2025-11-04T10:30:00Z'
            }
        """
        try:
            # Check database connectivity
            db_health = await self.db.health_check()
            db_connected = db_health.get('connected', False)
            
            # Get bioregion count
            count = await self.get_bioregion_count()
            
            # Calculate cache age
            cache_age = 0
            if self._last_cache_update:
                cache_age = (datetime.now(timezone.utc) - self._last_cache_update).total_seconds()
            
            status = 'healthy' if db_connected else 'unhealthy'
            
            return {
                'service': 'BioregionManager',
                'version': '1.0.0',
                'status': status,
                'database_connected': db_connected,
                'bioregion_count': count,
                'cache_age_seconds': int(cache_age),
                'last_update': datetime.now(timezone.utc).isoformat(),
                'phenomenal_schema_available': await self._check_phenomenal_schema()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'service': 'BioregionManager',
                'version': '1.0.0',
                'status': 'unhealthy',
                'error': str(e),
                'last_update': datetime.now(timezone.utc).isoformat()
            }
    
    async def _check_phenomenal_schema(self) -> bool:
        """Check if phenomenal schema is available."""
        try:
            result = await self.db.fetch_one(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'phenomenal'",
                ()
            )
            return result is not None
        except Exception:
            return False
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid based on TTL."""
        if not self._last_cache_update:
            return False
        
        age = (datetime.now(timezone.utc) - self._last_cache_update).total_seconds()
        return age < self._cache_ttl
    
    def _update_cache(self, key: str, value: Any) -> None:
        """Update cache with new value."""
        self._cache[key] = value
        self._last_cache_update = datetime.now(timezone.utc)
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if still valid."""
        if self._is_cache_valid() and key in self._cache:
            return self._cache[key]
        return None
    
    # ========================================================================
    # Core Bioregion Queries
    # ========================================================================
    
    async def get_bioregion_count(self) -> int:
        """
        Get total count of active bioregions.
        
        A bioregion is counted if it's a holon with:
        - holon_type = 'bioregion'
        - dissolved_at IS NULL (still active)
        - Has at least one constituent account
        
        Returns:
            Integer count of active bioregions
            
        Example:
            >>> count = await bioregion_mgr.get_bioregion_count()
            >>> print(f"Active bioregions: {count}")
            Active bioregions: 12
        """
        # Check cache first
        cached = self._get_cached('bioregion_count')
        if cached is not None:
            return cached
        
        try:
            # Query phenomenal.holons table for bioregions
            result = await self.db.fetch_one(
                """
                SELECT COUNT(*) as count
                FROM phenomenal.holons
                WHERE holon_type = 'bioregion'
                  AND dissolved_at IS NULL
                  AND constituent_accounts IS NOT NULL
                  AND array_length(constituent_accounts, 1) > 0
                """,
                ()
            )
            
            count = result['count'] if result else 0
            
            # Update cache
            self._update_cache('bioregion_count', count)
            
            self.logger.info(f"Found {count} active bioregions")
            return count
            
        except Exception as e:
            self.logger.error(f"Error getting bioregion count: {e}")
            # Return 0 instead of failing - graceful degradation
            return 0
    
    async def get_all_bioregions(
        self, 
        include_dissolved: bool = False,
        min_members: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get all bioregions with detailed information.
        
        Args:
            include_dissolved: If True, include dissolved bioregions
            min_members: Minimum number of members to include bioregion
            
        Returns:
            List of bioregion dictionaries with detailed information
            
        Example:
            >>> regions = await bioregion_mgr.get_all_bioregions()
            >>> for region in regions:
            ...     print(f"{region['name']}: {region['member_count']} members")
            Pacific Northwest: 87 members
            Great Lakes: 65 members
        """
        try:
            query = """
                SELECT 
                    h.id,
                    h.holon_name,
                    h.holon_type,
                    h.autonomy_score,
                    h.integration_score,
                    h.constituent_accounts,
                    h.constituent_assets,
                    h.emergent_properties,
                    h.ubuntu_scores,
                    h.emerged_at,
                    h.stable_from,
                    h.dissolved_at,
                    array_length(h.constituent_accounts, 1) as member_count,
                    array_length(h.constituent_assets, 1) as asset_count,
                    ST_Area(h.spatial_region::geography) / 1000000.0 as area_km2,
                    ST_AsGeoJSON(h.centroid) as centroid_geojson,
                    EXTRACT(days FROM (NOW() - h.emerged_at)) as age_days
                FROM phenomenal.holons h
                WHERE h.holon_type = 'bioregion'
                  AND array_length(h.constituent_accounts, 1) >= $1
            """
            
            if not include_dissolved:
                query += " AND h.dissolved_at IS NULL"
            
            query += " ORDER BY h.integration_score DESC, array_length(h.constituent_accounts, 1) DESC"
            
            results = await self.db.fetch_all(query, (min_members,))
            
            bioregions = []
            for row in results:
                bioregion = {
                    'id': row['id'],
                    'name': row['holon_name'],
                    'type': row['holon_type'],
                    'member_count': row['member_count'] or 0,
                    'asset_count': row['asset_count'] or 0,
                    'autonomy_score': float(row['autonomy_score']) if row['autonomy_score'] else 0.0,
                    'integration_score': float(row['integration_score']) if row['integration_score'] else 0.0,
                    'area_km2': float(row['area_km2']) if row['area_km2'] else None,
                    'age_days': int(row['age_days']) if row['age_days'] else 0,
                    'emerged_at': row['emerged_at'].isoformat() if row['emerged_at'] else None,
                    'stable_from': row['stable_from'].isoformat() if row['stable_from'] else None,
                    'dissolved_at': row['dissolved_at'].isoformat() if row['dissolved_at'] else None,
                    'status': 'active' if not row['dissolved_at'] else 'dissolved',
                    'ubuntu_scores': dict(row['ubuntu_scores']) if row['ubuntu_scores'] else {},
                    'emergent_properties': dict(row['emergent_properties']) if row['emergent_properties'] else {}
                }
                
                # Calculate health rating
                bioregion['health_rating'] = self._calculate_health_rating(bioregion)
                
                bioregions.append(bioregion)
            
            self.logger.info(f"Retrieved {len(bioregions)} bioregions")
            return bioregions
            
        except Exception as e:
            self.logger.error(f"Error getting all bioregions: {e}")
            return []
    
    async def get_bioregion_by_id(self, bioregion_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific bioregion.
        
        Args:
            bioregion_id: ID of the bioregion holon
            
        Returns:
            Dictionary with bioregion details or None if not found
        """
        try:
            result = await self.db.fetch_one(
                """
                SELECT 
                    h.id,
                    h.holon_name,
                    h.holon_type,
                    h.autonomy_score,
                    h.integration_score,
                    h.constituent_accounts,
                    h.constituent_assets,
                    h.emergent_properties,
                    h.collective_behavior,
                    h.ubuntu_scores,
                    h.emerged_at,
                    h.stable_from,
                    h.dissolved_at,
                    array_length(h.constituent_accounts, 1) as member_count,
                    array_length(h.constituent_assets, 1) as asset_count,
                    ST_Area(h.spatial_region::geography) / 1000000.0 as area_km2,
                    ST_AsGeoJSON(h.spatial_region) as region_geojson,
                    ST_AsGeoJSON(h.centroid) as centroid_geojson
                FROM phenomenal.holons h
                WHERE h.id = $1
                """,
                (bioregion_id,)
            )
            
            if not result:
                return None
            
            return {
                'id': result['id'],
                'name': result['holon_name'],
                'type': result['holon_type'],
                'member_count': result['member_count'] or 0,
                'asset_count': result['asset_count'] or 0,
                'autonomy_score': float(result['autonomy_score']) if result['autonomy_score'] else 0.0,
                'integration_score': float(result['integration_score']) if result['integration_score'] else 0.0,
                'area_km2': float(result['area_km2']) if result['area_km2'] else None,
                'emerged_at': result['emerged_at'].isoformat() if result['emerged_at'] else None,
                'stable_from': result['stable_from'].isoformat() if result['stable_from'] else None,
                'dissolved_at': result['dissolved_at'].isoformat() if result['dissolved_at'] else None,
                'status': 'active' if not result['dissolved_at'] else 'dissolved',
                'ubuntu_scores': dict(result['ubuntu_scores']) if result['ubuntu_scores'] else {},
                'emergent_properties': dict(result['emergent_properties']) if result['emergent_properties'] else {},
                'collective_behavior': dict(result['collective_behavior']) if result['collective_behavior'] else {},
                'region_geojson': result['region_geojson'],
                'centroid_geojson': result['centroid_geojson']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting bioregion {bioregion_id}: {e}")
            return None
    
    async def get_bioregion_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for all bioregions.
        
        Returns:
            Dictionary with summary statistics
            
        Example:
            {
                'total_count': 12,
                'total_members': 495,
                'average_size': 41.25,
                'largest_bioregion': 'Pacific Northwest',
                'average_autonomy': 0.68,
                'average_integration': 0.72
            }
        """
        try:
            result = await self.db.fetch_one(
                """
                SELECT 
                    COUNT(*) as bioregion_count,
                    SUM(array_length(constituent_accounts, 1)) as total_members,
                    AVG(array_length(constituent_accounts, 1)) as avg_members,
                    MAX(array_length(constituent_accounts, 1)) as max_members,
                    AVG(autonomy_score) as avg_autonomy,
                    AVG(integration_score) as avg_integration,
                    SUM(ST_Area(spatial_region::geography) / 1000000.0) as total_area_km2
                FROM phenomenal.holons
                WHERE holon_type = 'bioregion'
                  AND dissolved_at IS NULL
                """,
                ()
            )
            
            if not result:
                return {
                    'total_count': 0,
                    'total_members': 0,
                    'average_size': 0,
                    'average_autonomy': 0,
                    'average_integration': 0
                }
            
            # Get largest bioregion name
            largest = await self.db.fetch_one(
                """
                SELECT holon_name
                FROM phenomenal.holons
                WHERE holon_type = 'bioregion'
                  AND dissolved_at IS NULL
                ORDER BY array_length(constituent_accounts, 1) DESC
                LIMIT 1
                """,
                ()
            )
            
            return {
                'total_count': int(result['bioregion_count']) if result['bioregion_count'] else 0,
                'total_members': int(result['total_members']) if result['total_members'] else 0,
                'average_size': float(result['avg_members']) if result['avg_members'] else 0.0,
                'max_size': int(result['max_members']) if result['max_members'] else 0,
                'largest_bioregion': largest['holon_name'] if largest else None,
                'average_autonomy': float(result['avg_autonomy']) if result['avg_autonomy'] else 0.0,
                'average_integration': float(result['avg_integration']) if result['avg_integration'] else 0.0,
                'total_area_km2': float(result['total_area_km2']) if result['total_area_km2'] else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting bioregion summary: {e}")
            return {
                'total_count': 0,
                'total_members': 0,
                'average_size': 0,
                'average_autonomy': 0,
                'average_integration': 0
            }
    
    # ========================================================================
    # Bioregion Creation and Management
    # ========================================================================
    
    async def identify_and_create_bioregions(
        self,
        min_members: int = 10,
        min_density: float = 0.3,
        algorithm: str = 'spatial_clustering'
    ) -> List[int]:
        """
        Identify and create bioregions from network analysis.
        
        This method analyzes the account network to identify natural clusters
        that represent bioregional communities based on:
        - Spatial proximity (if position data available)
        - Transaction patterns and relationships
        - Shared assets and economic activity
        - Cultural/natural boundary indicators
        
        Args:
            min_members: Minimum accounts required for a bioregion
            min_density: Minimum connection density threshold
            algorithm: Clustering algorithm ('spatial_clustering', 'community_detection')
            
        Returns:
            List of newly created bioregion IDs
            
        Note:
            This is a complex operation that may take several seconds for large networks.
            Consider running as a background task for production systems.
        """
        self.logger.info(f"Identifying bioregions with algorithm: {algorithm}")
        
        try:
            # TODO: Implement sophisticated clustering algorithms
            # For now, return empty list - this is a placeholder for future enhancement
            self.logger.warning("Bioregion identification not yet implemented - placeholder method")
            return []
            
        except Exception as e:
            self.logger.error(f"Error identifying bioregions: {e}")
            return []
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _calculate_health_rating(self, bioregion: Dict[str, Any]) -> str:
        """
        Calculate overall health rating for a bioregion.
        
        Based on:
        - Integration score (how unified)
        - Autonomy score (how independent)
        - Member count (community size)
        - Ubuntu scores (principle alignment)
        
        Returns:
            Health rating: 'excellent', 'good', 'fair', 'poor'
        """
        integration = bioregion.get('integration_score', 0)
        autonomy = bioregion.get('autonomy_score', 0)
        member_count = bioregion.get('member_count', 0)
        
        # Calculate composite score
        composite = (integration + autonomy) / 2
        
        # Adjust for community size
        if member_count < 10:
            composite *= 0.8  # Penalty for small size
        elif member_count > 50:
            composite *= 1.1  # Bonus for large, stable community
        
        # Determine rating
        if composite >= 0.8:
            return 'excellent'
        elif composite >= 0.6:
            return 'good'
        elif composite >= 0.4:
            return 'fair'
        else:
            return 'poor'
    
    async def close(self) -> None:
        """
        Clean up resources.
        
        Called by service registry during system shutdown.
        """
        self.logger.info("Closing BioregionManager service")
        self._cache.clear()


# ============================================================================
# Service Factory Function for Registry Integration
# ============================================================================

async def create_bioregion_manager(registry) -> BioregionManager:
    """
    Factory function to create BioregionManager instance.
    
    This function is called by the ServiceRegistry to instantiate the service
    with proper dependency injection.
    
    Args:
        registry: ServiceRegistry instance providing dependencies
        
    Returns:
        Initialized BioregionManager instance
        
    Example:
        # In main.py service registration
        registry.register_factory(
            'bioregion_manager',
            create_bioregion_manager,
            dependencies=['database']
        )
    """
    database = await registry.get('database')
    manager = BioregionManager(database)
    await manager.initialize()
    return manager
