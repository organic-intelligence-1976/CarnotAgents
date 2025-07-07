"""
Configuration module for Renaissance, containing all prompts and settings.

This centralized configuration allows for easy experimentation with different
prompt variations and system behaviors.
"""

import os
import json
import yaml
from typing import Dict, Any

# Default system prompt for LLM providers
DEFAULT_SYSTEM_PROMPT = """You are part of a research team helping users solve problem. You receive a document/dossier that includes the user request and other sections that shows the work of other reseaechers on your team that have worked on this project. Each researcher puts his or her thoughts, insights, plans,.... in various sections of the document. There is no restriction on what sections can be created by researchers. Each of you, researchers, receives the project document in an incomplete form, reads its sections and tries to use all the available info to move the project forward by modifying the document.

So, this is NOT a one-shot response. You are working on a document that evolves over multiple turns, like a car moving through stations on an assembly line. Each time you receive the document, you should make incremental progress and request specific actions by having your response include xml tags (details below). Most actions you can request are to modify and update the document with your new thoughts and insights and plans. One distinguished request is execution of a piece of python code. As explained below, anytime you want to ask a piece of code to be executed, include a section with the tag "execute" and the content of the xml section being the code you want executed. After you give your response with various xml tags, an assistant separately will implement your requests and updates the document accordingly. For example any code which you or another researcher puts in a <execute> tag will be picked up and executed and whatever it prints will be added as the "result" along with the code that was requested in a section of the updated document.

When you request code execution or add thoughts/plans, another process will implement those and return the updated document to you for the next step. You don't need to provide a complete solution at once.

CRITICAL INSTRUCTION: You MUST use THESE EXACT tags in your response:

1. For requesting Python code execution (focus on what you need to know):
<execute>
your_python_code_here
</execute>

2. For creating new document sections (any section name you need):
<new_section name="Plan">
planning content here
</new_section>

3. For adding to existing sections (e.g. Findings):
<append_section name="Findings">
additional content to add
</append_section>

4. For replacing existing sections:
<update_section name="SectionName">
new content that replaces old content
</update_section>

5. For removing sections:
<delete_section>SectionName</delete_section>

6. For marking completion:
<status>done</status>

EXAMPLES OF GOOD ITERATIVE RESPONSES:

Example 1 (requesting information):
I need to understand the data distribution first.

<execute>
import pandas as pd
import numpy as np

# Generate sample data
data = np.random.normal(0, 1, 1000)
print(f"Mean: {data.mean()}")
print(f"Std dev: {data.std()}")
</execute>

<new_section name="Plan">
1. Generate and analyze sample data distribution
2. After seeing the results, determine appropriate modeling approach
3. Implement and test the model
</new_section>

Example 2 (after receiving execution results):
Now that I see the data is normally distributed, I'll implement a parametric approach.

<execute>
from scipy import stats
# Calculate confidence interval
confidence = 0.95
n = len(data)
mean = np.mean(data)
std_err = stats.sem(data)
interval = stats.t.interval(confidence, n-1, mean, std_err)
print(f"95% confidence interval: {interval}")
</execute>

<append_section name="Findings">
- The data appears to be normally distributed
- The next step is to calculate confidence intervals
</append_section>

YOUR RESPONSE MUST USE THESE TAGS.
"""

# Goal description for the document
DEFAULT_GOAL = """
  You are a research assistant working on an iterative, multi-turn document. Your goal is to make incremental progress on the problem described in the User Request section.
  
  IMPORTANT: This is NOT a one-shot task. You are part of an assembly line process where:
  1. You suggest a step (like running code or adding analysis)
  2. The system implements that step (executes code and shows results)
  3. You receive the updated document and suggest the next step

  You are expected to:
  1. Read the existing doc carefully, especially any code execution results
  2. Request execution of Python code when you need information
  3. Add planning sections to outline your approach
  4. Add findings and insights as you make progress
  5. Focus on one step at a time - don't try to solve everything at once
  
  Each time you see this document, it will contain the results of your previous requests. Build on these iteratively.
"""

# Document structure explanation
DEFAULT_DOC_STRUCTURE = """
  As you can see, this document is structured using XML tags. Each section is wrapped in tags matching its name. For example, a Doc with sections "Instructions" and "User Request" becomes:
      <Instructions>
      ...content...
      </Instructions>
      <User_Request>
      ...content...
      </User_Request>
"""

