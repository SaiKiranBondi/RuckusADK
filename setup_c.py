#!/usr/bin/env python3
"""
Setup script for C testing dependencies
Installs Unity framework and other required tools for C testing
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
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
    
    # Try apt (Ubuntu/Debian)
    if run_command("sudo apt-get update && sudo apt-get install -y gcc", "Installing gcc via apt"):
        return True
    
    # Try yum (CentOS/RHEL)
    if run_command("sudo yum install -y gcc", "Installing gcc via yum"):
        return True
    
    # Try dnf (Fedora)
    if run_command("sudo dnf install -y gcc", "Installing gcc via dnf"):
        return True
    
    print("❌ Could not install gcc automatically. Please install gcc manually.")
    return False

def install_gcc_macos():
    """Install gcc on macOS"""
    print("🔧 Installing gcc on macOS...")
    
    # Try homebrew
    if run_command("brew install gcc", "Installing gcc via homebrew"):
        return True
    
    print("❌ Could not install gcc automatically. Please install gcc manually.")
    print("   Run: brew install gcc")
    return False

def download_unity_framework():
    """Download and setup Unity framework"""
    print("🔧 Setting up Unity framework...")
    
    unity_dir = Path("unity")
    if unity_dir.exists():
        print("✅ Unity framework already exists")
        return True
    
    try:
        # Create unity directory
        unity_dir.mkdir(exist_ok=True)
        
        # Download Unity framework
        unity_url = "https://github.com/ThrowTheSwitch/Unity/archive/refs/heads/master.zip"
        unity_zip = "unity.zip"
        
        print("📥 Downloading Unity framework...")
        urllib.request.urlretrieve(unity_url, unity_zip)
        
        # Extract Unity
        with zipfile.ZipFile(unity_zip, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Move Unity files to unity directory
        extracted_dir = Path("Unity-master")
        if extracted_dir.exists():
            for item in extracted_dir.iterdir():
                shutil.move(str(item), str(unity_dir / item.name))
            shutil.rmtree(extracted_dir)
        
        # Clean up
        os.remove(unity_zip)
        
        print("✅ Unity framework installed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download Unity framework: {e}")
        return False

def create_unity_header():
    """Create a simple Unity header if download fails"""
    print("🔧 Creating Unity header...")
    
    unity_dir = Path("unity")
    unity_dir.mkdir(exist_ok=True)
    
    unity_h = unity_dir / "unity.h"
    
    # Create a minimal Unity header
    unity_content = '''#ifndef UNITY_H
#define UNITY_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Minimal Unity testing framework
#define TEST_ASSERT_EQUAL(expected, actual) \\
    do { \\
        if ((expected) != (actual)) { \\
            printf("FAIL: Expected %d, got %d\\n", (expected), (actual)); \\
            exit(1); \\
        } \\
    } while(0)

#define TEST_ASSERT_NOT_NULL(pointer) \\
    do { \\
        if ((pointer) == NULL) { \\
            printf("FAIL: Expected non-NULL pointer\\n"); \\
            exit(1); \\
        } \\
    } while(0)

#define TEST_ASSERT_TRUE(condition) \\
    do { \\
        if (!(condition)) { \\
            printf("FAIL: Expected true, got false\\n"); \\
            exit(1); \\
        } \\
    } while(0)

#define UNITY_BEGIN() printf("Running tests...\\n")
#define UNITY_END() printf("All tests passed!\\n"); return 0

#endif
'''
    
    with open(unity_h, 'w') as f:
        f.write(unity_content)
    
    print("✅ Unity header created")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up C testing dependencies...")
    print("=" * 50)
    
    # Check if gcc is available
    if not check_gcc():
        print("🔧 Installing gcc...")
        
        if sys.platform == "win32":
            success = install_gcc_windows()
        elif sys.platform == "linux":
            success = install_gcc_linux()
        elif sys.platform == "darwin":
            success = install_gcc_macos()
        else:
            print("❌ Unsupported platform. Please install gcc manually.")
            success = False
        
        if not success:
            print("❌ gcc installation failed. Please install gcc manually.")
            return False
    
    # Setup Unity framework
    if not download_unity_framework():
        print("🔧 Creating minimal Unity framework...")
        create_unity_header()
    
    print("=" * 50)
    print("✅ C testing dependencies setup complete!")
    print("\n📝 Next steps:")
    print("1. Run: python main.py (with TEST_FILE_PATH = 'sample_code.c')")
    print("2. Follow the C testing commands in TESTING_COMMANDS.txt")
    
    return True

if __name__ == "__main__":
    main()
