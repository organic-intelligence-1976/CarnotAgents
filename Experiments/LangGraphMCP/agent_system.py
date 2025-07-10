"""
Minimal LangGraph + MCP-style Agent System

This module provides a simple implementation of agents with tools,
combining LangGraph's state management with MCP-style tool interfaces.
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
import json
import asyncio
from functools import wraps
from llm_providers import create_llm, create_llm_for_use_case


@dataclass
class Tool:
    """MCP-style tool interface"""
    name: str
    func: Callable
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to MCP-style tool description"""
        return {
            "name": self.name,
            "description": self.description or f"Tool: {self.name}",
            "parameters": self.parameters
        }
    
    async def execute(self, *args, **kwargs) -> Any:
        """Execute the tool function"""
        if asyncio.iscoroutinefunction(self.func):
            return await self.func(*args, **kwargs)
        else:
            return self.func(*args, **kwargs)


class AgentState(dict):
    """State object for LangGraph"""
    messages: List[BaseMessage]
    context: Dict[str, Any]
    tools_used: List[str]
    current_task: str
    result: Any


class Agent:
    """Agent with context and tools"""
    
    def __init__(
        self, 
        name: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Tool]] = None,
        llm: Optional[BaseChatModel] = None,
        llm_config: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.context = context or {}
        self.tools = tools or []
        
        # Set up LLM - use provided LLM, create from config, or use default
        if llm:
            self.llm = llm
        elif llm_config:
            self.llm = create_llm(**llm_config)
        else:
            # Default to OpenAI GPT-4-turbo
            self.llm = create_llm("openai", model="gpt-4-turbo-preview", temperature=0.7)
        
        # Create tool lookup
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # Build the state graph
        self.graph = self._build_graph()
    
    @property
    def _is_gemini(self) -> bool:
        """Check if the LLM provider is Google Gemini"""
        return "Google" in self.llm.__class__.__name__
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("process_task", self._process_task)
        workflow.add_node("execute_tools", self._execute_tools)
        workflow.add_node("synthesize_result", self._synthesize_result)
        
        # Add edges
        workflow.add_edge("process_task", "execute_tools")
        workflow.add_edge("execute_tools", "synthesize_result")
        workflow.add_edge("synthesize_result", END)
        
        # Set entry point
        workflow.set_entry_point("process_task")
        
        return workflow.compile()
    
    async def _process_task(self, state: AgentState) -> AgentState:
        """Process the task and decide which tools to use"""
        # Build system message with agent context and available tools
        system_content = f"You are {self.name}, an AI agent with the following context:\n"
        system_content += json.dumps(self.context, indent=2)
        system_content += "\n\nAvailable tools:\n"
        for tool in self.tools:
            system_content += f"- {tool.name}: {tool.description}\n"
        system_content += "\nIMPORTANT: You MUST use the available tools when they are relevant to the task. If the task mentions a tool by name or requires a capability that a tool provides, you MUST indicate that you will use that tool. Respond with which tools you will use and why."
        
        # Create messages for LLM, adapting for Gemini
        if self._is_gemini:
            # Combine system and human content for Gemini
            combined_content = f"{system_content}\n\nTask: {state['current_task']}"
            messages = [HumanMessage(content=combined_content)]
        else:
            # Use standard System/Human messages for others
            messages = [
                SystemMessage(content=system_content),
                HumanMessage(content=state["current_task"])
            ]
        
        # Get LLM response
        response = await self.llm.ainvoke(messages)
        state["messages"].append(response)
        
        # Extract tool decisions from response
        # Store the analysis for tool execution phase
        state["tool_analysis"] = response.content
        
        return state
    
    async def _execute_tools(self, state: AgentState) -> AgentState:
        """Execute any necessary tools based on LLM analysis"""
        analysis = state.get("tool_analysis", "").lower()
        
        # Check which tools the LLM suggested
        for tool_name, tool in self.tool_map.items():
            # More robust detection - check if tool name or "use [tool]" or "will use" patterns appear
            tool_mentioned = (
                tool_name.lower() in analysis or
                f"use {tool_name.lower()}" in analysis or
                f"using {tool_name.lower()}" in analysis or
                (tool_name.lower() in analysis and ("will use" in analysis or "must use" in analysis or "should use" in analysis))
            )
            
            if tool_mentioned:
                try:
                    # Extract relevant part of task for the tool
                    # For calculator, extract mathematical expressions
                    if tool_name.lower() == "calculator":
                        # Look for mathematical expressions in the original task
                        import re
                        math_pattern = r'[\d\s\+\-\*\/\(\)]+(?:\s*[\+\-\*\/]\s*[\d\s\+\-\*\/\(\)]+)*'
                        matches = re.findall(math_pattern, state["current_task"])
                        if matches:
                            # Use the most complete expression found
                            expression = max(matches, key=len).strip()
                            result = await tool.execute(expression)
                        else:
                            # Fallback to full task
                            result = await tool.execute(state["current_task"])
                    else:
                        # For other tools, pass the full task
                        result = await tool.execute(state["current_task"])
                    
                    state["tools_used"].append(tool_name)
                    state["messages"].append(
                        AIMessage(content=f"Tool '{tool_name}' result: {result}")
                    )
                except Exception as e:
                    state["messages"].append(
                        AIMessage(content=f"Tool '{tool_name}' error: {str(e)}")
                    )
        
        return state
    
    async def _synthesize_result(self, state: AgentState) -> AgentState:
        """Synthesize the final result using LLM"""
        # Prepare synthesis prompt
        system_content = f"You are {self.name}. Synthesize the results of the task execution."
        
        synthesis_prompt = f"Task: {state['current_task']}\n\n"
        
        if state["tools_used"]:
            synthesis_prompt += "Tools used and their results:\n"
            for msg in state["messages"]:
                if isinstance(msg, AIMessage) and "Tool" in msg.content and "result:" in msg.content:
                    synthesis_prompt += f"{msg.content}\n"
        else:
            synthesis_prompt += "No tools were used.\n"
        
        synthesis_prompt += "\nProvide a coherent response to the original task."
        
        # Get final synthesis from LLM, adapting for Gemini
        if self._is_gemini:
            combined_content = f"{system_content}\n\n{synthesis_prompt}"
            messages = [HumanMessage(content=combined_content)]
        else:
            messages = [
                SystemMessage(content=system_content),
                HumanMessage(content=synthesis_prompt)
            ]
        
        final_response = await self.llm.ainvoke(messages)
        
        state["result"] = {
            "agent": self.name,
            "task": state["current_task"],
            "tools_used": state["tools_used"],
            "response": final_response.content,
            "context": self.context,
            "llm_provider": self.llm.__class__.__name__
        }
        
        return state
    
    async def run(self, task: str) -> Dict[str, Any]:
        """Run the agent on a task"""
        initial_state = AgentState(
            messages=[HumanMessage(content=task)],
            context=self.context,
            tools_used=[],
            current_task=task,
            result=None
        )
        
        final_state = await self.graph.ainvoke(initial_state)
        return final_state["result"]
    
    def as_tool(self) -> Tool:
        """Convert this agent to a tool that can be used by other agents"""
        async def agent_tool_func(task: str) -> str:
            result = await self.run(task)
            return result["response"]
        
        return Tool(
            name=f"agent_{self.name}",
            func=agent_tool_func,
            description=f"Delegate task to {self.name} agent",
            parameters={"task": {"type": "string", "description": "Task to delegate"}}
        )


