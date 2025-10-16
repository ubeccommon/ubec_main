#!/usr/bin/env python3
"""
UBEC Order Book Analytics Service - Complete Production Version

Provides comprehensive analytics and insights for order book dynamics across
the UBEC token ecosystem. Analyzes depth, account positions, market microstructure,
and order flow patterns for all four UBEC elements.

Design Principles Compliance:
- ✅ Modular Design: Self-contained order book service with defined boundaries
- ✅ Service Pattern: No standalone execution, used as service only
- ✅ Service Registry: Accessed through service registry pattern
- ✅ Database as Single Source of Truth: All data stored in database
- ✅ Strict Async Operations: All I/O uses async/await
- ✅ No Sync Fallbacks: Pure async implementation
- ✅ Per-Asset Monitoring: Individual token/element tracking
- ✅ No Duplicate Configuration: No config duplication
- ✅ Integrated Rate Limiting: Built-in Stellar API rate limiting
- ✅ Separation of Concerns: Order book analysis separated from other services
- ✅ Comprehensive Documentation: Full docstrings and examples
- ✅ Method Singularity: Each method implemented once

Key Features:
- Real-time order book snapshot fetching
- Account order position tracking
- Market depth analysis with liquidity metrics
- Order flow and buy/sell pressure analysis
- Integration with analytics service for combined insights
- Historical order book tracking
- Whale order detection
- Market microstructure analysis

Four-Element Architecture:
- 🜁 Air (UBEC) - Gateway & Universal Access
- 🜄 Water (UBECrc) - Flow & Exchange
- 🜃 Earth (UBECgpi) - Stability & Value
- 🜂 Fire (UBECtt) - Transformation & Action

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.

Author: UBEC Protocol Team
Version: 1.0
Date: October 16, 2025
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

# Configure precision for decimal calculations
getcontext().prec = 10

logger = logging.getLogger(__name__)


class TokenCode(str, Enum):
    """Valid UBEC token codes"""
    UBEC = "UBEC"
    UBECRC = "UBECrc"
    UBECGPI = "UBECgpi"
    UBECTT = "UBECtt"


class ElementType(str, Enum):
    """Four-element types"""
    AIR = "air"
    WATER = "water"
    EARTH = "earth"
    FIRE = "fire"


class OrderSide(str, Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"


# Element to token mapping
ELEMENT_TOKEN_MAP = {
    ElementType.AIR: TokenCode.UBEC,
    ElementType.WATER: TokenCode.UBECRC,
    ElementType.EARTH: TokenCode.UBECGPI,
    ElementType.FIRE: TokenCode.UBECTT
}

TOKEN_ELEMENT_MAP = {v: k for k, v in ELEMENT_TOKEN_MAP.items()}


class OrderBookException(Exception):
    """Base exception for order book service"""
    pass


@dataclass
class OrderBookLevel:
    """Single price level in order book"""
    price: Decimal
    amount: Decimal
    price_r_n: int  # Price ratio numerator
    price_r_d: int  # Price ratio denominator


@dataclass
class OrderBookSnapshot:
    """Complete order book snapshot"""
    asset_code: str
    counter_asset: str
    timestamp: datetime
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    best_bid: Decimal
    best_ask: Decimal
    spread: Decimal
    spread_bps: int
    mid_price: Decimal
    bid_depth_total: Decimal
    ask_depth_total: Decimal


@dataclass
class AccountOrder:
    """Individual order/offer"""
    offer_id: int
    account_id: str
    side: OrderSide
    price: Decimal
    amount: Decimal
    asset_code: str
    counter_asset: str
    is_passive: bool
    created_at: datetime
    last_modified: datetime


@dataclass
class AccountOrderPosition:
    """Account's order book positions for a specific asset"""
    account_id: str
    asset_code: str
    buy_orders: List[AccountOrder]
    sell_orders: List[AccountOrder]
    total_buy_volume: Decimal
    total_sell_volume: Decimal
    avg_buy_price: Decimal
    avg_sell_price: Decimal
    net_position: Decimal  # buy_volume - sell_volume
    last_updated: datetime


@dataclass
class MarketDepthMetrics:
    """Market depth and liquidity analysis"""
    asset_code: str
    counter_asset: str
    timestamp: datetime
    total_bid_liquidity: Decimal
    total_ask_liquidity: Decimal
    bid_ask_ratio: Decimal
    depth_within_1pct: Decimal  # Liquidity within 1% of mid
    depth_within_5pct: Decimal  # Liquidity within 5% of mid
    depth_within_10pct: Decimal  # Liquidity within 10% of mid
    top_5_bid_concentration: Decimal  # % in top 5 bids
    top_5_ask_concentration: Decimal  # % in top 5 asks
    unique_bid_accounts: int
    unique_ask_accounts: int
    bid_levels: int
    ask_levels: int
    market_depth_score: Decimal  # 0-100 composite score


