# Equity Sector Analyzer — Market Intelligence Dashboard

> A live quantitative analysis platform covering all 11 S&P 500 sector ETFs and 12 mega-cap stocks. Calculates institutional-grade metrics — Sharpe ratio, beta, RSI, momentum, max drawdown, correlation — and renders them in an interactive Streamlit dashboard with real-time market data.

**Built by Cameron Camarotti** · [GitHub](https://github.com/cameroncc333) · [All Around Services](https://allaroundservice.com)

---

## Live Dashboard

> 🚀 **[Launch Dashboard →](YOUR_STREAMLIT_URL_HERE)**  
> Pulls live data from Yahoo Finance. Refreshes hourly.

---

## What It Does

The dashboard has three tabs:

**🏭 Sector Analysis**
Ranks all 11 S&P 500 sector ETFs by momentum, Sharpe ratio, RSI, volatility, beta, and max drawdown. Includes a correlation heatmap, risk/return scatter, and individual sector deep-dive with price history and moving averages.

**📈 Mega-Cap Stocks**
Same institutional metrics applied to 12 individual stocks: AAPL, MSFT, NVDA, AMZN, META, GOOGL, TSLA, JPM, GS, BRK-B, V, XOM. Multi-period return comparison (30/60/90-day) and individual price charts.

**🔗 Cross-Asset View**
Sectors and mega-caps plotted together on a single Sharpe/volatility scatter. Combined top-10 ranking by risk-adjusted return. Mega-cap correlation matrix.

**Live macro bar at the top of every page:**
- S&P 500 (SPY) — live price and daily change
- VIX (fear index)
- 10-Year Treasury yield
- Fed funds rate (current: 3.50–3.75%, last action: hold Mar 18, 2026)
- Risk-free rate used in all Sharpe calculations: 3.75%

---

## Metrics Calculated

| Metric | What It Measures |
|--------|-----------------|
| **Sharpe Ratio** | Return per unit of total risk. `(Return − Risk-Free Rate) / Volatility`. Above 1.0 = strong. Nobel Prize metric (William Sharpe, 1990). Risk-free rate updated to match current Fed funds rate. |
| **Beta** | Sensitivity to S&P 500. >1.0 = amplifies market moves. <1.0 = defensive. Core input to CAPM. |
| **RSI** | Momentum oscillator (0–100). >70 = overbought, <30 = oversold. Standard signal on every institutional trading desk. |
| **Momentum** | Rate of price change over 30/60/90 days. Mathematically: `(P_t − P_{t−n}) / P_{t−n}`. The same concept as a derivative from calculus applied to price time-series. |
| **Annualized Volatility** | `σ_daily × √252`. Standard deviation of daily returns scaled to annual. Higher = more risk. |
| **Max Drawdown** | Largest peak-to-trough decline over the lookback period. Worst-case loss measure. |
| **Moving Averages** | 50-day and 200-day MAs. Golden Cross (50 > 200) = bullish trend. Death Cross (50 < 200) = bearish. |
| **Correlation Matrix** | Pairwise correlation of daily returns across all sectors/stocks. Foundation of Markowitz Modern Portfolio Theory (Nobel Prize 1990). Low correlation = diversification. |

---

## Motivation

I founded [All Around Services](https://allaroundservice.com) in January 2025 and built an 8-variable calculus-based pricing model to price every job mathematically — fuel cost, labor hours, route distance, equipment depreciation, seasonal demand coefficient, and three other variables optimized via partial derivatives. The business runs at a 93.7% job-level margin across 44 completed jobs.

That experience taught me that the same quantitative framework applies everywhere: whether you're pricing a moving job or evaluating a sector ETF, the question is always *which variables drive outcomes, and how do you measure them rigorously?*

This dashboard applies that framework to financial markets. The metrics I calculate here — Sharpe ratio, beta, correlation matrices — are the exact tools used by equity research teams at the firms where I want to build my career.

---

## Investment Thesis Log

I use this dashboard to inform allocation decisions in my custodial brokerage account. Each month I document my sector outlook and the reasoning behind any trades — not to chase returns, but to build a documented analytical process.

| Date | Thesis | Key Signals Used |
|------|--------|-----------------|
| *Updated monthly — see dashboard Investment Thesis tab* | | |

---

## Project Structure

```
equity-sector-analyzer/
│
├── README.md              # This file
├── dashboard_app.py       # Full Streamlit dashboard (run this)
└── requirements.txt       # Dependencies
```

---

## How to Run Locally

```bash
# Clone
git clone https://github.com/cameroncc333/equity-sector-analyzer.git
cd equity-sector-analyzer

# Install dependencies
pip install streamlit yfinance pandas numpy plotly

# Launch
streamlit run dashboard_app.py
```

Dashboard opens at `http://localhost:8501`

---

## Dependencies

```
streamlit
yfinance
pandas
numpy
plotly
```

---

## Connection to Other Projects

This is part of a four-project quantitative portfolio:

| Project | What It Does |
|---------|-------------|
| [equity-sector-analyzer](https://github.com/cameroncc333/equity-sector-analyzer) | This project — live sector + mega-cap analysis dashboard |
| [aas-pricing-model](https://github.com/cameroncc333/aas-pricing-model) | 8-variable calculus pricing model for AAS, Monte Carlo simulation |
| [fed-rate-sector-analysis](https://github.com/cameroncc333/fed-rate-sector-analysis) | FOMC rate decision impact on S&P 500 sectors (2015–2026) |
| [AAS-Website](https://github.com/cameroncc333/AAS-Website) | Source code for allaroundservice.com |

**The through-line:** applying mathematical and computational methods to real economic questions — from pricing a pressure washing job to analyzing how Federal Reserve policy ripples through equity markets.

---

## About

Cameron Camarotti — Junior, Mill Creek High School (Class of 2027)  
Founder, [All Around Services](https://allaroundservice.com) · Hoschton, Georgia  
Career goal: investment banking / quantitative finance

*For educational and informational purposes only. Not investment advice.*
