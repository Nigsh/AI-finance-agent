 Finance AI Assistant

A personal finance dashboard that analyzes your spending, suggests monthly budgets, generates charts, and answers questions about your money in plain English — powered by the free Google Gemini API.

Built with Python, Pandas, Matplotlib, and Streamlit.


Features


 Upload a CSV of your transactions (or use the built-in sample data)
 Analyze spending by category — automatic if your CSV doesn't already have categories
 Get monthly budget suggestions with an adjustable savings target
 Visualize your spending with pie charts, bar charts, and a daily trend line
 Ask questions in natural language, e.g.:

"Where am I spending the most?"
"How can I reduce my expenses?"
"Show me a chart of my spending."






Project Structure

finance-ai/
│
├── app.py              # Streamlit app — the dashboard and chat UI
├── finance_agent.py     # Data loading, categorization, budgeting, Gemini API calls
├── charts.py             # Matplotlib chart generators (pie, bar, trend)
├── transactions.csv      # Sample transaction data
├── requirements.txt      # Python dependencies
└── assets/               # Space for logos/icons if you customize the UI


Setup

1. Get a free Gemini API key


Go to Google AI Studio
Sign in with a Google account
Create a free API key


2. Install requirements

Make sure you have Python 3.11+ installed, then:

bashcd finance-ai
pip install -r requirements.txt

3. Run the app

bashstreamlit run app.py

Streamlit will open the app in your browser (usually at http://localhost:8501).

4. Enter your API key

Paste your Gemini API key into the sidebar text box. It's kept only in your session — nothing is saved to disk.


Using Your Own Data

Upload a CSV with these columns:

ColumnRequired?NotesDateYesAny standard date formatDescriptionYesMerchant or transaction descriptionAmountYesNumeric value of the transactionCategoryNoAuto-generated from keywords if missing

If you don't provide a Category column, the app guesses one using keyword matching (e.g. "supermarket" → Groceries, "rent" → Housing). You can always edit the CSV to correct categories before uploading.


How It Works


finance_agent.py loads and cleans the CSV, computes spending summaries, and builds a budget suggestion by scaling each category down toward a savings target (capped at a 30% max cut per category to keep suggestions realistic).
charts.py turns the cleaned data into Matplotlib figures for the pie chart, bar chart, and daily trend line.
app.py ties it together into a Streamlit dashboard, and sends a summary of your spending plus your question to Gemini for the chat feature — so the AI's answers are grounded in your actual numbers, not generic advice.



Tech Stack


Python — core logic
Pandas — data loading and aggregation
Matplotlib — chart generation
Streamlit — web interface
Google Gemini API (free tier via google-genai SDK) — natural language Q&A



Notes & Limitations


The keyword-based auto-categorization is a simple fallback; it won't be perfectly accurate on unfamiliar merchant names.
The Gemini free tier has rate limits — if you hit an error in the chat, wait a moment and try again.


