import asyncio
import json
import re
import subprocess
import os
import sys
from google.adk.runners import Runner
from google.genai import types
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv

# Import the coordinator module to create root agent dynamically
from agents.coordinator import create_root_agent

# Use a shared session service for the application
session_service = InMemorySessionService()

def detect_language(file_path: str) -> str:
    """Detect programming language based on file extension."""
    if file_path.endswith('.py'):
        return 'python'
    elif file_path.endswith('.c'):
        return 'c'
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

def run_python_tests():
    """Run pytest on the generated Python test file."""
    print("\n" + "="*60)
    print("🧪 RUNNING PYTHON TESTS")
    print("="*60)
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", "final_test_suite.py", "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=".")
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"\nExit code: {result.returncode}")
        if result.returncode == 0:
            print("✅ All Python tests passed!")
        else:
            print("❌ Some Python tests failed!")
            
    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest: pip install pytest")
    except Exception as e:
        print(f"❌ Error running Python tests: {e}")

def run_c_tests():
    """Run Unity tests on the generated C test file."""
    print("\n" + "="*60)
    print("🔧 RUNNING C TESTS")
    print("="*60)
    
    try:
        # First, check if gcc is available
        gcc_check = subprocess.run(["gcc", "--version"], capture_output=True, text=True)
        if gcc_check.returncode != 0:
            print("❌ gcc compiler not found. Please install gcc.")
            return
        
        # Create a simple test runner
        test_runner_content = '''#include "unity.h"
#include "final_test_suite.c"

int main(void) {
    UNITY_BEGIN();
    
    // Test function calls will be added here
    
    return UNITY_END();
}
'''
        
        with open("test_runner.c", "w") as f:
            f.write(test_runner_content)
        
        # Compile the test
        compile_result = subprocess.run([
            "gcc", "-o", "test_runner", "test_runner.c", "final_test_suite.c", "-I.", "-std=c99"
        ], capture_output=True, text=True)
        
        if compile_result.returncode != 0:
            print("❌ Compilation failed:")
            print(compile_result.stderr)
            return
        
        # Run the test
        result = subprocess.run(["./test_runner"], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"\nExit code: {result.returncode}")
        if result.returncode == 0:
            print("✅ All C tests passed!")
        else:
            print("❌ Some C tests failed!")
            
        # Clean up
        if os.path.exists("test_runner"):
            os.remove("test_runner")
        if os.path.exists("test_runner.c"):
            os.remove("test_runner.c")
            
    except FileNotFoundError:
        print("❌ gcc compiler not found. Please install gcc.")
    except Exception as e:
        print(f"❌ Error running C tests: {e}")

async def main():
    print("--- Starting Autonomous Test Suite Generation System ---")
    
    # 1. Configuration: Change this variable to test different files
    # Available options:
    # - "sample_code.py" (Python)
    # - "examples/sample_code.c" (C)
    # - Any other .py or .c file path
    TEST_FILE_PATH = "sample_code.c"  # Change this to test different files
    
    # 2. Load the source code we want to test
    try:
        with open(TEST_FILE_PATH, "r") as f:
            source_code_to_test = f.read()
        language = detect_language(TEST_FILE_PATH)
        print(f"Testing file: {TEST_FILE_PATH} (Language: {language})")
    except FileNotFoundError:
        print(f"Error: File '{TEST_FILE_PATH}' not found. Please ensure the file exists.")
        return
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # 2. Create the root agent for the detected language
    root_agent = create_root_agent(language)
    
    # 3. Instantiate the ADK Runner with our master agent
    # We pass the shared session_service instance here.
    runner = Runner(
        app_name="autotest_suite_generator",
        agent=root_agent,
        session_service=session_service
    )
    
    # 3. Create a session for this run
    session = await runner.session_service.create_session(
        app_name="autotest_suite_generator",
        user_id="end_user"
    )

    # 4. Format the initial user request as a JSON object
    # The `initialize_state` callback on our root agent will parse this.
    initial_request = json.dumps({
        "source_code": source_code_to_test,
        "language": language
    })
    
    print(f"\n[USER REQUEST] Generating tests for:\n---\n{source_code_to_test}\n---\n")

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=initial_request)]
    )

    # 5. Run the agent system and stream the process
    final_output = ""
    print("\n--- SYSTEM EXECUTION LOG ---")
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=user_message
    ):
        author = event.author
        content_text = ""
        # We only care about text parts for this simple log view
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    content_text += part.text + "\n"
        
        # Print agent's textual output as it happens
        if content_text.strip():
            print(f"[{author}]: {content_text.strip()}")

        # Capture the final response from the last agent in the sequence
        if event.is_final_response():
            final_output = content_text.strip()
            
    print("\n--- SYSTEM EXECUTION COMPLETE ---")
    print("\n--- FINAL RESULT ---")
    
    print(final_output)

    # Try to extract code block for saving based on language
    test_file_saved = False
    
    if language == 'python':
        python_code_match = re.search(r"```python\n([\s\S]+?)\n```", final_output, re.DOTALL)
        if python_code_match:
            final_code = python_code_match.group(1).strip()
            with open("final_test_suite.py", "w") as f:
                f.write(final_code)
            print("\n--- Final test suite saved to `final_test_suite.py` ---")
            test_file_saved = True
        else:
            print("\n--- Could not extract a Python code block to save to file. ---")
    
    elif language == 'c':
        c_code_match = re.search(r"```c\n([\s\S]+?)\n```", final_output, re.DOTALL)
        if c_code_match:
            final_code = c_code_match.group(1).strip()
            with open("final_test_suite.c", "w") as f:
                f.write(final_code)
            print("\n--- Final test suite saved to `final_test_suite.c` ---")
            test_file_saved = True
        else:
            print("\n--- Could not extract a C code block to save to file. ---")
    
    else:
        print(f"\n--- Unsupported language '{language}' for final output. ---")
    
    # Run the generated tests
    if test_file_saved:
        if language == 'python':
            run_python_tests()
        elif language == 'c':
            run_c_tests()


if __name__ == "__main__":
    # Make sure your .env file with GOOGLE_API_KEY is present
    load_dotenv()
    asyncio.run(main())