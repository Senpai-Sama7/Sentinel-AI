# api/dependencies.py

from core.manager import MemoryManager

# This creates a single, shared instance of the MemoryManager that will be
# used throughout the application's lifecycle. The startup and shutdown logic
# in main.py will manage its connections.
memory_manager = MemoryManager()

async def get_memory_manager() -> MemoryManager:
    """
    A FastAPI dependency provider function.
    
    When an endpoint declares `manager: MemoryManager = Depends(get_memory_manager)`,
    FastAPI will call this function and inject the returned `memory_manager` instance
    into the endpoint's arguments. This makes testing trivial by allowing us to
    override this dependency with a mock manager.
    """
    return memory_manager
