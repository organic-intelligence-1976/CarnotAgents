# Renaissance Test Notebook Guide

> **⚠️ NOTE: This guide is being migrated to the new examples directory structure. The recommended approach is to use examples/test_run_with_history.ipynb as a template for new tests.**

This document provides a systematic approach for creating and executing test notebooks that evaluate specific capabilities of the Renaissance framework, and documenting the findings in IMPROVEMENT_SUGGESTIONS.md.

## Test Notebook Creation Process

### 1. Select a Capability to Test

Each test notebook should focus on a specific capability or feature of Renaissance:
- Core functionality (document creation, iteration)
- Specific features (history tracking with run_with_history)
- Domain-specific capabilities (data analysis, web search, etc.)
- Edge cases or potential limitations

### 2. Create a New Test Notebook

Follow this naming convention and structure:

```bash
# Create new notebook in the examples directory
touch examples/test_<feature_name>.ipynb
```

### 3. Standard Notebook Structure

Each test notebook should include these standard sections:

#### a. Introduction and Objectives
```markdown
# Testing Renaissance with <Feature> Query

This notebook tests the Renaissance framework with a <feature description> request to evaluate 
how it handles <specific capabilities being tested>.

## Test Objectives
- Evaluate capability X
- Test handling of Y
- Observe behavior when Z
```

#### b. Imports and Setup
```python
# Import the module and components
from renaissance import (
    execute_code,
    process_llm_response,
    to_text_form,
    step_work_on_doc,
    create_default_doc,
    get_llm_provider,
    # Include specific feature imports as needed
    get_doc_history,
    get_history_length, 
    clear_doc_history,
    generate_table_of_contents
)

# Reset document history to ensure we start clean
clear_doc_history()

# Initialize LLM provider 
# IMPORTANT: Always use OpenAI for all automatic testing of LLM functionality
# This ensures consistency across test cases and reliable comparison of results
# Do NOT use mock providers or other LLM providers for testing unless specifically directed
llm = get_llm_provider("openai", model="gpt-4-turbo")
```

#### c. Test Query Definition
```python
# Define a test query that will exercise the target capability
prompt = """
<Your carefully crafted query that targets the specific feature>
"""

# Create the initial document
doc = create_default_doc(prompt)
print(f"Initial document created with {len(doc['User_Request'].split('\\n'))} lines")
```

#### d. First Iteration
```python
# First iteration - Initial approach
print("\n\n--- ITERATION 1 ---\n\n")
updated_doc, response = step_work_on_doc(llm, doc)
print(f"Document updated with {len(updated_doc.keys())} sections")
print("\nResponse:\n", response)
```

#### e. Second Iteration
```python
# Second iteration - Continue the work
print("\n\n--- ITERATION 2 ---\n\n")
updated_doc2, response2 = step_work_on_doc(llm, updated_doc)
print(f"Document updated with {len(updated_doc2.keys())} sections")
print("\nResponse:\n", response2)
```

#### f. Third Iteration (optional)
```python
# Third iteration - Refine and complete
print("\n\n--- ITERATION 3 ---\n\n")
updated_doc3, response3 = step_work_on_doc(llm, updated_doc2)
print(f"Document updated with {len(updated_doc3.keys())} sections")
print("\nResponse:\n", response3)
```

#### g. Document Evolution Analysis
```python
# Review document evolution
history = get_doc_history()
history_length = get_history_length()
print(f"Document has {history_length} versions in its history")

# Compare sections across versions
if history_length >= 2:
    first_version = history[0]
    latest_version = history[-1]
    
    print("\nNew sections added during test:")
    for section in latest_version.keys():
        if section not in first_version:
            print(f"- {section}")
    
    # Print the final document structure
    print("\nFinal document sections:")
    for section, content in latest_version.items():
        print(f"- {section}: {len(content.split('\\n'))} lines")
```

### 4. Execute the Notebook

```bash
jupyter nbconvert --to notebook --execute test_<feature_name>.ipynb --output test_<feature_name>_executed.ipynb
```

### 5. Document Findings in IMPROVEMENT_SUGGESTIONS.md

After executing the notebook and analyzing the results, add a new test case to IMPROVEMENT_SUGGESTIONS.md following this template:

```markdown
## Test Case X: <Feature Name>

**User Query:** "<Exact query text used in the test>"

**Test Results Observations:**

1. **<Category of Observation>:**
   - <Specific observation 1>
   - <Specific observation 2>
   - <Specific observation 3>

2. **<Another Category>:**
   - <Specific observation 1>
   - <Specific observation 2>

3. **<Third Category>:**
   - <Specific observation 1>
   - <Specific observation 2>

**Improvement Opportunities:**

1. **<Improvement Name> (High Priority):**
   - <Detailed description of the issue>
   - <Potential impact>
   - <Suggested approach>

2. **<Another Improvement> (Medium Priority):**
   - <Detailed description>
   - <Potential solution>

3. **<Third Improvement> (Low Priority):**
   - <Detailed description>
   - <Potential solution>
```

