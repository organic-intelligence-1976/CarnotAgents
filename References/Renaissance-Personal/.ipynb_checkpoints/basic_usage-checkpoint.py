#!/usr/bin/env python3
"""
Renaissance Basic Usage Demo

This script demonstrates the basic functionality of Renaissance in a simple Python script.
It shows how to:
1. Set up Renaissance with an LLM provider
2. Create a document with a user request
3. Run multiple iterations to solve a problem
4. Analyze the results
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from renaissance import (
    create_default_doc,
    step_work_on_doc,
    run_with_history,
    get_llm_provider,
    load_config_from_file
)

def simple_iteration_demo():
    """Demo of basic step-by-step iteration."""
    print("\n== BASIC ITERATION DEMO ==\n")
    
    # Set up LLM provider (use a real provider for actual testing)
    print("Setting up LLM provider...")
    llm = get_llm_provider("mock")  # For demo only, use "openai" or "claude" for real use
    
    # Create document with user request
    user_request = "Calculate the sum of all even numbers between 1 and 100."
    print(f"User request: {user_request}")
    
    # Load default configuration
    config = load_config_from_file("configs/default.json")
    doc = create_default_doc(user_request, config)
    
    # Run iterations
    max_iterations = 3
    print(f"\nRunning {max_iterations} iterations...")
    
    for i in range(max_iterations):
        print(f"\nIteration {i+1}:")
        doc, response = step_work_on_doc(llm, doc)
        
        # Check for section changes
        print("Sections:")
        for section in doc.keys():
            if section not in ["Goal", "Doc_Structure", "User_Request", "Formatting_of_Requests", "Table_of_Contents"]:
                content_preview = doc[section][:50] + "..." if len(doc[section]) > 50 else doc[section]
                print(f"  - {section}: {content_preview}")
        
        # Check if done
        if doc.get("Status") == "done":
            print("\nTask completed!")
            break
    
    # Show findings
    if "Findings" in doc:
        print("\nFindings:")
        print(doc["Findings"])

def history_tracking_demo():
    """Demo of comprehensive history tracking with run_with_history."""
    print("\n== HISTORY TRACKING DEMO ==\n")
    
    # Set up LLM provider (use a real provider for actual testing)
    print("Setting up LLM provider...")
    llm = get_llm_provider("mock")  # For demo only, use "openai" or "claude" for real use
    
    # Define user request
    user_request = "List the first 5 Fibonacci numbers."
    print(f"User request: {user_request}")
    
    # Load configuration
    config = load_config_from_file("configs/default.json")
    
    # Run with history tracking
    print("\nRunning with history tracking...")
    result = run_with_history(
        llm_obj=llm,
        user_request=user_request,
        config=config,
        iterations=3
    )
    
    # Display statistics
    print(f"\nStatistics:")
    print(f"- Total execution time: {result['stats']['total_time']:.2f} seconds")
    print(f"- Iterations completed: {result['stats']['iterations_completed']}")
    print(f"- Early finish: {result['stats']['early_finish']}")
    
    # Show changes per iteration
    print("\nChanges per iteration:")
    for i, iteration in enumerate(result['iterations']):
        print(f"Iteration {i+1}:")
        for change in iteration['changes']:
            print(f"  - {change}")
    
    # Show final document sections
    print("\nFinal document sections:")
    for section, content in result['final_document'].items():
        if section not in ["Goal", "Doc_Structure", "User_Request", "Formatting_of_Requests", "Table_of_Contents"]:
            print(f"- {section}: {len(content)} characters")
    
    # Show findings
    if "Findings" in result['final_document']:
        print("\nFindings:")
        print(result['final_document']['Findings'])

if __name__ == "__main__":
    print("Renaissance Basic Usage Demo")
    print("===========================\n")
    
    # Run the demos
    simple_iteration_demo()
    history_tracking_demo()
    
    print("\nDemos completed!")