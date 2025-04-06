-- First1KGreek Browser Launcher
-- This AppleScript launches the First1KGreek browser application

on run
    -- Use the absolute path to the project directory
    set projectPath to "/Users/james/Documents/GitHub/First1KGreek"
    set launcherPath to projectPath & "/First1KGreek_Launcher.sh"

    -- Make the launcher script executable
    do shell script "chmod +x " & quoted form of launcherPath

    -- Run the launcher script
    tell application "Terminal"
        activate
        do script "cd " & quoted form of projectPath & " && " & quoted form of launcherPath
    end tell
end run
