# First1KGreek IDE Setup Guide

This guide helps you set up your development environment to automatically apply the project's code formatting standards.

## Automatic Formatting Tools

The First1KGreek project uses the following code quality tools:

- **Black**: Code formatter that enforces a consistent style
- **isort**: Sorts imports according to PEP8 standards  
- **Flake8**: Linter to identify code quality issues
- **pydocstyle**: Checks docstring formatting and completeness

## VS Code Setup

1. Install the following extensions:
   - Python (Microsoft)
   - Black Formatter (Microsoft)
   - Flake8 (Microsoft)

2. The project includes a `.vscode/settings.json` file with the recommended settings:
   - Auto-formatting on save with Black
   - Auto-organizing imports on save 
   - Flake8 linting with project-specific rules
   - Docstring checking

3. To activate these settings:
   - Open VS Code in the project directory 
   - When prompted "Do you want to allow the workspace settings?", click "Allow"

## PyCharm Setup

1. Enable the Black formatter:
   - Go to Settings/Preferences → Tools → Python Integrated Tools
   - Set "Formatter" to "Black"
   - Check "Reformat code on save"

2. Set up isort:
   - Go to Settings/Preferences → Editor → Code Style → Python
   - Go to the "Imports" tab
   - Enable "Sort imports on the fly"
   - Check "Join imported names from the same module"
   - Set "Sort imports" section to "Line length" 120

3. Configure Flake8 integration:
   - Go to Settings/Preferences → Editor → Inspections
   - Under Python → PEP 8 coding style violation, set it to enabled
   - Go to Settings/Preferences → Tools → Python Integrated Tools → Linters
   - Enable Flake8 and configure arguments to include `--max-line-length=120`

4. The project includes the following PyCharm configuration files:
   - `.idea/codeStyles/Project.xml` - Black-compatible code style settings
   - `.idea/inspectionProfiles/Project_Default.xml` - Inspection settings

## Pre-commit Hooks

For automatic formatting before each commit:

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Set up the hooks:
   ```bash
   pre-commit install
   ```

3. The project's `.pre-commit-config.yaml` file configures:
   - Black formatting
   - isort import sorting  
   - Flake8 checks
   - Trailing whitespace and end-of-file fixes

## Manual Formatting

You can also manually format files:

```bash
# Format a single file with all tools
python tools/linting/format_incremental.py path/to/file.py

# Format an entire directory
python tools/linting/batch_format_directory.py path/to/directory
```

## Checking Compliance

To check if your code meets all standards:

```bash
python tools/linting/track_progress.py
```

This will generate a detailed report of compliance levels across different formatting aspects. 