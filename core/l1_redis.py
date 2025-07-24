# core/l1_redis.py

import redis.asyncio as redis
from typing import Optional, Any
import logging

from .exceptions import MemoryLayerError

class L1Redis:
    """
    An asynchronous, connection-pooled Redis client for the L1 (Warm Cache)
    distributed cache layer. It is designed for high throughput and resilience.
    """

    def __init__(self, url: str):
        """
        Initializes the L1 Redis client configuration.
        """
        self.url = url
        self.pool: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """
        Establishes and verifies the connection pool to the Redis server.
        """
        try:
            logging.info(f"Connecting to L1 Redis at {self.url}...")
            self.pool = redis.from_url(self.url, decode_responses=True)
            await self.pool.ping()
            logging.info("L1 Redis connection established and verified successfully.")
        except Exception as e:
            raise MemoryLayerError(layer="L1-Redis", message=f"Failed to connect: {e}")

    async def get(self, key: str) -> Optional[str]:
        """
        Asynchronously gets a value from Redis by key.
        """
        if self.pool is None:
            raise MemoryLayerError(layer="L1-Redis", message="Connection not initialized. Call connect() first.")
        try:
            return await self.pool.get(key)
        except Exception as e:
            raise MemoryLayerError(layer="L1-Redis", message=f"GET operation failed for key '{key}': {e}")

    async def set(self, key: str, value: Any, expire: Optional[int] = 3600) -> None:
        """
        Asynchronously sets a value in Redis by key, with an optional expiration.
        """
        if self.pool is None:
            raise MemoryLayerError(layer="L1-Redis", message="Connection not initialized. Call connect() first.")
        try:
            await self.pool.set(key, str(value), ex=expire)
        except Exception as e:
            raise MemoryLayerError(layer="L1-Redis", message=f"SET operation failed for key '{key}': {e}")

    async def close(self) -> None:
        """Gracefully closes the Redis connection pool."""
        if self.pool is not None:
            logging.info("Closing L1 Redis connection pool...")
            try:
                await self.pool.close()
                self.pool = None
                logging.info("L1 Redis connection pool closed.")
            except Exception as e:
                logging.error(f"Error while closing Redis connection pool: {e}")
