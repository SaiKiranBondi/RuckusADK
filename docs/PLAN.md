# TestMozart Multi-Language Support Plan

## 🎯 Objective
Extend TestMozart to support both Python and C code generation while maintaining the existing workflow architecture.

## 📋 Current System Analysis
- **Current Language**: Python only
- **Parser**: AST-based Python parser in `tools/code_analysis_tools.py`
- **Test Framework**: pytest
- **Workflow**: 6-agent pipeline (unchanged)

## 🚀 Action Items

### 1. **Language Detection & Configuration**
**Files to Modify:**
- `main.py` - Add language detection logic
- `agents/coordinator.py` - Update state initialization

**Changes:**
- Add file extension detection (`.py` → Python, `.c` → C)
- Update `initialize_state()` to detect language automatically
- Add language-specific configuration

### 2. **Code Analysis Tools Enhancement**
**Files to Modify:**
- `tools/code_analysis_tools.py` - Add C parser support
- `tools/c_analysis_tools.py` - **NEW FILE** - Isolated C-specific analysis

**New Parser Requirements:**
- **Keep**: Existing Python AST parser (unchanged)
- **Add**: Separate C parser using `pycparser` library
- **Add**: Language-specific visitor classes in isolated files

**Implementation:**
```python
# Add to requirements.txt
pycparser>=2.21

# NEW FILE: tools/c_analysis_tools.py
class CCodeVisitor(c_ast.NodeVisitor):
    def visit_FuncDef(self, node):
        # Extract C function definitions
    def visit_Decl(self, node):
        # Extract variable declarations

def analyze_c_code_structure(source_code: str) -> Dict[str, Any]:
    # C-specific analysis logic
    pass
```

### 3. **Test Framework Selection**
**Files to Modify:**
- `tools/test_implementation_tools.py` - Add conditional logic
- `tools/c_test_implementation_tools.py` - **NEW FILE** - Isolated C test generation
- `tools/test_execution_tools.py` - Add conditional logic
- `tools/c_test_execution_tools.py` - **NEW FILE** - Isolated C test execution

**C Test Framework Options:**
- **Unity** (recommended) - Lightweight C testing framework
- **CUnit** - Alternative option
- **Custom C test runner** - Simple assert-based approach

**Implementation:**
- **Keep**: Existing Python functions (unchanged)
- **Add**: Separate C functions in isolated files
- **Add**: Conditional logic in main files

### 4. **Test Execution Tools Enhancement**
**Files to Modify:**
- `tools/test_execution_tools.py` - Add conditional logic only
- `tools/c_test_execution_tools.py` - **NEW FILE** - Isolated C execution logic

**C Execution Process:**
1. Compile C source code to object file
2. Compile test code to object file
3. Link both with test framework
4. Execute and capture results

**Implementation:**
```python
# NEW FILE: tools/c_test_execution_tools.py
def execute_c_tests_sandboxed(source_code: str, test_code: str) -> Dict[str, Any]:
    # 1. Create source.c and test.c files
    # 2. Compile with gcc
    # 3. Link with Unity framework
    # 4. Execute and parse results
    pass

def parse_c_test_results(raw_execution_output: Dict[str, Any]) -> Dict[str, Any]:
    # C-specific result parsing
    pass
```

### 5. **Agent Instructions Updates**
**Files to Modify:**
- `agents/test_implementer.py` - Add conditional tool selection
- `agents/test_runner.py` - Add conditional tool selection
- `agents/debugger_and_refiner.py` - Add conditional tool selection

**Changes:**
- **Keep**: Existing Python instructions (unchanged)
- **Add**: Conditional logic to select appropriate tools based on language
- **Add**: Language-specific tool imports

### 6. **State Management Updates**
**Files to Modify:**
- `agents/coordinator.py` - Add language-specific state handling

**New State Variables:**
- `target_language` - Detected language (python/c)
- `test_framework` - Selected framework (pytest/unity)
- `compilation_flags` - C-specific compilation options

### 7. **File Structure Updates**
**New Files to Create:**
- `examples/sample_code.c` - C sample code
- `tools/c_analysis_tools.py` - C-specific analysis tools
- `tools/c_test_implementation_tools.py` - C test generation tools
- `tools/c_test_execution_tools.py` - C test execution tools

**Files to Modify:**
- `requirements.txt` - Add pycparser dependency
- `main.py` - Update file detection logic
- `tools/code_analysis_tools.py` - Add conditional logic
- `tools/test_implementation_tools.py` - Add conditional logic
- `tools/test_execution_tools.py` - Add conditional logic

## 🔄 Updated Workflow Flow

### **Phase 1: Language Detection & Analysis**
```
main.py → Language Detection → CodeAnalyzer → Language-Specific Parser
```

### **Phase 2: Test Generation (Language-Agnostic)**
```
TestCaseDesigner → TestImplementer → Language-Specific Test Code
```

### **Phase 3: Test Execution (Language-Specific)**
```
TestRunner → Language-Specific Execution → DebuggerAndRefiner
```

## 📁 File Modification Details

### **main.py Changes**
```python
# Add language detection
def detect_language(file_path: str) -> str:
    if file_path.endswith('.py'):
        return 'python'
    elif file_path.endswith('.c'):
        return 'c'
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

# Update file loading logic
language = detect_language("sample_code.py" or "sample_code.c")
```

