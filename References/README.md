# LLMFrameworks References

This directory contains reference materials and raw work from the original HQ structure that may be valuable for future development of the LLMFrameworks project.

## Contents

- **raw_work/** - Contains unprocessed code and documents from the original HQ structure
  - `rj_copy_langchain.ipynb` - Original notebook exploring LangChain framework capabilities
  - `rj_copy_autogen_test.ipynb` - Original notebook exploring Microsoft's AutoGen framework
  - `rj_copy_llm_executor_core.py` - Original LLM execution framework from Shared-Architecture

## Source Mapping

These files were sourced from the following locations in the original HQ structure:

1. **LangChain Exploration**
   - Original Path: `/Users/rezajamei/Desktop/HQ/Projects/AI-Research/LLM-Frameworks/`
   - Contains experiments with LangChain functionality, chains, and agents

2. **AutoGen Exploration**
   - Original Path: `/Users/rezajamei/Desktop/HQ/Projects/Modified-Public/Third-Party-Frameworks/AutoGen/`
   - Contains experiments with Microsoft's AutoGen multi-agent framework

3. **LLM Execution Framework**
   - Original Path: `/Users/rezajamei/Desktop/HQ/Projects/Shared-Architecture/LLM-Execution/`
   - Contains core LLM execution abstractions and interfaces

## Note to Future Developers

The LLMFrameworks project has been implemented as a more structured and standardized approach to working with multiple LLM frameworks. The raw work in this directory represents earlier explorations and implementations that informed the current design.

Key concepts that have been carried forward:
- Framework adapter patterns for consistent interfaces
- Multi-agent collaboration patterns
- Standardized message formats
- Cross-framework integration approaches

If you're continuing development on this project, you may find valuable ideas and approaches in these reference materials, especially for frameworks that aren't yet fully implemented in the main project structure.