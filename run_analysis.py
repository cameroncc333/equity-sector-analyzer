"""
Equity Sector Analyzer — Main Analysis Runner
Cameron Camarotti | github.com/cameroncc333

Run this script to execute the full analysis pipeline:
1. Download live market data for all S&P 500 sectors
2. Calculate quantitative metrics (momentum, volatility, Sharpe, RSI, beta, correlation)
3. Generate composite sector rankings
4. Create visual dashboard charts
5. Output plain-English market summary report

Usage:
    python run_analysis.py
"""

import os
import sys
from datetime import datetime

from config import SECTOR_ETFS
from data_engine import download_all_sectors, calculate_daily_returns, save_data
from metrics import (
    full_sector_analysis, composite_ranking, correlation_matrix,
    print_full_report
)
from dashboard import generate_all_charts
from report import generate_report


def main():
    print()
    print("=" * 70)
    print("  EQUITY SECTOR ANALYZER")
    print("  Quantitative Market Analysis Platform")
    print(f"  {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("=" * 70)
    print("  Cameron Camarotti | github.com/cameroncc333")
    print("  Analyzing all 11 S&P 500 sectors + SPY benchmark")
    print("=" * 70)

    # Step 1: Download data
    print("\n  [1/5] Downloading live market data...")
    prices = download_all_sectors()

    if prices is None:
        print("\n  ERROR: Could not download market data.")
        print("  Make sure yfinance is installed: pip install yfinance")
        print("  Make sure you have internet connection.")
        sys.exit(1)

    save_data(prices)

    # Step 2: Calculate returns
    print("\n  [2/5] Calculating daily returns...")
    returns = calculate_daily_returns(prices)
    print(f"  Computed returns for {len(returns)} trading days")

    # Step 3: Run quantitative analysis
    print("\n  [3/5] Running quantitative analysis...")
    print("  Computing: momentum, RSI, volatility, beta, Sharpe,")
    print("  Sortino, max drawdown, moving averages, correlations...")
    analysis = full_sector_analysis(prices, returns)
    rankings = composite_ranking(prices, returns)
    corr = correlation_matrix(returns)
    print(f"  Analysis complete for {len(analysis)} sectors")

    # Step 4: Print full report
    print("\n  [4/5] Generating reports...")
    print_full_report(analysis, rankings, corr)

    # Step 5: Generate charts and summary
    generate_all_charts(analysis, rankings, corr)
    report_text = generate_report(analysis, rankings, corr)

    print("\n" + report_text)

    print("\n" + "=" * 70)
    print("  ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"  Charts saved to: output/")
    print(f"  Report saved to: output/market_report.txt")
    print(f"  Price data saved to: output/sector_prices.csv")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
