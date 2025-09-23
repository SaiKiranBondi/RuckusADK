import json
import shutil
import tempfile
import os
import sys
import subprocess
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# --- Pydantic Models for C Test Results ---

class CTestFailureDetail(BaseModel):
    """Details of a single C test failure."""
    test_name: str
    error_message: str
    traceback: str

class CTestResult(BaseModel):
    """A structured representation of the C test execution results."""
    status: str = Field(..., description="Overall status: 'PASS' or 'FAIL'.")
    summary: str = Field(..., description="The summary line from the test runner.")
    failures: List[CTestFailureDetail] = Field(default_factory=list, description="A list of detailed failure information.")

def execute_c_tests_sandboxed(source_code: str, test_code: str) -> Dict[str, Any]:
    """
    Executes C tests using Unity framework in a temporary environment.
    
    Args:
        source_code: The original C source code as a string.
        test_code: The generated Unity test code as a string.
        
    Returns:
        A dictionary containing the raw stdout, stderr, and exit code from the execution.
    """
    
    # Create a temporary directory to work in
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # --- 1. Create files ---
        source_path = os.path.join(temp_dir, "source_to_test.c")
        test_path = os.path.join(temp_dir, "test_generated.c")
        header_path = os.path.join(temp_dir, "source_to_test.h")
        main_path = os.path.join(temp_dir, "test_main.c")
        
        # Write source code
        with open(source_path, "w") as f:
            f.write(source_code)
            
        # Write test code
        with open(test_path, "w") as f:
            f.write(test_code)
        
        # Create header file
        with open(header_path, "w") as f:
            f.write("#ifndef SOURCE_TO_TEST_H\n")
            f.write("#define SOURCE_TO_TEST_H\n")
            f.write("\n// Function declarations will be added here\n")
            f.write("\n#endif\n")
        
        # Create main test runner
        main_content = '''#include "unity.h"
#include "source_to_test.h"

// Include test functions
'''
        with open(main_path, "w") as f:
            f.write(main_content)
            f.write(test_code)
            f.write('''
int main(void) {
    UNITY_BEGIN();
    
    // Test function calls will be added here
    
    return UNITY_END();
}
''')
        
        # --- 2. Compile and link ---
        try:
            # Compile source and test files
            compile_result = subprocess.run([
                "gcc", "-o", "test_runner", 
                main_path, source_path, test_path,
                "-I.", "-std=c99"
            ], cwd=temp_dir, capture_output=True, text=True, check=True)
            
            # --- 3. Execute tests ---
            result = subprocess.run(
                ["./test_runner"],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "exit_code": e.returncode,
                "stdout": e.stdout,
                "stderr": f"Compilation error: {e.stderr}"
            }
        except FileNotFoundError:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "gcc compiler not found. Please install gcc."
            }

def parse_c_test_results(raw_execution_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses the raw output from C test execution into a structured JSON object.
    
    Args:
        raw_execution_output: The dictionary returned by execute_c_tests_sandboxed.
        
    Returns:
        A dictionary conforming to the CTestResult schema.
    """
    exit_code = raw_execution_output.get('exit_code', -1)
    stdout = raw_execution_output.get('stdout', '')
    stderr = raw_execution_output.get('stderr', '')
    
    # Unity exit code 0 means all tests passed
    status = "PASS" if exit_code == 0 else "FAIL"
    
    # Parse Unity output
    summary = "No summary found."
    failures = []
    
    if status == "FAIL":
        # Parse Unity failure output
        lines = stdout.split('\n')
        for line in lines:
            if "FAIL" in line or "ERROR" in line:
                # Extract test name and error message
                test_name = "unknown_test"
                error_message = line.strip()
                
                failures.append(CTestFailureDetail(
                    test_name=test_name,
                    error_message=error_message,
                    traceback=stderr
                ))
        
        summary = f"{len(failures)} test(s) failed"
    else:
        # Parse success output
        lines = stdout.split('\n')
        for line in lines:
            if "PASS" in line and "test" in line.lower():
                summary = line.strip()
                break
    
    result = CTestResult(status=status, summary=summary, failures=failures)
    return result.model_dump()
