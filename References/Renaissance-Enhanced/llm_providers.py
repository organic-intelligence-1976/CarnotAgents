import os
from typing import Callable, Dict, Any, Optional, Union
from .config import DEFAULT_SYSTEM_PROMPT, DEFAULT_LLM_SETTINGS


class Response:
    """Standardized response object for all LLM providers."""
    def __init__(self, content: str):
        self.content = content


class LLMProvider:
    """Base class for all LLM providers."""
    
    def invoke(self, prompt: str) -> Response:
        """
        Invoke the LLM with a prompt.
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            Response: A standardized Response object
        """
        raise NotImplementedError("Subclasses must implement invoke method")


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider (GPT models)."""
    
    def __init__(self, model: str = None, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            model (str, optional): Model name to use (defaults to config setting)
            api_key (str, optional): API key (defaults to os.environ["OPENAI_API_KEY"])
        """
        try:
            import openai
        except ImportError:
            raise ImportError("OpenAI package not installed. Run 'pip install openai'")
        
        # Use model from args, or from config, or fallback to default
        self.model = model or DEFAULT_LLM_SETTINGS["openai"]["model"]
        self.client = openai.OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        
    def invoke(self, prompt: str) -> Response:
        """
        Invoke the OpenAI model with a prompt.
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            Response: A standardized Response object
        """        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        return Response(completion.choices[0].message.content)


class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider (Claude models)."""
    
    def __init__(self, model: str = None, api_key: Optional[str] = None, max_tokens: int = None):
        """
        Initialize Anthropic provider.
        
        Args:
            model (str, optional): Model name to use (defaults to config setting)
            api_key (str, optional): API key (defaults to os.environ["ANTHROPIC_API_KEY"])
            max_tokens (int, optional): Maximum tokens to generate
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError("Anthropic package not installed. Run 'pip install anthropic'")
            
        # Use config values with appropriate fallbacks
        config = DEFAULT_LLM_SETTINGS["anthropic"]
        self.model = model or config["model"]
        self.max_tokens = max_tokens or config.get("max_tokens", 4096)
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        
    def invoke(self, prompt: str) -> Response:
        """
        Invoke the Anthropic model with a prompt.
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            Response: A standardized Response object
        """        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=DEFAULT_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return Response(message.content[0].text)


class GoogleProvider(LLMProvider):
    """Google LLM provider (Gemini models)."""
    
    def __init__(self, model: str = None, api_key: Optional[str] = None):
        """
        Initialize Google provider.
        
        Args:
            model (str, optional): Model name to use (defaults to config setting)
            api_key (str, optional): API key (defaults to os.environ["GOOGLE_API_KEY"])
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Google Generative AI package not installed. Run 'pip install google-generativeai'")
            
        # Use model from args, or from config, or fallback to default
        self.model = model or DEFAULT_LLM_SETTINGS["google"]["model"]
        genai.configure(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
        self.client = genai.GenerativeModel(model_name=self.model)
        
    def invoke(self, prompt: str) -> Response:
        """
        Invoke the Google model with a prompt.
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            Response: A standardized Response object
        """
        # For Google provider, we prepend the system prompt as it doesn't have a separate system message
        full_prompt = f"{DEFAULT_SYSTEM_PROMPT}\n\n{prompt}"
        response = self.client.generate_content(full_prompt)
        return Response(response.text)


class MLXProvider(LLMProvider):
    """MLX LLM provider for locally running models."""
    
    def __init__(self, model_path: str):
        """
        Initialize MLX provider.
        
        Args:
            model_path (str): Path to the model directory
        """
        try:
            import mlx.core as mx
            from mlx_lm import load, generate
        except ImportError:
            raise ImportError("MLX packages not installed. Run 'pip install mlx mlx-lm'")
            
        self.model_path = model_path
        self.model, self.tokenizer = load(model_path)
        
    def invoke(self, prompt: str) -> Response:
        """
        Invoke the local MLX model with a prompt.
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            Response: A standardized Response object
        """
        from mlx_lm import generate
        
        # For MLX models, we prepend the system prompt as it doesn't support system messages
        full_prompt = f"{DEFAULT_SYSTEM_PROMPT}\n\n{prompt}"
        
        # Get max_tokens from config if available, otherwise use default
        max_tokens = DEFAULT_LLM_SETTINGS.get("mlx", {}).get("max_tokens", 1024)
        response = generate(self.model, self.tokenizer, prompt=full_prompt, max_tokens=max_tokens)
        return Response(response)


class MockProvider(LLMProvider):
    """Mock LLM provider for testing purposes."""
    
    def __init__(self, response_mapping=None):
        """
        Initialize with optional mapping of inputs to responses.
        
        Args:
            response_mapping (dict, optional): Mapping of input patterns to responses
        """
        self.response_mapping = response_mapping or {}
        # Default mock response for testing
        self.default_response = """
        I'll analyze the data first to understand what we're working with.
        
        <new_section name="Plan">
        1. Create a sample dataset
        2. Perform basic statistical analysis
        3. Visualize the data distribution
        4. Draw initial conclusions
        </new_section>
        
        <execute>
        import pandas as pd
        import numpy as np
        
        # Create a sample dataframe
        df = pd.DataFrame({
            'A': np.random.randn(5),
            'B': np.random.randn(5)
        })
        
        print(df.describe())
        </execute>
        """
        
    def invoke(self, prompt: str) -> Response:
        """
        Invoke the mock LLM with a prompt.
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            Response: A Response object containing the content
        """
        # Check if any key in response_mapping is contained in the prompt
        for key, response in self.response_mapping.items():
            if key in prompt:
                return Response(response)
        
        # Return default response if no match
        return Response(self.default_response)


def get_llm_provider(provider_name: str, **kwargs) -> LLMProvider:
    """
    Factory function to get an LLM provider by name.
    
    Args:
        provider_name (str): Name of the provider (openai, anthropic, google, mlx, mock)
        **kwargs: Additional arguments to pass to the provider constructor
        
    Returns:
        LLMProvider: An instance of the requested LLM provider
        
    Raises:
        ValueError: If the provider name is not recognized
    """
    providers = {
        "openai": OpenAIProvider,
        "gpt": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "claude": AnthropicProvider,
        "google": GoogleProvider,
        "gemini": GoogleProvider,
        "mlx": MLXProvider,
        "mock": MockProvider
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}. Available providers: {', '.join(providers.keys())}")
    
    return provider_class(**kwargs)