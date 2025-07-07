# Renaissance Project Guidelines

## Repository Structure

- **renaissance/**: Core implementation package
- **configs/**: Pre-configured prompt variants for different use cases
- **docs/**: Documentation files
  - **AUTOMATED_TESTING_GUIDE.md**: Guide for the automated testing framework
  - **IMPROVEMENT_SUGGESTIONS.md**: Collected improvement ideas from testing
  - **ROADMAP.md**: Project roadmap and future development plans
  - **TEST_NOTEBOOK_GUIDE.md**: Guide for notebook-based testing
- **examples/**: Example scripts and notebooks demonstrating usage
  - **basic_usage.py**: Simple script showing core functionality
  - **test_run_with_history.ipynb**: Interactive testing notebook
  - **wiki_search_example.py**: Wikipedia search demonstration
  - **package_install_test.py**: Package installation capability demo
- **tests/**: Python scripts for automated testing
  - **renaissance_test_utils.py**: Shared testing utilities
  - **process_evaluation_test.py**: Process-focused testing tool
  - Domain-specific test scripts
  - Improvement tracking tools
- **scripts/**: Utility scripts for project management and automation
- **docs/high_level_design.py**: Original design document (conceptual reference only)

Note: The `docs/high_level_design.py` file is an inspirational starting point that shows the original conception of the project. The actual implementation may differ in syntax and behavior. It should not be imported or used directly.

## Testing Guidelines

When testing new functionality:
- **IMPORTANT: NEVER use the mock LLM provider for testing.** The mock provider uses canned responses that don't adapt to the actual query content, making test results meaningless.
- **Always use a real LLM provider** for meaningful testing
- Preferred provider for testing: `openai` with model `gpt-4-turbo`
- Secondary preferred provider: `claude` with model `claude-3-opus-20240229` 
- Document any unexpected behavior in detailed notes
- Compare actual vs. expected results to identify improvements
- If API keys are missing, document this as a limitation in your findings rather than falling back to the mock provider

> **⚠️ NOTE: Some test scripts in the tests directory need to be updated to match the patterns in the examples directory. The recommended approach is to use the run_with_history function as demonstrated in examples/test_run_with_history.ipynb.**

### Testing Approaches

Renaissance provides two complementary approaches for systematic testing:

#### Type 1: Process Evaluation Testing (HIGH PRIORITY)

This approach focuses on evaluating Renaissance's process and resilience when handling user requests:

1. **Use the process_evaluation_test.py script**:
   ```bash
   # Basic process evaluation test
   python tests/process_evaluation_test.py --prompt "Your test prompt"
   
   # With more iterations for deeper evaluation
   python tests/process_evaluation_test.py --prompt "Your test prompt" --iterations 10
   
   # Save output to a specific file
   python tests/process_evaluation_test.py --prompt "Your test prompt" --output test_results.txt
   ```

2. **Review the output log file**:
   - Raw LLM responses for each iteration
   - Document state after each iteration
   - Section additions and modifications
   - Error handling and recovery attempts

3. **Document findings in docs/IMPROVEMENT_SUGGESTIONS.md**:
   - Add a new test case section with the query used
   - Document key observations about system behavior
   - List specific improvement suggestions with priority levels
   - Update the implementation priorities based on all test cases

4. **Commit changes to git**:
   ```bash
   git add docs/IMPROVEMENT_SUGGESTIONS.md test_results.txt
   git commit -m "Add process evaluation test for <feature_name> and update improvement suggestions"
   ```

#### Type 2: Solution Quality Testing

For evaluating the quality and efficiency of Renaissance's final solutions:

1. **Use existing domain-specific test scripts**:
   ```bash
   # Domain-specific tests
   python tests/test_text_summarization.py
   python tests/test_sorting_algorithm.py
   ```

2. **Create custom test scripts for new capabilities**:
   ```bash
   # Create a new test script by duplicating and modifying existing ones
   cp tests/test_text_summarization.py tests/test_<your_feature>.py
   ```

3. **Capture test output and extract suggestions**:
   ```bash
   # Run test and capture output
   python tests/test_<your_feature>.py > test_results.log
   
   # Extract suggestions and update IMPROVEMENT_SUGGESTIONS.md
   python tests/extract_suggestions.py -i test_results.log -n "Your Feature Name" --interactive
   ```

For detailed information about the testing framework, see docs/AUTOMATED_TESTING_GUIDE.md.

The current priority is Type 1 Process Evaluation testing to establish basic system robustness before focusing on solution optimization.

### Analyzing Process Evaluation Test Results

When reviewing the logs from process_evaluation_test.py, focus on these key areas:

1. **Environment and Dependency Issues**:
   - Look for missing modules (e.g., ModuleNotFoundError)
   - Check if the system attempts to install or find alternatives to missing packages
   - Evaluate how well the system recovers from environment limitations

2. **Document Evolution**:
   - Track which sections are added in which iterations
   - Observe how Working_Memory accumulates information
   - Note whether information is properly transferred between iterations

3. **Error Recovery**:
   - Pay attention to how the system responds after execution errors
   - Check if it adjusts its approach after encountering obstacles
   - Look for creative problem-solving when faced with limitations

4. **Iteration Efficiency**:
   - Does progress accelerate or stall after multiple iterations?
   - Are later iterations building effectively on earlier work?
   - How many iterations are typically needed before meaningful progress?

5. **Prompt Handling Quality**:
   - How well does the system understand complex, multi-part instructions?
   - Does it maintain focus on the original goal throughout iterations?
   - Are all aspects of the prompt eventually addressed?

These observations will help identify opportunities to improve Renaissance's robustness, especially for handling edge cases and recovering from unexpected situations.

## Project Vision & Architecture

Renaissance implements a new paradigm for LLM-based problem solving:

1. **Document-Centric Approach**: All project state (goals, work, resources, challenges) is stored in a structured document with XML-like sections. This creates persistent memory beyond chat history limitations.

2. **Step Function Architecture**: The core function (`step_work_on_doc`) takes a partially completed document and advances it by one step. Through multiple iterations, the document evolves toward completion.

3. **Iterative Progress**: Each iteration may add thoughts, plans, insights, code, or execution results to the document so subsequent "researchers" build upon previous work.

4. **Structured Document Updates**: LLMs request document changes through structured tags (`<execute>`, `<new_section>`, etc.) which the system processes.

5. **Prototype Status**: This is an early implementation. The system may eventually handle very large documents by summarizing sections or storing them externally.

## Environment Setup
- Ensure correct Python version:
  - macOS/Linux: If `python` command doesn't work, use `python3` instead
  - You may want to create an alias: `alias python=python3` (add to .bashrc or .zshrc)
- Create virtual environment: 
  - `python3 -m venv venv` or
  - `python -m venv venv` (if python points to Python 3.x)
- Activate virtual environment:
  - macOS/Linux: `source venv/bin/activate`
  - Windows: `venv\Scripts\activate.bat`
- Git tracking:
  - Ensure the project is git tracked (but exclude venv folder)
  - Always run `git init` if starting a new project

## Commands
- Run tests: `python -m unittest discover tests/`
- Run single test: `python -m unittest tests/test_file.py`
- Lint code: `flake8 --max-line-length=100 --exclude=venv/,.venv/`
- Type checking: `mypy --ignore-missing-imports .`
- Install new dependencies: `pip install package_name && pip freeze > requirements.txt`

## Working with Configurations

### Default Configuration System
The system now uses a JSON-based configuration:

- **Default configuration**: Stored in `configs/default.json`
- **Variant configurations**: Stored in `configs/` directory (e.g., `coding_oriented.json`)
- **Configuration priority**: 
  1. Per-iteration config passed to functions
  2. Variant config loaded from file
  3. Default config from `default.json`
  4. Hardcoded fallback values

### Using Configuration Variants in Your Code
```python
# Load configuration variant
from renaissance.config import load_config_from_file
config = load_config_from_file("configs/coding_oriented.json")

# Create document with this configuration
doc = create_default_doc("Your prompt here", config=config)

# Run iteration with the configuration
updated_doc, response = step_work_on_doc(llm, doc, config=config)
```

### Creating Custom Configuration Variants
To create a custom configuration variant:

1. Start with an existing variant from the configs/ directory
2. Modify the specific parts you want to change:
   - system_prompt: The prompt sent to the LLM
   - goal: The task description shown in the document
   - formatting: Instructions on how to format responses
   - sections: List of section names to include in the document

3. Save your custom configuration to a JSON file for reuse

### Available Configuration Variants
- **default.json**: The default configuration with research team approach
- **research_oriented.json**: Uses scientific method (hypothesis, experiment, analysis)
- **coding_oriented.json**: Structured for software development
- **exploration_oriented.json**: Optimized for open-ended exploration

### Exporting a Configuration
You can export and update configurations:

```python
from renaissance.config import export_current_config, update_config

# Export current configuration to a file
export_current_config("my_custom_config.json", format="json")

# Update the default configuration
update_config({"system_prompt": "Your new prompt text", "sections": ["New", "Section", "List"]})

# Save changes back to the default.json file
export_current_config()  # No arguments updates the default config
```

## Using LLM Providers

### Supported LLM Providers
```python
# OpenAI (requires openai package and OPENAI_API_KEY)
llm = get_llm_provider("openai", model="gpt-4-turbo")

# Anthropic Claude (requires anthropic package and CLAUDE_API_KEY)
llm = get_llm_provider("claude", model="claude-3-opus-20240229")

# Google Gemini (requires google-generativeai package and GOOGLE_API_KEY)
llm = get_llm_provider("gemini", model="gemini-pro")

# MLX (for local models on Apple Silicon)
llm = get_llm_provider("mlx", model_path="/path/to/model")

# Mock (DO NOT USE FOR TESTING - only for demonstration or development setup)
llm = get_llm_provider("mock")  # WARNING: Returns canned responses regardless of query content
```

## Code Style
- **Imports**: Standard library first, third-party next, local imports last
- **Formatting**: 100 character line length maximum
- **Types**: Use docstrings for function type documentation
- **Docstrings**: All functions require docstrings with parameters and return values
- **Error Handling**: Use try/except with specific exceptions; include error messages
- **Naming**:
  - Functions: snake_case (e.g., `process_llm_response`)
  - Variables: snake_case (e.g., `doc_text_form`)
  - Constants: UPPER_SNAKE_CASE (e.g., `DEFAULT_GOAL`)
- **Comments**: TODO comments should include context on approach (e.g., "Reflexion-style")
- **Functions**: Keep functions focused on a single responsibility
- **Memory Management**: Be careful with global state (e.g., `_context`)