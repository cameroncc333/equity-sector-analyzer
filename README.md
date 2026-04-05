# Equity Sector Analyzer

**A live quantitative dashboard for analyzing S&P 500 sectors and mega-cap equities.**

Built by [Cameron Camarotti](https://github.com/cameroncc333) · Founder, [All Around Services](https://allaroundserviceatl.com)

<!-- After deploying, replace this line with: ![Dashboard Screenshot](screenshot.png) -->

🔗 **[Launch Live Dashboard](https://your-streamlit-url.streamlit.app)**

---

## Why This Exists

I run a home services company ([All Around Services](https://allaroundserviceatl.com)) that has generated $14,595 across 44 jobs in metro Atlanta. When I decided to invest a portion of those earnings through a custodial brokerage account, I didn't want to pick stocks based on Reddit threads or gut feeling. I wanted a framework for making allocation decisions — and more importantly, a system for documenting *why* I made each decision so I could learn from the outcomes.

This dashboard is that framework. It pulls live market data, computes the metrics that matter, and gives me a place to record my reasoning each month. The goal isn't to beat Wall Street. It's to develop the analytical discipline now, with small money, so the framework is already built when the stakes get higher.

---

## Design Decisions & Why I Made Them

### Why so many risk-adjusted return metrics?

Sharpe ratio is the standard, but it has a well-known flaw: it penalizes upside volatility the same as downside volatility. If a stock shoots up 15% in a day, Sharpe treats that as equally "risky" as a 15% drop. That's mathematically clean but economically wrong — no investor complains about upside surprise.

That's why I include **Sortino**, which only penalizes downside deviation. But Sortino has its own blind spot: it ignores how much systematic risk you're taking. A high-Sortino stock might just be a leveraged bet on the market. So I added **Treynor** (return per unit of beta) and **Jensen's Alpha** (the CAPM regression intercept — what return you're getting *beyond* what your beta exposure predicts).

**Calmar** answers a different question entirely: how much return am I getting relative to the worst drawdown? A stock with a 1.5 Sharpe but a -40% max drawdown tells a different story than one with the same Sharpe and a -12% drawdown.

**Omega** captures what all the others miss: the full shape of the return distribution, including fat tails and skewness. It's the ratio of probability-weighted gains above a threshold to losses below it — no normality assumption required.

I include all six because each one exposes something the others hide. If a stock ranks well on all six, that's a strong signal. If it ranks well on Sharpe but poorly on Calmar, that tells me the returns are real but the drawdown risk is severe.

### Why Ulcer Index instead of just standard deviation?

Standard deviation treats a stock that drops 10% for one day the same as one that drops 10% and stays there for three months. The Ulcer Index (root mean square of the drawdown percentage series) captures both the *depth* and the *duration* of pain. A stock that recovers quickly has a low Ulcer Index even if it had a sharp drawdown. A stock that bleeds slowly for months has a high one. For someone making allocation decisions with limited capital, duration of drawdown matters as much as magnitude.

### Why Historical VaR instead of Parametric?

Stock returns aren't normally distributed. They exhibit negative skewness (large losses are more frequent than a bell curve predicts) and excess kurtosis (extreme moves happen more often than they "should"). A parametric VaR that assumes normality would systematically underestimate tail risk. Historical VaR — just taking the 5th percentile of actual daily returns — makes no distributional assumption. It uses what actually happened. That's a more honest estimate of downside exposure.

I also report skewness and kurtosis directly so you can see *how far* from normal each stock's distribution actually is.

### Why Fama-French 5-Factor?

Single-factor models (CAPM) attribute all excess return to market beta. But decades of academic research show that size, value, profitability, and investment aggressiveness also explain returns systematically. A stock might look like it has high alpha under CAPM, but a 5-factor regression reveals that the "alpha" was really just exposure to the value factor or the profitability factor.

I pull daily factor return data from the [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) at Dartmouth and run OLS regression for the selected stock. The output includes:

- **Factor loadings** — how much the stock's returns are driven by each factor
- **t-statistics** — whether each loading is statistically significant (|t| > 1.96 at 95% confidence)
- **R²** — how much of the stock's return variation the five factors explain

If R² is 0.85, the five factors explain 85% of the stock's daily returns. The remaining 15% is idiosyncratic — that's where genuine stock-specific alpha lives, if it exists at all.

### Why Monte Carlo for portfolio projection?

I use the same simulation methodology here that I use in my [AAS pricing model](https://github.com/cameroncc333/aas-pricing-model) — different domain, same mathematical framework. The simulation draws 1,000 random return paths from the historical distribution of portfolio daily returns (using the actual mean and standard deviation, not a parametric assumption). The fan chart shows 5th/25th/50th/75th/95th percentile bands.

**Known limitation:** This assumes future returns are drawn from the same distribution as past returns, which is a strong assumption. It doesn't account for regime changes, correlation breakdowns during crises, or structural shifts in the market. I treat the output as a *range of plausible outcomes* for planning purposes, not as a prediction.

### Why adjustable composite weights?

The default ranking weights Sharpe, Sortino, Momentum, and inverse Volatility equally at 25% each. But the right weighting depends on the market environment. In a trending bull market, you might want to overweight momentum. In a choppy, range-bound market, you might care more about low volatility and downside protection (Sortino). The sliders make the model's assumptions explicit and adjustable rather than hidden.

### Why sector rotation tracking?

Capital rotates between offensive sectors (Technology, Consumer Discretionary, Communication Services, Financials) and defensive sectors (Healthcare, Consumer Staples, Utilities, Real Estate) based on risk appetite. When the 20-day cumulative return spread between offensive and defensive sectors turns negative, money is flowing into safety — that's historically correlated with increased volatility and weaker broad market performance. I track both 20-day and 60-day lookbacks because the shorter window catches early signals while the longer window filters out noise.

---

## What It Computes

**Per security (25 total — 11 sector ETFs, 14 mega-cap stocks):**

Risk-adjusted returns: Sharpe, Sortino, Treynor, Calmar, Omega, Jensen's Alpha, Information Ratio. Risk metrics: 95% Historical VaR, Max Drawdown, Current Drawdown, Ulcer Index, Skewness, Kurtosis. Technical: RSI (14-day Wilder), Beta (with R² and p-value), 20-day Momentum, Annualized Volatility, 50/200-day SMA with crossover detection, Relative Volume. Returns: 30d, 60d, 90d, 1y, plus regression-based acceleration. Additional: 52-week high/low, distance from 52-week high, dividend yield, Fama-French 5-factor loadings.

**Portfolio-level:** Sharpe, Sortino, Beta, Volatility, Information Ratio, correlation to SPY, Herfindahl-Hirschman Index for concentration, performance attribution, Monte Carlo projection, dividend income estimate, alpha vs. SPY benchmark.

**Market-level:** S&P 500 (SPY), VIX, 10-Year Treasury yield, yield curve spread (10Y minus 3-month), US Dollar Index, sector rotation signal (20d and 60d), market regime classification (Bull/Bear × Low/High Volatility).

---

## Features

- **Automated signal engine** — flags oversold/overbought RSI, golden/death crosses, deep drawdowns, volume spikes, 52-week proximity, earnings date warnings
- **Head-to-head comparison** — any two securities side by side with every metric, overlaid price charts, relative strength, return distributions, correlation
- **Portfolio tracker** — holdings with cost basis, thesis per position, sector concentration analysis, benchmark comparison, "what if" simulator for testing positions before committing
- **Watchlist** — monitor securities with defined trigger conditions that auto-check against live data
- **Thesis journal** — monthly written analysis with lessons learned, portfolio and market snapshots saved per entry
- **Research snapshot export** — downloadable text summary of current dashboard state
- **Adjustable ranking weights** and **multi-period lookback** (3 months to 2 years)

---

## Tech Stack

Python 3.9+, Streamlit, Plotly, pandas, NumPy, SciPy, yfinance, requests. Factor data from Kenneth French Data Library. Deployed on Streamlit Community Cloud.

## Run Locally

```bash
git clone https://github.com/cameroncc333/equity-sector-analyzer.git
cd equity-sector-analyzer
pip install -r requirements.txt
streamlit run dashboard_app.py
```

---

## Project Ecosystem

This dashboard is part of a broader set of quantitative tools I've built:

**[aas-pricing-model](https://github.com/cameroncc333/aas-pricing-model)** — An 8-variable cost function for my home services company using partial derivative optimization. Variables: fuel cost, route distance, labor hours, crew fatigue factor (φ), equipment depreciation, materials cost, disposal fees, seasonal demand coefficient (κ). Includes Monte Carlo simulation (10,000 scenarios) and sensitivity analysis, back-tested against all 44 real jobs. The crew fatigue factor was the key insight — by computing ∂Cost/∂φ relative to route distance, I found the threshold where dispatching a second crew becomes more profitable than overtime for the first. Same Monte Carlo methodology as this dashboard, applied to operations instead of markets.

**[fed-rate-sector-analysis](https://github.com/cameroncc333/fed-rate-sector-analysis)** — Analysis of how FOMC rate decisions propagate through S&P 500 sectors across 30/60/90-day windows. Tracks the 2025 cutting cycle and 2026 holds.

**[AAS-Website](https://github.com/cameroncc333/AAS-Website)** — Source for [allaroundservice.com](https://allaroundserviceatl.com). Netlify hosting, Cloudflare DNS.

---

## About

I'm Cameron Camarotti, a junior at Mill Creek High School in Hoschton, Georgia. I founded [All Around Services](https://allaroundserviceatl.com), a home services company operating across 15+ cities in metro Atlanta.

I'm not trying to claim I've built a Bloomberg Terminal. I built a tool that helps me make better-informed decisions with real money, and — more importantly — forces me to write down *why* I'm making each decision so I can evaluate my reasoning over time. The analytical framework matters more than the returns.

My approach: find a system, understand why it behaves the way it does, build a tool to make better decisions within it.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | Jan 2025 | Sector ETF analysis — Sharpe, RSI, beta, momentum, correlation |
| v2.0 | Mar 2025 | Added mega-cap stocks, portfolio tracker, thesis journal, multi-timeframe comparison |
| v3.0 | Apr 2025 | 30+ metrics, Fama-French 5-factor, Monte Carlo, sector rotation, yield curve, regime detection, head-to-head comparison, watchlist, backtest, HHI concentration, portfolio analytics, automated signals, adjustable weights |

---

*Not financial advice. Built for analytical and educational purposes. Data from Yahoo Finance and the Kenneth French Data Library.*
