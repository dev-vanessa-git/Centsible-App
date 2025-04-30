from together import Together
import json
from dotenv import load_dotenv
from typing import Dict, Union

# Initialize Together client with API key from environment variables
load_dotenv()
client = Together()  # Authentication uses os.environ.get("TOGETHER_API_KEY")


def generate_ai_insight(user_data: Dict[str, Union[str, float, int]]) -> str:
    """
    Generate AI-powered financial insights based on the user's financial data.

    Args:
        user_data: Dictionary containing the user's financial information including:
            - income: Various income sources and amounts
            - expenses: Categorized spending data
            - budgets: Budget allocations
            - savings: Current savings information

    Returns:
        str: Formatted financial insights with section headers, or an error message if the request fails.
        The response includes sections for summary, spending alerts, positive feedback,
        budget recommendations, savings suggestions, and additional advice.

    Raises:
        Note: Errors are caught and returned as strings rather than raised
    """
    prompt = f"""
    Analyze the following financial data and provide personalized insights and recommendations:
    
    User Financial Data:
    {json.dumps(user_data, indent=2)}
    
    Please structure your response with these clear sections:
    
    [Summary]
    Provide a brief overview of the user's financial situation including:
    - Total income
    - Total expenses
    - Net balance
    - General financial health assessment
    
    [Spending Alerts]
    Identify any concerning spending patterns where:
    - Expenses exceed budgets
    - Spending seems unusually high in certain categories
    - Any other potential financial risks
    Format these as clear warnings
    
    [Positive Feedback]
    Highlight good financial habits such as:
    - Categories where spending is well-controlled
    - Savings habits
    - Any other positive financial behaviors
    
    [Budget Recommendations]
    Provide specific suggestions for improving budgeting including:
    - Categories that could use adjustment
    - Potential savings opportunities
    - Budget allocation advice
    
    [Savings Suggestions]
    Offer advice on saving and investing including:
    - Recommended savings amounts
    - Potential investment opportunities
    - Emergency fund recommendations
    
    [Additional Advice]
    Provide any other relevant financial tips that could help the user
    
    Important Notes:
    - Use clear section headers in [brackets] for each part
    - Replace all $ symbols with ₦ (Naira)
    - Use bullet points for lists
    - Keep the tone professional but friendly
    """
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[
                {"role": "system", "content": "You are a helpful financial advisor providing detailed but clear advice."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
    
        insights = response.choices[0].message.content.strip()
        insights = insights.replace('$', '₦')  # Replace dollar signs with Naira symbol

        return insights
    except Exception as e:
        return f"Error generating insights: {str(e)}"