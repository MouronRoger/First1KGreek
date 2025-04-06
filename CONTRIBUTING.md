# Contributing to First1KGreek

Thank you for your interest in contributing to the First1KGreek project. This document outlines the coding standards and linting conventions we follow to maintain consistent code quality.

## Code Formatting Guidelines

### Python Formatting Standards

We follow these standards for Python code:

1. **Black**: We use Black for code formatting with a 120-character line limit
2. **isort**: We use isort with Black compatibility to sort imports
3. **Flake8**: We use Flake8 for style guide enforcement
4. **pydocstyle**: We use pydocstyle for docstring conventions (focused on public functions)

### Current Linting Configuration

Our current `.flake8` configuration is:

```
[flake8]
max-line-length = 120
exclude = .git,__pycache__,venv,backup
# Start with minimal rules, add more over time
select = E9,F63,F7,F82
```

We are gradually enabling more linting rules as we clean up the codebase.

## How to Format Your Code

### Manual Formatting

Before submitting changes, please format your code with:

```bash
# Sort imports
python -m isort --profile=black --line-length=120 your_file.py

# Format code
python -m black --line-length=120 your_file.py

# Remove unused imports
python -m autoflake --remove-all-unused-imports --in-place your_file.py

# Check for errors
python -m flake8 your_file.py
```

### Using Our Formatting Tools

We provide tools to help with formatting:

1. Use the incremental formatter to safely format files:
   ```bash
   python tools/linting/format_incremental.py your_file.py
   ```

2. Run with `--dry-run` to see changes without applying them:
   ```bash
   python tools/linting/format_incremental.py your_file.py --dry-run
   ```

3. Format an entire directory at once:
   ```bash
   python tools/linting/batch_format_directory.py path/to/directory --dry-run
   ```

### Pre-commit Hook

We use a pre-commit hook to check for basic code quality issues before commits:

1. Install the pre-commit hook:
   ```bash
   ./tools/linting/install_hooks.sh
   ```

2. The hook will automatically run on each commit and prevent commits with critical issues.

3. If you encounter issues with the pre-commit hook, see the [Troubleshooting Guide](tools/linting/TROUBLESHOOTING.md).

## Docstring Conventions

We follow the Google style for docstrings:

```python
def example_function(param1, param2):
    """Summary of function purpose.

    More detailed description if needed.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of the return value

    Raises:
        ValueError: If an invalid value is provided
    """
    # function body
```

## Pull Request Process

1. Make sure your code passes all linting checks
2. Run the test suite to ensure no functionality is broken
3. Update documentation as necessary
4. Submit your pull request with a clear description of the changes

## Troubleshooting

If you encounter issues with the linting tools, see our [Troubleshooting Guide](tools/linting/TROUBLESHOOTING.md).

Thank you for following these guidelines!
