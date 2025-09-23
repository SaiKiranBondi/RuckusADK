import re
from typing import Dict, Any

def _sanitize_for_function_name(description: str) -> str:
    """Converts a natural language description into a valid C function name."""
    # Convert to lowercase
    s = description.lower()
    # Remove special characters and replace with underscores
    s = re.sub(r'[^a-z0-9\s_]', '', s)
    # Replace spaces with underscores
    s = re.sub(r'\s+', '_', s)
    # Ensure it starts with 'test_' for Unity framework
    if not s.startswith('test_'):
        s = 'test_' + s
    return s

def write_c_test_code(test_scenario: Dict[str, Any]) -> str:
    """
    Creates Unity-based C test code based on a structured test scenario.
    
    Args:
        test_scenario: A dictionary containing 'description' and 'expected_outcome'.
        
    Returns:
        A string containing the Unity C test code.
    """
    description = test_scenario.get('description', 'No description provided')
    expected_outcome = test_scenario.get('expected_outcome', 'No expected outcome provided')
    
    function_name = _sanitize_for_function_name(description)
    
    # Create a detailed comment from the scenario
    comment = f"/*\n * Tests: {description}\n * Expected Outcome: {expected_outcome}\n */"
    
    # Unity test function template
    code_template = f'''{comment}
void {function_name}(void) {{
    // TODO: Implement the test logic and assertion here.
    // Use Unity assertions like:
    // TEST_ASSERT_EQUAL(expected, actual);
    // TEST_ASSERT_NOT_NULL(pointer);
    // TEST_ASSERT_TRUE(condition);
}}
'''
    return code_template.strip()

def generate_c_test_boilerplate() -> str:
    """
    Generates the Unity test framework boilerplate for C tests.
    
    Returns:
        A string containing the Unity test framework setup code.
    """
    return '''#include "unity.h"
#include "source_to_test.h"

void setUp(void) {
    // Set up code that runs before each test
}

void tearDown(void) {
    // Clean up code that runs after each test
}

// Test functions will be inserted here
'''
