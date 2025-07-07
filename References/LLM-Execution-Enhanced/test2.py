from core import TaskSolver, LLMInterface, create_mlx_llm_function

mlx_llm = LLMInterface(custom_llm_func=create_mlx_llm_function())
solver = TaskSolver(mlx_llm, "./config")

task = """Create a list of the first 5 square numbers, then calculate their average. 
Print both the list and the average."""

print("Starting task...")
result = solver.solve_task(task)
print("\nFull conversation:")
print(result)

