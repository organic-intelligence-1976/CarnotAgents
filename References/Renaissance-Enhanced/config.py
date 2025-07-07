"""
Configuration module for Renaissance, containing all prompts and settings.

This centralized configuration allows for easy experimentation with different
prompt variations and system behaviors. Default configuration is loaded from
the 'configs/default.json' file.
"""

import os
import json
import yaml
import logging
from typing import Dict, Any
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration values - these will be overridden by the JSON file if available
# but are kept as fallbacks in case the JSON file can't be loaded
DEFAULT_SYSTEM_PROMPT = "You are a research assistant helping solve problems through an iterative process."
DEFAULT_GOAL = "Your goal is to make incremental progress on the problem."
DEFAULT_DOC_STRUCTURE = "This document is structured using XML tags."
DEFAULT_FORMATTING_OF_REQUESTS = "Use tags like <execute>, <new_section>, etc. to interact with the document."
DEFAULT_LLM_SETTINGS = {
    "openai": {"model": "gpt-4-turbo"},
    "anthropic": {"model": "claude-3-opus-20240229", "max_tokens": 4096},
    "google": {"model": "gemini-pro"},
    "mock": {}
}
CODE_EXECUTION_FORMAT = """## Code Execution Result\n\n### Executed Code:\n```python\n{code}\n```\n\n### Output:\n```\n{result}\n```\n"""
DEFAULT_SECTIONS = [
    "Goal", "Doc_Structure", "User_Request", "Formatting_of_Requests",
    "Previous_Analysis_Summary", "Working_Memory", "Findings", "Status"
]

# Initialize current configuration with default values
current_config = {
    "system_prompt": DEFAULT_SYSTEM_PROMPT,
    "goal": DEFAULT_GOAL,
    "doc_structure": DEFAULT_DOC_STRUCTURE,
    "formatting": DEFAULT_FORMATTING_OF_REQUESTS,
    "code_execution_format": CODE_EXECUTION_FORMAT,
    "llm_settings": DEFAULT_LLM_SETTINGS,
    "sections": DEFAULT_SECTIONS
}

# Try to load the default configuration from JSON file
try:
    # Calculate the path to the default config file based on the location of this module
    module_dir = Path(__file__).resolve().parent.parent
    default_config_path = module_dir / "configs" / "default.json"
    
    if default_config_path.exists():
        with open(default_config_path, 'r') as f:
            loaded_config = json.load(f)
            
        # Update the current configuration with the loaded values
        current_config.update(loaded_config)
        
        # Update the module-level variables for backward compatibility
        DEFAULT_SYSTEM_PROMPT = current_config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
        DEFAULT_GOAL = current_config.get("goal", DEFAULT_GOAL)
        DEFAULT_DOC_STRUCTURE = current_config.get("doc_structure", DEFAULT_DOC_STRUCTURE)
        DEFAULT_FORMATTING_OF_REQUESTS = current_config.get("formatting", DEFAULT_FORMATTING_OF_REQUESTS)
        CODE_EXECUTION_FORMAT = current_config.get("code_execution_format", CODE_EXECUTION_FORMAT)
        DEFAULT_LLM_SETTINGS.update(current_config.get("llm_settings", {}))
        DEFAULT_SECTIONS = current_config.get("sections", DEFAULT_SECTIONS)
        
        logger.info(f"Loaded default configuration from {default_config_path}")
    else:
        logger.warning(f"Default configuration file not found at {default_config_path}. Using hardcoded defaults.")
except Exception as e:
    logger.warning(f"Error loading default configuration: {e}. Using hardcoded defaults.")

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
    
    # Update both the module-level variables and the current_config dictionary
    for key, value in new_config.items():
        if key in current_config:
            current_config[key] = value
            
            # Also update the corresponding module variable for backward compatibility
            if key == "system_prompt":
                DEFAULT_SYSTEM_PROMPT = value
            elif key == "goal":
                DEFAULT_GOAL = value
            elif key == "doc_structure":
                DEFAULT_DOC_STRUCTURE = value
            elif key == "formatting":
                DEFAULT_FORMATTING_OF_REQUESTS = value
            elif key == "code_execution_format":
                CODE_EXECUTION_FORMAT = value
            elif key == "sections":
                DEFAULT_SECTIONS = value
            elif key == "llm_settings" and isinstance(value, dict):
                DEFAULT_LLM_SETTINGS.update(value)

def export_current_config(config_path: str = None, format: str = 'json') -> None:
    """
    Export the current configuration to a file.
    
    Args:
        config_path (str, optional): Path to save the configuration. If None, updates the default.json file.
        format (str): Format to use ('json' or 'yaml')
    
    Raises:
        ValueError: If the format is not supported
    """
    # If no config_path is provided, update the default config file
    if config_path is None:
        module_dir = Path(__file__).resolve().parent.parent
        config_path = module_dir / "configs" / "default.json"
        format = 'json'  # Force JSON format for default config
        
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    
    if format.lower() == 'json':
        with open(config_path, 'w') as f:
            json.dump(current_config, f, indent=2)
        logger.info(f"Configuration exported to {config_path}")
    elif format.lower() == 'yaml':
        with open(config_path, 'w') as f:
            yaml.dump(current_config, f, default_flow_style=False)
        logger.info(f"Configuration exported to {config_path}")
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'json' or 'yaml'.")