# Instructions on how to format requests
DEFAULT_FORMATTING_OF_REQUESTS = """
In order to make progress on the task iteratively, you can take the following kinds of actions:

1. Request Python code execution to gather information or perform analysis
2. Create/update document sections to record your thoughts, plans, and findings
3. Mark the document as complete when you've solved the problem

IMPORTANT: This is a multi-turn process. Each time you suggest an action, the system will implement it,
and then return the updated document to you. You should focus on ONE STEP AT A TIME.

Structure your response using these tags:

To request Python code execution (focus on what you need to learn next):
<execute>
your_python_code_here
</execute>

To create a new section (for plans, approaches, or any topic you need):
<new_section name="Plan">
section_content
</new_section>

To append to an existing section:
<append_section name="Findings">
new_content_to_add
</append_section>

To replace an existing section (use sparingly):
<update_section name="SectionName">
new_content_here
</update_section>

To delete a section:
<delete_section>section_name</delete_section>

To mark the problem as solved:
<status>done</status>

EXAMPLES OF GOOD RESPONSES:

Example 1 (first step - planning and code execution):
I'll start by exploring the data to understand its structure.

<new_section name="Plan">
1. Examine the data structure
2. Analyze distributions of key variables
3. Identify correlations between features
4. Develop and test a predictive model
</new_section>

<execute>
# Load and inspect the data
import pandas as pd
import numpy as np

# Generate sample data to explore
df = pd.DataFrame({
    'feature1': np.random.normal(0, 1, 100),
    'feature2': np.random.normal(5, 2, 100)
})
print(df.describe())
</execute>

Example 2 (after seeing code results):
Now that I see the statistical properties of our features, let's visualize them.

<execute>
import matplotlib.pyplot as plt
plt.scatter(df['feature1'], df['feature2'])
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('Feature Relationship')
plt.show()
</execute>

Remember to focus on ONE STEP AT A TIME in this iterative process.
"""

# Default settings for the LLM providers
DEFAULT_LLM_SETTINGS = {
    "openai": {
        "model": "gpt-4-turbo"
    },
    "anthropic": {
        "model": "claude-3-opus-20240229",
        "max_tokens": 4096
    },
    "google": {
        "model": "gemini-pro"
    },
    "mock": {}
}

# Code execution result formatting
CODE_EXECUTION_FORMAT = """## Code Execution Result

### Executed Code:
```python
{code}
```

### Output:
```
{result}
```
"""

# Default document sections
DEFAULT_SECTIONS = [
    "Goal",
    "Doc_Structure", 
    "User_Request",
    "Formatting_of_Requests",
    "Previous_Analysis_Summary",
    "Working_Memory",
    "Findings",
    "Status"
]

# Store the current configuration for easy access
current_config = {
    "system_prompt": DEFAULT_SYSTEM_PROMPT,
    "goal": DEFAULT_GOAL,
    "doc_structure": DEFAULT_DOC_STRUCTURE,
    "formatting": DEFAULT_FORMATTING_OF_REQUESTS,
    "code_execution_format": CODE_EXECUTION_FORMAT,
    "llm_settings": DEFAULT_LLM_SETTINGS,
    "sections": DEFAULT_SECTIONS
}

def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON or YAML file.
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        dict: The loaded configuration
    
    Raises:
        ValueError: If the file format is not supported
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    _, ext = os.path.splitext(config_path)
    ext = ext.lower()
    
    if ext == '.json':
        with open(config_path, 'r') as f:
            config = json.load(f)
    elif ext in ['.yaml', '.yml']:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported config file format: {ext}")
    
    return config

def update_config(new_config: Dict[str, Any]) -> None:
    """
    Update the current configuration with new values.
    
    Args:
        new_config (dict): New configuration values
    """
    global DEFAULT_SYSTEM_PROMPT, DEFAULT_GOAL, DEFAULT_DOC_STRUCTURE
    global DEFAULT_FORMATTING_OF_REQUESTS, CODE_EXECUTION_FORMAT
    global DEFAULT_LLM_SETTINGS, DEFAULT_SECTIONS, current_config
    
    # Update global variables if provided in the new config
    if "system_prompt" in new_config:
        DEFAULT_SYSTEM_PROMPT = new_config["system_prompt"]
        current_config["system_prompt"] = DEFAULT_SYSTEM_PROMPT
        
    if "goal" in new_config:
        DEFAULT_GOAL = new_config["goal"]
        current_config["goal"] = DEFAULT_GOAL
        
    if "doc_structure" in new_config:
        DEFAULT_DOC_STRUCTURE = new_config["doc_structure"]
        current_config["doc_structure"] = DEFAULT_DOC_STRUCTURE
        
    if "formatting" in new_config:
        DEFAULT_FORMATTING_OF_REQUESTS = new_config["formatting"]
        current_config["formatting"] = DEFAULT_FORMATTING_OF_REQUESTS
        
    if "code_execution_format" in new_config:
        CODE_EXECUTION_FORMAT = new_config["code_execution_format"]
        current_config["code_execution_format"] = CODE_EXECUTION_FORMAT
        
    if "llm_settings" in new_config:
        DEFAULT_LLM_SETTINGS.update(new_config["llm_settings"])
        current_config["llm_settings"] = DEFAULT_LLM_SETTINGS
        
    if "sections" in new_config:
        DEFAULT_SECTIONS = new_config["sections"]
        current_config["sections"] = DEFAULT_SECTIONS

def export_current_config(config_path: str, format: str = 'json') -> None:
    """
    Export the current configuration to a file.
    
    Args:
        config_path (str): Path to save the configuration
        format (str): Format to use ('json' or 'yaml')
    
    Raises:
        ValueError: If the format is not supported
    """
    if format.lower() == 'json':
        with open(config_path, 'w') as f:
            json.dump(current_config, f, indent=2)
    elif format.lower() == 'yaml':
        with open(config_path, 'w') as f:
            yaml.dump(current_config, f, default_flow_style=False)
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'json' or 'yaml'.")