# Updated File Categorization for First1KGreek Project

# No XML or data files are to be touched or deleted without explicit permission
## 1. Known Core (KC)
* **Core Application Files:**
* run_server.py - Main execution script
* src/first1k/ directory - Modular implementation
* src/first1k/__init__.py, __main__.py, config.py - Core package structure
* requirements.txt, setup.py - Package management
* **Essential Data:**
* authors_data.json - Author metadata
* user_preferences.json - User settings
* data/ directory - Core XML files (source of truth)
* catalog.json - Comprehensive catalog of works
* new_edition_metadata.csv - Detailed bibliographic information
* **Documentation:**
* README.md - Main documentation
* USAGE.md - Usage instructions
* README_CLEANUP.md - Cleanup documentation
* README_tests.md - Test documentation

⠀2. Extracted (EXT)
* src/first1k/utils/ - Utility functions
* src/first1k/server/ - Server implementation
* src/first1k/handlers/ - Request handlers
* static/css/, static/js/ - Extracted frontend assets

⠀3. Transitional (TRN)
* browse_texts_fixed.py - Wrapper for modular implementation
* src/first1k/xml_utils/ - XML processing (in transition)
* src/first1k/search/ - Search functionality (in transition)
* src/first1k/import_export/ - Import/export (in development)
* src/first1k/editor/ - Editor (in development)
* First1KGreek Comprehensive Repository Analysis.md - Refactoring guide
* 25_03_09_First1kGreek_project_overview.md - Project overview

⠀4. Deprecated (DEP)
* browse_texts_fixed.py.bak, browse_texts_fixed_bak2.py - Old versions
* *.bak files - Various backups
* simple_test_server.py - Superseded test server
* authors_data.json.bak, authors_data.json.original - Data backups
* **greek-texts-index/** directory - Next.js implementation (redundant with main data)
* greek-texts-index/public/data/ - Duplicate of core data

⠀5. Uncertain (UNC)
* First1KGreek_Launcher.sh, MakeDesktopShortcut.sh - Launcher scripts
* test_server_launcher.sh, simple_launcher.sh - Secondary launchers
* authors_data_detail.json - Alternative author data format
* data_2/, volume_xml/, raw_files/, split/ - Additional data directories
* COMPARISON.md, first1kgreek_memory.md - Documentation with unclear purpose

⠀The Next.js implementation (greek-texts-index/ directory) has been moved from Uncertain to Deprecated as we've confirmed it contains no unique data and can be safely removed to simplify the codebase for your Python + HTMX approach.

### No XML or data files are to be touched or deleted without explicit permission