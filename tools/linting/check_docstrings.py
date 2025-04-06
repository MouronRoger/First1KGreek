#!/usr/bin/env python3
"""
Check Python files for docstring compliance using pydocstyle.

This script checks Python files in the specified directory for compliance with
docstring standards (D100, D101, D102, D103) which are:
- D100: Missing docstring in public module
- D101: Missing docstring in public class
- D102: Missing docstring in public method
- D103: Missing docstring in public function
"""

import argparse
import glob
import json
import os
import subprocess
import sys
from pathlib import Path


def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def get_python_files(directory):
    """Get all Python files in the specified directory."""
    return [f for f in glob.glob(f"{directory}/**/*.py", recursive=True) if not f.endswith("__init__.py")]


def check_docstrings(file_paths, select_codes=None):
    """
    Check files for docstring compliance.

    Args:
        file_paths: List of file paths to check
        select_codes: List of pydocstyle codes to check for (e.g., ["D100", "D101"])

    Returns:
        Dictionary with results (compliant files, non-compliant files, error count)
    """
    if not select_codes:
        select_codes = ["D100", "D101", "D102", "D103"]

    compliant_files = []
    non_compliant_files = {}
    total_errors = 0

    for file_path in file_paths:
        cmd = ["pydocstyle", "--select=" + ",".join(select_codes), file_path]

        process = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if process.returncode == 0:
            compliant_files.append(file_path)
        else:
            errors = process.stdout.strip().split("\n")
            error_count = len([e for e in errors if e and not e.isspace()])
            non_compliant_files[file_path] = error_count
            total_errors += error_count

    return {
        "compliant_files": compliant_files,
        "non_compliant_files": non_compliant_files,
        "total_errors": total_errors,
    }


def generate_report(results, output_dir=None):
    """
    Generate a report of docstring compliance.

    Args:
        results: Dictionary with check results
        output_dir: Directory to save report JSON (if None, won't save)

    Returns:
        Compliance percentage
    """
    total_files = len(results["compliant_files"]) + len(results["non_compliant_files"])
    if total_files == 0:
        compliance_pct = 100.0
    else:
        compliance_pct = (len(results["compliant_files"]) / total_files) * 100

    print(f"Total files checked: {total_files}")
    print(f"Docstring compliant files: {len(results['compliant_files'])} ({compliance_pct:.2f}%)")
    print(f"Non-compliant files: {len(results['non_compliant_files'])}")
    print(f"Total docstring errors: {results['total_errors']}")

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, "docstring_report.json")
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Report saved to {report_path}")

    return compliance_pct


def main():
    """Run docstring checks on Python files."""
    parser = argparse.ArgumentParser(description="Check Python files for docstring compliance")
    parser.add_argument("directory", help="Directory to check")
    parser.add_argument("--output-dir", help="Directory to save report files")
    parser.add_argument(
        "--select", default="D100,D101,D102,D103", help="Docstring error codes to check (comma-separated)"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)

    try:
        # Try importing pydocstyle to ensure it's installed
        import pydocstyle
    except ImportError:
        print("Error: pydocstyle is not installed")
        print("Please install it with: pip install pydocstyle")
        sys.exit(1)

    print_section(f"Checking docstrings in {args.directory}")

    files = get_python_files(args.directory)
    if not files:
        print(f"No Python files found in {args.directory}")
        sys.exit(0)

    print(f"Found {len(files)} Python files to check")

    # Check docstrings
    select_codes = args.select.split(",")
    results = check_docstrings(files, select_codes)

    print_section("Docstring Check Results")
    compliance_pct = generate_report(results, args.output_dir)

    # Exit with non-zero if compliance is below 50%
    if compliance_pct < 50:
        sys.exit(1)


if __name__ == "__main__":
    main()
