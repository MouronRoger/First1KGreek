#!/usr/bin/env python3
"""
First1KGreek Incremental Formatter

This script applies formatting incrementally to files,
running tests after each change to ensure functionality is preserved.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.bak"
    with open(file_path, "r", encoding="utf-8") as src, open(backup_path, "w", encoding="utf-8") as dst:
        dst.write(src.read())
    return backup_path


def run_tests():
    """Run the test suite."""
    print("Running tests...")

    # Adjust this command to match the First1KGreek test command
    test_command = ["python", "run_first1k_tests.py"]

    process = subprocess.run(test_command, capture_output=True, text=True, check=False)

    success = process.returncode == 0

    if success:
        print("✓ Tests passed")
    else:
        print("❌ Tests failed")
        print(process.stdout)
        print(process.stderr)

    return success


def format_file(file_path, tool, options=None):
    """Format a file with the specified tool."""
    if options is None:
        options = []

    print(f"Formatting {file_path} with {tool}...")

    command = [tool, file_path, *options]
    process = subprocess.run(command, capture_output=True, text=True, check=False)

    if process.returncode != 0:
        print(f"❌ Formatting failed: {process.stderr}")
        return False

    return True


def process_file(file_path, tools, run_tests_after=True, dry_run=False, restore_on_failure=True):
    """Process a single file with multiple formatting tools."""
    print_section(f"Processing {file_path}")

    if dry_run:
        print("Dry run - no changes will be made")

    # Create backup
    if not dry_run:
        backup_path = backup_file(file_path)
        print(f"Created backup at {backup_path}")

    tool_configs = {
        "isort": ["--profile=black", "--line-length=120"],
        "black": ["--line-length=120"],
        "autoflake": ["--remove-all-unused-imports", "--in-place"],
    }

    success = True

    for tool in tools:
        if tool not in tool_configs:
            print(f"Unknown tool: {tool}")
            continue

        if dry_run:
            # For dry run, just show what would change
            if tool == "black":
                subprocess.run(["black", "--diff", file_path, *tool_configs[tool]], check=False)
            elif tool == "isort":
                subprocess.run(["isort", "--diff", file_path, *tool_configs[tool]], check=False)
            continue

        # Apply the tool
        if not format_file(file_path, tool, tool_configs[tool]):
            success = False
            break

        # Run tests after each tool if requested
        if run_tests_after:
            if not run_tests():
                print(f"❌ Tests failed after applying {tool}")
                if restore_on_failure:
                    print(f"Restoring from backup: {backup_path}")
                    shutil.copy(backup_path, file_path)
                success = False
                break

    if success and not dry_run:
        print("✓ All formatting tools applied successfully")
    elif not dry_run:
        print("❌ Some formatting tools failed or caused test failures")

    return success


def main():
    """Process files incrementally with formatting tools."""
    parser = argparse.ArgumentParser(description="Format Python files incrementally.")
    parser.add_argument("file", nargs="+", help="Python file(s) to process")
    parser.add_argument(
        "--tools",
        nargs="+",
        default=["isort", "black", "autoflake"],
        help="Tools to apply in order (default: isort black autoflake)",
    )
    parser.add_argument("--no-tests", action="store_true", help="Skip running tests after each tool")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")
    parser.add_argument("--no-restore", action="store_true", help="Do not restore from backup on test failure")
    args = parser.parse_args()

    # Ensure tools are installed
    for tool in args.tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=False)
        except FileNotFoundError:
            print(f"Installing {tool}...")
            subprocess.run([sys.executable, "-m", "pip", "install", tool], check=True)

    # Process each file
    success = True
    for file_path in args.file:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            success = False
            continue

        if not file_path.endswith(".py"):
            print(f"Warning: {file_path} does not appear to be a Python file, skipping")
            continue

        if not process_file(
            file_path,
            args.tools,
            run_tests_after=not args.no_tests,
            dry_run=args.dry_run,
            restore_on_failure=not args.no_restore,
        ):
            success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
