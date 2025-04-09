# First1KGreek Test Reorganization

## Directory Structure

The tests have been reorganized into a more structured directory layout:

```
tests/
├── __init__.py
├── conftest.py (moved to core/)
├── core/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_base.py
│   ├── test_http_handler.py
│   ├── test_page_generation.py
│   ├── test_pytest_sample.py
│   ├── test_server.py
│   └── test_utils.py
├── integration/
│   ├── __init__.py
│   └── test_server.py
├── performance/
│   ├── __init__.py
│   ├── test_http_server.py
│   └── test_xml_processing.py
├── runners/
│   ├── __init__.py
│   ├── run_pytest.py
│   └── run_tests.py
└── unit/
    ├── __init__.py
    └── test_xml.py
```

## What Was Done

1. Created a proper directory structure:
   - `core/` - For core application test files
   - `unit/`, `integration/`, `performance/` - Maintained existing categorization
   - `runners/` - For test runner scripts

2. Cleaned up duplicate files:
   - Removed files with " 2" suffixes
   - Backed up copies to `tests/backup/duplicates/`

3. Created a proper pytest.ini configuration file:
   - Added test discovery patterns
   - Configured test markers
   - Set up basic pytest options

4. Updated import paths in test files:
   - Updated relative imports to work with the new structure
   - Adjusted system path insertions in runner scripts

5. Created a symlink to maintain backward compatibility:
   - `run_pytest.py` in the project root links to `tests/runners/run_pytest.py`

6. Made runner scripts executable:
   - Both `run_pytest.py` and `run_tests.py` have executable permissions

## Known Issues

The tests are currently failing because of changes to the project's architecture:

1. The tests are designed to work with the monolithic `browse_texts_fixed.py` file, but that file has been refactored to be a wrapper around the modular implementation in `src/first1k/`.

2. The specific error is that the tests are trying to mock `browse_texts_fixed.AUTHORS_DATA`, but that variable no longer exists in the wrapper file.

## Next Steps

1. Update all tests to work with the new modular structure:
   - Modify the imports to target the appropriate modules in `src/first1k/`
   - Update mocks to patch the correct paths
   - Adjust test expectations to match the new implementation

2. Consider updating the test structure further:
   - Mirror the module structure in `src/first1k/` with a corresponding test structure
   - Create specific test files for each module in the new structure

3. Create integration tests that verify the wrapper functionality:
   - Test that `browse_texts_fixed.py` correctly forwards to the modular implementation
   - Ensure that error handling in the wrapper works correctly

4. Update the test documentation in `README_tests.md` with comprehensive information about the test approach for the modular architecture.

## How to Use

Use the runner scripts to execute tests:

```bash
# Using pytest (recommended)
python tests/runners/run_pytest.py --unit
python tests/runners/run_pytest.py --integration
python tests/runners/run_pytest.py --performance
python tests/runners/run_pytest.py --core
python tests/runners/run_pytest.py --all --coverage

# Using unittest
python tests/runners/run_tests.py --unit
python tests/runners/run_tests.py --integration
python tests/runners/run_tests.py --performance
python tests/runners/run_tests.py --core
python tests/runners/run_tests.py --all
```

Alternatively, use pytest or unittest directly:

```bash
# Using pytest directly
pytest tests/core/
pytest tests/unit/
pytest -m unit
pytest -m integration
pytest -m performance

# Using unittest directly
python -m unittest discover -s tests/core
python -m unittest discover -s tests/unit
```

See `README_tests.md` for more detailed information on the testing approach. 