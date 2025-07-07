# Renaissance

A flexible framework for iterative document-based problem solving through LLM interactions.

## Core Concept

Renaissance represents a fundamentally different approach to LLM problem-solving:

1. **Document-Based Progress**: We represent any project, with all its goals, partial work, resources, and challenges, as a structured document organized in XML-like sections. Rather than relying on chat history, the document itself contains the entire state of the project.

2. **Iterative Refinement**: The system implements a single core function that receives a partially completed document and moves the project forward by one step. Through multiple iterations, the document gradually evolves toward a complete solution.

3. **Structured Evolution**: Each step can add thoughts, plans, insights, or request code execution. The LLM provides explicit instructions on how to update the document using standardized tags that the system processes.

4. **Execution Integration**: When the LLM needs computational help, it can request code execution. The results are integrated back into the document, creating a continuous record of the project's development.

5. **Early Implementation**: While the current implementation is an early prototype, the core patterns enable a powerful new paradigm for complex problem-solving with LLMs.

## Capabilities

Renaissance enables:

- Step-by-step document evolution with full memory persistence
- Executing Python code snippets in a shared context
- Structured document creation and manipulation
- Processing LLM responses with XML-like tags
- Support for multiple LLM providers with a unified interface

## Installation

> **New to Renaissance?** See our [QUICK_START.md](docs/QUICK_START.md) guide for the fastest way to get up and running!

### Quick Setup (Linux/macOS)

You can use the provided setup script to quickly set up your environment:

```bash
# Run the setup script
./scripts/setup_env.sh
```

This script will:
- Check your Python version
- Offer to create a `python=python3` alias in your shell configuration
- Create a virtual environment if it doesn't exist
- Provide instructions for activating the environment and installing requirements

### Manual Setup

1. Clone the repository
2. Create and activate a virtual environment
```bash
# If python command is not available, use python3 instead
python3 -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate.bat
```

> **Tip**: On some systems, the `python` command might not be available or might point to Python 2.x.
> You can create an alias by adding `alias python=python3` to your `.bashrc` or `.zshrc` file.

3. Install the requirements
```bash
pip install -r requirements.txt
```
4. Uncomment and install optional dependencies for specific LLM providers as needed

## Project Structure

The repository is organized as follows:

