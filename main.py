import customtkinter as ctk
from typing import Optional
from auth import AuthManager
from views.dashboard import Dashboard
from views.home import HomeView
from models import User


class CentiSibleApp(ctk.CTk):
    """Main application class for CentiSible personal finance application.
    
    Handles:
    - Application window configuration
    - User authentication flow
    - View management
    - Thread-safe application shutdown
    
    Attributes:
        auth_manager: Handles user authentication and data persistence
        current_user: Currently logged in user (None if not authenticated)
        dashboard: Main application dashboard view
        home_view: Login/registration view
        running: Flag for controlling background threads
    """

    def __init__(self) -> None:
        """Initialize the application window and components."""
        super().__init__()
        self.running = True  # Flag for thread control
        
        # Window configuration
        self._configure_window()
        
        # Authentication setup
        self.auth_manager = AuthManager()
        self.current_user: Optional[User] = None
        
        # Initialize views
        self._initialize_views()
        
        # Set up safe shutdown
        self.protocol("WM_DELETE_WINDOW", self._safe_shutdown)
        
        # Check initial authentication state
        self.check_authentication()

    def _configure_window(self) -> None:
        """Configure the main application window settings."""
        self.title("CentiSible - Smart Budgeting App")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _initialize_views(self) -> None:
        """Initialize and configure all application views."""
        # Create dashboard (hidden initially)
        self.dashboard = Dashboard(self)
        self.dashboard.grid(row=0, column=0, sticky="nsew")
        self.dashboard.sidebar.grid_remove()
        
        # Create home view (login/registration)
        self.home_view = HomeView(self, self)
        self.home_view.grid(row=0, column=0, sticky="nsew")

    def _safe_shutdown(self) -> None:
        """Handle application shutdown safely, stopping all background threads."""
        self.running = False  # Signal threads to stop
        self.destroy()  # Close the window

    def check_authentication(self) -> None:
        """Check authentication state and update UI accordingly.
        
        Shows/hides appropriate views based on whether a user is logged in.
        """
        if self.current_user:
            self.home_view.grid_remove()
            self.dashboard.sidebar.grid()
            self.dashboard.show_authenticated_views()
        else:
            self.home_view.grid()
            self.dashboard.sidebar.grid_remove()
            self.dashboard.show_unauthenticated_views()

    def login_user(self, username: str, password: str) -> bool:
        """Authenticate a user with provided credentials.
        
        Args:
            username: User's login username
            password: User's login password
            
        Returns:
            bool: True if login succeeded, False otherwise
        """
        user = self.auth_manager.login(username, password)
        if user:
            self.current_user = user
            self.check_authentication()
            self.dashboard.show_transactions()  # Show transactions by default
            return True
        return False

    def register_user(self, username: str, password: str) -> bool:
        """Register a new user account.
        
        Args:
            username: New username
            password: New password
            
        Returns:
            bool: True if registration succeeded, False otherwise
        """
        success = self.auth_manager.register(username, password)
        if success:
            # Auto-login after successful registration
            return self.login_user(username, password)
        return False
        
    def logout_user(self) -> None:
        """Log out the current user and reset the UI."""
        self.current_user = None
        self.check_authentication()
        self.dashboard.views['home'].grid()
        self.dashboard.show_home()

    

if __name__ == "__main__":
    app = CentiSibleApp()
    app.mainloop()