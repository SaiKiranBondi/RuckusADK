# 📚 TestMozart Usage Examples

This guide shows you exactly how to use your deployed TestMozart system with real examples.

## 🌐 **Method 1: Web Interface (Easiest)**

### **Step 1: Access Your Web Interface**
1. Open your browser
2. Go to: `https://testmozart-web-xxxxx-uc.a.run.app` (your actual URL)
3. You'll see the TestMozart interface

### **Step 2: Upload a File**
1. **Drag & Drop**: Drag your `.py` or `.c` file onto the upload area
2. **OR Click to Select**: Click the upload area and select a file from your computer
3. Supported formats: `.py` (Python), `.c` (C)

### **Step 3: Generate Tests**
1. Click "🚀 Generate Tests"
2. Wait 1-3 minutes (you'll see progress updates)
3. Download the generated test file

---

## 📝 **Example 1: Python Calculator**

### **Input File** (`calculator.py`):
```python
class Calculator:
    def add(self, a, b):
        """Add two numbers"""
        return a + b
    
    def subtract(self, a, b):
        """Subtract two numbers"""
        return a - b
    
    def multiply(self, a, b):
        """Multiply two numbers"""
        return a * b
    
    def divide(self, a, b):
        """Divide two numbers"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
```

### **Upload Process**:
1. Save the code above as `calculator.py`
2. Go to your web interface
3. Drag & drop `calculator.py`
4. Click "Generate Tests"
5. Wait for processing
6. Download `final_test_suite.py`

### **Generated Output** (`final_test_suite.py`):
```python
import pytest
from calculator import Calculator

def test_add_positive_numbers():
    """Tests: Test the 'add' method with two positive integers.
    Expected Outcome: The method should return the correct sum of the two integers."""
    calc = Calculator()
    result = calc.add(5, 3)
    assert result == 8

def test_add_with_zero():
    """Tests: Test the 'add' method with a positive integer and zero.
    Expected Outcome: The method should return the positive integer itself."""
    calc = Calculator()
    result = calc.add(5, 0)
    assert result == 5

def test_subtract_positive_numbers():
    """Tests: Test the 'subtract' method with two positive integers.
    Expected Outcome: The method should return the correct difference."""
    calc = Calculator()
    result = calc.subtract(10, 3)
    assert result == 7

def test_multiply_positive_numbers():
    """Tests: Test the 'multiply' method with two positive integers.
    Expected Outcome: The method should return the correct product."""
    calc = Calculator()
    result = calc.multiply(4, 5)
    assert result == 20

def test_divide_positive_numbers():
    """Tests: Test the 'divide' method with two positive integers.
    Expected Outcome: The method should return the correct quotient."""
    calc = Calculator()
    result = calc.divide(15, 3)
    assert result == 5

def test_divide_by_zero():
    """Tests: Test the 'divide' method with zero as divisor.
    Expected Outcome: The method should raise a ValueError."""
    calc = Calculator()
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(10, 0)
```

### **Run the Tests**:
```bash
# Install pytest if not already installed
pip install pytest

# Run the generated tests
pytest final_test_suite.py -v
```

### **Expected Output**:
```
========================= test session starts =========================
test_add_positive_numbers PASSED
test_add_with_zero PASSED
test_subtract_positive_numbers PASSED
test_multiply_positive_numbers PASSED
test_divide_positive_numbers PASSED
test_divide_by_zero PASSED
========================= 6 passed in 0.02s =========================
```

---

## 🔧 **Example 2: C Math Functions**

### **Input File** (`math.c`):
```c
#include <stdio.h>
#include <stdlib.h>

// Simple math functions
int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int multiply(int a, int b) {
    return a * b;
}

int divide(int a, int b) {
    if (b == 0) {
        printf("Error: Division by zero\n");
        return 0;
    }
    return a / b;
}

// String function
char* greet(const char* name) {
    static char greeting[100];
    snprintf(greeting, sizeof(greeting), "Hello, %s!", name);
    return greeting;
}
```

### **Upload Process**:
1. Save the code above as `math.c`
2. Go to your web interface
3. Drag & drop `math.c`
4. Click "Generate Tests"
5. Wait for processing
6. Download `final_test_suite.c`

### **Generated Output** (`final_test_suite.c`):
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "math.c"

// Simple test framework
int tests_passed = 0;
int tests_failed = 0;

#define ASSERT_EQUAL(expected, actual, message) \
    do { \
        if ((expected) == (actual)) { \
            printf("✅ PASS: %s\n", message); \
            tests_passed++; \
        } else { \
            printf("❌ FAIL: %s (expected %d, got %d)\n", message, expected, actual); \
            tests_failed++; \
        } \
    } while(0)

#define ASSERT_STRING_EQUAL(expected, actual, message) \
    do { \
        if (strcmp(expected, actual) == 0) { \
            printf("✅ PASS: %s\n", message); \
            tests_passed++; \
        } else { \
            printf("❌ FAIL: %s (expected '%s', got '%s')\n", message, expected, actual); \
            tests_failed++; \
        } \
    } while(0)

void test_add_positive_integers() {
    int result = add(5, 3);
    ASSERT_EQUAL(8, result, "add(5, 3) should return 8");
}

void test_add_with_zero() {
    int result = add(5, 0);
    ASSERT_EQUAL(5, result, "add(5, 0) should return 5");
}

void test_subtract_positive_integers() {
    int result = subtract(10, 3);
    ASSERT_EQUAL(7, result, "subtract(10, 3) should return 7");
}

void test_multiply_positive_integers() {
    int result = multiply(4, 5);
    ASSERT_EQUAL(20, result, "multiply(4, 5) should return 20");
}

void test_divide_positive_integers() {
    int result = divide(15, 3);
    ASSERT_EQUAL(5, result, "divide(15, 3) should return 5");
}

void test_greet_function() {
    char* result = greet("World");
    ASSERT_STRING_EQUAL("Hello, World!", result, "greet('World') should return 'Hello, World!'");
}

int main() {
    printf("🧪 Running C Tests...\n");
    printf("====================\n\n");
    
    test_add_positive_integers();
    test_add_with_zero();
    test_subtract_positive_integers();
    test_multiply_positive_integers();
    test_divide_positive_integers();
    test_greet_function();
    
    printf("\n====================\n");
    printf("📊 Test Results:\n");
    printf("✅ Passed: %d\n", tests_passed);
    printf("❌ Failed: %d\n", tests_failed);
    printf("📈 Total: %d\n", tests_passed + tests_failed);
    
    if (tests_failed == 0) {
        printf("🎉 All tests passed!\n");
        return 0;
    } else {
        printf("💥 Some tests failed!\n");
        return 1;
    }
}
```

### **Run the Tests**:
```bash
# Compile the test file
gcc -o test_runner final_test_suite.c -std=c99

# Run the tests
./test_runner
```

### **Expected Output**:
```
🧪 Running C Tests...
====================

✅ PASS: add(5, 3) should return 8
✅ PASS: add(5, 0) should return 5
✅ PASS: subtract(10, 3) should return 7
✅ PASS: multiply(4, 5) should return 20
✅ PASS: divide(15, 3) should return 5
✅ PASS: greet('World') should return 'Hello, World!'

====================
📊 Test Results:
✅ Passed: 6
❌ Failed: 0
📈 Total: 6
🎉 All tests passed!
```

---

## 🔄 **Method 2: API Calls (Advanced)**

### **Python API Example**:
```python
import requests
import json

# Your web interface URL
WEB_URL = "https://testmozart-web-xxxxx-uc.a.run.app"

def upload_and_generate_tests(file_path):
    """Upload a file and generate tests"""
    print(f"📁 Uploading {file_path}...")
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{WEB_URL}/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"📝 Generated tests for {result['language']} code")
        print(f"🔗 Download URL: {result['download_url']}")
        
        # Save the generated test code
        with open(f"generated_{file_path.replace('.py', '_test.py').replace('.c', '_test.c')}", 'w') as f:
            f.write(result['test_code'])
        print("💾 Test file saved locally")
        
    else:
        print(f"❌ Error: {response.text}")

