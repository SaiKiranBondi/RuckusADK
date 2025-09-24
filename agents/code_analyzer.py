from google.adk.agents import LlmAgent
from RuckusADK.tools.code_analysis_tools import analyze_code_structure
from .prompts import get_code_analyzer_prompt_original

def create_code_analyzer_agent():
    """Create a fresh code analyzer agent instance."""
    agent = LlmAgent(
        name="CodeAnalyzer",
        description="Performs deep, accurate static analysis of source code by parsing it into a structured format.",
        model="gemini-2.5-flash", # Or any capable model
        instruction=get_code_analyzer_prompt_original(),
        tools=[
            analyze_code_structure
        ]
    )
    
    return agent

# Default agent (will be updated dynamically)
code_analyzer_agent = create_code_analyzer_agent()