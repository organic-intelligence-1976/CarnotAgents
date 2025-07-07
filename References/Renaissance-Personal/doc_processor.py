import io
import contextlib
import traceback
import re
import time
import json
import copy
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Tuple
from .config import (
    DEFAULT_GOAL,
    DEFAULT_DOC_STRUCTURE,
    DEFAULT_FORMATTING_OF_REQUESTS,
    CODE_EXECUTION_FORMAT,
    DEFAULT_SECTIONS
)

# Global execution context for Python code
_context = {}  

# Global storage for verbose content
_details_dict = {}

# Global storage for document history
_doc_history = []

# Initialize details_dict and helper functions in the execution context
_context['details_dict'] = _details_dict

# Make a copy of the global details_dict to avoid reference issues
def _update_context_details_dict():
    """Update the details_dict in the execution context to match the global version"""
    _context['details_dict'] = _details_dict

# Helper functions for content management
def store_section(section_name: str, content: str, summary: Optional[str] = None, 
                  tags: Optional[List[str]] = None) -> str:
    """
    Store verbose content with metadata and return reference key.
    
    Args:
        section_name (str): Name of the section being stored
        content (str): The verbose content to store
        summary (str, optional): A summary of the content
        tags (list, optional): List of tags for categorization
        
    Returns:
        str: The key used to reference this content
    """
    # Generate a unique key based on section name and timestamp
    timestamp = int(time.time())
    key = f"{section_name}_{timestamp}"
    
    # Store the content with metadata
    _details_dict[key] = {
        'content': content,
        'created': datetime.now().isoformat(),
        'summary': summary or f"Stored content for {section_name}",
        'tags': tags or [],
        'section_name': section_name
    }
    
    return key

