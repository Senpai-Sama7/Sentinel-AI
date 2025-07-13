# core/exceptions.py

class MemoryLayerError(Exception):
    """
    Base exception for all memory layer failures.
    
    This custom exception allows for centralized error handling and provides
    clear context about which part of the system failed.
    """
    def __init__(self, layer: str, message: str):
        """
        Args:
            layer: The name of the layer that failed (e.g., "L1-Redis", "L3-Git").
            message: A description of the error.
        """
        self.layer = layer
        self.message = message
        super().__init__(f"[{self.layer}] {self.message}")

class NotFoundError(Exception):
    """
    A specific exception raised when a requested key or resource is not found
    in any of the configured memory layers after a full fallback search.
    """
    pass
