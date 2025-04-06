# First1KGreek Linting Tools

This directory contains tools for implementing a phased linting strategy for the First1KGreek project.

## Installation

Install the required dependencies:

```bash
pip install -r requirements-lint.txt
```

## Phase 1: Analysis Without Enforcement

Run analysis to understand the current state of the codebase without making any changes:

```bash
# From the project root
python tools/linting/analyze_code.py
```

This will generate reports in a `lint_reports` directory, including:
- flake8_report.txt
- pylint_report.txt
- black_report.txt
- isort_report.txt
- summary_report.txt

## Phase 2: Fixing Critical Issues

Fix critical issues one file at a time:

```bash
# First check what issues exist (without fixing)
python tools/linting/fix_critical.py path/to/file.py

# Apply fixes
python tools/linting/fix_critical.py path/to/file.py --fix
```

## Phase 3: Incremental Formatting

Apply formatting incrementally to ensure functionality is preserved:

```bash
# Show changes that would be made without applying them
python tools/linting/format_incremental.py path/to/file.py --dry-run

# Apply formatting and run tests to verify functionality
python tools/linting/format_incremental.py path/to/file.py

# Apply formatting without running tests
python tools/linting/format_incremental.py path/to/file.py --no-tests
```

## Phase 4: Pre-Commit Hook

Install the pre-commit hook to enforce standards in Git workflow:

```bash
bash tools/linting/install_hooks.sh
```

The hook will automatically run on `git commit` operations and prevent commits if critical issues are found.

## Recommended Workflow

1. Start with Phase 1 to understand the current state of the codebase
2. Fix critical issues (Phase 2) one file at a time
3. Apply formatting (Phase 3) incrementally, starting with non-critical files
4. Once the codebase is stabilized, implement the pre-commit hook (Phase 4)

This phased approach minimizes the risk of breaking functionality while gradually improving code quality.
