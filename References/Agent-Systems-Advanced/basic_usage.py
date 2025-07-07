from typing import Any, Dict
from ..src.core import ContextLevel, EvolutionType
from ..src.context.pool import ContextPool
from ..src.agents.base import HybridAgent

class ResearchAgent(HybridAgent):
    """An agent that performs research tasks with context awareness."""
    
    def process(self, input_data: Any, context: ContextPool, **kwargs) -> Dict:
        visible_context = context.get_visible_layers(self.agent_id, self.context_level)
        
        # Store research question in global context
        if isinstance(input_data, str) and "?" in input_data:
            context.update_context(
                self.agent_id,
                {"current_research_question": input_data},
                ContextLevel.GLOBAL
            )
        
        # Process based on visible context
        if "current_research_question" in visible_context:
            # Send a message about the research question
            self.send_message(
                f"Working on question: {visible_context['current_research_question']}",
                context,
                visibility=ContextLevel.GROUP
            )
            
            # Propose an evolution to improve research capabilities
            self.propose_evolution(
                context,
                EvolutionType.BEHAVIOR,
                "Add data analysis capabilities",
                {"new_method": "analyze_data", "parameters": ["data_source", "method"]}
            )
            
        return {
            "agent_id": self.agent_id,
            "processed_input": input_data,
            "visible_context_keys": list(visible_context.keys()),
            "message_count": len(self.message_history)
        }

def main():
    # Initialize context pool
    context_pool = ContextPool()
    
    # Create agents with different context access levels
    researcher1 = ResearchAgent("researcher1", ContextLevel.GLOBAL, "Primary researcher")
    researcher2 = ResearchAgent("researcher2", ContextLevel.GROUP, "Assistant researcher")
    researcher3 = ResearchAgent("researcher3", ContextLevel.PRIVATE, "Data collector")
    
    # Process a research question
    question = "How does context sharing affect agent collaboration?"
    
    print("\n=== Processing Research Question ===")
    result1 = researcher1.process(question, context_pool)
    print(f"Researcher 1 result: {result1}")
    
    result2 = researcher2.process("Analyzing collaboration patterns", context_pool)
    print(f"Researcher 2 result: {result2}")
    
    result3 = researcher3.process("Collecting data", context_pool)
    print(f"Researcher 3 result: {result3}")
    
    # Check evolution proposals
    print("\n=== Evolution Proposals ===")
    for agent in [researcher1, researcher2, researcher3]:
        evolutions = agent.get_evolution_history()
        if evolutions:
            print(f"\n{agent.agent_id} proposed changes:")
            for evolution in evolutions:
                print(f"- {evolution.description} ({evolution.type.value})")
                
    # Check messages
    print("\n=== Messages ===")
    for agent in [researcher1, researcher2, researcher3]:
        messages = agent.get_message_history()
        if messages:
            print(f"\n{agent.agent_id} messages:")
            for msg in messages:
                print(f"- [{msg.visibility.value}] {msg.content}")

if __name__ == "__main__":
    main() 