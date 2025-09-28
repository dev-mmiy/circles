#!/usr/bin/env python3
"""
Test runner script for the healthcare community platform.
Provides convenient commands for running different types of tests.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <command>")
        print("\nAvailable commands:")
        print("  unit          - Run unit tests only")
        print("  integration    - Run integration tests only")
        print("  all          - Run all tests")
        print("  coverage     - Run tests with coverage report")
        print("  lint         - Run linting checks")
        print("  format       - Format code with black and isort")
        print("  clean        - Clean test artifacts")
        print("  help         - Show this help message")
        return
    
    command = sys.argv[1].lower()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    if command == "unit":
        success = run_command(
            "python -m pytest tests/test_app_simple.py tests/test_models.py -v",
            "Running Unit Tests"
        )
        
    elif command == "integration":
        success = run_command(
            "python -m pytest tests/test_integration.py -v",
            "Running Integration Tests"
        )
        
    elif command == "all":
        success = run_command(
            "python -m pytest tests/ -v",
            "Running All Tests"
        )
        
    elif command == "coverage":
        success = run_command(
            "python -m pytest tests/ --cov=app_simple --cov-report=term-missing --cov-report=html:htmlcov",
            "Running Tests with Coverage"
        )
        if success:
            print(f"\n📊 Coverage report generated in htmlcov/index.html")
        
    elif command == "lint":
        print("🔍 Running Linting Checks...")
        lint_commands = [
            ("python -m flake8 app_simple.py tests/", "Flake8 linting"),
            ("python -m black --check app_simple.py tests/", "Black formatting check"),
            ("python -m isort --check-only app_simple.py tests/", "Import sorting check"),
        ]
        
        all_success = True
        for cmd, desc in lint_commands:
            if not run_command(cmd, desc):
                all_success = False
        
        success = all_success
        
    elif command == "format":
        print("🎨 Formatting Code...")
        format_commands = [
            ("python -m black app_simple.py tests/", "Black formatting"),
            ("python -m isort app_simple.py tests/", "Import sorting"),
        ]
        
        all_success = True
        for cmd, desc in format_commands:
            if not run_command(cmd, desc):
                all_success = False
        
        success = all_success
        
    elif command == "clean":
        print("🧹 Cleaning Test Artifacts...")
        clean_commands = [
            "rm -rf htmlcov/",
            "rm -rf .coverage",
            "rm -rf .pytest_cache/",
            "find . -type d -name __pycache__ -exec rm -rf {} +",
            "find . -name '*.pyc' -delete",
        ]
        
        for cmd in clean_commands:
            subprocess.run(cmd, shell=True)
        
        print("✅ Cleanup completed")
        success = True
        
    elif command == "help":
        print("🧪 Healthcare Community Platform Test Runner")
        print("\nAvailable commands:")
        print("  unit          - Run unit tests only")
        print("  integration  - Run integration tests only")
        print("  all          - Run all tests")
        print("  coverage     - Run tests with coverage report")
        print("  lint         - Run linting checks")
        print("  format       - Format code with black and isort")
        print("  clean        - Clean test artifacts")
        print("  help         - Show this help message")
        print("\nExamples:")
        print("  python run_tests.py unit")
        print("  python run_tests.py coverage")
        print("  python run_tests.py lint")
        success = True
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python run_tests.py help' for available commands")
        success = False
    
    if success:
        print(f"\n✅ {command.title()} completed successfully!")
    else:
        print(f"\n❌ {command.title()} failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
