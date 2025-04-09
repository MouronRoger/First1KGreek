#!/usr/bin/env python3
"""
Test runner for First1KGreek Browser tests.

This script runs all test suites and provides a summary of results.
"""

import argparse
import os
import sys
import time
import unittest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run First1KGreek Browser tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--performance", action="store_true", help="Run only performance tests")
    parser.add_argument("--core", action="store_true", help="Run only core tests")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    return parser.parse_args()


def discover_tests(test_dir):
    """Discover tests in the specified directory."""
    if not os.path.exists(test_dir):
        print(f"Warning: Test directory {test_dir} does not exist")
        return unittest.TestSuite()
    return unittest.defaultTestLoader.discover(test_dir, pattern="test_*.py")


def run_tests(args):
    """Run the specified test suites."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Get the tests directory
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Determine which tests to run
    run_all = args.all or not (args.unit or args.integration or args.performance or args.core)

    # Add unit tests
    if run_all or args.unit:
        print("Adding unit tests...")
        unit_tests = discover_tests(os.path.join(tests_dir, "unit"))
        test_suite.addTests(unit_tests)

    # Add integration tests
    if run_all or args.integration:
        print("Adding integration tests...")
        integration_tests = discover_tests(os.path.join(tests_dir, "integration"))
        test_suite.addTests(integration_tests)

    # Add performance tests
    if run_all or args.performance:
        print("Adding performance tests...")
        performance_tests = discover_tests(os.path.join(tests_dir, "performance"))
        test_suite.addTests(performance_tests)
        
    # Add core tests
    if run_all or args.core:
        print("Adding core tests...")
        core_tests = discover_tests(os.path.join(tests_dir, "core"))
        test_suite.addTests(core_tests)

    # Run tests with appropriate verbosity
    verbosity = 2 if args.verbose else 1
    print(f"\nRunning tests with verbosity: {verbosity}")

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(test_suite)
    end_time = time.time()

    # Print summary
    print("\nTest Summary:")
    print(f"Ran {result.testsRun} tests in {end_time - start_time:.2f} seconds")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    return result.wasSuccessful()


if __name__ == "__main__":
    args = parse_args()
    success = run_tests(args)
    sys.exit(0 if success else 1)
