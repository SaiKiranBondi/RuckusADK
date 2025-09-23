# TestMozart Usage Guide

This guide provides step-by-step instructions for running TestMozart and understanding what to expect at each stage of the autonomous test generation process.

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- Internet connection (for Google AI API access)
- Windows, macOS, or Linux operating system

### Required Setup
1. **Google AI API Key**: Obtain from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Python Environment**: Virtual environment recommended

## 🚀 Quick Start

### Step 1: Environment Setup

```bash
# Clone or download the project
cd testmozart

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: API Configuration

Create a `.env` file in the project root:
```bash
# .env
GOOGLE_API_KEY=your_actual_api_key_here
```

### Step 3: Prepare Test Code

Ensure `sample_code.py` contains the code you want to test. The default file includes:

```python
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

def greet(name: str) -> str:
    return f"Hello, {name}"
```

### Step 4: Run TestMozart

```bash
python main.py
```

## 📊 Detailed Execution Flow

### Stage 1: System Initialization
**What happens:**
- Loads source code from `sample_code.py`
- Creates ADK session and runner
- Initializes shared state for agent communication

**Expected output:**
```
--- Starting Autonomous Test Suite Generation System ---

[USER REQUEST] Generating tests for:
---
[Your source code here]
---

--- SYSTEM EXECUTION LOG ---
```

**Duration:** 2-5 seconds

### Stage 2: Code Analysis (CodeAnalyzer Agent)
**What happens:**
- Parses source code using Abstract Syntax Tree (AST)
- Extracts classes, methods, functions, parameters, and type hints
- Generates structured JSON report

**Expected output:**
```
[CodeAnalyzer]: Static analysis complete.
```

**What's happening behind the scenes:**
- AST parsing identifies all code elements
- Type annotations are extracted
- Docstrings are captured
- Structure is converted to JSON format

**Duration:** 3-8 seconds

### Stage 3: Test Scenario Design (TestCaseDesigner Agent)
**What happens:**
- Analyzes code structure to generate comprehensive test scenarios
- Covers happy path, edge cases, and error handling
- Creates natural language test descriptions

**Expected output:**
```
[TestCaseDesigner]: [Generated test scenarios in natural language]
```

**Sample scenarios generated:**
```
SCENARIO: Test the 'add' method with two positive integers.
EXPECTED: The method should return the correct sum of the two integers.
---
SCENARIO: Test the 'add' method with zero values.
EXPECTED: The method should return zero.
---
SCENARIO: Test the 'greet' function with an empty string.
EXPECTED: The function should return 'Hello, '.
```

**Duration:** 10-20 seconds

### Stage 4: Test Implementation (TestImplementer Agent)
**What happens:**
- Converts abstract scenarios into executable pytest code
- Generates proper imports and test function skeletons
- Creates complete, runnable test file

**Expected output:**
```
[TestImplementer]: [Complete Python test code]
```

**Sample generated code:**
```python
import pytest
from source_to_test import Calculator, greet

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
```

**Duration:** 15-30 seconds

### Stage 5: Test Execution (TestRunner Agent)
**What happens:**
- Creates isolated virtual environment
- Installs pytest and dependencies
- Executes tests against source code
- Captures detailed results

**Expected output:**
```
[TestRunner]: {"status": "PASS", "summary": "2 passed", "failures": []}
```

**What's happening behind the scenes:**
- Temporary directory creation
- Virtual environment setup
- File creation (source_to_test.py, test_generated.py)
- pytest execution
- Result parsing

**Duration:** 10-25 seconds

### Stage 6: Debugging and Refinement (DebuggerAndRefiner Agent)
**What happens:**
- Analyzes test results
- If tests pass: exits loop
- If tests fail: fixes issues and iterates

**Expected output (if tests pass):**
```
[DebuggerAndRefiner]: Loop exit signal sent. The task is complete.
```

**Expected output (if tests fail):**
```
[DebuggerAndRefiner]: [Corrected test code]
```

**Duration:** 5-15 seconds per iteration (max 3 iterations)

### Stage 7: Result Summarization (ResultSummarizer Agent)
**What happens:**
- Formats final test suite
- Corrects import statements (source_to_test → sample_code)
- Prepares final output

**Expected output:**
```
[ResultSummarizer]: ```python
import pytest
from sample_code import Calculator, greet

def test_add_positive_integers():
    # ... complete test code ...
```

**Duration:** 5-10 seconds

### Stage 8: File Output
**What happens:**
- Extracts Python code from final response
- Saves to `final_test_suite.py`

**Expected output:**
```
--- SYSTEM EXECUTION COMPLETE ---

--- FINAL RESULT ---
[Complete test suite code]

--- Final test suite saved to `final_test_suite.py` ---
```

**Duration:** 1-2 seconds

## 🔍 Understanding Output Files

### `final_test_suite.py`
Contains the complete, executable test suite:
- Proper imports from `sample_code`
- All test functions with descriptive names
- Comprehensive assertions
- Ready to run with `pytest final_test_suite.py`

### Console Output
- Real-time agent communication
- Detailed execution trace
- Error messages and debugging information
- Final formatted results

## ⚠️ Troubleshooting

### Common Issues

**1. API Key Error**
```
Error: Invalid API key
```
**Solution:** Verify `.env` file contains correct `GOOGLE_API_KEY`

**2. File Not Found**
```
Error: `sample_code.py` not found
```
**Solution:** Ensure `sample_code.py` exists in project root

**3. Import Errors in Generated Tests**
```
ImportError: No module named 'source_to_test'
```
**Solution:** This is normal during execution; final output corrects imports

**4. Test Failures**
```
[DebuggerAndRefiner]: [Corrected code after analysis]
```
**Solution:** System automatically fixes issues; monitor for successful completion

### Performance Expectations

**Total Runtime:** 1-3 minutes for typical code
**Factors affecting speed:**
- Code complexity
- Number of test scenarios
- API response times
- System performance

## 📈 Success Indicators

### ✅ Successful Execution
- All agents complete without errors
- Final test suite saved to file
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

## 📊 Expected Test Coverage

For the sample `Calculator` class and `greet` function:
- **Happy path tests**: Normal operation scenarios
- **Edge case tests**: Boundary values, empty inputs
- **Error handling tests**: Invalid input types
- **Integration tests**: Multiple function interactions

## 🚀 Next Steps

After successful execution:
1. Review `final_test_suite.py`
2. Run tests manually: `pytest final_test_suite.py`
3. Integrate into your development workflow
4. Customize tests for specific requirements
5. Add to your CI/CD pipeline

---

*This guide covers the complete TestMozart workflow. For advanced usage and customization, refer to the main README.md file.*
