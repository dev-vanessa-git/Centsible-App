import json
import os
from typing import Optional, List, Dict, Any
from models import User


class AuthManager:
    """Handles user authentication, registration, and data persistence.
    
    Provides:
    - User registration and login functionality
    - Secure storage of user data
    - User data loading and saving
    
    Args:
        data_file: Path to JSON file storing user data (default: 'data/users.json')
    """

    def __init__(self, data_file: str = 'data/users.json') -> None:
        """Initialize the AuthManager with data file path."""
        self.data_file = data_file
        self._ensure_data_file_exists()
    
    def _ensure_data_file_exists(self) -> None:
        """Ensure the data directory and file exist.
        
        Creates the directory and initializes an empty JSON file if they don't exist.
        """
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)
    
    def _load_users(self) -> List[Dict[str, Any]]:
        """Load all users from the data file.
        
        Returns:
            List of user dictionaries loaded from the JSON file
            
        Raises:
            json.JSONDecodeError: If the file contains invalid JSON
            IOError: If there are file reading issues
        """
        with open(self.data_file, 'r') as f:
            return json.load(f)
    
    def _save_users(self, users_data: List[Dict[str, Any]]) -> None:
        """Save users to the data file.
        
        Args:
            users_data: List of user dictionaries to save
            
        Raises:
            IOError: If there are file writing issues
        """
        with open(self.data_file, 'w') as f:
            json.dump(users_data, f, indent=2)
    
    def register(self, username: str, password: str) -> bool:
        """Register a new user with the system.
        
        Args:
            username: The username to register
            password: The password for the new account
            
        Returns:
            bool: True if registration succeeded, False if username exists
            
        Example:
            >>> auth = AuthManager()
            >>> auth.register("newuser", "securepassword")
            True
        """
        users = self._load_users()
        
        # Check for existing username
        if any(u['username'] == username for u in users):
            return False
        
        # Create and save new user
        new_user = User(username=username, password=password)
        users.append(new_user.to_dict())
        self._save_users(users)
        return True
    
    def login(self, username: str, password: str) -> Optional[User]:
        """Authenticate and retrieve a user.
        
        Args:
            username: The username to authenticate
            password: The password to verify
            
        Returns:
            Optional[User]: User object if authentication succeeds, None otherwise
            
        Example:
            >>> auth = AuthManager()
            >>> user = auth.login("existinguser", "correctpassword")
            >>> isinstance(user, User)
            True
        """
        users = self._load_users()
        user_data = next(
            (u for u in users if u['username'] == username and u['password'] == password),
            None
        )
        return User.from_dict(user_data) if user_data else None
    
    def save_user_data(self, user: User) -> None:
        """Persist updated user data to storage.
        
        Args:
            user: The User object with updated data to save
            
        Example:
            >>> user = User(username="test", password="pass")
            >>> user.add_income("Salary", 5000)
            >>> auth = AuthManager()
            >>> auth.save_user_data(user)
        """
        users = self._load_users()
        
        # Find and update the user
        for i, u in enumerate(users):
            if u['username'] == user.username:
                users[i] = user.to_dict()
                break
        
        self._save_users(users)