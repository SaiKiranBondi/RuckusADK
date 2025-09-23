import json
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types

# Import the individual agent instances and the new workflow tool
from .code_analyzer import create_code_analyzer_agent
from .test_case_designer import create_test_case_designer_agent
from .test_implementer import create_test_implementer_agent
from .test_runner import create_test_runner_agent
from .debugger_and_refiner import create_debugger_and_refiner_agent
from tools.workflow_tools import exit_loop

# --- State Initialization ---

def initialize_state(callback_context: CallbackContext):
    """Parses the initial user message and populates the session state."""
    user_content = callback_context.user_content
    if user_content and user_content.parts:
        try:
            initial_data = json.loads(user_content.parts[0].text)
            callback_context.state['source_code'] = initial_data.get('source_code')
            callback_context.state['language'] = initial_data.get('language', 'python')
            # Initialize test_results to ensure the final agent doesn't fail
            # if the loop is skipped or fails early.
            callback_context.state['test_results'] = {"status": "UNKNOWN"}
        except (json.JSONDecodeError, AttributeError):
            print("Warning: Could not parse initial JSON request. Treating content as raw source code.")
            callback_context.state['source_code'] = user_content.parts[0].text
            callback_context.state['language'] = 'python'
            callback_context.state['test_results'] = {"status": "UNKNOWN"}



def save_analysis_to_state(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict):
    """
    This callback intercepts the result from the `analyze_code_structure` tool,
    saves it directly to the session state, and ends the agent's turn.
    This is more efficient than waiting for the LLM to summarize the result.
    """
    if tool.name == 'analyze_code_structure':
        # Save the tool's direct output to the state.
        tool_context.state['static_analysis_report'] = tool_response
        # Return a simple content object. This signals to the ADK that the
        # agent's turn is complete, preventing an unnecessary second LLM call.
        return types.Content(parts=[types.Part(text="Static analysis complete.")])


# --- Configure Individual Agents for the Workflow ---

# 1. CodeAnalyzer: Use the callback to save output.
# 1. CodeAnalyzer: Read from `source_code`, save to `static_analysis_report`.
# Note: CodeAnalyzer agent is now created dynamically, so callbacks are handled in the factory function

# 2. TestCaseDesigner: Read from `static_analysis_report`, save to `test_scenarios`.
# Note: TestCaseDesigner agent is now created dynamically, so instructions are handled in the factory function

# 3. TestImplementer: Read from `test_scenarios` and `language`, save to `generated_test_code`.
# Note: TestImplementer agent is now created dynamically, so this instruction is handled in the prompts.py file

# 4. TestRunner: Read `source_code` & `generated_test_code`, save to `test_results`.
async def build_test_runner_instruction(ctx: CallbackContext) -> str:
    """Dynamically creates the prompt for the test runner with code from the state."""
    source_code = ctx.state.get('source_code', '')
    generated_code = ctx.state.get('generated_test_code', '')
    language = ctx.state.get('language', 'python')

    source_code_json_str = json.dumps(source_code)
    generated_code_json_str = json.dumps(generated_code)
    
    return f"""
    You are a highly reliable test execution engine. Your task is to execute a test suite against source code.

    First, call the `execute_tests_sandboxed` tool with the following three arguments:
    - `source_code_under_test`: Set this to the string {source_code_json_str}
    - `generated_test_code`: Set this to the string {generated_code_json_str}
    - `language`: Set this to the string "{language}"

    Second, take the entire, raw JSON output from `execute_tests_sandboxed` and immediately pass it as the `raw_execution_output` argument to the `parse_test_results` tool, along with the `language` parameter.
    Your final output must be only the structured JSON object returned by the `parse_test_results` tool. Do not add any commentary or explanation.
    """
# 5. DebuggerAndRefiner: Read all context, save corrected code back to `generated_test_code`.
# Note: DebuggerAndRefiner agent is now created dynamically, so this instruction is handled in the prompts.py file


# --- Assemble Workflow Agents ---

def create_workflow_agents(language: str = "python"):
    """Create workflow agents for the specified language."""
    # Create fresh agent instances
    code_analyzer = create_code_analyzer_agent()
    test_case_designer = create_test_case_designer_agent()
    test_implementer = create_test_implementer_agent(language)
    test_runner = create_test_runner_agent(language)
    debugger_and_refiner = create_debugger_and_refiner_agent(language)
    
    # Set up callbacks and output keys
    code_analyzer.after_tool_callback = save_analysis_to_state
    
    # The first part of the workflow is a deterministic sequence.
    generation_pipeline = SequentialAgent(
        name="GenerationPipeline",
        description="Analyzes code and designs test scenarios in a strict sequence.",
        sub_agents=[
            code_analyzer,
            test_case_designer,
            test_implementer,
        ]
    )

    # The second part is an iterative loop for implementation and refinement.
    refinement_loop = LoopAgent(
        name="RefinementLoop",
        description="An iterative workflow that implements, runs, and debugs test code until it passes or max attempts are reached.",
        sub_agents=[
            test_runner,
            debugger_and_refiner
        ],
        max_iterations=3
    )
    
    return generation_pipeline, refinement_loop

# Default workflow agents (will be updated dynamically)
generation_pipeline, refinement_loop = create_workflow_agents("python")

def create_result_summarizer_agent():
    """Create a fresh result summarizer agent instance."""
    return LlmAgent(
        name="ResultSummarizer",
        description="Summarizes the final test generation results for the user.",
        model="gemini-2.5-pro",
        instruction="""You are the final reporting agent. Your task is to present the results to the user based on the final shared state.
1. Retrieve the final test code from the `{generated_test_code}` state variable (if available).
2. Retrieve the target language from the `{language}` state variable.
3. Inspect the `{test_results}` from the shared state.

Based on the language:
- For Python: Find the line `from source_to_test import ...` and change it to `from sample_code import ...`
- For C: Ensure proper includes and function declarations are present

4. Format the final output:
- If `test_results.status` is "PASS", your final answer MUST be only the modified code, enclosed in the appropriate markdown block (```python for Python, ```c for C).
- If `test_results.status` is anything other than "PASS", respond with a message explaining that the tests could not be automatically fixed. You MUST include both the modified code (in the appropriate markdown block) and the final `{test_results}` (in a json markdown block) to help the user debug manually.

If `generated_test_code` is not available in the state, provide a summary of the test generation process and indicate that the test code was generated successfully.
""",
    )

# Default agent (will be updated dynamically)
result_summarizer_agent = create_result_summarizer_agent()

def create_root_agent(language: str = "python"):
    """Create the root agent for the specified language."""
    # Create language-specific workflow agents
    generation_pipeline, refinement_loop = create_workflow_agents(language)
    result_summarizer = create_result_summarizer_agent()
    
    # The root_agent is now a SequentialAgent that controls the deterministic high-level workflow.
    return SequentialAgent(
        name="CoordinatorAgent",
        description="The master orchestrator for the autonomous test suite generation system.",
        sub_agents=[
            generation_pipeline,
            refinement_loop,
            result_summarizer,
        ],
        before_agent_callback=initialize_state
    )

# Default root agent (will be updated dynamically)
root_agent = create_root_agent("python")