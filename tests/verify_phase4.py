#!/usr/bin/env python3
"""
Verification script for Phase 4 of First1KGreek Browser refactoring.

This script tests various ways to run the application and ensures
they all work as expected. It helps verify that the transition
to the modular structure is complete and working correctly.
"""

import os
import sys
import time
import subprocess
import requests
import logging
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("verification.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Test parameters
TEST_PORT_START = 8800  # We'll use ports starting from this
REQUEST_TIMEOUT = 3.0   # Timeout for HTTP requests
SERVER_STARTUP_WAIT = 2.0  # Wait time for server to start

class TestFailure(Exception):
    """Exception raised when a test fails."""
    pass

def wait_for_server(port, max_attempts=10):
    """Wait for server to start accepting connections."""
    logger.info(f"Waiting for server on port {port}...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"http://localhost:{port}/", timeout=REQUEST_TIMEOUT)
            logger.info(f"Server is up on port {port}! Status: {response.status_code}")
            return True
        except requests.RequestException:
            logger.info(f"Attempt {attempt+1}/{max_attempts} - Server not ready...")
            time.sleep(SERVER_STARTUP_WAIT)
    
    logger.error(f"Server failed to start on port {port} after {max_attempts} attempts")
    return False

def kill_process(process):
    """Kill a process and ensure it's terminated."""
    if process and process.poll() is None:
        logger.info(f"Terminating process {process.pid}...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning(f"Process {process.pid} didn't terminate, killing...")
            process.kill()

def test_endpoint(port, path="/", expected_status=200):
    """Test if an endpoint returns the expected status code."""
    url = f"http://localhost:{port}{path}"
    try:
        logger.info(f"Testing endpoint: {url}")
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code != expected_status:
            logger.error(f"Endpoint {url} returned status {response.status_code}, expected {expected_status}")
            return False
        logger.info(f"Endpoint {url} returned status {response.status_code} as expected")
        return True
    except requests.RequestException as e:
        logger.error(f"Error accessing {url}: {str(e)}")
        return False

def test_server(command, port, name):
    """Test a server by running a command and checking if it starts."""
    logger.info(f"\n==== Testing {name} ====")
    logger.info(f"Command: {command}")
    
    # Start the server process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True
    )
    
    # Wait for server to start
    if not wait_for_server(port):
        kill_process(process)
        raise TestFailure(f"Server '{name}' failed to start")
    
    # Test basic endpoints
    endpoints = [
        "/",
        "/browse/authors",
        "/search",
    ]
    
    all_passed = True
    for endpoint in endpoints:
        if not test_endpoint(port, endpoint):
            all_passed = False
    
    # Kill the server process
    kill_process(process)
    
    # Check process output for errors
    stdout, stderr = process.communicate()
    if stderr and "Error" in stderr:
        logger.error(f"Server '{name}' reported errors:\n{stderr}")
        all_passed = False
    
    if all_passed:
        logger.info(f"==== {name} TEST PASSED ====\n")
    else:
        logger.error(f"==== {name} TEST FAILED ====\n")
        raise TestFailure(f"Server '{name}' failed tests")
    
    return all_passed

def run_tests(args):
    """Run the verification tests."""
    results = {}
    port = TEST_PORT_START
    
    # Directory for testing the installed version
    temp_dir = None
    
    try:
        # Test 1: Run with run_server.py
        if args.all or args.run_server:
            test_cmd = f"python run_server.py --port {port} --no-browser"
            results["run_server.py"] = test_server(test_cmd, port, "run_server.py")
            port += 1
        
        # Test 2: Run with python -m src.first1k
        if args.all or args.module:
            test_cmd = f"python -m src.first1k --port {port} --no-browser"
            results["module"] = test_server(test_cmd, port, "python -m src.first1k")
            port += 1
        
        # Test 3: Run with browse_texts_fixed.py (legacy)
        if args.all or args.legacy:
            test_cmd = f"python browse_texts_fixed.py --port {port} --no-browser"
            results["legacy"] = test_server(test_cmd, port, "browse_texts_fixed.py (legacy)")
            port += 1
        
        # Test 4: Install and run as package (if requested)
        if args.all or args.installed:
            # Create a temporary directory for the test
            temp_dir = tempfile.mkdtemp()
            logger.info(f"Created temporary directory: {temp_dir}")
            
            # Build and install the package
            logger.info("Building and installing package...")
            install_cmd = f"pip install -e . --target={temp_dir}"
            subprocess.run(install_cmd, shell=True, check=True)
            
            # Add the temp directory to Python path
            sys.path.insert(0, temp_dir)
            
            # Run the command
            test_cmd = f"PYTHONPATH={temp_dir} {temp_dir}/bin/first1k --port {port} --no-browser"
            results["installed"] = test_server(test_cmd, port, "installed package")
        
        # Report results
        logger.info("\n==== VERIFICATION RESULTS ====")
        all_passed = True
        for name, passed in results.items():
            status = "PASSED" if passed else "FAILED"
            logger.info(f"{name}: {status}")
            all_passed = all_passed and passed
        
        if all_passed:
            logger.info("\nALL TESTS PASSED! Phase 4 implementation is successful.")
            return 0
        else:
            logger.error("\nSOME TESTS FAILED! See log for details.")
            return 1
    
    except TestFailure as e:
        logger.error(f"Test failure: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1
    finally:
        # Clean up
        if temp_dir and os.path.exists(temp_dir):
            logger.info(f"Cleaning up temporary directory: {temp_dir}")
            shutil.rmtree(temp_dir)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Verify Phase 4 implementation of First1KGreek Browser",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--run-server", action="store_true", help="Test run_server.py")
    parser.add_argument("--module", action="store_true", help="Test python -m src.first1k")
    parser.add_argument("--legacy", action="store_true", help="Test browse_texts_fixed.py")
    parser.add_argument("--installed", action="store_true", help="Test installed package")
    
    args = parser.parse_args()
    
    # If no specific test is specified, run all tests
    if not (args.all or args.run_server or args.module or args.legacy or args.installed):
        args.all = True
    
    return args

if __name__ == "__main__":
    args = parse_args()
    sys.exit(run_tests(args)) 