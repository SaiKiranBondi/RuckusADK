import json
import os
import tempfile
from google.cloud import storage
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
from .prompts import (
    get_result_summarizer_prompt_deployed,
    get_code_analyzer_prompt_deployed,
    get_test_case_designer_prompt_deployed
)
from RuckusADK.tools.workflow_tools import exit_loop

# --- State Initialization for Deployed Agent ---

def initialize_state_deployed(callback_context: CallbackContext):
    """Parses the initial user message and populates the session state for deployed agent."""
    user_content = callback_context.user_content
    if user_content and user_content.parts:
        try:
            # Try to parse as JSON first (for file-based inputs)
            initial_data = json.loads(user_content.parts[0].text)
            
            # Handle file-based input
            if 'file_url' in initial_data:
                # Download file from GCS bucket
                source_code = download_file_from_gcs(initial_data['file_url'])
                language = detect_language_from_filename(initial_data.get('filename', ''))
            elif 'source_code' in initial_data:
                # Direct source code input
                source_code = initial_data.get('source_code')
                language = initial_data.get('language', 'python')
            else:
                # Fallback to treating as raw source code
                source_code = user_content.parts[0].text
                language = 'python'
            
            callback_context.state['source_code'] = source_code
            callback_context.state['language'] = language
            callback_context.state['test_results'] = {"status": "UNKNOWN"}
            callback_context.state['file_url'] = initial_data.get('file_url', '')
            callback_context.state['filename'] = initial_data.get('filename', '')
            
        except (json.JSONDecodeError, AttributeError):
            # Fallback: treat content as raw source code
            callback_context.state['source_code'] = user_content.parts[0].text
            callback_context.state['language'] = 'python'
            callback_context.state['test_results'] = {"status": "UNKNOWN"}
            callback_context.state['file_url'] = ''
            callback_context.state['filename'] = ''

def detect_language_from_filename(filename: str) -> str:
    """Detect programming language based on file extension."""
    if filename.endswith('.py'):
        return 'python'
    elif filename.endswith('.c'):
        return 'c'
    else:
        return 'python'  # Default to python

def download_file_from_gcs(file_url: str) -> str:
    """Download file content from Google Cloud Storage."""
    try:
        # Parse GCS URL: gs://bucket-name/path/to/file
        if file_url.startswith('gs://'):
            url_parts = file_url[5:].split('/', 1)
            bucket_name = url_parts[0]
            blob_name = url_parts[1] if len(url_parts) > 1 else ''
            
            # Initialize GCS client
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Download file content
            content = blob.download_as_text()
            return content
        else:
            raise ValueError(f"Invalid GCS URL format: {file_url}")
    except Exception as e:
        raise Exception(f"Failed to download file from GCS: {e}")

def save_result_to_gcs(content: str, filename: str, bucket_name: str = "saikiranruckusdevtools-bucket") -> str:
    """Save test result to Google Cloud Storage."""
    try:
        # Initialize GCS client
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        # Create blob name with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"test_results/{timestamp}_{filename}"
        
        # Upload content
        blob = bucket.blob(blob_name)
        blob.upload_from_string(content)
        
        # Return public URL
        return f"gs://{bucket_name}/{blob_name}"
    except Exception as e:
        print(f"Warning: Failed to save to GCS: {e}")
        return ""

# --- Configure Individual Agents for the Workflow ---

def save_analysis_to_state(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict):
    """
    This callback intercepts the result from the `analyze_code_structure` tool,
    saves it directly to the session state, and ends the agent's turn.
    """
    if tool.name == 'analyze_code_structure':
        # Save the tool's direct output to the state.
        tool_context.state['static_analysis_report'] = tool_response
        # Return a simple content object. This signals to the ADK that the
        # agent's turn is complete, preventing an unnecessary second LLM call.
        return types.Content(parts=[types.Part(text="Static analysis complete.")])

# --- Assemble Workflow Agents ---

def create_workflow_agents_deployed(language: str = "python"):
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

def create_result_summarizer_agent_deployed():
    """Create a fresh result summarizer agent instance for deployed version."""
    return LlmAgent(
        name="ResultSummarizer",
        description="Summarizes the final test generation results for the user.",
        model="gemini-2.5-pro",
        instruction=get_result_summarizer_prompt_deployed(),
    )

def create_root_agent_deployed(language: str = "python"):
    """Create the root agent for the specified language for deployment."""
    # Create language-specific workflow agents
    generation_pipeline, refinement_loop = create_workflow_agents_deployed(language)
    result_summarizer = create_result_summarizer_agent_deployed()
    
    # The root_agent is now a SequentialAgent that controls the deterministic high-level workflow.
    return SequentialAgent(
        name="CoordinatorAgent",
        description="The master orchestrator for the autonomous test suite generation system (deployed version).",
        sub_agents=[
            generation_pipeline,
            refinement_loop,
            result_summarizer,
        ],
        before_agent_callback=initialize_state_deployed
    )

# Default root agent for deployment
root_agent = create_root_agent_deployed("python")
