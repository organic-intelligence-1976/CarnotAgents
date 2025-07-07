# Renaissance Automated Testing Guide

This guide describes how to use Renaissance's automated testing framework to systematically evaluate and improve the system's capabilities across different use cases.

> **⚠️ NOTE: Some test scripts in the tests directory need to be updated to match the patterns in the examples directory. The recommended approach is to use the run_with_history function as demonstrated in examples/test_run_with_history.ipynb.**

## Overview

The Renaissance testing framework supports two distinct testing approaches:

### Type 1: Process Evaluation Testing (HIGHER PRIORITY)
- **Purpose**: Evaluate Renaissance's process and resilience when handling user requests
- **Focus**: Document the system's behavior through each iteration, including raw responses, document updates, and recovery from errors
- **Output**: Detailed log file showing the full sequence of system behavior for manual analysis
- **Status**: Implemented in process_evaluation_test.py script
- **Priority**: HIGH - Critical for establishing basic system robustness before optimizing solutions

### Type 2: Solution Quality Testing
- **Purpose**: Evaluate the quality and efficiency of Renaissance's final solutions
- **Focus**: Analyze specific capabilities (algorithms, text processing, etc.) in final output
- **Output**: Performance metrics, code analysis, and quality assessment
- **Status**: Currently implemented in domain-specific test scripts
- **Priority**: LOWER - Will become more important after basic process robustness is established

The following test capabilities are supported:

1. Run automated tests on various prompts
2. Capture and analyze LLM responses through multiple iterations
3. Track document evolution
4. Generate improvement suggestions based on test results 
5. Automatically update the centralized improvement suggestions document

## Testing Infrastructure

### Core Components

The testing infrastructure consists of:

1. **renaissance_test_utils.py**: Common utilities for running tests and analyzing results
2. **Domain-specific test scripts**: Pre-configured scripts for testing specific capabilities
3. **General-purpose CLI tool**: For quick ad-hoc testing with custom prompts
4. **Improvement suggestion tracking**: Automated mechanism to capture and organize enhancement ideas

### Key Utilities

The `renaissance_test_utils.py` module provides these core functions:

- `run_renaissance_test()`: Orchestrates the entire test process
- `run_iteration()`: Executes a single iteration and captures results
- `analyze_document_evolution()`: Tracks how the document structure evolves
- `find_section_by_candidates()`: Searches for relevant content in the document
- Helper functions for output formatting and analysis

## Running Tests

### Using the Command-Line Interface

For quick, ad-hoc testing:

```bash
python test_renaissance_simple.py --prompt "Your test prompt here" --iterations 3
```

Options:
- `--prompt`, `-p`: The prompt to test (can be provided directly)
- `--prompt-file`, `-f`: Path to a file containing the prompt
- `--iterations`, `-i`: Number of iterations to run (default: 3)
- `--model`, `-m`: LLM model to use (default: gpt-4-turbo)

### Using Domain-Specific Scripts

For testing specific capabilities with pre-configured analysis:

```bash
python test_text_summarization.py  # Test text summarization capabilities
python test_sorting_algorithm.py   # Test algorithm implementation capabilities
```

### Creating Custom Test Scripts

To create a new domain-specific test script:

1. Import core utilities:
   ```python
   from renaissance_test_utils import run_renaissance_test, print_section
   ```

2. Define a domain-specific analysis function:
   ```python
   def analyze_my_domain(final_doc):
       print_section("DOMAIN-SPECIFIC ANALYSIS")
       # Custom analysis logic here
   ```

3. Set up the test in the main function:
   ```python
   def main():
       prompt = "Your domain-specific test prompt"
       run_renaissance_test(
           prompt=prompt,
           iterations=3,
           model="gpt-4-turbo",
           analysis_func=analyze_my_domain
       )
   ```

## Analyzing Test Results

The testing framework automatically analyzes and reports:

1. **Iteration details**: Time taken, document sections, LLM responses
2. **Document evolution**: Section additions, content growth, structure changes
3. **Domain-specific insights**: Custom analysis for the specific capability being tested

The analysis is displayed during test execution and can be captured for documentation.

## Generating Improvement Suggestions

### Automated Suggestion Workflow

The testing framework can be integrated with an improvement suggestion tracking system:

