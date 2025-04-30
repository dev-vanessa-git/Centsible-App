import matplotlib.pyplot as plt
from typing import Dict, List


def create_bar_chart(
    expenses_by_category: Dict[str, float],
    budgets_by_category: Dict[str, float]
) -> plt.Figure:
    """
    Create a comparative bar chart showing actual expenses versus budgeted amounts by category.

    Args:
        expenses_by_category: Dictionary mapping category names to actual spent amounts.
            Example: {'Food': 15000, 'Transport': 8000}
        budgets_by_category: Dictionary mapping category names to budgeted amounts.
            Example: {'Food': 12000, 'Transport': 10000}

    Returns:
        matplotlib.figure.Figure: A Figure object containing the generated bar chart.
            The chart displays:
            - Blue bars representing budgeted amounts
            - Orange bars representing actual expenses
            - Value labels for each bar
            - Properly formatted axes and legend

    Notes:
        - Categories are taken from expenses_by_category keys
        - Budgets default to 0 for categories not in budgets_by_category
        - Handles empty data by displaying "No expense data" message
        - Automatically formats amounts with thousands separators
        - Uses Naira symbol (₦) for currency
    """
    fig, ax = plt.subplots(figsize=(5, 6))
    
    if not expenses_by_category:
        ax.text(0.5, 0.5, "No expense data", 
               ha='center', va='center', fontsize=12)
        ax.set_title("Expenses vs Budgets")
        return fig
    
    categories = list(expenses_by_category.keys())
    expenses = list(expenses_by_category.values())
    budgets = [budgets_by_category.get(cat, 0) for cat in categories]
    
    # Chart configuration
    bar_width = 0.35
    x_positions = range(len(categories))
    
    # Create bars with corporate-style colors
    budget_bars = ax.bar(
        x_positions, 
        budgets, 
        bar_width, 
        label='Budget', 
        color='#1f77b4'  # Corporate blue
    )
    expense_bars = ax.bar(
        [i + bar_width for i in x_positions], 
        expenses, 
        bar_width, 
        label='Actual', 
        color='#ff7f0e'  # Corporate orange
    )
    
    # Axes and labels configuration
    ax.set_xlabel('Categories')
    ax.set_ylabel('Amount (₦)')
    ax.set_title('Expenses vs Budgets by Category')
    ax.set_xticks([i + bar_width / 2 for i in x_positions])
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()
    
    def add_value_labels(bars: List[plt.Rectangle]) -> None:
        """Helper function to add value labels above bars."""
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f'{height:,.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center',
                    va='bottom',
                    fontsize=8
                )
    
    add_value_labels(budget_bars)
    add_value_labels(expense_bars)
    
    plt.tight_layout()
    return fig