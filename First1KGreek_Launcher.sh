#!/bin/bash

# First1KGreek Launcher Script
# This script launches the First1KGreek browser application

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    # Check if python is Python 3
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
    else
        echo "Error: Python 3 is required but not found."
        echo "Please install Python 3 and try again."
        exit 1
    fi
else
    echo "Error: Python is not installed or not in PATH."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Function to open the browser
open_browser() {
    sleep 2  # Give the server a moment to start up
    
    # Open browser based on platform
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "http://localhost:8000"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &>/dev/null; then
            xdg-open "http://localhost:8000"
        elif command -v gnome-open &>/dev/null; then
            gnome-open "http://localhost:8000"
        else
            echo "Unable to automatically open browser. Please open http://localhost:8000 manually."
        fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        start "http://localhost:8000"
    else
        echo "Unable to automatically open browser. Please open http://localhost:8000 manually."
    fi
}

# Launch the browser in the background
open_browser &

# Launch the application
echo "Starting First1KGreek Browser..."
"$PYTHON_CMD" browse_texts_fixed.py

# Keep terminal window open in case of errors
read -p "Press enter to close this window..." 