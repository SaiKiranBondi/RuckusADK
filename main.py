import asyncio
import json
import re
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

# Test execution functions removed - run tests manually

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
    # For Google Cloud, we don't need to specify authentication
    # as it will use the default Google Cloud credentials
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
    
    # Tests have been generated and saved
    # You can now run them manually:
    # For Python: pytest -v final_test_suite.py
    # For C: gcc -o test_runner final_test_suite.c -std=c99 && ./test_runner


if __name__ == "__main__":
    # For Google Cloud Shell, we don't need .env file
    # The system will use Google Cloud credentials automatically
    load_dotenv()
    
    # Don't override Google Cloud authentication
    # Let the system use the default Google Cloud credentials
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        os.environ["GOOGLE_CLOUD_PROJECT"] = "ruckusdevtools"
    
    # Check if we're in Google Cloud environment
    if os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("✅ Running in Google Cloud environment")
        print("Using Google Cloud credentials for authentication")
    else:
        print("⚠️  Not in Google Cloud environment")
        print("Make sure you're authenticated with Google Cloud")
    
    asyncio.run(main())