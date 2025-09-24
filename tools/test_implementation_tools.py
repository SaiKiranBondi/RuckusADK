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
        # Use local C test implementation function
        print(f"DEBUG: Using C test implementation for language: {language}")
        return write_c_test_code(test_scenario)
    
    else:
        return f"# Error: Unsupported language '{language}'. Only 'python' and 'c' are supported."

# C-specific test implementation functions
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
    Creates simple C test code based on a structured test scenario.
    
    Args:
        test_scenario: A dictionary containing 'description' and 'expected_outcome'.
        
    Returns:
        A string containing simple C test code.
    """
    description = test_scenario.get('description', 'No description provided')
    expected_outcome = test_scenario.get('expected_outcome', 'No expected outcome provided')
    
    function_name = _sanitize_for_function_name(description)
    
    # Create a detailed comment from the scenario
    comment = f"/*\n * Tests: {description}\n * Expected Outcome: {expected_outcome}\n */"
    
    # Simple C test function template
    code_template = f'''{comment}
void {function_name}(void) {{
    // Test implementation will be added by the LLM
    // This is a placeholder for simple C test function
}}
'''
    return code_template.strip()

def generate_complete_c_test_file(test_scenarios: list) -> str:
    """
    Generates a complete C test file with Unity framework.
    
    Args:
        test_scenarios: List of test scenario dictionaries.
        
    Returns:
        A complete C test file as a string.
    """
    # Start with simple C includes
    test_file = '''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "source_to_test.h"

// Simple test framework
int tests_passed = 0;
int tests_failed = 0;

#define ASSERT_EQUAL(expected, actual, message) \\
    do { \\
        if ((expected) == (actual)) { \\
            printf("✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("❌ FAIL: %s (expected %d, got %d)\\n", message, expected, actual); \\
            tests_failed++; \\
        } \\
    } while(0)

#define ASSERT_STRING_EQUAL(expected, actual, message) \\
    do { \\
        if (strcmp(expected, actual) == 0) { \\
            printf("✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("❌ FAIL: %s (expected '%s', got '%s')\\n", message, expected, actual); \\
            tests_failed++; \\
        } \\
    } while(0)

'''
    
    # Add test functions for each scenario
    for scenario in test_scenarios:
        description = scenario.get('description', 'No description provided')
        expected_outcome = scenario.get('expected_outcome', 'No expected outcome provided')
        function_name = _sanitize_for_function_name(description)
        
        test_file += f'''/*
 * Tests: {description}
 * Expected Outcome: {expected_outcome}
 */
void {function_name}(void) {{
    // Test implementation will be added by the LLM
    // This is a placeholder for simple C test function
}}

'''
    
    # Add main function
    test_file += '''int main(void) {
    printf("🧪 Running C Tests...\\n");
    printf("====================\\n\\n");
    
    // Test function calls will be added here
    
    printf("\\n====================\\n");
    printf("📊 Test Results:\\n");
    printf("✅ Passed: %d\\n", tests_passed);
    printf("❌ Failed: %d\\n", tests_failed);
    printf("📈 Total: %d\\n", tests_passed + tests_failed);
    
    if (tests_failed == 0) {
        printf("🎉 All tests passed!\\n");
        return 0;
    } else {
        printf("💥 Some tests failed!\\n");
        return 1;
    }
}
'''
    
    return test_file

def generate_c_test_boilerplate() -> str:
    """
    Generates the simple C test framework boilerplate for C tests.
    
    Returns:
        A string containing the simple C test framework setup code.
    """
    return '''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "source_to_test.h"

// Simple test framework
int tests_passed = 0;
int tests_failed = 0;

#define ASSERT_EQUAL(expected, actual, message) \\
    do { \\
        if ((expected) == (actual)) { \\
            printf("✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("❌ FAIL: %s (expected %d, got %d)\\n", message, expected, actual); \\
            tests_failed++; \\
        } \\
    } while(0)

#define ASSERT_STRING_EQUAL(expected, actual, message) \\
    do { \\
        if (strcmp(expected, actual) == 0) { \\
            printf("✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("❌ FAIL: %s (expected '%s', got '%s')\\n", message, expected, actual); \\
            tests_failed++; \\
        } \\
    } while(0)

// Test functions will be inserted here
'''