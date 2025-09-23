# TestMozart - Autonomous Test Suite Generation System

![TestMozart Architecture](docs/image.png)

TestMozart is an intelligent, autonomous system that automatically generates comprehensive test suites for Python code using Google's Agent Development Kit (ADK). The system employs a multi-agent architecture where specialized AI agents collaborate to analyze code, design test scenarios, implement tests, and refine them until they pass.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google AI API Key
- Virtual environment (recommended)

### Installation
```bash
# Clone the repository
cd testmozart

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up API key
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### Running TestMozart
```bash
python main.py
```

## 🏗️ System Architecture

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
├── main.py                          # Main entry point
├── run.py                           # Interactive launcher
├── requirements.txt                 # Python dependencies
├── agents/                          # AI agent implementations
│   ├── coordinator.py              # Main workflow coordinator
│   ├── code_analyzer.py            # Static code analysis agent
│   ├── test_case_designer.py       # Test scenario generation agent
│   ├── test_implementer.py         # Test code implementation agent
│   ├── test_runner.py              # Test execution agent
│   └── debugger_and_refiner.py     # Test debugging and refinement agent
├── tools/                          # Specialized tools for each agent
│   ├── code_analysis_tools.py      # AST parsing and code structure analysis
│   ├── test_design_tools.py        # Test scenario parsing and validation
│   ├── test_implementation_tools.py # Test code boilerplate generation
│   ├── test_execution_tools.py     # Sandboxed test execution and result parsing
│   └── workflow_tools.py           # Loop control and workflow management
├── docs/                           # Documentation
│   ├── README.md                   # Detailed system documentation
│   ├── USAGE_GUIDE.md              # Step-by-step usage instructions
│   ├── ARCHITECTURE_EXPLANATION.md # System architecture details
│   ├── mermaid.md                  # Mermaid diagram source
│   └── image.png                   # System architecture diagram
├── tests/                          # Generated test files
└── examples/                       # Example code to test
    └── sample_code.py              # Sample Calculator class and greet function
```

## 🔄 Detailed Workflow

### Phase 1: Generation Pipeline (Sequential)
1. **State Initialization** - Parses user input and initializes shared state
2. **Code Analysis** - Uses AST parsing to extract code structure
3. **Test Scenario Design** - Generates comprehensive test scenarios
4. **Test Implementation** - Converts scenarios into executable pytest code

### Phase 2: Refinement Loop (Iterative, max 3 attempts)
5. **Test Execution** - Creates isolated virtual environment and runs tests
6. **Debugging and Refinement** - Analyzes failures and fixes issues

### Phase 3: Finalization
7. **Result Summarization** - Formats final test suite and saves to file

## 📊 Sample Execution

### Input: `examples/sample_code.py`
```python
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

def greet(name: str) -> str:
    return f"Hello, {name}"
```

### Expected Output Flow:

**Stage 1: Code Analysis**
```
[CodeAnalyzer]: Static analysis complete.
```

**Stage 2: Test Scenario Design**
```
[TestCaseDesigner]: SCENARIO: Test the 'add' method with two positive integers.
EXPECTED: The method should return the correct sum of the two integers.
---
SCENARIO: Test the 'add' method with zero values.
EXPECTED: The method should return zero.
```

**Stage 3: Test Implementation**
```
[TestImplementer]: [Complete Python test code with 12 test functions]
```

**Stage 4: Test Execution**
```
[TestRunner]: {"status": "PASS", "summary": "12 passed", "failures": []}
```

**Stage 5: Final Output**
```
--- Final test suite saved to `tests/final_test_suite.py` ---
```

### Generated Test Suite
```python
import pytest
from sample_code import Calculator, greet

def test_add_positive_integers():
    """Tests: Test the 'add' method with two positive integers."""
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5

def test_add_zero_values():
    """Tests: Test the 'add' method with zero values."""
    calc = Calculator()
    result = calc.add(0, 0)
    assert result == 0

def test_greet_valid_name():
    """Tests: Test the 'greet' function with a valid name."""
    result = greet("Alice")
    assert result == "Hello, Alice"
```

