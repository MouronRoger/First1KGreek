#!/usr/bin/env python3
"""
Pytest runner for First1KGreek tests.

Provides a command-line interface to run pytest tests with the same
categorization as the original unittest runner.
"""

import argparse
import subprocess
import sys


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run First1KGreek tests using pytest")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", 
                        help="Run only integration tests")
    parser.add_argument("--performance", action="store_true", 
                        help="Run only performance tests")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--coverage", action="store_true", 
                        help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    return parser.parse_args()


def run_pytest(args):
    """Run pytest with appropriate options based on args."""
    pytest_args = ["pytest"]
    
    # Handle test categories
    markers = []
    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")
    if args.performance:
        markers.append("performance")
    
    # Apply markers if specific categories requested
    if markers and not args.all:
        pytest_args.extend(["-m", " or ".join(markers)])
    
    # Add verbosity
    if args.verbose:
        pytest_args.append("-v")
    
    # Add coverage if requested
    if args.coverage:
        pytest_args.extend(["--cov=src", "--cov=browse_texts_fixed", 
                           "--cov-report=term"])
    
    # Run pytest
    result = subprocess.run(pytest_args)
    return result.returncode == 0


if __name__ == "__main__":
    args = parse_args()
    success = run_pytest(args)
    sys.exit(0 if success else 1) 