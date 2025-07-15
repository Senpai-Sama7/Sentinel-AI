# api/dependencies.py

from core.manager import MemoryManager

# Lazily create a single shared MemoryManager instance.  This avoids
# initializing external services during module import which can cause issues
# in test environments.
memory_manager: MemoryManager | None = None

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
