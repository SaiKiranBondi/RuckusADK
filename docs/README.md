# TestMozart - Autonomous Test Suite Generation System

![TestMozart Architecture](image.png)

TestMozart is an intelligent, autonomous system that automatically generates comprehensive test suites for Python code using Google's Agent Development Kit (ADK). The system employs a multi-agent architecture where specialized AI agents collaborate to analyze code, design test scenarios, implement tests, and refine them until they pass.

## 🎯 Overview

TestMozart transforms any Python source code into a complete, executable test suite through a sophisticated pipeline of AI agents. Each agent has a specific role and expertise, working together to ensure high-quality, comprehensive test coverage.

## 🏗️ System Architecture

The system follows a hierarchical agent architecture with the following components:

### Core Agents

1. **CodeAnalyzer** - Performs static analysis of source code
2. **TestCaseDesigner** - Generates abstract test scenarios
3. **TestImplementer** - Converts scenarios into executable test code
4. **TestRunner** - Executes tests in a sandboxed environment
5. **DebuggerAndRefiner** - Fixes failing tests through iterative refinement
6. **ResultSummarizer** - Formats and presents final results

### Workflow Structure

```
main.py → CoordinatorAgent → [GenerationPipeline → RefinementLoop → ResultSummarizer]
```

## 📁 Project Structure

```
testmozart/
├── main.py                          # Entry point and orchestration
├── sample_code.py                   # Example code to test (Calculator class)
├── agents/                          # AI agent implementations
│   ├── __init__.py
│   ├── coordinator.py              # Main workflow coordinator
│   ├── code_analyzer.py            # Static code analysis agent
│   ├── test_case_designer.py       # Test scenario generation agent
│   ├── test_implementer.py         # Test code implementation agent
│   ├── test_runner.py              # Test execution agent
│   └── debugger_and_refiner.py     # Test debugging and refinement agent
├── tools/                          # Specialized tools for each agent
│   ├── __init__.py
│   ├── code_analysis_tools.py      # AST parsing and code structure analysis
│   ├── test_design_tools.py        # Test scenario parsing and validation
│   ├── test_implementation_tools.py # Test code boilerplate generation
│   ├── test_execution_tools.py     # Sandboxed test execution and result parsing
│   └── workflow_tools.py           # Loop control and workflow management
├── requirements.txt                # Python dependencies
├── image.png                       # System architecture diagram
└── mermaid.md                      # Mermaid diagram source
```

## 🔄 Detailed Workflow

### Phase 1: Generation Pipeline (Sequential)

1. **State Initialization**
   - Parses user input (source code + language)
   - Initializes shared state for agent communication

2. **Code Analysis**
   - Uses AST parsing to extract code structure
   - Identifies classes, methods, functions, parameters, and type hints
   - Generates structured JSON report

3. **Test Scenario Design**
   - Analyzes code structure to generate comprehensive test scenarios
   - Covers happy path, edge cases, and error handling
   - Outputs structured test scenarios in natural language

4. **Test Implementation**
   - Converts abstract scenarios into executable pytest code
   - Generates proper imports and test function skeletons
   - Creates complete, runnable test file

### Phase 2: Refinement Loop (Iterative, max 3 attempts)

5. **Test Execution**
   - Creates isolated virtual environment
   - Executes tests against source code
   - Captures detailed results and failures

6. **Debugging and Refinement**
   - Analyzes test failures and error messages
   - Automatically fixes issues in test code
   - Iterates until tests pass or max attempts reached

### Phase 3: Finalization

7. **Result Summarization**
   - Formats final test suite
   - Corrects import statements for final output
   - Saves to `final_test_suite.py`

## 🛠️ Key Components

### Agent Specializations

- **CodeAnalyzer**: Uses AST parsing for accurate code structure analysis
- **TestCaseDesigner**: Leverages LLM creativity for comprehensive test coverage
- **TestImplementer**: Combines structured scenarios with code generation
- **TestRunner**: Provides secure, isolated test execution
- **DebuggerAndRefiner**: Applies debugging expertise to fix test issues

