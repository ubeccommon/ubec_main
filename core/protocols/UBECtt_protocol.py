#!/usr/bin/env python3
# core/protocols/UBECtt_protoco.py
"""
UBECtt Protocol - Transform Token (Fire Element)
================================================

The Fire Element of the Ubuntu EcoCoin four-element protocol system.
UBECtt represents transformative actions, catalytic change, and regenerative impact.

Element Role: FIRE - Transformation & Catalytic Change
Token Symbol: UBECtt
Issuer: [To be configured in settings]

Core Functions:
1. Track transformative community actions
2. Measure catalytic impact and ripple effects
3. Reward regenerative contributions
4. Facilitate system-wide transformation
5. Enable phase transitions in community evolution

Ubuntu Principle Alignment: REGENERATION
- Measures: Transformative actions, renewal capacity, systemic impact
- Element Role: Catalyst for change and evolution
- Scoring: Impact magnitude, transformation rate, regeneration depth

Design Principles Compliance:
- ✅ Modular Design: Self-contained service with clear boundaries
- ✅ Service Pattern: No standalone execution, only service interface
- ✅ Async Operations: All I/O operations use async/await
- ✅ Single Source of Truth: Database is authoritative data source
- ✅ No Sync Fallbacks: Pure async implementation
- ✅ Service Registry Compatible: Designed for dependency injection
- ✅ Rate Limiting: Built-in for all external API calls
- ✅ Separation of Concerns: Clean layer separation
- ✅ Method Singularity: No duplicate implementations

"You never change things by fighting the existing reality.
To change something, build a new model that makes the existing model obsolete."
- R. Buckminster Fuller

This project uses the services of Claude and Anthropic PBC to inform our decisions 
and recommendations. This project was made possible with the assistance of Claude 
and Anthropic PBC.
"""

import os
import asyncio
import logging
import json
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import aiohttp
from contextlib import asynccontextmanager

# Configure precision for decimal calculations
getcontext().prec = 10

# Setup logging
logger = logging.getLogger("UBECtt")


# ==================== ENUMERATIONS ====================

class TransformationType(Enum):
    """Types of transformative actions in the Ubuntu Economic Commons"""
    INDIVIDUAL_GROWTH = "individual_growth"           # Personal development & learning
    COMMUNITY_BUILDING = "community_building"         # Creating connections & networks
    RESOURCE_REGENERATION = "resource_regeneration"   # Ecological restoration
    KNOWLEDGE_CREATION = "knowledge_creation"         # Innovation & education
    SYSTEM_EVOLUTION = "system_evolution"             # Infrastructure improvements
    CULTURAL_SHIFT = "cultural_shift"                 # Mindset & paradigm changes
    ECONOMIC_TRANSITION = "economic_transition"       # New economic models
    SOCIAL_HEALING = "social_healing"                 # Conflict resolution & reconciliation


class ImpactScale(Enum):
    """Scale of impact for transformative actions"""
    MICRO = "micro"           # Individual level (1-10 people)
    MESO = "meso"             # Community level (10-100 people)
    MACRO = "macro"           # Regional level (100-1000 people)
    META = "meta"             # System level (1000+ people)


# ==================== DATA CLASSES ====================

