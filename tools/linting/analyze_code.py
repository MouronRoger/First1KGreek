#!/usr/bin/env python3
"""
First1KGreek Lint Analysis Tool

This script runs linting tools on the codebase but doesn't enforce any rules.
It generates reports to help understand the current state of the code.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def ensure_tools_installed():
    """Check if required tools are installed and install if missing."""
    required_tools = ["flake8", "pylint", "black", "isort"]

    for tool in required_tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=False)
        except FileNotFoundError:
            print(f"Installing {tool}...")
            subprocess.run([sys.executable, "-m", "pip", "install", tool], check=True)


def collect_python_files(directory=".", exclude_dirs=None):
    """Collect all Python files in the directory."""
    if exclude_dirs is None:
        exclude_dirs = [".git", "__pycache__", "venv", "env", ".env", "build", "dist"]

    python_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def run_flake8(files, report_dir):
    """Run flake8 on the files and generate a report."""
    print_section("Running Flake8")

    report_path = os.path.join(report_dir, "flake8_report.txt")

    with open(report_path, "w") as report_file:
        process = subprocess.run(
            ["flake8", "--exit-zero", "--statistics", "--count", *files], capture_output=True, text=True, check=False
        )
        report_file.write(process.stdout)

        # Also capture error categories
        process = subprocess.run(
            ["flake8", "--exit-zero", "--statistics", *files], capture_output=True, text=True, check=False
        )
        report_file.write("\n\nError Categories:\n")
        report_file.write(process.stdout)

    print(f"Flake8 report saved to {report_path}")

    # Print summary
    error_count = 0
    with open(report_path, "r") as f:
        for line in f:
            if line.strip() and line[0].isdigit():
                try:
                    error_count += int(line.split()[0])
                except (ValueError, IndexError):
                    pass

    print(f"Total Flake8 issues: {error_count}")
    return error_count


def run_pylint(files, report_dir):
    """Run pylint on the files and generate a report."""
    print_section("Running Pylint")

    report_path = os.path.join(report_dir, "pylint_report.txt")
    json_report_path = os.path.join(report_dir, "pylint_report.json")

    # Run with minimal checks first as specified in setup.cfg
    with open(report_path, "w") as report_file:
        process = subprocess.run(
            ["pylint", "--output-format=text", *files], capture_output=True, text=True, check=False
        )
        report_file.write(process.stdout)

    # Run with full checks but only generate JSON report for analysis
    subprocess.run(
        [
            "pylint",
            "--disable=all",
            "--enable=syntax-error,undefined-variable,unused-import",
            "--output-format=json",
            *files,
            "--output=" + json_report_path,
        ],
        check=False,
    )

    print(f"Pylint report saved to {report_path}")

    # Count critical issues
    critical_count = 0
    try:
        with open(json_report_path, "r") as f:
            lint_data = json.load(f)
            critical_count = len(lint_data)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Could not parse Pylint JSON report")

    print(f"Critical Pylint issues: {critical_count}")
    return critical_count


def analyze_black_changes(files, report_dir):
    """Check what changes Black would make without applying them."""
    print_section("Analyzing Black Formatting Changes")

    report_path = os.path.join(report_dir, "black_report.txt")

    with open(report_path, "w") as report_file:
        # Use --diff to show changes without applying them
        process = subprocess.run(["black", "--diff", "--color", *files], capture_output=True, text=True, check=False)
        report_file.write(process.stdout)

    print(f"Black formatting report saved to {report_path}")

    # Count files that would be changed
    changed_files = 0
    with open(report_path, "r") as f:
        content = f.read()
        changed_files = content.count("would reformat")

    print(f"Files that would be reformatted by Black: {changed_files}")
    return changed_files


def analyze_isort_changes(files, report_dir):
    """Check what changes isort would make without applying them."""
    print_section("Analyzing Import Sorting Changes")

    report_path = os.path.join(report_dir, "isort_report.txt")

    with open(report_path, "w") as report_file:
        # Use --diff to show changes without applying them
        process = subprocess.run(["isort", "--diff", *files], capture_output=True, text=True, check=False)
        report_file.write(process.stdout)

    print(f"isort report saved to {report_path}")

    # Count files that would be changed
    changed_files = 0
    with open(report_path, "r") as f:
        content = f.read()
        changed_files = content.count("---")  # Each file diff starts with ---

    print(f"Files that would have imports resorted: {changed_files}")
    return changed_files


def create_summary_report(report_dir, stats):
    """Create a summary report with all findings."""
    summary_path = os.path.join(report_dir, "summary_report.txt")

    with open(summary_path, "w") as f:
        f.write("=" * 80 + "\n")
        f.write(" First1KGreek Code Analysis Summary ".center(80, "=") + "\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("Findings:\n")
        f.write(f"- Flake8 issues: {stats['flake8']}\n")
        f.write(f"- Critical Pylint issues: {stats['pylint']}\n")
        f.write(f"- Files that would be reformatted by Black: {stats['black']}\n")
        f.write(f"- Files that would have imports resorted: {stats['isort']}\n\n")

        f.write("Next Steps:\n")
        if stats["pylint"] > 0:
            f.write("1. Fix critical Pylint issues (syntax errors, undefined variables)\n")
            f.write("2. Re-run analysis to verify fixes\n")
            f.write("3. Consider applying Black to a single file as a test\n")
        else:
            f.write("1. Apply Black to a single non-critical file as a test\n")
            f.write("2. Verify functionality after formatting\n")
            f.write("3. Gradually apply formatting to more files\n")

    print(f"\nSummary report saved to {summary_path}")


def main():
    """Run code analysis without modifying any files."""
    parser = argparse.ArgumentParser(description="Analyze Python code quality without enforcing standards.")
    parser.add_argument("--dir", default=".", help="Directory to analyze")
    args = parser.parse_args()

    # Create reports directory
    report_dir = os.path.join(args.dir, "lint_reports")
    os.makedirs(report_dir, exist_ok=True)

    # Ensure tools are installed
    ensure_tools_installed()

    # Collect Python files
    print_section("Collecting Python Files")
    python_files = collect_python_files(args.dir)
    print(f"Found {len(python_files)} Python files to analyze")

    # Run analysis tools
    stats = {}
    stats["flake8"] = run_flake8(python_files, report_dir)
    stats["pylint"] = run_pylint(python_files, report_dir)
    stats["black"] = analyze_black_changes(python_files, report_dir)
    stats["isort"] = analyze_isort_changes(python_files, report_dir)

    # Create summary report
    create_summary_report(report_dir, stats)

    print_section("Analysis Complete")
    print(f"All reports saved to {report_dir}")
    print("Review the summary_report.txt for findings and next steps")


if __name__ == "__main__":
    main()