def get_section(key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve section content and metadata.
    
    Args:
        key (str): The reference key for the stored content
        
    Returns:
        dict: The content and metadata, or None if not found
    """
    return _details_dict.get(key)

def get_section_content(key: str) -> str:
    """
    Retrieve just the content of a stored section.
    
    Args:
        key (str): The reference key for the stored content
        
    Returns:
        str: The content, or a message if not found
    """
    section = _details_dict.get(key)
    if section:
        return section['content']
    return f"Section {key} not found"

def list_sections(tag: Optional[str] = None, section_name: Optional[str] = None) -> Dict[str, str]:
    """
    List available sections, optionally filtered by tag or section name.
    
    Args:
        tag (str, optional): Filter by this tag
        section_name (str, optional): Filter by this section name
        
    Returns:
        dict: Dictionary of keys and their summaries
    """
    result = {}
    for key, data in _details_dict.items():
        # Apply filters if provided
        if tag and tag not in data.get('tags', []):
            continue
        if section_name and section_name != data.get('section_name'):
            continue
            
        result[key] = data.get('summary', 'No summary available')
    
    return result

# Document history management functions
def save_doc_history(doc: Dict[str, str]) -> None:
    """
    Save a snapshot of the document to the history.
    
    Args:
        doc (dict): The document to save in history
    """
    # Create a deep copy to ensure the history snapshot is independent
    _doc_history.append(copy.deepcopy(doc))

def get_doc_history(index: Optional[int] = None) -> Union[List[Dict[str, str]], Dict[str, str]]:
    """
    Get document history, either complete or at a specific index.
    
    Args:
        index (int, optional): Specific history point to retrieve (zero-indexed)
        
    Returns:
        Either the complete history list or a specific document snapshot
    """
    if index is not None:
        if 0 <= index < len(_doc_history):
            return _doc_history[index]
        return {}
    return _doc_history

def get_history_length() -> int:
    """
    Get the number of document versions in history.
    
    Returns:
        int: The length of document history
    """
    return len(_doc_history)

def clear_doc_history() -> None:
    """Clear the document history."""
    _doc_history.clear()

def generate_table_of_contents(doc: Dict[str, str]) -> str:
    """
    Generate a table of contents from the document sections.
    
    Args:
        doc (dict): The document dictionary with sections
        
    Returns:
        str: Formatted table of contents
    """
    # Filter out system sections that shouldn't appear in TOC
    system_sections = {'Goal', 'Doc_Structure', 'User_Request', 'Formatting_of_Requests'}
    
    sections = []
    for section in doc.keys():
        if section not in system_sections:
            # Get the first line or a portion to use as a summary
            content = doc[section]
            summary = content.split('\n')[0][:50]
            if len(summary) < len(content.split('\n')[0]):
                summary += "..."
            
            sections.append(f"- **{section}**: {summary}")
    
    if not sections:
        return "No content sections available yet."
    
    return "## Table of Contents\n\n" + "\n".join(sections)

# Add helper functions to execution context
_context['store_section'] = store_section
_context['get_section'] = get_section
_context['get_section_content'] = get_section_content
_context['list_sections'] = list_sections
_context['get_doc_history'] = get_doc_history
_context['get_history_length'] = get_history_length
_context['generate_table_of_contents'] = generate_table_of_contents

def install_package(package_name: str, extra_args: str = "") -> str:
    """
    Install a Python package using pip.
    
    Args:
        package_name (str): Name of the package to install
        extra_args (str): Additional pip arguments (e.g., "--upgrade", "--no-cache-dir")
        
    Returns:
        str: Output from pip installation
    
    Note: This function runs pip as a subprocess and captures its output.
    It's safer than using os.system() and allows for proper error handling.
    """
    # Basic security check - prevent command injection
    if not re.match(r'^[a-zA-Z0-9\._\-=<>]+$', package_name):
        return f"Error: Invalid package name '{package_name}'. Package names should only contain letters, numbers, dots, underscores, and hyphens."
    
    if extra_args and not re.match(r'^[a-zA-Z0-9\._\-= ]+$', extra_args):
        return f"Error: Invalid extra arguments '{extra_args}'. Only simple options are allowed."
    
    # Construct the command
    pip_command = [sys.executable, "-m", "pip", "install", package_name]
    
    # Add any extra arguments
    if extra_args:
        pip_command.extend(extra_args.split())
    
    try:
        # Run the pip installation
        process = subprocess.run(
            pip_command,
            capture_output=True,
            text=True,
            check=False  # Don't raise an exception on non-zero return codes
        )
        
        # Return the combined output
        output = process.stdout
        if process.stderr:
            output += "\n" + process.stderr
            
        return output
    except Exception as e:
        return f"Error: Failed to run pip install. {str(e)}"


def execute_code(code_string, provided_vars=None):
    """
    Executes the given code_string in a shared context, optionally
    updated with provided_vars. Returns the stdout and/or traceback.
    
    Args:
        code_string (str): Python code to execute
        provided_vars (dict, optional): Variables to add to execution context
        
    Returns:
        str: Output from code execution or error traceback
    """
    global _context
    if provided_vars is not None:
        _context.update(provided_vars)
    
    # Ensure the details_dict is up to date
    _update_context_details_dict()
    
    # Add the install_package function to the execution context
    _context['install_package'] = install_package

    output_buffer = io.StringIO()
    with contextlib.redirect_stdout(output_buffer):
        try:
            exec(code_string, _context)
        except Exception as e:
            error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            output_buffer.write(error_message)

    return output_buffer.getvalue()


def process_llm_response(doc, response, provided_vars=None):
    """
    Processes the LLM's response by extracting and executing tagged actions.
    
    Args:
        doc (dict): Document dictionary with sections
        response (str): LLM response containing tagged actions
        provided_vars (dict, optional): Variables to provide to code execution
        
    Returns:
        dict: Updated document
    """
    def extract_tag_content(tag, text):
        pattern = f"<{tag}.*?>(.*?)</{tag}>"
        return re.findall(pattern, text, re.DOTALL)

    # 1. Execute Python code and organize results
    for code in extract_tag_content("execute", response):
        result = execute_code(code, provided_vars)
        
        # Format the code and results using the template from config
        execution_record = CODE_EXECUTION_FORMAT.format(code=code, result=result)
        # Add to working memory and also create/update a dedicated section
        doc["Working_Memory"] = doc.get("Working_Memory", "") + f"\n{execution_record}"
        
        # # Create or update a Code_Execution_Results section for more visibility
        # if "Code_Execution_Results" in doc:
        #     doc["Code_Execution_Results"] += f"\n\n{execution_record}"
        # else:
        #     doc["Code_Execution_Results"] = execution_record

    # 2. Update existing sections
    update_pattern = r'<update_section\s+name="([^"]+)">(.*?)</update_section>'
    for section_name, content in re.findall(update_pattern, response, re.DOTALL):
        doc[section_name] = content.strip()

    # 3. Append to existing sections
    append_pattern = r'<append_section\s+name="([^"]+)">(.*?)</append_section>'
    for section_name, content in re.findall(append_pattern, response, re.DOTALL):
        doc[section_name] = doc.get(section_name, "") + "\n" + content.strip()

    # 4. Create (or append to) new sections
    new_pattern = r'<new_section\s+name="([^"]+)">(.*?)</new_section>'
    for section_name, content in re.findall(new_pattern, response, re.DOTALL):
        if section_name in doc:
            doc[section_name] += "\n" + content.strip()
        else:
            doc[section_name] = content.strip()

    # 5. Delete sections
    for section in extract_tag_content("delete_section", response):
        doc.pop(section.strip(), None)

    # 6. Check for completion
    status_updates = extract_tag_content("status", response)
    if status_updates and status_updates[-1].strip() == "done":
        doc["Status"] = "done"

    return doc


def to_text_form(doc):
    """
    Converts a Doc (dict) into a structured text representation using XML-like tags.
    
    Args:
        doc (dict): Document dictionary with sections
        
    Returns:
        str: Text form of document with XML-like tags
    """
    def sanitize_section_name(name):
        return name.replace(" ", "_")

    sections_text = []
    for section_name, content in doc.items():
        tag_name = sanitize_section_name(section_name)
        sections_text.append(f"<{tag_name}>\n{content}\n</{tag_name}>")

    return "\n\n".join(sections_text)


def step_work_on_doc(llm_obj, doc, provided_vars=None, config=None, add_toc=True):
    """
    Sends the doc text to the LLM, processes the response, and returns
    both the updated doc and the raw response.
    
    Args:
        llm_obj: LLM object with invoke method
        doc (dict): Document dictionary with sections
        provided_vars (dict, optional): Variables to provide to code execution
        config (dict, optional): Configuration object to use for this step.
                                If provided, overrides global config for this step.
        add_toc (bool): Whether to add a table of contents to the document
        
    Returns:
        tuple: (updated document, raw LLM response)
    """
    # Make copies to avoid side effects
    doc_copy = doc.copy()
    local_config = {}
    
    # Add a table of contents if requested
    if add_toc:
        toc = generate_table_of_contents(doc_copy)
        doc_copy["Table_of_Contents"] = toc
    
    # Save the pre-update document to history
    save_doc_history(doc_copy)
    
    # If config provided, use it for this step
    if config:
        from .config import current_config
        # Create a temporary copy of the global config
        local_config = current_config.copy()
        # Temporarily update config for this step only
        from .config import update_config
        update_config(config)
        
    # Convert document to text format
    doc_text_form = to_text_form(doc_copy)
    
    # Get LLM response
    response = llm_obj.invoke(doc_text_form).content
    
    # Process response
    updated_doc = process_llm_response(doc_copy, response, provided_vars)
    
    # Update table of contents after changes
    if add_toc:
        updated_doc["Table_of_Contents"] = generate_table_of_contents(updated_doc)
    
    # Restore original config if we temporarily changed it
    if config and local_config:
        from .config import update_config
        # Reset to the previous configuration
        update_config(local_config)
        
    return updated_doc, response


def create_default_doc(user_request, config=None):
    """
    Construct a doc dictionary with all the sections needed.
    
    Args:
        user_request (str): The user's query or task
        config (dict, optional): Custom configuration to use for document creation
        
    Returns:
        dict: Document dictionary with default sections
    """
    # Use default config values
    goal = DEFAULT_GOAL
    doc_structure = DEFAULT_DOC_STRUCTURE
    formatting = DEFAULT_FORMATTING_OF_REQUESTS
    
    # Override with custom config if provided
    if config:
        goal = config.get("goal", DEFAULT_GOAL)
        doc_structure = config.get("doc_structure", DEFAULT_DOC_STRUCTURE)
        formatting = config.get("formatting", DEFAULT_FORMATTING_OF_REQUESTS)
    
    doc = {
        "Goal": goal,
        "Doc_Structure": doc_structure,
        "User_Request": user_request,
        "Formatting_of_Requests": formatting,
        "Previous_Analysis_Summary": "",
        "Working_Memory": "",
        "Findings": "",
        "Status": "in_progress"
    }
    return doc


def run_with_history(llm_obj, user_request, config=None, iterations=5):
    """
    Run Renaissance for multiple iterations and capture the complete history.
    
    Args:
        llm_obj: LLM provider instance to use
        user_request (str): The user's query or task
        config (dict, optional): Custom configuration to use
        iterations (int): Number of iterations to run (default: 5)
        
    Returns:
        dict: A structured dictionary containing the complete history:
            - request: Original user request
            - config: Configuration used
            - iterations: List of iteration records with before/after states
            - final_document: Final document state
            - stats: Execution statistics
    """
    import time
    import copy
    
    # Clear existing history to avoid contamination
    clear_doc_history()
    
    # Create a new document with the user request
    doc = create_default_doc(user_request, config)
    
    # Track total execution time and token usage
    start_time = time.time()
    iteration_records = []
    
    # Run the requested number of iterations
    for i in range(iterations):
        iteration_start = time.time()
        
        # Store document state before the step
        doc_before = copy.deepcopy(doc)
        
        # Run a single step
        doc, raw_response = step_work_on_doc(llm_obj, doc, config=config)
        
        # Identify changes between iterations
        changes = []
        for section in set(list(doc.keys()) + list(doc_before.keys())):
            if section not in doc_before:
                changes.append(f"Added section: {section}")
            elif section not in doc:
                changes.append(f"Removed section: {section}")
            elif doc[section] != doc_before[section]:
                changes.append(f"Modified section: {section}")
        
        # Record this iteration
        iteration_records.append({
            "step": i + 1,
            "document_before": doc_before,
            "document_after": copy.deepcopy(doc),
            "raw_llm_output": raw_response,
            "changes": changes,
            "time_taken": time.time() - iteration_start
        })
        
        # Stop if the document is marked as done
        if doc.get("Status") == "done":
            break
    
    # Calculate stats
    total_time = time.time() - start_time
    
    # Assemble the result object
    result = {
        "request": user_request,
        "config": config,
        "iterations": iteration_records,
        "final_document": doc,
        "stats": {
            "total_time": total_time,
            "iterations_completed": len(iteration_records),
            "early_finish": doc.get("Status") == "done"
        }
    }
    
    return result