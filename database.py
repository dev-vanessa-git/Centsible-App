import json
import os
from typing import Dict, Any

DATA_FOLDER = "user_data"  # Directory where user data files are stored

def load_user_data(username: str) -> Dict[str, Any]:
    """
    Load a user's financial data from their JSON file.

    Args:
        username: The username identifier used to locate the data file.
                 The corresponding file should be in the DATA_FOLDER directory
                 with a .json extension (e.g., 'john_doe.json').

    Returns:
        Dictionary containing the user's financial data if found, 
        or an empty dictionary if either:
        - The user file doesn't exist
        - The file is empty
        - The file contains invalid JSON

    Example:
        >>> load_user_data("john_doe")
        {'income': {'salary': 500000}, 'expenses': {'rent': 150000}}
    """
    user_file = os.path.join(DATA_FOLDER, f"{username}.json")
    
    if not os.path.exists(user_file):
        return {}

    try:
        with open(user_file, "r", encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}