# First1KGreek Formatting Patterns

This document provides a quick reference for common formatting patterns used in the First1KGreek project. Following these patterns will help maintain code consistency and pass linting checks.

## Imports

Imports should follow this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

Each group should be separated by a blank line.

```python
# Good import pattern
import os
import sys
import json

import requests
from lxml import etree

from first1k.xml_utils import parse_xml
from first1k.utils.logging import setup_logger
```

## Docstrings

All modules, classes, methods, and functions should have docstrings:

```python
"""
Module-level docstring describing the purpose of the module.

Additional details can be included here.
"""

class MyClass:
    """Class docstring describing the class purpose and behavior."""
    
    def my_method(self, arg1, arg2=None):
        """
        Method docstring describing what this method does.
        
        Args:
            arg1: Description of arg1
            arg2: Description of arg2, defaults to None
            
        Returns:
            Description of the return value
        """
        # Method implementation
```

## Function/Method Definitions

For methods with multiple parameters, format them like this:

```python
def function_with_many_parameters(
    param1,
    param2,
    param3,
    long_parameter_name="default_value",
    another_param=None
):
    """
    Function docstring here.
    
    Args:
        param1: Description
        param2: Description
        param3: Description
        long_parameter_name: Description, defaults to "default_value"
        another_param: Description, defaults to None
    """
    # Implementation
```

## Constants

Define constants at the module level, using UPPER_CASE:

```python
DEFAULT_PORT = 8000
MAX_RETRIES = 3
XML_NAMESPACES = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "cts": "http://chs.harvard.edu/xmlns/cts",
}
```

## Error Handling

Use specific exceptions and include context:

```python
try:
    # Code that might raise an exception
    with open(file_path, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    logger.error(f"Config file not found: {file_path}")
    # Handle the error appropriately
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in config file {file_path}: {str(e)}")
    # Handle the error appropriately
```

## Logging

Use the logger configured for the application:

```python
import logging

# Get logger at the module level
logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Entering some_function")
    try:
        # Some code
        logger.info("Operation completed successfully")
    except Exception as e:
        logger.error(f"Error in some_function: {str(e)}")
        raise
```

## Line Length

Maximum line length is 120 characters. For long strings, use parentheses:

```python
long_string = (
    "This is a very long string that would exceed the 120 character limit if "
    "it were not split across multiple lines using parentheses."
)
```

## Conditionals

For complex conditions, use parentheses and line breaks for clarity:

```python
if (
    condition1 and 
    condition2 and
    (condition3 or condition4)
):
    # Action if complex condition is met
```

## List/Dict Comprehensions

Keep them simple. For complex comprehensions, use a regular for loop instead:

```python
# Good - simple comprehension
squared = [x**2 for x in numbers]

# Good - simple comprehension with condition
even_squared = [x**2 for x in numbers if x % 2 == 0]

# Bad - too complex, should be a normal for loop
result = [func(x, y) for x in range(10) for y in range(10) if condition(x, y)]
```

## XML Handling

When working with XML, use ElementTree with proper namespace handling:

```python
import xml.etree.ElementTree as ET

# Define namespaces
NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "cts": "http://chs.harvard.edu/xmlns/cts",
}

# Use namespaces in XPath expressions
root = ET.parse(xml_file).getroot()
titles = root.findall(".//tei:title", NS)
```

## Avoid Global Variables

Prefer configuration classes over global variables:

```python
class Config:
    """Configuration for the application."""
    
    PORT = 8000
    DEBUG = False
    DATA_DIR = "data"
    
    @classmethod
    def from_file(cls, file_path):
        """Load configuration from a file."""
        # Implementation
        return cls()
```

## Type Hints

Use type hints for function signatures where appropriate:

```python
from typing import List, Dict, Optional, Union

def process_data(
    data: List[Dict[str, str]],
    options: Optional[Dict[str, Union[str, int]]] = None
) -> List[str]:
    """
    Process the input data.
    
    Args:
        data: List of data dictionaries to process
        options: Optional processing parameters
        
    Returns:
        List of processed string results
    """
    # Implementation
``` 