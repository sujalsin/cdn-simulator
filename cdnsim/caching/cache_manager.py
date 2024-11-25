from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.max_size = 1000  # Maximum number of items in cache
        
    def get(self, key: str) -> Optional[str]:
        """Get an item from the cache."""
        return self.cache.get(key)
        
    def set(self, key: str, value: str) -> None:
        """Set an item in the cache with LRU eviction."""
        if len(self.cache) >= self.max_size:
            # Simple LRU: remove first item (oldest)
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[key] = value
        
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'usage': len(self.cache) / self.max_size * 100
        }
