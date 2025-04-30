import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import uuid
import json
from models import Transaction


class TransactionsView(ctk.CTkFrame):
    """View for managing financial transactions including income and expenses.
    
    Provides:
    - Transaction logging interface
    - Category and budget management
    - Income tracking
    - Recent transactions display
    
    Args:
        master: Parent widget
        app: Reference to main application instance
        **kwargs: Additional arguments for CTkFrame
    """

    def __init__(self, master: ctk.CTk, app: Any, **kwargs) -> None:
        """Initialize the transactions view with UI components."""
        super().__init__(master, **kwargs)
        self.app = app
        self.categories: Dict[str, float] = {}
        self.category_fields: List[Tuple[ctk.CTkEntry, ctk.CTkEntry]] = []
        self.message_label: Optional[ctk.CTkLabel] = None
        self.load_categories()

        # Configure grid layout
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create UI components
        self._create_title()
        self._create_income_display()
        self._create_categories_display()
        self._create_transaction_form()
        self._create_transactions_table()

        # Initial view update
        self.update_view()

    def _create_title(self) -> None:
        """Create the view title label."""
        self.title_label = ctk.CTkLabel(
            self,
            text="Track Your Transactions",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

    def _create_income_display(self) -> None:
        """Create the income display frame."""
        self.income_frame = ctk.CTkFrame(self)
        self.income_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        self.income_label = ctk.CTkLabel(
            self.income_frame,
            text="Total Income: ₦0.00",
            font=ctk.CTkFont(size=14)
        )
        self.income_label.pack(side="left", padx=10, pady=5)
        
        self.add_income_button = ctk.CTkButton(
            self.income_frame,
            text="Add Income",
            command=self._show_add_income_dialog,
            width=100
        )
        self.add_income_button.pack(side="right", padx=10, pady=5)

    def _create_categories_display(self) -> None:
        """Create the categories display frame."""
        self.categories_frame = ctk.CTkFrame(self)
        self.categories_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        
        self.categories_label = ctk.CTkLabel(
            self.categories_frame,
            text="Category: None     Budget: ₦0.00",
            font=ctk.CTkFont(size=14)
        )
        self.categories_label.pack(side="left", padx=10, pady=5)
        
        self.add_categories_button = ctk.CTkButton(
            self.categories_frame,
            text="Add Categories",
            command=self._show_add_categories_dialog,
            width=120,
            state="normal"
        )
        self.add_categories_button.pack(side="right", padx=10, pady=5)

    def _create_transaction_form(self) -> None:
        """Create the transaction input form."""
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        # Category dropdown
        ctk.CTkLabel(self.form_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        self.category_var = ctk.StringVar(value="Select Category")
        self.category_dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            variable=self.category_var,
            values=list(self.categories.keys()),
            command=self._update_category_display
        )
        self.category_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Amount field
        ctk.CTkLabel(self.form_frame, text="Amount:").grid(row=0, column=2, padx=5, pady=5)
        self.amount_entry = ctk.CTkEntry(self.form_frame, width=120)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Date field
        ctk.CTkLabel(self.form_frame, text="Date:").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = ctk.CTkEntry(self.form_frame, width=120)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Submit button
        self.submit_button = ctk.CTkButton(
            self.form_frame,
            text="Add Transaction",
            command=self._add_transaction
        )
        self.submit_button.grid(row=1, column=0, columnspan=6, pady=10)

    def _create_transactions_table(self) -> None:
        """Create the transactions display table."""
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        
        self._init_transactions_table()

    def _init_transactions_table(self) -> None:
        """Initialize the transactions table with headers."""
        self.transactions_table = ctk.CTkScrollableFrame(
            self.table_frame,
            label_text="Recent Transactions"
        )
        self.transactions_table.grid(row=0, column=0, sticky="nsew")
        
        # Header row
        headers = ["Date", "Category", "Amount", "Budget"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.transactions_table,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                anchor="center"
            )
            label.grid(row=0, column=col, padx=10, pady=5, sticky="ew")

    def _update_category_display(self, choice: str) -> None:
        """Update category display when a category is selected.
        
        Args:
            choice: Selected category name
        """
        if choice in self.categories:
            budget = self.categories[choice]
            self.categories_label.configure(
                text=f"Category: {choice} | Budget: ₦{budget:,.2f}"
            )

    def _show_add_categories_dialog(self) -> None:
        """Show dialog for adding/editing categories and budgets."""
        self.category_dialog = ctk.CTkToplevel(self)
        self.category_dialog.title("Add Categories")
        self.category_dialog.geometry("400x400")
        self.category_dialog.resizable(False, False)
        self.category_dialog.grid_rowconfigure(1, weight=1)
        self.category_dialog.grid_columnconfigure(0, weight=1)
        
        # Title
        ctk.CTkLabel(
            self.category_dialog,
            text="Add Categories & Budgets",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, pady=10)
        
        # Fields container
        self.fields_container = ctk.CTkFrame(self.category_dialog)
        self.fields_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Headers
        ctk.CTkLabel(self.fields_container, text="Category").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(self.fields_container, text="Budget").grid(row=0, column=1, padx=5, pady=5)
        
        # Clear existing fields
        self.category_fields = []
        
        # Populate with saved categories
        for i, (category, budget) in enumerate(self.categories.items(), start=1):
            self._add_category_field_pair(
                category, 
                str(budget), 
                show_plus=(i == len(self.categories)))
        
        # Add empty row if no categories exist
        if not self.categories:
            self._add_category_field_pair(show_plus=True)
        
        # Save button
        ctk.CTkButton(
            self.category_dialog,
            text="Save",
            command=self._save_categories
        ).grid(row=2, column=0, pady=10)

    def _add_category_field_pair(
        self, 
        category: str = "", 
        budget: str = "", 
        show_plus: bool = False
    ) -> None:
        """Add a new pair of category and budget fields.
        
        Args:
            category: Existing category name (optional)
            budget: Existing budget amount (optional)
            show_plus: Whether to show the add button
        """
        row = len(self.category_fields) + 1
        
        # Category field
        category_entry = ctk.CTkEntry(self.fields_container)
        category_entry.grid(row=row, column=0, padx=5, pady=5)
        if category:
            category_entry.insert(0, category)
        
        # Budget field with optional plus button
        budget_frame = ctk.CTkFrame(self.fields_container, fg_color="transparent")
        budget_frame.grid(row=row, column=1, padx=5, pady=5)
        
        budget_entry = ctk.CTkEntry(budget_frame)
        budget_entry.pack(side="left", padx=(0, 5))
        if budget:
            budget_entry.insert(0, budget)
        
        if show_plus:
            plus_button = ctk.CTkButton(
                budget_frame,
                text="+",
                width=30,
                command=lambda: [
                    self._add_category_field_pair(),
                    plus_button.pack_forget()
                ]
            )
            plus_button.pack(side="left")
        
        self.category_fields.append((category_entry, budget_entry))

    def _save_categories(self) -> None:
        """Save categories and budgets to file and update UI."""
        new_categories = {}
        for category_entry, budget_entry in self.category_fields:
            category = category_entry.get().strip()
            budget_str = budget_entry.get().strip()
            
            if category and budget_str:
                try:
                    budget = float(budget_str)
                    if budget >= 0:  # Only accept positive budgets
                        new_categories[category] = budget
                except ValueError:
                    pass  # Skip invalid budget entries
        
        # Update categories if valid entries exist
        if new_categories:
            self.categories = new_categories
            with open('data/categories.json', 'w') as f:
                json.dump(self.categories, f)
            
            # Update dropdown and display
            self.category_dropdown.configure(values=list(self.categories.keys()))
            if self.categories:
                self.category_var.set(next(iter(self.categories.keys())))
                self._update_category_display(next(iter(self.categories.keys())))
            
            self.category_dialog.destroy()
            self._show_message("Categories saved successfully!")
        else:
            messagebox.showerror("Error", "Please enter at least one valid category and budget")

    def load_categories(self) -> None:
        """Load categories from JSON file."""
        try:
            with open('data/categories.json', 'r') as f:
                self.categories = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.categories = {}

    def _show_add_income_dialog(self) -> None:
        """Show dialog for adding new income source."""
        dialog = ctk.CTkInputDialog(
            text="Enter income source and amount (format: 'Salary:5000')",
            title="Add Income"
        )
        
        def handle_dialog():
            value = dialog.get_input()
            if value:
                try:
                    source, amount_str = value.split(":")
                    amount = float(amount_str)
                    self._add_income(source.strip(), amount)
                except ValueError:
                    self._show_message("Invalid format. Use 'Source:Amount'", is_error=True)
        
        dialog.after(100, handle_dialog)

    def _add_income(self, source: str, amount: float) -> None:
        """Add new income source to user data.
        
        Args:
            source: Name of income source
            amount: Income amount
        """
        if not source or amount <= 0:
            self._show_message("Please enter valid source and amount", is_error=True)
            return
        
        if self.app.current_user:
            self.app.current_user.add_income(source, amount)
            self.app.auth_manager.save_user_data(self.app.current_user)
            self.update_view()
            self._show_message(f"Income source '{source}' added successfully!")

    def _add_transaction(self) -> None:
        """Add a new transaction to user data."""
        if not self.app.current_user:
            self._show_message("Please log in to add transactions", is_error=True)
            return
        
        category = self.category_var.get()
        amount_str = self.amount_entry.get()
        date_str = self.date_entry.get()
        
        # Validate inputs
        if category == "Select Category":
            self._show_message("Please select a category", is_error=True)
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            self._show_message("Please enter a valid amount", is_error=True)
            return
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self._show_message("Please enter date in YYYY-MM-DD format", is_error=True)
            return
        
        # Create and add transaction
        transaction = Transaction(
            id=str(uuid.uuid4()),
            type="expense",
            category=category,
            amount=amount,
            date=date_str,
            budget=self.categories.get(category)
        )
        
        self.app.current_user.add_transaction(transaction)
        self.app.auth_manager.save_user_data(self.app.current_user)
        
        # Clear form and update view
        self.amount_entry.delete(0, "end")
        self.update_view()
        self._show_message("Transaction added successfully!")

    def _show_message(self, message: str, is_error: bool = False) -> None:
        """Display a status message to the user.
        
        Args:
            message: Text to display
            is_error: Whether to style as error message
        """
        if self.message_label:
            self.message_label.destroy()
        
        fg_color = ("#FF5555", "#FF0000") if is_error else ("#55AA55", "#008000")
        self.message_label = ctk.CTkLabel(
            self,
            text=message,
            text_color=fg_color
        )
        self.message_label.grid(row=5, column=0, pady=(0, 10))

    def update_view(self) -> None:
        """Update the view with current user data."""
        if not self.app.current_user:
            return
        
        # Update income display
        total_income = self.app.current_user.get_total_income()
        self.income_label.configure(text=f"Total Income: ₦{total_income:,.2f}")
        
        # Clear and rebuild transactions table
        for widget in self.transactions_table.winfo_children():
            widget.destroy()
        
        self._init_transactions_table()
        
        # Add transactions (most recent first)
        transactions = sorted(
            self.app.current_user.transactions,
            key=lambda t: t.date,
            reverse=True
        )[:20]  # Limit to 20 most recent
        
        for row, transaction in enumerate(transactions, start=1):
            # Date
            ctk.CTkLabel(
                self.transactions_table,
                text=transaction.date,
                anchor="center"
            ).grid(row=row, column=0, padx=10, pady=2)
            
            # Category
            ctk.CTkLabel(
                self.transactions_table,
                text=transaction.category,
                anchor="center"
            ).grid(row=row, column=1, padx=10, pady=2)
            
            # Amount
            ctk.CTkLabel(
                self.transactions_table,
                text=f"₦{transaction.amount:,.2f}",
                anchor="center",
                text_color="red"
            ).grid(row=row, column=2, padx=10, pady=2)
            
            # Budget
            budget = self.app.current_user.expense_budgets.get(transaction.category, 0)
            budget_text = f"₦{budget:,.2f}" if budget else "N/A"
            ctk.CTkLabel(
                self.transactions_table,
                text=budget_text,
                anchor="center"
            ).grid(row=row, column=3, padx=10, pady=2)