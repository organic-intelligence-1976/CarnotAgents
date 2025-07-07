import io
import contextlib
import traceback
import re

_context = {}  # Global execution context for Python code

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

    # 1. Execute Python code
    for code in extract_tag_content("execute", response):
        result = execute_code(code, provided_vars)
        doc["Working_Memory"] = doc.get("Working_Memory", "") + f"\nExecution Result:\n{result}"

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


def step_work_on_doc(llm_obj, doc, provided_vars=None):
    """
    Sends the doc text to the LLM, processes the response, and returns
    both the updated doc and the raw response.
    
    Args:
        llm_obj: LLM object with invoke method
        doc (dict): Document dictionary with sections
        provided_vars (dict, optional): Variables to provide to code execution
        
    Returns:
        tuple: (updated document, raw LLM response)
    """
    doc_copy = doc.copy()
    doc_text_form = to_text_form(doc_copy)
    response = llm_obj.invoke(doc_text_form).content
    updated_doc = process_llm_response(doc_copy, response, provided_vars)
    return updated_doc, response


# Default text blocks (goal, doc structure, etc.)
default_goal = """
  You are a research assistant. Your goal is to make progress on the problem described in the User Request section below and add your insights to this report. 
  
  You are expected to:

  1. Read the existing doc.
  2. Potentially create new Python variables (dataframes, summary stats, etc.) that you can reuse later.
  3. Save partial results or artifacts to the file system, if beneficial for the final report (e.g. any visualizations produced saved as pdf or similar formats).
  4. Provide new insights in the doc. Notice that the insights may be intermediate results that just make progress on the task that the user requested; It doesn't have to be the "final insight" or high level in any sense.
"""

default_doc_structure = """
  As you can see, this document is structured using XML tags. Each section is wrapped in tags matching its name. For example, a Doc with sections "Instructions" and "User Request" becomes:
      <Instructions>
      ...content...
      </Instructions>
      <User_Request>
      ...content...
      </User_Request>
"""

default_formatting_of_requests = """
 In order to make progress on the task, apart from thinking about the info you have, you can take two kinds of actions: 

  1- Request an edit of this document to include the more important parts of your new thoughts (so that you have access to it for future thoughts, research and reporting)

  2- Ask for a piece of python code to be run and see what it produces (for example, typically the user question tells you about the name of a pandas dataframe you can query. Of course you can use computational facilities and modules in python too)


  If you want to request one of the two actions above, structure your response  using the following  tags to indicate different actions:

  To execute Python code: 
  <execute>
  your python code without Markdown formatting (do not include ``` fences...).
  </execute>

  To modify document sections (this should be rare since it removes the previous info in this section, unless new content includes the info in the old content):
  <update_section name="section_name">
  new_content_here
  </update_section>

  To append to existing section content:
  <append_section name="section_name">
  content_to_append
  </append_section>

  To create a new section:
  <new_section name="section_name">
  section_content
  </new_section>

  To delete a section:
  <delete_section>section_name</delete_section>

  To indicate the problem is solved (status should only have two values: done or in_progress):
  <status>done</status>

  You can include multiple actions in one response. Actions will be processed in order.
  Before each action, explain your reasoning in plain text.
"""

def create_default_doc(user_request):
    """
    Construct a doc dictionary with all the sections needed.
    
    Args:
        user_request (str): The user's query or task
        
    Returns:
        dict: Document dictionary with default sections
    """
    return {
        "Goal": default_goal,
        "Doc_Structure": default_doc_structure,
        "User_Request": user_request,
        "Formatting_of_Requests": default_formatting_of_requests,
        "Previous_Analysis_Summary": "",
        "Working_Memory": "",
        "Findings": "",
        "Status": "in_progress"
    }