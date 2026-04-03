# Equity Sector Analyzer — Quantitative Market Analysis Platform

A Python-based equity analysis platform that pulls live S&P 500 sector data, calculates institutional-grade quantitative metrics, and generates visual dashboard reports. Built to apply the same analytical framework used by equity research analysts and portfolio managers to real market data.

## Motivation

I founded [All Around Services](https://allaroundservice.com) in January 2025 and built an [8-variable pricing model](https://github.com/cameroncc333/aas-pricing-model) that uses calculus-based optimization to price every job mathematically. That experience taught me that data-driven decision-making produces better results than intuition — my business runs at a 93.7% job-level margin across 44 jobs because the math works.

This project applies the same principle to financial markets. Instead of asking "what should I charge for this job?", I'm asking "which market sectors offer the best risk-adjusted returns, and how are they behaving relative to each other?" The metrics I calculate here — Sharpe ratio, beta, momentum, volatility, correlation — are the same ones used by equity research teams at the investment banks where I want to build my career.

## What It Does

### 1. Live Market Data Engine
Connects to Yahoo Finance API and pulls real, current market data for all 11 S&P 500 sector ETFs:

| Ticker | Sector |
|--------|--------|
| XLK | Technology |
| XLF | Financials |
| XLE | Energy |
| XLV | Healthcare |
| XLY | Consumer Discretionary |
| XLP | Consumer Staples |
| XLI | Industrials |
| XLB | Materials |
| XLRE | Real Estate |
| XLU | Utilities |
| XLC | Communication Services |
| SPY | S&P 500 (benchmark) |

### 2. Quantitative Metrics Engine
Calculates the following for each sector — the same metrics equity research analysts use daily:

**Momentum & Trend**
- **50-Day & 200-Day Moving Averages** — Golden cross (bullish) and death cross (bearish) signals
- **Rate of Change (Momentum)** — Speed of price movement over 30 and 90 days. This is a derivative — the rate of change of price with respect to time, the same concept from AP Calculus applied to stock prices
- **Relative Strength Index (RSI)** — Oscillator between 0-100. Above 70 = overbought, below 30 = oversold. Every trading desk monitors this

**Risk & Volatility**
- **Annualized Volatility** — Standard deviation of daily returns, annualized. Measures how much a sector's price swings. Higher = riskier
- **Beta** — Sensitivity to overall market movements. Beta > 1.0 = more volatile than the market. Beta < 1.0 = more stable. Used in the Capital Asset Pricing Model (CAPM)
- **Maximum Drawdown** — Largest peak-to-trough decline. Measures worst-case loss

**Risk-Adjusted Returns**
- **Sharpe Ratio** — The most important metric in portfolio management. Measures return per unit of risk: (Return - Risk-Free Rate) / Volatility. Above 1.0 = good, above 2.0 = excellent. William Sharpe won the Nobel Prize for this
- **Sortino Ratio** — Like Sharpe but only penalizes downside volatility, not upside. A more refined risk-adjusted measure

**Cross-Sector Analysis**
- **Correlation Matrix** — How sectors move relative to each other. High correlation = they move together. Low correlation = diversification opportunity. Foundation of Modern Portfolio Theory (Markowitz, Nobel Prize 1990)
- **Sector Rankings** — Comprehensive ranking across all metrics with composite scoring

### 3. Visual Dashboard
Generates publication-quality charts:
- Sector performance comparison (30/60/90-day returns)
- Correlation heatmap across all 11 sectors
- Volatility comparison bar chart
- RSI gauge showing overbought/oversold conditions
- Moving average trend signals
- Risk-return scatter plot (return vs volatility for each sector)
- Composite ranking summary

### 4. Market Summary Report
Outputs a plain-English analysis that reads like a mini equity research note, identifying the strongest and weakest sectors, overbought/oversold conditions, and notable correlation shifts.

## Project Structure

```
equity-sector-analyzer/
│
├── README.md                # This file
├── config.py                # Configuration, tickers, parameters
├── data_engine.py           # Live data collection from Yahoo Finance
├── metrics.py               # Quantitative analysis calculations
├── dashboard.py             # Visualization and chart generation
├── report.py                # Plain-English market summary generator
├── run_analysis.py          # Main script — runs everything
└── output/
    ├── sector_performance.png
    ├── correlation_heatmap.png
    ├── volatility_comparison.png
    ├── risk_return_scatter.png
    ├── rsi_signals.png
    ├── rankings.png
    └── market_report.txt
```

## How to Run

```bash
# Clone the repository
git clone https://github.com/cameroncc333/equity-sector-analyzer.git
cd equity-sector-analyzer

# Install dependencies
pip install yfinance pandas numpy matplotlib seaborn scipy

# Run the full analysis
python run_analysis.py

# Output charts saved to /output/
# Market summary printed to console and saved to output/market_report.txt
```

## Connection to Academics & Career Goals

This project applies concepts from multiple disciplines:

- **AP Calculus** — Rate of change (momentum), optimization, derivatives
- **AP Statistics / Data Analysis** — Standard deviation, correlation, probability distributions
- **AP Macroeconomics** — Sector behavior, monetary policy impacts, market cycles
- **AP Computer Science** — Python programming, API integration, data structures

The metrics calculated here — Sharpe ratio, beta, RSI, correlation matrices — are the foundational tools of equity research and portfolio management. Building this platform at 17 is preparation for the quantitative finance career I'm pursuing.

## Part of a Broader Portfolio

This project connects to three other quantitative analysis projects:

- **[AAS Pricing Model](https://github.com/cameroncc333/aas-pricing-model)** — Applied calculus to business pricing optimization
- **[Fed Rate Sector Analysis](https://github.com/cameroncc333/fed-rate-sector-analysis)** — Macroeconomic policy impact on equity sectors
- **[AAS Website](https://github.com/cameroncc333/AAS-Website)** — Source code for allaroundservice.com

The through-line: applying mathematical and computational methods to real-world economic questions — from pricing a pressure washing job to analyzing how Federal Reserve policy ripples through the stock market.

## About

**Cameron Camarotti**
- Founder, [All Around Services](https://allaroundservice.com) | [Facebook](https://www.facebook.com/profile.php?id=61588386760982)
- Junior at Mill Creek High School (Class of 2027)
- 4.1 GPA | 12 AP Courses
- Varsity Football — All-Region Honorable Mention
