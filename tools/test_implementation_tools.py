import re
from typing import Dict, Any

def _sanitize_for_function_name(description: str) -> str:
    """Converts a natural language description into a valid Python function name."""
    # Convert to lowercase
    s = description.lower()
    # Remove special characters
    s = re.sub(r'[^a-z0-9\s_]', '', s)
    # Replace spaces with underscores
    s = re.sub(r'\s+', '_', s)
    # Ensure it starts with 'test_' for pytest discovery
    if not s.startswith('test_'):
        s = 'test_' + s
    return s

def write_test_code(test_scenario: Dict[str, Any], target_framework: str, language: str = 'python') -> str:
    """
    Creates boilerplate test code based on a structured test scenario, target framework, and language.
    
    This tool assists the LLM by handling the repetitive and syntactically strict
    parts of writing a test, leaving placeholders for the core logic.

    Args:
        test_scenario: A dictionary containing 'description' and 'expected_outcome'.
        target_framework: The testing framework to target (e.g., 'pytest', 'unity').
        language: The programming language (e.g., 'python', 'c').

    Returns:
        A string containing the boilerplate test code.
    """
    if language.lower() == 'python':
        if target_framework.lower() != 'pytest':
            return f"# Error: Unsupported framework '{target_framework}'. Only 'pytest' is supported for Python."

        description = test_scenario.get('description', 'No description provided')
        expected_outcome = test_scenario.get('expected_outcome', 'No expected outcome provided')

        function_name = _sanitize_for_function_name(description)

        # Create a detailed docstring from the scenario
        docstring = f'''"""
    Tests: {description}
    Expected Outcome: {expected_outcome}
    """'''

        # The template for the test function. The '...' is a placeholder for the LLM.
        code_template = f'''
def {function_name}():
    {docstring}
    # TODO: Implement the test logic and assertion here.
    ...
'''
        return code_template.strip()
    
    elif language.lower() == 'c':
        # Import C test implementation tools
        from tools.c_test_implementation_tools import write_c_test_code
        return write_c_test_code(test_scenario)
    
    else:
        return f"# Error: Unsupported language '{language}'. Only 'python' and 'c' are supported."