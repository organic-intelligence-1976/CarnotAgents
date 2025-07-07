# Purpose: Orchestrate the interaction between LLM, code execution, and context management.
# Main entry point for using the system through TaskSolver class.
#
# Requirements:
# - OpenAI API key for default LLM interface
# - Config directory with base_system.txt
# - Access to parsers.py and executor.py functions
#
# Process flow:
# 1. TaskSolver initialized with LLM interface and config path
# 2. solve_task creates initial context from config and task
# 3. run_llm_loop manages conversation flow:
#    - Get LLM response
#    - Check for completion or code
#    - Execute code if present
#    - Update context with results
#
# Known issues/limitations:
# - No error recovery in main loop
# - Context grows unbounded
# - No message history management
# - Basic LLM interface with minimal configuration
# - No handling of API rate limits or errors
# - Config loading assumes specific file structure
# - No validation of loaded config content
# - Completion detection is crude (simple string match)



from typing import Callable, Dict, Optional
import os
from dataclasses import dataclass
import openai
from parsers import contains_code, extract_code
from executor import safe_execute_code

@dataclass
class LLMConfig:
    """Configuration for LLM interface"""
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.1
    max_tokens: Optional[int] = None

class LLMInterface:
    def __init__(self, 
                 custom_llm_func: Optional[Callable[[str], str]] = None,
                 llm_config: Optional[LLMConfig] = None):
        self.custom_llm_func = custom_llm_func
        self.config = llm_config or LLMConfig()

    def get_completion(self, prompt: str) -> str:
        if self.custom_llm_func:
            return self.custom_llm_func(prompt)
        
        # Default OpenAI implementation
        response = openai.ChatCompletion.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        return response.choices[0].message.content

def load_context_pieces(config_path: str) -> Dict[str, str]:
    pieces = {}
    for filename in os.listdir(config_path):
        with open(os.path.join(config_path, filename), 'r') as f:
            name = filename.replace('.txt', '')
            pieces[name] = f.read()
    return pieces

def build_initial_context(task: str, context_pieces: Dict[str, str]) -> str:
    return f"{context_pieces['base_system']}\n\nTask: {task}\n"

def append_to_context(current_context: str, new_content: str, content_type: str) -> str:
    return f"{current_context}\n{content_type}: {new_content}"

class TaskSolver:
    def __init__(self, llm_interface: LLMInterface, config_path: str):
        self.llm = llm_interface
        self.config_path = config_path

    def solve_task(self, task_description: str) -> str:
        context_pieces = load_context_pieces(self.config_path)
        initial_context = build_initial_context(task_description, context_pieces)
        return self.run_llm_loop(initial_context)

    def run_llm_loop(self, context: str) -> str:
        while True:
            print("\nGetting LLM response...")
            llm_response = self.llm.get_completion(context)
            print(f"\nLLM response length: {len(llm_response)}")
            
            # Clean up response - get only the first response before any additional tasks
            if "### 2" in llm_response:
                llm_response = llm_response.split("### 2")[0]
            
            # Remove markdown formatting
            llm_response = llm_response.replace('"""', '').strip()
            
            print("\nCleaned response:", llm_response)
            
            # First check for code
            if contains_code(llm_response):
                print("\nCode block found")
                code = extract_code(llm_response)
                output = safe_execute_code(code)
                print(f"\nExecution output: {output}")
                context = append_to_context(context, llm_response, "Assistant")
                context = append_to_context(context, output, "Execution")
            else:
                print("\nNo code block found in response")
                context = append_to_context(context, llm_response, "Assistant")
                
            # Then check for completion
            if "TASK COMPLETE" in llm_response:
                print("\nTask complete marker found")
                return context

        return context

def create_mlx_llm_function() -> Callable[[str], str]:
    """
    Creates a text-in/text-out function using MLX LLM.
    Returns a function that can be used with LLMInterface.
    """
    from mlx_lm import load, generate
    model, tokenizer = load("mlx-community/Meta-Llama-3-8B-Instruct-4bit")
    
    def mlx_completion(prompt: str) -> str:
        response = generate(model, tokenizer, prompt=prompt, verbose=False)
        return response
    
    return mlx_completion

# Example usage:
if __name__ == "__main__":
    # Option 1: OpenAI
    # openai.api_key = "your-api-key-here"  # Better to get from environment variable
    # openai_llm = LLMInterface()
    # openai_solver = TaskSolver(openai_llm, "./config")
    
    # Option 2: MLX
    mlx_llm = LLMInterface(custom_llm_func=create_mlx_llm_function())
    mlx_solver = TaskSolver(mlx_llm, "./config")
    
    # Use whichever solver you want:
    result = mlx_solver.solve_task("Calculate the sum of numbers from 1 to 10")
    print(result)




    