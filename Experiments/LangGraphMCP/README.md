# LangGraph + MCP Architecture Experiment

This is a minimal experiment combining LangGraph for agent coordination with MCP-style tool interfaces, using real LLMs from multiple providers.

## Installation

```bash
# Run the setup script
./setup.sh

# Or manually:
source venv/bin/activate
pip install -r requirements.txt
```

## Supported LLM Providers

- **OpenAI** (GPT-3.5, GPT-4)
- **Anthropic** (Claude 3 Opus, Sonnet, Haiku)
- **Google** (Gemini Pro)
- **Ollama** (Local Llama, Mistral, CodeLlama models)

## Quick Start

```python
from agent_system import Agent, Tool, AgentSystem
from llm_providers import create_llm

# Create an agent with a specific LLM
agent = Agent(
    name="Assistant",
    context={"role": "helpful assistant"},
    llm_config={
        "provider": "openai",  # or "anthropic", "gemini", "ollama"
        "model": "gpt-4-turbo-preview",
        "temperature": 0.7
    }
)

# Or create agents with different LLMs
fast_agent = Agent(
    name="FastAgent",
    llm_config={"provider": "openai", "model": "gpt-3.5-turbo"}
)

powerful_agent = Agent(
    name="PowerfulAgent", 
    llm_config={"provider": "anthropic", "model": "claude-3-opus-20240229"}
)

# Agents can have different LLMs for different purposes!
```

### Structured Agents (V2)

For more reliable tool usage, use the structured agent system:

```python
from agent_system_v2 import StructuredAgent

# Creates agents that reliably use tools when asked
agent = StructuredAgent(
    name="Assistant",
    tools=[calculator_tool, web_search_tool],
    llm_config={"provider": "openai", "model": "gpt-4"}
)

# Tools will actually be used when mentioned in tasks
result = await agent.run("Use the calculator to compute 25 * 4")
# result['tools_used'] will contain ['calculator']
```

## Features

1. **Multi-LLM Support**: Use different LLMs for different agents
2. **Agent Creation**: Create agents with context, tools, and specific LLMs
3. **Tool Creation**: Define tools as simple functions or other agents
4. **Agent as Tool**: Agents can be exposed as tools to other agents
5. **Hierarchical Teams**: Supervisors with different LLMs than workers
6. **Use-Case Optimization**: Pre-configured models for fast/balanced/powerful needs

## Files

- `agent_system.py`: Core agent and tool abstractions with real LLM integration
- `agent_system_v2.py`: Improved structured agent system with reliable tool usage
- `llm_providers.py`: LLM provider factory for easy model access
- `examples.ipynb`: Basic examples
- `examples_with_llms.ipynb`: Advanced examples with multiple LLM providers
- `examples_structured_agents.ipynb`: Examples using the improved v2 structured agents

## Environment Variables

Set these for the providers you want to use:
```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
# Ollama runs locally, no API key needed
```

## Notes

### Gemini Message Handling
Google's Gemini models handle messages differently than other providers. While OpenAI and Anthropic support system messages, Gemini requires all instructions to be in user messages. The agent system automatically detects Gemini models and adapts the message format accordingly.