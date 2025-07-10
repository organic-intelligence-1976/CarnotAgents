"""
Enhanced Agent System with Structured Tool Usage

This version uses a more structured approach to ensure tools are actually used.
"""

from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
import json
import asyncio
import re
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
    structured_response: Dict[str, Any]


class StructuredAgent:
    """Agent that uses structured responses for reliable tool usage"""
    
    def __init__(
        self, 
        name: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Tool]] = None,
        llm: Optional[BaseChatModel] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        force_tool_use: bool = True
    ):
        self.name = name
        self.context = context or {}
        self.tools = tools or []
        self.force_tool_use = force_tool_use
        
        # Set up LLM
        if llm:
            self.llm = llm
        elif llm_config:
            self.llm = create_llm(**llm_config)
        else:
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
        workflow.add_node("analyze_task", self._analyze_task)
        workflow.add_node("execute_action", self._execute_action)
        workflow.add_node("check_completion", self._check_completion)
        workflow.add_node("final_response", self._final_response)
        
        # Add edges
        workflow.add_edge("analyze_task", "execute_action")
        workflow.add_edge("execute_action", "check_completion")
        
        # Conditional edge from check_completion
        workflow.add_conditional_edges(
            "check_completion",
            self._should_continue,
            {
                "continue": "analyze_task",
                "end": "final_response"
            }
        )
        
        workflow.add_edge("final_response", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_task")
        
        return workflow.compile()
    
    def _should_continue(self, state: AgentState) -> str:
        """Decide whether to continue or end"""
        # Simple logic: if we've used tools or tried enough times, end
        if state["tools_used"] or state.get("iterations", 0) > 2:
            return "end"
        return "continue"
    
    async def _analyze_task(self, state: AgentState) -> AgentState:
        """Analyze task and decide on next action"""
        # Build structured prompt
        system_content = f"""You are {self.name}, an AI agent with specific tools available.

Your context: {json.dumps(self.context, indent=2)}

Available tools:
{self._format_tools()}

IMPORTANT: You must respond in the following JSON format:
{{
    "thought": "Your reasoning about what to do",
    "action": "tool_name or 'none' if no tool is needed",
    "action_input": "input for the tool if action is not 'none'"
}}

When a task explicitly asks you to use a specific tool, you MUST use that tool.
Example: If asked to "use the calculator", your action must be "calculator"."""

        task_prompt = f"Task: {state['current_task']}"
        
        # Handle Gemini's message format
        if self._is_gemini:
            messages = [HumanMessage(content=f"{system_content}\n\n{task_prompt}")]
        else:
            messages = [
                SystemMessage(content=system_content),
                HumanMessage(content=task_prompt)
            ]
        
        # Get structured response
        response = await self.llm.ainvoke(messages)
        state["messages"].append(response)
        
        # Parse the structured response
        try:
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                structured = json.loads(json_match.group())
            else:
                # Fallback: try to parse the whole response
                structured = json.loads(response.content)
            
            state["structured_response"] = structured
        except:
            # If parsing fails, create a default structure
            state["structured_response"] = {
                "thought": response.content,
                "action": "none",
                "action_input": ""
            }
        
        # Increment iteration counter
        state["iterations"] = state.get("iterations", 0) + 1
        
        return state
    
    async def _execute_action(self, state: AgentState) -> AgentState:
        """Execute the action decided by analysis"""
        structured = state.get("structured_response", {})
        action = structured.get("action", "none").lower()
        action_input = structured.get("action_input", "")
        
        if action != "none" and action in self.tool_map:
            tool = self.tool_map[action]
            try:
                result = await tool.execute(action_input)
                state["tools_used"].append(action)
                state["messages"].append(
                    AIMessage(content=f"Tool '{action}' result: {result}")
                )
            except Exception as e:
                state["messages"].append(
                    AIMessage(content=f"Tool '{action}' error: {str(e)}")
                )
        
        return state
    
    async def _check_completion(self, state: AgentState) -> AgentState:
        """Check if the task is complete"""
        # This is handled by _should_continue
        return state
    
    async def _final_response(self, state: AgentState) -> AgentState:
        """Generate the final response"""
        system_content = f"You are {self.name}. Provide a final response to the task."
        
        # Build context from execution
        context_prompt = f"Task: {state['current_task']}\n\n"
        
        if state["tools_used"]:
            context_prompt += "Actions taken:\n"
            for msg in state["messages"]:
                if isinstance(msg, AIMessage) and "Tool" in msg.content:
                    context_prompt += f"- {msg.content}\n"
        else:
            context_prompt += "No tools were used.\n"
        
        context_prompt += "\nProvide a clear, complete response to the original task."
        
        # Handle message format
        if self._is_gemini:
            messages = [HumanMessage(content=f"{system_content}\n\n{context_prompt}")]
        else:
            messages = [
                SystemMessage(content=system_content),
                HumanMessage(content=context_prompt)
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
    
    def _format_tools(self) -> str:
        """Format tools for prompt"""
        if not self.tools:
            return "No tools available"
        
        formatted = []
        for tool in self.tools:
            formatted.append(f"- {tool.name}: {tool.description}")
        return "\n".join(formatted)
    
    async def run(self, task: str) -> Dict[str, Any]:
        """Run the agent on a task"""
        initial_state = AgentState(
            messages=[HumanMessage(content=task)],
            context=self.context,
            tools_used=[],
            current_task=task,
            result=None,
            structured_response={}
        )
        
        final_state = await self.graph.ainvoke(initial_state)
        return final_state["result"]


# For backward compatibility
Agent = StructuredAgent


# Example usage
if __name__ == "__main__":
    async def test_structured_agent():
        # Create a simple tool
        def calculator(expression: str) -> str:
            try:
                result = eval(expression)
                return f"Result: {result}"
            except:
                return "Error: Invalid expression"
        
        calc_tool = Tool(name="calculator", func=calculator, description="Evaluates math expressions")
        
        # Create agent
        agent = StructuredAgent(
            name="MathAgent",
            context={"role": "mathematics assistant"},
            tools=[calc_tool],
            force_tool_use=True
        )
        
        # Test
        result = await agent.run("Use the calculator to compute 25 * 4")
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_structured_agent())