# Usage
upload_and_generate_tests("calculator.py")
```

### **cURL Example**:
```bash
# Upload a file via cURL
curl -X POST \
  -F "file=@calculator.py" \
  https://testmozart-web-xxxxx-uc.a.run.app/upload

# Expected response:
# {
#   "success": true,
#   "message": "Successfully generated test suite for calculator.py (python)",
#   "test_code": "...",
#   "download_url": "gs://ruckusdevtools-bucket/test_results/...",
#   "language": "python"
# }
```

---

## 🎯 **Best Practices**

### **For Input Files**:
1. **Use clear, descriptive function names**
2. **Include docstrings/comments** for better test generation
3. **Keep functions focused** (single responsibility)
4. **Handle edge cases** in your code

### **For Generated Tests**:
1. **Review generated tests** before using in production
2. **Add additional test cases** if needed
3. **Run tests manually** to verify they work
4. **Integrate into your CI/CD** pipeline

### **File Size Limits**:
- **Maximum file size**: 16MB
- **Recommended size**: < 1MB for best performance
- **Processing time**: 1-3 minutes for typical files

---

## 🚨 **Troubleshooting**

### **Common Issues**:

#### **"File upload failed"**
- Check file size (must be < 16MB)
- Ensure file extension is .py or .c
- Verify web interface is accessible

#### **"Test generation failed"**
- Check if your code has syntax errors
- Ensure functions are properly defined
- Try with a simpler test file first

#### **"Download link not working"**
- Check GCS bucket permissions
- Verify the generated file exists
- Try regenerating the tests

### **Debug Commands**:
```bash
# Check if web interface is running
curl https://your-web-interface-url/health

# Check agent status
adk list agents

# View recent logs
gcloud logging read "resource.type=agent_engine" --limit=10
```

---

## 📞 **Getting Help**

1. **Check the logs**: Use the debug commands above
2. **Verify deployment**: Ensure all services are running
3. **Test with sample files**: Use the examples above
4. **Check permissions**: Ensure all IAM roles are set correctly

---

## 🎉 **You're Ready!**

Your TestMozart system is now ready to use! Start with the simple examples above, then try your own code files. The AI will generate comprehensive test suites that cover:

- ✅ **Happy path scenarios**
- ✅ **Edge cases**
- ✅ **Error handling**
- ✅ **Boundary conditions**

Happy testing! 🚀
