"""
AutoGen Basic Integration Examples

This module demonstrates fundamental integration patterns with the AutoGen framework,
showing basic agent creation, configuration, and interaction.

Key components:
- ConversableAgent configuration and creation
- Basic agent-to-agent interaction
- Termination conditions
- Human-in-the-loop integration

This implementation is based on the examples from the original AutoGen test notebook.
"""

import os
from typing import Dict, List, Any, Optional

# Import AutoGen components
try:
    from autogen import ConversableAgent
except ImportError:
    print("AutoGen is not installed. Please install it using: pip install pyautogen")
    print("For more information, visit: https://github.com/microsoft/autogen")


class AutoGenIntegration:
    """A wrapper class for AutoGen integration patterns."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the AutoGen integration with optional API key.
        
        Args:
            openai_api_key: The OpenAI API key. If None, will try to use the environment variable.
        """
        # Set API key if provided, otherwise rely on environment variable
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Validate API key
        if not os.environ.get("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY not found in environment variables.")
    
    def create_basic_agent(self, name: str, system_message: str = "") -> ConversableAgent:
        """
        Create a basic conversable agent with default configuration.
        
        Args:
            name: The agent's name
            system_message: Optional system message for the agent
            
        Returns:
            The created ConversableAgent
        """
        return ConversableAgent(
            name=name,
            system_message=system_message,
            llm_config={
                "config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]
            },
            human_input_mode="NEVER",  # Never ask for human input by default
        )
    
    def create_human_proxy(self) -> ConversableAgent:
        """
        Create a human proxy agent that will ask for human input.
        
        Returns:
            The created human proxy ConversableAgent
        """
        return ConversableAgent(
            name="human_proxy",
            llm_config=False,  # No LLM used for human proxy
            human_input_mode="ALWAYS",  # Always ask for human input
        )
    
    def create_termination_agent(self, 
                               name: str, 
                               system_message: str,
                               termination_condition: callable) -> ConversableAgent:
        """
        Create an agent with a custom termination condition.
        
        Args:
            name: The agent's name
            system_message: System message for the agent
            termination_condition: A function that takes a message dict and returns True if conversation should end
            
        Returns:
            The created ConversableAgent with termination condition
        """
        return ConversableAgent(
            name=name,
            system_message=system_message,
            llm_config={
                "config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]
            },
            is_termination_msg=termination_condition,  # Custom termination condition
            human_input_mode="NEVER",
        )


# Example usage
def example_basic_conversation():
    """Run a basic example of two agents having a conversation."""
    integration = AutoGenIntegration()
    
    # Create two comedian agents
    louis = integration.create_basic_agent(
        "Louis",
        system_message="Your name is Louis CK and you are a comedian. Your conversations are often self-deprecating and observational."
    )
    
    ricky = integration.create_basic_agent(
        "Ricky",
        system_message="Your name is Ricky Gervais and you are a comedian. Your conversations often include dry wit and sarcasm."
    )
    
    # Start a conversation
    result = ricky.initiate_chat(louis, message="Louis, how is it going?", max_turns=3)
    return result


def example_number_guessing_game():
    """Run an example of a number guessing game with termination condition."""
    integration = AutoGenIntegration()
    
    # Create an agent with a number in mind
    agent_with_number = integration.create_termination_agent(
        "agent_with_number",
        system_message="You are playing a game of guess-my-number. You have the "
        "number 42 in your mind, and I will try to guess it. "
        "If I guess too high, say 'too high', if I guess too low, say 'too low'. ",
        termination_condition=lambda msg: "42" in msg["content"],  # Terminate when number is guessed
    )
    
    # Create an agent that will guess the number
    agent_guess_number = integration.create_basic_agent(
        "agent_guess_number",
        system_message="I have a number in my mind, and you will try to guess it. "
        "If I say 'too high', you should guess a lower number. If I say 'too low', "
        "you should guess a higher number. "
    )
    
    # Start the guessing game
    result = agent_with_number.initiate_chat(
        agent_guess_number,
        message="I have a number between 1 and 100. Guess it!",
    )
    return result


def example_human_in_the_loop():
    """Run an example with a human proxy agent."""
    integration = AutoGenIntegration()
    
    # Create an agent with a number
    agent_with_number = integration.create_termination_agent(
        "agent_with_number",
        system_message="You are playing a game of guess-my-number. You have the "
        "number 73 in your mind, and I will try to guess it. "
        "If I guess too high, say 'too high', if I guess too low, say 'too low'. ",
        termination_condition=lambda msg: "73" in msg["content"],  # Terminate when number is guessed
    )
    
    # Create a human proxy
    human_proxy = integration.create_human_proxy()
    
    # Start a chat with human input
    print("Human Proxy: Enter numbers to guess. The agent is thinking of 73.")
    result = human_proxy.initiate_chat(
        agent_with_number,
        message="50",  # Initial guess
    )
    return result


if __name__ == "__main__":
    # Check if OpenAI API key is available
    if os.environ.get("OPENAI_API_KEY"):
        print("Running AutoGen basic conversation example...")
        example_basic_conversation()
        
        print("\nRunning AutoGen number guessing game example...")
        example_number_guessing_game()
        
        print("\nRunning AutoGen human-in-the-loop example...")
        example_human_in_the_loop()
    else:
        print("Please set the OPENAI_API_KEY environment variable to run the examples.")
        print("Example: export OPENAI_API_KEY=your_api_key_here")