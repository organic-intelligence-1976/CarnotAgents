"""Context pool implementation for Cursor-LangGraph."""

class ContextPool:
    """Manages shared context between agents."""
    
    def __init__(self):
        self._context = {}
    
    def add(self, key: str, value: any):
        """Add or update a context value."""
        self._context[key] = value
    
    def get(self, key: str) -> any:
        """Retrieve a context value."""
        return self._context.get(key)
    
    def remove(self, key: str):
        """Remove a context value."""
        if key in self._context:
            del self._context[key] 