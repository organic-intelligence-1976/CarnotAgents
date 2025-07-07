
import io
import contextlib
import traceback
import re

# Core system capabilities and interaction protocol
doc_structure = """
This document maintains the complete state of our task. It contains sections that track our goals, progress, findings, and work memory.
Each section is marked with XML-style tags: <section_name>content</section_name>
"""

formatting_of_requests = """
You can request the following actions by including them in your response:

1. Execute Python code:
   <execute>
   print("Hello World")
   </execute>

2. Update a section:
   <update_section name="Section Name">
   New content replacing old content
   </update_section>

3. Append to a section:
   <append_section name="Section Name">
   Content to add to existing content
   </append_section>

4. Create new section:
   <new_section name="New Section">
   Content for new section
   </new_section>

5. Delete a section:
   <delete_section>Section Name</delete_section>

6. Mark task completion:
   <status>done</status>

All execution results will be automatically added to Working Memory.
"""

def create_init_doc(user_request):
    return {
        "Goal": f"Understanding and fulfilling the user request in the section User_Request below.",
        "Doc Structure": doc_structure,
        "User Request": user_request,
        "Formatting of Requests": formatting_of_requests,
        "Working Memory": "No computations performed yet.",
        "Plan": "Initial analysis of the request pending...",
        "Findings": "Investigation in progress. No findings to report yet.",
        "Status": "in_progress"
    }


# This module implements a system for LLM orchestration that follows the "living document" 
# paradigm. The core idea is to maintain a central state (document) that contains everything
# known about the project, allowing the LLM to iteratively improve and build upon it.



# Global execution context for Python code execution
# This allows maintaining state between different code executions
_context = {}  

def execute_code(code_string, provided_vars=None):
    """
    Executes Python code in a shared context and captures its output.
    
    This function is crucial for the system's universality - it gives the LLM the ability
    to actually execute code and not just generate text. This makes the system Turing-complete
    in practice, not just in theory.
    
    Args:
        code_string (str): The Python code to execute
        provided_vars (dict, optional): Variables to inject into execution context
    
    Returns:
        str: The captured stdout and/or traceback from code execution
    
    Design Notes:
        - Uses a global _context to maintain state between executions
        - Captures both stdout and errors, making debugging easier
        - Could be extended to handle different execution environments or languages
    """
    global _context
    if provided_vars is not None:
        _context.update(provided_vars)

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
    
    This function implements the core interaction loop between the LLM and the document.
    It parses XML-like tags in the LLM's response and performs corresponding actions
    to modify the document state.
    
    Key Features:
        - Executes embedded Python code
        - Updates document sections
        - Appends to existing sections
        - Creates new sections
        - Deletes sections
        - Tracks completion status
    
    Potential Improvements:
        - Could be extended to support hierarchical document structure
        - Could add support for parallel processing of sections
        - Could implement a mechanism for the LLM to request specific section details
    
    Args:
        doc (dict): The current document state
        response (str): The LLM's response containing tagged actions
        provided_vars (dict, optional): Variables for code execution context
    
    Returns:
        dict: The updated document state
    """
    def extract_tag_content(tag, text):
        pattern = f"<{tag}.*?>(.*?)</{tag}>"
        return re.findall(pattern, text, re.DOTALL)

    # 1. Execute Python code
    # This gives the LLM ability to perform actual computations and actions
    for code in extract_tag_content("execute", response):
        result = execute_code(code, provided_vars)
        doc["Working Memory"] = doc.get("Working Memory", "") + f"\nExecution Result:\n{result}"

    # 2. Update existing sections
    # Allows complete replacement of section content
    update_pattern = r'<update_section\s+name="([^"]+)">(.*?)</update_section>'
    for section_name, content in re.findall(update_pattern, response, re.DOTALL):
        doc[section_name] = content.strip()

    # 3. Append to existing sections
    # Enables incremental additions to sections
    append_pattern = r'<append_section\s+name="([^"]+)">(.*?)</append_section>'
    for section_name, content in re.findall(append_pattern, response, re.DOTALL):
        doc[section_name] = doc.get(section_name, "") + "\n" + content.strip()

    # 4. Create (or append to) new sections
    # Supports dynamic creation of new document sections
    new_pattern = r'<new_section\s+name="([^"]+)">(.*?)</new_section>'
    for section_name, content in re.findall(new_pattern, response, re.DOTALL):
        if section_name in doc:
            doc[section_name] += "\n" + content.strip()
        else:
            doc[section_name] = content.strip()

    # 5. Delete sections
    # Allows removal of unnecessary sections
    for section in extract_tag_content("delete_section", response):
        doc.pop(section.strip(), None)

    # 6. Check for completion
    # Tracks whether the LLM considers its task complete
    status_updates = extract_tag_content("status", response)
    if status_updates and status_updates[-1].strip() == "done":
        doc["Status"] = "done"

    return doc

def to_text_form(doc):
    """
    Converts a document dictionary into a structured text representation.
    
    This function is crucial for maintaining the "living document" paradigm,
    as it creates a consistent format for the LLM to process. The XML-like
    structure makes it easy for the LLM to understand and modify the document.
    
    Potential Improvements:
        - Could add support for hierarchical document structure
        - Could implement selective section rendering
        - Could add metadata or section types
    
    Args:
        doc (dict): The document to convert
    
    Returns:
        str: XML-like text representation of the document
    """
    def sanitize_section_name(name):
        return name.replace(" ", "_")

    sections_text = []
    for section_name, content in doc.items():
        tag_name = sanitize_section_name(section_name)
        sections_text.append(f"<{tag_name}>\n{content}\n</{tag_name}>")

    return "\n\n".join(sections_text)

def step_work_on_doc(llm_obj, doc, provided_vars=None):
    """
    Performs one iteration of document processing with the LLM.
    
    This function implements the main interaction loop between the LLM
    and the document. It converts the document to text, sends it to
    the LLM, and processes the response to update the document.
    
    Potential Improvements:
        - Could add support for parallel processing
        - Could implement recursive document processing
        - Could add mechanisms for the LLM to request specific sections
    
    Args:
        llm_obj: The language model interface
        doc (dict): The current document state
        provided_vars (dict, optional): Variables for code execution
    
    Returns:
        tuple: (updated document, raw LLM response)
    """
    doc_copy = doc.copy()
    doc_text_form = to_text_form(doc_copy)
    response = llm_obj.invoke(doc_text_form).content
    updated_doc = process_llm_response(doc_copy, response, provided_vars)
    return updated_doc, response