"""
Equity Sector Analyzer — Configuration
Cameron Camarotti | github.com/cameroncc333
"""

# S&P 500 Sector ETFs
SECTOR_ETFS = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Healthcare",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLI": "Industrials",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
    "XLC": "Communication Services",
}

BENCHMARK = "SPY"  # S&P 500 ETF as market benchmark
RISK_FREE_RATE = 0.045  # Current ~4.5% (10-year Treasury approximation)

# Analysis parameters
LOOKBACK_YEARS = 2  # Years of historical data to pull
SHORT_MA = 50  # Short-term moving average (days)
LONG_MA = 200  # Long-term moving average (days)
RSI_PERIOD = 14  # RSI calculation period
MOMENTUM_WINDOWS = [30, 60, 90]  # Return calculation windows (days)
TRADING_DAYS_PER_YEAR = 252

# RSI thresholds
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Sharpe ratio benchmarks
SHARPE_EXCELLENT = 2.0
SHARPE_GOOD = 1.0
SHARPE_POOR = 0.0
