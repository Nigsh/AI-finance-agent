"""
finance_agent.py
Core logic for the Finance AI Assistant:
- Loading and cleaning transaction data
- Auto-categorizing transactions when no Category column is present
- Computing spending summaries and budget suggestions
- Talking to the Gemini API for natural-language Q&A
"""

import pandas as pd
from google import genai

# ---------------------------------------------------------------------------
# Keyword map used only as a fallback when the uploaded CSV has no
# "Category" column. Users are always free to upload their own categories.
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS = {
    "Groceries": ["supermarket", "market", "grocery", "shoa", "novis"],
    "Transport": ["ride", "fuel", "taxi", "uber", "bus", "transport"],
    "Utilities": ["electricity", "water", "telecom", "internet", "bill", "data bundle"],
    "Food & Drink": ["coffee", "restaurant", "cafe", "dinner", "lunch", "kaldi"],
    "Entertainment": ["netflix", "cinema", "streaming", "movie"],
    "Health": ["pharmacy", "clinic", "hospital", "gym", "health"],
    "Housing": ["rent", "housing", "landlord"],
    "Education": ["book", "tuition", "course", "school", "printing"],
    "Shopping": ["clothing", "shop", "store", "accessory", "electronics"],
}


def load_transactions(file) -> pd.DataFrame:
    """
    Load a transactions CSV into a cleaned DataFrame.
    Expects at least 'Date', 'Description', 'Amount' columns.
    Adds a 'Category' column automatically if missing.
    """
    df = pd.read_csv(file)
    df.columns = [c.strip().title() for c in df.columns]

    required = {"Date", "Description", "Amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required column(s): {', '.join(missing)}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    df = df.dropna(subset=["Date"])

    if "Category" not in df.columns:
        df["Category"] = df["Description"].apply(_guess_category)

    df["Category"] = df["Category"].fillna("Other").replace("", "Other")
    return df


def _guess_category(description: str) -> str:
    text = str(description).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "Other"


def spending_summary(df: pd.DataFrame) -> dict:
    """Return a dict of high-level spending stats used for display and prompting."""
    total = df["Amount"].sum()
    by_category = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    top_category = by_category.index[0] if not by_category.empty else "N/A"
    num_days = max((df["Date"].max() - df["Date"].min()).days + 1, 1)
    daily_avg = total / num_days

    return {
        "total": total,
        "by_category": by_category,
        "top_category": top_category,
        "top_category_amount": by_category.iloc[0] if not by_category.empty else 0,
        "daily_avg": daily_avg,
        "num_days": num_days,
        "num_transactions": len(df),
    }


def suggest_budget(df: pd.DataFrame, savings_target_pct: float = 20.0) -> pd.DataFrame:
    """
    Suggest a simple next-month budget per category.
    Approach: scale observed spend down proportionally so total spend
    leaves room for the requested savings percentage, while capping
    any single category's cut at 30% to keep suggestions realistic.
    """
    by_category = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    total = by_category.sum()
    target_total = total * (1 - savings_target_pct / 100)

    if total == 0:
        return pd.DataFrame(columns=["Category", "Current Spend", "Suggested Budget"])

    scale = max(target_total / total, 0.7)  # never suggest cutting a category by more than 30%
    suggested = (by_category * scale).round(0)

    result = pd.DataFrame(
        {
            "Category": by_category.index,
            "Current Spend": by_category.values,
            "Suggested Budget": suggested.values,
        }
    )
    return result.reset_index(drop=True)


class FinanceAgent:
    """Wraps the Gemini API to answer natural-language questions about spending."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    @staticmethod
    def _build_context(df: pd.DataFrame) -> str:
        summary = spending_summary(df)
        lines = [
            f"Total spending: {summary['total']:,.2f} ETB over {summary['num_days']} days "
            f"({summary['num_transactions']} transactions).",
            f"Average daily spend: {summary['daily_avg']:,.2f} ETB.",
            f"Top spending category: {summary['top_category']} "
            f"({summary['top_category_amount']:,.2f} ETB).",
            "Spending by category:",
        ]
        for cat, amt in summary["by_category"].items():
            lines.append(f"  - {cat}: {amt:,.2f} ETB")
        return "\n".join(lines)

    def answer_question(self, df: pd.DataFrame, question: str) -> str:
        """Send the user's question plus a spending summary to Gemini and return the reply."""
        context = self._build_context(df)
        prompt = (
            "You are a helpful personal finance assistant. A user has shared a summary "
            "of their recent transactions below. Answer their question clearly and "
            "concisely, with practical, specific advice when relevant. Use the currency "
            "ETB (Ethiopian Birr) since that is what the data is in.\n\n"
            f"SPENDING SUMMARY:\n{context}\n\n"
            f"USER QUESTION: {question}\n\n"
            "Answer:"
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text