class AgentSystem:
    """System for managing multiple agents"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.shared_tools: List[Tool] = []
    
    def register_agent(self, agent: Agent) -> None:
        """Register an agent in the system"""
        self.agents[agent.name] = agent
    
    def register_shared_tool(self, tool: Tool) -> None:
        """Register a tool available to all agents"""
        self.shared_tools.append(tool)
        # Add to all existing agents
        for agent in self.agents.values():
            agent.tools.append(tool)
            agent.tool_map[tool.name] = tool
    
    def create_agent(
        self, 
        name: str, 
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Tool]] = None,
        include_shared_tools: bool = True,
        llm: Optional[BaseChatModel] = None,
        llm_config: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """Create and register a new agent with optional LLM specification"""
        all_tools = []
        if include_shared_tools:
            all_tools.extend(self.shared_tools)
        if tools:
            all_tools.extend(tools)
            
        agent = Agent(
            name=name, 
            context=context, 
            tools=all_tools,
            llm=llm,
            llm_config=llm_config
        )
        self.register_agent(agent)
        return agent
    
    def create_hierarchical_agents(
        self,
        supervisor_name: str,
        worker_names: List[str],
        supervisor_context: Optional[Dict[str, Any]] = None,
        worker_contexts: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Agent:
        """Create a supervisor agent with worker agents as tools"""
        worker_contexts = worker_contexts or {}
        
        # Create worker agents
        workers = []
        for worker_name in worker_names:
            worker = self.create_agent(
                name=worker_name,
                context=worker_contexts.get(worker_name, {})
            )
            workers.append(worker)
        
        # Convert workers to tools for the supervisor
        worker_tools = [worker.as_tool() for worker in workers]
        
        # Create supervisor with worker tools
        supervisor = self.create_agent(
            name=supervisor_name,
            context=supervisor_context,
            tools=worker_tools
        )
        
        return supervisor


# Utility functions for creating common tools

def create_python_tool() -> Tool:
    """Create a tool for executing Python code"""
    def python_executor(code: str) -> str:
        try:
            # Create a restricted namespace
            namespace = {}
            exec(code, namespace)
            # Return any printed output or the last expression
            return str(namespace.get('result', 'Code executed successfully'))
        except Exception as e:
            return f"Error: {str(e)}"
    
    return Tool(
        name="python",
        func=python_executor,
        description="Execute Python code",
        parameters={"code": {"type": "string", "description": "Python code to execute"}}
    )


def create_memory_tool() -> Tool:
    """Create a tool for storing and retrieving memory"""
    memory_store = {}
    
    def memory_func(action: str, key: str = None, value: str = None) -> str:
        if action == "store" and key and value:
            memory_store[key] = value
            return f"Stored '{key}': '{value}'"
        elif action == "retrieve" and key:
            return memory_store.get(key, f"No value found for key '{key}'")
        elif action == "list":
            return f"Keys in memory: {list(memory_store.keys())}"
        else:
            return "Invalid memory operation"
    
    return Tool(
        name="memory",
        func=memory_func,
        description="Store and retrieve information",
        parameters={
            "action": {"type": "string", "enum": ["store", "retrieve", "list"]},
            "key": {"type": "string", "description": "Memory key"},
            "value": {"type": "string", "description": "Value to store"}
        }
    )


# Example usage
if __name__ == "__main__":
    async def main():
        # Create an agent system
        system = AgentSystem()
        
        # Create a simple calculator tool
        def calculator(expression: str) -> str:
            try:
                result = eval(expression)
                return f"Result: {result}"
            except:
                return "Error: Invalid expression"
        
        calc_tool = Tool(name="calculator", func=calculator)
        
        # Create an agent with the calculator tool
        math_agent = system.create_agent(
            name="MathAgent",
            context={"expertise": "mathematics"},
            tools=[calc_tool]
        )
        
        # Run a task
        result = await math_agent.run("Use calculator to compute 15 * 23")
        print(json.dumps(result, indent=2))
        
        # Create hierarchical agents
        supervisor = system.create_hierarchical_agents(
            supervisor_name="ProjectManager",
            worker_names=["Researcher", "Developer"],
            supervisor_context={"role": "coordinator"}
        )
        
        # Supervisor can delegate to workers
        result = await supervisor.run("agent_Researcher find information about LangGraph")
        print(json.dumps(result, indent=2))
    
    asyncio.run(main())