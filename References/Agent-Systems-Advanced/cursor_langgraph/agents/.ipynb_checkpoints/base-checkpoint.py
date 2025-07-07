"""Base agent implementation for Cursor-LangGraph."""

class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(self, context_pool=None):
        self.context_pool = context_pool
    
    def process_message(self, message: str) -> str:
        """Process an incoming message and return a response."""
        return f"Received message: {message}" 