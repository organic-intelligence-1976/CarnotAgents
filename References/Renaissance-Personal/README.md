# Renaissance Examples

This directory contains streamlined examples that show how to use the Renaissance framework.

## Contents

1. **basic_usage.py**: Simple Python script showing the core functionality:
   - Basic step-by-step iteration with `step_work_on_doc`
   - Comprehensive history tracking with `run_with_history`
   - Minimal code needed to get started

2. **package_install_test.py**: Demonstrates package installation capabilities:
   - Shows how to use the `install_package()` function
   - Allows LLMs to install required Python packages
   - Tests with the autonomous_research.json configuration

3. **test_run_with_history.ipynb**: Interactive Jupyter notebook demonstrating the testing approach:
   - Set up Renaissance with different LLM providers
   - Run tests with history tracking
   - Analyze system behavior across iterations
   - Examine document evolution and changes

4. **wiki_search_example.py**: Practical application example:
   - Setting up Renaissance with appropriate configuration
   - Performing Wikipedia searches
   - Saving results to files

## Quick Start

### Using the Jupyter Notebook Demo

```bash
# Start a Jupyter notebook server
jupyter notebook

# Navigate to examples/test_run_with_history.ipynb
```

### Running the Python Script Demos

```bash
# Run the basic usage demo
python examples/basic_usage.py

# Test package installation capability
python examples/package_install_test.py

# Run the Wikipedia search example
python examples/wiki_search_example.py
```

## Creating Your Own Tests and Applications

These demos are meant to be templates for your own applications. To create your own:

1. Copy an existing demo as a starting point
2. Customize the prompt, configuration, and analysis to your needs
3. Add domain-specific code as required

For more advanced features, please refer to the full documentation.