```python
from improvement_tracker import record_suggestions

def analyze_test_results(final_doc, iterations_data):
    # Analyze results and identify improvement opportunities
    suggestions = []
    
    # Example suggestion
    suggestions.append({
        "category": "Error Handling",
        "description": "Improve error messages for missing libraries",
        "priority": "High",
        "context": "Observed in iteration 2 when attempting to import matplotlib"
    })
    
    # Record suggestions to the improvement tracking system
    record_suggestions("test_case_name", suggestions)
```

### Updating IMPROVEMENT_SUGGESTIONS.md

The `record_suggestions()` function:

1. Reads the current IMPROVEMENT_SUGGESTIONS.md file
2. Adds the new suggestions in the proper format
3. Updates the implementation priorities section based on suggestion priorities
4. Writes the updated content back to the file

## Best Practices for Test Case Development

1. **Create focused test cases** that target specific capabilities
2. **Use realistic prompts** that represent actual user needs
3. **Run multiple iterations** to observe the system's learning behavior
4. **Analyze failure modes** to identify improvement opportunities
5. **Document specific observations** rather than general issues
6. **Prioritize suggestions** based on impact and feasibility
7. **Group related test cases** to identify broader patterns
8. **Test edge cases** to identify robustness issues

## Integrating with Development Workflow

The automated testing system integrates with the development workflow:

1. **Regression testing**: Run existing tests after making changes
2. **Feature validation**: Create new tests for new capabilities
3. **Improvement prioritization**: Use aggregated suggestions to guide development
4. **Progress tracking**: Compare test results before and after changes

## Example: Complete Test and Documentation Workflow

```bash
# 1. Run the test
python test_text_summarization.py > test_results.log

# 2. Extract suggestions and update tracking (can be automated)
python extract_suggestions.py --input test_results.log --test-name "Text Summarization"

# 3. Review updated improvement suggestions
cat IMPROVEMENT_SUGGESTIONS.md

# 4. Commit the changes
git add IMPROVEMENT_SUGGESTIONS.md test_results.log
git commit -m "Add text summarization test results and improvement suggestions"
```

## Creating a Type 1 Process Evaluation Test

To create a script-based process evaluation test (Type 1 - HIGH PRIORITY):

1. **Create a new test script file**:
   ```python
   # process_evaluation_test.py
   
   import os
   import time
   from renaissance import (
       create_default_doc,
       step_work_on_doc,
       get_llm_provider,
       to_text_form
   )
   
   def run_process_evaluation_test(prompt, iterations=3, model="gpt-4-turbo", output_file=None):
       """
       Run a process evaluation test that captures the full sequence of Renaissance's
       work on a user request, including raw responses and document updates.
       
       Args:
           prompt: The user request to process
           iterations: Number of iterations to run (default: 3)
           model: The LLM model to use (default: gpt-4-turbo)
           output_file: Path to save the detailed log (default: auto-generated)
       
       Returns:
           Path to the generated log file
       """
       # Initialize LLM provider
       llm = get_llm_provider("openai", model=model)
       
       # Generate output filename if not provided
       if output_file is None:
           timestamp = time.strftime("%Y%m%d_%H%M%S")
           first_words = "_".join(prompt.split()[:3]).lower()
           output_file = f"test_log_{first_words}_{timestamp}.txt"
       
       # Create the initial document
       doc = create_default_doc(prompt)
       
       # Initialize the log content
       log_content = [
           f"RENAISSANCE PROCESS EVALUATION TEST\n",
           f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
           f"Model: {model}\n",
           f"Iterations: {iterations}\n",
           f"\n{'='*80}\n",
           f"USER REQUEST:\n{prompt}\n",
           f"{'='*80}\n\n",
           f"INITIAL DOCUMENT:\n{to_text_form(doc)}\n",
           f"\n{'='*80}\n"
       ]
       
       # Run iterations
       current_doc = doc
       for i in range(iterations):
           section_header = f"ITERATION {i+1}"
           log_content.append(f"\n{section_header}\n{'-'*len(section_header)}\n\n")
           
           # Run the iteration
           start_time = time.time()
           updated_doc, response = step_work_on_doc(llm, current_doc)
           end_time = time.time()
           
           # Log the raw response
           log_content.append(f"RAW RESPONSE:\n{response}\n\n")
           
           # Log the updated document
           log_content.append(f"UPDATED DOCUMENT:\n{to_text_form(updated_doc)}\n\n")
           
           # Log document changes
           new_sections = set(updated_doc.keys()) - set(current_doc.keys())
           if new_sections:
               log_content.append(f"NEW SECTIONS ADDED: {', '.join(new_sections)}\n\n")
           
           modified_sections = {k for k in current_doc.keys() & updated_doc.keys() 
                               if current_doc[k] != updated_doc[k]}
           if modified_sections:
               log_content.append(f"MODIFIED SECTIONS: {', '.join(modified_sections)}\n\n")
           
           # Log timing information
           log_content.append(f"Time taken: {end_time - start_time:.2f} seconds\n")
           log_content.append(f"{'='*80}\n")
           
           # Update current document for next iteration
           current_doc = updated_doc
       
       # Write the log to file
       with open(output_file, 'w') as f:
           f.write("".join(log_content))
       
       print(f"Process evaluation test completed. Log saved to: {output_file}")
       return output_file
   
   def main():
       """Run the process evaluation test from command line."""
       import argparse
       
       parser = argparse.ArgumentParser(description="Renaissance Process Evaluation Test")
       parser.add_argument('--prompt', '-p', type=str, help='User request to process')
       parser.add_argument('--prompt-file', '-f', type=str, help='File containing the user request')
       parser.add_argument('--iterations', '-i', type=int, default=3, help='Number of iterations to run')
       parser.add_argument('--model', '-m', type=str, default='gpt-4-turbo', help='LLM model to use')
       parser.add_argument('--output', '-o', type=str, help='Output file path')
       
       args = parser.parse_args()
       
       # Get prompt from arguments or file
       if args.prompt:
           prompt = args.prompt
       elif args.prompt_file:
           with open(args.prompt_file, 'r') as f:
               prompt = f.read()
       else:
           parser.error("You must provide either --prompt or --prompt-file")
       
       # Run the test
       run_process_evaluation_test(
           prompt=prompt,
           iterations=args.iterations,
           model=args.model,
           output_file=args.output
       )
   
   if __name__ == "__main__":
       main()
   ```

