# core/l0_cache.py

from cachetools import LRUCache
from threading import RLock
from typing import Any, Optional, Hashable

class L0Cache:
    """
    A thread-safe, high-performance in-process Least Recently Used (LRU) cache.
    This serves as the L0 (Hot Cache) memory layer, providing the fastest possible
    access to frequently used data within a single service instance.
    """

    def __init__(self, maxsize: int = 10000):
        """
        Initializes the L0 cache.

        Args:
            maxsize: The maximum number of items to store in the cache. Once the
                     cache exceeds this size, the least recently used items are evicted.
        """
        if maxsize <= 0:
            raise ValueError("L0Cache maxsize must be a positive integer.")
            
        self.cache: LRUCache[Hashable, Any] = LRUCache(maxsize=maxsize)
        # RLock (Re-entrant Lock) is used to make the cache operations atomic and
        # prevent race conditions in a multi-threaded environment (e.g., with Gunicorn workers).
        self.lock = RLock()

    def get(self, key: Hashable) -> Optional[Any]:
        """
        Retrieves a value from the cache by its key. This operation is thread-safe.

        Args:
            key: The key of the item to retrieve. Must be hashable.

        Returns:
            The cached value if the key exists, otherwise None.
        """
        with self.lock:
            return self.cache.get(key)

    def set(self, key: Hashable, value: Any) -> None:
        """
        Sets a value in the cache. This operation is thread-safe.

        Args:
            key: The key of the item to set. Must be hashable.
            value: The value to be stored.
        """
        with self.lock:
            self.cache[key] = value

    def clear(self) -> None:
        """Clears the entire cache. This operation is thread-safe."""
        with self.lock:
            self.cache.clear()

    def __len__(self) -> int:
        """Returns the current number of items in the cache."""
        with self.lock:
            return len(self.cache)
