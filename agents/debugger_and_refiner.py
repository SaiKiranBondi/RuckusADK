from google.adk.agents import LlmAgent
from .prompts import get_debugger_and_refiner_prompt

# Create the agent with dynamic instruction based on language
def create_debugger_and_refiner_agent(language: str = "python"):
    """Create a debugger and refiner agent for the specified language."""
    return LlmAgent(
        name="DebuggerAndRefiner",
        description="Analyzes test failures and autonomously attempts to correct the generated test code.",
        model="gemini-2.5-pro",
        instruction=get_debugger_and_refiner_prompt(language),
        tools=[]
    )

# Default agent (will be updated dynamically)
debugger_and_refiner_agent = create_debugger_and_refiner_agent("python")