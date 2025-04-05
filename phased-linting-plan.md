# Phased Linting Strategy for First1KGreek

## Phase 1: Observation Without Enforcement

### 1.1 Setup Initial Configuration

```python
# setup.cfg
[flake8]
# Start with very permissive settings
ignore = E121,E123,E126,E226,E24,E704,W503,W504,E501
max-line-length = 160
exclude = .git,__pycache__,build,dist
# Only report, don't fail builds
exit-zero = True

[pylint]
# Start with minimal checks
disable=all
enable=syntax-error,undefined-variable,unused-import
# High threshold to only catch critical issues
fail-under=1
```

### 1.2 Create Analysis Script

```python
#!/usr/bin/env python3
"""
First1KGreek Lint Analysis Tool

This script runs linting tools on the codebase but doesn't enforce any rules.
It generates reports to help understand the current state of the code.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
from datetime import datetime

def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def ensure_tools_installed():
    """Check if required tools are installed and install if missing."""
    required_tools = ['flake8', 'pylint', 'black', 'isort']
    
    for tool in required_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=False)
        except FileNotFoundError:
            print(f"Installing {tool}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', tool], check=True)

def collect_python_files(directory='.', exclude_dirs=None):
    """Collect all Python files in the directory."""
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', 'venv', 'env', '.env', 'build', 'dist']
    
    python_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def run_flake8(files, report_dir):
    """Run flake8 on the files and generate a report."""
    print_section("Running Flake8")
    
    report_path = os.path.join(report_dir, 'flake8_report.txt')
    
    with open(report_path, 'w') as report_file:
        process = subprocess.run(
            ['flake8', '--exit-zero', '--statistics', '--count', *files],
            capture_output=True,
            text=True,
            check=False
        )
        report_file.write(process.stdout)
        
        # Also capture error categories
        process = subprocess.run(
            ['flake8', '--exit-zero', '--statistics', *files],
            capture_output=True,
            text=True,
            check=False
        )
        report_file.write("\n\nError Categories:\n")
        report_file.write(process.stdout)
    
    print(f"Flake8 report saved to {report_path}")
    
    # Print summary
    error_count = 0
    with open(report_path, 'r') as f:
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
    
    report_path = os.path.join(report_dir, 'pylint_report.txt')
    json_report_path = os.path.join(report_dir, 'pylint_report.json')
    
    # Run with minimal checks first as specified in setup.cfg
    with open(report_path, 'w') as report_file:
        process = subprocess.run(
            ['pylint', '--output-format=text', *files],
            capture_output=True,
            text=True,
            check=False
        )
        report_file.write(process.stdout)
    
    # Run with full checks but only generate JSON report for analysis
    subprocess.run(
        ['pylint', '--disable=all', '--enable=syntax-error,undefined-variable,unused-import', 
         '--output-format=json', *files, '--output=' + json_report_path],
        check=False
    )
    
    print(f"Pylint report saved to {report_path}")
    
    # Count critical issues
    critical_count = 0
    try:
        with open(json_report_path, 'r') as f:
            lint_data = json.load(f)
            critical_count = len(lint_data)
    except (json.JSONDecodeError, FileNotFoundError):
        print("Could not parse Pylint JSON report")
    
    print(f"Critical Pylint issues: {critical_count}")
    return critical_count

def analyze_black_changes(files, report_dir):
    """Check what changes Black would make without applying them."""
    print_section("Analyzing Black Formatting Changes")
    
    report_path = os.path.join(report_dir, 'black_report.txt')
    
    with open(report_path, 'w') as report_file:
        # Use --diff to show changes without applying them
        process = subprocess.run(
            ['black', '--diff', '--color', *files],
            capture_output=True,
            text=True,
            check=False
        )
        report_file.write(process.stdout)
    
    print(f"Black formatting report saved to {report_path}")
    
    # Count files that would be changed
    changed_files = 0
    with open(report_path, 'r') as f:
        content = f.read()
        changed_files = content.count('would reformat')
    
    print(f"Files that would be reformatted by Black: {changed_files}")
    return changed_files

def analyze_isort_changes(files, report_dir):
    """Check what changes isort would make without applying them."""
    print_section("Analyzing Import Sorting Changes")
    
    report_path = os.path.join(report_dir, 'isort_report.txt')
    
    with open(report_path, 'w') as report_file:
        # Use --diff to show changes without applying them
        process = subprocess.run(
            ['isort', '--diff', *files],
            capture_output=True,
            text=True,
            check=False
        )
        report_file.write(process.stdout)
    
    print(f"isort report saved to {report_path}")
    
    # Count files that would be changed
    changed_files = 0
    with open(report_path, 'r') as f:
        content = f.read()
        changed_files = content.count('---')  # Each file diff starts with ---
    
    print(f"Files that would have imports resorted: {changed_files}")
    return changed_files

def create_summary_report(report_dir, stats):
    """Create a summary report with all findings."""
    summary_path = os.path.join(report_dir, 'summary_report.txt')
    
    with open(summary_path, 'w') as f:
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
        if stats['pylint'] > 0:
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
    parser = argparse.ArgumentParser(description='Analyze Python code quality without enforcing standards.')
    parser.add_argument('--dir', default='.', help='Directory to analyze')
    args = parser.parse_args()
    
    # Create reports directory
    report_dir = os.path.join(args.dir, 'lint_reports')
    os.makedirs(report_dir, exist_ok=True)
    
    # Ensure tools are installed
    ensure_tools_installed()
    
    # Collect Python files
    print_section("Collecting Python Files")
    python_files = collect_python_files(args.dir)
    print(f"Found {len(python_files)} Python files to analyze")
    
    # Run analysis tools
    stats = {}
    stats['flake8'] = run_flake8(python_files, report_dir)
    stats['pylint'] = run_pylint(python_files, report_dir)
    stats['black'] = analyze_black_changes(python_files, report_dir)
    stats['isort'] = analyze_isort_changes(python_files, report_dir)
    
    # Create summary report
    create_summary_report(report_dir, stats)
    
    print_section("Analysis Complete")
    print(f"All reports saved to {report_dir}")
    print("Review the summary_report.txt for findings and next steps")

if __name__ == "__main__":
    main()
```

