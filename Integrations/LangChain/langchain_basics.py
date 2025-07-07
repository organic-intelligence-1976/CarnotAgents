"""
LangChain Basic Integration Examples

This module demonstrates fundamental integration patterns with the LangChain framework,
showing basic chain creation, prompt templates, and tool usage.

Key components:
- Simple chain creation
- Prompt templates
- Tool integration
- LangGraph integration for workflow

This implementation is based on the examples from the original LangChain test notebook.
"""

import os
from typing import Dict, List, Any, Optional

# Import LangChain components
try:
    from langchain.agents import Tool
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, AIMessage
    from langchain_openai import ChatOpenAI
    from typing import TypedDict, Annotated, Sequence
    from langgraph.graph import Graph, END
    import operator
except ImportError:
    print("Required packages are not installed. Please install using:")
    print("pip install langchain langchain_openai langgraph")


class LangChainIntegration:
    """A wrapper class for LangChain integration patterns."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the LangChain integration with optional API key.
        
        Args:
            openai_api_key: The OpenAI API key. If None, will try to use the environment variable.
        """
        # Set API key if provided, otherwise rely on environment variable
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Validate API key
        if not os.environ.get("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY not found in environment variables.")
    
    def create_chat_model(self, model_name: str = "gpt-3.5-turbo") -> ChatOpenAI:
        """
        Create a ChatOpenAI model instance.
        
        Args:
            model_name: The name of the model to use
            
        Returns:
            The ChatOpenAI model instance
        """
        return ChatOpenAI(model_name=model_name)
    
    def create_simple_chain(self, template: str, model_name: str = "gpt-3.5-turbo"):
        """
        Create a simple chain with a template and model.
        
        Args:
            template: The prompt template string
            model_name: The name of the model to use
            
        Returns:
            A simple chain that can be invoked
        """
        prompt = ChatPromptTemplate.from_template(template)
        model = self.create_chat_model(model_name)
        chain = prompt | model
        return chain
    
    def create_calculator_tool(self):
        """
        Create a simple calculator tool function.
        
        Returns:
            A function that evaluates mathematical expressions
        """
        def calculator(expression: str) -> str:
            """Evaluates a mathematical expression."""
            try:
                return str(eval(expression))
            except Exception as e:
                return f"Error in calculation: {str(e)}"
        
        return calculator
    
    def create_agent_with_tools(self, system_message: str, model_name: str = "gpt-3.5-turbo"):
        """
        Create an agent with tools using LangGraph.
        
        Args:
            system_message: The system message for the agent
            model_name: The name of the model to use
            
        Returns:
            A compiled graph that can be invoked
        """
        # Define state structure for the graph
        class AgentState(TypedDict):
            messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
            next: str
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Create the model and agent
        model = self.create_chat_model(model_name)
        agent = prompt | model
        
        # Create the calculator tool
        calculator = self.create_calculator_tool()
        
        # Define the agent function
        def run_agent(state: AgentState) -> AgentState:
            messages = state["messages"]
            response = agent.invoke({"messages": messages})
            
            # Parse response for tool use
            content = response.content
            if "ACTION: calculator" in content:
                # Extract the expression from the response
                expression = content.split("INPUT:")[1].strip()
                result = calculator(expression)
                
                # Add both the tool request and result to messages
                new_messages = list(messages)
                new_messages.extend([
                    AIMessage(content=content),
                    HumanMessage(content=f"Calculator result: {result}")
                ])
                return {"messages": new_messages, "next": "agent"}
            
            # No tool use, just continue
            return {"messages": messages + [response], "next": END}
        
        # Format the final output
        def format_output(state: AgentState) -> dict:
            """Format the final output from the messages"""
            messages = state["messages"]
            return {"output": messages[-1].content}
        
        # Create and compile the graph
        workflow = Graph()
        workflow.add_node("agent", run_agent)
        workflow.add_node("output", format_output)
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", "output")
        workflow.set_finish_point("output")
        
        return workflow.compile()


# Example usage
def example_simple_chain():
    """Run a simple chain example."""
    integration = LangChainIntegration()
    
    # Create a simple chain
    chain = integration.create_simple_chain(
        "Tell me a short joke about {topic}."
    )
    
    # Invoke the chain
    response = chain.invoke({"topic": "programming"})
    print(f"Response: {response.content}")
    return response


def example_calculator_agent():
    """Run an example of an agent with a calculator tool."""
    integration = LangChainIntegration()
    
    # Create an agent with calculator tool
    agent_chain = integration.create_agent_with_tools(
        system_message="""You are hired to answer questions. You have access to a calculator tool.
        To use the calculator, format your response as:
        ACTION: calculator
        INPUT: <math expression>
        
        Otherwise just respond normally. In your response please make sure you respect the following wish:
        DO NOT ASK any questions or wait for a confirmation if they approve of your plan of action. 
        Just give your best answer."""
    )
    
    # Invoke the agent
    result = agent_chain.invoke({
        "messages": [HumanMessage(content="What is 123123 multiplied by 123123123?")]
    })
    
    print(f"Result: {result}")
    return result


if __name__ == "__main__":
    # Check if OpenAI API key is available
    if os.environ.get("OPENAI_API_KEY"):
        print("Running LangChain simple chain example...")
        example_simple_chain()
        
        print("\nRunning LangChain calculator agent example...")
        example_calculator_agent()
    else:
        print("Please set the OPENAI_API_KEY environment variable to run the examples.")
        print("Example: export OPENAI_API_KEY=your_api_key_here")