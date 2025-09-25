from google.adk.agents import LlmAgent
from tools.test_implementation_tools import write_test_code
from tools.test_execution_tools import execute_tests_sandboxed, execute_c_tests_simple
from .prompts import get_test_implementer_prompt

# Create the agent with dynamic instruction based on language
def create_test_implementer_agent(language: str = "python"):
    """Create a test implementer agent for the specified language."""
    agent = LlmAgent(
        name="TestImplementer",
        description="Translates abstract test scenarios into syntactically correct, idiomatic unit test code.",
        model="gemini-2.5-pro",
        instruction=get_test_implementer_prompt(language),
        tools=[write_test_code, execute_tests_sandboxed, execute_c_tests_simple]
    )
    
    # Set up the output key
    agent.output_key = "generated_test_code"
    
    return agent


# Default agent (will be updated dynamically)
test_implementer_agent = create_test_implementer_agent("python")    