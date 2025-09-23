# Google ADK Syntax Guide for TestMozart

This guide explains the Google Agent Development Kit (ADK) syntax and concepts used throughout the TestMozart codebase. It covers agent types, tool definitions, state management, and multi-agent workflows.

## 📚 Table of Contents

1. [Agent Types](#agent-types)
2. [Tool Definitions](#tool-definitions)
3. [State Management](#state-management)
4. [Multi-Agent Workflows](#multi-agent-workflows)
5. [Callbacks and Context](#callbacks-and-context)
6. [Code Examples from TestMozart](#code-examples-from-testmozart)

## 🤖 Agent Types

### 1. LlmAgent
The basic AI agent that uses Large Language Models for processing.

```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="AgentName",                    # Unique identifier
    description="What this agent does",  # Human-readable description
    model="gemini-2.5-pro",             # LLM model to use
    instruction="""                     # System prompt/instructions
        You are an expert in...
        Your task is to...
    """,
    tools=[tool1, tool2],               # List of available tools
    output_key="state_variable_name"    # Where to save output
)
```

**Example from TestMozart:**
```python
# agents/code_analyzer.py
code_analyzer_agent = LlmAgent(
    name="CodeAnalyzer",
    description="Performs deep, accurate static analysis of source code",
    model="gemini-2.5-flash",
    instruction="""
        You are a specialized agent for static code analysis. 
        Your sole responsibility is to receive a block of source code 
        and call the `analyze_code_structure` tool.
    """,
    tools=[analyze_code_structure]
)
```

### 2. SequentialAgent
Executes sub-agents in a specific order, one after another.

```python
from google.adk.agents import SequentialAgent

sequential_agent = SequentialAgent(
    name="SequentialWorkflow",
    description="Executes agents in order",
    sub_agents=[agent1, agent2, agent3],  # List of agents to run
    before_agent_callback=init_function,   # Optional: runs before each agent
    after_agent_callback=cleanup_function  # Optional: runs after each agent
)
```

**Example from TestMozart:**
```python
# agents/coordinator.py
generation_pipeline = SequentialAgent(
    name="GenerationPipeline",
    description="Analyzes code and designs test scenarios in sequence",
    sub_agents=[
        code_analyzer_agent,
        test_case_designer_agent,
        test_implementer_agent,
    ]
)
```

### 3. LoopAgent
Repeats a sequence of agents until a condition is met or max iterations reached.

```python
from google.adk.agents import LoopAgent

loop_agent = LoopAgent(
    name="IterativeWorkflow",
    description="Repeats agents until condition met",
    sub_agents=[agent1, agent2],  # Agents to repeat
    max_iterations=3              # Maximum number of loops
)
```

**Example from TestMozart:**
```python
# agents/coordinator.py
refinement_loop = LoopAgent(
    name="RefinementLoop",
    description="Iterative workflow for test refinement",
    sub_agents=[
        test_runner_agent,
        debugger_and_refiner_agent
    ],
    max_iterations=3
)
```

## 🛠️ Tool Definitions

### Basic Tool Structure
Tools are functions that agents can call to perform specific tasks.

```python
from google.adk.tools.base_tool import BaseTool
from pydantic import BaseModel, Field

class ToolInput(BaseModel):
    """Input schema for the tool"""
    parameter1: str = Field(..., description="Description of parameter")
    parameter2: int = Field(default=0, description="Optional parameter")

def tool_function(parameter1: str, parameter2: int = 0) -> dict:
    """
    Tool function that performs a specific task.
    
    Args:
        parameter1: Description of what this parameter does
        parameter2: Description of optional parameter
        
    Returns:
        Dictionary with results
    """
    # Tool implementation
    return {"status": "success", "result": "data"}

# Create the tool
tool = BaseTool(
    name="tool_name",
    description="What this tool does",
    func=tool_function,
    args_schema=ToolInput
)
```

**Example from TestMozart:**
```python
# tools/code_analysis_tools.py
def analyze_code_structure(source_code: str, language: str) -> Dict[str, Any]:
    """
    Parses source code into a structured JSON representation.
    
    Args:
        source_code: The source code to be analyzed
        language: The programming language (e.g., 'python')
        
    Returns:
        A JSON-serializable dictionary representing the code structure
    """
    if language.lower() == 'python':
        try:
            tree = ast.parse(source_code)
            visitor = CodeVisitor()
            visitor.visit(tree)
            return {"status": "success", "structure": visitor.structure}
        except SyntaxError as e:
            return {"status": "error", "message": f"Python syntax error: {e}"}
```

### Tool with Callback
Tools can have callbacks to handle results automatically.

```python
def tool_callback(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict):
    """
    Callback function that processes tool results.
    
    Args:
        tool: The tool that was called
        args: Arguments passed to the tool
        tool_context: Context with state and actions
        tool_response: Response from the tool
    """
    # Process the response
    tool_context.state['result'] = tool_response
    return types.Content(parts=[types.Part(text="Tool completed successfully")])

# Attach callback to agent
agent.after_tool_callback = tool_callback
```

**Example from TestMozart:**
```python
# agents/coordinator.py
def save_analysis_to_state(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict):
    """Saves tool output to state and ends agent turn."""
    if tool.name == 'analyze_code_structure':
        tool_context.state['static_analysis_report'] = tool_response
        return types.Content(parts=[types.Part(text="Static analysis complete.")])

# Attach to agent
code_analyzer_agent.after_tool_callback = save_analysis_to_state
```

## 🔄 State Management

### Shared State
Agents communicate through shared state variables.

```python
# Setting state
callback_context.state['variable_name'] = value

# Reading state
value = callback_context.state.get('variable_name', default_value)

# State in agent instructions
agent.instruction = """
    You will receive data in the `{state_variable}` state variable.
    Process this data and save results to `{output_variable}`.
"""
```

**Example from TestMozart:**
```python
# agents/coordinator.py
def initialize_state(callback_context: CallbackContext):
    """Parses initial user message and populates session state."""
    user_content = callback_context.user_content
    if user_content and user_content.parts:
        try:
            initial_data = json.loads(user_content.parts[0].text)
            callback_context.state['source_code'] = initial_data.get('source_code')
            callback_context.state['language'] = initial_data.get('language')
        except (json.JSONDecodeError, AttributeError):
            callback_context.state['source_code'] = user_content.parts[0].text
            callback_context.state['language'] = 'python'
```

### State Flow Between Agents
```python
# Agent 1: Saves to state
agent1.output_key = "analysis_result"

# Agent 2: Reads from state
agent2.instruction = """
    You will receive the analysis in the `{analysis_result}` state variable.
    Process this data and save to `{processed_result}`.
"""
agent2.output_key = "processed_result"
```

## 🔗 Multi-Agent Workflows

### Hierarchical Agent Structure
```python
# Root agent coordinates everything
root_agent = SequentialAgent(
    name="RootCoordinator",
    description="Main orchestrator",
    sub_agents=[
        phase1_pipeline,    # SequentialAgent
        phase2_loop,        # LoopAgent
        final_agent         # LlmAgent
    ],
    before_agent_callback=initialize_state
)

# Phase 1: Sequential pipeline
phase1_pipeline = SequentialAgent(
    name="Phase1",
    sub_agents=[agent1, agent2, agent3]
)

# Phase 2: Iterative loop
phase2_loop = LoopAgent(
    name="Phase2",
    sub_agents=[agent4, agent5],
    max_iterations=3
)
```

**Example from TestMozart:**
```python
# agents/coordinator.py
root_agent = SequentialAgent(
    name="CoordinatorAgent",
    description="Master orchestrator for autonomous test generation",
    sub_agents=[
        generation_pipeline,    # SequentialAgent
        refinement_loop,        # LoopAgent
        result_summarizer_agent # LlmAgent
    ],
    before_agent_callback=initialize_state
)
```

### Agent Communication Patterns

#### 1. Producer-Consumer Pattern
```python
# Producer agent
producer.instruction = "Generate data and save to `{output_data}`"
producer.output_key = "output_data"

# Consumer agent
consumer.instruction = "Process data from `{output_data}` and save to `{processed_data}`"
consumer.output_key = "processed_data"
```

#### 2. Pipeline Pattern
```python
pipeline = SequentialAgent(
    sub_agents=[
        data_loader,      # Loads data
        data_processor,   # Processes data
        data_analyzer,    # Analyzes data
        data_reporter     # Reports results
    ]
)
```

#### 3. Iterative Refinement Pattern
```python
refinement_loop = LoopAgent(
    sub_agents=[
        executor,         # Executes task
        evaluator,        # Evaluates results
        refiner          # Refines based on evaluation
    ],
    max_iterations=3
)
```

## 📞 Callbacks and Context

### CallbackContext
Provides access to user input, state, and actions.

```python
def callback_function(callback_context: CallbackContext):
    # Access user input
    user_content = callback_context.user_content
    user_text = user_content.parts[0].text if user_content.parts else ""
    
    # Access and modify state
    callback_context.state['key'] = 'value'
    existing_value = callback_context.state.get('key', 'default')
    
    # Access actions (for tool context)
    if hasattr(callback_context, 'actions'):
        callback_context.actions.escalate = True  # Exit loop
```

### ToolContext
Provides access to state and actions within tool callbacks.

```python
def tool_callback(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict):
    # Access state
    tool_context.state['result'] = tool_response
    
    # Control flow
    tool_context.actions.escalate = True  # Exit current loop
    
    # Return content
    return types.Content(parts=[types.Part(text="Success")])
```

## 💻 Code Examples from TestMozart

### 1. Complete Agent Definition
```python
# agents/test_case_designer.py
from google.adk.agents import LlmAgent
from tools.test_design_tools import generate_test_scenarios

test_case_designer_agent = LlmAgent(
    name="TestCaseDesigner",
    description="Generates comprehensive abstract test scenarios",
    model="gemini-2.5-pro",
    instruction="""
        You are an expert Senior Software Engineer in Test. 
        Your task is to design abstract test scenarios based on a static analysis report.
        
        The report is provided as a JSON object in the user's message.
        
        Your goal is to brainstorm a comprehensive list of test scenarios for each 
        function and method in the report.
        
        Consider the following categories:
        1. Happy Path: Test with typical, valid inputs
        2. Edge Cases: Test with boundary values
        3. Error Handling: Test how the code handles invalid inputs
        
        IMPORTANT: You MUST format your output as a plain text string.
        For each scenario, provide a 'SCENARIO' and an 'EXPECTED' outcome, separated by '---'.
        
        After generating the natural language scenarios, you MUST call the 
        `generate_test_scenarios` tool to structure your output.
    """,
    tools=[generate_test_scenarios]
)
```

### 2. Dynamic Instruction Generation
```python
# agents/coordinator.py
async def build_test_runner_instruction(ctx: CallbackContext) -> str:
    """Dynamically creates the prompt for the test runner with code from state."""
    source_code = ctx.state.get('source_code', '')
    generated_code = ctx.state.get('generated_test_code', '')

    source_code_json_str = json.dumps(source_code)
    generated_code_json_str = json.dumps(generated_code)
    
    return f"""
    You are a highly reliable test execution engine. Your task is to execute a test suite against source code.

    First, call the `execute_tests_sandboxed` tool with the following two arguments:
    - `source_code_under_test`: Set this to the string {source_code_json_str}
    - `generated_test_code`: Set this to the string {generated_code_json_str}

    Second, take the entire, raw JSON output from `execute_tests_sandboxed` and immediately 
    pass it as the `raw_execution_output` argument to the `parse_test_results` tool.
    
    Your final output must be only the structured JSON object returned by the 
    `parse_test_results` tool. Do not add any commentary or explanation.
    """

# Assign dynamic instruction
test_runner_agent.instruction = build_test_runner_instruction
```

### 3. Loop Control with Tools
```python
# tools/workflow_tools.py
from google.adk.tools import ToolContext

def exit_loop(tool_context: ToolContext):
    """
    Exits the current agent loop. Call this tool when a task is successfully
    completed or a terminal condition is met.
    """
    # Setting escalate to True signals to a LoopAgent that it should stop iterating
    tool_context.actions.escalate = True
    return "Loop exit signal sent. The task is complete."

# Add to agent
debugger_and_refiner_agent.tools.append(exit_loop)
```

### 4. State-Based Agent Configuration
```python
# agents/coordinator.py
# Configure agents to read from and write to specific state variables

# TestCaseDesigner: Read from `static_analysis_report`, save to `test_scenarios`
test_case_designer_agent.instruction += "\n\nYou will receive the static analysis report in the `{static_analysis_report}` state variable."
test_case_designer_agent.output_key = "test_scenarios"

# TestImplementer: Read from `test_scenarios`, save to `generated_test_code`
test_implementer_agent.instruction += "\n\nYou will receive the test scenarios in the `{test_scenarios}` state variable."
test_implementer_agent.output_key = "generated_test_code"

# TestRunner: Read `source_code` & `generated_test_code`, save to `test_results`
test_runner_agent.output_key = "test_results"
```

## 🎯 Best Practices

### 1. Agent Design
- **Single Responsibility**: Each agent should have one clear purpose
- **Clear Instructions**: Provide detailed, specific instructions
- **Appropriate Models**: Use faster models for simple tasks, powerful models for complex ones
- **Tool Integration**: Provide agents with the tools they need

### 2. State Management
- **Descriptive Names**: Use clear, descriptive state variable names
- **Default Values**: Always provide defaults when reading state
- **State Flow**: Design clear data flow between agents
- **State Validation**: Validate state data before processing

### 3. Error Handling
- **Graceful Degradation**: Handle errors without crashing the workflow
- **Error Propagation**: Pass error information through state
- **Retry Logic**: Use LoopAgent for retry mechanisms
- **Fallback Values**: Provide fallback values for missing state

### 4. Performance
- **Model Selection**: Choose appropriate models for each task
- **Parallel Processing**: Use SequentialAgent for dependent tasks, consider parallel for independent ones
- **State Efficiency**: Minimize state size and complexity
- **Tool Optimization**: Make tools efficient and focused

## 🔧 Common Patterns

### 1. Data Processing Pipeline
```python
pipeline = SequentialAgent(
    sub_agents=[
        data_loader,      # Loads raw data
        data_cleaner,     # Cleans data
        data_analyzer,    # Analyzes data
        data_reporter     # Generates report
    ]
)
```

### 2. Iterative Refinement
```python
refinement_loop = LoopAgent(
    sub_agents=[
        executor,         # Executes task
        evaluator,        # Evaluates results
        refiner          # Refines based on evaluation
    ],
    max_iterations=3
)
```

### 3. Conditional Workflow
```python
def conditional_callback(ctx: CallbackContext):
    if ctx.state.get('condition'):
        # Route to different agents based on condition
        pass

conditional_agent = SequentialAgent(
    sub_agents=[agent1, agent2],
    before_agent_callback=conditional_callback
)
```

---

*This guide covers the essential ADK syntax and patterns used in TestMozart. For more advanced features and patterns, refer to the official Google ADK documentation.*
