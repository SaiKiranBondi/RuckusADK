from google.adk.agents import LlmAgent
from tools.test_implementation_tools import write_test_code
from tools.test_execution_tools import execute_tests_sandboxed, execute_c_tests_simple
from .prompts import get_debugger_and_refiner_prompt

# Create the agent with dynamic instruction based on language
def create_debugger_and_refiner_agent(language: str = "python"):
    """Create a debugger and refiner agent for the specified language."""
    return LlmAgent(
        name="DebuggerAndRefiner",
        description="Analyzes test failures and autonomously attempts to correct the generated test code.",
        model="gemini-2.5-pro",
        instruction=get_debugger_and_refiner_prompt(language),
        tools=[write_test_code, execute_tests_sandboxed, execute_c_tests_simple]
    )

# Default agent (will be updated dynamically)
debugger_and_refiner_agent = create_debugger_and_refiner_agent("python")