@dataclass
class OrderFlowMetrics:
    """Order flow and pressure analysis"""
    asset_code: str
    period_minutes: int
    timestamp: datetime
    buy_pressure_score: Decimal  # 0-100
    sell_pressure_score: Decimal  # 0-100
    order_imbalance: Decimal  # -1 to 1 (negative=sell pressure)
    new_buy_orders: int
    new_sell_orders: int
    cancelled_buy_orders: int
    cancelled_sell_orders: int
    filled_buy_volume: Decimal
    filled_sell_volume: Decimal
    net_flow: Decimal  # Net buy/sell flow


@dataclass
class LiquidityHealth:
    """Combined liquidity health metrics"""
    asset_code: str
    timestamp: datetime
    orderbook_liquidity: Dict
    token_liquidity: Dict
    combined_metrics: Dict
    liquidity_health_score: Decimal  # 0-100


class UBECOrderBookService:
    """
    Comprehensive order book analytics service for UBEC ecosystem.
    
    Tracks and analyzes order book dynamics across all four UBEC tokens,
    providing insights into market depth, liquidity, account positions,
    and order flow patterns.
    
    Usage:
        service = UBECOrderBookService(db_manager, stellar_client)
        await service.initialize()
        
        # Get order book snapshot
        snapshot = await service.fetch_orderbook_snapshot('UBEC')
        
        # Analyze account positions
        positions = await service.get_account_orders(account_id)
        
        # Market depth analysis
        depth = await service.analyze_market_depth('UBEC')
        
        await service.close()
    """
    
    def __init__(
        self,
        db_manager,
        stellar_client,
        issuer_address: str,
        rate_limiter=None,
        cache_ttl: int = 60,  # 1 minute cache
        sync_interval: int = 300  # 5 minutes background sync
    ):
        """
        Initialize order book service.
        
        Args:
            db_manager: AsyncDatabaseManager instance
            stellar_client: Stellar ServerAsync client
            issuer_address: UBEC token issuer address
            rate_limiter: Optional rate limiter
            cache_ttl: Cache time-to-live in seconds
            sync_interval: Background sync interval in seconds
        """
        self.db = db_manager
        self.stellar = stellar_client
        self.issuer = issuer_address
        self.rate_limiter = rate_limiter
        self.cache_ttl = cache_ttl
        self.sync_interval = sync_interval
        
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._initialized = False
        self._sync_task = None
        self._counter_assets = ["XLM"]  # Default counter assets
        
        logger.info("[OrderBook] Service created")
    
    async def initialize(self):
        """Initialize service and start background tasks"""
        if self._initialized:
            logger.warning("[OrderBook] Already initialized")
            return
        
        try:
            # Verify database connection
            await self.db.ensure_connection()
            logger.info("[OrderBook] ✓ Database connection verified")
            
            # Load configuration
            await self._load_configuration()
            
            # Start background sync task
            self._sync_task = asyncio.create_task(self._background_orderbook_sync())
            
            self._initialized = True
            logger.info("[OrderBook] ✓ Service initialized successfully")
            
        except Exception as e:
            logger.error(f"[OrderBook] Initialization failed: {e}")
            raise OrderBookException(f"Service initialization failed: {e}")
    
    async def _load_configuration(self):
        """Load service configuration from database"""
        try:
            query = """
            SELECT parameter_name, parameter_value 
            FROM ubec_main.system_configuration 
            WHERE parameter_name LIKE 'orderbook_%'
            """
            config = await self.db.fetch(query)
            
            for row in config:
                if row['parameter_name'] == 'orderbook_counter_assets':
                    self._counter_assets = json.loads(row['parameter_value'])
                elif row['parameter_name'] == 'orderbook_cache_ttl':
                    self.cache_ttl = int(row['parameter_value'])
                elif row['parameter_name'] == 'orderbook_sync_interval':
                    self.sync_interval = int(row['parameter_value'])
            
            logger.info(f"[OrderBook] Configuration loaded: {len(config)} parameters")
            
        except Exception as e:
            logger.warning(f"[OrderBook] Could not load config, using defaults: {e}")
    
    # ========================================================================
    # CACHE MANAGEMENT
    # ========================================================================
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get item from cache if not expired"""
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        if datetime.now() - timestamp > timedelta(seconds=self.cache_ttl):
            del self._cache[key]
            return None
        
        return value
    
    def _set_cached(self, key: str, value: Any):
        """Store item in cache"""
        self._cache[key] = (value, datetime.now())
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        logger.info("[OrderBook] Cache cleared")
    
    # ========================================================================
    # REAL-TIME ORDER BOOK FETCHING
    # ========================================================================
    
    async def fetch_orderbook_snapshot(
        self,
        asset_code: str,
        counter_asset: str = "XLM",
        use_cache: bool = True
    ) -> OrderBookSnapshot:
        """
        Fetch current order book snapshot from Stellar network.
        
        Args:
            asset_code: UBEC token code (UBEC, UBECrc, UBECgpi, UBECtt)
            counter_asset: Counter asset (default XLM)
            use_cache: Use cached data if available
            
        Returns:
            OrderBookSnapshot with bids, asks, and metrics
            
        Raises:
            OrderBookException: If fetch fails
        """
        if not self._initialized:
            raise OrderBookException("Service not initialized")
        
        # Check cache
        cache_key = f"orderbook:{asset_code}:{counter_asset}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                logger.debug(f"[OrderBook] Cache hit for {cache_key}")
                return cached
        
        try:
            # Apply rate limiting
            if self.rate_limiter:
                await self.rate_limiter.acquire()
            
            # Import here to avoid circular dependency
            from stellar_sdk import Asset
            
            # Create asset objects
            selling_asset = Asset(asset_code, self.issuer)
            buying_asset = Asset.native() if counter_asset == "XLM" else Asset(counter_asset, self.issuer)
            
            # Fetch from Stellar
            logger.debug(f"[OrderBook] Fetching {asset_code}/{counter_asset} from Stellar")
            orderbook_response = await self.stellar.orderbook(
                selling=selling_asset,
                buying=buying_asset
            ).limit(200).call()
            
            # Parse bids
            bids = []
            for level in orderbook_response.get('bids', []):
                bids.append(OrderBookLevel(
                    price=Decimal(level['price']),
                    amount=Decimal(level['amount']),
                    price_r_n=int(level['price_r']['n']),
                    price_r_d=int(level['price_r']['d'])
                ))
            
            # Parse asks
            asks = []
            for level in orderbook_response.get('asks', []):
                asks.append(OrderBookLevel(
                    price=Decimal(level['price']),
                    amount=Decimal(level['amount']),
                    price_r_n=int(level['price_r']['n']),
                    price_r_d=int(level['price_r']['d'])
                ))
            
            # Calculate metrics
            best_bid = bids[0].price if bids else Decimal('0')
            best_ask = asks[0].price if asks else Decimal('0')
            mid_price = (best_bid + best_ask) / 2 if (bids and asks) else Decimal('0')
            spread = best_ask - best_bid if (bids and asks) else Decimal('0')
            spread_bps = int((spread / mid_price) * 10000) if mid_price > 0 else 0
            
            bid_depth = sum(level.amount for level in bids)
            ask_depth = sum(level.amount for level in asks)
            
            snapshot = OrderBookSnapshot(
                asset_code=asset_code,
                counter_asset=counter_asset,
                timestamp=datetime.now(),
                bids=bids,
                asks=asks,
                best_bid=best_bid,
                best_ask=best_ask,
                spread=spread,
                spread_bps=spread_bps,
                mid_price=mid_price,
                bid_depth_total=bid_depth,
                ask_depth_total=ask_depth
            )
            
            # Store to database
            await self._store_snapshot(snapshot)
            
            # Cache result
            self._set_cached(cache_key, snapshot)
            
            logger.info(f"[OrderBook] ✓ Fetched {asset_code}/{counter_asset}: "
                       f"Spread={spread_bps}bps, Depth={bid_depth + ask_depth}")
            
            return snapshot
            
        except Exception as e:
            logger.error(f"[OrderBook] Error fetching snapshot: {e}")
            raise OrderBookException(f"Failed to fetch order book: {e}")
    
    async def _store_snapshot(self, snapshot: OrderBookSnapshot):
        """Store order book snapshot to database"""
        try:
            query = """
            INSERT INTO ubec_main.orderbook_snapshots (
                asset_code, counter_asset, snapshot_time,
                best_bid, best_ask, spread_bps,
                bid_depth_total, ask_depth_total,
                bid_levels, ask_levels, raw_data
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (asset_code, counter_asset, snapshot_time) DO UPDATE SET
                best_bid = EXCLUDED.best_bid,
                best_ask = EXCLUDED.best_ask,
                spread_bps = EXCLUDED.spread_bps,
                bid_depth_total = EXCLUDED.bid_depth_total,
                ask_depth_total = EXCLUDED.ask_depth_total,
                bid_levels = EXCLUDED.bid_levels,
                ask_levels = EXCLUDED.ask_levels,
                raw_data = EXCLUDED.raw_data
            """
            
            raw_data = {
                'bids': [
                    {'price': str(b.price), 'amount': str(b.amount)} 
                    for b in snapshot.bids[:10]  # Store top 10
                ],
                'asks': [
                    {'price': str(a.price), 'amount': str(a.amount)} 
                    for a in snapshot.asks[:10]
                ]
            }
            
            await self.db.execute(
                query,
                snapshot.asset_code,
                snapshot.counter_asset,
                snapshot.timestamp,
                snapshot.best_bid,
                snapshot.best_ask,
                snapshot.spread_bps,
                snapshot.bid_depth_total,
                snapshot.ask_depth_total,
                len(snapshot.bids),
                len(snapshot.asks),
                json.dumps(raw_data)
            )
            
        except Exception as e:
            logger.warning(f"[OrderBook] Could not store snapshot: {e}")
    
    # ========================================================================
    # ACCOUNT ORDER POSITION TRACKING
    # ========================================================================
    
    async def get_account_orders(
        self,
        account_id: str,
        asset_code: Optional[str] = None
    ) -> List[AccountOrderPosition]:
        """
        Get all active orders for an account across all or specific UBEC tokens.
        
        Args:
            account_id: Stellar account address
            asset_code: Optional filter by specific asset
            
        Returns:
            List of AccountOrderPosition objects, one per asset
            
        Raises:
            OrderBookException: If fetch fails
        """
        if not self._initialized:
            raise OrderBookException("Service not initialized")
        
        try:
            # Apply rate limiting
            if self.rate_limiter:
                await self.rate_limiter.acquire()
            
            logger.debug(f"[OrderBook] Fetching orders for {account_id}")
            
            # Fetch offers from Stellar
            offers_response = await self.stellar.offers().for_account(account_id).limit(200).call()
            
            # Group by asset
            positions_by_asset: Dict[str, Dict] = {}
            
            for offer in offers_response.get('_embedded', {}).get('records', []):
                # Parse offer details
                selling = offer['selling']
                buying = offer['buying']
                
                selling_code = selling['asset_code'] if selling['asset_type'] != 'native' else 'XLM'
                buying_code = buying['asset_code'] if buying['asset_type'] != 'native' else 'XLM'
                
                # Determine if this is a UBEC token order
                is_ubec_sell = selling_code in [t.value for t in TokenCode]
                is_ubec_buy = buying_code in [t.value for t in TokenCode]
                
                if is_ubec_sell:
                    token = selling_code
                    side = OrderSide.SELL
                    counter = buying_code
                elif is_ubec_buy:
                    token = buying_code
                    side = OrderSide.BUY
                    counter = selling_code
                else:
                    continue  # Not a UBEC token order
                
                # Filter by asset if specified
                if asset_code and token != asset_code:
                    continue
                
                # Initialize position tracking for this asset
                if token not in positions_by_asset:
                    positions_by_asset[token] = {
                        'buy_orders': [],
                        'sell_orders': [],
                        'buy_volume': Decimal('0'),
                        'sell_volume': Decimal('0'),
                        'buy_prices': [],
                        'sell_prices': [],
                        'counter_asset': counter
                    }
                
                # Create order object
                order = AccountOrder(
                    offer_id=int(offer['id']),
                    account_id=account_id,
                    side=side,
                    price=Decimal(offer['price']),
                    amount=Decimal(offer['amount']),
                    asset_code=token,
                    counter_asset=counter,
                    is_passive=offer.get('type', '') == 'passive',
                    created_at=datetime.fromisoformat(offer['last_modified_time'].replace('Z', '+00:00')),
                    last_modified=datetime.fromisoformat(offer['last_modified_time'].replace('Z', '+00:00'))
                )
                
                # Add to appropriate side
                if side == OrderSide.BUY:
                    positions_by_asset[token]['buy_orders'].append(order)
                    positions_by_asset[token]['buy_volume'] += order.amount
                    positions_by_asset[token]['buy_prices'].append(order.price)
                else:
                    positions_by_asset[token]['sell_orders'].append(order)
                    positions_by_asset[token]['sell_volume'] += order.amount
                    positions_by_asset[token]['sell_prices'].append(order.price)
            
            # Create AccountOrderPosition objects
            positions = []
            for token, data in positions_by_asset.items():
                avg_buy = (
                    sum(data['buy_prices']) / len(data['buy_prices'])
                ) if data['buy_prices'] else Decimal('0')
                
                avg_sell = (
                    sum(data['sell_prices']) / len(data['sell_prices'])
                ) if data['sell_prices'] else Decimal('0')
                
                position = AccountOrderPosition(
                    account_id=account_id,
                    asset_code=token,
                    buy_orders=data['buy_orders'],
                    sell_orders=data['sell_orders'],
                    total_buy_volume=data['buy_volume'],
                    total_sell_volume=data['sell_volume'],
                    avg_buy_price=avg_buy,
                    avg_sell_price=avg_sell,
                    net_position=data['buy_volume'] - data['sell_volume'],
                    last_updated=datetime.now()
                )
                positions.append(position)
            
            # Store to database
            if positions:
                await self._store_account_positions(positions)
            
            logger.info(f"[OrderBook] ✓ Found {len(positions)} position(s) for {account_id}")
            
            return positions
            
        except Exception as e:
            logger.error(f"[OrderBook] Error fetching account orders: {e}")
            raise OrderBookException(f"Failed to fetch account orders: {e}")
    
    async def _store_account_positions(self, positions: List[AccountOrderPosition]):
        """Store account order positions to database"""
        try:
            for pos in positions:
                query = """
                INSERT INTO ubec_main.account_order_positions (
                    account_id, asset_code,
                    total_buy_orders, total_sell_orders,
                    total_buy_volume, total_sell_volume,
                    avg_buy_price, avg_sell_price,
                    last_updated
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (account_id, asset_code) DO UPDATE SET
                    total_buy_orders = EXCLUDED.total_buy_orders,
                    total_sell_orders = EXCLUDED.total_sell_orders,
                    total_buy_volume = EXCLUDED.total_buy_volume,
                    total_sell_volume = EXCLUDED.total_sell_volume,
                    avg_buy_price = EXCLUDED.avg_buy_price,
                    avg_sell_price = EXCLUDED.avg_sell_price,
                    last_updated = EXCLUDED.last_updated
                """
                
                await self.db.execute(
                    query,
                    pos.account_id,
                    pos.asset_code,
                    len(pos.buy_orders),
                    len(pos.sell_orders),
                    pos.total_buy_volume,
                    pos.total_sell_volume,
                    pos.avg_buy_price,
                    pos.avg_sell_price,
                    pos.last_updated
                )
            
        except Exception as e:
            logger.warning(f"[OrderBook] Could not store positions: {e}")
    
    async def get_top_order_accounts(
        self,
        asset_code: str,
        limit: int = 10,
        side: Optional[OrderSide] = None
    ) -> List[Dict]:
        """
        Get top accounts by order volume.
        
        Args:
            asset_code: Token to analyze
            limit: Number of top accounts to return
            side: Optional filter by buy/sell side
            
        Returns:
            List of account data with volumes
        """
        try:
            if side == OrderSide.BUY:
                order_column = "total_buy_volume"
            elif side == OrderSide.SELL:
                order_column = "total_sell_volume"
            else:
                order_column = "(total_buy_volume + total_sell_volume)"
            
            query = f"""
            SELECT 
                account_id,
                asset_code,
                total_buy_orders,
                total_sell_orders,
                total_buy_volume,
                total_sell_volume,
                avg_buy_price,
                avg_sell_price,
                last_updated
            FROM ubec_main.account_order_positions
            WHERE asset_code = $1
            ORDER BY {order_column} DESC
            LIMIT $2
            """
            
            results = await self.db.fetch(query, asset_code, limit)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"[OrderBook] Error fetching top accounts: {e}")
            return []
    
    # ========================================================================
    # MARKET DEPTH ANALYSIS
    # ========================================================================
    
    async def analyze_market_depth(
        self,
        asset_code: str,
        counter_asset: str = "XLM",
        use_cache: bool = True
    ) -> MarketDepthMetrics:
        """
        Analyze market depth and liquidity distribution.
        
        Calculates:
        - Total bid/ask liquidity
        - Depth within price ranges (1%, 5%, 10%)
        - Concentration metrics (top 5 orders)
        - Unique participant counts
        - Market depth score (0-100)
        
        Args:
            asset_code: UBEC token code
            counter_asset: Counter asset
            use_cache: Use cached data
            
        Returns:
            MarketDepthMetrics object
        """
        if not self._initialized:
            raise OrderBookException("Service not initialized")
        
        # Check cache
        cache_key = f"depth:{asset_code}:{counter_asset}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        try:
            # Get order book snapshot
            snapshot = await self.fetch_orderbook_snapshot(asset_code, counter_asset, use_cache)
            
            # Calculate total liquidity
            total_bid_liq = snapshot.bid_depth_total
            total_ask_liq = snapshot.ask_depth_total
            
            # Liquidity within percentage ranges
            mid = snapshot.mid_price
            depth_1pct = self._calculate_depth_in_range(snapshot, mid, Decimal('0.01'))
            depth_5pct = self._calculate_depth_in_range(snapshot, mid, Decimal('0.05'))
            depth_10pct = self._calculate_depth_in_range(snapshot, mid, Decimal('0.10'))
            
            # Top 5 concentration
            top_5_bid_vol = sum(
                level.amount for level in snapshot.bids[:5]
            ) if len(snapshot.bids) >= 5 else total_bid_liq
            
            top_5_ask_vol = sum(
                level.amount for level in snapshot.asks[:5]
            ) if len(snapshot.asks) >= 5 else total_ask_liq
            
            top_5_bid_pct = (top_5_bid_vol / total_bid_liq * 100) if total_bid_liq > 0 else Decimal('0')
            top_5_ask_pct = (top_5_ask_vol / total_ask_liq * 100) if total_ask_liq > 0 else Decimal('0')
            
            # Get unique account counts
            unique_buyers, unique_sellers = await self._count_unique_traders(asset_code)
            
            # Calculate market depth score
            depth_score = self._calculate_market_depth_score(
                total_bid_liq,
                total_ask_liq,
                depth_1pct,
                unique_buyers,
                unique_sellers,
                top_5_bid_pct,
                top_5_ask_pct
            )
            
            metrics = MarketDepthMetrics(
                asset_code=asset_code,
                counter_asset=counter_asset,
                timestamp=datetime.now(),
                total_bid_liquidity=total_bid_liq,
                total_ask_liquidity=total_ask_liq,
                bid_ask_ratio=total_bid_liq / total_ask_liq if total_ask_liq > 0 else Decimal('0'),
                depth_within_1pct=depth_1pct,
                depth_within_5pct=depth_5pct,
                depth_within_10pct=depth_10pct,
                top_5_bid_concentration=top_5_bid_pct,
                top_5_ask_concentration=top_5_ask_pct,
                unique_bid_accounts=unique_buyers,
                unique_ask_accounts=unique_sellers,
                bid_levels=len(snapshot.bids),
                ask_levels=len(snapshot.asks),
                market_depth_score=depth_score
            )
            
            # Cache result
            self._set_cached(cache_key, metrics)
            
            logger.info(f"[OrderBook] ✓ Market depth analyzed: Score={depth_score:.1f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"[OrderBook] Error analyzing market depth: {e}")
            raise OrderBookException(f"Market depth analysis failed: {e}")
    
    def _calculate_depth_in_range(
        self,
        snapshot: OrderBookSnapshot,
        mid_price: Decimal,
        pct_range: Decimal
    ) -> Decimal:
        """Calculate total liquidity within percentage range of mid price"""
        if mid_price == 0:
            return Decimal('0')
        
        lower_bound = mid_price * (1 - pct_range)
        upper_bound = mid_price * (1 + pct_range)
        
        # Bid depth in range
        bid_depth = sum(
            level.amount for level in snapshot.bids
            if level.price >= lower_bound
        )
        
        # Ask depth in range
        ask_depth = sum(
            level.amount for level in snapshot.asks
            if level.price <= upper_bound
        )
        
        return bid_depth + ask_depth
    
    def _calculate_market_depth_score(
        self,
        bid_liquidity: Decimal,
        ask_liquidity: Decimal,
        depth_1pct: Decimal,
        unique_buyers: int,
        unique_sellers: int,
        bid_concentration: Decimal,
        ask_concentration: Decimal
    ) -> Decimal:
        """
        Calculate composite market depth score (0-100).
        
        Factors:
        - Total liquidity (30%)
        - Depth within 1% (30%)
        - Number of participants (20%)
        - Low concentration (20%)
        """
        # Total liquidity score (normalize to reasonable range)
        total_liq = float(bid_liquidity + ask_liquidity)
        liq_score = min(total_liq / 10000, 1.0) * 30  # 30 points max
        
        # Tight depth score
        depth_score = min(float(depth_1pct) / 5000, 1.0) * 30  # 30 points max
        
        # Participation score
        total_traders = unique_buyers + unique_sellers
        participation_score = min(total_traders / 50, 1.0) * 20  # 20 points max
        
        # Concentration score (lower is better)
        avg_concentration = (float(bid_concentration) + float(ask_concentration)) / 2
        concentration_score = max(0, (100 - avg_concentration) / 100) * 20  # 20 points max
        
        total_score = Decimal(str(liq_score + depth_score + participation_score + concentration_score))
        
        return total_score
    
    async def _count_unique_traders(self, asset_code: str) -> Tuple[int, int]:
        """Count unique buying and selling accounts"""
        try:
            query = """
            SELECT 
                COUNT(DISTINCT CASE WHEN total_buy_orders > 0 THEN account_id END) as buyers,
                COUNT(DISTINCT CASE WHEN total_sell_orders > 0 THEN account_id END) as sellers
            FROM ubec_main.account_order_positions
            WHERE asset_code = $1
            """
            
            result = await self.db.fetchrow(query, asset_code)
            
            if result:
                return result['buyers'] or 0, result['sellers'] or 0
            
            return 0, 0
            
        except Exception as e:
            logger.warning(f"[OrderBook] Could not count traders: {e}")
            return 0, 0
    
    # ========================================================================
    # ORDER FLOW ANALYTICS
    # ========================================================================
    
    async def analyze_order_flow(
        self,
        asset_code: str,
        period_minutes: int = 15
    ) -> OrderFlowMetrics:
        """
        Analyze order flow and buy/sell pressure over a time period.
        
        Tracks:
        - New order creation
        - Order cancellations
        - Filled volumes
        - Buy/sell pressure scores (0-100)
        - Order imbalance (-1 to 1)
        
        Args:
            asset_code: Token to analyze
            period_minutes: Analysis time window
            
        Returns:
            OrderFlowMetrics object
        """
        if not self._initialized:
            raise OrderBookException("Service not initialized")
        
        try:
            cutoff_time = datetime.now() - timedelta(minutes=period_minutes)
            
            # Query database for order flow data
            query = """
            SELECT 
                side,
                COUNT(*) FILTER (WHERE status = 'active' AND created_at >= $1) as new_orders,
                COUNT(*) FILTER (WHERE status = 'cancelled' AND updated_at >= $1) as cancelled,
                COALESCE(SUM(amount) FILTER (WHERE status = 'filled' AND updated_at >= $1), 0) as filled_volume
            FROM ubec_main.stellar_offers
            WHERE (selling_asset = $2 OR buying_asset = $2)
            AND (created_at >= $1 OR updated_at >= $1)
            GROUP BY side
            """
            
            results = await self.db.fetch(query, cutoff_time, asset_code)
            
            # Parse results
            buy_data = next((dict(r) for r in results if r['side'] == 'buy'), {})
            sell_data = next((dict(r) for r in results if r['side'] == 'sell'), {})
            
            new_buys = buy_data.get('new_orders', 0)
            new_sells = sell_data.get('new_orders', 0)
            cancelled_buys = buy_data.get('cancelled', 0)
            cancelled_sells = sell_data.get('cancelled', 0)
            filled_buy_vol = Decimal(str(buy_data.get('filled_volume', 0)))
            filled_sell_vol = Decimal(str(sell_data.get('filled_volume', 0)))
            
            # Calculate pressure scores (0-100)
            total_activity = new_buys + new_sells + 1  # Avoid division by zero
            buy_pressure = Decimal(str((new_buys / total_activity) * 100))
            sell_pressure = Decimal(str((new_sells / total_activity) * 100))
            
            # Order imbalance (-1 to 1)
            total_new = new_buys + new_sells
            if total_new > 0:
                imbalance = Decimal(str((new_buys - new_sells) / total_new))
            else:
                imbalance = Decimal('0')
            
            # Net flow
            net_flow = filled_buy_vol - filled_sell_vol
            
            metrics = OrderFlowMetrics(
                asset_code=asset_code,
                period_minutes=period_minutes,
                timestamp=datetime.now(),
                buy_pressure_score=buy_pressure,
                sell_pressure_score=sell_pressure,
                order_imbalance=imbalance,
                new_buy_orders=new_buys,
                new_sell_orders=new_sells,
                cancelled_buy_orders=cancelled_buys,
                cancelled_sell_orders=cancelled_sells,
                filled_buy_volume=filled_buy_vol,
                filled_sell_volume=filled_sell_vol,
                net_flow=net_flow
            )
            
            logger.info(f"[OrderBook] ✓ Order flow: Buy={buy_pressure:.1f}%, "
                       f"Sell={sell_pressure:.1f}%, Imbalance={imbalance:.2f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"[OrderBook] Error analyzing order flow: {e}")
            raise OrderBookException(f"Order flow analysis failed: {e}")
    
    # ========================================================================
    # INTEGRATED ANALYTICS
    # ========================================================================
    
    async def get_combined_liquidity_analysis(
        self,
        asset_code: str,
        analytics_service=None
    ) -> LiquidityHealth:
        """
        Combine order book depth with overall liquidity metrics.
        
        Integrates:
        - Order book depth (this service)
        - Token circulation (analytics service)
        - Holder distribution (analytics service)
        
        Args:
            asset_code: Token to analyze
            analytics_service: Optional analytics service instance
            
        Returns:
            LiquidityHealth with combined metrics
        """
        if not self._initialized:
            raise OrderBookException("Service not initialized")
        
        try:
            # Get order book metrics
            depth_metrics = await self.analyze_market_depth(asset_code)
            snapshot = await self.fetch_orderbook_snapshot(asset_code)
            
            orderbook_liq = {
                'bid_depth': float(depth_metrics.total_bid_liquidity),
                'ask_depth': float(depth_metrics.total_ask_liquidity),
                'spread_bps': snapshot.spread_bps,
                'depth_1pct': float(depth_metrics.depth_within_1pct),
                'depth_5pct': float(depth_metrics.depth_within_5pct),
                'unique_traders': depth_metrics.unique_bid_accounts + depth_metrics.unique_ask_accounts,
                'market_depth_score': float(depth_metrics.market_depth_score)
            }
            
            # Get token liquidity from analytics service if available
            token_liq = {}
            if analytics_service:
                try:
                    liq_metrics = await analytics_service.get_liquidity_metrics(asset_code)
                    token_liq = {
                        'circulating_supply': float(liq_metrics.circulating_supply),
                        'available_liquidity': float(liq_metrics.available_liquidity),
                        'liquidity_ratio': float(liq_metrics.liquidity_ratio)
                    }
                except Exception as e:
                    logger.warning(f"[OrderBook] Could not get analytics data: {e}")
            
            # Combined metrics
            combined = {
                'orderbook_to_supply_ratio': (
                    (depth_metrics.total_bid_liquidity + depth_metrics.total_ask_liquidity) /
                    Decimal(str(token_liq.get('circulating_supply', 1)))
                ) if token_liq else Decimal('0'),
                'liquidity_concentration': depth_metrics.top_5_bid_concentration
            }
            
            # Calculate health score
            health_score = self._calculate_liquidity_health_score(
                orderbook_liq,
                token_liq,
                combined
            )
            
            return LiquidityHealth(
                asset_code=asset_code,
                timestamp=datetime.now(),
                orderbook_liquidity=orderbook_liq,
                token_liquidity=token_liq,
                combined_metrics={k: float(v) for k, v in combined.items()},
                liquidity_health_score=health_score
            )
            
        except Exception as e:
            logger.error(f"[OrderBook] Error in combined analysis: {e}")
            raise OrderBookException(f"Combined liquidity analysis failed: {e}")
    
    def _calculate_liquidity_health_score(
        self,
        orderbook_liq: Dict,
        token_liq: Dict,
        combined: Dict
    ) -> Decimal:
        """Calculate overall liquidity health score (0-100)"""
        # Market depth component (40%)
        depth_score = orderbook_liq.get('market_depth_score', 0) * 0.4
        
        # Token liquidity component (30%)
        if token_liq:
            token_ratio = token_liq.get('liquidity_ratio', 0)
            token_score = min(token_ratio / 100, 1.0) * 30
        else:
            token_score = 0
        
        # Spread component (20%)
        spread_bps = orderbook_liq.get('spread_bps', 1000)
        spread_score = max(0, (1000 - spread_bps) / 1000) * 20
        
        # Participation component (10%)
        traders = orderbook_liq.get('unique_traders', 0)
        participation_score = min(traders / 50, 1.0) * 10
        
        total = Decimal(str(depth_score + token_score + spread_score + participation_score))
        
        return total
    
    # ========================================================================
    # HISTORICAL ANALYSIS
    # ========================================================================
    
    async def get_historical_spreads(
        self,
        asset_code: str,
        hours: int = 24
    ) -> List[Dict]:
        """
        Get historical spread data.
        
        Args:
            asset_code: Token to analyze
            hours: Lookback period
            
        Returns:
            List of spread data points
        """
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            
            query = """
            SELECT 
                snapshot_time,
                spread_bps,
                best_bid,
                best_ask,
                bid_depth_total,
                ask_depth_total
            FROM ubec_main.orderbook_snapshots
            WHERE asset_code = $1
            AND snapshot_time >= $2
            ORDER BY snapshot_time ASC
            """
            
            results = await self.db.fetch(query, asset_code, cutoff)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"[OrderBook] Error fetching historical spreads: {e}")
            return []
    
    async def detect_whale_orders(
        self,
        asset_code: str,
        threshold_pct: float = 5.0
    ) -> List[Dict]:
        """
        Detect large orders (whales) that represent significant % of liquidity.
        
        Args:
            asset_code: Token to analyze
            threshold_pct: Minimum % of total liquidity to qualify as whale
            
        Returns:
            List of whale order data
        """
        try:
            # Get current depth
            depth = await self.analyze_market_depth(asset_code)
            total_liquidity = depth.total_bid_liquidity + depth.total_ask_liquidity
            
            if total_liquidity == 0:
                return []
            
            threshold_amount = total_liquidity * Decimal(str(threshold_pct / 100))
            
            # Get large positions
            query = """
            SELECT 
                account_id,
                asset_code,
                total_buy_volume,
                total_sell_volume,
                avg_buy_price,
                avg_sell_price,
                (total_buy_volume + total_sell_volume) as total_volume
            FROM ubec_main.account_order_positions
            WHERE asset_code = $1
            AND (total_buy_volume + total_sell_volume) >= $2
            ORDER BY total_volume DESC
            """
            
            results = await self.db.fetch(query, asset_code, threshold_amount)
            
            whale_orders = []
            for row in results:
                whale_orders.append({
                    'account_id': row['account_id'],
                    'total_volume': float(row['total_volume']),
                    'buy_volume': float(row['total_buy_volume']),
                    'sell_volume': float(row['total_sell_volume']),
                    'pct_of_liquidity': float(row['total_volume'] / total_liquidity * 100),
                    'avg_buy_price': float(row['avg_buy_price']) if row['avg_buy_price'] else None,
                    'avg_sell_price': float(row['avg_sell_price']) if row['avg_sell_price'] else None
                })
            
            logger.info(f"[OrderBook] ✓ Detected {len(whale_orders)} whale orders")
            
            return whale_orders
            
        except Exception as e:
            logger.error(f"[OrderBook] Error detecting whale orders: {e}")
            return []
    
    # ========================================================================
    # BACKGROUND SYNC
    # ========================================================================
    
    async def _background_orderbook_sync(self):
        """Background task to periodically sync order book data"""
        logger.info("[OrderBook] Starting background sync task")
        
        while self._initialized:
            try:
                # Sync all UBEC tokens
                for token in TokenCode:
                    try:
                        # Fetch snapshot
                        await self.fetch_orderbook_snapshot(token.value, use_cache=False)
                        
                        # Small delay between tokens
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"[OrderBook] Sync error for {token.value}: {e}")
                
                # Wait for next sync interval
                await asyncio.sleep(self.sync_interval)
                
            except asyncio.CancelledError:
                logger.info("[OrderBook] Background sync cancelled")
                break
            except Exception as e:
                logger.error(f"[OrderBook] Background sync error: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    # ========================================================================
    # CLEANUP
    # ========================================================================
    
    async def close(self):
        """Cleanup and close connections"""
        if not self._initialized:
            return
        
        self._initialized = False
        
        # Cancel background task
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        
        # Clear cache
        self.clear_cache()
        
        logger.info("[OrderBook] ✓ Service closed")


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_orderbook_service(
    db_manager,
    stellar_client,
    issuer_address: str,
    **kwargs
) -> UBECOrderBookService:
    """
    Factory function to create order book service instance.
    
    Args:
        db_manager: AsyncDatabaseManager instance
        stellar_client: Stellar ServerAsync client
        issuer_address: UBEC token issuer address
        **kwargs: Additional service configuration
        
    Returns:
        UBECOrderBookService instance
        
    Example:
        service = create_orderbook_service(
            db_manager=db,
            stellar_client=stellar,
            issuer_address="GXXX...",
            cache_ttl=120,
            sync_interval=600
        )
        await service.initialize()
    """
    return UBECOrderBookService(
        db_manager=db_manager,
        stellar_client=stellar_client,
        issuer_address=issuer_address,
        **kwargs
    )
