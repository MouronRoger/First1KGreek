# Linting Troubleshooting Guide

## Common Issues

### Pre-commit Hook Fails with "No such file or directory: 'pylint'"

**Problem:** When trying to commit changes, you get an error like:
```
FileNotFoundError: [Errno 2] No such file or directory: 'pylint'
```

**Solution:**

1. Install the required linting dependencies:
   ```bash
   pip install -r tools/linting/requirements-lint.txt
   ```

2. Reinstall the pre-commit hook:
   ```bash
   ./tools/linting/install_hooks.sh
   ```

3. If you still encounter issues, you can temporarily bypass the pre-commit hook:
   ```bash
   git commit --no-verify -m "Your commit message"
   ```

   However, please fix the linting issues properly before pushing your changes.

### Black or isort Not Found

**Problem:** When running the formatting scripts, you get a "command not found" error.

**Solution:**

1. Install the required tools:
   ```bash
   pip install -r tools/linting/requirements-lint.txt
   ```

2. Make sure you're using the correct Python environment (if you're using virtualenv or conda).

### Linting Changes Breaking Functionality

**Problem:** After applying linting tools, the code no longer works correctly.

**Solution:**

1. Check the backup files created by the formatting tools (with `.bak` extension).

2. Use the incremental formatter with `--dry-run` to preview changes before applying them:
   ```bash
   python tools/linting/format_incremental.py your_file.py --dry-run
   ```

3. If there are specific formatting rules causing issues, you can add exceptions in the code:
   ```python
   # For Black
   # fmt: off
   problematic_code_here
   # fmt: on

   # For Flake8
   # noqa: <error-code>
   ```

## Miscellaneous Tips

### Installing Linting Tools in Virtual Environment

If you're using a virtual environment (recommended), make sure to activate it before installing the linting tools:

```bash
# For venv
source venv/bin/activate  # On Unix/MacOS
venv\Scripts\activate     # On Windows

# Install linting tools
pip install -r tools/linting/requirements-lint.txt
```

### Configuring IDE Support

Many IDEs support automatic linting and formatting:

- **VS Code:** Install the Python, Pylint, and Black extensions
- **PyCharm:** Go to Settings > Tools > Python Integrated Tools and select Black as the formatter

### Manually Running the Linting Tools

You can manually run the linting tools with these commands:

```bash
# Sort imports
python -m isort --profile=black --line-length=120 your_file.py

# Format code
python -m black --line-length=120 your_file.py

# Check for errors
python -m flake8 your_file.py

# Check docstrings
python -m pydocstyle --select=D100,D101,D102,D103 your_file.py
```
