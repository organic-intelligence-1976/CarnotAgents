# Renaissance Framework

## Original Location
`/Users/rezajamei/Desktop/repos/renaissance/`

## Purpose
The Renaissance framework provides a document-centric approach to iterative problem solving with LLMs. It represents a fundamentally different architectural approach by using a structured document as the central representation of project state, rather than relying on chat history or conversational context.

## Key Components

### Core Architecture
- **doc_processor.py**: The heart of the system, implementing the document processing pipeline
- **config.py**: Configuration management for the Renaissance system
- **llm_providers.py**: Abstraction for different LLM service providers

### Documentation
- **README.md**: Comprehensive overview of the framework's approach and capabilities
- **CLAUDE.md**: Development guidelines and architectural documentation
- **docs/**: Additional documentation including roadmaps and testing guides

### Examples and Tests
- **examples/**: Demonstration scripts and notebooks showing various usage patterns
- **tests/**: Automated testing infrastructure
- **configs/**: Pre-configured prompt configurations for different use cases

## Content Description

The Renaissance framework represents a structured approach to document-based problem solving with several distinctive features:

1. **Document-Centric State**: All project progress, goals, resources, and partial work are represented in a structured document
2. **Iterative Processing**: A core function processes the document incrementally, making small improvements with each pass
3. **XML-like Structure**: The document uses standardized tags to structure content and processing instructions
4. **Code Execution**: The framework can execute code and integrate results back into the document
5. **Multi-Step Workflows**: Complex problems are broken down into sequential document transformations

## Usage Context

This framework can be used for:
- Implementing document generation systems with structured evolution
- Building problem-solving systems that require multiple steps
- Creating code generation pipelines with integrated execution
- Developing research assistants that maintain state in a document

## Files Copied
- `/Users/rezajamei/Desktop/repos/renaissance/README.md` → `/Users/rezajamei/Desktop/HQ/Projects/Shared-Architecture/Renaissance-Integration/rj_copy_renaissance_README.md`
- `/Users/rezajamei/Desktop/repos/renaissance/CLAUDE.md` → `/Users/rezajamei/Desktop/HQ/Projects/Shared-Architecture/Renaissance-Integration/rj_copy_renaissance_CLAUDE.md`
- `/Users/rezajamei/Desktop/repos/renaissance/renaissance/doc_processor.py` → `/Users/rezajamei/Desktop/HQ/Projects/Shared-Architecture/Renaissance-Integration/rj_copy_renaissance_doc_processor.py`

## Note on Architecture Integration

The Renaissance architecture offers significant integration opportunities with other shared architectural components:

1. **Complementary to recursive_llm.py**: Both use recursive/iterative approaches to problem solving
2. **Document Generation Enhancement**: Offers structured document evolution that can enhance document generation
3. **Unification Potential**: Could serve as a unifying architecture across multiple projects

The document-centric approach represents a significant architectural pattern that could inform the development of a more unified approach across projects in HQ.