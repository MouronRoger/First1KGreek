#!/bin/bash

# MakeDesktopShortcut.sh
# Creates a desktop shortcut for the First1KGreek test server

# Get the project directory
PROJECT_DIR="/Users/james/Documents/GitHub/First1KGreek"

# Change to the project directory
cd "$PROJECT_DIR"

# Make sure scripts are executable
chmod +x test_server_launcher.sh

# Create an Automator workflow application
echo "Creating Automator application..."

# Define Automator application path
APP_PATH="$HOME/Desktop/First1KGreek.app"

# Create the application structure
mkdir -p "$APP_PATH/Contents/MacOS"

# Create the executable script
cat > "$APP_PATH/Contents/MacOS/First1KGreek" << 'EOF'
#!/bin/bash
cd "/Users/james/Documents/GitHub/First1KGreek"
./test_server_launcher.sh
EOF

# Make it executable
chmod +x "$APP_PATH/Contents/MacOS/First1KGreek"

# Create Info.plist
cat > "$APP_PATH/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>First1KGreek</string>
    <key>CFBundleIdentifier</key>
    <string>org.opengreekandlatin.first1kgreek</string>
    <key>CFBundleName</key>
    <string>First1KGreek</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1</string>
</dict>
</plist>
EOF

echo "Desktop shortcut created at $APP_PATH"
echo "Double-click to run the First1KGreek test server."
