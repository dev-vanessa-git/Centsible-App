import customtkinter as ctk
from typing import Dict, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from utils.charts import create_bar_chart


class ExpensesView(ctk.CTkFrame):
    """A view for visualizing and analyzing expense data with interactive charts and tables.
    
    Provides:
    - Summary of income and net balance
    - Interactive bar charts comparing expenses to budgets
    - Detailed table view of expenses by category
    - Visual indicators for budget over/under spending
    
    Args:
        master: Parent widget
        app: Reference to main application instance
        **kwargs: Additional arguments for CTkFrame
    """

    def __init__(self, master: ctk.CTk, app, **kwargs) -> None:
        """Initialize the Expenses View with all UI components."""
        super().__init__(master, **kwargs)
        self.app = app
        
        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)  # Main content area expands
        self.grid_columnconfigure(0, weight=1)
        
        self._create_title()
        self._create_content_frame()
        self._create_income_display()
        self._create_chart_and_table_frames()
        
        # Initialize chart and table references
        self.bar_chart_frame: Optional[ctk.CTkFrame] = None
        self.expenses_table: Optional[ctk.CTkFrame] = None
        
        self.update_view()

    def _create_title(self) -> None:
        """Create the view title label."""
        self.title_label = ctk.CTkLabel(
            self,
            text="Your Expenses Overview",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    def _create_content_frame(self) -> None:
        """Create the main content frame container."""
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_rowconfigure(0, weight=0)  # Income frame
        self.content_frame.grid_rowconfigure(1, weight=1)  # Charts/table
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)

    def _create_income_display(self) -> None:
        """Create the income and balance summary frame."""
        self.income_frame = ctk.CTkFrame(self.content_frame)
        self.income_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        self.income_label = ctk.CTkLabel(
            self.income_frame,
            text="Total Income: ₦0.00",
            font=ctk.CTkFont(size=16)
        )
        self.income_label.pack(side="left", padx=10, pady=5)
        
        self.net_balance_label = ctk.CTkLabel(
            self.income_frame,
            text="Net Balance: ₦0.00",
            font=ctk.CTkFont(size=16)
        )
        self.net_balance_label.pack(side="right", padx=10, pady=5)

    def _create_chart_and_table_frames(self) -> None:
        """Create frames for charts and table display."""
        # Charts frame (left side)
        self.charts_frame = ctk.CTkFrame(self.content_frame)
        self.charts_frame.grid(row=1, column=0, sticky="nsew", padx=(10,5), pady=10)
        self.charts_frame.grid_rowconfigure(0, weight=1)
        self.charts_frame.grid_columnconfigure(0, weight=1)
        
        # Table frame (right side)
        self.table_frame = ctk.CTkFrame(self.content_frame)
        self.table_frame.grid(row=1, column=1, sticky="nsew", padx=(5,10), pady=10)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

    def update_view(self) -> None:
        """Refresh the view with current user data.
        
        Updates:
        - Income and balance displays
        - Expense charts
        - Expense table
        """
        if not self.app.current_user:
            return
        
        # Update financial summary
        total_income = self.app.current_user.get_total_income()
        total_expenses = self.app.current_user.get_total_expenses()
        net_balance = total_income - total_expenses
        
        self.income_label.configure(text=f"Total Income: ₦{total_income:,.2f}")
        self.net_balance_label.configure(
            text=f"Net Balance: ₦{net_balance:,.2f}",
            text_color=("green" if net_balance >= 0 else "red")
        )
        
        # Get expense data
        expenses_by_category = self.app.current_user.get_expenses_by_category()
        expense_budgets = self.app.current_user.expense_budgets
        
        if expenses_by_category:
            self._update_charts(expenses_by_category, expense_budgets)
            self._update_expenses_table(expenses_by_category, expense_budgets)
        else:
            self._show_no_data_message()

    def _update_charts(self, expenses_by_category: Dict[str, float], 
                      expense_budgets: Dict[str, float]) -> None:
        """Update the chart visualization with current expense data.
        
        Args:
            expenses_by_category: Mapping of category names to amounts spent
            expense_budgets: Mapping of category names to budget amounts
        """
        # Clear previous chart
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        # Create tabbed interface for charts
        self.chart_tabs = ctk.CTkTabview(self.charts_frame)
        self.chart_tabs.grid(row=0, column=0, sticky="nsew")
        self.chart_tabs.add("Bar Chart")
        
        # Generate and display bar chart
        bar_fig: Figure = create_bar_chart(expenses_by_category, expense_budgets)
        bar_canvas = FigureCanvasTkAgg(bar_fig, master=self.chart_tabs.tab("Bar Chart"))
        bar_canvas.draw()
        bar_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _update_expenses_table(self, expenses_by_category: Dict[str, float],
                             expense_budgets: Dict[str, float]) -> None:
        """Update the expenses table with current data.
        
        Args:
            expenses_by_category: Mapping of category names to amounts spent
            expense_budgets: Mapping of category names to budget amounts
        """
        # Clear previous table
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # Create scrollable table container
        scrollable_frame = ctk.CTkScrollableFrame(
            self.table_frame,
            label_text="Expenses by Category"
        )
        scrollable_frame.grid(row=0, column=0, sticky="nsew")
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Table headers
        headers = ["Category", "Spent", "Budget", "Remaining", "% of Budget"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                scrollable_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=col, padx=5, pady=2, sticky="ew")
        
        # Populate table rows
        for row, (category, spent) in enumerate(expenses_by_category.items(), start=1):
            budget = expense_budgets.get(category, 0)
            remaining = budget - spent if budget > 0 else 0
            percent_used = (spent / budget * 100) if budget > 0 else 0
            
            # Category name
            ctk.CTkLabel(
                scrollable_frame,
                text=category
            ).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            # Amount spent (always red)
            ctk.CTkLabel(
                scrollable_frame,
                text=f"₦{spent:,.2f}",
                text_color="red"
            ).grid(row=row, column=1, padx=5, pady=2, sticky="e")
            
            # Budget amount
            budget_text = f"₦{budget:,.2f}" if budget > 0 else "Not set"
            ctk.CTkLabel(
                scrollable_frame,
                text=budget_text
            ).grid(row=row, column=2, padx=5, pady=2, sticky="e")
            
            # Remaining budget (green/red)
            remaining_text = f"₦{remaining:,.2f}" if budget > 0 else "N/A"
            remaining_color = "green" if remaining >= 0 or budget == 0 else "red"
            ctk.CTkLabel(
                scrollable_frame,
                text=remaining_text,
                text_color=remaining_color
            ).grid(row=row, column=3, padx=5, pady=2, sticky="e")
            
            # Budget percentage (green/red/gray)
            percent_text = f"{percent_used:.1f}%" if budget > 0 else "N/A"
            percent_color = ("green" if percent_used <= 100 else "red") if budget > 0 else "gray"
            ctk.CTkLabel(
                scrollable_frame,
                text=percent_text,
                text_color=percent_color
            ).grid(row=row, column=4, padx=5, pady=2, sticky="e")

    def _show_no_data_message(self) -> None:
        """Display a message when no expense data is available."""
        for frame in [self.charts_frame, self.table_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
        
        ctk.CTkLabel(
            self.charts_frame,
            text="No expense data available. Start by adding transactions.",
            font=ctk.CTkFont(size=14),
            wraplength=300
        ).pack(pady=50)