import json
import streamlit as st 
import google.generativeai as genai
import os
from dotenv import load_dotenv  

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Store API key in environment variable
if not GOOGLE_API_KEY:
    st.error("API Key is missing. Set it as an environment variable.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# 🔹 Streamlit UI
st.title("Investment Planner")

col1, col2 = st.columns(2)
with col1:
    goal = st.selectbox(
        "What is your primary financial goal?", 
        ("Saving for retirement", "Building an emergency fund", "Buying a house", 
         "Paying for a child's education", "Taking a dream vacation")
    )
    income = st.number_input("What is your current income level?")

with col2:
    time = st.selectbox(
        "What is your investment time horizon?", 
        ("Short-term (Less than 5 years)", "Medium-term (5-10 years)", "Long-term (10+ years)")
    )
    debt = st.selectbox("Do you have any existing debt?", ("Yes", "No"))

invest = st.number_input("How much investable money do you have available?")
scale = st.slider("How comfortable are you with risk?", min_value=1, max_value=10, step=1)

# 🔹 Formatting user input as context
user_data = f"""
- Primary financial goal: {goal}
- Current income level: INR {income}
- Investment time horizon: {time}
- Existing debt status: {debt}
- Available investable money: INR {invest}
- Risk tolerance level: {scale}/10
"""

# 🔹 Expected JSON format
output_format = """
{
    "Understanding Your Situation": "Short summary of user's financial situation.",
    "Investment Options & Potential Allocation": {
        "High-Yield Savings Account": "Allocation and reason.",
        "Liquid Funds": "Allocation and reason.",
        "Conservative Hybrid Mutual Funds": "Allocation and reason.",
        "Blue-chip Stocks/Index Funds": "Allocation and reason."
    },
    "Important Considerations": "Additional notes or warnings.",
    "Disclaimer": "AI-generated content. Not professional financial advice."
}
"""

# 🔹 Prompt for Gemini AI
prompt = f"{user_data}\nBased on the above details, suggest an investment plan. Return ONLY JSON. Format reference:\n{output_format}"

# 🔹 Generate Investment Plan
if st.button("Generate Investment Plan"):
    with st.spinner("Creating Investment Plan..."):
        response = model.generate_content(prompt)

        investment_plan = response.text.strip()  # Get AI response

        # 🔹 Debugging: Print AI response
        print("Raw AI Response:", investment_plan)

        # 🔹 Ensure JSON format
        if investment_plan.startswith("```json"):
            investment_plan = investment_plan.strip("```json").strip("```")

        try:
            investment_plan_json = json.loads(investment_plan)  # Parse JSON

            # 🔹 Display Investment Plan
            st.subheader("📌 Understanding Your Situation")
            st.write(investment_plan_json.get("Understanding Your Situation", "No information provided."))

            st.subheader("📈 Investment Options & Potential Allocation")
            for key, value in investment_plan_json.get("Investment Options & Potential Allocation", {}).items():
                st.markdown(f"**{key}**: {value}")

            st.subheader("⚠️ Important Considerations")
            st.write(investment_plan_json.get("Important Considerations", "No information provided."))

            st.subheader("📢 Disclaimer")
            st.write(investment_plan_json.get("Disclaimer", "No information provided."))

        except json.JSONDecodeError:
            st.error("Failed to parse AI response. Please try again.")
            st.text("Raw AI Response:\n" + investment_plan)  # Show response for debugging
