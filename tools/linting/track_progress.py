#!/usr/bin/env python3
"""
Track code linting progress across the codebase.

This script analyzes Python files in the codebase to determine what percentage
meet our formatting standards. It checks for:
1. Black formatting compliance
2. Flake8 compliance (based on current rules)
3. isort compliance
4. Critical issue freedom (no undefined variables or syntax errors)
5. Docstring compliance (based on D100,D101,D102,D103)

It generates a progress report to track improvement over time.
"""

import os
import sys
import argparse
import subprocess
import json
import glob
from pathlib import Path
from datetime import datetime


def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def get_python_files(directories, exclude=None):
    """
    Get all Python files in the specified directories.
    
    Args:
        directories: List of directories to scan
        exclude: List of glob patterns to exclude
        
    Returns:
        List of Python file paths
    """
    if exclude is None:
        exclude = []
    
    all_files = []
    for directory in directories:
        files = glob.glob(f"{directory}/**/*.py", recursive=True)
        all_files.extend(files)
    
    # Filter out excluded files
    for pattern in exclude:
        exclude_files = glob.glob(pattern, recursive=True)
        all_files = [f for f in all_files if f not in exclude_files]
    
    return all_files


def check_black_compliance(file_path):
    """
    Check if a file is formatted according to Black.
    
    Returns:
        True if file is properly formatted, False otherwise
    """
    cmd = ["black", "--check", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def check_flake8_compliance(file_path):
    """
    Check if a file passes flake8 checks.
    
    Returns:
        True if file passes flake8, False otherwise
    """
    cmd = ["flake8", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def check_isort_compliance(file_path):
    """
    Check if a file's imports are sorted according to isort.
    
    Returns:
        True if imports are sorted, False otherwise
    """
    cmd = ["isort", "--check", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def check_critical_issues(file_path):
    """
    Check if a file has any critical issues (undefined variables, syntax errors).
    
    Returns:
        True if no critical issues, False otherwise
    """
    cmd = ["pylint", "--disable=all", "--enable=undefined-variable,syntax-error", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def check_docstring_compliance(file_path):
    """
    Check if a file has proper docstrings.
    
    Returns:
        True if docstrings are compliant, False otherwise
    """
    cmd = ["pydocstyle", "--select=D100,D101,D102,D103", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def track_progress(files):
    """
    Track linting progress for a list of files.
    
    Args:
        files: List of file paths to check
        
    Returns:
        Dictionary with progress statistics
    """
    total_files = len(files)
    black_compliant = 0
    flake8_compliant = 0
    isort_compliant = 0
    critical_free = 0
    docstring_compliant = 0
    full_compliant = 0
    
    fully_compliant_files = []
    non_compliant_files = {}
    
    print(f"Checking {total_files} Python files...")
    
    for i, file_path in enumerate(files):
        if i % 10 == 0:
            progress = (i / total_files) * 100
            print(f"Progress: {progress:.2f}% ({i}/{total_files})", end="\r")
        
        # Check each linting aspect
        is_black_compliant = check_black_compliance(file_path)
        is_flake8_compliant = check_flake8_compliance(file_path)
        is_isort_compliant = check_isort_compliance(file_path)
        is_critical_free = check_critical_issues(file_path)
        is_docstring_compliant = check_docstring_compliance(file_path)
        
        # Update counters
        black_compliant += is_black_compliant
        flake8_compliant += is_flake8_compliant
        isort_compliant += is_isort_compliant
        critical_free += is_critical_free
        docstring_compliant += is_docstring_compliant
        
        # Check if fully compliant
        is_fully_compliant = (
            is_black_compliant and 
            is_flake8_compliant and 
            is_isort_compliant and 
            is_critical_free and 
            is_docstring_compliant
        )
        
        if is_fully_compliant:
            full_compliant += 1
            fully_compliant_files.append(file_path)
        else:
            # Record which aspects failed
            non_compliant_files[file_path] = {
                "black": not is_black_compliant,
                "flake8": not is_flake8_compliant,
                "isort": not is_isort_compliant,
                "critical": not is_critical_free,
                "docstring": not is_docstring_compliant
            }
    
    print(f"Progress: 100.00% ({total_files}/{total_files})")
    
    # Calculate percentages
    black_pct = (black_compliant / total_files) * 100 if total_files > 0 else 0
    flake8_pct = (flake8_compliant / total_files) * 100 if total_files > 0 else 0
    isort_pct = (isort_compliant / total_files) * 100 if total_files > 0 else 0
    critical_pct = (critical_free / total_files) * 100 if total_files > 0 else 0
    docstring_pct = (docstring_compliant / total_files) * 100 if total_files > 0 else 0
    full_pct = (full_compliant / total_files) * 100 if total_files > 0 else 0
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_files": total_files,
        "black_compliant": black_compliant,
        "black_percentage": black_pct,
        "flake8_compliant": flake8_compliant,
        "flake8_percentage": flake8_pct,
        "isort_compliant": isort_compliant,
        "isort_percentage": isort_pct,
        "critical_free": critical_free,
        "critical_percentage": critical_pct,
        "docstring_compliant": docstring_compliant,
        "docstring_percentage": docstring_pct,
        "full_compliant": full_compliant,
        "full_percentage": full_pct,
        "fully_compliant_files": fully_compliant_files,
        "non_compliant_files": non_compliant_files
    }


def generate_report(progress, output_file=None, detailed=False):
    """
    Generate a report of linting progress.
    
    Args:
        progress: Progress statistics dictionary
        output_file: Path to save JSON report (if None, won't save)
        detailed: Whether to show detailed information about non-compliant files
    """
    print_section("Linting Progress Report")
    print(f"Total Python files: {progress['total_files']}")
    print(f"Files in full compliance: {progress['full_compliant']} ({progress['full_percentage']:.2f}%)")
    print()
    print("Compliance by category:")
    print(f"- Black formatting:  {progress['black_compliant']} ({progress['black_percentage']:.2f}%)")
    print(f"- Flake8 checks:     {progress['flake8_compliant']} ({progress['flake8_percentage']:.2f}%)")
    print(f"- isort compliance:  {progress['isort_compliant']} ({progress['isort_percentage']:.2f}%)")
    print(f"- No critical issues: {progress['critical_free']} ({progress['critical_percentage']:.2f}%)")
    print(f"- Docstring standards: {progress['docstring_compliant']} ({progress['docstring_percentage']:.2f}%)")
    
    if detailed:
        print_section("Non-Compliant Files Details")
        for file_path, issues in progress['non_compliant_files'].items():
            print(f"\n{file_path}:")
            if issues['black']:
                print("  - Needs Black formatting")
            if issues['flake8']:
                print("  - Has Flake8 issues")
            if issues['isort']:
                print("  - Needs import sorting")
            if issues['critical']:
                print("  - Has critical issues")
            if issues['docstring']:
                print("  - Missing or invalid docstrings")
    
    # Save the report if requested
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(progress, f, indent=2)
        print(f"\nDetailed report saved to: {output_file}")


def main():
    """Run the linting progress tracker."""
    parser = argparse.ArgumentParser(description="Track code linting progress")
    parser.add_argument("--directories", nargs="+", default=["src"], 
                        help="Directories to scan (default: src)")
    parser.add_argument("--exclude", nargs="+", default=[], 
                        help="Glob patterns to exclude")
    parser.add_argument("--output", default="lint_reports/progress.json",
                        help="Output file for detailed report")
    parser.add_argument("--detailed", action="store_true",
                        help="Show detailed information about non-compliant files")
    args = parser.parse_args()
    
    print_section("Tracking Linting Progress")
    print(f"Scanning directories: {', '.join(args.directories)}")
    if args.exclude:
        print(f"Excluding: {', '.join(args.exclude)}")
    
    try:
        # Get files to check
        files = get_python_files(args.directories, args.exclude)
        
        if not files:
            print("No Python files found in the specified directories")
            sys.exit(0)
        
        # Track progress
        progress = track_progress(files)
        
        # Generate report
        generate_report(progress, args.output, args.detailed)
        
        # Exit with status based on progress
        if progress["full_percentage"] >= 80:
            print("\n✅ We've reached 80% or more compliance!")
            sys.exit(0)
        else:
            print(f"\n⚠️ We're at {progress['full_percentage']:.2f}% compliance, target is 80%")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 