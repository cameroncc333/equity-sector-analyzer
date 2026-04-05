# Equity Sector Analyzer v3.0

**Institutional-grade quantitative market dashboard — 30+ metrics across 25 equities, live.**

Built by [Cameron Camarotti](https://github.com/cameroncc333) · Founder, [All Around Services](https://allaroundservice.com)

<!-- After deploying, replace this line with: ![Dashboard Screenshot](screenshot.png) -->

---

## What This Is

A live quantitative analysis platform that computes 30+ institutional-grade metrics across 11 S&P 500 sector ETFs and 14 mega-cap stocks, with a portfolio tracker, Monte Carlo simulation, Fama-French 5-factor regression, automated signal detection, and a monthly investment thesis journal.

This isn't a class project. I built it to make real allocation decisions with real money — earnings from my home services company, [All Around Services](https://allaroundservice.com), which has completed 44 jobs across 15+ cities in metro Atlanta with $14,595 in revenue. Every investment thesis is documented, every trade has a recorded rationale, and the dashboard recalculates from live market data every time it's opened.

## Live Dashboard

🔗 **[Launch Dashboard](https://your-streamlit-url.streamlit.app)** *(update after deployment)*

---

## Features

### Market Context Bar
Live S&P 500 price, VIX fear gauge, 10-Year Treasury yield, yield curve spread (10Y minus 3-month — the Fed's preferred recession indicator), sector rotation signal (20-day and 60-day), market regime classification (Bull/Bear × Low/High Volatility), and US Dollar Index.

### Sector Analysis
All 11 S&P 500 sector ETFs ranked by customizable composite score. Adjustable ranking weights let you shift emphasis between Sharpe, Sortino, Momentum, and inverse Volatility — because quantitative models have assumptions, and those assumptions should be transparent.

### Mega-Cap Stock Analysis
14 individual equities with intra-sector rankings (e.g., "NVDA — #1 of 3 tech mega-caps"), deep-dive charts with rolling Sharpe and relative strength vs. SPY, and Fama-French 5-factor regression with t-statistics and R².

### Multi-Timeframe Comparison
30-day, 60-day, 90-day, and 1-year returns side by side with regression-based momentum acceleration detection. Includes a ranking backtest showing how top-ranked securities from 90 days ago actually performed vs. SPY.

### Sector Rotation & Risk
Offensive vs. defensive sector performance tracking, yield curve chart with inversion detection, relative strength vs. SPY for all sectors, and a combined drawdown + Value at Risk analysis.

### Head-to-Head Comparison
Select any two securities for a side-by-side metric comparison, overlaid price charts, relative strength, return distribution histograms, and correlation analysis.

### Portfolio Tracker
Input holdings with cost basis and investment thesis. Tracks allocation, gain/loss, sector concentration (with Herfindahl-Hirschman Index), portfolio-level Sharpe/Sortino/Beta/Volatility/Information Ratio, correlation to SPY, performance attribution, dividend income estimation, and a "What If" position simulator. Portfolio performance is benchmarked against SPY with alpha calculation.

### Monte Carlo Simulation
1,000 simulated forward paths over 6 months based on historical portfolio return distribution. Displays probability bands (5th/25th/50th/75th/95th percentile) for projected outcomes.

### Watchlist
Monitor securities with defined trigger conditions (e.g., "buy if RSI drops below 35"). Auto-checks whether triggers are met against live data. Shows correlation to existing portfolio for concentration risk awareness.

### Investment Thesis Journal
Monthly written market outlook with macro analysis, position rationale, and a "Lessons Learned" field for intellectual humility. Each entry saves a snapshot of market conditions, your portfolio holdings, and your watchlist at the time of writing. Exportable as JSON.

### Automated Signals
Detects oversold/overbought RSI, golden/death crosses, deep drawdowns, volume spikes, 52-week high/low proximity, and earnings date warnings. Highlights the single highest-conviction signal prominently.

---

## Quantitative Methodology

### Why Multiple Risk-Adjusted Return Measures?

No single ratio tells the full story. Each one answers a different question:

| Metric | What It Answers | How It's Calculated | When It Fails |
|--------|----------------|---------------------|---------------|
| **Sharpe** | Return per unit of total risk | (Ann. excess return / ann. σ), rf = 3.75% | Assumes normally distributed returns |
| **Sortino** | Return per unit of downside risk | Excess return / downside σ only | Ignores upside volatility entirely |
| **Treynor** | Return per unit of systematic risk | Excess return / β | Only meaningful for diversified portfolios |
| **Calmar** | Return per unit of worst-case pain | Ann. return / |max drawdown| | Sensitive to single extreme events |
| **Omega** | Probability-weighted gains vs. losses | Σ gains above threshold / Σ losses below | Less intuitive to interpret |
| **Information Ratio** | Excess return vs. benchmark per unit of tracking error | (Asset return - SPY return) / tracking error | Benchmark-dependent |
| **Jensen's Alpha** | Return beyond what beta predicts | CAPM regression intercept, annualized | Assumes CAPM is correct |

### Risk Metrics

| Metric | What It Measures |
|--------|-----------------|
| **95% Historical VaR** | "On 95% of days, you won't lose more than X%." Uses 5th percentile of actual returns — not parametric, because stock returns aren't normally distributed. |
| **Max Drawdown** | Largest peak-to-trough decline in the period |
| **Ulcer Index** | RMS of percentage drawdown series — captures both depth and duration of drawdowns |
| **Skewness** | Negative = more frequent large losses. Positive = more frequent large gains. |
| **Kurtosis** | High = fat tails, more extreme moves than a normal distribution predicts. |

### Factor Analysis

The Fama-French 5-factor model decomposes a stock's returns into exposure to five systematic factors:
- **Mkt-RF**: Market excess return (broad market beta)
- **SMB**: Small minus Big (size factor — positive = behaves like small caps)
- **HML**: High minus Low (value factor — positive = behaves like value stocks)
- **RMW**: Robust minus Weak (profitability — positive = tilts toward profitable firms)
- **CMA**: Conservative minus Aggressive (investment — positive = tilts toward conservative investors)

Factor data is sourced from the [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html). Regression uses OLS with t-statistics and R² for statistical significance.

### Other Calculations

- **RSI**: 14-day Relative Strength Index using Wilder smoothing
- **Beta**: OLS regression of daily returns vs. SPY, reported with R² and p-value
- **Momentum**: 20-day trailing price change
- **Volatility**: Annualized standard deviation of daily log returns
- **Relative Strength**: Asset price / benchmark price ratio, normalized to 100
- **Relative Volume**: Today's volume / 20-day average volume
- **Acceleration**: OLS slope of per-period returns across 30d/60d/90d timeframes
- **Sector Rotation**: Cumulative return spread between offensive sectors (Tech, Discretionary, Communication, Financials) and defensive sectors (Healthcare, Staples, Utilities, Real Estate)
- **Market Regime**: 2×2 classification using SPY vs. 200-day SMA crossed with VIX vs. 20
- **HHI**: Herfindahl-Hirschman Index for portfolio concentration (used by DOJ for antitrust, by portfolio managers for risk)
- **Monte Carlo**: 1,000 simulated paths using historical μ and σ of portfolio daily returns

---

## Tech Stack

- **Python 3.9+**
- **Streamlit** — web framework and deployment
- **yfinance** — real-time market data
- **Plotly** — interactive visualizations
- **pandas / NumPy** — data computation
- **SciPy** — statistical regressions
- **requests** — Fama-French data retrieval

## Run Locally

```bash
git clone https://github.com/cameroncc333/equity-sector-analyzer.git
cd equity-sector-analyzer
pip install -r requirements.txt
streamlit run dashboard_app.py
```

Opens at `http://localhost:8501`.

---

## Project Ecosystem

I apply quantitative methods across domains — from pricing optimization for my home services business to factor regressions on public equities:

| Repository | What It Does |
|-----------|--------------|
| **[equity-sector-analyzer](https://github.com/cameroncc333/equity-sector-analyzer)** | This dashboard — 30+ quantitative metrics, factor model, Monte Carlo, portfolio tracker |
| **[aas-pricing-model](https://github.com/cameroncc333/aas-pricing-model)** | 8-variable calculus-based pricing model with Monte Carlo simulation for All Around Services. Same simulation methodology, different domain. |
| **[fed-rate-sector-analysis](https://github.com/cameroncc333/fed-rate-sector-analysis)** | FOMC rate decision impact analysis on S&P 500 sectors — macro meets markets |
| **[AAS-Website](https://github.com/cameroncc333/AAS-Website)** | Source code for [allaroundservice.com](https://allaroundservice.com) |

---

## About

I'm Cameron Camarotti, a junior at Mill Creek High School in Hoschton, Georgia. I founded [All Around Services](https://allaroundservice.com), a multi-service home services company operating across 15+ cities in metro Atlanta — 44 completed jobs, $14,595 in revenue, 82%+ net margin, optimized by an 8-variable calculus-based pricing model.

This dashboard exists because I believe quantitative analysis should inform real decisions. I'm funding my custodial brokerage account with business earnings and using this platform to document every allocation decision — not to claim trading profitability, but to build the analytical framework I'll carry into a career in investment banking or quantitative finance.

My approach to everything: find a system, build a tool to analyze it, make better decisions with data.

---

## Changelog

| Version | What Changed |
|---------|-------------|
| **v1.0** | Basic sector ETF analysis — Sharpe, RSI, beta, momentum, correlation |
| **v2.0** | Added 14 mega-cap stocks, portfolio tracker, investment thesis journal, multi-timeframe comparison, market context header |
| **v3.0** | 30+ metrics (Sortino, Treynor, Calmar, Omega, Jensen's Alpha, Information Ratio, VaR, Ulcer Index, Skewness, Kurtosis), Fama-French 5-factor regression, Monte Carlo simulation, sector rotation with 20d/60d lookback, market regime classifier, yield curve tracking, head-to-head comparison, watchlist with triggers, ranking backtest, portfolio sector concentration (HHI), portfolio-level analytics, performance attribution, "What If" simulator, dividend tracking, automated signal engine, research snapshot export, adjustable composite weights, multi-period lookback |

---

*Not financial advice. Built for analytical and educational purposes. Data sourced from Yahoo Finance and the Kenneth French Data Library.*
