"""
A practical example of using Cursor-LangGraph to create a Wikipedia research assistant
that combines multiple specialized agents to gather and analyze information while
maintaining shared context.
"""

from typing import Dict, List, Optional
import json
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from cursor_langgraph.agents import Agent, AgentState
from cursor_langgraph.context import SharedContext
from cursor_langgraph.core import Process

# Define specialized agents for different aspects of research
class TopicExplorerAgent(Agent):
    """Agent responsible for initial topic exploration and identifying key areas to research."""
    
    def __init__(self):
        super().__init__()
        self.wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    
    async def run(self, context: SharedContext) -> AgentState:
        # Get the research topic from context
        topic = context.get("topic", "")
        if not topic:
            return AgentState(status="error", message="No research topic provided")
            
        # Search Wikipedia for initial information
        try:
            wiki_result = self.wiki_tool.run(topic)
            
            # Extract key areas to research
            llm = ChatOpenAI(temperature=0)
            response = llm.invoke([
                HumanMessage(content=f"""
                Based on this Wikipedia excerpt about {topic}, identify 3-4 key areas that warrant deeper research:
                
                {wiki_result}
                
                Format your response as a JSON list of strings.
                """)
            ])
            
            key_areas = json.loads(response.content)
            
            # Update shared context
            context.update({
                "initial_summary": wiki_result,
                "key_areas": key_areas,
                "research_status": "exploration_complete"
            })
            
            return AgentState(
                status="success",
                message=f"Identified {len(key_areas)} key areas for research"
            )
            
        except Exception as e:
            return AgentState(status="error", message=str(e))

class DetailResearchAgent(Agent):
    """Agent responsible for deep-diving into each key area."""
    
    def __init__(self):
        super().__init__()
        self.wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        
    async def run(self, context: SharedContext) -> AgentState:
        key_areas = context.get("key_areas", [])
        if not key_areas:
            return AgentState(status="error", message="No key areas to research")
            
        detailed_findings = {}
        
        for area in key_areas:
            try:
                # Research this specific area
                wiki_result = self.wiki_tool.run(area)
                
                # Analyze findings
                llm = ChatOpenAI(temperature=0)
                response = llm.invoke([
                    HumanMessage(content=f"""
                    Analyze this information about {area} and provide key insights:
                    
                    {wiki_result}
                    
                    Format your response as a concise JSON object with:
                    - main_points: list of key points
                    - implications: potential implications
                    """)
                ])
                
                detailed_findings[area] = json.loads(response.content)
                
            except Exception as e:
                detailed_findings[area] = {"error": str(e)}
        
        # Update shared context
        context.update({
            "detailed_findings": detailed_findings,
            "research_status": "details_complete"
        })
        
        return AgentState(
            status="success",
            message=f"Completed detailed research on {len(key_areas)} areas"
        )

class SynthesisAgent(Agent):
    """Agent responsible for synthesizing all research into a coherent summary."""
    
    async def run(self, context: SharedContext) -> AgentState:
        initial_summary = context.get("initial_summary", "")
        detailed_findings = context.get("detailed_findings", {})
        
        if not detailed_findings:
            return AgentState(status="error", message="No detailed findings to synthesize")
            
        try:
            llm = ChatOpenAI(temperature=0)
            response = llm.invoke([
                HumanMessage(content=f"""
                Synthesize this research into a comprehensive summary:
                
                Initial Overview:
                {initial_summary}
                
                Detailed Findings:
                {json.dumps(detailed_findings, indent=2)}
                
                Format your response as a JSON object with:
                - executive_summary: high-level overview
                - key_findings: list of main points
                - conclusions: final thoughts and implications
                """)
            ])
            
            synthesis = json.loads(response.content)
            
            # Update shared context
            context.update({
                "final_synthesis": synthesis,
                "research_status": "complete"
            })
            
            return AgentState(
                status="success",
                message="Successfully synthesized research findings"
            )
            
        except Exception as e:
            return AgentState(status="error", message=str(e))

def create_research_process(topic: str) -> Process:
    """Creates a research process for the given topic."""
    
    # Initialize agents
    explorer = TopicExplorerAgent()
    researcher = DetailResearchAgent()
    synthesizer = SynthesisAgent()
    
    # Create process with initial context
    process = Process(
        agents=[explorer, researcher, synthesizer],
        initial_context={"topic": topic}
    )
    
    return process

async def main():
    # Example usage
    topic = "Quantum Computing"
    process = create_research_process(topic)
    
    # Run the research process
    final_state = await process.execute()
    
    # Access results
    context = process.context
    if context.get("research_status") == "complete":
        synthesis = context.get("final_synthesis")
        print("\nResearch Results:")
        print("================")
        print(f"\nExecutive Summary:\n{synthesis['executive_summary']}")
        print("\nKey Findings:")
        for finding in synthesis['key_findings']:
            print(f"- {finding}")
        print("\nConclusions:")
        print(synthesis['conclusions'])
    else:
        print("Research process did not complete successfully")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 