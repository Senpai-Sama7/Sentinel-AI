# api/dependencies.py

from core.manager import MemoryManager
from typing import Optional

# Lazily instantiate the MemoryManager to avoid unnecessary connections during
# import time (e.g., when running tests).
memory_manager: Optional[MemoryManager] = None

async def get_memory_manager() -> MemoryManager:
    """
    A FastAPI dependency provider function.
    
    When an endpoint declares `manager: MemoryManager = Depends(get_memory_manager)`,
    FastAPI will call this function and inject the returned `memory_manager` instance
    into the endpoint's arguments. This makes testing trivial by allowing us to
    override this dependency with a mock manager.
    """
    global memory_manager
    if memory_manager is None:
        memory_manager = MemoryManager()
    return memory_manager
