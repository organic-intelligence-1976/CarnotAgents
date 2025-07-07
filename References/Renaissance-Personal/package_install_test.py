#!/usr/bin/env python3
"""
Renaissance Package Installation Test

This script demonstrates how to install packages during Renaissance execution.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from renaissance import (
    create_default_doc,
    step_work_on_doc,
    get_llm_provider,
    load_config_from_file
)

# Set up a simple test
print("Renaissance Package Installation Test")
print("===================================\n")

# Get LLM provider (use mock for testing)
llm = get_llm_provider("mock")

# Create a document with a request that requires package installation
user_request = """
Please analyze a small dataset with pandas and matplotlib:
1. Create a sample dataset
2. Calculate basic statistics
3. Generate a visualization
"""

# Load configuration
config = load_config_from_file("configs/autonomous_research.json")

# Create the document
doc = create_default_doc(user_request, config)

# Update TaskQueue section to include package installation
doc["TaskQueue"] = """
## In Progress
- [ ] Install required packages (pandas, matplotlib)
- [ ] Create sample dataset
- [ ] Calculate statistics
- [ ] Generate visualization

## Backlog
- [ ] Save results to file
"""

print("Initial document created.")
print("Running first iteration to test package installation...\n")

# Run the first iteration
updated_doc, raw_response = step_work_on_doc(llm, doc)

# Print the results
print("Task Queue after execution:")
print("==========================")
if "TaskQueue" in updated_doc:
    print(updated_doc["TaskQueue"])
else:
    print("TaskQueue section not found.")

print("\nWorking Memory after execution:")
print("==============================")
if "WorkingMemory" in updated_doc:
    print(updated_doc["WorkingMemory"][:500] + "..." if len(updated_doc["WorkingMemory"]) > 500 else updated_doc["WorkingMemory"])
else:
    print("WorkingMemory section not found.")

print("\nTest completed. Check the output above to verify that the LLM was able to use the install_package() function.")