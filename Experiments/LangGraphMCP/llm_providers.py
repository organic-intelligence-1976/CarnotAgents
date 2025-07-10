"""
LLM Provider Factory for Agent System

Provides easy access to different LLM providers:
- OpenAI (GPT models)
- Anthropic (Claude models)
- Google (Gemini models)
- Ollama (Local Llama models)
"""

import os
from typing import Optional, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


class LLMProviderFactory:
    """Factory for creating LLM instances from different providers"""
    
    @staticmethod
    def create_openai(
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        **kwargs
    ) -> BaseChatModel:
        """Create an OpenAI LLM instance"""
        from langchain_openai import ChatOpenAI
        
        api_key = kwargs.pop('api_key', None) or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY or pass api_key parameter")
        
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            **kwargs
        )
    
    @staticmethod
    def create_anthropic(
        model: str = "claude-3-opus-20240229",
        temperature: float = 0.7,
        **kwargs
    ) -> BaseChatModel:
        """Create an Anthropic Claude LLM instance"""
        from langchain_anthropic import ChatAnthropic
        
        api_key = kwargs.pop('api_key', None) or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY or pass api_key parameter")
        
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            anthropic_api_key=api_key,
            **kwargs
        )
    
    @staticmethod
    def create_gemini(
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        **kwargs
    ) -> BaseChatModel:
        """Create a Google Gemini LLM instance"""
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = kwargs.pop('api_key', None) or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key not found. Set GOOGLE_API_KEY or pass api_key parameter")
        
        # Available models: gemini-1.5-flash, gemini-1.5-pro, gemini-1.0-pro
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key,
            **kwargs
        )
    
    @staticmethod
    def create_ollama(
        model: str = "llama2",
        temperature: float = 0.7,
        base_url: str = "http://localhost:11434",
        **kwargs
    ) -> BaseChatModel:
        """Create an Ollama (local) LLM instance"""
        from langchain_community.chat_models import ChatOllama
        
        return ChatOllama(
            model=model,
            temperature=temperature,
            base_url=base_url,
            **kwargs
        )
    
    @classmethod
    def create(
        cls,
        provider: str,
        model: Optional[str] = None,
        **kwargs
    ) -> BaseChatModel:
        """
        Create an LLM instance from any supported provider
        
        Args:
            provider: One of 'openai', 'anthropic', 'gemini', 'ollama'
            model: Model name (uses sensible defaults if not provided)
            **kwargs: Additional parameters for the specific provider
            
        Returns:
            A LangChain chat model instance
        """
        provider_lower = provider.lower()
        
        # Default models for each provider
        default_models = {
            'openai': 'gpt-4-turbo-preview',
            'anthropic': 'claude-3-opus-20240229',
            'gemini': 'gemini-1.5-flash',
            'ollama': 'llama2'
        }
        
        if model is None:
            model = default_models.get(provider_lower)
        
        if provider_lower == 'openai':
            return cls.create_openai(model=model, **kwargs)
        elif provider_lower == 'anthropic':
            return cls.create_anthropic(model=model, **kwargs)
        elif provider_lower == 'gemini':
            return cls.create_gemini(model=model, **kwargs)
        elif provider_lower == 'ollama':
            return cls.create_ollama(model=model, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: openai, anthropic, gemini, ollama")


# Convenience functions for quick LLM creation
def create_llm(provider: str = "openai", **kwargs) -> BaseChatModel:
    """Quick function to create an LLM"""
    return LLMProviderFactory.create(provider, **kwargs)


# Model recommendations for different use cases
RECOMMENDED_MODELS = {
    'fast': {
        'openai': 'gpt-3.5-turbo',
        'anthropic': 'claude-3-haiku-20240307',
        'gemini': 'gemini-1.5-flash',
        'ollama': 'llama2:7b'
    },
    'balanced': {
        'openai': 'gpt-4-turbo-preview',
        'anthropic': 'claude-3-sonnet-20240229',
        'gemini': 'gemini-1.5-pro',
        'ollama': 'llama2:13b'
    },
    'powerful': {
        'openai': 'gpt-4',
        'anthropic': 'claude-3-opus-20240229',
        'gemini': 'gemini-1.5-pro',  # Most powerful available
        'ollama': 'llama2:70b'
    }
}


def create_llm_for_use_case(
    use_case: str = "balanced",
    provider: str = "openai",
    **kwargs
) -> BaseChatModel:
    """
    Create an LLM optimized for a specific use case
    
    Args:
        use_case: One of 'fast', 'balanced', 'powerful'
        provider: LLM provider to use
        **kwargs: Additional parameters
        
    Returns:
        LLM instance optimized for the use case
    """
    if use_case not in RECOMMENDED_MODELS:
        raise ValueError(f"Unknown use case: {use_case}. Choose from: fast, balanced, powerful")
    
    model = RECOMMENDED_MODELS[use_case].get(provider)
    if not model:
        raise ValueError(f"No recommendation for provider {provider} with use case {use_case}")
    
    return create_llm(provider=provider, model=model, **kwargs)