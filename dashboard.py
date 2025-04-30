import customtkinter as ctk
from typing import Dict
from .home import HomeView
from .transactions import TransactionsView
from .expenses import ExpensesView
from .insights import InsightsView


class Dashboard(ctk.CTkFrame):
    """Main application dashboard frame containing sidebar navigation and content views.
    
    The dashboard manages:
    - Sidebar navigation buttons
    - Multiple content views (Home, Transactions, Expenses, Insights)
    - Authentication state management
    - View switching logic

    Args:
        master: The parent widget
        **kwargs: Additional configuration options for CTkFrame
    """

    def __init__(self, master: ctk.CTk, **kwargs) -> None:
        """Initialize the dashboard with sidebar and content frame."""
        super().__init__(master, **kwargs)
        self.master = master
        
        # Configure grid layout - sidebar (column 0) and content (column 1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)  # Content area gets all extra space
        
        self._create_sidebar()
        self._create_content_frame()
        self._initialize_views()
        self.show_unauthenticated_views()  # Start in unauthenticated state

    def _create_sidebar(self) -> None:
        """Create and configure the sidebar frame with navigation buttons."""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)  # Space between buttons and logout
        
        # App logo/title
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="CentiSible",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation buttons (initially disabled)
        self.transactions_button = ctk.CTkButton(
            self.sidebar, 
            text="Transactions",
            command=self.show_transactions
        )
        self.transactions_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.expenses_button = ctk.CTkButton(
            self.sidebar, 
            text="View Expenses",
            command=self.show_expenses
        )
        self.expenses_button.grid(row=3, column=0, padx=20, pady=10)
        
        self.insights_button = ctk.CTkButton(
            self.sidebar, 
            text="AI Insights",
            command=self.show_insights
        )
        self.insights_button.grid(row=4, column=0, padx=20, pady=10)
        
        # Logout button (hidden by default)
        self.logout_button = ctk.CTkButton(
            self.sidebar, 
            text="Logout",
            command=self.master.logout_user,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE")
        )
        self.logout_button.grid(row=6, column=0, padx=20, pady=10, sticky="s")
        self.logout_button.grid_remove()

    def _create_content_frame(self) -> None:
        """Create the main content area frame where views will be displayed."""
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _initialize_views(self) -> None:
        """Create and store all application views in a dictionary."""
        self.views: Dict[str, ctk.CTkFrame] = {
            'home': HomeView(self.content_frame, self.master),
            'transactions': TransactionsView(self.content_frame, self.master),
            'expenses': ExpensesView(self.content_frame, self.master),
            'insights': InsightsView(self.content_frame, self.master)
        }
        
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def show_view(self, view_name: str) -> None:
        """Raise the specified view to the top and refresh its content.
        
        Args:
            view_name: The name of the view to show (must exist in self.views)
        """
        if view_name in self.views:
            self.views[view_name].tkraise()
            self.views[view_name].update_view()  # Refresh view data

    def show_home(self) -> None:
        """Show the home view."""
        self.show_view('home')

    def show_transactions(self) -> None:
        """Show the transactions view."""
        self.show_view('transactions')

    def show_expenses(self) -> None:
        """Show the expenses view."""
        self.show_view('expenses')

    def show_insights(self) -> None:
        """Show the insights view."""
        self.show_view('insights')

    def show_authenticated_views(self) -> None:
        """Configure UI for authenticated state (enable all features)."""
        # Remove home button if it exists
        if hasattr(self, 'home_button'):
            self.home_button.grid_remove()
            del self.home_button

        # Enable all navigation buttons
        self.transactions_button.configure(state="normal")
        self.expenses_button.configure(state="normal")
        self.insights_button.configure(state="normal")
        
        # Show logout button and default to transactions view
        self.logout_button.grid()
        self.show_transactions()

    def show_unauthenticated_views(self) -> None:
        """Configure UI for unauthenticated state (restricted features)."""
        # Create home button only once
        if not hasattr(self, 'home_button'):
            self.home_button = ctk.CTkButton(
                self.sidebar, 
                text="Home",
                command=self.show_home
            )
            self.home_button.grid(row=1, column=0, padx=20, pady=10)

        self.home_button.grid()    
        # Disable navigation buttons
        self.transactions_button.configure(state="disabled")
        self.expenses_button.configure(state="disabled")
        self.insights_button.configure(state="disabled")
        
        # Hide logout button and show home view
        self.logout_button.grid_remove()
        self.show_home()