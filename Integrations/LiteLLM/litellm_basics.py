"""
LiteLLM Basic Integration Examples

This module demonstrates fundamental integration patterns with the LiteLLM library,
showing provider-agnostic model access, fallbacks, and routing.

Key components:
- Provider-agnostic model access
- Fallback handling
- Model routing and selection
- Cost tracking

This implementation demonstrates the core patterns of LiteLLM usage.
"""

import os
from typing import Dict, List, Any, Optional

# Import LiteLLM components
try:
    import litellm
    from litellm import completion
except ImportError:
    print("LiteLLM is not installed. Please install it using: pip install litellm")
    print("For more information, visit: https://github.com/BerriAI/litellm")


class LiteLLMIntegration:
    """A wrapper class for LiteLLM integration patterns."""
    
    def __init__(self, 
                openai_api_key: Optional[str] = None,
                anthropic_api_key: Optional[str] = None):
        """
        Initialize the LiteLLM integration with optional API keys.
        
        Args:
            openai_api_key: The OpenAI API key
            anthropic_api_key: The Anthropic API key
        """
        # Set API keys if provided, otherwise rely on environment variables
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        if anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
        
        # Configure LiteLLM
        litellm.drop_params = True  # Drop unsupported params instead of raising exceptions
        litellm.set_verbose = False  # Set to True for detailed logging
    
    def generate_text(self, 
                     prompt: str, 
                     model: str = "gpt-3.5-turbo",
                     max_tokens: int = 500) -> str:
        """
        Generate text using the specified model.
        
        Args:
            prompt: The input prompt
            model: The model to use
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated text
        """
        try:
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating text: {str(e)}"
    
    def generate_with_fallbacks(self, 
                              prompt: str, 
                              models: List[str] = ["gpt-4", "gpt-3.5-turbo", "claude-instant-1"],
                              max_tokens: int = 500) -> Dict[str, Any]:
        """
        Generate text with automatic fallbacks if primary models fail.
        
        Args:
            prompt: The input prompt
            models: List of models to try in order of preference
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dictionary with response and metadata
        """
        result = {
            "success": False,
            "model_used": None,
            "content": None,
            "error": None
        }
        
        for model in models:
            try:
                response = completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                result["success"] = True
                result["model_used"] = model
                result["content"] = response.choices[0].message.content
                # Add cost tracking if available
                if hasattr(response, "usage") and response.usage:
                    result["usage"] = response.usage
                break
            except Exception as e:
                # Continue to the next model if this one fails
                continue
        
        if not result["success"]:
            result["error"] = "All models failed to generate a response"
        
        return result
    
    def setup_model_routing(self, routing_config: Dict[str, Any]) -> None:
        """
        Setup model routing based on the provided configuration.
        
        Args:
            routing_config: Configuration for model routing
            
        Example config:
        {
            "default_model": "gpt-3.5-turbo",
            "routing": [
                {"when": "token_count > 4000", "use": "claude-2"},
                {"when": "contains_code", "use": "gpt-4"}
            ],
            "contains_code_keywords": ["function", "class", "def", "```"]
        }
        """
        # This is a simplified version of what LiteLLM's router might do
        self.routing_config = routing_config
    
    def route_request(self, prompt: str, token_count: Optional[int] = None) -> str:
        """
        Route a request to the appropriate model based on routing configuration.
        
        Args:
            prompt: The input prompt
            token_count: Optional token count for routing decisions
            
        Returns:
            The selected model name
        """
        if not hasattr(self, "routing_config"):
            return "gpt-3.5-turbo"  # Default model if no routing is set up
        
        # Get default model from config
        selected_model = self.routing_config.get("default_model", "gpt-3.5-turbo")
        
        # Apply routing rules
        for rule in self.routing_config.get("routing", []):
            condition = rule.get("when", "")
            target_model = rule.get("use", selected_model)
            
            # Handle token count condition
            if "token_count >" in condition and token_count:
                threshold = int(condition.split(">")[1].strip())
                if token_count > threshold:
                    selected_model = target_model
                    break
            
            # Handle content-based conditions
            if "contains_code" in condition:
                code_keywords = self.routing_config.get("contains_code_keywords", [])
                if any(keyword in prompt for keyword in code_keywords):
                    selected_model = target_model
                    break
        
        return selected_model


# Example usage
def example_basic_generation():
    """Run a basic text generation example."""
    integration = LiteLLMIntegration()
    
    # Generate text with default model
    response = integration.generate_text(
        prompt="Explain quantum computing in simple terms.",
        model="gpt-3.5-turbo",
        max_tokens=150
    )
    
    print(f"Response: {response}")
    return response


def example_fallback_generation():
    """Run an example with model fallbacks."""
    integration = LiteLLMIntegration()
    
    # Generate with fallbacks
    result = integration.generate_with_fallbacks(
        prompt="Write a short poem about artificial intelligence.",
        models=["gpt-4", "gpt-3.5-turbo", "claude-instant-1"],
        max_tokens=100
    )
    
    print(f"Model used: {result['model_used']}")
    print(f"Response: {result['content']}")
    return result


def example_model_routing():
    """Run an example of model routing based on content."""
    integration = LiteLLMIntegration()
    
    # Set up routing
    integration.setup_model_routing({
        "default_model": "gpt-3.5-turbo",
        "routing": [
            {"when": "token_count > 4000", "use": "claude-2"},
            {"when": "contains_code", "use": "gpt-4"}
        ],
        "contains_code_keywords": ["function", "class", "def", "```"]
    })
    
    # Test routing with different prompts
    prompts = [
        "Tell me about the weather today.",
        "Write a function in Python to calculate the Fibonacci sequence.",
        "Explain the theory of relativity."
    ]
    
    for prompt in prompts:
        model = integration.route_request(prompt)
        print(f"Prompt: {prompt[:30]}...")
        print(f"Routed to model: {model}\n")


if __name__ == "__main__":
    # Check if API keys are available
    has_api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    
    if has_api_key:
        print("Running LiteLLM basic generation example...")
        example_basic_generation()
        
        print("\nRunning LiteLLM fallback generation example...")
        example_fallback_generation()
        
        print("\nRunning LiteLLM model routing example...")
        example_model_routing()
    else:
        print("Please set at least one API key environment variable to run the examples.")
        print("Example: export OPENAI_API_KEY=your_api_key_here")