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

# Define the default port
PORT=8000

# First, kill any existing processes on port 8000
echo "Checking for existing processes on port $PORT..."
if command -v lsof &>/dev/null; then
    EXISTING_PID=$(lsof -ti:$PORT)
    if [ -n "$EXISTING_PID" ]; then
        echo "Found process using port $PORT. Attempting to kill PID: $EXISTING_PID"
        kill -9 $EXISTING_PID
        sleep 1
    fi
fi

# Function to find an available port
find_available_port() {
    local port=$1
    while [ $(lsof -ti:$port | wc -l) -gt 0 ]; do
        echo "Port $port is still in use, trying next port..."
        port=$((port + 1))
    done
    echo $port
}

# Find an available port if 8000 is still in use
if command -v lsof &>/dev/null; then
    if [ $(lsof -ti:$PORT | wc -l) -gt 0 ]; then
        PORT=$(find_available_port $PORT)
    fi
fi

echo "Using port: $PORT"

# Modify the Python file to use the selected port
if [ $PORT -ne 8000 ]; then
    echo "Temporarily modifying browse_texts_fixed.py to use port $PORT..."
    # Using sed to replace PORT = 8000 with the new port number
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS requires different sed syntax
        sed -i '' "s/PORT = 8000/PORT = $PORT/" browse_texts_fixed.py
    else
        # Linux/Windows
        sed -i "s/PORT = 8000/PORT = $PORT/" browse_texts_fixed.py
    fi
fi

# Function to open the browser
open_browser() {
    sleep 2  # Give the server a moment to start up
    
    # Open browser based on platform
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "http://localhost:$PORT"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &>/dev/null; then
            xdg-open "http://localhost:$PORT"
        elif command -v gnome-open &>/dev/null; then
            gnome-open "http://localhost:$PORT"
        else
            echo "Unable to automatically open browser. Please open http://localhost:$PORT manually."
        fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        start "http://localhost:$PORT"
    else
        echo "Unable to automatically open browser. Please open http://localhost:$PORT manually."
    fi
}

# Launch the browser in the background
open_browser &

# Launch the application
echo "Starting First1KGreek Browser on port $PORT..."
"$PYTHON_CMD" browse_texts_fixed.py

# Restore the original port setting in the Python file if we changed it
if [ $PORT -ne 8000 ]; then
    echo "Restoring original port setting in browse_texts_fixed.py..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS requires different sed syntax
        sed -i '' "s/PORT = $PORT/PORT = 8000/" browse_texts_fixed.py
    else
        # Linux/Windows
        sed -i "s/PORT = $PORT/PORT = 8000/" browse_texts_fixed.py
    fi
fi

# Keep terminal window open in case of errors
read -p "Press enter to close this window..." 