@dataclass
class TransformativeAction:
    """Represents a transformative action or contribution"""
    action_id: str
    agent_id: str                                      # Stellar address of the agent
    action_type: TransformationType
    description: str
    impact_scale: ImpactScale
    timestamp: datetime
    
    # Impact metrics
    direct_beneficiaries: int = 0                      # Number of people directly affected
    indirect_reach: int = 0                            # Estimated ripple effect reach
    regeneration_score: Decimal = Decimal('0.0')      # 0.0 - 1.0
    catalytic_multiplier: Decimal = Decimal('1.0')    # How much it amplifies other actions
    
    # Verification & validation
    verified: bool = False
    verifier_ids: List[str] = field(default_factory=list)
    evidence_urls: List[str] = field(default_factory=list)
    
    # Token economics
    ubectt_awarded: Decimal = Decimal('0.0')
    distribution_tx_hash: Optional[str] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    related_actions: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def calculate_transformation_score(self) -> Decimal:
        """
        Calculate the overall transformation score for this action.
        
        Factors:
        - Impact scale (micro to meta)
        - Regeneration depth
        - Catalytic potential
        - Network effects
        - Verification status
        
        Returns:
            Decimal: Score from 0.0 to 1.0
        """
        # Base score from impact scale
        scale_weights = {
            ImpactScale.MICRO: Decimal('0.25'),
            ImpactScale.MESO: Decimal('0.50'),
            ImpactScale.MACRO: Decimal('0.75'),
            ImpactScale.META: Decimal('1.00')
        }
        base_score = scale_weights.get(self.impact_scale, Decimal('0.25'))
        
        # Factor in regeneration depth
        regeneration_factor = self.regeneration_score
        
        # Factor in catalytic multiplier (capped at 2.0 for calculation)
        catalytic_factor = min(self.catalytic_multiplier, Decimal('2.0')) / Decimal('2.0')
        
        # Verification bonus
        verification_bonus = Decimal('0.2') if self.verified else Decimal('0.0')
        
        # Calculate composite score
        raw_score = (
            base_score * Decimal('0.4') +
            regeneration_factor * Decimal('0.3') +
            catalytic_factor * Decimal('0.2') +
            verification_bonus * Decimal('0.1')
        )
        
        # Normalize to 0.0 - 1.0 range
        return min(max(raw_score, Decimal('0.0')), Decimal('1.0'))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['action_type'] = self.action_type.value
        data['impact_scale'] = self.impact_scale.value
        data['timestamp'] = self.timestamp.isoformat()
        data['regeneration_score'] = str(self.regeneration_score)
        data['catalytic_multiplier'] = str(self.catalytic_multiplier)
        data['ubectt_awarded'] = str(self.ubectt_awarded)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TransformativeAction':
        """Create from dictionary"""
        data['action_type'] = TransformationType(data['action_type'])
        data['impact_scale'] = ImpactScale(data['impact_scale'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['regeneration_score'] = Decimal(str(data.get('regeneration_score', '0.0')))
        data['catalytic_multiplier'] = Decimal(str(data.get('catalytic_multiplier', '1.0')))
        data['ubectt_awarded'] = Decimal(str(data.get('ubectt_awarded', '0.0')))
        return cls(**data)


@dataclass
class TransformationPhase:
    """Represents a phase in community or system transformation"""
    phase_id: str
    name: str
    description: str
    start_date: datetime
    end_date: Optional[datetime] = None
    
    # Phase characteristics
    target_outcomes: List[str] = field(default_factory=list)
    key_indicators: Dict[str, Decimal] = field(default_factory=dict)
    participating_agents: List[str] = field(default_factory=list)
    
    # Progress tracking
    actions_completed: int = 0
    total_ubectt_distributed: Decimal = Decimal('0.0')
    phase_momentum: Decimal = Decimal('0.0')          # Rate of transformation
    
    # Status
    is_active: bool = True
    completion_percentage: Decimal = Decimal('0.0')
    
    def calculate_phase_momentum(self, recent_actions: List[TransformativeAction]) -> Decimal:
        """
        Calculate the momentum of transformation in this phase.
        
        Args:
            recent_actions: List of recent transformative actions
            
        Returns:
            Decimal: Momentum score from 0.0 to 1.0
        """
        if not recent_actions:
            return Decimal('0.0')
        
        # Calculate average transformation score
        total_score = sum(action.calculate_transformation_score() for action in recent_actions)
        avg_score = total_score / len(recent_actions)
        
        # Factor in frequency (actions per day)
        if self.start_date:
            days_elapsed = (datetime.now() - self.start_date).days or 1
            action_frequency = Decimal(len(recent_actions)) / Decimal(days_elapsed)
            frequency_factor = min(action_frequency / Decimal('10.0'), Decimal('1.0'))
        else:
            frequency_factor = Decimal('0.5')
        
        # Calculate momentum
        momentum = (avg_score * Decimal('0.7')) + (frequency_factor * Decimal('0.3'))
        
        return min(momentum, Decimal('1.0'))


# ==================== RATE LIMITER ====================

class RateLimiter:
    """
    Rate limiter for external API calls with async support.
    Prevents service abuse and ensures compliance with provider limits.
    """
    
    def __init__(self, calls_per_second: float = 10.0):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_second: Maximum number of calls allowed per second
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make an API call, waiting if necessary"""
        async with self._lock:
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self.last_call
            
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                await asyncio.sleep(wait_time)
            
            self.last_call = asyncio.get_event_loop().time()


# ==================== PROTOCOL SERVICE ====================

class UBECttProtocolService:
    """
    UBECtt Transform Token Protocol Service Implementation
    
    The Fire Element protocol handles:
    1. Recording and validating transformative actions
    2. Calculating transformation scores and impact
    3. Distributing UBECtt tokens based on regenerative contributions
    4. Tracking transformation phases and momentum
    5. Coordinating with other element protocols (Air, Water, Earth)
    
    This is a SERVICE - it does not execute standalone.
    All methods are async for proper I/O handling.
    """
    
    def __init__(
        self,
        db_manager,
        config: Dict[str, Any],
        stellar_client = None,
        rate_limit_calls_per_second: float = 10.0
    ):
        """
        Initialize the UBECtt Transform Token protocol service.
        
        Args:
            db_manager: Database manager instance (must have async methods)
            config: Configuration dictionary
            stellar_client: Optional Stellar client for blockchain operations
            rate_limit_calls_per_second: Rate limit for external API calls
        """
        self.db = db_manager
        self.config = config
        self.stellar_client = stellar_client
        self.logger = logger
        
        # Rate limiting
        self.rate_limiter = RateLimiter(calls_per_second=rate_limit_calls_per_second)
        
        # Configuration
        self.asset_code = config.get('asset_code', 'UBECtt')
        self.issuer = config.get('issuer')
        self.min_verification_threshold = config.get('min_verification_threshold', 3)
        self.base_reward = Decimal(str(config.get('base_reward', '100.0')))
        self.max_reward = Decimal(str(config.get('max_reward', '10000.0')))
        
        # In-memory cache (database is source of truth)
        self._action_cache: Dict[str, TransformativeAction] = {}
        self._phase_cache: Dict[str, TransformationPhase] = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_cache_refresh = 0.0
        
        self.logger.info(f"UBECtt Protocol Service initialized: {self.asset_code}")
    
    # ==================== CACHE MANAGEMENT ====================
    
    async def _refresh_cache_if_needed(self):
        """Refresh in-memory cache from database if TTL expired"""
        current_time = asyncio.get_event_loop().time()
        if current_time - self._last_cache_refresh > self._cache_ttl:
            await self._load_from_database()
            self._last_cache_refresh = current_time
    
    async def _load_from_database(self):
        """Load recent data from database into cache"""
        try:
            # Ensure connection is established
            if hasattr(self.db, 'conn') and self.db.conn is None:
                await self.db.connect()
            
            # Load recent actions (last 30 days)
            query = """
                SELECT action_id, agent_id, action_type, description, impact_scale,
                       timestamp, direct_beneficiaries, indirect_reach, 
                       regeneration_score, catalytic_multiplier, verified,
                       verifier_ids, evidence_urls, ubectt_awarded, 
                       distribution_tx_hash, tags, related_actions, metadata
                FROM ubec_main.transformative_actions
                WHERE timestamp > NOW() - INTERVAL '30 days'
                ORDER BY timestamp DESC
                LIMIT 1000
            """
            
            rows = await self.db.fetch_all(query)
            
            if rows:
                for row in rows:
                    action_data = {
                        'action_id': row[0],
                        'agent_id': row[1],
                        'action_type': row[2],
                        'description': row[3],
                        'impact_scale': row[4],
                        'timestamp': row[5],
                        'direct_beneficiaries': row[6] or 0,
                        'indirect_reach': row[7] or 0,
                        'regeneration_score': str(row[8] or 0),
                        'catalytic_multiplier': str(row[9] or 1),
                        'verified': row[10] or False,
                        'verifier_ids': row[11] or [],
                        'evidence_urls': row[12] or [],
                        'ubectt_awarded': str(row[13] or 0),
                        'distribution_tx_hash': row[14],
                        'tags': row[15] or [],
                        'related_actions': row[16] or [],
                        'metadata': row[17] or {}
                    }
                    action = TransformativeAction.from_dict(action_data)
                    self._action_cache[action.action_id] = action
                
                self.logger.info(f"Loaded {len(rows)} actions from database into cache")
            
            # Load active phases
            phase_query = """
                SELECT phase_id, name, description, start_date, end_date,
                       target_outcomes, key_indicators, participating_agents,
                       actions_completed, total_ubectt_distributed, 
                       phase_momentum, is_active, completion_percentage
                FROM ubec_main.transformation_phases
                WHERE is_active = TRUE
                ORDER BY start_date DESC
            """
            
            phase_rows = await self.db.execute_query(phase_query, fetch_all=True)
            
            if phase_rows:
                for row in phase_rows:
                    key_indicators = row[6]
                    if isinstance(key_indicators, str):
                        key_indicators = json.loads(key_indicators)
                    
                    phase = TransformationPhase(
                        phase_id=row[0],
                        name=row[1],
                        description=row[2],
                        start_date=row[3],
                        end_date=row[4],
                        target_outcomes=row[5] or [],
                        key_indicators={k: Decimal(str(v)) for k, v in (key_indicators or {}).items()},
                        participating_agents=row[7] or [],
                        actions_completed=row[8] or 0,
                        total_ubectt_distributed=Decimal(str(row[9] or 0)),
                        phase_momentum=Decimal(str(row[10] or 0)),
                        is_active=row[11],
                        completion_percentage=Decimal(str(row[12] or 0))
                    )
                    self._phase_cache[phase.phase_id] = phase
                
                self.logger.info(f"Loaded {len(phase_rows)} phases from database into cache")
                
        except Exception as e:
            self.logger.error(f"Error loading from database: {e}")
    
    # ==================== ACTION RECORDING ====================
    
    async def record_action(self, action: TransformativeAction) -> bool:
        """
        Record a new transformative action.
        
        Args:
            action: TransformativeAction object to record
            
        Returns:
            bool: True if successfully recorded
        """
        try:
            # Validate action
            if not action.agent_id or not action.description:
                self.logger.error("Invalid action: missing required fields")
                return False
            
            # Store to database (single source of truth)
            await self._store_action_to_db(action)
            
            # Update cache
            self._action_cache[action.action_id] = action
            
            self.logger.info(f"Recorded action {action.action_id} by {action.agent_id[:8]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording action: {e}")
            return False
    
    async def _store_action_to_db(self, action: TransformativeAction):
        """Store action to database"""
        query = """
        INSERT INTO ubec_main.transformative_actions 
        (action_id, agent_id, action_type, description, impact_scale,
         timestamp, direct_beneficiaries, indirect_reach, regeneration_score,
         catalytic_multiplier, verified, verifier_ids, evidence_urls,
         ubectt_awarded, distribution_tx_hash, tags, related_actions, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
        ON CONFLICT (action_id) DO UPDATE SET
            verified = EXCLUDED.verified,
            verifier_ids = EXCLUDED.verifier_ids,
            evidence_urls = EXCLUDED.evidence_urls,
            ubectt_awarded = EXCLUDED.ubectt_awarded,
            distribution_tx_hash = EXCLUDED.distribution_tx_hash
        """
        
        params = (
            action.action_id,
            action.agent_id,
            action.action_type.value,
            action.description,
            action.impact_scale.value,
            action.timestamp,
            action.direct_beneficiaries,
            action.indirect_reach,
            float(action.regeneration_score),
            float(action.catalytic_multiplier),
            action.verified,
            action.verifier_ids,
            action.evidence_urls,
            float(action.ubectt_awarded),
            action.distribution_tx_hash,
            action.tags,
            action.related_actions,
            json.dumps(action.metadata)
        )
        
        await self.db.execute(query, *params)
    
    async def verify_action(
        self,
        action_id: str,
        verifier_id: str,
        evidence_url: Optional[str] = None
    ) -> bool:
        """
        Add verification to a transformative action.
        
        Args:
            action_id: ID of the action to verify
            verifier_id: Stellar address of the verifier
            evidence_url: Optional URL to evidence
            
        Returns:
            bool: True if verification added successfully
        """
        try:
            await self._refresh_cache_if_needed()
            
            action = self._action_cache.get(action_id)
            if not action:
                # Try to load from database
                query = "SELECT * FROM ubec_main.transformative_actions WHERE action_id = $1"
                row = await self.db.fetch_one(query, action_id)
                if not row:
                    self.logger.error(f"Action {action_id} not found")
                    return False
            
            # Add verifier
            if verifier_id not in action.verifier_ids:
                action.verifier_ids.append(verifier_id)
            
            # Add evidence if provided
            if evidence_url and evidence_url not in action.evidence_urls:
                action.evidence_urls.append(evidence_url)
            
            # Check if action meets verification threshold
            if len(action.verifier_ids) >= self.min_verification_threshold:
                action.verified = True
                self.logger.info(f"Action {action_id} is now verified")
            
            # Update database
            await self._store_action_to_db(action)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying action: {e}")
            return False
    
    # ==================== TOKEN DISTRIBUTION ====================
    
    def calculate_reward(self, action: TransformativeAction) -> Decimal:
        """
        Calculate the UBECtt reward amount for a transformative action.
        
        Args:
            action: The transformative action
            
        Returns:
            Decimal: Amount of UBECtt to award
        """
        # Get transformation score
        score = action.calculate_transformation_score()
        
        # Scale reward based on score
        reward = self.base_reward + (score * (self.max_reward - self.base_reward))
        
        # Apply verification multiplier
        if action.verified:
            reward *= Decimal('1.5')
        
        # Apply catalytic multiplier (with diminishing returns)
        if action.catalytic_multiplier > Decimal('1.0'):
            catalytic_bonus = min(
                (action.catalytic_multiplier - Decimal('1.0')) * Decimal('0.5'),
                Decimal('1.0')
            )
            reward *= (Decimal('1.0') + catalytic_bonus)
        
        # Cap at maximum
        return min(reward, self.max_reward)
    
    async def distribute_reward(self, action_id: str, dry_run: bool = True) -> Optional[str]:
        """
        Distribute UBECtt tokens for a transformative action.
        
        Args:
            action_id: ID of the action to reward
            dry_run: If True, calculate but don't execute transaction
            
        Returns:
            Optional[str]: Transaction hash if successful, None otherwise
        """
        try:
            await self._refresh_cache_if_needed()
            
            action = self._action_cache.get(action_id)
            if not action:
                self.logger.error(f"Action {action_id} not found")
                return None
            
            # Check if already distributed
            if action.ubectt_awarded > Decimal('0.0'):
                self.logger.warning(f"Reward already distributed for action {action_id}")
                return action.distribution_tx_hash
            
            # Calculate reward
            reward_amount = self.calculate_reward(action)
            
            if dry_run:
                self.logger.info(f"[DRY RUN] Would distribute {reward_amount} UBECtt to {action.agent_id[:8]}...")
                action.ubectt_awarded = reward_amount
                await self._store_action_to_db(action)
                return "DRY_RUN_TX_HASH"
            
            # Execute distribution via Stellar (if configured)
            if self.stellar_client:
                tx_hash = await self._execute_stellar_distribution(action.agent_id, reward_amount)
                if tx_hash:
                    action.ubectt_awarded = reward_amount
                    action.distribution_tx_hash = tx_hash
                    await self._store_action_to_db(action)
                    self.logger.info(f"Distributed {reward_amount} UBECtt in tx {tx_hash[:16]}...")
                    return tx_hash
            else:
                self.logger.warning("Stellar client not configured - simulating distribution")
                action.ubectt_awarded = reward_amount
                await self._store_action_to_db(action)
                return "SIMULATED_TX_HASH"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error distributing reward: {e}")
            return None
    
    async def _execute_stellar_distribution(self, recipient: str, amount: Decimal) -> Optional[str]:
        """
        Execute token distribution on Stellar network with rate limiting.
        
        Args:
            recipient: Destination account
            amount: Amount to send
            
        Returns:
            Optional[str]: Transaction hash if successful
        """
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # This would require a source account with UBECtt tokens and signing keys
        # Implementation depends on the specific distribution mechanism
        self.logger.info(f"Would send {amount} UBECtt to {recipient}")
        
        # TODO: Implement actual Stellar transaction submission
        # using the stellar_client (ServerAsync)
        
        return None
    
    # ==================== AGENT PROFILES ====================
    
    async def get_agent_profile(self, agent_id: str) -> Dict:
        """
        Get the transformation profile for an agent.
        
        Args:
            agent_id: Stellar address of the agent
            
        Returns:
            Dict: Agent's transformation profile
        """
        await self._refresh_cache_if_needed()
        
        # Get agent actions from cache/database
        agent_actions = [a for a in self._action_cache.values() if a.agent_id == agent_id]
        
        profile = {
            'agent_id': agent_id,
            'total_actions': len(agent_actions),
            'verified_actions': sum(1 for a in agent_actions if a.verified),
            'total_ubectt_earned': sum(a.ubectt_awarded for a in agent_actions),
            'transformation_types': {},
            'impact_scales': {},
            'avg_transformation_score': Decimal('0.0'),
            'catalytic_rating': Decimal('0.0'),
            'regeneration_capacity': Decimal('0.0')
        }
        
        if agent_actions:
            # Calculate statistics
            for action in agent_actions:
                # Count by type
                action_type = action.action_type.value
                profile['transformation_types'][action_type] = profile['transformation_types'].get(action_type, 0) + 1
                
                # Count by scale
                impact_scale = action.impact_scale.value
                profile['impact_scales'][impact_scale] = profile['impact_scales'].get(impact_scale, 0) + 1
            
            # Calculate averages
            scores = [a.calculate_transformation_score() for a in agent_actions]
            profile['avg_transformation_score'] = sum(scores) / len(scores)
            
            catalytic_multipliers = [a.catalytic_multiplier for a in agent_actions]
            profile['catalytic_rating'] = sum(catalytic_multipliers) / len(catalytic_multipliers)
            
            regeneration_scores = [a.regeneration_score for a in agent_actions]
            profile['regeneration_capacity'] = sum(regeneration_scores) / len(regeneration_scores)
        
        return profile
    
    # ==================== PHASE MANAGEMENT ====================
    
    async def create_phase(self, phase: TransformationPhase) -> bool:
        """
        Create a new transformation phase.
        
        Args:
            phase: TransformationPhase object
            
        Returns:
            bool: True if successfully created
        """
        try:
            await self._store_phase_to_db(phase)
            self._phase_cache[phase.phase_id] = phase
            self.logger.info(f"Created transformation phase: {phase.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating phase: {e}")
            return False
    
    async def _store_phase_to_db(self, phase: TransformationPhase):
        """Store phase to database"""
        query = """
        INSERT INTO ubec_main.transformation_phases
        (phase_id, name, description, start_date, end_date,
         target_outcomes, key_indicators, participating_agents,
         actions_completed, total_ubectt_distributed, phase_momentum,
         is_active, completion_percentage)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        ON CONFLICT (phase_id) DO UPDATE SET
            actions_completed = EXCLUDED.actions_completed,
            total_ubectt_distributed = EXCLUDED.total_ubectt_distributed,
            phase_momentum = EXCLUDED.phase_momentum,
            is_active = EXCLUDED.is_active,
            completion_percentage = EXCLUDED.completion_percentage
        """
        
        params = (
            phase.phase_id,
            phase.name,
            phase.description,
            phase.start_date,
            phase.end_date,
            phase.target_outcomes,
            json.dumps({k: str(v) for k, v in phase.key_indicators.items()}),
            phase.participating_agents,
            phase.actions_completed,
            float(phase.total_ubectt_distributed),
            float(phase.phase_momentum),
            phase.is_active,
            float(phase.completion_percentage)
        )
        
        await self.db.execute(query, *params)
    
    async def update_phase_progress(self, phase_id: str) -> bool:
        """
        Update the progress of a transformation phase.
        
        Args:
            phase_id: ID of the phase to update
            
        Returns:
            bool: True if successfully updated
        """
        try:
            await self._refresh_cache_if_needed()
            
            phase = self._phase_cache.get(phase_id)
            if not phase:
                self.logger.error(f"Phase {phase_id} not found")
                return False
            
            # Get actions in this phase
            phase_actions = [
                a for a in self._action_cache.values()
                if a.agent_id in phase.participating_agents
                and a.timestamp >= phase.start_date
                and (not phase.end_date or a.timestamp <= phase.end_date)
            ]
            
            # Update metrics
            phase.actions_completed = len(phase_actions)
            phase.total_ubectt_distributed = sum(a.ubectt_awarded for a in phase_actions)
            phase.phase_momentum = phase.calculate_phase_momentum(phase_actions)
            
            # Update completion percentage
            if phase_actions:
                verified_count = sum(1 for a in phase_actions if a.verified)
                phase.completion_percentage = Decimal(verified_count) / Decimal(max(phase.actions_completed, 1))
            
            # Update database
            await self._store_phase_to_db(phase)
            
            self.logger.info(f"Updated phase {phase.name}: {phase.completion_percentage*100:.1f}% complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating phase progress: {e}")
            return False
    
    # ==================== ANALYSIS & REPORTING ====================
    
    async def get_system_transformation_metrics(self) -> Dict:
        """
        Get overall system-wide transformation metrics.
        
        Returns:
            Dict: System transformation metrics
        """
        await self._refresh_cache_if_needed()
        
        total_actions = len(self._action_cache)
        verified_actions = sum(1 for a in self._action_cache.values() if a.verified)
        
        metrics = {
            'total_actions': total_actions,
            'verified_actions': verified_actions,
            'verification_rate': Decimal(verified_actions) / Decimal(total_actions) if total_actions > 0 else Decimal('0.0'),
            'total_ubectt_distributed': sum(a.ubectt_awarded for a in self._action_cache.values()),
            'unique_agents': len(set(a.agent_id for a in self._action_cache.values())),
            'active_phases': sum(1 for p in self._phase_cache.values() if p.is_active),
            'transformation_types': {},
            'impact_distribution': {},
            'avg_catalytic_multiplier': Decimal('0.0'),
            'system_regeneration_capacity': Decimal('0.0')
        }
        
        if total_actions > 0:
            # Analyze by type
            for action in self._action_cache.values():
                action_type = action.action_type.value
                metrics['transformation_types'][action_type] = metrics['transformation_types'].get(action_type, 0) + 1
                
                impact_scale = action.impact_scale.value
                metrics['impact_distribution'][impact_scale] = metrics['impact_distribution'].get(impact_scale, 0) + 1
            
            # Calculate averages
            all_catalytic = [a.catalytic_multiplier for a in self._action_cache.values()]
            metrics['avg_catalytic_multiplier'] = sum(all_catalytic) / len(all_catalytic)
            
            all_regeneration = [a.regeneration_score for a in self._action_cache.values()]
            metrics['system_regeneration_capacity'] = sum(all_regeneration) / len(all_regeneration)
        
        return metrics
    
    async def generate_report(self, output_path: Optional[str] = None) -> Dict:
        """
        Generate a comprehensive transformation report.
        
        Args:
            output_path: Optional path to save the report
            
        Returns:
            Dict: Complete transformation report
        """
        metrics = await self.get_system_transformation_metrics()
        
        report = {
            'protocol': 'UBECtt - Transform Token (Fire Element)',
            'generated_at': datetime.now().isoformat(),
            'system_metrics': {k: (str(v) if isinstance(v, Decimal) else v) for k, v in metrics.items()},
            'active_phases': {
                phase_id: {
                    'name': phase.name,
                    'progress': float(phase.completion_percentage),
                    'momentum': float(phase.phase_momentum),
                    'actions_completed': phase.actions_completed
                }
                for phase_id, phase in self._phase_cache.items() if phase.is_active
            },
            'top_transformers': []
        }
        
        # Get top agents by transformation score
        agent_scores = []
        unique_agents = set(a.agent_id for a in self._action_cache.values())
        
        for agent_id in unique_agents:
            profile = await self.get_agent_profile(agent_id)
            agent_scores.append({
                'agent_id': agent_id,
                'total_actions': profile['total_actions'],
                'avg_score': float(profile['avg_transformation_score']),
                'ubectt_earned': float(profile['total_ubectt_earned'])
            })
        
        # Sort by average transformation score
        agent_scores.sort(key=lambda x: x['avg_score'], reverse=True)
        report['top_transformers'] = agent_scores[:10]
        
        # Save report if path provided
        if output_path:
            try:
                async with aiofiles.open(output_path, 'w') as f:
                    await f.write(json.dumps(report, indent=2, default=str))
                self.logger.info(f"Report saved to {output_path}")
            except Exception as e:
                self.logger.error(f"Error saving report: {e}")
        
        return report
    
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health.
        
        Returns:
            Dict with health status
        """
        try:
            await self._refresh_cache_if_needed()
            
            return {
                'protocol': f'UBECtt (Fire)',
                'status': 'healthy',
                'cached_actions': len(self._action_cache),
                'cached_phases': len(self._phase_cache),
                'cache_age_seconds': (
                    (asyncio.get_event_loop().time() - self._last_cache_refresh)
                    if self._last_cache_refresh > 0 else None
                ),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'protocol': f'UBECtt (Fire)',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    # ==================== PROTOCOL COORDINATION ====================
    
    async def assess_regeneration(self) -> Dict[str, Any]:
        """
        Assess regeneration principle (Fire's ubuntu principle).
        
        Fire element's ubuntu principle is REGENERATION - the capacity for
        transformative renewal, catalytic change, and system evolution.
        
        Returns:
            Dictionary with regeneration assessment
        """
        self.logger.info("Assessing regeneration principle for Fire element")
        
        try:
            metrics = await self.get_system_transformation_metrics()
            
            # Regeneration metrics
            system_regen_capacity = metrics.get('system_regeneration_capacity', Decimal('0.0'))
            avg_catalytic = metrics.get('avg_catalytic_multiplier', Decimal('1.0'))
            total_actions = metrics.get('total_actions', 0)
            verified_rate = float(metrics.get('verification_rate', Decimal('0.0')))
            
            # Calculate regeneration score
            regen_score = float(system_regen_capacity) * 0.4
            
            # Catalytic contribution
            catalytic_normalized = min((float(avg_catalytic) - 1.0), 1.0)
            regen_score += catalytic_normalized * 0.3
            
            # Action quantity (logarithmic scale)
            if total_actions > 0:
                import math
                action_score = min(math.log10(total_actions + 1) / math.log10(1001), 1.0)
                regen_score += action_score * 0.2
            
            # Verification quality
            regen_score += verified_rate * 0.1
            
            # Determine status
            if regen_score > 0.7:
                status = 'excellent'
                description = 'Strong regenerative capacity with catalytic impact'
            elif regen_score > 0.5:
                status = 'good'
                description = 'Healthy transformation dynamics'
            elif regen_score > 0.3:
                status = 'developing'
                description = 'Building regenerative capacity'
            else:
                status = 'emerging'
                description = 'Early stage regeneration activity'
            
            return {
                'principle': 'regeneration',
                'element': 'fire',
                'score': round(regen_score, 2),
                'status': status,
                'description': description,
                'metrics': {
                    'system_regeneration_capacity': float(system_regen_capacity),
                    'catalytic_multiplier': float(avg_catalytic),
                    'total_transformative_actions': total_actions,
                    'verification_rate': verified_rate
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing regeneration: {e}")
            return {
                'principle': 'regeneration',
                'element': 'fire',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def evaluate_holonic(self, agent_id: str) -> Dict[str, Any]:
        """
        Evaluate an agent's holonic alignment with UBECtt (Fire) principles.
        
        Fire element focuses on:
        - Transformative action and regenerative impact
        - Catalytic contribution (amplifying others' transformations)
        - Diversity of transformation types
        - Balance across impact scales (individual to systemic)
        
        Args:
            agent_id: Stellar account ID
        
        Returns:
            dict: Holonic evaluation results
        """
        self.logger.info(f"Evaluating holonic alignment for agent {agent_id}")
        
        try:
            profile = await self.get_agent_profile(agent_id)
            alignment_score = await self._calculate_holonic_alignment(agent_id, profile)
            
            # Calculate specific metrics
            metrics = {
                'regenerative_capacity': float(profile.get('regeneration_capacity', Decimal('0.0'))),
                'catalytic_rating': float(profile.get('catalytic_rating', Decimal('1.0'))),
                'transformation_diversity': len(profile.get('transformation_types', {})) / 8.0,
                'impact_scale_balance': self._calculate_impact_balance(profile),
                'verification_quality': (
                    profile.get('verified_actions', 0) / profile.get('total_actions', 1)
                    if profile.get('total_actions', 0) > 0 else 0.0
                )
            }
            
            return {
                'agent_id': agent_id,
                'protocol': 'UBECtt (Fire)',
                'total_actions': profile.get('total_actions', 0),
                'verified_actions': profile.get('verified_actions', 0),
                'total_ubectt_earned': str(profile.get('total_ubectt_earned', Decimal('0.0'))),
                'avg_transformation_score': float(profile.get('avg_transformation_score', Decimal('0.0'))),
                'metrics': metrics,
                'holonic_score': float(alignment_score),
                'alignment_level': self._determine_alignment_level(float(alignment_score))
            }
            
        except Exception as e:
            self.logger.error(f"Holonic evaluation failed: {e}")
            raise
    
    async def _calculate_holonic_alignment(self, agent_id: str, profile: Dict) -> Decimal:
        """Calculate holonic alignment score"""
        # Factors for holonic alignment
        diversity_score = Decimal(len(profile.get('transformation_types', {}))) / Decimal('8.0')
        diversity_score = min(diversity_score, Decimal('1.0'))
        
        # Balance across impact scales
        balance_score = Decimal(str(self._calculate_impact_balance(profile)))
        
        # Catalytic potential
        catalytic_score = profile.get('catalytic_rating', Decimal('1.0')) / Decimal('2.0')
        
        # Regeneration capacity
        regeneration_score = profile.get('regeneration_capacity', Decimal('0.0'))
        
        # Weighted combination
        alignment = (
            diversity_score * Decimal('0.25') +
            balance_score * Decimal('0.25') +
            catalytic_score * Decimal('0.25') +
            regeneration_score * Decimal('0.25')
        )
        
        return min(alignment, Decimal('1.0'))
    
    def _calculate_impact_balance(self, profile: Dict) -> float:
        """Calculate balance across impact scales"""
        impact_scales = profile.get('impact_scales', {})
        if not impact_scales:
            return 0.0
        
        total = sum(impact_scales.values())
        if total == 0:
            return 0.0
        
        proportions = [count / total for count in impact_scales.values()]
        
        # Shannon entropy normalized
        if len(proportions) > 1:
            import math
            entropy = -sum(p * math.log(p) for p in proportions if p > 0)
            max_entropy = math.log(len(proportions))
            return entropy / max_entropy if max_entropy > 0 else 0.0
        else:
            return 0.5
    
    def _determine_alignment_level(self, score: float) -> str:
        """Determine alignment level from score"""
        if score >= 0.9:
            return 'Exemplar'
        elif score >= 0.7:
            return 'Integrator'
        elif score >= 0.5:
            return 'Contributor'
        elif score >= 0.3:
            return 'Participant'
        else:
            return 'Observer'
    
    async def sync_transformation_data(self) -> Dict:
        """
        Synchronize transformation data from database.
        Called by the main protocol coordinator.
        
        Returns:
            Dict: Sync status and metrics
        """
        try:
            self.logger.info("Starting Fire (UBECtt) transformation data synchronization...")
            
            # Force cache refresh
            await self._load_from_database()
            
            # Calculate current metrics
            metrics = await self.get_system_transformation_metrics()
            
            return {
                'element': 'fire',
                'token': self.asset_code,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'actions_loaded': len(self._action_cache),
                'phases_loaded': len(self._phase_cache),
                'metrics': {
                    'total_actions': metrics['total_actions'],
                    'verified_actions': metrics['verified_actions'],
                    'total_ubectt_distributed': float(metrics['total_ubectt_distributed']),
                    'unique_agents': metrics['unique_agents'],
                    'active_phases': metrics['active_phases'],
                    'system_regeneration_capacity': float(metrics['system_regeneration_capacity'])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error syncing transformation data: {e}")
            return {
                'element': 'fire',
                'token': self.asset_code,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# ==================== SERVICE FACTORY ====================

def create_ubectt_service(
    db_manager,
    config: Dict[str, Any],
    stellar_client = None,
    **kwargs
) -> UBECttProtocolService:
    """
    Factory function to create UBECtt protocol service instance.
    
    This is the proper way to instantiate the service for use in the service registry.
    
    Args:
        db_manager: Database manager with async support
        config: Configuration dictionary
        stellar_client: Optional Stellar async client
        **kwargs: Additional configuration options
    
    Returns:
        UBECttProtocolService: Initialized service instance
    """
    return UBECttProtocolService(
        db_manager=db_manager,
        config=config,
        stellar_client=stellar_client,
        rate_limit_calls_per_second=kwargs.get('rate_limit_calls_per_second', 10.0)
    )


# ==================== MODULE EXPORTS ====================

__all__ = [
    'TransformationType',
    'ImpactScale',
    'TransformativeAction',
    'TransformationPhase',
    'UBECttProtocolService',
    'create_ubectt_service',
    'RateLimiter'
]
