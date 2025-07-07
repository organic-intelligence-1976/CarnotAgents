from typing import Dict, Any
from ..src.core import ContextLevel, EvolutionType
from ..src.core.task_management import Task, TaskManager, TaskStatus
from ..src.context.pool import ContextPool
from ..src.agents.maintenance import CodeQualityAgent, ContextOptimizationAgent
import time

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

def create_maintenance_tasks(code_block: str) -> Dict[str, Task]:
    """Create a set of maintenance tasks with dependencies."""
    tasks = {}
    
    # Initial code quality check
    tasks['quality_check'] = Task(
        id='quality_check',
        description="Perform initial code quality analysis",
        assigned_agent_type='CodeQualityAgent',
        required_context_level=ContextLevel.GROUP
    )
    
    # Context optimization check (depends on quality check)
    tasks['context_check'] = Task(
        id='context_check',
        description="Analyze context usage patterns",
        assigned_agent_type='ContextOptimizationAgent',
        required_context_level=ContextLevel.PRIVATE,
        dependencies={'quality_check'}
    )
    
    # Detailed quality analysis (depends on initial check)
    tasks['detailed_analysis'] = Task(
        id='detailed_analysis',
        description="Perform detailed code quality analysis",
        assigned_agent_type='CodeQualityAgent',
        required_context_level=ContextLevel.GROUP,
        dependencies={'quality_check'}
    )
    
    return tasks

def main():
    # Initialize systems
    context_pool = ContextPool()
    task_manager = TaskManager()
    
    # Create agents
    code_quality = CodeQualityAgent("code_quality_agent")
    context_optimizer = ContextOptimizationAgent("context_optimizer")
    
    # Create and add tasks
    tasks = create_maintenance_tasks(SAMPLE_CODE)
    for task in tasks.values():
        task_manager.add_task(task)
    
    print("\n=== Starting Maintenance Tasks ===")
    
    # Process tasks until all are completed or failed
    while True:
        # Get ready tasks for each agent type
        code_quality_tasks = task_manager.get_tasks_for_agent('CodeQualityAgent')
        context_tasks = task_manager.get_tasks_for_agent('ContextOptimizationAgent')
        
        if not code_quality_tasks and not context_tasks:
            # Check if all tasks are done
            all_completed = all(
                task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                for task in tasks.values()
            )
            if all_completed:
                break
            time.sleep(0.1)  # Prevent busy waiting
            continue
            
        # Process code quality tasks
        for task in code_quality_tasks:
            print(f"\nProcessing task: {task.id}")
            result = code_quality.handle_task(task, context_pool, task_manager)
            print(f"Task {task.id} result: {result}")
            
        # Process context optimization tasks
        for task in context_tasks:
            print(f"\nProcessing task: {task.id}")
            result = context_optimizer.handle_task(task, context_pool, task_manager)
            print(f"Task {task.id} result: {result}")
    
    print("\n=== Final Task Status ===")
    for task_id, task in tasks.items():
        print(f"\nTask: {task_id}")
        print(f"Status: {task.status.value}")
        if task.result:
            print(f"Result: {task.result}")
        if task.error:
            print(f"Error: {task.error}")
    
    print("\n=== Execution History ===")
    for event in task_manager.get_execution_history():
        print(f"\nEvent: {event['event_type']}")
        print(f"Task: {event['task_id']}")
        print(f"Status: {event['task_status']}")
        print(f"Agent: {event['agent_type']}")
        print(f"Time: {event['timestamp']}")

if __name__ == "__main__":
    main() 