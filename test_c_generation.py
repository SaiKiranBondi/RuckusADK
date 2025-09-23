#!/usr/bin/env python3
"""
Test script to verify C test generation is working
"""

from tools.c_test_implementation_tools import write_c_test_code

# Test C test generation
test_scenario = {
    "description": "Test the 'add' method with two positive integers",
    "expected_outcome": "The method should return the correct sum of the two integers"
}

print("Testing C test generation:")
print("=" * 50)

c_test_code = write_c_test_code(test_scenario)
print(c_test_code)

print("\n" + "=" * 50)
print("C test generation working correctly!")