### Tool Ecosystem

- **AST Parser**: Extracts detailed code structure information
- **Scenario Parser**: Converts natural language to structured test scenarios
- **Sandbox Executor**: Runs tests in isolated virtual environments
- **Result Parser**: Extracts meaningful information from test outputs
- **Loop Controller**: Manages iterative refinement process

## 📊 Sample Execution Trace

### Input: `sample_code.py`
```python
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

def greet(name: str) -> str:
    return f"Hello, {name}"
```

### Expected Output Flow:

1. **Code Analysis Result**:
```json
{
  "status": "success",
  "structure": [
    {
      "type": "class",
      "name": "Calculator",
      "methods": [
        {
          "name": "add",
          "parameters": [{"name": "a", "annotation": "int"}, {"name": "b", "annotation": "int"}],
          "return_type": "int"
        }
      ]
    },
    {
      "type": "function",
      "name": "greet",
      "parameters": [{"name": "name", "annotation": "str"}],
      "return_type": "str"
    }
  ]
}
```

2. **Generated Test Scenarios**:
```
SCENARIO: Test the 'add' method with two positive integers.
EXPECTED: The method should return the correct sum of the two integers.
---
SCENARIO: Test the 'add' method with zero values.
EXPECTED: The method should return zero.
---
SCENARIO: Test the 'greet' function with a valid name.
EXPECTED: The function should return a proper greeting message.
```

3. **Final Test Suite**:
```python
import pytest
from sample_code import Calculator, greet

def test_add_positive_integers():
    """Tests: Test the 'add' method with two positive integers.
    Expected Outcome: The method should return the correct sum of the two integers."""
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5

def test_add_zero_values():
    """Tests: Test the 'add' method with zero values.
    Expected Outcome: The method should return zero."""
    calc = Calculator()
    result = calc.add(0, 0)
    assert result == 0

def test_greet_valid_name():
    """Tests: Test the 'greet' function with a valid name.
    Expected Outcome: The function should return a proper greeting message."""
    result = greet("Alice")
    assert result == "Hello, Alice"
```

## 🔧 Technical Features

### State Management
- Shared state across agents using ADK's session service
- Persistent data flow between pipeline stages
- Automatic state initialization and cleanup

### Error Handling
- Graceful handling of syntax errors in source code
- Robust parsing of test execution results
- Automatic retry mechanism for failed tests

### Security
- Sandboxed test execution in temporary virtual environments
- Isolated file system operations
- No persistent changes to host system

### Extensibility
- Modular agent architecture
- Pluggable tool system
- Support for multiple programming languages (Python implemented)

## 🎨 Architecture Diagram

The system architecture is visualized in `image.png`, showing:
- Agent hierarchy and relationships
- Data flow between components
- State management and tool interactions
- Loop control and iteration logic

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment**:
   - Create `.env` file with `GOOGLE_API_KEY=your_api_key`
   - Ensure `sample_code.py` contains code to test

3. **Run the System**:
   ```bash
   python main.py
   ```

4. **Check Results**:
   - Review console output for execution trace
   - Find generated tests in `final_test_suite.py`

## 🔍 Key Benefits

- **Autonomous**: No human intervention required after initial setup
- **Comprehensive**: Covers multiple test scenarios automatically
- **Reliable**: Iterative refinement ensures working test code
- **Secure**: Sandboxed execution prevents system damage
- **Extensible**: Easy to add new agents or modify existing ones

## 📈 Future Enhancements

- Support for additional programming languages
- Integration with CI/CD pipelines
- Advanced test coverage metrics
- Custom test framework support
- Performance benchmarking capabilities

---

*TestMozart represents the future of automated testing, combining the power of AI agents with robust software engineering practices to deliver comprehensive, reliable test suites with minimal human intervention.*
