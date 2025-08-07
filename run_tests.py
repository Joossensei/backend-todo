#!/usr/bin/env python3
"""
Test runner script for the Todo API
Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit            # Run only unit tests
    python run_tests.py --integration     # Run only integration tests
    python run_tests.py --coverage        # Run tests with coverage report
    python run_tests.py --verbose         # Run tests with verbose output
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(args):
    """Run pytest with the specified arguments"""
    cmd = ["python", "-m", "pytest"]

    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])

    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html"])

    if args.verbose:
        cmd.append("-v")

    if args.tests:
        cmd.extend(args.tests)

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for the Todo API")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage report"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "tests", nargs="*", help="Specific test files or directories to run"
    )

    args = parser.parse_args()

    # Check if pytest is installed
    try:
        import pytest  # noqa: F401
    except ImportError:
        print("Error: pytest is not installed. Please install it with:")
        print("pip install pytest pytest-asyncio httpx pytest-cov")
        return 1

    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
