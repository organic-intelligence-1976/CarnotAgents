# LLM Executor Framework

## Original Location
`/Users/rezajamei/Desktop/repos/llm_executor/`

## Purpose
The LLM Executor framework orchestrates the interaction between LLMs, code execution, and context management. It provides a structured approach to solving tasks by allowing LLMs to write and execute code while maintaining conversation context throughout the problem-solving process.

## Key Components

### Core Implementation
- **core.py**: The main orchestration module containing the TaskSolver class
- **config/**: Configuration files including system prompts

## Content Description

The LLM Executor framework implements a task solving approach with several key features:

1. **Orchestrated Interaction**:
   - Manages the flow between LLM, code execution, and context
   - Handles conversation state throughout the problem-solving process
   - Provides clear entry points through the TaskSolver class

2. **Code Execution**:
   - Enables LLMs to write and execute code
   - Captures execution results and integrates them back into the context
   - Supports iterative refinement based on execution outcomes

3. **Context Management**:
   - Maintains problem context throughout the solution process
   - Updates context with execution results
   - Provides context for subsequent LLM calls

## Usage Context

This framework can be used for:
- Building systems that solve computational problems with LLMs
- Creating agents that can execute code to accomplish tasks
- Implementing interactive problem-solving assistants
- Developing educational tools that explain computational concepts

## Files Copied
- `/Users/rezajamei/Desktop/repos/llm_executor/core.py` → `/Users/rezajamei/Desktop/HQ/Projects/Shared-Architecture/LLM-Execution/rj_copy_llm_executor_core.py`

## Note on Shared Architecture Integration

The LLM Executor framework offers significant integration opportunities with other shared architectural components:

1. **Complementary to recursive_llm.py**: It adds code execution capabilities to recursive processing
2. **Document Generation Enhancement**: It can add computational capabilities to document generation
3. **Renaissance Integration**: It can work alongside Renaissance's document-centric approach to add execution

The execution-oriented approach represents a valuable architectural pattern that can enhance multiple projects in HQ by adding computational capabilities to LLM-based workflows.