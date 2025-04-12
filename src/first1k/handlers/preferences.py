"""API handler for user preferences in First1KGreek Browser.

This module provides API endpoints for managing user preferences.
"""

import os
import json
import logging
from pathlib import Path

from ..config import USER_PREFS_FILE

logger = logging.getLogger(__name__)


def get_user_preferences():
    """
    Load user preferences from file.
    
    Returns:
        dict: User preferences including favorites and archived items
    """
    try:
        if not os.path.exists(USER_PREFS_FILE):
            logger.warning(f"Preferences file not found at {USER_PREFS_FILE}, creating new")
            return {'favorites': [], 'archived': []}
            
        with open(USER_PREFS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading preferences: {str(e)}")
        return {'favorites': [], 'archived': []}


def update_user_preferences(prefs):
    """
    Save user preferences to file.
    
    Args:
        prefs (dict): User preferences to save
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        with open(USER_PREFS_FILE, 'w') as f:
            json.dump(prefs, f)
        return True
    except Exception as e:
        logger.error(f"Error saving preferences: {str(e)}")
        return False


def handle_update_work_preference(query_params, post_data):
    """
    Handle API request to update preference for a specific work.
    
    Args:
        query_params (dict): Query parameters from the request
        post_data (dict): POST data from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    try:
        # Parse JSON if post_data is a string
        if isinstance(post_data, str):
            data = json.loads(post_data)
        else:
            data = post_data
            
        work_id = data.get('work_id')
        preference_type = data.get('type')  # 'favorite', 'archive', or 'delete'
        action = data.get('action')  # 'add' or 'remove'
        
        if not work_id or not preference_type or not action:
            return 400, 'application/json', {
                "error": "Missing required parameters: work_id, type, and action"
            }
        
        # Load existing preferences
        user_prefs = get_user_preferences()
        
        # Update preferences based on type and action
        if preference_type == 'favorite':
            preference_list = user_prefs.get('favorites', [])
            if action == 'add' and work_id not in preference_list:
                preference_list.append(work_id)
            elif action == 'remove' and work_id in preference_list:
                preference_list.remove(work_id)
            user_prefs['favorites'] = preference_list
            
        elif preference_type == 'archive':
            preference_list = user_prefs.get('archived', [])
            if action == 'add' and work_id not in preference_list:
                preference_list.append(work_id)
            elif action == 'remove' and work_id in preference_list:
                preference_list.remove(work_id)
            user_prefs['archived'] = preference_list
            
        elif preference_type == 'delete':
            # For delete, add to archived list (same as archive)
            preference_list = user_prefs.get('archived', [])
            if work_id not in preference_list:
                preference_list.append(work_id)
            user_prefs['archived'] = preference_list
        
        # Save updated preferences
        update_user_preferences(user_prefs)
        
        return 200, 'application/json', {
            "status": "success",
            "message": f"Updated {preference_type} preference for {work_id}"
        }
        
    except json.JSONDecodeError:
        return 400, 'application/json', {"error": "Invalid JSON in request body"}
    except Exception as e:
        logger.error(f"Error updating work preference: {str(e)}")
        return 500, 'application/json', {"error": f"Error updating preference: {str(e)}"}


def handle_update_preference(query_params, post_data):
    """
    Handle API request to update multiple preferences at once.
    
    Args:
        query_params (dict): Query parameters from the request
        post_data (dict): POST data from the request
        
    Returns:
        tuple: (status_code, content_type, response_data)
    """
    try:
        # Parse JSON if post_data is a string
        if isinstance(post_data, str):
            new_prefs = json.loads(post_data)
        else:
            new_prefs = post_data
            
        if not isinstance(new_prefs, dict):
            return 400, 'application/json', {"error": "Request body must be a JSON object"}
        
        # Validate the preferences structure
        if 'favorites' in new_prefs and not isinstance(new_prefs['favorites'], list):
            return 400, 'application/json', {"error": "'favorites' must be an array"}
        
        if 'archived' in new_prefs and not isinstance(new_prefs['archived'], list):
            return 400, 'application/json', {"error": "'archived' must be an array"}
        
        # Load existing preferences
        user_prefs = get_user_preferences()
        
        # Update with new preferences
        if 'favorites' in new_prefs:
            user_prefs['favorites'] = new_prefs['favorites']
        
        if 'archived' in new_prefs:
            user_prefs['archived'] = new_prefs['archived']
        
        # Save updated preferences
        update_user_preferences(user_prefs)
        
        return 200, 'application/json', {
            "status": "success",
            "message": "Preferences updated successfully"
        }
        
    except json.JSONDecodeError:
        return 400, 'application/json', {"error": "Invalid JSON in request body"}
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        return 500, 'application/json', {"error": f"Error updating preferences: {str(e)}"} 