### **tools/code_analysis_tools.py Changes**
```python
# Add conditional logic only
from tools.c_analysis_tools import analyze_c_code_structure

def analyze_code_structure(source_code: str, language: str) -> Dict[str, Any]:
    if language.lower() == 'python':
        # Existing Python logic (unchanged)
        return analyze_python_code_structure(source_code)
    elif language.lower() == 'c':
        return analyze_c_code_structure(source_code)
    else:
        return {"status": "error", "message": f"Unsupported language: {language}"}
```

### **tools/c_analysis_tools.py (NEW FILE)**
```python
from pycparser import c_parser, c_ast

class CCodeVisitor(c_ast.NodeVisitor):
    def visit_FuncDef(self, node):
        # Extract C function information
        pass

def analyze_c_code_structure(source_code: str) -> Dict[str, Any]:
    # Parse C code and extract structure
    pass
```

### **tools/test_implementation_tools.py Changes**
```python
# Add conditional logic only
from tools.c_test_implementation_tools import write_c_test_code

def write_test_code(test_scenario: Dict[str, Any], target_framework: str, language: str) -> str:
    if language == 'python':
        # Existing Python logic (unchanged)
        return write_python_test_code(test_scenario, target_framework)
    elif language == 'c':
        return write_c_test_code(test_scenario)
```

### **tools/c_test_implementation_tools.py (NEW FILE)**
```python
def write_c_test_code(test_scenario: Dict[str, Any]) -> str:
    """Generate Unity-based C test code"""
    # Generate C test functions using Unity framework
    pass
```

### **tools/test_execution_tools.py Changes**
```python
# Add conditional logic only
from tools.c_test_execution_tools import execute_c_tests_sandboxed, parse_c_test_results

def execute_tests_sandboxed(source_code: str, generated_test_code: str, language: str) -> Dict[str, Any]:
    if language == 'python':
        # Existing Python logic (unchanged)
        return execute_python_tests_sandboxed(source_code, generated_test_code)
    elif language == 'c':
        return execute_c_tests_sandboxed(source_code, generated_test_code)

def parse_test_results(raw_execution_output: Dict[str, Any], language: str) -> Dict[str, Any]:
    if language == 'python':
        # Existing Python logic (unchanged)
        return parse_python_test_results(raw_execution_output)
    elif language == 'c':
        return parse_c_test_results(raw_execution_output)
```

### **tools/c_test_execution_tools.py (NEW FILE)**
```python
def execute_c_tests_sandboxed(source_code: str, test_code: str) -> Dict[str, Any]:
    """Execute C tests using Unity framework"""
    # 1. Create source.c and test.c
    # 2. Compile with gcc
    # 3. Link with Unity
    # 4. Execute and capture results
    pass

def parse_c_test_results(raw_execution_output: Dict[str, Any]) -> Dict[str, Any]:
    # C-specific result parsing
    pass
```

## 🛠️ Implementation Steps

### **Step 1: Dependencies & Setup**
1. Add `pycparser>=2.21` to `requirements.txt`
2. Install Unity C testing framework
3. Create `examples/sample_code.c` with sample C code

### **Step 2: Create Isolated C Tools**
1. Create `tools/c_analysis_tools.py` with C parser
2. Create `tools/c_test_implementation_tools.py` with C test generation
3. Create `tools/c_test_execution_tools.py` with C execution logic

### **Step 3: Add Conditional Logic**
1. Update `tools/code_analysis_tools.py` with conditional imports
2. Update `tools/test_implementation_tools.py` with conditional logic
3. Update `tools/test_execution_tools.py` with conditional logic

### **Step 4: Agent Updates**
1. Update agent instructions for language awareness
2. Add conditional tool selection based on language
3. Update state management for language context

### **Step 5: Integration & Testing**
1. Test with Python code (existing functionality)
2. Test with C code (new functionality)
3. Verify both workflows work correctly

## 🎯 Success Criteria

- [ ] Python code analysis and test generation (existing functionality preserved)
- [ ] C code analysis and test generation (new functionality)
- [ ] Automatic language detection based on file extension
- [ ] Language-appropriate test frameworks (pytest for Python, Unity for C)
- [ ] Successful test execution for both languages
- [ ] Iterative refinement works for both languages
- [ ] Final output generation works for both languages

## 📝 Notes

- **Workflow Architecture**: No changes to the 6-agent pipeline
- **State Management**: Minimal changes, mostly additive
- **Backward Compatibility**: All existing Python functionality preserved
- **Isolation**: C-specific functionality completely isolated in separate files
- **Conditional Logic**: Clean separation with conditional checks in main files
- **Extensibility**: Framework designed to easily add more languages in the future

## 🏗️ File Organization

### **Existing Files (Minimal Changes)**
- `tools/code_analysis_tools.py` - Add conditional logic only
- `tools/test_implementation_tools.py` - Add conditional logic only
- `tools/test_execution_tools.py` - Add conditional logic only
- `agents/*.py` - Add conditional tool selection

### **New C-Specific Files (Isolated)**
- `tools/c_analysis_tools.py` - C parser and analysis
- `tools/c_test_implementation_tools.py` - C test generation
- `tools/c_test_execution_tools.py` - C test execution
- `examples/sample_code.c` - C sample code

### **Benefits of This Approach**
- ✅ **Clean Separation**: C logic completely isolated
- ✅ **No Jumbling**: Existing Python code untouched
- ✅ **Easy Maintenance**: C-specific changes in dedicated files
- ✅ **Conditional Logic**: Simple if/else statements for language selection
- ✅ **Extensibility**: Easy to add more languages following same pattern

## 🚀 Future Enhancements

- Support for C++ code
- Support for Java code
- Support for JavaScript/TypeScript code
- Language-specific test coverage metrics
- Cross-language integration testing
