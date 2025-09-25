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
    Generates a complete C test file with enhanced printf statements and progress tracking.
    
    Args:
        test_scenarios: List of test scenario dictionaries.
        
    Returns:
        A complete C test file as a string.
    """
    # Start with enhanced C test framework
    test_file = '''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "source_to_test.h"

// Enhanced test framework with detailed reporting
int tests_passed = 0;
int tests_failed = 0;
int current_test = 0;
int total_tests = 0;

// Enhanced assertion macros with detailed output
#define ASSERT_EQUAL_INT(expected, actual, message) \\
    do { \\
        current_test++; \\
        printf("\\n[%d/%d] Testing: %s\\n", current_test, total_tests, message); \\
        printf("   Expected: %d\\n", expected); \\
        printf("   Actual:   %d\\n", actual); \\
        if ((expected) == (actual)) { \\
            printf("   ✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("   ❌ FAIL: %s (expected %d, got %d)\\n", message, expected, actual); \\
            tests_failed++; \\
        } \\
    } while(0)

#define ASSERT_EQUAL_DOUBLE(expected, actual, message) \\
    do { \\
        current_test++; \\
        printf("\\n[%d/%d] Testing: %s\\n", current_test, total_tests, message); \\
        printf("   Expected: %.6f\\n", expected); \\
        printf("   Actual:   %.6f\\n", actual); \\
        if (fabs((expected) - (actual)) < 0.000001) { \\
            printf("   ✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("   ❌ FAIL: %s (expected %.6f, got %.6f)\\n", message, expected, actual); \\
            tests_failed++; \\
        } \\
    } while(0)

#define ASSERT_STRING_EQUAL(expected, actual, message) \\
    do { \\
        current_test++; \\
        printf("\\n[%d/%d] Testing: %s\\n", current_test, total_tests, message); \\
        printf("   Expected: '%s'\\n", expected); \\
        printf("   Actual:   '%s'\\n", actual); \\
        if (strcmp(expected, actual) == 0) { \\
            printf("   ✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("   ❌ FAIL: %s (expected '%s', got '%s')\\n", message, expected, actual); \\
            tests_failed++; \\
        } \\
    } while(0)

#define ASSERT_NOT_NULL(actual, message) \\
    do { \\
        current_test++; \\
        printf("\\n[%d/%d] Testing: %s\\n", current_test, total_tests, message); \\
        printf("   Expected: Non-NULL pointer\\n"); \\
        printf("   Actual:   %s\\n", (actual) ? "Non-NULL" : "NULL"); \\
        if ((actual) != NULL) { \\
            printf("   ✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("   ❌ FAIL: %s (expected non-NULL, got NULL)\\n", message); \\
            tests_failed++; \\
        } \\
    } while(0)

#define ASSERT_NULL(actual, message) \\
    do { \\
        current_test++; \\
        printf("\\n[%d/%d] Testing: %s\\n", current_test, total_tests, message); \\
        printf("   Expected: NULL pointer\\n"); \\
        printf("   Actual:   %s\\n", (actual) ? "Non-NULL" : "NULL"); \\
        if ((actual) == NULL) { \\
            printf("   ✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("   ❌ FAIL: %s (expected NULL, got non-NULL)\\n", message); \\
            tests_failed++; \\
        } \\
    } while(0)

#define ASSERT_TRUE(condition, message) \\
    do { \\
        current_test++; \\
        printf("\\n[%d/%d] Testing: %s\\n", current_test, total_tests, message); \\
        printf("   Expected: TRUE (1)\\n"); \\
        printf("   Actual:   %s\\n", (condition) ? "TRUE (1)" : "FALSE (0)"); \\
        if (condition) { \\
            printf("   ✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("   ❌ FAIL: %s (expected TRUE, got FALSE)\\n", message); \\
            tests_failed++; \\
        } \\
    } while(0)

#define ASSERT_FALSE(condition, message) \\
    do { \\
        current_test++; \\
        printf("\\n[%d/%d] Testing: %s\\n", current_test, total_tests, message); \\
        printf("   Expected: FALSE (0)\\n"); \\
        printf("   Actual:   %s\\n", (condition) ? "TRUE (1)" : "FALSE (0)"); \\
        if (!(condition)) { \\
            printf("   ✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("   ❌ FAIL: %s (expected FALSE, got TRUE)\\n", message); \\
            tests_failed++; \\
        } \\
    } while(0)

// Legacy macros for backward compatibility
#define ASSERT_EQUAL(expected, actual, message) ASSERT_EQUAL_INT(expected, actual, message)

'''
    
    # Add test functions for each scenario
    for i, scenario in enumerate(test_scenarios):
        description = scenario.get('description', 'No description provided')
        expected_outcome = scenario.get('expected_outcome', 'No expected outcome provided')
        function_name = _sanitize_for_function_name(description)
        
        test_file += f'''/*
 * Test Scenario {i+1}: {description}
 * Expected Outcome: {expected_outcome}
 */
void {function_name}(void) {{
    printf("\\n🧪 Running Test Scenario {i+1}: {description}\\n");
    printf("📋 Expected: {expected_outcome}\\n");
    printf("----------------------------------------\\n");
    
    // Test implementation will be added by the LLM
    // This is a placeholder for simple C test function
    printf("⚠️  PLACEHOLDER: Test implementation needed\\n");
}}

'''
    
    # Add main function with enhanced reporting
    test_file += f'''int main(void) {{
    total_tests = {len(test_scenarios)};
    
    printf("🧪 TestMozart C Test Suite\\n");
    printf("==========================\\n");
    printf("📊 Total Test Scenarios: %d\\n", total_tests);
    printf("==========================\\n\\n");
    
    // Run all test scenarios
'''
    
    # Add calls to all test functions
    for i, scenario in enumerate(test_scenarios):
        function_name = _sanitize_for_function_name(scenario.get('description', f'Test scenario {i+1}'))
        test_file += f'    {function_name}();\n'
    
    test_file += '''    
    printf("\\n==========================\\n");
    printf("📊 FINAL TEST RESULTS\\n");
    printf("==========================\\n");
    printf("✅ Tests Passed: %d\\n", tests_passed);
    printf("❌ Tests Failed: %d\\n", tests_failed);
    printf("📈 Total Tests:  %d\\n", tests_passed + tests_failed);
    printf("📊 Success Rate: %.1f%%\\n", (tests_passed * 100.0) / (tests_passed + tests_failed));
    printf("==========================\\n");
    
    if (tests_failed == 0) {
        printf("🎉 ALL TESTS PASSED! 🎉\\n");
        printf("✨ Test suite completed successfully!\\n");
        return 0;
    } else {
        printf("💥 SOME TESTS FAILED! 💥\\n");
        printf("🔧 Please review the failed tests above.\\n");
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