## Phase 2: Targeted Fixing of Critical Issues

### 2.1 Create File-by-File Fix Script

```python
#!/usr/bin/env python3
"""
First1KGreek Critical Issue Fixer

This script identifies and optionally fixes critical issues in individual files.
It works on one file at a time to minimize risk of breaking functionality.
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path

def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def get_critical_issues(file_path):
    """Get critical issues in the file using pylint."""
    process = subprocess.run(
        ['pylint', '--disable=all', '--enable=syntax-error,undefined-variable,unused-import', 
         '--output-format=json', file_path],
        capture_output=True,
        text=True,
        check=False
    )
    
    try:
        if process.stdout.strip():
            issues = json.loads(process.stdout)
            return issues
        return []
    except json.JSONDecodeError:
        print(f"Error parsing pylint output: {process.stdout}")
        return []

def check_syntax(file_path):
    """Check Python syntax without executing the file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    try:
        compile(source, file_path, 'exec')
        return None
    except SyntaxError as e:
        return e

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.bak"
    with open(file_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    return backup_path

def fix_unused_imports(file_path):
    """Fix unused imports in the file."""
    print(f"Checking for unused imports in {file_path}")
    
    process = subprocess.run(
        ['autoflake', '--remove-all-unused-imports', '--in-place', file_path],
        capture_output=True,
        text=True,
        check=False
    )
    
    if process.stderr:
        print(f"Error while fixing unused imports: {process.stderr}")
        return False
    
    return True

def process_file(file_path, fix=False):
    """Process a single file to identify and optionally fix issues."""
    print_section(f"Processing {file_path}")
    
    # Check syntax first
    syntax_error = check_syntax(file_path)
    if syntax_error:
        print(f"Syntax error: {syntax_error}")
        print("Cannot safely fix this file automatically")
        return False
    
    # Get critical issues
    issues = get_critical_issues(file_path)
    
    if not issues:
        print("No critical issues found")
        return True
    
    print(f"Found {len(issues)} critical issues:")
    for issue in issues:
        print(f"Line {issue.get('line', '?')}: {issue.get('message', 'Unknown issue')}")
    
    if not fix:
        print("\nRun with --fix to attempt automatic fixes")
        return False
    
    # Create backup
    backup_path = backup_file(file_path)
    print(f"Created backup at {backup_path}")
    
    # Apply fixes
    fixed = True
    
    # Check for unused imports
    if any('unused-import' in issue.get('message', '') for issue in issues):
        if not fix_unused_imports(file_path):
            fixed = False
    
    # Re-check issues after fixes
    remaining_issues = get_critical_issues(file_path)
    
    if remaining_issues:
        print(f"\nStill have {len(remaining_issues)} issues after automatic fixes:")
        for issue in remaining_issues:
            print(f"Line {issue.get('line', '?')}: {issue.get('message', 'Unknown issue')}")
        print("\nManual intervention required")
        fixed = False
    else:
        print("\nAll critical issues fixed successfully")
    
    return fixed

def main():
    """Process files to identify and fix critical issues."""
    parser = argparse.ArgumentParser(description='Find and fix critical issues in Python files.')
    parser.add_argument('file', nargs='+', help='Python file(s) to process')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix issues')
    args = parser.parse_args()
    
    # Ensure autoflake is installed
    try:
        subprocess.run(['autoflake', '--version'], capture_output=True, check=False)
    except FileNotFoundError:
        print("Installing autoflake...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'autoflake'], check=True)
    
    # Process each file
    success = True
    for file_path in args.file:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            success = False
            continue
            
        if not file_path.endswith('.py'):
            print(f"Warning: {file_path} does not appear to be a Python file, skipping")
            continue
            
        if not process_file(file_path, args.fix):
            success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## Phase 3: Gradual Style Enforcement

### 3.1 Updated Linting Configuration

```ini
# setup.cfg - Phase 3
[flake8]
# Still permissive but more strict than before
ignore = E121,E123,E126,E226,E24,W503,W504
max-line-length = 120
exclude = .git,__pycache__,build,dist,*.bak

