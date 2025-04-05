# First1KGreek Desktop Shortcut

This folder contains files to create a desktop shortcut for launching the First1KGreek Browser application.

## Option 1: AppleScript Application (Recommended for macOS)

### Creating the Application:

1. Open the `First1KGreek.applescript` file with Script Editor (built into macOS)
2. In Script Editor, go to File > Export
3. Change the File Format to "Application"
4. Name it "First1KGreek Browser"
5. Select "Save as stay-open application" if you want the script to stay running
6. Click "Save"
7. Move the resulting application to your Desktop or Dock

### Using the Application:

Simply double-click the application icon. The browser will launch in a Terminal window and open at http://localhost:8000.

## Option 2: Shell Script Launcher (Alternative Method)

If you prefer a simpler approach, you can use the shell script directly:

1. Make sure the `First1KGreek_Launcher.sh` script is executable:
   ```
   chmod +x First1KGreek_Launcher.sh
   ```

2. Create a symbolic link on your desktop:
   ```
   ln -s /full/path/to/First1KGreek_Launcher.sh ~/Desktop/First1KGreek
   ```
   Replace `/full/path/to/` with the actual path to your project directory.

3. To launch, double-click the symbolic link on your desktop.

## Troubleshooting

- If the application doesn't launch, verify that Python 3 is installed on your system.
- Make sure the `browse_texts_fixed.py` file is in the same directory as the launcher script.
- If you get permission errors, ensure that both scripts are executable.

## Notes

- The browser will open at http://localhost:8000
- To stop the server, simply close the Terminal window or press Ctrl+C in the Terminal window
- If you move your First1KGreek folder, you'll need to recreate the desktop shortcut 