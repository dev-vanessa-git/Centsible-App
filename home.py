import customtkinter as ctk
from typing import Tuple, Optional, Dict, Any


class HomeView(ctk.CTkFrame):
    """The application's home view containing login and registration forms.
    
    Provides:
    - User login form with username/password fields
    - New user registration form
    - Form validation and error messaging
    - Toggle between login and registration views
    
    Args:
        master: The parent widget
        app: Reference to the main application instance
        **kwargs: Additional arguments for CTkFrame
    """

    def __init__(self, master: ctk.CTk, app: Any, **kwargs) -> None:
        """Initialize the home view with login and registration forms."""
        super().__init__(master, **kwargs)
        self.app = app
        
        # Configure grid layout to fill entire space
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create main container frame
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Create welcome message
        self._create_welcome_label()
        
        # Initialize forms
        self._create_login_frame()
        self._create_register_frame()
        
        # Show login form by default
        self.show_login()
        self.message_label: Optional[ctk.CTkLabel] = None

    def _create_welcome_label(self) -> None:
        """Create the welcome message label."""
        self.welcome_label = ctk.CTkLabel(
            self.container,
            text="Welcome to CentiSible",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.welcome_label.grid(row=0, column=0, columnspan=2, pady=(20, 30))

    def _create_login_frame(self) -> None:
        """Create and configure the login form frame."""
        self.login_frame = ctk.CTkFrame(self.container)
        
        # Form title
        ctk.CTkLabel(
            self.login_frame, 
            text="Login to Your Account",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=(10, 20))
        
        # Username field
        ctk.CTkLabel(self.login_frame, text="Username:").grid(
            row=1, column=0, padx=10, pady=5, sticky="e")
        self.login_username = ctk.CTkEntry(self.login_frame, width=200)
        self.login_username.grid(row=1, column=1, padx=10, pady=5)
        
        # Password field
        ctk.CTkLabel(self.login_frame, text="Password:").grid(
            row=2, column=0, padx=10, pady=5, sticky="e")
        self.login_password = ctk.CTkEntry(self.login_frame, width=200, show="•")
        self.login_password.grid(row=2, column=1, padx=10, pady=5)
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.login_frame,
            text="Login",
            command=self._handle_login
        )
        self.login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Registration link
        ctk.CTkLabel(
            self.login_frame,
            text="Don't have an account?",
        ).grid(row=4, column=0, columnspan=2)
        
        ctk.CTkButton(
            self.login_frame,
            text="Register here",
            command=self.show_register,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            text_color=("gray10", "#DCE4EE")
        ).grid(row=5, column=0, columnspan=2, pady=(0, 10))

    def _create_register_frame(self) -> None:
        """Create and configure the registration form frame."""
        self.register_frame = ctk.CTkFrame(self.container)
        
        # Form title
        ctk.CTkLabel(
            self.register_frame, 
            text="Create New Account",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=(10, 20))
        
        # Username field
        ctk.CTkLabel(self.register_frame, text="Username:").grid(
            row=1, column=0, padx=10, pady=5, sticky="e")
        self.register_username = ctk.CTkEntry(self.register_frame, width=200)
        self.register_username.grid(row=1, column=1, padx=10, pady=5)
        
        # Password field
        ctk.CTkLabel(self.register_frame, text="Password:").grid(
            row=2, column=0, padx=10, pady=5, sticky="e")
        self.register_password = ctk.CTkEntry(self.register_frame, width=200, show="•")
        self.register_password.grid(row=2, column=1, padx=10, pady=5)
        
        # Confirm password field
        ctk.CTkLabel(self.register_frame, text="Confirm Password:").grid(
            row=3, column=0, padx=10, pady=5, sticky="e")
        self.register_confirm_password = ctk.CTkEntry(self.register_frame, width=200, show="•")
        self.register_confirm_password.grid(row=3, column=1, padx=10, pady=5)
        
        # Register button
        self.register_button = ctk.CTkButton(
            self.register_frame,
            text="Register",
            command=self._handle_register
        )
        self.register_button.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Login link
        ctk.CTkLabel(
            self.register_frame,
            text="Already have an account?",
        ).grid(row=5, column=0, columnspan=2)
        
        ctk.CTkButton(
            self.register_frame,
            text="Login here",
            command=self.show_login,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            text_color=("gray10", "#DCE4EE")
        ).grid(row=6, column=0, columnspan=2, pady=(0, 10))

    def show_login(self) -> None:
        """Display the login form and hide the registration form."""
        self.register_frame.grid_forget()
        self.login_frame.grid(row=1, column=0, padx=20, pady=20)
        self.login_username.focus_set()

    def show_register(self) -> None:
        """Display the registration form and hide the login form."""
        self.login_frame.grid_forget()
        self.register_frame.grid(row=1, column=0, padx=20, pady=20)
        self.register_username.focus_set()

    def _handle_login(self) -> None:
        """Handle login form submission.
        
        Validates input and attempts to authenticate the user.
        Shows appropriate success/error messages.
        """
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            self._show_message("Please enter both username and password", is_error=True)
            return
        
        success = self.app.login_user(username, password)
        if success:
            self._show_message("Login successful!", is_error=False)
        else:
            self._show_message("Invalid username or password", is_error=True)

    def _handle_register(self) -> None:
        """Handle registration form submission.
        
        Validates input and attempts to register a new user.
        Shows appropriate success/error messages.
        """
        username = self.register_username.get().strip()
        password = self.register_password.get().strip()
        confirm_password = self.register_confirm_password.get().strip()
        
        if not username or not password:
            self._show_message("Please enter both username and password", is_error=True)
            return
        
        if password != confirm_password:
            self._show_message("Passwords do not match", is_error=True)
            return
        
        success = self.app.register_user(username, password)
        if success:
            self._show_message("Registration successful! You are now logged in.", is_error=False)
        else:
            self._show_message("Username already exists", is_error=True)

    def _show_message(self, message: str, is_error: bool = False) -> None:
        """Display a message to the user.
        
        Args:
            message: The text to display
            is_error: Whether to style as an error message (red) or success (green)
        """
        if self.message_label:
            self.message_label.destroy()
        
        fg_color = ("#FF5555", "#FF0000") if is_error else ("#55AA55", "#008000")
        self.message_label = ctk.CTkLabel(
            self.container,
            text=message,
            text_color=fg_color
        )
        self.message_label.grid(row=2, column=0, pady=(0, 20))

    def update_view(self) -> None:
        """Update the view when called (no-op in this view)."""
        pass