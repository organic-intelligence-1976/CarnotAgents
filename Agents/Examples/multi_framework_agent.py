"""
Multi-Framework Agent Example

This module demonstrates how to create an agent that can leverage multiple LLM frameworks
together, showing how the LLMFrameworks project enables interoperability between
different frameworks like LangChain, AutoGen, and LiteLLM.

Key components:
- Framework detection and initialization
- Message passing between frameworks
- Combined agent capabilities
- Cross-framework workflow
"""

import os
import sys
from typing import Dict, List, Any, Optional, Union

# Add the parent directory to the path to import from Core
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import utility classes from Core
try:
    from Core.framework_adapter import FrameworkDetector, MessageStandardizer, ConfigurationNormalizer
except ImportError:
    print("Core modules not found. Make sure you're running from the correct directory.")
    sys.exit(1)


class MultiFrameworkAgent:
    """
    An agent that combines capabilities from multiple LLM frameworks.
    This is a conceptual demonstration of how frameworks can be used together.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the multi-framework agent.
        
        Args:
            config: Configuration dictionary for the agent
        """
        self.config = config or {}
        self.available_frameworks = FrameworkDetector.get_available_frameworks()
        
        # Framework-specific components
        self.components = {}
        
        # Initialize available frameworks
        self._initialize_frameworks()
    
    def _initialize_frameworks(self) -> None:
        """Initialize components for each available framework."""
        # Import and initialize LangChain components if available
        if "langchain" in self.available_frameworks:
            try:
                from langchain_core.prompts import ChatPromptTemplate
                from langchain_openai import ChatOpenAI
                
                # Create a basic LangChain model
                model_config = ConfigurationNormalizer.normalize_model_config(
                    self.config.get("model_config", {}), 
                    "langchain"
                )
                
                model = ChatOpenAI(**model_config)
                prompt = ChatPromptTemplate.from_template("{input}")
                chain = prompt | model
                
                self.components["langchain"] = {
                    "model": model,
                    "chain": chain
                }
                
                print("LangChain components initialized.")
            except ImportError as e:
                print(f"Error initializing LangChain: {e}")
        
        # Import and initialize AutoGen components if available
        if "autogen" in self.available_frameworks:
            try:
                from autogen import ConversableAgent
                
                # Create a basic AutoGen agent
                model_config = ConfigurationNormalizer.normalize_model_config(
                    self.config.get("model_config", {}), 
                    "autogen"
                )
                
                agent = ConversableAgent(
                    name="assistant",
                    system_message=self.config.get("system_message", "You are a helpful assistant."),
                    llm_config=model_config,
                    human_input_mode="NEVER"
                )
                
                self.components["autogen"] = {
                    "agent": agent
                }
                
                print("AutoGen components initialized.")
            except ImportError as e:
                print(f"Error initializing AutoGen: {e}")
        
        # Import and initialize LiteLLM components if available
        if "litellm" in self.available_frameworks:
            try:
                import litellm
                
                # Store the litellm module for later use
                self.components["litellm"] = {
                    "module": litellm
                }
                
                print("LiteLLM components initialized.")
            except ImportError as e:
                print(f"Error initializing LiteLLM: {e}")
    
    def process_with_langchain(self, input_text: str) -> str:
        """
        Process input using LangChain.
        
        Args:
            input_text: The input text
            
        Returns:
            The processed output
        """
        if "langchain" not in self.components:
            return "LangChain is not available."
        
        try:
            chain = self.components["langchain"]["chain"]
            response = chain.invoke({"input": input_text})
            return response.content
        except Exception as e:
            return f"Error processing with LangChain: {str(e)}"
    
    def process_with_autogen(self, input_text: str) -> str:
        """
        Process input using AutoGen.
        
        Args:
            input_text: The input text
            
        Returns:
            The processed output
        """
        if "autogen" not in self.components:
            return "AutoGen is not available."
        
        try:
            agent = self.components["autogen"]["agent"]
            response = agent.generate_reply(messages=[{"content": input_text, "role": "user"}])
            return response
        except Exception as e:
            return f"Error processing with AutoGen: {str(e)}"
    
    def process_with_litellm(self, input_text: str) -> str:
        """
        Process input using LiteLLM.
        
        Args:
            input_text: The input text
            
        Returns:
            The processed output
        """
        if "litellm" not in self.components:
            return "LiteLLM is not available."
        
        try:
            litellm = self.components["litellm"]["module"]
            model_config = ConfigurationNormalizer.normalize_model_config(
                self.config.get("model_config", {}), 
                "litellm"
            )
            
            response = litellm.completion(
                model=model_config.get("model", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": input_text}],
                max_tokens=model_config.get("max_tokens", 500)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error processing with LiteLLM: {str(e)}"
    
    def get_enhanced_response(self, input_text: str) -> Dict[str, Any]:
        """
        Get an enhanced response by combining results from multiple frameworks.
        
        Args:
            input_text: The input text
            
        Returns:
            A dictionary with responses from each framework
        """
        results = {
            "input": input_text,
            "frameworks_used": self.available_frameworks,
            "responses": {}
        }
        
        # Process with each available framework
        if "langchain" in self.available_frameworks:
            results["responses"]["langchain"] = self.process_with_langchain(input_text)
        
        if "autogen" in self.available_frameworks:
            results["responses"]["autogen"] = self.process_with_autogen(input_text)
        
        if "litellm" in self.available_frameworks:
            results["responses"]["litellm"] = self.process_with_litellm(input_text)
        
        # Add a consolidated response if multiple frameworks were used
        if len(results["responses"]) > 1:
            # This is a simple example - in a real application, you might
            # use more sophisticated methods to combine responses
            framework_responses = list(results["responses"].values())
            results["consolidated_response"] = framework_responses[0]
        elif len(results["responses"]) == 1:
            # If only one framework was used, use that response
            results["consolidated_response"] = next(iter(results["responses"].values()))
        else:
            results["consolidated_response"] = "No frameworks available to process the input."
        
        return results


# Example usage
def run_multi_framework_example():
    """Run an example using the multi-framework agent."""
    # Check if any API keys are available
    has_api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    
    if not has_api_key:
        print("Please set at least one API key environment variable to run the examples.")
        print("Example: export OPENAI_API_KEY=your_api_key_here")
        return
    
    # Create the multi-framework agent
    agent = MultiFrameworkAgent(
        config={
            "model_config": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 300
            },
            "system_message": "You are a helpful assistant that provides concise answers."
        }
    )
    
    # Process some example inputs
    example_inputs = [
        "Explain quantum computing in simple terms.",
        "What are the main differences between Python and JavaScript?",
        "Generate a short poem about artificial intelligence."
    ]
    
    for input_text in example_inputs:
        print(f"\nProcessing input: \"{input_text}\"")
        result = agent.get_enhanced_response(input_text)
        
        print("\nFrameworks used:")
        for framework in result["frameworks_used"]:
            print(f"- {framework}")
        
        print("\nConsolidated response:")
        print(result["consolidated_response"])
        
        print("\n" + "-" * 80)


if __name__ == "__main__":
    run_multi_framework_example()