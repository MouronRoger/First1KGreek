# First1KGreek Repository Linting Guide

## Advisory Linting Approach

This repository uses an **advisory linting** approach to gradually improve code quality without breaking existing functionality. Automated formatting tools are **not** run on the entire codebase as they may introduce functional regressions.

**Important:** Linting issues never block commits. This is by design to ensure that development can continue without interruption.

## Linting Standards

For all new or modified code, follow these standards:

1. Format using **Black** (line length: 88 characters)
2. Lint using **flake8**
3. Ensure top-level docstrings per **pydocstyle D100** series
4. Use consistent **4-space indentation**
5. Do not leave functions undocumented

## Pylint Advisory Tool

The repository includes a pylint advisory tool that helps identify potential issues without automatically changing code. Use it as follows:

```bash
# Install pylint if not already installed
pip install pylint

# Run on a specific file
python lint_advisory.py path/to/file.py

# Run on multiple files with summary
python lint_advisory.py file1.py file2.py --summary

# Show only errors (not warnings)
python lint_advisory.py path/to/file.py --error-only

# Update the code quality tracking file
python lint_advisory.py path/to/file.py --update-tracker
```

## Code Quality Tracking

The repository maintains a `code_quality.md` file that tracks the linting status of all files. This file is updated manually or using the `--update-tracker` flag with the linting tool.

File statuses are marked as:
- ✅ **Fully Compliant**: Passes all linting checks with no issues
- 🔄 **Partially Improved**: Some linting issues addressed, others remain
- ⚠️ **Not Yet Addressed**: Original code with linting issues not yet reviewed

To update the quality tracker:
```bash
python lint_advisory.py path/to/file.py --update-tracker
```

## Linting Rules

When applying linting recommendations:

1. **⚠️ Fix only what you touch** — or what you can clearly see in the local context of the change.
2. **🛑 Never run** auto-formatters or linters repo-wide.
3. **✅ Preserve** existing functionality when making formatting changes.
4. **📝 Document** your code with clear docstrings following the pydocstyle D100 series.
5. **🔍 Test** thoroughly after making any changes.

## Adding Pylint to Your Workflow

1. **Before Coding**: Consider running the advisory linter on files you plan to modify.
2. **During Development**: Make small, incremental improvements to linting issues.
3. **After Changes**: Run the linter again to verify improvements and update the quality tracker.

## Configuration

The repository includes a `.pylintrc` configuration file that has been adjusted to be compatible with Black formatting and the repository's other linting rules.

### Important Notes

- Pylint messages are **advisory only** and should be reviewed with care.
- Some pylint messages may conflict with Black's formatting style; in these cases, **Black's formatting takes precedence**.
- Focus on improving **one file at a time** rather than attempting to fix everything at once.
- Linting issues **never block commits** - they are purely informational.

## Linting Category Priorities

Address linting issues in this order of priority:

1. **Errors (E)**: Likely bugs or serious issues
2. **Warnings (W)**: Potential problems that should be addressed
3. **Convention (C)**: Style issues that can be improved
4. **Refactor (R)**: Code that could be refactored for better quality

## Pre-Commit Hook (Optional)

For developers who want linting feedback before committing, but without blocking commits, you can set up an optional pre-commit hook:

```bash
#!/bin/sh
# Optional pre-commit hook that runs linting without blocking

# Get list of staged Python files
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$FILES" ]; then
  echo "Running linting checks on staged Python files..."
  python lint_advisory.py $FILES --summary
  
  # Optionally update the quality tracker
  # python lint_advisory.py $FILES --update-tracker
fi

# Always exit with success (never block a commit)
exit 0
```

Save this as `.git/hooks/pre-commit` and make it executable:
```bash
chmod +x .git/hooks/pre-commit
``` 