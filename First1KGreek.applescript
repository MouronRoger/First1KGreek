-- First1KGreek Browser Launcher
-- This AppleScript launches the First1KGreek browser application

on run
    -- Get the path to the launcher script
    set scriptPath to (path to me as text)
    set appContainer to container of (path to me as alias)
    set projectPath to POSIX path of appContainer
    set launcherPath to projectPath & "First1KGreek_Launcher.sh"
    
    -- Make the launcher script executable
    do shell script "chmod +x " & quoted form of launcherPath
    
    -- Run the launcher script
    tell application "Terminal"
        activate
        do script "cd " & quoted form of projectPath & " && " & quoted form of launcherPath
    end tell
end run 