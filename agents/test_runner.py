from google.adk.agents import LlmAgent
from tools.test_execution_tools import execute_tests_sandboxed, parse_test_results
from .prompts import get_test_runner_prompt

# Create the agent with dynamic instruction based on language
def create_test_runner_agent(language: str = "python"):
    """Create a test runner agent for the specified language."""
    return LlmAgent(
        name="TestRunner",
        description="Executes generated test code against the original source code in a secure sandbox and parses the results.",
        model="gemini-2.5-pro",
        instruction=get_test_runner_prompt(language),
        tools=[execute_tests_sandboxed, parse_test_results]
    )

# Default agent (will be updated dynamically)
test_runner_agent = create_test_runner_agent("python")