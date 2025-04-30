import customtkinter as ctk
from tkinter import filedialog
import threading
from typing import Dict, List, Optional, Tuple, Any
from utils.ai_helper import generate_ai_insight
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import io
from datetime import datetime


class InsightsView(ctk.CTkFrame):
    """View for displaying AI-generated financial insights and visualizations.
    
    Provides:
    - AI-powered financial analysis generation
    - Interactive visualization of budget vs expenses
    - Categorized insights cards
    - PDF report generation
    
    Args:
        master: Parent widget
        app: Reference to main application instance
        **kwargs: Additional arguments for CTkFrame
    """

    def __init__(self, master: ctk.CTk, app: Any, **kwargs) -> None:
        """Initialize the insights view with UI components."""
        super().__init__(master, **kwargs)
        self.app = app
        self.current_figure: Optional[Figure] = None
        self.insights_data: Dict[str, List[str]] = {}  # Stores categorized insights
        self.chart_data: Optional[Dict[str, List]] = None  # Stores chart data for export

        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create UI components
        self._create_title()
        self._create_content_frame()
        self._create_controls()
        self._create_cards_container()
        self._create_chart_frame()

        # Initial view state
        self.update_view()

    def _create_title(self) -> None:
        """Create the view title label."""
        self.title_label = ctk.CTkLabel(
            self, 
            text="AI-Powered Financial Insights",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="w")

    def _create_content_frame(self) -> None:
        """Create the main content container frame."""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        self.content_frame.grid_rowconfigure(1, weight=1)  # Cards container
        self.content_frame.grid_rowconfigure(2, weight=0)  # Chart frame
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _create_controls(self) -> None:
        """Create the control buttons frame."""
        self.controls_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.controls_frame.grid(row=0, column=0, sticky="ew")
        
        self.generate_button = ctk.CTkButton(
            self.controls_frame, 
            text="Generate Insights",
            command=self._generate_insights
        )
        self.generate_button.pack(side="left", padx=(0, 10))

        self.export_button = ctk.CTkButton(
            self.controls_frame, 
            text="Export Full Report",
            command=self._export_full_report,
            state="disabled"
        )
        self.export_button.pack(side="left", padx=(10, 10))

        self.loading_label = ctk.CTkLabel(
            self.controls_frame, 
            text="", 
            text_color="green"
        )
        self.loading_label.pack(side="left")

    def _create_cards_container(self) -> None:
        """Create the container for insight cards."""
        self.cards_container = ctk.CTkFrame(self.content_frame)
        self.cards_container.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.cards_container.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="columns")
        self.cards_container.grid_rowconfigure(0, weight=1)

    def _create_chart_frame(self) -> None:
        """Create the frame for budget vs expense chart."""
        self.chart_frame = ctk.CTkFrame(self.content_frame)
        self.chart_frame.grid(row=2, column=0, sticky="nsew", pady=(20, 0))
        self.chart_frame.grid_columnconfigure(0, weight=1)

    def _generate_insights(self) -> None:
        """Initiate the AI insights generation process."""
        if not self.app.current_user:
            self._show_message("Please log in to get insights", is_error=True)
            return

        self.generate_button.configure(state="disabled")
        self.export_button.configure(state="disabled")
        self.loading_label.configure(text="Generating insights...")

        # Prepare user data for AI analysis
        user_data = self._prepare_user_data()
        
        # Run AI generation in background thread
        threading.Thread(
            target=self._call_ai_and_update,
            args=(user_data,),
            daemon=True
        ).start()

    def _prepare_user_data(self) -> Dict[str, Any]:
        """Prepare user financial data for AI analysis.
        
        Returns:
            Dictionary containing formatted user financial data
        """
        dates = [datetime.strptime(t.date, "%Y-%m-%d") for t in self.app.current_user.transactions]
        date_range = f"{min(dates).strftime('%B %d, %Y')} to {max(dates).strftime('%B %d, %Y')}" if dates else "No date range"

        return {
            "income_sources": self.app.current_user.income_sources,
            "expense_budgets": self.app.current_user.expense_budgets,
            "transactions": [
                {
                    "category": t.category,
                    "amount": t.amount,
                    "date": t.date,
                    "budget": t.budget
                } for t in self.app.current_user.transactions
            ],
            "total_income": self.app.current_user.get_total_income(),
            "total_expenses": self.app.current_user.get_total_expenses(),
            "net_balance": self.app.current_user.get_net_balance(),
            "date_range": date_range,
            "username": self.app.current_user.username
        }

    def _call_ai_and_update(self, user_data: Dict[str, Any]) -> None:
        """Call AI helper and update UI with results.
        
        Args:
            user_data: Prepared financial data for analysis
        """
        try:
            insights = generate_ai_insight(user_data)
            if not self.winfo_exists():  # Check if widget still exists
                return
                
            self.insights_data = self._group_insights(insights)
            self.chart_data = self._prepare_chart_data(user_data)
            
            # Schedule UI updates on main thread
            self.after(0, self._update_ui_after_generation)
            self._show_message("Insights generated successfully!")
        except Exception as e:
            if self.winfo_exists():
                self._show_message(f"Error: {e}", is_error=True)
            self.after(0, self._reset_ui)

    def _update_ui_after_generation(self) -> None:
        """Update UI components after successful generation."""
        if self.winfo_exists():
            self._display_insight_cards()
            if self.chart_data:
                self._generate_budget_chart(self.chart_data)
            self.export_button.configure(state="normal")
            self.generate_button.configure(state="normal")

    def _group_insights(self, insights: str) -> Dict[str, List[str]]:
        """Categorize raw insights text into structured groups.
        
        Args:
            insights: Raw text output from AI
            
        Returns:
            Dictionary mapping categories to lists of insights
        """
        categories = {
            "Summary": [],
            "Spending Alerts": [],
            "Budget Recommendations": [],
            "Positive Feedback": [],
            "General Advice": []
        }
        
        current_category = "Summary"
        for line in insights.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Detect category headers
            if line.lower().startswith("[summary]"):
                current_category = "Summary"
                line = line.replace("[Summary]", "").strip()
            elif "alert" in line.lower() or "warning" in line.lower():
                current_category = "Spending Alerts"
            elif "recommendation" in line.lower() or "suggestion" in line.lower():
                current_category = "Budget Recommendations"
            elif "positive" in line.lower() or "good" in line.lower():
                current_category = "Positive Feedback"
            elif "advice" in line.lower() or "tip" in line.lower():
                current_category = "General Advice"
                
            if line:
                categories[current_category].append(line)
                
        return categories

    def _display_insight_cards(self) -> None:
        """Display insight cards for each category."""
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        categories = [
            ("Summary", "#4B8BBE"),  # Blue
            ("Spending Alerts", "#FF5555"),  # Red
            ("Budget Recommendations", "#FFA500"),  # Orange
            ("Positive Feedback", "#55FF55"),  # Green
            ("General Advice", "#888888")  # Gray
        ]

        for i, (category, color) in enumerate(categories):
            card = self._create_category_card(category, color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

    def _create_category_card(self, category: str, color: str) -> ctk.CTkFrame:
        """Create an interactive card for an insight category.
        
        Args:
            category: Insight category name
            color: Base color for the card
            
        Returns:
            Configured CTkFrame widget
        """
        preview_text = "\n".join(self.insights_data.get(category, ["No insights"])[:3])
        
        card = ctk.CTkFrame(self.cards_container, corner_radius=10)
        card.configure(width=180, height=180)

        # Card header
        header = ctk.CTkFrame(card, fg_color=color, corner_radius=8)
        header.pack(fill="x", padx=5, pady=(5, 0))
        
        ctk.CTkLabel(
            header, text=category, 
            font=ctk.CTkFont(weight="bold"),
            text_color="black"
        ).pack(pady=5)

        # Preview content
        content = ctk.CTkTextbox(
            card, wrap="word", 
            height=100,
            font=ctk.CTkFont(size=12),
            activate_scrollbars=True
        )
        content.insert("1.0", preview_text)
        content.configure(state="disabled")
        content.pack(fill="both", expand=True, padx=5, pady=5)

        # View button
        ctk.CTkButton(
            card, text="View Details", 
            command=lambda c=category: self._show_category_modal(c),
            fg_color=color,
            hover_color=self._darken_color(color),
            text_color="black"
        ).pack(pady=(0, 5), padx=5, fill="x")

        return card

    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        """Darken a hex color by specified factor.
        
        Args:
            hex_color: Original color in hex format
            factor: Darkening factor (0-1)
            
        Returns:
            Darkened color in hex format
        """
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * factor)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def _show_category_modal(self, category: str) -> None:
        """Show modal dialog with full insights for a category.
        
        Args:
            category: Name of insight category to display
        """
        modal = ctk.CTkToplevel(self)
        modal.geometry("600x400")
        modal.title(f"{category} Details")

        text_box = ctk.CTkTextbox(modal, wrap="word")
        text_box.insert("1.0", "\n".join(self.insights_data.get(category, ["No insights available"])))
        text_box.configure(state="disabled")
        text_box.pack(padx=20, pady=20, expand=True, fill="both")

    def _prepare_chart_data(self, user_data: Dict[str, Any]) -> Dict[str, List]:
        """Prepare data for budget vs expense chart.
        
        Args:
            user_data: Dictionary containing user financial data
            
        Returns:
            Dictionary containing formatted chart data
        """
        categories = []
        budget_data = []
        expense_data = []
        status_colors = []
        
        for category, budget in user_data["expense_budgets"].items():
            categories.append(category)
            budget_data.append(budget)
            
            category_expenses = sum(
                t["amount"] for t in user_data["transactions"] 
                if t["category"] == category
            )
            expense_data.append(category_expenses)
            
            # Determine status color
            if budget == 0:
                status_colors.append("gray")
            elif category_expenses > budget * 1.1:  # 10% over budget
                status_colors.append("red")
            elif category_expenses > budget:
                status_colors.append("orange")
            else:
                status_colors.append("green")
        
        return {
            "categories": categories,
            "budget_data": budget_data,
            "expense_data": expense_data,
            "status_colors": status_colors
        }

    def _generate_budget_chart(self, chart_data: Dict[str, List]) -> None:
        """Generate and display budget vs expense chart.
        
        Args:
            chart_data: Prepared chart data dictionary
        """
        # Clear previous chart
        if self.current_figure:
            plt.close(self.current_figure)
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

        # Create new figure
        fig, ax = plt.subplots(figsize=(8, 4))
        self.current_figure = fig
        
        # Plot budget line
        ax.plot(
            chart_data["categories"], 
            chart_data["budget_data"], 
            label='Budget', 
            color='blue', 
            linestyle='--'
        )
        
        # Plot expenses with status colors
        for i, (category, expense, color) in enumerate(zip(
            chart_data["categories"],
            chart_data["expense_data"],
            chart_data["status_colors"]
        )):
            ax.bar(i, expense, color=color, alpha=0.6, width=0.6)
        
        # Chart styling
        ax.set_title("Budget vs. Expense Comparison", fontsize=14)
        ax.set_xlabel("Categories")
        ax.set_ylabel("Amount (₦)")
        ax.legend(["Budget", "Expense"])
        ax.set_xticks(range(len(chart_data["categories"])))
        ax.set_xticklabels(chart_data["categories"], rotation=45, ha='right')
        fig.tight_layout()

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _export_full_report(self) -> None:
        """Export insights and chart to PDF report."""
        if not self.insights_data or not self.chart_data:
            self._show_message("No insights to export", is_error=True)
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{self.app.current_user.username}_Financial_Report.pdf"
        )
        
        if not file_path:
            return

        try:
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Add title
            title = Paragraph(
                f"<b>{self.app.current_user.username}'s Financial Health Report</b>",
                styles['Title']
            )
            story.append(title)
            
            # Add date range if available
            date_range = next(
                (line for line in self.insights_data['Summary'] 
                 if "date range" in line.lower()), 
                ""
            )
            if date_range:
                story.append(Paragraph(date_range, styles['Normal']))
            
            story.append(Spacer(1, 12))
            
            # Add all insights by category
            for category, insights in self.insights_data.items():
                if insights:
                    story.append(Paragraph(f"<b>{category}</b>", styles['Heading2']))
                    for insight in insights:
                        story.append(Paragraph(f"• {insight}", styles['Normal']))
                    story.append(Spacer(1, 8))
            
            # Add chart
            story.append(Paragraph("<b>Budget vs. Expenses</b>", styles['Heading2']))
            
            # Save chart to buffer
            buf = io.BytesIO()
            self.current_figure.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            
            # Add chart image to PDF
            story.append(Image(buf, width=400, height=200))
            
            # Build PDF
            doc.build(story)
            self._show_message("Report exported successfully!")
        except Exception as e:
            self._show_message(f"Export failed: {str(e)}", is_error=True)

    def update_view(self) -> None:
        """Reset the view to initial state."""
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        self._show_message("Click 'Generate Insights' to get financial advice.")
        self.export_button.configure(state="disabled")

    def _reset_ui(self) -> None:
        """Reset UI controls after generation attempt."""
        self.generate_button.configure(state="normal")
        self.loading_label.configure(text="")

    def _show_message(self, message: str, is_error: bool = False) -> None:
        """Display a status message.
        
        Args:
            message: Text to display
            is_error: Whether to style as error message
        """
        self.loading_label.configure(
            text=message,
            text_color=("red" if is_error else "green")
        )