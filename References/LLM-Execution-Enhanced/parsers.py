# Purpose: Detect and extract code blocks from LLM responses using predefined markers.
# Used by: Main loop in TaskSolver (core.py) to identify when code execution is needed.
#
# Requirements:
# - Text contains code blocks marked with:
#   [#start of code to be executed]
#   code here
#   [#end of code to be executed]
#
# Known issues/limitations:
# - No handling of nested code blocks
# - No handling of malformed markers
# - No validation of extracted code
# - No handling of multiple code blocks in one response
# - Assumes markers are exactly as specified (sensitive to whitespace/formatting)



# def contains_code(text: str) -> bool:
#     has_start = "#start of code to be executed" in text
#     has_end = "#end of code to be executed" in text
#     print(f"Checking for code blocks: start={has_start}, end={has_end}")
#     return has_start and has_end

# def extract_code(text: str) -> str:
#     start = text.find("#start of code to be executed") + len("#start of code to be executed")
#     end = text.find("#end of code to be executed")
#     extracted = text[start:end].strip()
#     print(f"Extracted code: {extracted}")
#     return extracted


import re

def contains_code(text: str) -> bool:
    """
    Check if text contains both start and end code markers, ignoring case and whitespace variations.
    
    Args:
        text (str): The text to check for code blocks
        
    Returns:
        bool: True if both start and end markers are found, False otherwise
    """
    # Create case-insensitive patterns that match varying whitespace
    start_pattern = r'#\s*start\s+of\s+code\s+to\s+be\s+executed\s*'
    end_pattern = r'#\s*end\s+of\s+code\s+to\s+be\s+executed\s*'
    
    has_start = bool(re.search(start_pattern, text, re.IGNORECASE))
    has_end = bool(re.search(end_pattern, text, re.IGNORECASE))
    
    print(f"Checking for code blocks: start={has_start}, end={has_end}")
    return has_start and has_end

def extract_code(text: str) -> str:
    """
    Extract code between start and end markers, handling variations in marker formatting.
    
    Args:
        text (str): The text containing the code block
        
    Returns:
        str: The extracted code, stripped of leading/trailing whitespace
        
    Raises:
        ValueError: If start or end markers are not found
    """
    # Pattern matches everything between the start and end markers
    pattern = r'#\s*start\s+of\s+code\s+to\s+be\s+executed\s*(.*?)#\s*end\s+of\s+code\s+to\s+be\s+executed'
    
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError("Could not find complete code block with start and end markers")
    
    extracted = match.group(1).strip()
    print(f"Extracted code: {extracted}")
    return extracted
