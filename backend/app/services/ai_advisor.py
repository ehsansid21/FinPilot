import json
from google import genai
from app.core.config import settings
from app.services.calculator import calculate_simulation

# Initialize the Gemini client
# It will automatically pick up GEMINI_API_KEY from environment variables if not passed explicitly,
# but we can also pass it explicitly from our settings.
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_financial_advice(user_id: int, db):
    # Get the calculated simulation data
    sim_data = calculate_simulation(user_id, db)
    
    # Format the data into a prompt
    prompt = f"""
You are FinPilot, an expert AI financial advisor.
Review the following user financial data and provide actionable, personalized advice.

Financial Profile:
- Monthly Income: ${sim_data['monthly_income']}
- Current Savings: ${sim_data['current_savings']}
- Total Monthly Expenses: ${sim_data['total_monthly_expenses']}
- Monthly Savings Capacity (Income - Expenses): ${sim_data['monthly_savings_capacity']}

Financial Goals:
"""
    for goal in sim_data['goals']:
        prompt += f"- {goal['name']}: Need ${goal['target_amount']} in {goal['months_to_goal']} months (Requires ${goal['required_monthly']:.2f}/mo)\n"
    
    prompt += f"""
Total required monthly for all goals: ${sim_data['required_monthly_for_goals']:.2f}
Is this feasible based on their capacity? {'Yes' if sim_data['is_feasible'] else 'No'}

Please provide a short, encouraging summary of their situation.
If it is not feasible, suggest specific areas they could cut back on or how they should adjust their goals.
If it is feasible, validate their plan and suggest how they could optimize their remaining capacity.
Keep the response under 150 words and use markdown formatting.
"""

    if not settings.GEMINI_API_KEY:
        return "⚠️ Gemini API Key is missing. Please configure your .env file."

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error communicating with AI Advisor: {str(e)}"
