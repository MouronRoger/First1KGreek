#!/usr/bin/env python3
"""
Update author_centuries.json to include author names alongside century data.
"""

import json
import os
import re

def main():
    """Main function to update author_centuries.json with author names."""
    print("Updating author_centuries.json to include author names...")
    
    # Load current century data
    try:
        with open('author_centuries.json', 'r', encoding='utf-8') as f:
            centuries = json.load(f)
        print(f"Loaded {len(centuries)} author entries from author_centuries.json")
    except Exception as e:
        print(f"Error loading author_centuries.json: {e}")
        return
    
    # Create updated structure
    updated_data = {}
    
    # Process each author in the data directory
    data_dir = 'data'
    count = 0
    
    for author_id in os.listdir(data_dir):
        author_path = os.path.join(data_dir, author_id)
        
        if not os.path.isdir(author_path) or not (author_id.startswith('tlg') or author_id.startswith('heb')):
            continue
        
        # Get author name from __cts__.xml if possible
        author_name = author_id  # Default to ID if name not found
        cts_path = os.path.join(author_path, '__cts__.xml')
        
        if os.path.exists(cts_path):
            try:
                with open(cts_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                name_match = re.search(r'<ti:groupname[^>]*>(.*?)</ti:groupname>', content)
                if name_match:
                    author_name = name_match.group(1).strip()
            except Exception as e:
                print(f"Error reading {cts_path}: {e}")
        
        # If author_id exists in the century data, add it to the updated structure
        if author_id in centuries:
            updated_data[author_id] = {
                "name": author_name,
                "century": centuries[author_id]
            }
            count += 1
            print(f"Added {author_id} -> {author_name} ({centuries[author_id]})")
        else:
            # Add the author even without a century, marking as "Unknown"
            updated_data[author_id] = {
                "name": author_name,
                "century": "Unknown"
            }
            print(f"Added {author_id} -> {author_name} (Unknown century)")
    
    # Add any remaining authors from the original century data that weren't in the data dir
    for author_id, century in centuries.items():
        if author_id not in updated_data:
            updated_data[author_id] = {
                "name": author_id,  # Default to ID since we don't have the name
                "century": century
            }
            count += 1
            print(f"Added {author_id} (name unknown) with century {century}")
    
    # Save the updated structure to a new file
    try:
        # First backup the existing file
        if os.path.exists('author_centuries.json'):
            os.rename('author_centuries.json', 'author_centuries_backup.json')
            print("Created backup of original file as author_centuries_backup.json")
        
        # Save new data
        with open('author_centuries.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, sort_keys=True)
        
        print(f"Successfully updated author_centuries.json with {count} authors including names and centuries.")
        print("You can now restart the browse_texts_fixed.py server to use the updated data.")
    except Exception as e:
        print(f"Error saving updated data: {e}")

if __name__ == "__main__":
    main() 