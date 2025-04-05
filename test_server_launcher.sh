#!/bin/bash

# Test server launcher for First1KGreek Browser
# This script launches a minimal HTTP server for testing

# Kill any existing processes on port 8080
if command -v lsof &>/dev/null; then
    EXISTING_PID=$(lsof -ti:8080)
    if [ -n "$EXISTING_PID" ]; then
        echo "Found process using port 8080. Killing PID: $EXISTING_PID"
        kill -9 $EXISTING_PID
        sleep 1
    fi
fi

# Make sure test.html is available
if [ ! -f "static/test.html" ]; then
    echo "Creating test page..."
    mkdir -p static
    cat > static/test.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>First1KGreek Test Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #2c5282;
        }
    </style>
</head>
<body>
    <h1>First1KGreek Browser Test Page</h1>
    <p>If you can see this page, the server is working correctly.</p>
    <p>Time: <span id="current-time"></span></p>
    
    <script>
        document.getElementById('current-time').textContent = new Date().toLocaleTimeString();
    </script>
</body>
</html>
EOF
fi

# Launch the application with test configuration
echo "Starting simple HTTP server on port 8080..."
python3 simple_server.py --port 8080

# Keep terminal window open in case of errors
read -p "Press enter to close this window..." 