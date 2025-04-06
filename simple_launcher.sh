#!/bin/bash

# Simple test launcher for First1KGreek Browser
# This script tests basic functionality

# Kill any existing processes on port 8000 or 8080
if command -v lsof &>/dev/null; then
    for PORT in 8000 8080; do
        EXISTING_PID=$(lsof -ti:$PORT)
        if [ -n "$EXISTING_PID" ]; then
            echo "Found process using port $PORT. Killing PID: $EXISTING_PID"
            kill -9 $EXISTING_PID
            sleep 1
        fi
    done
fi

# Choose a port
PORT=8080

# Launch the application with test configuration
echo "Starting First1KGreek Browser test on port $PORT..."
python3 browse_texts_fixed.py --port $PORT

# Keep terminal window open in case of errors
read -p "Press enter to close this window..."
