import json
import shutil
import tempfile
import os
import sys
import subprocess
import re  # Added missing import for the parser function
from typing import Any, Dict, List, Optional
# import docker # No longer needed
from pydantic import BaseModel, Field

# --- Pydantic Models for Structured Output ---

class TestFailureDetail(BaseModel):
    """Details of a single test failure."""
    test_name: str
    error_message: str
    traceback: str

class TestResult(BaseModel):
    """A structured representation of the test execution results."""
    status: str = Field(..., description="Overall status: 'PASS' or 'FAIL'.")
    summary: str = Field(..., description="The summary line from the test runner (e.g., '1 failed, 1 passed').")
    failures: List[TestFailureDetail] = Field(default_factory=list, description="A list of detailed failure information.")

# --- Tool Implementations ---

def execute_tests_sandboxed(source_code_under_test: str, generated_test_code: str, language: str = 'python') -> Dict[str, Any]:
    """
    Executes generated tests against source code locally in a temporary environment.
    
    Args:
        source_code_under_test: The original source code as a string.
        generated_test_code: The generated test code as a string.
        language: The programming language (e.g., 'python', 'c').

    Returns:
        A dictionary containing the raw stdout, stderr, and exit code from the execution.
    """
    if language.lower() == 'python':
        return execute_python_tests_sandboxed(source_code_under_test, generated_test_code)
    elif language.lower() == 'c':
        return execute_c_tests_sandboxed(source_code_under_test, generated_test_code)
    else:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Unsupported language: {language}"
        }

