#!/bin/sh
# Optional non-blocking pre-commit hook for First1KGreek repository
# This hook runs linting checks but never blocks commits
# 
# To install:
# 1. Copy this file to .git/hooks/pre-commit
# 2. Make it executable: chmod +x .git/hooks/pre-commit

# Get list of staged Python files
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$FILES" ]; then
  echo "=========================================="
  echo "Running advisory linting on staged Python files..."
  echo "=========================================="
  python lint_advisory.py $FILES --summary
  
  echo ""
  echo "Note: This is advisory only and will not block your commit."
  echo "Consider addressing issues before pushing to the repository."
  
  # Uncomment to update the quality tracker automatically
  # python lint_advisory.py $FILES --update-tracker
fi

# Always exit with success (0) to never block a commit
exit 0 