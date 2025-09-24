from google.adk.agents import LlmAgent
from RuckusADK.tools.test_design_tools import generate_test_scenarios
from .prompts import get_test_case_designer_prompt_original

def create_test_case_designer_agent():
    """Create a fresh test case designer agent instance."""
    agent = LlmAgent(
        name="TestCaseDesigner",
        description="Generates comprehensive abstract test scenarios in natural language based on a code analysis report.",
        model="gemini-2.5-pro",
        instruction=get_test_case_designer_prompt_original(),
        tools=[
            generate_test_scenarios
        ]
    )
    
    # Set up the output key
    agent.output_key = "test_scenarios"
    
    return agent

# Default agent (will be updated dynamically)
test_case_designer_agent = create_test_case_designer_agent()