[pylint]
# Expanded checks but still focused on correctness over style
disable=C0103,C0111,C0303,C0330,C0326
enable=syntax-error,undefined-variable,unused-import,unused-variable,reimported,redefined-outer-name
fail-under=5

[isort]
profile = black
line_length = 120

[tool.black]
line-length = 120
```

### 3.2 Create Incremental Formatting Script

```python
#!/usr/bin/env python3
"""
First1KGreek Incremental Formatter

This script applies formatting incrementally to files,
running tests after each change to ensure functionality is preserved.
"""

import os
import sys
import subprocess
import argparse
import tempfile
import shutil
from pathlib import Path

def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.bak"
    with open(file_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    return backup_path

def run_tests():
    """Run the test suite."""
    print("Running tests...")
    
    # Adapt this to your test command
    test_command = ['python', '-m', 'unittest', 'discover']
    
    process = subprocess.run(
        test_command,
        capture_output=True,
        text=True,
        check=False
    )
    
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
    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False
    )
    
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
        'isort': ['--profile=black'],
        'black': ['--line-length=120'],
        'autoflake': ['--remove-all-unused-imports', '--in-place'],
    }
    
    success = True
    
    for tool in tools:
        if tool not in tool_configs:
            print(f"Unknown tool: {tool}")
            continue
        
        if dry_run:
            # For dry run, just show what would change
            if tool == 'black':
                subprocess.run(['black', '--diff', file_path, *tool_configs[tool]], check=False)
            elif tool == 'isort':
                subprocess.run(['isort', '--diff', file_path, *tool_configs[tool]], check=False)
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
    parser = argparse.ArgumentParser(description='Format Python files incrementally.')
    parser.add_argument('file', nargs='+', help='Python file(s) to process')
    parser.add_argument('--tools', nargs='+', default=['isort', 'black', 'autoflake'],
                        help='Tools to apply in order (default: isort black autoflake)')
    parser.add_argument('--no-tests', action='store_true', help='Skip running tests after each tool')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying them')
    parser.add_argument('--no-restore', action='store_true', help='Do not restore from backup on test failure')
    args = parser.parse_args()
    
    # Ensure tools are installed
    for tool in args.tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=False)
        except FileNotFoundError:
            print(f"Installing {tool}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', tool], check=True)
    
    # Process each file
    success = True
    for file_path in args.file:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            success = False
            continue
            
        if not file_path.endswith('.py'):
            print(f"Warning: {file_path} does not appear to be a Python file, skipping")
            continue
            
        if not process_file(
            file_path, 
            args.tools, 
            run_tests_after=not args.no_tests,
            dry_run=args.dry_run,
            restore_on_failure=not args.no_restore
        ):
            success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## Phase 4: Implementing a Pre-Commit Hook

### 4.1 Create Pre-Commit Hook

```python
#!/usr/bin/env python3
"""
First1KGreek Pre-Commit Hook

This script runs basic linting checks on staged Python files.
It will prevent commits if critical issues are found.
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path

def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def get_staged_python_files():
    """Get list of staged Python files."""
    process = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True,
        check=True
    )
    
    files = process.stdout.strip().split('\n')
    return [f for f in files if f.endswith('.py') and os.path.exists(f)]

def check_syntax(file_path):
    """Check Python syntax without executing the file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    try:
        compile(source, file_path, 'exec')
        return True
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return False

def check_critical_issues(file_path):
    """Check for critical issues using pylint."""
    process = subprocess.run(
        ['pylint', '--disable=all', '--enable=syntax-error,undefined-variable', 
         '--output-format=json', file_path],
        capture_output=True,
        text=True,
        check=False
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

def main():
    """Run pre-commit checks on staged Python files."""
    print_section("Pre-Commit Checks")
    
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
```

### 4.2 Install Pre-Commit Hook

```bash
#!/bin/bash
# install_hooks.sh

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy pre-commit hook
cp hooks/pre-commit.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "Pre-commit hook installed successfully"
```

## Implementation Approach

1. Start with the Analysis Script (Phase 1) to understand the current state
2. Fix critical issues one file at a time using the Critical Issue Fixer (Phase 2)
3. Apply formatting incrementally with the Incremental Formatter (Phase 3)
4. Once code is stabilized, implement the Pre-Commit Hook (Phase 4)

This phased approach minimizes the risk of breaking functionality while gradually improving code quality.

## Phase 1 Progress Update - Apr 05, 2025

We've made significant progress on implementing the linting plan:

1. ✅ Created a base `.flake8` configuration with minimal rules
   ```
   [flake8]
   max-line-length = 120
   exclude = .git,__pycache__,venv,backup
   # Start with minimal rules, add more over time
   select = E9,F63,F7,F82
   ```

2. ✅ Formatted these directories:
   - src/first1k/utils/
   - src/first1k/xml_utils/

3. ✅ Formatted test files:
   - simple_test.py
   - simple_xml_test.py
   - simple_integration_test.py

4. ✅ Created tools for automation:
   - tools/linting/batch_format_directory.py: New script to batch process entire directories
   - Set up GitHub Actions workflow for weekly formatting (.github/workflows/weekly-linting.yml)

5. ✅ Created CONTRIBUTING.md with coding standards documentation

### Next Steps

1. ◻️ Continue formatting the remaining directories in this order:
   - src/first1k/handlers/
   - src/first1k/editor/
   - src/first1k/search/
   - src/first1k/server/
   - src/first1k/import_export/

2. ◻️ Address CSS variables issues in browse_texts_fixed.py

3. ◻️ Once we reach 80% of files formatted, introduce pydocstyle with:
   ```bash
   pip install pydocstyle
   pydocstyle --select=D100,D101,D102,D103 src/first1k/
   ```

4. ◻️ Gradually expand Flake8 rules to include more checks:
   ```
   # Phase 2 flake8 config
   [flake8]
   max-line-length = 120
   exclude = .git,__pycache__,venv,backup
   # Adding more rules
   select = E9,F63,F7,F82,E225,E226,E227,E228,F401,F821
   ```
