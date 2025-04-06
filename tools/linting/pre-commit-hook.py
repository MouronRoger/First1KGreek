#!/usr/bin/env python3
"""
First1KGreek Pre-Commit Hook

This script runs basic linting checks on staged Python files.
It will prevent commits if critical issues are found.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def ensure_dependencies():
    """Check if required dependencies are installed, and install them if not."""
    dependencies = ["pylint"]
    missing = []

    for dep in dependencies:
        try:
            subprocess.run([dep, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except FileNotFoundError:
            missing.append(dep)

    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", *missing], check=True)
            print("✓ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("You may need to install them manually:")
            print(f"pip install {' '.join(missing)}")
            return False

    return True


def get_staged_python_files():
    """Get list of staged Python files."""
    process = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], capture_output=True, text=True, check=True
    )

    files = process.stdout.strip().split("\n")
    return [f for f in files if f.endswith(".py") and os.path.exists(f)]


def check_syntax(file_path):
    """Check Python syntax without executing the file."""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        compile(source, file_path, "exec")
        return True
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return False


def check_critical_issues(file_path):
    """Check for critical issues using pylint."""
    try:
        process = subprocess.run(
            ["pylint", "--disable=all", "--enable=syntax-error,undefined-variable", "--output-format=json", file_path],
            capture_output=True,
            text=True,
            check=False,
        )

        try:
            if process.stdout.strip():
                issues = json.loads(process.stdout)
                if issues:
                    print(f"Critical issues in {file_path}:")
                    for issue in issues:
                        print(f"  Line {issue.get('line', '?')}: {issue.get('message', 'Unknown issue')}")
                    return False
            return True
        except json.JSONDecodeError:
            print(f"Error parsing pylint output for {file_path}")
            return False
    except FileNotFoundError:
        print(f"Warning: pylint not found in PATH, skipping critical issues check for {file_path}")
        print("Consider installing pylint: pip install pylint")
        # Return True to allow the commit to proceed
        return True


def main():
    """Run pre-commit checks on staged Python files."""
    print_section("Pre-Commit Checks")

    # Ensure dependencies are installed
    if not ensure_dependencies():
        print("Warning: proceeding with limited checks due to missing dependencies")

    # Get staged Python files
    python_files = get_staged_python_files()

    if not python_files:
        print("No Python files staged for commit")
        return 0

    print(f"Checking {len(python_files)} Python files")

    # Check each file
    success = True
    for file_path in python_files:
        print(f"\nChecking {file_path}...")

        # Check syntax
        if not check_syntax(file_path):
            success = False
            continue

        # Check critical issues
        if not check_critical_issues(file_path):
            success = False
            continue

        print(f"✓ {file_path} passed checks")

    if not success:
        print_section("Commit Failed")
        print("Fix the issues above before committing")
        return 1

    print_section("All Checks Passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