## 🛠️ Key Features

### Agent Specializations
- **CodeAnalyzer**: Uses AST parsing for accurate code structure analysis
- **TestCaseDesigner**: Leverages LLM creativity for comprehensive test coverage
- **TestImplementer**: Combines structured scenarios with code generation
- **TestRunner**: Provides secure, isolated test execution
- **DebuggerAndRefiner**: Applies debugging expertise to fix test issues

### Technical Features
- **State Management**: Shared state across agents using ADK's session service
- **Error Handling**: Graceful handling of syntax errors and test failures
- **Security**: Sandboxed test execution in temporary virtual environments
- **Extensibility**: Modular agent architecture with pluggable tool system

## 🎮 Interactive Launcher

Use the interactive launcher for easy navigation:
```bash
python run.py
```

Choose from menu:
1. 🚀 Standard Version (main.py)
2. 📚 View Documentation
3. 🔧 Check Setup
4. 🚪 Exit

## ⚠️ Troubleshooting

### Common Issues

**API Errors (503/500)**
- These are temporary Google API issues
- Wait a few minutes and try again
- Check your API quota in [Google AI Studio](https://makersuite.google.com/app/apikey)

**File Not Found**
```
Error: `examples/sample_code.py` not found
```
**Solution:** Ensure the examples folder contains sample_code.py

**Import Errors in Generated Tests**
```
ImportError: No module named 'source_to_test'
```
**Solution:** This is normal during execution; final output corrects imports

### Performance Expectations
- **Total Runtime**: 1-3 minutes for typical code
- **Test Coverage**: Comprehensive (happy path, edge cases, error handling)
- **Success Rate**: High with automatic retry and refinement

## 🔍 Success Indicators

### ✅ Successful Execution
- All agents complete without errors
- Final test suite saved to `tests/final_test_suite.py`
- Tests pass when executed manually
- Console shows "Final test suite saved"

### ❌ Failed Execution
- Agent errors or timeouts
- No final output file created
- Persistent test failures after 3 iterations
- API quota exceeded

## 🎯 Best Practices

### For Source Code
- Use clear, descriptive function/class names
- Include type hints where possible
- Add docstrings for better analysis
- Keep functions focused and simple

### For Testing
- Review generated tests before use
- Add additional edge cases if needed
- Verify test coverage manually
- Run tests in your development environment

## 🔄 Iterative Improvement

The system learns from failures:
1. **First iteration**: Initial test implementation
2. **Second iteration**: Fixes import and syntax errors
3. **Third iteration**: Corrects logic and assertion errors
4. **Final output**: Best possible test suite

## 📈 Expected Test Coverage

For the sample `Calculator` class and `greet` function:
- **Happy path tests**: Normal operation scenarios
- **Edge case tests**: Boundary values, empty inputs
- **Error handling tests**: Invalid input types
- **Integration tests**: Multiple function interactions

## 🚀 Next Steps

After successful execution:
1. Review `tests/final_test_suite.py`
2. Run tests manually: `pytest tests/final_test_suite.py`
3. Integrate into your development workflow
4. Customize tests for specific requirements
5. Add to your CI/CD pipeline

## 🔧 Configuration

The system uses Google's ADK with the following models:
- **CodeAnalyzer**: gemini-2.5-flash (fast analysis)
- **TestCaseDesigner**: gemini-2.5-pro (creative scenarios)
- **TestImplementer**: gemini-2.5-pro (code generation)
- **TestRunner**: gemini-2.5-pro (execution)
- **DebuggerAndRefiner**: gemini-2.5-pro (debugging)

## 📚 Documentation

- **`docs/README.md`** - Detailed system documentation
- **`docs/USAGE_GUIDE.md`** - Step-by-step usage instructions
- **`docs/ARCHITECTURE_EXPLANATION.md`** - System architecture details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*TestMozart represents the future of automated testing, combining the power of AI agents with robust software engineering practices to deliver comprehensive, reliable test suites with minimal human intervention.*