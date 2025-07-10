"""
Test script to verify tool usage with different scenarios
"""

import asyncio
import nest_asyncio
nest_asyncio.apply()

from agent_system_v2 import StructuredAgent as Agent, Tool
import json

# Create different tools
def calculator_tool(expression: str) -> str:
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

def web_search_tool(query: str) -> str:
    # Mock web search
    return f"Search results for '{query}': [Mock results - In real implementation, this would search the web]"

def file_reader_tool(filename: str) -> str:
    # Mock file reader
    return f"Contents of {filename}: [Mock content - In real implementation, this would read the file]"

# Create tools
calc_tool = Tool(
    name="calculator",
    func=calculator_tool,
    description="Evaluates mathematical expressions accurately"
)

search_tool = Tool(
    name="web_search",
    func=web_search_tool,
    description="Searches the web for information"
)

file_tool = Tool(
    name="file_reader",
    func=file_reader_tool,
    description="Reads contents of files"
)

async def test_agents():
    # Test different scenarios that should trigger tool use
    test_scenarios = [
        {
            "task": "Please use the calculator tool to compute 15 * 23 + 42",
            "tools": [calc_tool],
            "expected_tool": "calculator"
        },
        {
            "task": "I need you to calculate the exact value of 123456789 * 987654321 using the calculator",
            "tools": [calc_tool],
            "expected_tool": "calculator"
        },
        {
            "task": "Use the web_search tool to find information about quantum computing",
            "tools": [search_tool],
            "expected_tool": "web_search"
        },
        {
            "task": "Read the contents of config.json using the file_reader tool",
            "tools": [file_tool],
            "expected_tool": "file_reader"
        },
        {
            "task": "First use the calculator to compute 50 * 30, then search the web for that number",
            "tools": [calc_tool, search_tool],
            "expected_tools": ["calculator", "web_search"]
        }
    ]
    
    # Test with different providers
    providers = []
    if os.getenv('OPENAI_API_KEY'):
        providers.append(("openai", "gpt-4-turbo-preview"))
    if os.getenv('ANTHROPIC_API_KEY'):
        providers.append(("anthropic", "claude-3-opus-20240229"))
    if os.getenv('GOOGLE_API_KEY'):
        providers.append(("gemini", "gemini-1.5-flash"))
    
    for provider, model in providers:
        print(f"\n{'='*60}")
        print(f"Testing {provider} ({model})")
        print(f"{'='*60}")
        
        for i, scenario in enumerate(test_scenarios[:3]):  # Test first 3 scenarios
            print(f"\nScenario {i+1}: {scenario['task']}")
            
            try:
                agent = Agent(
                    name=f"{provider}_agent",
                    context={"role": "helpful assistant that uses tools"},
                    tools=scenario['tools'],
                    llm_config={
                        "provider": provider,
                        "model": model,
                        "temperature": 0.7
                    }
                )
                
                result = await agent.run(scenario['task'])
                
                print(f"Tools used: {result['tools_used']}")
                expected = scenario.get('expected_tools', [scenario.get('expected_tool')])
                if isinstance(expected, str):
                    expected = [expected]
                
                # Check if expected tools were used
                tools_correct = all(tool in result['tools_used'] for tool in expected if tool)
                print(f"Expected tools used: {'✓' if tools_correct else '✗'}")
                
                # Show the response
                print(f"Response preview: {result['response'][:200]}...")
                
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    import os
    asyncio.run(test_agents())