- **renaissance/**: Core implementation of the Renaissance framework
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
  - **test_sorting_algorithm.py**, **test_text_summarization.py**: Domain-specific tests
  - **extract_suggestions.py**, **improvement_tracker.py**: Improvement tracking tools
- **scripts/**: Utility scripts for project management and automation
- **scripts/setup_env.sh**: Environment setup script
- **CLAUDE.md**: Detailed documentation and code patterns
- **README.md**: Overview of the framework (this file)

Note that `docs/high_level_design.py` is kept as a conceptual reference to show the original inspiration for the project. The actual API implementation in the `renaissance` package may differ in syntax and behavior.

### Renaissance Package Components

The `renaissance/` package contains several Python modules, each with specific responsibilities:

1. **__init__.py**:
   - Imports and re-exports all public functions and classes from the package
   - Makes these accessible when importing directly from the renaissance package
   - Organizes exports into document processing, history/TOC, details dictionary, and LLM provider functions

2. **config.py**:
   - Manages configuration settings for the Renaissance framework
   - Functions:
     - `load_config_from_file()`: Loads JSON or YAML configuration files
     - `update_config()`: Updates the current configuration with new values
     - `export_current_config()`: Exports current configuration to a file
   - Handles default values and configuration priorities
   - Automatically loads default configuration from configs/default.json

3. **doc_processor.py**:
   - Core of the Renaissance framework, handling document management and processing
   - Key functions:
     - `execute_code()`: Executes Python code in a shared context
     - `process_llm_response()`: Processes LLM responses with tagged actions
     - `to_text_form()`: Converts document dictionary to structured text
     - `step_work_on_doc()`: Advances document by one step using an LLM
     - `create_default_doc()`: Creates initial document structure
     - Document history: `save_doc_history()`, `get_doc_history()`, `get_history_length()`
     - Table of contents: `generate_table_of_contents()`
     - Details dictionary: `store_section()`, `get_section()`, `get_section_content()`, `list_sections()`
   - Maintains global state for document history and execution context

4. **llm_providers.py**:
   - Implements integrations with various LLM APIs
   - Classes:
     - `LLMProvider`: Base class for all providers
     - `OpenAIProvider`: For OpenAI GPT models
     - `AnthropicProvider`: For Anthropic Claude models
     - `GoogleProvider`: For Google Gemini models
     - `MLXProvider`: For local models using MLX (Apple Silicon)
     - `MockProvider`: For testing without API keys (not recommended for actual testing)
   - Factory function:
     - `get_llm_provider()`: Returns appropriate provider based on name

5. **mock_llm.py**:
   - Provides mock LLM functionality for testing
   - Classes:
     - `Response`: Mimics LLM API response structure
     - `MockLLM`: Returns predefined responses for testing
   - Note: This appears to be a legacy file as its functionality is now incorporated into `llm_providers.py`

The Renaissance framework uses a document-centric approach, where an evolving document holds all state, and the LLM makes incremental changes to it through multiple iterations. The framework handles code execution, document history tracking, and structuring content with XML-like sections. The system is designed with a plugin architecture for different LLM providers and configurable behavior through JSON configuration files.

## Usage

The module provides several key functions:

- `execute_code`: Run Python code in a shared context
- `process_llm_response`: Extract and process tagged actions from LLM responses
- `to_text_form`: Convert document dictionaries to XML-like structured text
- `step_work_on_doc`: Run a full iteration step with the LLM
- `create_default_doc`: Create a new document with default sections

### LLM Providers

Renaissance supports multiple LLM providers with a unified interface:

- OpenAI (GPT models)
- Anthropic (Claude models)
- Google (Gemini models)
- MLX (for local models on Apple Silicon)
- Mock (for testing)

Example of using an LLM provider:

```python
from renaissance import get_llm_provider, create_default_doc, step_work_on_doc

# Initialize an LLM provider (OpenAI in this example)
llm = get_llm_provider("openai", model="gpt-4-turbo")

# Create a document with a user request
doc = create_default_doc("Analyze the Fibonacci sequence.")

# Process with the LLM
updated_doc, _ = step_work_on_doc(llm, doc)
```

You can also run the example script:

```bash
python example_real_llm.py --provider openai --model gpt-4-turbo
```

### Configuration System

Renaissance features a comprehensive configuration system that makes it easy to experiment with different prompts and settings. All text prompts are stored in a configuration module and can be customized per iteration.

#### Global Configuration

To export the default configuration:

```bash
python export_config.py --format json --output my_config.json
```

You can then modify this file and use it with the example script:

```bash
python example_real_llm.py --config my_config.json --provider openai
```

#### Step-Specific Configuration

Renaissance now supports explicitly providing configuration for each iteration step:

```python
# Load a specific prompt variant
import json
with open("configs/research_oriented.json", "r") as f:
    research_config = json.load(f)

# Create a document with a specific configuration
doc = create_default_doc("Analyze quantum entanglement.", config=research_config)

# Run an iteration with the same configuration
updated_doc, response = step_work_on_doc(llm, doc, config=research_config)
```

From the command line:

```bash
# Use a predefined prompt variant from the configs directory
python example_real_llm.py --prompt-variant research_oriented --request "Investigate protein folding"

# Use a custom step-specific config file
python example_real_llm.py --step-config my_step_config.json --request "Design a neural network"
```

#### Included Prompt Variants

Renaissance comes with several pre-configured prompt variants in the `configs/` directory:

1. **research_oriented.json** - Optimized for scientific research with hypotheses, experiments, and analysis
2. **coding_oriented.json** - Focused on software development with architecture, implementation, and testing
3. **exploration_oriented.json** - Designed for open-ended exploration with questions, insights, and reflections

#### Creating Custom Variants

You can easily create your own configuration variants using the provided script:

```bash
# Create a variant based on the default configuration
./create_config_variant.py --output configs/my_variant.json --sections "Goal,Doc_Structure,User_Request,Working_Memory,Analysis,Status"

# Create a variant based on an existing variant
./create_config_variant.py --name research_oriented --output configs/my_research_variant.json

# Create a variant with custom content from files
./create_config_variant.py --output configs/custom_variant.json --system-prompt prompts/system.txt --goal prompts/goal.txt
```

This allows you to experiment with different variations of:
- System prompts for LLMs
- Document structure and formatting
- Code execution display
- LLM provider settings
- Document section organization

You can maintain multiple configuration files for different experiments and easily compare their performance.

## How It Works

The Renaissance workflow consists of these key components:

1. **Document Structure**: Projects are represented as documents with structured sections. Initially, a document might just contain the user's goal, but it evolves through iterations.

2. **Step-by-Step Progress**: Each iteration involves:
   - The current document state is sent to an LLM
   - The LLM suggests document updates via structured tags
   - The system processes these tags to update the document
   - For code execution requests, the system runs the code and captures results
   - The updated document is ready for the next iteration

3. **Document Evolution**: Through multiple iterations, the document grows to include:
   - Plans and approaches
   - Intermediate results from code execution
   - Insights and findings
   - Final conclusions

4. **XML-Based Communication**: The LLM uses specific tags to request changes:
   ```
   <execute>
   # Python code to run
   </execute>
   
   <new_section name="Analysis">
   Content for the new section
   </new_section>
   ```

Each step builds on previous work, creating an iterative research process that can solve complex problems incrementally.

## Comprehensive File Documentation

### Core Documentation Files

1. **README.md**: 
   - Overview of the Renaissance framework and its core concepts
   - Installation and setup instructions
   - Usage examples and configuration options
   - Project structure and architecture overview
   - Testing procedures and roadmap references
   - Serves as the main entry point for users

2. **CLAUDE.md**: 
   - Detailed project guidelines and standards
   - Repository structure and organization
   - Testing methodology and best practices
   - Project vision and architectural principles
   - Environment setup and common commands
   - Configuration system details and examples
   - LLM provider usage instructions
   - Code style standards and conventions

3. **docs/ROADMAP.md**: 
   - Current state of the project (last updated March 2, 2025)
   - Strengths and limitations analysis
   - Short-term improvements (1-3 months)
   - Medium-term goals (3-6 months)
   - Long-term vision (6+ months)
   - Implementation strategy and principles
   - Contribution guidelines

4. **docs/IMPROVEMENT_SUGGESTIONS.md**: 
   - Organized collection of test case observations
   - Detailed findings and improvement opportunities from testing
   - Prioritized enhancement suggestions
   - Implementation priorities across all test cases
   - Track record of identified issues and their importance

5. **docs/AUTOMATED_TESTING_GUIDE.md**:
   - Detailed instructions for using the automated testing framework
   - Step-by-step testing workflow
   - Guide to creating new test scripts
   - Documentation for test utilities and helper functions
   - Integration with improvement tracking

6. **docs/TEST_NOTEBOOK_GUIDE.md**:
   - Guide for notebook-based testing approaches
   - Standard notebook structure and sections
   - Documentation conventions and procedures
   - Analysis methodologies for notebook test results

7. **docs/high_level_design.py**:
   - Original design document (not for direct use)
   - Conceptual model with implementation notes
   - Architectural principles and patterns
   - Detailed comments about potential future directions
   - Function prototypes that inspired the actual implementation

### Core Setup and Configuration Files

1. **scripts/setup_env.sh**: 
   - Automated environment setup script
   - Python version detection and configuration
   - Virtual environment creation
   - Shell configuration and alias setup
   - Installation instructions

2. **requirements.txt**: 
   - Core dependencies (numpy, matplotlib, pandas, jupyter)
   - LLM provider dependencies (openai)
   - Optional dependencies for additional providers
   - Version specifications for compatibility

3. **configs/default.json**: 
   - Default system prompt templates
   - Goal and document structure definitions
   - Formatting instructions for LLM interactions
   - Code execution display templates
   - LLM provider settings
   - Default section definitions

4. **configs/variant*.json**: 
   - Specialized configuration variants:
     - **coding_oriented.json**: Software development focus
     - **research_oriented.json**: Scientific method approach
     - **exploration_oriented.json**: Open-ended exploration

### Conceptual Design Files

1. **high_level_design.py**: 
   - Original design document (not for direct use)
   - Conceptual model with implementation notes
   - Architectural principles and patterns
   - Detailed comments about potential future directions
   - Function prototypes that inspired the actual implementation

### Example Files

1. **examples/basic_usage.py**: 
   - Main demonstration script
   - Basic framework usage examples
   - Core functionality demonstration

2. **examples/test_run_with_history.ipynb**: 
   - Interactive Jupyter notebook for testing
   - Complete history tracking
   - Document evolution visualization
   - Iterative problem-solving

3. **examples/wiki_search_example.py**: 
   - Demonstrates web search implementation
   - LLM-based search functionality without direct API
   - Shows file I/O capabilities
   - Error handling and recovery

4. **examples/package_install_test.py**:
   - Demonstrates package installation capabilities
   - Dynamic environment adaptation
   - Dependency management
   - Shows how LLMs can modify their environment


### Implementation Files (renaissance/ directory)

1. **__init__.py**: 
   - Imports and re-exports all public functions and classes
   - Organizes exports into logical groups
   - Makes core functionality accessible at package level
   - Maintains clean public API

2. **config.py**: 
   - Configuration management system
   - JSON and YAML configuration loading
   - Configuration updating and exporting
   - Default value management
   - Configuration prioritization logic

3. **doc_processor.py**: 
   - Core document management and processing
   - Code execution in shared context
   - LLM response processing with XML tags
   - Document history tracking
   - Table of contents generation
   - Details dictionary storage/retrieval
   - Document-to-text conversion
   - Step-based iteration logic

4. **llm_providers.py**: 
   - LLM provider implementations
   - Common interface for all providers (LLMProvider base class)
   - Implementations for:
     - OpenAI (GPT models)
     - Anthropic (Claude models)
     - Google (Gemini models)
     - MLX (local models on Apple Silicon)
     - Mock (testing provider)
   - Factory function for provider selection

5. **mock_llm.py**: 
   - Legacy mock LLM implementation
   - Test response generation
   - Predefined response patterns
   - Functionality now incorporated in llm_providers.py

## Testing

The project includes both example notebooks and a comprehensive automated testing framework to systematically evaluate and improve the system's capabilities.

### Example Notebook

The main example Jupyter notebook demonstrates core functionality:

- **examples/test_run_with_history.ipynb**: Demonstrates history tracking and complete testing workflow

To execute the example notebook and save the results:

```bash
jupyter nbconvert --to notebook --execute examples/test_run_with_history.ipynb --output examples/test_run_with_history_executed.ipynb
```

### Automated Testing Framework

Renaissance includes a powerful automated testing framework for more systematic evaluation:

```bash
# Run quick test with simple CLI
python tests/test_renaissance_simple.py --prompt "Your prompt here" --iterations 3

# Run domain-specific tests
python tests/test_text_summarization.py   # Test text summarization
python tests/test_sorting_algorithm.py    # Test algorithm implementation
```

The automated testing system provides:

1. **Structured test execution** with consistent output
2. **Document evolution tracking** across iterations
3. **Performance measurement** and detailed analysis
4. **Automatic improvement suggestion generation**

#### Capturing Improvement Suggestions

Test results can be analyzed to automatically extract and track improvement suggestions:

```bash
# Run a test and capture output
python tests/test_text_summarization.py > test_results.log

# Extract improvement suggestions interactively
python tests/extract_suggestions.py -i test_results.log -n "Text Summarization" --interactive

# View updated improvement suggestions
cat docs/IMPROVEMENT_SUGGESTIONS.md
```

For detailed information about the automated testing framework, see [docs/AUTOMATED_TESTING_GUIDE.md](docs/AUTOMATED_TESTING_GUIDE.md).

### Systematic Feature Testing Workflow

The recommended testing workflow combines automated tests with systematic documentation:

1. **Select a capability** to test (e.g., text summarization, code generation)
2. **Create a focused prompt** that exercises the targeted capability
3. **Run the test** using the appropriate test script or creating a new one
4. **Analyze results** including iterations, document evolution, and errors
5. **Extract improvement suggestions** using the automated tools
6. **Review and prioritize** the suggestions in docs/IMPROVEMENT_SUGGESTIONS.md

This process helps identify improvement opportunities and builds a comprehensive roadmap for future development. See CLAUDE.md for additional testing procedures.

## Future Directions

Renaissance is under active development with many planned enhancements. See our [docs/ROADMAP.md](docs/ROADMAP.md) file for detailed information about:

- **Near-term improvements** - Document scaling, tool integration, UX enhancements
- **Medium-term goals** - Workflow templates, evaluation framework, integration ecosystem
- **Long-term vision** - Advanced research capabilities, enterprise features, domain-specific extensions

We welcome contributions and suggestions for the project's future development!

## License

MIT