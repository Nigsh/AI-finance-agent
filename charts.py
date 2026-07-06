"""
charts.py
Chart-generation utilities for the Finance AI Assistant.
Builds matplotlib figures that Streamlit can render with st.pyplot().
"""

import matplotlib.pyplot as plt
import pandas as pd


def _category_totals(df: pd.DataFrame) -> pd.Series:
    """Return total spending per category, sorted descending."""
    return (
        df.groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )


def plot_pie_chart(df: pd.DataFrame):
    """Pie chart of spending share by category."""
    totals = _category_totals(df)

    fig, ax = plt.subplots(figsize=(6, 6))
    colors = plt.cm.Set2.colors
    ax.pie(
        totals.values,
        labels=totals.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        wedgeprops={"edgecolor": "white", "linewidth": 1},
    )
    ax.set_title("Spending by Category", fontsize=14, fontweight="bold")
    ax.axis("equal")
    fig.tight_layout()
    return fig


def plot_bar_chart(df: pd.DataFrame):
    """Bar chart of total spending by category."""
    totals = _category_totals(df)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(totals.index, totals.values, color="#4C78A8")
    ax.set_ylabel("Amount (ETB)")
    ax.set_title("Total Spending by Category", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=35)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:,.0f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            fontsize=8,
        )

    fig.tight_layout()
    return fig


def plot_daily_trend(df: pd.DataFrame):
    """Line chart of total spending per day, useful for spotting trends."""
    daily = df.groupby("Date")["Amount"].sum().sort_index()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(daily.index, daily.values, marker="o", color="#E45756")
    ax.set_ylabel("Amount (ETB)")
    ax.set_title("Daily Spending Trend", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig
