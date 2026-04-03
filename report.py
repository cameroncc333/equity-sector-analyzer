"""
Equity Sector Analyzer — Market Summary Report Generator
Cameron Camarotti | github.com/cameroncc333

Generates a plain-English market analysis report that reads like
a mini equity research note. Identifies strongest/weakest sectors,
overbought/oversold conditions, and notable patterns.
"""

import os
from datetime import datetime
from config import SECTOR_ETFS, RSI_OVERBOUGHT, RSI_OVERSOLD


def generate_report(analysis, rankings, corr_matrix):
    """
    Generate a plain-English market summary from analysis results.

    This is what makes the tool more than just a calculator —
    it INTERPRETS the data and produces actionable analysis.
    """
    report_lines = []
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    report_lines.append("=" * 70)
    report_lines.append("  EQUITY SECTOR ANALYSIS — MARKET SUMMARY REPORT")
    report_lines.append(f"  Generated: {timestamp}")
    report_lines.append("  Cameron Camarotti | github.com/cameroncc333")
    report_lines.append("=" * 70)

    # Top and bottom sectors
    if rankings:
        top = rankings[0]
        bottom = rankings[-1]

        report_lines.append(f"\n  SECTOR RANKINGS SUMMARY")
        report_lines.append(f"  {'─' * 60}")
        report_lines.append(f"")
        report_lines.append(f"  Strongest Sector: {top['ticker']} ({top['name']})")
        report_lines.append(f"    60-Day Return: {top['60d_momentum']:+.2f}%")
        report_lines.append(f"    Sharpe Ratio: {top['sharpe']:.3f}")
        report_lines.append(f"    Composite Score: {top['composite_score']:.2f}")
        report_lines.append(f"")
        report_lines.append(f"  Weakest Sector: {bottom['ticker']} ({bottom['name']})")
        report_lines.append(f"    60-Day Return: {bottom['60d_momentum']:+.2f}%")
        report_lines.append(f"    Sharpe Ratio: {bottom['sharpe']:.3f}")
        report_lines.append(f"    Composite Score: {bottom['composite_score']:.2f}")

    # Overbought / oversold signals
    overbought = []
    oversold = []
    for ticker, data in analysis.items():
        if "rsi" in data:
            if data["rsi"]["rsi"] > RSI_OVERBOUGHT:
                overbought.append((ticker, data["name"], data["rsi"]["rsi"]))
            elif data["rsi"]["rsi"] < RSI_OVERSOLD:
                oversold.append((ticker, data["name"], data["rsi"]["rsi"]))

    report_lines.append(f"\n  RSI SIGNALS")
    report_lines.append(f"  {'─' * 60}")

    if overbought:
        report_lines.append(f"\n  OVERBOUGHT (RSI > {RSI_OVERBOUGHT}) — potential pullback risk:")
        for ticker, name, val in overbought:
            report_lines.append(f"    {ticker} ({name}): RSI {val:.1f}")
    else:
        report_lines.append(f"\n  No sectors currently overbought (RSI > {RSI_OVERBOUGHT})")

    if oversold:
        report_lines.append(f"\n  OVERSOLD (RSI < {RSI_OVERSOLD}) — potential bounce opportunity:")
        for ticker, name, val in oversold:
            report_lines.append(f"    {ticker} ({name}): RSI {val:.1f}")
    else:
        report_lines.append(f"  No sectors currently oversold (RSI < {RSI_OVERSOLD})")

    # Moving average signals
    golden_crosses = []
    death_crosses = []
    for ticker, data in analysis.items():
        if "moving_averages" in data:
            ma = data["moving_averages"]
            if "GOLDEN" in ma["signal"]:
                golden_crosses.append((ticker, data["name"]))
            else:
                death_crosses.append((ticker, data["name"]))

    report_lines.append(f"\n  TREND SIGNALS (Moving Average Crossovers)")
    report_lines.append(f"  {'─' * 60}")

    if golden_crosses:
        report_lines.append(f"\n  BULLISH — Golden Cross (50-day MA > 200-day MA):")
        for ticker, name in golden_crosses:
            report_lines.append(f"    {ticker} ({name})")

    if death_crosses:
        report_lines.append(f"\n  BEARISH — Death Cross (50-day MA < 200-day MA):")
        for ticker, name in death_crosses:
            report_lines.append(f"    {ticker} ({name})")

    # Risk analysis
    report_lines.append(f"\n  RISK ANALYSIS")
    report_lines.append(f"  {'─' * 60}")

    high_beta = [(t, d["name"], d["beta"]["beta"]) for t, d in analysis.items()
                 if "beta" in d and d["beta"]["beta"] > 1.2]
    low_beta = [(t, d["name"], d["beta"]["beta"]) for t, d in analysis.items()
                if "beta" in d and d["beta"]["beta"] < 0.8]

    if high_beta:
        report_lines.append(f"\n  HIGH BETA sectors (amplify market moves, β > 1.2):")
        for ticker, name, b in sorted(high_beta, key=lambda x: x[2], reverse=True):
            report_lines.append(f"    {ticker} ({name}): β = {b:.3f}")

    if low_beta:
        report_lines.append(f"\n  DEFENSIVE sectors (dampen market moves, β < 0.8):")
        for ticker, name, b in sorted(low_beta, key=lambda x: x[2]):
            report_lines.append(f"    {ticker} ({name}): β = {b:.3f}")

    # Correlation insights
    report_lines.append(f"\n  DIVERSIFICATION ANALYSIS")
    report_lines.append(f"  {'─' * 60}")

    tickers = list(corr_matrix.columns)
    pairs = []
    for i in range(len(tickers)):
        for j in range(i + 1, len(tickers)):
            pairs.append((tickers[i], tickers[j], corr_matrix.iloc[i, j]))

    pairs.sort(key=lambda x: x[2])
    lowest = pairs[:3]
    highest = pairs[-3:]

    report_lines.append(f"\n  Best diversification pairs (lowest correlation):")
    for t1, t2, corr in lowest:
        n1 = SECTOR_ETFS.get(t1, t1)
        n2 = SECTOR_ETFS.get(t2, t2)
        report_lines.append(f"    {t1}/{t2} ({n1}/{n2}): {corr:.3f}")

    report_lines.append(f"\n  Highest correlation pairs (move together):")
    for t1, t2, corr in reversed(highest):
        n1 = SECTOR_ETFS.get(t1, t1)
        n2 = SECTOR_ETFS.get(t2, t2)
        report_lines.append(f"    {t1}/{t2} ({n1}/{n2}): {corr:.3f}")

    # Full rankings table
    report_lines.append(f"\n  COMPLETE SECTOR RANKINGS")
    report_lines.append(f"  {'─' * 60}")
    report_lines.append(f"  {'Rank':<6}{'Ticker':<7}{'Sector':<28}{'Score':<8}{'60d Ret':<10}{'Sharpe':<8}")
    report_lines.append(f"  {'─' * 60}")

    for r in rankings:
        report_lines.append(
            f"  {r['rank']:<6}{r['ticker']:<7}{r['name']:<28}"
            f"{r['composite_score']:<8.2f}{r['60d_momentum']:+<10.2f}{r['sharpe']:<8.3f}"
        )

    report_lines.append(f"\n{'=' * 70}")
    report_lines.append(f"  DISCLAIMER: This analysis is for educational and informational")
    report_lines.append(f"  purposes only. It is not investment advice. Past performance")
    report_lines.append(f"  does not guarantee future results.")
    report_lines.append(f"{'=' * 70}")

    report_text = "\n".join(report_lines)

    # Save to file
    os.makedirs("output", exist_ok=True)
    filepath = "output/market_report.txt"
    with open(filepath, "w") as f:
        f.write(report_text)
    print(f"  Report saved: {filepath}")

    return report_text
