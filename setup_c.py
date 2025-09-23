#!/usr/bin/env python3
"""
Setup script for C testing dependencies
Installs gcc compiler for simple C testing (no Unity framework needed)
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_gcc():
    """Check if gcc is available"""
    print("🔍 Checking for gcc compiler...")
    try:
        subprocess.run(["gcc", "--version"], check=True, capture_output=True)
        print("✅ gcc is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ gcc not found")
        return False

def install_gcc_windows():
    """Install gcc on Windows using chocolatey or winget"""
    print("🔧 Installing gcc on Windows...")
    
    # Try winget first
    if run_command("winget install -e --id GNU.GCC", "Installing gcc via winget"):
        return True
    
    # Try chocolatey
    if run_command("choco install mingw", "Installing gcc via chocolatey"):
        return True
    
    print("❌ Could not install gcc automatically. Please install MinGW-w64 manually.")
    print("   Download from: https://www.mingw-w64.org/downloads/")
    return False

def install_gcc_linux():
    """Install gcc on Linux"""
    print("🔧 Installing gcc on Linux...")
    
    # Try different package managers
    package_managers = [
        ("apt-get update && apt-get install -y gcc", "Installing gcc via apt-get"),
        ("yum install -y gcc", "Installing gcc via yum"),
        ("dnf install -y gcc", "Installing gcc via dnf"),
        ("pacman -S --noconfirm gcc", "Installing gcc via pacman"),
        ("zypper install -y gcc", "Installing gcc via zypper")
    ]
    
    for command, description in package_managers:
        if run_command(command, description):
            return True
    
    print("❌ Could not install gcc automatically. Please install gcc manually.")
    print("   Run: sudo apt-get install gcc (Ubuntu/Debian)")
    print("   Run: sudo yum install gcc (CentOS/RHEL)")
    return False

def install_gcc_macos():
    """Install gcc on macOS"""
    print("🔧 Installing gcc on macOS...")
    
    # Try Homebrew
    if run_command("brew install gcc", "Installing gcc via Homebrew"):
        return True
    
    print("❌ Could not install gcc automatically. Please install gcc manually.")
    print("   Run: brew install gcc")
    return False

def create_simple_test_template():
    """Create a simple C test template for reference"""
    print("🔧 Creating simple C test template...")
    
    template_content = '''#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Simple test framework
int tests_passed = 0;
int tests_failed = 0;

#define ASSERT_EQUAL(expected, actual, message) \\
    do { \\
        if ((expected) == (actual)) { \\
            printf("✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("❌ FAIL: %s (expected %d, got %d)\\n", message, expected, actual); \\
            tests_failed++; \\
        } \\
    } while(0)

#define ASSERT_STRING_EQUAL(expected, actual, message) \\
    do { \\
        if (strcmp(expected, actual) == 0) { \\
            printf("✅ PASS: %s\\n", message); \\
            tests_passed++; \\
        } else { \\
            printf("❌ FAIL: %s (expected '%s', got '%s')\\n", message, expected, actual); \\
            tests_failed++; \\
        } \\
    } while(0)

// Include your source code here
// #include "your_source_code.c"

void test_example(void) {
    // Example test
    int result = 2 + 3;
    ASSERT_EQUAL(5, result, "2 + 3 should equal 5");
}

int main(void) {
    printf("🧪 Running C Tests...\\n");
    printf("====================\\n\\n");
    
    test_example();
    // Add more tests here
    
    printf("\\n====================\\n");
    printf("📊 Test Results:\\n");
    printf("✅ Passed: %d\\n", tests_passed);
    printf("❌ Failed: %d\\n", tests_failed);
    printf("📈 Total: %d\\n", tests_passed + tests_failed);
    
    if (tests_failed == 0) {
        printf("🎉 All tests passed!\\n");
        return 0;
    } else {
        printf("💥 Some tests failed!\\n");
        return 1;
    }
}
'''
    
    with open("simple_test_template.c", 'w') as f:
        f.write(template_content)
    
    print("✅ Simple C test template created")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up C testing dependencies...")
    print("=" * 50)
    
    # Check if gcc is already available
    if check_gcc():
        print("✅ gcc is already available!")
        create_simple_test_template()
        print("=" * 50)
        print("✅ C testing dependencies setup complete!")
        print("\n📝 Next steps:")
        print("1. Run: python main.py (with TEST_FILE_PATH = 'sample_code.c')")
        print("2. Follow the C testing commands in TESTING_COMMANDS.txt")
        print("3. Check simple_test_template.c for reference")
        return True
    
    # Install gcc based on platform
    print("🔧 Installing gcc compiler...")
    
    if sys.platform.startswith('win'):
        success = install_gcc_windows()
    elif sys.platform.startswith('linux'):
        success = install_gcc_linux()
    elif sys.platform.startswith('darwin'):
        success = install_gcc_macos()
    else:
        print(f"❌ Unsupported platform: {sys.platform}")
        print("Please install gcc manually for your platform.")
        return False
    
    if success:
        print("=" * 50)
        print("✅ C testing dependencies setup complete!")
        print("\n📝 Next steps:")
        print("1. Run: python main.py (with TEST_FILE_PATH = 'sample_code.c')")
        print("2. Follow the C testing commands in TESTING_COMMANDS.txt")
        print("3. Check simple_test_template.c for reference")
        return True
    else:
        print("=" * 50)
        print("❌ C testing dependencies setup failed!")
        print("Please install gcc manually and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)