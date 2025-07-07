"""
Renaissance Wiki Search Example

This example demonstrates how to use Renaissance to look up information on Wikipedia
and save it to a local file.
"""

import os
import sys
# Add the repository root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from renaissance import get_llm_provider, create_default_doc, step_work_on_doc
from renaissance.config import load_config_from_file

# Set your API key
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"
# or: os.environ["CLAUDE_API_KEY"] = "your-api-key-here"

def run_wiki_search_example():
    """Run the Wikipedia search and file save example."""
    
    # Load the coding-oriented configuration (better for file I/O)
    # Get the absolute path to the config file
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    config_path = os.path.join(project_root, "configs", "coding_oriented.json")
    print(f"Loading config from: {config_path}")
    config = load_config_from_file(config_path)
    
    # Initialize LLM provider
    # You can change this to your preferred provider
    llm = get_llm_provider("openai", model="gpt-4-turbo")
    
    # Create a document with our query
    query = "look up category theory in wikipedia and save it to a local file called cat.txt"
    doc = create_default_doc(query, config=config)
    
    print(f"Initial document created for query: {query}")
    
    # Run 3 iterations
    for i in range(3):
        print(f"\nRunning iteration {i+1}...")
        doc, _ = step_work_on_doc(llm, doc, config=config)
        print(f"Completed iteration {i+1}")
    
    # Check if the file was created
    file_path = "cat.txt"
    if os.path.exists(file_path):
        print(f"\nSuccess! File {file_path} was created.")
        
        # Print the first few lines
        with open(file_path, "r") as f:
            content = f.read(200)  # First 200 characters
        print(f"\nFile content preview:\n{content}...")
    else:
        print(f"\nFile {file_path} was not created.")
    
    print("\nRelevant document sections:")
    for section in ["Approach", "Implementation", "Findings"]:
        if section in doc:
            print(f"\n--- {section} ---")
            print(doc[section])
    
    return doc

if __name__ == "__main__":
    print("Starting Renaissance Wikipedia search example...\n")
    run_wiki_search_example()
    print("\nExample completed!")