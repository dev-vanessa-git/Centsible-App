from typing import List, Dict, Optional
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Transaction:
    """Represents a financial transaction with all relevant details.
    
    Attributes:
        id: Unique identifier for the transaction
        type: Type of transaction ('income' or 'expense')
        category: Transaction category (e.g., 'Food', 'Salary')
        amount: Monetary amount of the transaction
        date: Date of transaction in YYYY-MM-DD format
        description: Optional description of the transaction
        budget: Budget amount for expense transactions (optional)
    """
    id: str
    type: str  # 'income' or 'expense'
    category: str
    amount: float
    date: str
    description: str = ""
    budget: Optional[float] = None  # Only applicable for expenses

    def is_expense(self) -> bool:
        """Check if this is an expense transaction.
        
        Returns:
            bool: True if transaction is an expense, False otherwise
        """
        return self.type == 'expense'

    def is_income(self) -> bool:
        """Check if this is an income transaction.
        
        Returns:
            bool: True if transaction is income, False otherwise
        """
        return self.type == 'income'

    def is_over_budget(self) -> Optional[bool]:
        """Check if an expense transaction exceeds its budget.
        
        Returns:
            Optional[bool]: 
                - True if expense exceeds budget
                - False if expense is within budget
                - None if not an expense or no budget set
        """
        if not self.is_expense() or self.budget is None:
            return None
        return self.amount > self.budget


@dataclass
class User:
    """Represents a user account with financial data and transactions.
    
    Attributes:
        username: Unique username identifier
        password: User password (should be hashed in production)
        transactions: List of all user transactions
        income_sources: Dictionary of income sources and amounts
        expense_budgets: Dictionary of expense categories and budgets
    """
    username: str
    password: str  # In production, store only hashed passwords
    transactions: List[Transaction] = field(default_factory=list)
    income_sources: Dict[str, float] = field(default_factory=dict)
    expense_budgets: Dict[str, float] = field(default_factory=dict)
    
    def add_income(self, source: str, amount: float) -> None:
        """Add or update an income source.
        
        Args:
            source: Name of the income source (e.g., 'Salary')
            amount: Amount of income
        """
        if amount <= 0:
            raise ValueError("Income amount must be positive")
        self.income_sources[source] = amount
    
    def add_expense_budget(self, category: str, budget: float) -> None:
        """Add or update an expense category budget.
        
        Args:
            category: Name of the expense category
            budget: Budget amount for the category
        """
        if budget < 0:
            raise ValueError("Budget amount cannot be negative")
        self.expense_budgets[category] = budget
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to the user's history.
        
        Args:
            transaction: Transaction object to add
            
        Note:
            For new expense categories, initializes budget if not set
        """
        self.transactions.append(transaction)
        
        # Initialize budget for new expense categories
        if (transaction.is_expense() and 
            transaction.category not in self.expense_budgets):
            self.expense_budgets[transaction.category] = transaction.budget or 0
    
    def get_total_income(self) -> float:
        """Calculate the user's total income from all sources.
        
        Returns:
            float: Sum of all income amounts
        """
        return sum(self.income_sources.values())
    
    def get_total_expenses(self) -> float:
        """Calculate the user's total expenses.
        
        Returns:
            float: Sum of all expense transactions
        """
        return sum(t.amount for t in self.transactions if t.is_expense())
    
    def get_net_balance(self) -> float:
        """Calculate the user's net balance (income - expenses).
        
        Returns:
            float: Current net balance
        """
        return self.get_total_income() - self.get_total_expenses()
    
    def get_expenses_by_category(self) -> Dict[str, float]:
        """Get expenses aggregated by category.
        
        Returns:
            Dict[str, float]: 
                Dictionary mapping category names to total amounts spent
        """
        expenses = {}
        for t in self.transactions:
            if t.is_expense():
                expenses[t.category] = expenses.get(t.category, 0) + t.amount
        return expenses
    
    def get_budget_status(self) -> Dict[str, Dict[str, float]]:
        """Get budget status for all expense categories.
        
        Returns:
            Dict[str, Dict[str, float]]: 
                Dictionary with category budgets, spent amounts, and remaining amounts
                Format: {category: {'budget': x, 'spent': y, 'remaining': z}}
        """
        status = {}
        expenses_by_category = self.get_expenses_by_category()
        
        for category, budget in self.expense_budgets.items():
            spent = expenses_by_category.get(category, 0)
            status[category] = {
                'budget': budget,
                'spent': spent,
                'remaining': max(0, budget - spent)
            }
        
        return status
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize user data to a dictionary for storage.
        
        Returns:
            Dict[str, Any]: Dictionary containing all user data
        """
        return {
            'username': self.username,
            'password': self.password,
            'transactions': [
                {
                    'id': t.id,
                    'type': t.type,
                    'category': t.category,
                    'amount': t.amount,
                    'date': t.date,
                    'description': t.description,
                    'budget': t.budget
                } for t in self.transactions
            ],
            'income_sources': self.income_sources,
            'expense_budgets': self.expense_budgets
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User object from serialized dictionary data.
        
        Args:
            data: Dictionary containing serialized user data
            
        Returns:
            User: Reconstructed User object
        """
        user = cls(
            username=data['username'],
            password=data['password']
        )
        user.transactions = [
            Transaction(
                id=t['id'],
                type=t['type'],
                category=t['category'],
                amount=t['amount'],
                date=t['date'],
                description=t.get('description', ''),
                budget=t.get('budget')
            ) for t in data.get('transactions', [])
        ]
        user.income_sources = data.get('income_sources', {})
        user.expense_budgets = data.get('expense_budgets', {})
        return user