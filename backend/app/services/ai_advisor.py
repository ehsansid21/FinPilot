import json
from google import genai
from app.core.config import settings
from app.services.calculator import calculate_simulation

# Initialize the Gemini client
# It will automatically pick up GEMINI_API_KEY from environment variables if not passed explicitly,
# but we can also pass it explicitly from our settings.
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_financial_advice(user_id: int, db, query: str = None):
    # Get the calculated simulation data
    sim_data = calculate_simulation(user_id, db)
    
    # Parse risk tolerance value
    risk_val = sim_data['risk_tolerance']
    
    # Calculate emergency fund requirements
    emergency_3mo = sim_data['total_monthly_expenses'] * 3
    emergency_6mo = sim_data['total_monthly_expenses'] * 6
    
    # Format the data into a prompt
    prompt = f"""
You are FinPilot, an elite, professional AI wealth advisor and financial strategist specializing in the Indian financial markets.
Perform a comprehensive assessment of the following user's financial profile, expenses, and goals in Indian Rupees (₹).

User Profile:
- Monthly Income: ₹{sim_data['monthly_income']}
- Current Savings: ₹{sim_data['current_savings']}
- Total Monthly Expenses: ₹{sim_data['total_monthly_expenses']}
- Actual Monthly Surplus (Income - Expenses): ₹{sim_data['monthly_savings_capacity']}
- Planned Target Monthly Savings: ₹{sim_data['target_savings']}
- Risk Tolerance Profile: {risk_val} (0% is Conservative, 100% is extremely Aggressive)

Active Expenses:
"""
    for exp in sim_data['expenses']:
        prompt += f"- {exp['name']}: ₹{exp['amount']}/mo\n"
        
    prompt += f"""
Financial Goals:
"""
    for goal in sim_data['goals']:
        prompt += f"- {goal['name']}: Target ₹{goal['target_amount']} in {goal['months_to_goal']} mos (Requires ₹{goal['required_monthly']:.2f}/mo)\n"
    
    prompt += f"""
Simulation Assessment:
- Required Monthly Contribution for Goals: ₹{sim_data['required_monthly_for_goals']:.2f}
- Planned target monthly savings of ₹{sim_data['target_savings']} covers goals?: {'Yes' if sim_data['is_feasible'] else 'No'}
- Planned target monthly savings is within actual monthly capacity of ₹{sim_data['monthly_savings_capacity']}?: {'Yes' if sim_data['savings_plan_feasible'] else 'No'}
"""

    if query:
        prompt += f"""
The user has read your initial perspective and has now asked a specific follow-up doubt or request regarding their plan:
"{query}"

Please answer this doubt directly. 
Guidelines:
- Act as their personal wealth manager. Address their doubt with deep financial intelligence.
- If they ask for a new/revised plan, outline a concrete step-by-step target savings or allocation plan tailored to their new request.
- Keep recommendations fully aligned with the Indian market context (mutual funds, PPF, FDs, Sovereign Gold Bonds).
- Keep the response under 350 words. Format with clean markdown headers and bullet points.
"""
    else:
        # Work out useful numbers for the prompt
        total_exp = sim_data['total_monthly_expenses']
        surplus   = sim_data['monthly_savings_capacity']
        target    = sim_data['target_savings']
        required  = sim_data['required_monthly_for_goals']
        gap_goals = required - target          # positive = goals underfunded
        gap_budget = target - surplus          # positive = target exceeds cash flow

        prompt += f"""
Please write your initial wealth assessment using EXACTLY the following markdown headers. Be specific, use the real rupee numbers given, name individual expenses, and keep every section concise and plain-language so a first-time investor can act on it immediately.

## 📊 Overall Financial Health Assessment
- Total monthly outgoings: ₹{total_exp:.0f} out of ₹{sim_data['monthly_income']:.0f} income → actual surplus ₹{surplus:.0f}/mo.
- Emergency fund needed (3–6 months of expenses): ₹{emergency_3mo:.0f} – ₹{emergency_6mo:.0f}.
- Current savings ₹{sim_data['current_savings']:.0f}: state clearly whether this covers the emergency fund or not, and by how much.

## ✂️ Expense Optimization
Look at the user's individual expenses listed above. For EACH expense, give one of three verdicts:
- **Keep** – reasonable and necessary.
- **Reduce** – slightly high; suggest a specific lower amount in ₹ and the monthly saving achieved.
- **Cut** – discretionary or excessive; recommend eliminating it and the monthly saving freed up.

Then summarise: "By acting on the above, you can free up an extra ₹X/mo."

Use this section especially if:
1. Their planned target savings (₹{target:.0f}/mo) exceeds their actual surplus (₹{surplus:.0f}/mo) — they MUST cut expenses to avoid a cash-flow crisis.
2. Their actual surplus is enough but goals are still not covered — cutting expenses and redirecting the savings is the fastest fix.

## 🎯 Goal Fulfillment & Savings Strategy
- Goals require: ₹{required:.0f}/mo total.
- Planned savings: ₹{target:.0f}/mo.
{"- ⚠️ DEFICIT of ₹" + f"{gap_goals:.0f}/mo — explain step-by-step how to close this gap (cut expenses identified above + increase planned savings target to ₹" + f"{required:.0f}/mo). If surplus (₹{surplus:.0f}) is still insufficient after cutting, suggest extending individual goal deadlines by name." if gap_goals > 0 else f"- ✅ Goals are fully covered. The remaining ₹{surplus - target:.0f}/mo unallocated surplus can compound further — tell them exactly where to put it."}
{"- ⚠️ Cash-flow problem: planned savings (₹" + f"{target:.0f}) exceed actual surplus (₹{surplus:.0f}) by ₹{gap_budget:.0f}/mo — the user cannot sustain this plan without cutting expenses. Be direct about this." if gap_budget > 0 else ""}

## 📈 Recommended Asset Allocation (Risk: {risk_val})
Give a concrete percentage split for the user's monthly investable surplus using Indian instruments only.
- Low risk (0–30 %): Bank FDs, Post Office schemes, Sovereign Gold Bonds, Liquid Debt Mutual Funds.
- Medium risk (31–70 %): PPF (up to ₹1.5L/yr, tax-free under 80C), Nifty 50 Index Fund, Balanced Advantage Funds.
- High risk (71–100 %): Nifty Next 50, Mid & Small-Cap Equity Mutual Funds, Flexi-Cap Funds.
Show a simple table: Instrument | % | Approx. ₹/mo.

Keep the total response under 420 words. Use plain language — no jargon without explanation.
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
