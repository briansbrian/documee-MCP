"""Unified 3-Tier Cache Manager for MCP Server.

This module implements a high-performance caching system with three tiers:
- Tier 1: Memory cache with LRU eviction (<0.001s access)
- Tier 2: SQLite persistent cache (<0.1s access)
- Tier 3: Optional Redis distributed cache (<0.2s access)

The cache manager supports cache promotion, statistics tracking, and session state management.
"""

import json
import logging
import sys
import time
from collections import OrderedDict
from datetime import datetime
from typing import Any, Optional

import aiosqlite


logger = logging.getLogger(__name__)


class UnifiedCacheManager:
    """3-Tier cache manager with Memory, SQLite, and optional Redis support.
    
    Provides high-performance caching with automatic promotion between tiers,
    LRU eviction, and comprehensive statistics tracking.
    """
    
    def __init__(
        self,
        max_memory_mb: int = 500,
        sqlite_path: str = "cache_db/cache.db",
        redis_url: Optional[str] = None
    ):
        """Initialize the cache manager.
        
        Args:
            max_memory_mb: Maximum memory cache size in MB (default: 500)
            sqlite_path: Path to SQLite database file (default: "cache_db/cache.db")
            redis_url: Optional Redis connection URL (default: None)
        """
        # Memory cache (Tier 1) - LRU using OrderedDict
        self.memory_cache: OrderedDict[str, dict] = OrderedDict()
        self.current_memory_size = 0
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        
        # SQLite cache (Tier 2)
        self.sqlite_path = sqlite_path
        self.sqlite_conn: Optional[aiosqlite.Connection] = None
        
        # Redis cache (Tier 3) - optional
        self.redis_url = redis_url
        self.redis_client = None
        
        # Session state storage
        self.session_state: dict[str, dict] = {}
        
        # Resource storage (for MCP resources)
        self.resources: dict[str, Any] = {}
        
        # Statistics tracking
        self.stats = {
            "memory_hits": 0,
            "memory_misses": 0,
            "sqlite_hits": 0,
            "sqlite_misses": 0,
            "redis_hits": 0,
            "redis_misses": 0,
            "evictions": 0,
            "total_requests": 0,
        }
        
        # Initialization flag
        self._initialized = False
    
    async def initialize(self):
        """Initialize cache connections and create database tables.
        
        Creates SQLite database tables and establishes Redis connection if configured.
        """
        if self._initialized:
            logger.debug("Cache manager already initialized")
            return
        
        logger.info(f"Initializing UnifiedCacheManager (max_memory: {self.max_memory_bytes / 1024 / 1024:.1f}MB)")
        
        # Initialize SQLite
        try:
            self.sqlite_conn = await aiosqlite.connect(self.sqlite_path)
            await self._create_tables()
            logger.info(f"SQLite cache initialized at {self.sqlite_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite cache: {e}")
            raise
        
        # Initialize Redis if URL provided
        if self.redis_url:
            try:
                # Import redis only if needed
                import redis.asyncio as aioredis
                self.redis_client = await aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                # Test connection
                await self.redis_client.ping()
                logger.info(f"Redis cache initialized at {self.redis_url}")
            except ImportError:
                logger.warning("redis package not installed, Redis cache disabled")
                self.redis_client = None
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}. Continuing without Redis.")
                self.redis_client = None
        
        self._initialized = True
        logger.info("UnifiedCacheManager initialization complete")
    
    async def close(self):
        """Close all cache connections and cleanup resources."""
        if not self._initialized:
            return
        
        logger.info("Closing UnifiedCacheManager")
        
        # Close SQLite connection
        if self.sqlite_conn:
            try:
                await self.sqlite_conn.close()
                logger.debug("SQLite connection closed")
            except Exception as e:
                logger.error(f"Error closing SQLite connection: {e}")
        
        # Close Redis connection
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.debug("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
        
        # Clear memory cache
        self.memory_cache.clear()
        self.current_memory_size = 0
        self.session_state.clear()
        self.resources.clear()
        
        self._initialized = False
        logger.info("UnifiedCacheManager closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        return False
    
    async def _create_tables(self):
        """Create SQLite database tables if they don't exist."""
        if not self.sqlite_conn:
            raise RuntimeError("SQLite connection not initialized")
        
        # File cache table
        await self.sqlite_conn.execute("""
            CREATE TABLE IF NOT EXISTS file_cache (
                path TEXT PRIMARY KEY,
                content TEXT,
                hash TEXT,
                language TEXT,
                size INTEGER,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analysis cache table
        await self.sqlite_conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                key TEXT PRIMARY KEY,
                data TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ttl INTEGER
            )
        """)
        
        # Session state table
        await self.sqlite_conn.execute("""
            CREATE TABLE IF NOT EXISTS session_state (
                codebase_id TEXT PRIMARY KEY,
                state TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.sqlite_conn.commit()
        logger.debug("SQLite tables created/verified")

    
    def _get_size(self, data: Any) -> int:
        """Estimate the size of data in bytes.
        
        Args:
            data: Data to measure
            
        Returns:
            Estimated size in bytes
        """
        try:
            # Serialize to JSON and measure
            json_str = json.dumps(data)
            return sys.getsizeof(json_str)
        except Exception:
            # Fallback to sys.getsizeof
            return sys.getsizeof(data)
    
    def _evict_lru(self):
        """Evict least recently used item from memory cache."""
        if not self.memory_cache:
            return
        
        # Remove oldest item (first item in OrderedDict)
        key, value = self.memory_cache.popitem(last=False)
        size = self._get_size(value)
        self.current_memory_size -= size
        self.stats["evictions"] += 1
        logger.debug(f"Evicted LRU item: {key} (freed {size} bytes)")
    
    def _ensure_memory_space(self, required_size: int):
        """Ensure enough memory space by evicting LRU items if needed.
        
        Args:
            required_size: Required space in bytes
        """
        while (self.current_memory_size + required_size > self.max_memory_bytes 
               and self.memory_cache):
            self._evict_lru()
    
    async def get_analysis(self, key: str) -> Optional[dict]:
        """Get analysis result from cache with tier promotion.
        
        Checks Memory → SQLite → Redis in order, promoting to faster tiers on hit.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        self.stats["total_requests"] += 1
        
        # Check memory cache (Tier 1)
        if key in self.memory_cache:
            self.stats["memory_hits"] += 1
            # Move to end (most recently used)
            self.memory_cache.move_to_end(key)
            logger.debug(f"Cache hit (memory): {key}")
            return self.memory_cache[key]["data"]
        
        self.stats["memory_misses"] += 1
        
        # Check SQLite cache (Tier 2)
        if self.sqlite_conn:
            try:
                async with self.sqlite_conn.execute(
                    "SELECT data, ttl, cached_at FROM analysis_cache WHERE key = ?",
                    (key,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        data_json, ttl, cached_at = row
                        
                        # Check if expired
                        if ttl > 0:
                            cached_time = datetime.fromisoformat(cached_at).timestamp()
                            if time.time() - cached_time > ttl:
                                logger.debug(f"Cache expired (sqlite): {key}")
                                self.stats["sqlite_misses"] += 1
                                return None
                        
                        data = json.loads(data_json)
                        self.stats["sqlite_hits"] += 1
                        logger.debug(f"Cache hit (sqlite): {key}")
                        
                        # Promote to memory cache
                        await self._promote_to_memory(key, data)
                        
                        return data
            except Exception as e:
                logger.error(f"Error reading from SQLite cache: {e}")
        
        self.stats["sqlite_misses"] += 1
        
        # Check Redis cache (Tier 3)
        if self.redis_client:
            try:
                data_json = await self.redis_client.get(f"analysis:{key}")
                if data_json:
                    data = json.loads(data_json)
                    self.stats["redis_hits"] += 1
                    logger.debug(f"Cache hit (redis): {key}")
                    
                    # Promote to memory and SQLite
                    await self._promote_to_memory(key, data)
                    await self._promote_to_sqlite(key, data, ttl=3600)
                    
                    return data
            except Exception as e:
                logger.error(f"Error reading from Redis cache: {e}")
        
        self.stats["redis_misses"] += 1
        logger.debug(f"Cache miss (all tiers): {key}")
        return None
    
    async def _promote_to_memory(self, key: str, data: dict):
        """Promote data to memory cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        size = self._get_size(data)
        self._ensure_memory_space(size)
        
        self.memory_cache[key] = {"data": data, "size": size}
        self.current_memory_size += size
        logger.debug(f"Promoted to memory: {key} ({size} bytes)")
    
    async def _promote_to_sqlite(self, key: str, data: dict, ttl: int):
        """Promote data to SQLite cache.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
        """
        if not self.sqlite_conn:
            return
        
        try:
            data_json = json.dumps(data)
            await self.sqlite_conn.execute(
                """
                INSERT OR REPLACE INTO analysis_cache (key, data, cached_at, ttl)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                """,
                (key, data_json, ttl)
            )
            await self.sqlite_conn.commit()
            logger.debug(f"Promoted to sqlite: {key}")
        except Exception as e:
            logger.error(f"Error promoting to SQLite: {e}")
    
    async def set_analysis(self, key: str, data: dict, ttl: int = 3600):
        """Store analysis result in all cache tiers.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds (default: 3600)
        """
        # Store in memory cache (Tier 1)
        size = self._get_size(data)
        self._ensure_memory_space(size)
        
        self.memory_cache[key] = {"data": data, "size": size}
        self.current_memory_size += size
        logger.debug(f"Stored in memory: {key} ({size} bytes)")
        
        # Store in SQLite cache (Tier 2)
        if self.sqlite_conn:
            try:
                data_json = json.dumps(data)
                await self.sqlite_conn.execute(
                    """
                    INSERT OR REPLACE INTO analysis_cache (key, data, cached_at, ttl)
                    VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                    """,
                    (key, data_json, ttl)
                )
                await self.sqlite_conn.commit()
                logger.debug(f"Stored in sqlite: {key}")
            except Exception as e:
                logger.error(f"Error storing in SQLite: {e}")
        
        # Store in Redis cache (Tier 3)
        if self.redis_client:
            try:
                data_json = json.dumps(data)
                await self.redis_client.setex(
                    f"analysis:{key}",
                    ttl,
                    data_json
                )
                logger.debug(f"Stored in redis: {key}")
            except Exception as e:
                logger.error(f"Error storing in Redis: {e}")
    
    async def get_session(self, codebase_id: str) -> Optional[dict]:
        """Get session state for a codebase.
        
        Args:
            codebase_id: Unique codebase identifier
            
        Returns:
            Session state or None if not found
        """
        # Check memory first
        if codebase_id in self.session_state:
            logger.debug(f"Session hit (memory): {codebase_id}")
            return self.session_state[codebase_id]
        
        # Check SQLite
        if self.sqlite_conn:
            try:
                async with self.sqlite_conn.execute(
                    "SELECT state FROM session_state WHERE codebase_id = ?",
                    (codebase_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        state = json.loads(row[0])
                        # Cache in memory
                        self.session_state[codebase_id] = state
                        logger.debug(f"Session hit (sqlite): {codebase_id}")
                        return state
            except Exception as e:
                logger.error(f"Error reading session from SQLite: {e}")
        
        logger.debug(f"Session miss: {codebase_id}")
        return None
    
    async def set_session(self, codebase_id: str, state: dict):
        """Store session state for a codebase.
        
        Args:
            codebase_id: Unique codebase identifier
            state: Session state data
        """
        # Store in memory
        self.session_state[codebase_id] = state
        logger.debug(f"Session stored (memory): {codebase_id}")
        
        # Store in SQLite
        if self.sqlite_conn:
            try:
                state_json = json.dumps(state)
                await self.sqlite_conn.execute(
                    """
                    INSERT OR REPLACE INTO session_state (codebase_id, state, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """,
                    (codebase_id, state_json)
                )
                await self.sqlite_conn.commit()
                logger.debug(f"Session stored (sqlite): {codebase_id}")
            except Exception as e:
                logger.error(f"Error storing session in SQLite: {e}")
    
    async def get_resource(self, key: str) -> Optional[Any]:
        """Get MCP resource data.
        
        Args:
            key: Resource key
            
        Returns:
            Resource data or None if not found
        """
        resource = self.resources.get(key)
        if resource:
            logger.debug(f"Resource hit: {key}")
        else:
            logger.debug(f"Resource miss: {key}")
        return resource
    
    async def set_resource(self, key: str, data: Any):
        """Store MCP resource data.
        
        Args:
            key: Resource key
            data: Resource data
        """
        self.resources[key] = data
        logger.debug(f"Resource stored: {key}")
    
    async def get_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics including hit rates, memory usage, etc.
        """
        total_hits = (
            self.stats["memory_hits"] + 
            self.stats["sqlite_hits"] + 
            self.stats["redis_hits"]
        )
        total_requests = self.stats["total_requests"]
        hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
        
        # Count cache entries
        file_cache_entries = 0
        analysis_cache_entries = 0
        if self.sqlite_conn:
            try:
                async with self.sqlite_conn.execute(
                    "SELECT COUNT(*) FROM file_cache"
                ) as cursor:
                    row = await cursor.fetchone()
                    file_cache_entries = row[0] if row else 0
                
                async with self.sqlite_conn.execute(
                    "SELECT COUNT(*) FROM analysis_cache"
                ) as cursor:
                    row = await cursor.fetchone()
                    analysis_cache_entries = row[0] if row else 0
            except Exception as e:
                logger.error(f"Error counting cache entries: {e}")
        
        return {
            "hit_rate": hit_rate,
            "memory_hits": self.stats["memory_hits"],
            "memory_misses": self.stats["memory_misses"],
            "sqlite_hits": self.stats["sqlite_hits"],
            "sqlite_misses": self.stats["sqlite_misses"],
            "redis_hits": self.stats["redis_hits"],
            "redis_misses": self.stats["redis_misses"],
            "evictions": self.stats["evictions"],
            "total_requests": total_requests,
            "current_memory_mb": self.current_memory_size / 1024 / 1024,
            "max_memory_mb": self.max_memory_bytes / 1024 / 1024,
            "file_cache_entries": file_cache_entries,
            "analysis_cache_entries": analysis_cache_entries,
            "active_sessions": len(self.session_state),
        }
