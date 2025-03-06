#!/usr/bin/env python3
"""
Fix CSS braces in browse_texts.py file to ensure all single braces are replaced with double braces
in CSS sections of HTML template strings.
"""

import re
import os
import shutil

def fix_css_braces(filename):
    """Fix CSS braces in HTML template strings."""
    print(f"Creating backup of {filename} to {filename}.bak")
    shutil.copy(filename, f"{filename}.bak")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all CSS style sections in HTML template strings
    pattern = r'<style>(.*?)</style>'
    css_sections = re.findall(pattern, content, re.DOTALL)
    
    # Process each CSS section
    for css_section in css_sections:
        # Create a fixed version with all single braces replaced with double braces
        fixed_section = css_section
        
        # Fix CSS class/id definitions - find { not followed by another {
        fixed_section = re.sub(r'([#\.][a-zA-Z0-9_-]+\s*){(?!{)', r'\1{{', fixed_section)
        
        # Fix CSS closing braces - find } not preceded by another }
        fixed_section = re.sub(r'(?<!})}(\s*\n)', r'}}\1', fixed_section)
        
        # Replace in the original content
        content = content.replace(css_section, fixed_section)
    
    print(f"Writing fixed content to {filename}")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Done!")

if __name__ == "__main__":
    fix_css_braces("browse_texts.py") 