2. **How to use the script**:

   ```bash
   # Basic usage with prompt text
   python process_evaluation_test.py --prompt "Create a solution for web scraping stock prices"
   
   # Using a prompt file
   python process_evaluation_test.py --prompt-file my_prompt.txt
   
   # Custom iterations and model
   python process_evaluation_test.py --prompt "Analyze this dataset" --iterations 5 --model "gpt-4-turbo"
   
   # Specify output file
   python process_evaluation_test.py --prompt "Design an algorithm" --output my_test_log.txt
   ```

This script captures the essential aspects of Type 1 testing:
- Records each raw response exactly as received
- Shows the document state after each iteration
- Highlights new and modified sections
- Tracks timing information
- Creates a comprehensive log file for analysis

Unlike Type 2 testing, this approach doesn't evaluate solution quality but provides a detailed record of the system's thought process, document evolution, and behavior when handling user requests.

## Recent Updates (2025-03-07)

The process_evaluation_test.py script has been enhanced with the following features:

1. **Configuration Support**
   - Added support for custom configuration files via the `--config` parameter
   - Enabled loading configuration from JSON/YAML files
   - Updated code to use configuration in step_work_on_doc function

2. **Proto-Researcher Integration**
   - Added support for testing with Proto-Researcher-inspired document structure
   - Enhanced testing for TaskQueue and other specialized sections
   - Improved output formatting for better readability

### Using Custom Configurations in Tests

To use a custom configuration with the testing framework:

```bash
# Run test with custom configuration
python tests/process_evaluation_test.py --prompt-file user_requests/your_prompt.txt --config configs/proto_inspired.json --iterations 5 --output your_test_output.txt
```

### Testing with TaskQueue Structure

When testing with the TaskQueue structure, the testing framework will now track:
- Task completion status across iterations
- Addition of new tasks
- Movement of tasks between status categories (Completed/In Progress/Backlog)

This provides better insight into how Renaissance breaks down complex problems and tracks progress when using the Proto-Researcher-inspired configuration.

## Conclusion

The Renaissance automated testing framework provides a systematic approach to evaluating system capabilities, identifying improvement opportunities, and tracking progress. By integrating testing with improvement suggestion tracking, the development process becomes more data-driven and focused on user needs.

The current priority is implementing Type 1 Process Evaluation testing to establish basic system robustness before moving on to optimizing solution quality. This will help ensure Renaissance can reliably handle requests and recover from errors before focusing on solution optimization.

For implementation details of specific test cases, see the domain-specific test scripts in the repository.