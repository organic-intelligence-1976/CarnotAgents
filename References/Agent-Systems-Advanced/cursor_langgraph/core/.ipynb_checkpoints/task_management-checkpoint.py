"""Task management system for Cursor-LangGraph."""

class TaskManager:
    """Manages tasks and their execution in the system."""
    
    def __init__(self):
        self.tasks = {}
    
    def create_task(self, task_id: str, config: dict):
        """Create a new task with the given ID and configuration."""
        task = Task(task_id, config)
        self.tasks[task_id] = task
        return task

class Task:
    """Represents a task in the system."""
    
    def __init__(self, task_id: str, config: dict):
        self.task_id = task_id
        self.config = config
        self.status = "created"
    
    def __repr__(self):
        return f"Task(id={self.task_id}, status={self.status})" 