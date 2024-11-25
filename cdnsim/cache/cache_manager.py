import redis
from typing import Optional, Dict, List
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }

    def get(self, key: str) -> Optional[Dict]:
        """Retrieve item from cache."""
        try:
            data = self.redis_client.get(key)
            if data:
                self.cache_stats['hits'] += 1
                return json.loads(data)
            self.cache_stats['misses'] += 1
            return None
        except redis.RedisError as e:
            logger.error(f"Redis error in get operation: {e}")
            return None

    def set(self, key: str, value: Dict, ttl: int = 3600):
        """Store item in cache with TTL."""
        try:
            serialized_value = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized_value)
            logger.debug(f"Cached {key} with TTL {ttl}s")
        except redis.RedisError as e:
            logger.error(f"Redis error in set operation: {e}")

    def invalidate(self, key: str):
        """Remove item from cache."""
        try:
            self.redis_client.delete(key)
            self.cache_stats['evictions'] += 1
            logger.debug(f"Invalidated cache key: {key}")
        except redis.RedisError as e:
            logger.error(f"Redis error in invalidate operation: {e}")

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        try:
            info = self.redis_client.info()
            return {
                **self.cache_stats,
                'memory_used': info.get('used_memory_human', 'N/A'),
                'total_keys': self.redis_client.dbsize(),
                'hit_rate': self._calculate_hit_rate()
            }
        except redis.RedisError as e:
            logger.error(f"Redis error in get_stats operation: {e}")
            return self.cache_stats

    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        if total == 0:
            return 0.0
        return self.cache_stats['hits'] / total

    def clear_expired(self):
        """Clear expired cache entries."""
        try:
            # Note: Redis automatically handles expiration
            # This method is mainly for statistics tracking
            logger.info("Redis automatically handles cache expiration")
        except redis.RedisError as e:
            logger.error(f"Redis error in clear_expired operation: {e}")

    def get_keys_by_pattern(self, pattern: str) -> List[str]:
        """Get all keys matching the given pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            return [key.decode('utf-8') for key in keys]
        except redis.RedisError as e:
            logger.error(f"Redis error in get_keys_by_pattern operation: {e}")
            return []

    def set_cache_policy(self, max_memory_mb: int, eviction_policy: str = 'allkeys-lru'):
        """Configure Redis cache policies."""
        try:
            self.redis_client.config_set('maxmemory', f'{max_memory_mb}mb')
            self.redis_client.config_set('maxmemory-policy', eviction_policy)
            logger.info(f"Set cache policy: max_memory={max_memory_mb}MB, policy={eviction_policy}")
        except redis.RedisError as e:
            logger.error(f"Redis error in set_cache_policy operation: {e}")

    def health_check(self) -> Dict:
        """Check cache system health."""
        try:
            self.redis_client.ping()
            info = self.redis_client.info()
            return {
                'status': 'healthy',
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', 'N/A'),
                'uptime_seconds': info.get('uptime_in_seconds', 0)
            }
        except redis.RedisError as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
