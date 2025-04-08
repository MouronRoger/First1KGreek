# First1KGreek Repository Linting Guide

## Advisory Linting Approach

This repository uses an **advisory linting** approach to gradually improve code quality without breaking existing functionality. Automated formatting tools are **not** run on the entire codebase as they may introduce functional regressions.

**Important:** Linting issues never block commits. This is by design to ensure that development can continue without interruption.

## XML File Exclusion Policy

**⚠️ CRITICAL: XML files are NEVER to be linted, formatted, or modified by automatic tools.**

The repository contains valuable XML data files (in `/volume_xml/` and other directories) that:
- Contain critical Greek text data in specific formats
- Must maintain their exact formatting and structure
- Should only be modified manually after careful review
- Are automatically excluded from all linting processes

All linting tools in this repository are configured to:
1. Only process Python (.py) files
2. Explicitly skip XML files with a warning message
3. Require file extensions to match exactly (.py)

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

Note: The linting tool will only process Python (.py) files and will skip any other file types with a warning message.

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

The repository includes a `.pylintrc` configuration file that has been adjusted to be compatible with Black formatting and the repository's other linting rules. Outdated pylint options have been removed to ensure compatibility with the current version of pylint.

### Important Notes

- Pylint messages are **advisory only** and should be reviewed with care.
- Some pylint messages may conflict with Black's formatting style; in these cases, **Black's formatting takes precedence**.
- Focus on improving **one file at a time** rather than attempting to fix everything at once.
- Linting issues **never block commits** - they are purely informational.
- XML files and non-Python files are **never processed** by any linting tools.

## Linting Category Priorities

Address linting issues in this order of priority:

1. **Errors (E)**: Likely bugs or serious issues
2. **Warnings (W)**: Potential problems that should be addressed
3. **Convention (C)**: Style issues that can be improved
4. **Refactor (R)**: Code that could be refactored for better quality

## Pre-Commit Hook (Installed and Non-Blocking)

The repository includes a non-blocking pre-commit hook that provides advisory linting feedback before committing without ever preventing commits from proceeding.

The pre-commit hook will:
1. Check Python syntax (advisory only)
2. Look for critical issues using pylint (advisory only)
3. Always return exit code 0 (success) to allow the commit to proceed
4. Only process Python (.py) files, never XML or other file types

If you want to customize the pre-commit hook, it's located at `.git/hooks/pre-commit`.

If you accidentally disable or modify the hook, you can restore a non-blocking version from our template:

```bash
cp pre-commit-hook-example.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
``` 