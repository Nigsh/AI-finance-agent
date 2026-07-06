"""
app.py
Finance AI Assistant — Streamlit front end.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd

from finance_agent import load_transactions, spending_summary, suggest_budget, FinanceAgent
from charts import plot_pie_chart, plot_bar_chart, plot_daily_trend

st.set_page_config(page_title="Finance AI Assistant", page_icon="💰", layout="wide")


# ---------------------------------------------------------------------------
# Sidebar: API key + data upload
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("💰 Finance AI Assistant")
    st.caption("Powered by Google Gemini (free tier)")

    st.subheader("1. Gemini API Key")
    api_key = st.text_input(
        "Enter your Gemini API key",
        type="password",
        help="Get a free key at https://aistudio.google.com",
        value=st.session_state.get("api_key", ""),
    )
    if api_key:
        st.session_state["api_key"] = api_key
        st.success("API key set for this session.")
    else:
        st.info("Paste your API key to enable the chat assistant.")

    st.subheader("2. Upload Transactions")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    use_sample = st.checkbox("Use sample data instead", value=uploaded_file is None)

    st.markdown("---")
    st.caption(
        "CSV should have columns: **Date, Description, Amount** "
        "(a **Category** column is optional — one is auto-generated if missing)."
    )


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = None
error_message = None

try:
    if uploaded_file is not None and not use_sample:
        df = load_transactions(uploaded_file)
    elif use_sample:
        df = load_transactions("transactions.csv")
except Exception as e:
    error_message = str(e)

if error_message:
    st.error(f"Couldn't load transactions: {error_message}")
    st.stop()

if df is None:
    st.warning("Upload a CSV or check 'Use sample data' in the sidebar to get started.")
    st.stop()


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
st.title("📊 Your Spending Dashboard")

summary = spending_summary(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Spending", f"{summary['total']:,.0f} ETB")
col2.metric("Daily Average", f"{summary['daily_avg']:,.0f} ETB")
col3.metric("Top Category", summary["top_category"])
col4.metric("Transactions", summary["num_transactions"])

st.markdown("### Transactions")
with st.expander("View transaction table", expanded=False):
    st.dataframe(df.sort_values("Date"), use_container_width=True)

st.markdown("### 📈 Charts")
tab1, tab2, tab3 = st.tabs(["Pie Chart", "Bar Chart", "Daily Trend"])
with tab1:
    st.pyplot(plot_pie_chart(df))
with tab2:
    st.pyplot(plot_bar_chart(df))
with tab3:
    st.pyplot(plot_daily_trend(df))

st.markdown("### 💡 Suggested Monthly Budget")
savings_target = st.slider("Target savings (% of current spending)", 0, 50, 20)
budget_df = suggest_budget(df, savings_target_pct=savings_target)
st.dataframe(
    budget_df.style.format({"Current Spend": "{:,.0f}", "Suggested Budget": "{:,.0f}"}),
    use_container_width=True,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Chat assistant
# ---------------------------------------------------------------------------
st.markdown("### 💬 Ask Your Finance Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not st.session_state.get("api_key"):
    st.info("Enter your Gemini API key in the sidebar to start chatting.")
else:
    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(message)

    example_cols = st.columns(3)
    example_questions = [
        "Where am I spending the most?",
        "How can I reduce my expenses?",
        "Show me a chart of my spending.",
    ]
    clicked_question = None
    for col, q in zip(example_cols, example_questions):
        if col.button(q, use_container_width=True):
            clicked_question = q

    user_question = st.chat_input("Ask about your spending...")
    question = user_question or clicked_question

    if question:
        st.session_state.chat_history.append(("user", question))
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    agent = FinanceAgent(api_key=st.session_state["api_key"])
                    if "chart" in question.lower() or "graph" in question.lower():
                        st.pyplot(plot_bar_chart(df))
                        reply = (
                            "Here's a bar chart of your spending by category. "
                            "Check the Charts section above for a pie chart and daily trend too."
                        )
                    else:
                        reply = agent.answer_question(df, question)
                    st.markdown(reply)
                    st.session_state.chat_history.append(("assistant", reply))
                except Exception as e:
                    st.error(f"Something went wrong calling Gemini: {e}")
