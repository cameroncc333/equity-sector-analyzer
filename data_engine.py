"""
Equity Sector Analyzer — Data Engine
Cameron Camarotti | github.com/cameroncc333

Pulls live and historical market data for S&P 500 sector ETFs
using the Yahoo Finance API.
"""

import pandas as pd
from datetime import datetime, timedelta
import os

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

from config import SECTOR_ETFS, BENCHMARK, LOOKBACK_YEARS


def download_all_sectors(lookback_years=LOOKBACK_YEARS):
    """
    Download historical daily prices for all sector ETFs plus benchmark.

    Returns:
        DataFrame with dates as index, tickers as columns (closing prices)
    """
    if not HAS_YFINANCE:
        print("  ERROR: yfinance not installed. Run: pip install yfinance")
        return None

    end_date = datetime.today()
    start_date = end_date - timedelta(days=lookback_years * 365)

    all_tickers = list(SECTOR_ETFS.keys()) + [BENCHMARK]

    print(f"  Downloading {len(all_tickers)} tickers...")
    print(f"  Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    data = yf.download(all_tickers, start=start_date, end=end_date, progress=False)

    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data

    prices = prices.dropna(how="all")

    print(f"  Downloaded {len(prices)} trading days")
    print(f"  Sectors: {len(prices.columns)} tickers")

    return prices


def get_current_prices(prices):
    """Get the most recent closing price for each sector."""
    latest = prices.iloc[-1]
    result = {}
    for ticker in SECTOR_ETFS:
        if ticker in latest.index and pd.notna(latest[ticker]):
            result[ticker] = round(latest[ticker], 2)
    return result


def calculate_daily_returns(prices):
    """
    Calculate daily percentage returns from price data.

    Daily return = (Price_today - Price_yesterday) / Price_yesterday

    This is the foundation for virtually every metric we calculate.
    Volatility, Sharpe ratio, beta, correlation — all built from
    the distribution of daily returns.
    """
    returns = prices.pct_change().dropna()
    return returns


def save_data(prices, filepath="output/sector_prices.csv"):
    """Save price data to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    prices.to_csv(filepath)
    print(f"  Saved: {filepath}")


if __name__ == "__main__":
    print("\n  EQUITY SECTOR ANALYZER — DATA ENGINE")
    print("  Cameron Camarotti | github.com/cameroncc333\n")

    prices = download_all_sectors()

    if prices is not None:
        current = get_current_prices(prices)
        print("\n  Current Sector Prices:")
        for ticker, price in current.items():
            print(f"    {ticker:5s} ({SECTOR_ETFS[ticker]:28s}): ${price:.2f}")

        save_data(prices)
        print("\n  Data engine ready.")
