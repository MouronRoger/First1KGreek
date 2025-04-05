# Creating a First1KGreek Desktop Shortcut with Automator

For users who prefer not to use AppleScript or terminal commands, you can create a simple desktop application using Automator, which is included with macOS.

## Instructions:

1. **Open Automator**:
   - Find Automator in your Applications folder
   - Open it (it has a robot icon)

2. **Create a new Application**:
   - When Automator opens, select "Application" when prompted for the type of document
   - Click "Choose"

3. **Add a Run Shell Script action**:
   - In the search field (top left), type "Run Shell Script"
   - Drag the "Run Shell Script" action to the workflow area on the right

4. **Configure the Shell Script**:
   - Make sure "Shell: /bin/bash" is selected
   - Make sure "Pass input: to stdin" is selected
   - Enter the following script, replacing `/full/path/to/your/project` with the actual path to your First1KGreek folder:

```bash
cd /full/path/to/your/project
python3 browse_texts_fixed.py
```

5. **Save the Application**:
   - Go to File > Save
   - Name it "First1KGreek Browser"
   - Choose your Desktop as the save location
   - Click "Save"

6. **Customize the Icon (Optional)**:
   - Right-click on the new application on your desktop
   - Select "Get Info"
   - If you have an icon file, drag it onto the small icon in the top-left of the Get Info window

7. **Use Your New Shortcut**:
   - Simply double-click the application on your desktop to launch the First1KGreek Browser
   - A Terminal window will open running the server
   - Your default web browser should automatically open to http://localhost:8000

## Notes:

- This method creates a more native-looking macOS application than the script methods
- To quit the application, you'll need to close the Terminal window that opens
- The current path in the script must be the exact location of your First1KGreek project 