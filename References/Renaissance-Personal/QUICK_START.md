# Renaissance Quick Start Guide

This guide helps you get started with Renaissance quickly, whether you're new to the project or returning after some time.

## What is Renaissance?

Renaissance is a document-based LLM problem-solving framework that:
- Stores all project state in a structured document
- Uses iterative steps to evolve solutions
- Integrates code execution with document updates
- Supports multiple LLM providers (OpenAI, Claude, Gemini)
- Maintains history and structure through multiple iterations

## Setup in 60 Seconds

```bash
# Clone repo if you don't have it
git clone https://github.com/yourusername/renaissance.git
cd renaissance

# Create and activate virtual environment
./scripts/setup_env.sh
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set your API key (choose your preferred provider)
export OPENAI_API_KEY="your-api-key-here"
# or: export CLAUDE_API_KEY="your-api-key-here"
```

## Running a Simple Test

```python
from renaissance import get_llm_provider, create_default_doc, step_work_on_doc

# Choose your LLM provider
llm = get_llm_provider("openai", model="gpt-4-turbo")
# or: llm = get_llm_provider("claude", model="claude-3-opus-20240229")

# Create a document with your query
doc = create_default_doc("Explain how quicksort works with a simple example")

# Run 3 iterations
for i in range(3):
    doc, _ = step_work_on_doc(llm, doc)
    print(f"Completed iteration {i+1}")
    
# Print the final document
print(doc["Doc_Text"])
```

## Testing with Notebooks

Our primary testing approach uses Jupyter notebooks:

```bash
# Create a new test notebook based on the example
cp examples/test_run_with_history.ipynb examples/test_your_feature.ipynb

# Open with Jupyter
jupyter notebook examples/test_your_feature.ipynb
```

Standard notebook structure:
1. Feature introduction and objectives
2. Renaissance imports and setup
3. Test query definition
4. Run test with run_with_history function
5. Response examination
6. Document evolution analysis

After testing, document your findings:
```bash
# Execute notebook with results saved
jupyter nbconvert --to notebook --execute examples/test_your_feature.ipynb --output examples/test_your_feature_executed.ipynb

# Update improvement suggestions
# Edit docs/IMPROVEMENT_SUGGESTIONS.md with your findings
```

## Automated Testing

For script-based testing:

```bash
# Run quick test
python tests/test_renaissance_simple.py --prompt "Your test prompt" --iterations 3

# Run specific capability test
python tests/test_sorting_algorithm.py

# Create your own test script
cp tests/test_text_summarization.py tests/test_your_feature.py
# Edit the new file to test your specific functionality

# Extract improvement suggestions
python tests/extract_suggestions.py -i test_results.log -n "Your Feature" --interactive
```

## Key Files & Directories

- **renaissance/**: Core implementation 
- **configs/**: JSON configuration files for different prompt variants
- **examples/**: Example scripts and notebooks demonstrating usage
- **tests/**: Python test scripts and utilities
- **docs/**: Documentation files
- **scripts/**: Utility scripts for setup and maintenance

## Configuration

Renaissance uses JSON-based configuration for flexibility:

```python
# Load a specific configuration variant
from renaissance.config import load_config_from_file
config = load_config_from_file("configs/coding_oriented.json")

# Create document with this configuration
doc = create_default_doc("Your prompt here", config=config)
```

Available variants:
- **default.json**: Standard research team approach
- **research_oriented.json**: Scientific method structure
- **coding_oriented.json**: Software development focus
- **exploration_oriented.json**: Open-ended exploration

## Common Commands

- Run test script: `python tests/process_evaluation_test.py --prompt "Your prompt"`
- Execute example: `python examples/basic_usage.py`
- Execute notebook: `jupyter nbconvert --to notebook --execute examples/test_run_with_history.ipynb --output examples/test_run_with_history_executed.ipynb`
- Check Python version: `python --version`
- Check code style: `flake8 --max-line-length=100 --exclude=venv/,.venv/`
- Run type checking: `mypy --ignore-missing-imports .`

## Documentation

- **README.md**: Project overview and main documentation
- **CLAUDE.md**: Detailed project guidelines and patterns
- **docs/ROADMAP.md**: Future development plans
- **docs/IMPROVEMENT_SUGGESTIONS.md**: Collected enhancement ideas
- **docs/AUTOMATED_TESTING_GUIDE.md**: Detailed testing procedures

## Git Workflow

We use feature branches for development:

```bash
# Check current branch
git branch

# Create a new branch for your feature
git checkout -b your-feature-name

# Make changes and commit
git add .
git commit -m "Descriptive message about your changes"

# When done, merge back to main (or submit PR)
git checkout main
git merge your-feature-name
```

Remember to update docs/IMPROVEMENT_SUGGESTIONS.md with any insights from your testing!