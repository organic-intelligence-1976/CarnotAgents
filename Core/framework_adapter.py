"""
Framework Adapter Base Module

This module provides the foundation for adapter classes that create a unified interface
across different LLM frameworks. It defines base classes and common utilities for
standardizing interactions with frameworks like LangChain, AutoGen, LiteLLM, and LlamaIndex.

Key components:
- Base adapter class for all frameworks
- Message standardization
- Configuration normalization
- Framework detection utilities
"""

import os
import importlib
from typing import Dict, List, Any, Optional, Union, Callable
from abc import ABC, abstractmethod


class BaseFrameworkAdapter(ABC):
    """Base class for all framework adapters."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the framework adapter.
        
        Args:
            config: Configuration dictionary for the adapter
        """
        self.config = config or {}
        self._initialize_adapter()
    
    @abstractmethod
    def _initialize_adapter(self) -> None:
        """Initialize the specific adapter. Implemented by subclasses."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the framework is available (installed and configured).
        
        Returns:
            True if the framework is available, False otherwise
        """
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a response using the framework.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional framework-specific parameters
            
        Returns:
            A dictionary containing the response and metadata
        """
        pass


class MessageStandardizer:
    """Utility class for standardizing message formats across frameworks."""
    
    @staticmethod
    def to_standard_format(
        messages: Union[str, List[Dict[str, str]], Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Convert various message formats to a standardized format.
        
        Args:
            messages: Input messages in various formats
            
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        # Handle string input
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        
        # Handle list of dictionaries
        if isinstance(messages, list):
            # Ensure each dictionary has 'role' and 'content' keys
            standardized = []
            for msg in messages:
                if not isinstance(msg, dict):
                    raise ValueError(f"Expected dictionary, got {type(msg)}")
                
                # Ensure required keys
                if "role" not in msg:
                    msg["role"] = "user"
                if "content" not in msg:
                    raise ValueError("Message missing 'content' field")
                
                standardized.append({"role": msg["role"], "content": msg["content"]})
            return standardized
        
        # Handle dictionary with content
        if isinstance(messages, dict) and "content" in messages:
            role = messages.get("role", "user")
            return [{"role": role, "content": messages["content"]}]
        
        raise ValueError(f"Unsupported message format: {type(messages)}")
    
    @staticmethod
    def from_standard_format(
        messages: List[Dict[str, str]], 
        target_format: str
    ) -> Any:
        """
        Convert from standardized format to framework-specific format.
        
        Args:
            messages: Standardized message list
            target_format: Target framework format ('langchain', 'autogen', etc.)
            
        Returns:
            Messages in the target framework's format
        """
        if target_format.lower() == "langchain":
            try:
                from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
                
                converted = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    
                    if role == "user":
                        converted.append(HumanMessage(content=content))
                    elif role == "assistant":
                        converted.append(AIMessage(content=content))
                    elif role == "system":
                        converted.append(SystemMessage(content=content))
                    else:
                        # Default to HumanMessage for unknown roles
                        converted.append(HumanMessage(content=content))
                
                return converted
            except ImportError:
                raise ImportError("LangChain not installed. Cannot convert to LangChain format.")
        
        elif target_format.lower() == "autogen":
            # AutoGen typically uses dictionaries with role and content
            return messages
        
        elif target_format.lower() == "litellm":
            # LiteLLM uses the same format as the OpenAI API
            return messages
        
        elif target_format.lower() == "llamaindex":
            try:
                from llama_index.core.llms import ChatMessage
                from llama_index.core.llms import MessageRole
                
                converted = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    
                    if role == "user":
                        role_enum = MessageRole.USER
                    elif role == "assistant":
                        role_enum = MessageRole.ASSISTANT
                    elif role == "system":
                        role_enum = MessageRole.SYSTEM
                    else:
                        role_enum = MessageRole.USER
                    
                    converted.append(ChatMessage(role=role_enum, content=content))
                
                return converted
            except ImportError:
                raise ImportError("LlamaIndex not installed. Cannot convert to LlamaIndex format.")
        
        else:
            raise ValueError(f"Unsupported target format: {target_format}")


class FrameworkDetector:
    """Utility class for detecting available frameworks."""
    
    @staticmethod
    def is_langchain_available() -> bool:
        """Check if LangChain is installed."""
        try:
            import langchain
            return True
        except ImportError:
            return False
    
    @staticmethod
    def is_autogen_available() -> bool:
        """Check if AutoGen is installed."""
        try:
            import autogen
            return True
        except ImportError:
            return False
    
    @staticmethod
    def is_litellm_available() -> bool:
        """Check if LiteLLM is installed."""
        try:
            import litellm
            return True
        except ImportError:
            return False
    
    @staticmethod
    def is_llamaindex_available() -> bool:
        """Check if LlamaIndex is installed."""
        try:
            import llama_index
            return True
        except ImportError:
            return False
    
    @classmethod
    def get_available_frameworks(cls) -> List[str]:
        """
        Get a list of all available frameworks.
        
        Returns:
            List of available framework names
        """
        frameworks = []
        
        if cls.is_langchain_available():
            frameworks.append("langchain")
        
        if cls.is_autogen_available():
            frameworks.append("autogen")
        
        if cls.is_litellm_available():
            frameworks.append("litellm")
        
        if cls.is_llamaindex_available():
            frameworks.append("llamaindex")
        
        return frameworks


class ConfigurationNormalizer:
    """Utility class for normalizing configurations across frameworks."""
    
    @staticmethod
    def normalize_model_config(
        config: Dict[str, Any], 
        target_framework: str
    ) -> Dict[str, Any]:
        """
        Normalize model configuration for a specific framework.
        
        Args:
            config: Input configuration dictionary
            target_framework: Target framework name
            
        Returns:
            Normalized configuration dictionary for the target framework
        """
        # Extract common parameters
        model_name = config.get("model", config.get("model_name", "gpt-3.5-turbo"))
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", config.get("max_new_tokens", 500))
        
        # Framework-specific normalization
        if target_framework.lower() == "langchain":
            return {
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        
        elif target_framework.lower() == "autogen":
            return {
                "config_list": [
                    {
                        "model": model_name,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "api_key": os.environ.get("OPENAI_API_KEY")
                    }
                ]
            }
        
        elif target_framework.lower() == "litellm":
            return {
                "model": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        
        elif target_framework.lower() == "llamaindex":
            return {
                "model": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        
        else:
            # Return as-is for unknown frameworks
            return config


# Factory function for creating framework adapters
def create_adapter(framework_name: str, config: Optional[Dict[str, Any]] = None) -> BaseFrameworkAdapter:
    """
    Create an appropriate adapter for the specified framework.
    
    Args:
        framework_name: Name of the framework ('langchain', 'autogen', etc.)
        config: Configuration dictionary for the adapter
        
    Returns:
        An instance of the appropriate adapter class
        
    Raises:
        ImportError: If the framework or its adapter is not available
        ValueError: If the framework is not supported
    """
    # This function would dynamically import and instantiate the appropriate adapter
    # based on the framework name. The actual implementation would need to be
    # expanded once the specific adapter classes are defined.
    
    framework_name = framework_name.lower()
    
    # Check if the framework is available
    if framework_name == "langchain" and not FrameworkDetector.is_langchain_available():
        raise ImportError("LangChain is not installed. Please install it first.")
    elif framework_name == "autogen" and not FrameworkDetector.is_autogen_available():
        raise ImportError("AutoGen is not installed. Please install it first.")
    elif framework_name == "litellm" and not FrameworkDetector.is_litellm_available():
        raise ImportError("LiteLLM is not installed. Please install it first.")
    elif framework_name == "llamaindex" and not FrameworkDetector.is_llamaindex_available():
        raise ImportError("LlamaIndex is not installed. Please install it first.")
    
    # This would be expanded to import and return the actual adapter classes
    # For now, return a placeholder message
    raise NotImplementedError(f"Adapter for {framework_name} is not yet implemented.")