def execute_python_tests_sandboxed(source_code_under_test: str, generated_test_code: str) -> Dict[str, Any]:
    """
    Executes Python tests against source code locally in a temporary virtual environment.
    
    Args:
        source_code_under_test: The original source code as a string.
        generated_test_code: The generated pytest test code as a string.

    Returns:
        A dictionary containing the raw stdout, stderr, and exit code from the execution.
    """
    
    # Create a temporary directory to work in
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # --- 1. Create files ---
        source_path = os.path.join(temp_dir, "source_to_test.py")
        test_path = os.path.join(temp_dir, "test_generated.py")
        req_path = os.path.join(temp_dir, "requirements.txt")

        with open(source_path, "w") as f:
            f.write(source_code_under_test)
            
        with open(test_path, "w") as f:
            f.write(generated_test_code)

        with open(req_path, "w") as f:
            f.write("pytest\n")

        # --- 2. Create a virtual environment ---
        venv_path = os.path.join(temp_dir, "venv")
        try:
            # Use the currently running Python executable to create the venv
            subprocess.run(
                [sys.executable, "-m", "venv", venv_path], 
                check=True, 
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            return {
                "exit_code": e.returncode,
                "stdout": e.stdout,
                "stderr": f"Failed to create virtual environment:\n{e.stderr}"
            }

        # --- 3. Determine platform-specific executable paths ---
        if os.name == 'nt':  # Windows
            bin_dir = "Scripts"
        else:  # macOS, Linux, etc.
            bin_dir = "bin"
            
        pip_exe = os.path.join(venv_path, bin_dir, "pip")
        pytest_exe = os.path.join(venv_path, bin_dir, "pytest")

        # --- 4. Install requirements into the venv ---
        try:
            subprocess.run(
                [pip_exe, "install", "-r", req_path],
                check=True,
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
        except subprocess.CalledProcessError as e:
            return {
                "exit_code": e.returncode,
                "stdout": e.stdout,
                "stderr": f"Failed to install pytest:\n{e.stderr}"
            }

        # --- 5. Run tests using the venv's pytest ---
        # We run from temp_dir so pytest can find 'source_to_test.py'
        # We do NOT use check=True here, as a non-zero exit code is
        # the expected result for failing tests.
        result = subprocess.run(
            [pytest_exe, test_path],
            capture_output=True,
            text=True,
            cwd=temp_dir
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    # temp_dir and its contents (venv, files) are automatically deleted here


def parse_test_results(raw_execution_output: Dict[str, Any], language: str = 'python') -> Dict[str, Any]:
    """
    Parses the raw output from the sandboxed execution into a structured JSON object.

    Args:
        raw_execution_output: The dictionary returned by execute_tests_sandboxed.
        language: The programming language (e.g., 'python', 'c').

    Returns:
        A dictionary conforming to the TestResult schema.
    """
    if language.lower() == 'python':
        return parse_python_test_results(raw_execution_output)
    elif language.lower() == 'c':
        return parse_c_test_results(raw_execution_output)
    else:
        return {
            "status": "FAIL",
            "summary": f"Unsupported language: {language}",
            "failures": []
        }

def parse_python_test_results(raw_execution_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses the raw output from Python test execution into a structured JSON object.

    Args:
        raw_execution_output: The dictionary returned by execute_python_tests_sandboxed.

    Returns:
        A dictionary conforming to the TestResult schema.
    """
    exit_code = raw_execution_output.get('exit_code', -1)
    stdout = raw_execution_output.get('stdout', '')
    
    # pytest exit code 0 means all tests passed
    # pytest exit code 1 means tests were collected and run, but some failed
    # Other codes (2-5) indicate other errors (interruption, internal error, etc.)
    status = "PASS" if exit_code == 0 else "FAIL"
    
    # If no tests were run (e.g., syntax error in test file), exit_code might be > 1
    # but the parser might not find failure blocks.
    if exit_code != 0 and exit_code != 1:
        summary = "Test execution error (non-zero exit code)."
        # Put stderr in the summary if stdout is empty
        if not stdout.strip() and raw_execution_output.get('stderr'):
             summary = f"Test execution error:\n{raw_execution_output.get('stderr')}"
        
        return TestResult(
            status="FAIL",
            summary=summary,
            failures=[]
        ).model_dump()

    summary = "No summary found."
    
    # Find the pytest summary line
    # This regex looks for the "short test summary info" block
    summary_match = re.search(r"={10,}\s(short test summary info)\s={10,}([\s\S]*)", stdout)
    
    if summary_match:
        # If the summary block exists, grab the content after it
        summary_content = summary_match.group(2).strip()
        # The actual summary is usually the last line(s) of the output
        final_summary_line = stdout.strip().splitlines()[-1]
        if "failed" in final_summary_line or "passed" in final_summary_line:
             summary = final_summary_line.strip('= ')
        else:
             # Fallback if the last line isn't the summary
             summary = summary_content.splitlines()[0] if summary_content else "Test run complete."
    else:
        # Fallback for simpler output
        final_line = stdout.strip().splitlines()[-1]
        if "failed" in final_line or "passed" in final_line or "no tests ran" in final_line:
            summary = final_line.strip('= ')

    
    # In case of failure, parse the details
    failures = []
    if status == "FAIL":
        # Pytest failure sections are typically marked by '___' underlines
        failure_blocks = re.findall(r"_{5,}\s(.+?)\s_{5,}([\s\S]+?)(?=(_{5,}\s.+?\s_{5,}|={10,}\s(short test summary info)\s={10,}))", stdout)
        
        for block in failure_blocks:
            test_name_full = block[0].strip()
            # Extract just the function name
            test_name = test_name_full.split("::")[-1] if "::" in test_name_full else test_name_full
            
            traceback_content = block[1].strip()
            # The error message is typically the last line before the traceback details or a line starting with 'E '
            error_message = "No specific error message found."
            error_lines = [line for line in traceback_content.splitlines() if line.strip().startswith('E ')]
            
            if error_lines:
                error_message = error_lines[-1].strip()[2:] # Get text after 'E '
            elif traceback_content.splitlines():
                error_message = traceback_content.splitlines()[-1].strip()

            failures.append(TestFailureDetail(
                test_name=test_name,
                error_message=error_message,
                traceback=traceback_content
            ))

    result = TestResult(status=status, summary=summary, failures=failures)
    return result.model_dump()

# C-specific test execution functions
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