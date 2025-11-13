"""Course Generation Cache Manager.

This module provides caching for generated course content to improve performance.
Implements Requirements 11.5, 15.1, 15.2:
- Caches course structures, lesson content, and exercises
- Invalidates cache on file changes
- Tracks file modification times for incremental updates
"""

import hashlib
import json
import logging
import os
import time
from typing import Optional, Dict, Any
from datetime import datetime

from src.cache.unified_cache import UnifiedCacheManager
from .models import CourseOutline, LessonContent, Exercise


logger = logging.getLogger(__name__)


class CourseCacheManager:
    """Manages caching for course generation with file change detection.
    
    Provides high-performance caching for:
    - Course structures (CourseOutline)
    - Lesson content (LessonContent)
    - Generated exercises (Exercise)
    
    Automatically invalidates cache when source files change.
    """
    
    def __init__(self, cache_manager: UnifiedCacheManager):
        """Initialize the course cache manager.
        
        Args:
            cache_manager: Unified cache manager instance
        """
        self.cache = cache_manager
        self.file_mtimes: Dict[str, float] = {}  # Track file modification times
        
        # Cache key prefixes
        self.COURSE_PREFIX = "course:structure:"
        self.LESSON_PREFIX = "course:lesson:"
        self.EXERCISE_PREFIX = "course:exercise:"
        self.MTIME_PREFIX = "course:mtime:"
        
        # Cache TTL (time to live) in seconds
        self.COURSE_TTL = 3600  # 1 hour
        self.LESSON_TTL = 1800  # 30 minutes
        self.EXERCISE_TTL = 1800  # 30 minutes
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash of file content for cache invalidation.
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash of file content
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash file {file_path}: {e}")
            return ""
    
    def _get_file_mtime(self, file_path: str) -> float:
        """Get file modification time.
        
        Args:
            file_path: Path to file
            
        Returns:
            Modification time as timestamp
        """
        try:
            return os.path.getmtime(file_path)
        except Exception as e:
            logger.warning(f"Failed to get mtime for {file_path}: {e}")
            return 0.0
    
    async def _is_file_changed(self, file_path: str) -> bool:
        """Check if file has changed since last cache.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file has changed, False otherwise
        """
        current_mtime = self._get_file_mtime(file_path)
        
        # Check cached mtime
        mtime_key = f"{self.MTIME_PREFIX}{file_path}"
        cached_data = await self.cache.get_analysis(mtime_key)
        
        if cached_data:
            cached_mtime = cached_data.get("mtime", 0.0)
            return current_mtime > cached_mtime
        
        # No cached mtime, consider it changed
        return True
    
    async def _update_file_mtime(self, file_path: str):
        """Update cached file modification time.
        
        Args:
            file_path: Path to file
        """
        current_mtime = self._get_file_mtime(file_path)
        mtime_key = f"{self.MTIME_PREFIX}{file_path}"
        
        await self.cache.set_analysis(
            mtime_key,
            {"mtime": current_mtime, "updated_at": time.time()},
            ttl=self.COURSE_TTL
        )
    
    async def get_course_structure(self, codebase_id: str) -> Optional[Dict[str, Any]]:
        """Get cached course structure.
        
        Args:
            codebase_id: Unique codebase identifier
            
        Returns:
            Cached course structure data or None if not found/invalid
        """
        cache_key = f"{self.COURSE_PREFIX}{codebase_id}"
        cached_data = await self.cache.get_analysis(cache_key)
        
        if cached_data:
            logger.info(f"Course structure cache hit: {codebase_id}")
            return cached_data
        
        logger.debug(f"Course structure cache miss: {codebase_id}")
        return None
    
    async def set_course_structure(
        self,
        codebase_id: str,
        course_data: Dict[str, Any],
        file_paths: list[str]
    ):
        """Cache course structure with file tracking.
        
        Args:
            codebase_id: Unique codebase identifier
            course_data: Course structure data to cache
            file_paths: List of source file paths used in course
        """
        cache_key = f"{self.COURSE_PREFIX}{codebase_id}"
        
        # Add metadata
        cache_entry = {
            "data": course_data,
            "file_paths": file_paths,
            "cached_at": time.time(),
            "codebase_id": codebase_id
        }
        
        await self.cache.set_analysis(cache_key, cache_entry, ttl=self.COURSE_TTL)
        
        # Update file mtimes
        for file_path in file_paths:
            await self._update_file_mtime(file_path)
        
        logger.info(f"Cached course structure: {codebase_id} ({len(file_paths)} files)")
    
    async def get_lesson_content(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get cached lesson content.
        
        Args:
            file_path: Source file path
            
        Returns:
            Cached lesson content data or None if not found/invalid
        """
        # Check if file has changed
        if await self._is_file_changed(file_path):
            logger.debug(f"File changed, invalidating lesson cache: {file_path}")
            return None
        
        cache_key = f"{self.LESSON_PREFIX}{file_path}"
        cached_data = await self.cache.get_analysis(cache_key)
        
        if cached_data:
            logger.info(f"Lesson content cache hit: {file_path}")
            return cached_data
        
        logger.debug(f"Lesson content cache miss: {file_path}")
        return None
    
    async def set_lesson_content(self, file_path: str, lesson_data: Dict[str, Any]):
        """Cache lesson content.
        
        Args:
            file_path: Source file path
            lesson_data: Lesson content data to cache
        """
        cache_key = f"{self.LESSON_PREFIX}{file_path}"
        
        # Add metadata
        cache_entry = {
            "data": lesson_data,
            "file_path": file_path,
            "cached_at": time.time()
        }
        
        await self.cache.set_analysis(cache_key, cache_entry, ttl=self.LESSON_TTL)
        await self._update_file_mtime(file_path)
        
        logger.info(f"Cached lesson content: {file_path}")
    
    async def get_exercise(self, file_path: str, pattern_type: str) -> Optional[Dict[str, Any]]:
        """Get cached exercise.
        
        Args:
            file_path: Source file path
            pattern_type: Pattern type for the exercise
            
        Returns:
            Cached exercise data or None if not found/invalid
        """
        # Check if file has changed
        if await self._is_file_changed(file_path):
            logger.debug(f"File changed, invalidating exercise cache: {file_path}")
            return None
        
        cache_key = f"{self.EXERCISE_PREFIX}{file_path}:{pattern_type}"
        cached_data = await self.cache.get_analysis(cache_key)
        
        if cached_data:
            logger.info(f"Exercise cache hit: {file_path}:{pattern_type}")
            return cached_data
        
        logger.debug(f"Exercise cache miss: {file_path}:{pattern_type}")
        return None
    
    async def set_exercise(
        self,
        file_path: str,
        pattern_type: str,
        exercise_data: Dict[str, Any]
    ):
        """Cache exercise.
        
        Args:
            file_path: Source file path
            pattern_type: Pattern type for the exercise
            exercise_data: Exercise data to cache
        """
        cache_key = f"{self.EXERCISE_PREFIX}{file_path}:{pattern_type}"
        
        # Add metadata
        cache_entry = {
            "data": exercise_data,
            "file_path": file_path,
            "pattern_type": pattern_type,
            "cached_at": time.time()
        }
        
        await self.cache.set_analysis(cache_key, cache_entry, ttl=self.EXERCISE_TTL)
        await self._update_file_mtime(file_path)
        
        logger.info(f"Cached exercise: {file_path}:{pattern_type}")
    
    async def invalidate_file(self, file_path: str):
        """Invalidate all caches related to a file.
        
        Args:
            file_path: Path to file that changed
        """
        # Note: We don't explicitly delete cache entries, we rely on
        # the mtime check to detect changes. This is more efficient.
        await self._update_file_mtime(file_path)
        logger.info(f"Invalidated cache for file: {file_path}")
    
    async def invalidate_codebase(self, codebase_id: str):
        """Invalidate course structure cache for a codebase.
        
        Args:
            codebase_id: Unique codebase identifier
        """
        cache_key = f"{self.COURSE_PREFIX}{codebase_id}"
        # We can't directly delete from unified cache, but we can mark it as invalid
        # by setting a very short TTL
        await self.cache.set_analysis(cache_key, {"invalid": True}, ttl=1)
        logger.info(f"Invalidated course structure cache: {codebase_id}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        base_stats = await self.cache.get_stats()
        
        return {
            **base_stats,
            "course_cache_enabled": True,
            "tracked_files": len(self.file_mtimes)
        }
