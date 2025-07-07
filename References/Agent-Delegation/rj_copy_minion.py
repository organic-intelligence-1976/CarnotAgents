import json
import subprocess
import os

def read_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def write_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def append_file(filepath, content):
     with open(filepath, 'a') as f:
        f.write(content)

def create_directory(dirpath):
    os.makedirs(dirpath, exist_ok=True)

def run_llm(prompt):
    # Placeholder for actual LLM API call.  Replace this.
    print(f"**LLM PROMPT:**\n{prompt}\n**END PROMPT**") # For testing.
    return input("(Simulated LLM Output): ") # Simulate LLM

def evaluate_offspring(directory):
    #Simulate offspring evaluation. In real implementation, the LLM will decide which evaluations it performs and its results will decide the future of the offspring
    print(f"\n Evaluating offspring in {directory}\n")
    return "SUCCESS" #Simulate offspring success for this minimal example

def spawn_offspring(code_filepath, problem_filepath, offspring_dir):
    create_directory(offspring_dir)
    new_problem_filepath = os.path.join(offspring_dir, "problem_statement.txt")
    new_code_filepath = os.path.join(offspring_dir, "minion.py")
    new_instruction_filepath = os.path.join(offspring_dir, "instruction.txt")
    #Read the content of problem_filepath and code_filepath from the parent minion directory and copy them to the child.
    problem_statement = read_file(problem_filepath)
    code = read_file(code_filepath)
    write_file(new_problem_filepath, problem_statement)
    write_file(new_code_filepath, code)
    write_file(new_instruction_filepath, read_file("instruction.txt")) #Copy the instruction.
    command = ['python', new_code_filepath]
    process = subprocess.Popen(command, cwd=offspring_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    print(f"Offspring output for {offspring_dir}:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
    #For simplicity let's imagine there are no errors to report back. Instead there may be other ways to communicate the result. For example through output files, like result.txt
    return evaluate_offspring(offspring_dir) #Simulate result.

def main():
    directory = os.getcwd()
    print(f"Minion running in directory: {directory}")

    while True:
        instructions = read_file("instructions.txt")
        state_str = read_file("state.json")
        if state_str: #If the file is not empty
            state = json.loads(state_str)
        else:
             state = {}

        # Minimal "tools" made available to the LLM.  These are *described*
        # in instructions.txt, and the LLM decides when/how to use them.
        available_tools = {
            "read_file": read_file,
            "write_file": write_file,
            "append_file": append_file,
            "run_code": lambda code_string: subprocess.run(['python', '-c', code_string], capture_output=True, text=True).stdout, #Basic sandbox
            "run_llm": run_llm,
            "create_directory": create_directory,
            "spawn_offspring":spawn_offspring
        }

        prompt = instructions + "\n\n" + json.dumps(state, indent=2) # State as context

        llm_output = run_llm(prompt)
        print(f"**LLM Output:**\n{llm_output}")

        # **Crucially:  We're assuming the LLM's output is structured (e.g., JSON)
        #  to indicate which tool to use and its arguments.
        #  Error handling and more robust parsing would be needed in a
        #  real system.**
        try:
            action_request = json.loads(llm_output) #Simplified assumption.
            tool_name = action_request["tool"]
            tool_args = action_request.get("args", {}) #Optional args

            if tool_name in available_tools:
                result = available_tools[tool_name](**tool_args)
                state["last_tool_result"] = result  # Store for next cycle
            else:
                state["last_tool_result"] = f"Error: Tool '{tool_name}' not found."
        except json.JSONDecodeError:
            state["last_tool_result"] = f"Error: Invalid JSON from LLM: {llm_output}"
        except Exception as e:
            state["last_tool_result"] = f"Error: {e}"

        write_file("state.json", json.dumps(state, indent=2))

if __name__ == "__main__":
    main()