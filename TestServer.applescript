-- TestServer.applescript
-- Simple AppleScript to launch a test HTTP server for First1KGreek

on run
    set projectPath to "/Users/james/Documents/GitHub/First1KGreek"
    set launcherPath to projectPath & "/test_server_launcher.sh"

    -- Make the launcher script executable
    do shell script "chmod +x " & quoted form of launcherPath

    -- Run the launcher script
    tell application "Terminal"
        activate
        do script "cd " & quoted form of projectPath & " && " & quoted form of launcherPath
    end tell

    -- Open the browser after a short delay
    delay 2
    do shell script "open http://localhost:8080/static/test.html"
end run