### 6. Update Implementation Priorities

After adding the new test case, review and update the "Implementation Priorities" section at the end of IMPROVEMENT_SUGGESTIONS.md to reflect any new high-priority improvements identified.

### 7. Commit Changes to Git

```bash
git add IMPROVEMENT_SUGGESTIONS.md examples/test_<feature_name>.ipynb examples/test_<feature_name>_executed.ipynb
git commit -m "Add <feature_name> test case and update improvement suggestions"
```

## Example Test User Queries

When creating synthetic user queries, aim for requests that:
1. Exercise specific capabilities of the framework
2. Represent realistic use cases
3. Might expose limitations or edge cases

Here are some example queries by category:

### Knowledge Synthesis
- "Create a comparative analysis of three major machine learning frameworks (TensorFlow, PyTorch, and JAX), considering performance, ease of use, and community support."
- "Research and summarize the key developments in quantum computing from the last five years, organizing by hardware advances, algorithm developments, and practical applications."

### Creativity and Writing
- "Draft a creative short story about artificial intelligence, using the story structure of introduction, rising action, climax, falling action, and resolution."
- "Generate a comprehensive business plan for a hypothetical startup focusing on sustainable energy solutions."

### Complex Problem Solving
- "Solve the Tower of Hanoi puzzle with 5 disks using Python, explaining each step of your solution and the mathematical principles involved."
- "Implement the A* search algorithm to find the shortest path in a maze, with visualization of the search process and path found."

### Multi-Step Processing
- "Design a recommendation system for movies that combines collaborative filtering and content-based approaches. Implement a simplified version using Python."
- "Create a text summarization pipeline that extracts key information from a long document, using both extractive and abstractive techniques."

### Learning and Tutorial Generation
- "Create a step-by-step tutorial on implementing a simple neural network from scratch in Python, explaining each component and its purpose."
- "Generate an educational guide explaining how public key cryptography works, with code examples demonstrating RSA encryption and decryption."

## Criteria for Evaluating Test Results

When analyzing test results, look for:

1. **Functionality**: Did the system correctly handle the request?
2. **LLM Utilization**: How well did the LLM use the Renaissance framework?
3. **Document Evolution**: How did the document structure evolve over iterations?
4. **Error Handling**: How did the system handle errors or limitations?
5. **Code Quality**: What was the quality of code generated?
6. **Context Utilization**: Did the system effectively use its context?
7. **Adaptability**: Did the system adapt to challenges encountered?

## Best Practices

1. **Always use OpenAI (GPT-4-Turbo)** for all testing to ensure consistent results
2. **Never use mock LLM providers** as they return canned responses regardless of query
3. **Maintain consistent LLM versions** across test cases for reliable comparisons
4. **Document exact query text** used in the test
5. **Include screenshots** of notable UI issues or successes
6. **Run multiple iterations** to observe document evolution
7. **Be specific about improvements** rather than general suggestions
8. **Prioritize improvements** based on impact and implementation difficulty

## Appendix: Example Findings Documentation

Here's an example of how findings might be documented in IMPROVEMENT_SUGGESTIONS.md:

```markdown
## Test Case X: Multi-Step Data Processing

**User Query:** "Create a dataset of 100 random points in 2D space, cluster them using K-means with k=3, visualize the clusters, and analyze the cluster characteristics."

**Test Results Observations:**

1. **Code Execution:**
   - Successfully generated random data points
   - Implemented K-means algorithm correctly
   - Generated appropriate visualizations
   - Error handling was minimal when matplotlib failed

2. **Document Structure:**
   - Created well-organized sections (Data_Generation, Clustering, Visualization)
   - Table of contents accurately reflected document structure
   - Some sections became quite lengthy, making navigation difficult

3. **LLM Behavior:**
   - Properly utilized code execution tags
   - Created appropriate new sections
   - Occasionally referenced non-existent variables from previous cells
   - Made good use of the working memory section

**Improvement Opportunities:**

1. **Code Persistence (High Priority):**
   - Variables defined in one code block weren't available in subsequent blocks
   - Should implement a shared execution context that persists across iterations
   - Consider showing available variables to the LLM before each iteration

2. **Visualization Fallbacks (Medium Priority):**
   - When matplotlib visualization failed, no text-based alternative was provided
   - Should implement ASCII-based visualization fallbacks
   - Could add explicit error handlers for common visualization issues

3. **Section Length Management (Medium Priority):**
   - Some sections became very long, making navigation difficult
   - Could implement automatic subsection creation for lengthy sections
   - Consider adding collapsible sections or "Continue in new section" suggestions
```