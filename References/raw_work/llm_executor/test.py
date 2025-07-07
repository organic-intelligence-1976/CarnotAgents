
from core import TaskSolver, LLMInterface, create_mlx_llm_function

mlx_llm = LLMInterface(custom_llm_func=create_mlx_llm_function())
solver = TaskSolver(mlx_llm, "./config")

# Add debug printing
print("Starting task...")
result = solver.solve_task("Calculate 2 + 2 and print the result")
print("\nFull conversation:")
print(result)

if "Execution" not in result:
    print("\nWarning: No code was executed!")