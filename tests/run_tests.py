#!/usr/bin/env python3
"""
Test runner script for Cuentamelo LangGraph test suite.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run the test suite with specified options."""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Select test type
    if test_type == "unit":
        cmd.extend(["tests/unit/models", "tests/unit/agents", "tests/unit/graphs", "tests/unit/services", "tests/unit/tools"])
    elif test_type == "integration":
        cmd.extend(["tests/integration"])
    elif test_type == "models":
        cmd.extend(["tests/unit/models"])
    elif test_type == "agents":
        cmd.extend(["tests/unit/agents"])
    elif test_type == "graphs":
        cmd.extend(["tests/unit/graphs"])
    elif test_type == "services":
        cmd.extend(["tests/unit/services"])
    elif test_type == "tools":
        cmd.extend(["tests/unit/tools"])
    elif test_type == "personality":
        cmd.extend(["tests/unit/models/test_personality.py"])
    elif test_type == "thread":
        cmd.extend(["tests/unit/models/test_thread_engagement.py"])
    elif test_type == "news":
        cmd.extend(["tests/unit/models/test_news_processing.py"])
    elif test_type == "character":
        cmd.extend(["tests/unit/agents/test_character_agents.py"])
    elif test_type == "workflow":
        cmd.extend(["tests/unit/graphs/test_character_workflow.py"])
    elif test_type == "orchestrator":
        cmd.extend(["tests/unit/graphs/test_orchestrator.py"])
    elif test_type == "integration":
        cmd.extend(["tests/integration/test_langgraph_integration.py"])
    else:
        # Run all tests
        cmd.append("tests")
    
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user.")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    """Main function for test runner."""
    parser = argparse.ArgumentParser(description="Run Cuentamelo LangGraph tests")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=[
            "all", "unit", "integration", "models", "agents", "graphs",
            "personality", "thread", "news", "character", "workflow", 
            "orchestrator"
        ],
        help="Type of tests to run"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("Error: tests directory not found. Please run from project root.")
        sys.exit(1)
    
    # Run tests
    exit_code = run_tests(args.test_type, args.verbose, args.coverage)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 