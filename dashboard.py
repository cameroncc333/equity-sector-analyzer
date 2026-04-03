"""
Equity Sector Analyzer — Visual Dashboard
Cameron Camarotti | github.com/cameroncc333

Generates publication-quality charts for the equity analysis.
"""

import numpy as np
import pandas as pd
import os

try:
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import seaborn as sns
    HAS_SNS = True
except ImportError:
    HAS_SNS = False

from config import SECTOR_ETFS, RSI_OVERBOUGHT, RSI_OVERSOLD


def set_style():
    if not HAS_MPL:
        return
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "#f8f9fa",
        "axes.edgecolor": "#cccccc",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
    })


def plot_sector_performance(rankings, save_path="output/sector_performance.png"):
    """Bar chart of sector performance ranked by composite score."""
    if not HAS_MPL:
        print("  matplotlib required for charts. pip install matplotlib")
        return

    set_style()
    fig, ax = plt.subplots(figsize=(12, 7))

    names = [f"{r['ticker']} — {r['name']}" for r in rankings]
    scores = [r["60d_momentum"] for r in rankings]
    colors = ["#27AE60" if s >= 0 else "#E74C3C" for s in scores]

    bars = ax.barh(names, scores, color=colors, edgecolor="white", height=0.6)

    for bar, score in zip(bars, scores):
        offset = 0.3 if score >= 0 else -0.3
        ha = "left" if score >= 0 else "right"
        ax.text(bar.get_width() + offset, bar.get_y() + bar.get_height() / 2,
                f"{score:+.1f}%", va="center", ha=ha, fontsize=10, fontweight="bold")

    ax.axvline(x=0, color="#333333", linewidth=0.8)
    ax.set_xlabel("60-Day Return (%)")
    ax.set_title("S&P 500 Sector Performance — 60-Day Returns")
    ax.invert_yaxis()

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_correlation_heatmap(corr_matrix, save_path="output/correlation_heatmap.png"):
    """Heatmap of cross-sector correlations."""
    if not HAS_MPL:
        return

    set_style()
    fig, ax = plt.subplots(figsize=(12, 10))

    names = [SECTOR_ETFS.get(t, t) for t in corr_matrix.columns]

    if HAS_SNS:
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="RdYlGn",
                    center=0, vmin=-1, vmax=1, square=True,
                    xticklabels=names, yticklabels=names,
                    linewidths=0.5, ax=ax,
                    cbar_kws={"label": "Correlation"})
    else:
        im = ax.imshow(corr_matrix.values, cmap="RdYlGn", vmin=-1, vmax=1)
        ax.set_xticks(range(len(names)))
        ax.set_yticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha="right")
        ax.set_yticklabels(names)
        for i in range(len(names)):
            for j in range(len(names)):
                ax.text(j, i, f"{corr_matrix.values[i, j]:.2f}",
                        ha="center", va="center", fontsize=8)
        plt.colorbar(im, ax=ax, label="Correlation")

    ax.set_title("S&P 500 Sector Correlation Matrix\n"
                 "Higher correlation = sectors move together | "
                 "Lower = diversification opportunity")

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_risk_return(rankings, save_path="output/risk_return_scatter.png"):
    """Scatter plot of risk (volatility) vs return for each sector."""
    if not HAS_MPL:
        return

    set_style()
    fig, ax = plt.subplots(figsize=(11, 8))

    for r in rankings:
        ax.scatter(r["volatility"], r["60d_momentum"], s=120,
                   zorder=3, edgecolors="white", linewidth=1.5)
        ax.annotate(f"  {r['ticker']}", (r["volatility"], r["60d_momentum"]),
                    fontsize=10, fontweight="bold")

    ax.axhline(y=0, color="#999999", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Annualized Volatility (%)")
    ax.set_ylabel("60-Day Return (%)")
    ax.set_title("Risk vs Return by Sector\n"
                 "Top-left = best (high return, low risk) | "
                 "Bottom-right = worst (low return, high risk)")

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_rsi_signals(analysis, save_path="output/rsi_signals.png"):
    """Bar chart of RSI values with overbought/oversold zones."""
    if not HAS_MPL:
        return

    set_style()
    fig, ax = plt.subplots(figsize=(12, 6))

    tickers = []
    rsi_values = []
    for ticker, data in analysis.items():
        if "rsi" in data:
            tickers.append(f"{ticker}\n{data['name']}")
            rsi_values.append(data["rsi"]["rsi"])

    colors = []
    for val in rsi_values:
        if val > RSI_OVERBOUGHT:
            colors.append("#E74C3C")
        elif val < RSI_OVERSOLD:
            colors.append("#27AE60")
        else:
            colors.append("#2E75B6")

    bars = ax.bar(tickers, rsi_values, color=colors, edgecolor="white", width=0.7)

    ax.axhline(y=RSI_OVERBOUGHT, color="#E74C3C", linewidth=1.5,
               linestyle="--", label=f"Overbought ({RSI_OVERBOUGHT})")
    ax.axhline(y=RSI_OVERSOLD, color="#27AE60", linewidth=1.5,
               linestyle="--", label=f"Oversold ({RSI_OVERSOLD})")
    ax.axhline(y=50, color="#999999", linewidth=0.8, linestyle=":")

    for bar, val in zip(bars, rsi_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val:.0f}", ha="center", fontsize=9, fontweight="bold")

    ax.set_ylabel("RSI")
    ax.set_title("Relative Strength Index (RSI) by Sector\n"
                 "Red = Overbought (>70) | Blue = Neutral | Green = Oversold (<30)")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right")

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def plot_sharpe_comparison(rankings, save_path="output/sharpe_comparison.png"):
    """Bar chart comparing Sharpe ratios across sectors."""
    if not HAS_MPL:
        return

    set_style()
    fig, ax = plt.subplots(figsize=(12, 7))

    sorted_r = sorted(rankings, key=lambda x: x["sharpe"], reverse=True)
    names = [f"{r['ticker']} — {r['name']}" for r in sorted_r]
    sharpes = [r["sharpe"] for r in sorted_r]

    colors = []
    for s in sharpes:
        if s >= 2.0:
            colors.append("#1a9641")
        elif s >= 1.0:
            colors.append("#27AE60")
        elif s >= 0:
            colors.append("#F39C12")
        else:
            colors.append("#E74C3C")

    bars = ax.barh(names, sharpes, color=colors, edgecolor="white", height=0.6)

    ax.axvline(x=0, color="#333333", linewidth=0.8)
    ax.axvline(x=1.0, color="#27AE60", linewidth=1, linestyle="--", alpha=0.5, label="Good (1.0)")
    ax.axvline(x=2.0, color="#1a9641", linewidth=1, linestyle="--", alpha=0.5, label="Excellent (2.0)")

    for bar, val in zip(bars, sharpes):
        offset = 0.05 if val >= 0 else -0.05
        ha = "left" if val >= 0 else "right"
        ax.text(bar.get_width() + offset, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", ha=ha, fontsize=10)

    ax.set_xlabel("Sharpe Ratio")
    ax.set_title("Risk-Adjusted Returns by Sector (Sharpe Ratio)\n"
                 "Green ≥ 1.0 (Good) | Dark Green ≥ 2.0 (Excellent) | "
                 "Orange = Moderate | Red = Poor")
    ax.legend(loc="lower right")
    ax.invert_yaxis()

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"  Saved: {save_path}")
    plt.close()


def generate_all_charts(analysis, rankings, corr_matrix):
    """Generate all dashboard charts."""
    print("\n  Generating dashboard charts...\n")
    plot_sector_performance(rankings)
    plot_correlation_heatmap(corr_matrix)
    plot_risk_return(rankings)
    plot_rsi_signals(analysis)
    plot_sharpe_comparison(rankings)
    print("\n  All charts saved to /output/")
