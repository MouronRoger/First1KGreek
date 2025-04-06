#!/usr/bin/env python3
"""
Test runner for First1KGreek Browser tests.

This script runs all working test suites and provides a summary of results.
"""

import argparse
import os
import sys
import time
import unittest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from simple_integration_test import SimpleIntegrationTest
from simple_performance_test import SimplePerformanceTest

# Import test modules
from simple_xml_test import SimpleXMLTest


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run First1KGreek Browser tests")
    parser.add_argument("--xml", action="store_true", help="Run only XML tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--performance", action="store_true", help="Run only performance tests")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    return parser.parse_args()


def run_tests(args):
    """Run the specified test suites."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Determine which tests to run
    run_all = args.all or not (args.xml or args.integration or args.performance)

    # Add XML tests
    if run_all or args.xml:
        print("Adding XML tests...")
        xml_tests = unittest.defaultTestLoader.loadTestsFromTestCase(SimpleXMLTest)
        test_suite.addTests(xml_tests)

    # Add integration tests
    if run_all or args.integration:
        print("Adding integration tests...")
        integration_tests = unittest.defaultTestLoader.loadTestsFromTestCase(SimpleIntegrationTest)
        test_suite.addTests(integration_tests)

    # Add performance tests
    if run_all or args.performance:
        print("Adding performance tests...")
        performance_tests = unittest.defaultTestLoader.loadTestsFromTestCase(SimplePerformanceTest)
        test_suite.addTests(performance_tests)

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
