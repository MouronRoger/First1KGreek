#!/bin/bash
# Install Git hooks for First1KGreek

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy pre-commit hook
cp tools/linting/pre-commit-hook.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Install required dependencies
echo "Installing required dependencies..."
pip install --quiet pylint flake8 black isort autoflake

# Verify installation
echo "Verifying pylint installation..."
if ! command -v pylint &> /dev/null; then
    echo "Warning: pylint couldn't be found in PATH after installation"
    echo "You may need to install it manually: pip install pylint"
fi

echo "Pre-commit hook installed successfully"
echo "The hook will run automatically on future commits"
