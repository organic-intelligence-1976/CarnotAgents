from typing import Dict, Any
from ..src.core import ContextLevel, EvolutionType
from ..src.context.pool import ContextPool
from ..src.agents.base import HybridAgent
from ..src.agents.maintenance import CodeQualityAgent, ContextOptimizationAgent

# Sample code to analyze
SAMPLE_CODE = '''
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number using a really long line that definitely exceeds our style guidelines and should trigger a violation in our quality checks."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

def another_function_with_no_docstring():
    result = []
    for i in range(10):
        for j in range(i):
            for k in range(j):
                result.append(i * j * k)  # This creates high complexity
    return result
'''

class ResearchAgent(HybridAgent):
    """A basic research agent that generates some context data."""
    
    def process(self, input_data: Any, context: ContextPool, **kwargs) -> Dict:
        # Store some data in different context levels
        context.update_context(
            self.agent_id,
            {"research_question": input_data},
            ContextLevel.GLOBAL
        )
        
        context.update_context(
            self.agent_id,
            {"analysis_step": "initial"},
            ContextLevel.GROUP
        )
        
        context.update_context(
            self.agent_id,
            {"private_notes": "Some private thoughts"},
            ContextLevel.PRIVATE
        )
        
        return {
            "status": "Data stored in context",
            "agent_id": self.agent_id
        }

def main():
    # Initialize context pool
    context_pool = ContextPool()
    
    # Create main research agent
    researcher = ResearchAgent("researcher1", ContextLevel.GLOBAL)
    
    # Create maintenance agents
    code_quality = CodeQualityAgent("code_quality_agent")
    context_optimizer = ContextOptimizationAgent("context_optimizer")
    
    print("\n=== Initial Research Phase ===")
    # Research agent stores some data
    researcher.process("How can we optimize code quality?", context_pool)
    researcher.process("What patterns emerge in optimization?", context_pool)
    
    print("\n=== Code Quality Analysis ===")
    # Code quality agent analyzes code
    quality_result = code_quality.process(SAMPLE_CODE, context_pool)
    print("\nCode Quality Metrics:")
    print(f"Lines of Code: {quality_result['metrics'].lines_of_code}")
    print(f"Documentation Lines: {quality_result['metrics'].documentation_lines}")
    print(f"Complexity Score: {quality_result['metrics'].complexity_score}")
    print("\nStyle Violations:")
    for violation in quality_result['metrics'].style_violations:
        print(f"- {violation}")
    
    print("\n=== Context Optimization Analysis ===")
    # Context optimizer analyzes usage patterns
    optimization_result = context_optimizer.process(context_pool)
    print("\nContext Metrics:")
    print(f"Total Entries: {optimization_result['metrics'].total_entries}")
    print("\nContext Sizes:")
    for context_type, sizes in optimization_result['metrics'].context_sizes.items():
        print(f"- {context_type}: {sizes}")
    
    if optimization_result['optimizations']:
        print("\nOptimization Suggestions:")
        for opt in optimization_result['optimizations']:
            print(f"- {opt['type']}: {opt.get('reason', opt.get('context', 'No detail'))}")
    
    print("\n=== Evolution Proposals ===")
    for agent in [researcher, code_quality, context_optimizer]:
        evolutions = agent.get_evolution_history()
        if evolutions:
            print(f"\n{agent.agent_id} proposed changes:")
            for evolution in evolutions:
                print(f"- {evolution.description} ({evolution.type.value})")
    
    print("\n=== Messages ===")
    for agent in [researcher, code_quality, context_optimizer]:
        messages = agent.get_message_history()
        if messages:
            print(f"\n{agent.agent_id} messages:")
            for msg in messages:
                print(f"- [{msg.visibility.value}] {msg.content}")

if __name__ == "__main__":
    main() 