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

        Args:
            url: The connection URL for the Redis server (e.g., "redis://localhost:6379/0").
        """
        self.url = url
        self.pool: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """
        Establishes and verifies the connection pool to the Redis server.
        This should be called during application startup.
        
        Raises:
            MemoryLayerError: If the connection to Redis fails.
        """
        try:
            logging.info(f"Connecting to L1 Redis at {self.url}...")
            # from_url automatically creates a connection pool for efficient reuse of connections.
            self.pool = await redis.from_url(self.url, decode_responses=True)
            # PING is a lightweight command to verify the connection is alive and authenticated.
            await self.pool.ping()
            logging.info("L1 Redis connection established and verified successfully.")
        except Exception as e:
            # Wrap the low-level redis exception in our custom error type for consistent handling.
            raise MemoryLayerError(layer="L1-Redis", message=f"Failed to connect: {e}")

    async def get(self, key: str) -> Optional[str]:
        """
        Asynchronously gets a value from Redis by key.

        Args:
            key: The key of the item to retrieve.

        Returns:
            The value as a string if the key exists, otherwise None.
        
        Raises:
            MemoryLayerError: If the Redis operation fails.
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

        Args:
            key: The key of the item to set.
            value: The value to store. It will be coerced to a string.
            expire: The time-to-live for the key in seconds. Defaults to 1 hour.
        
        Raises:
            MemoryLayerError: If the Redis operation fails.
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
                # Log the error but don't raise, as shutdown should not fail.
                logging.error(f"Error while closing Redis connection pool: {e}")
