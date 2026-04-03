"""
Equity Sector Analyzer — Quantitative Metrics Engine
Cameron Camarotti | github.com/cameroncc333

Calculates institutional-grade quantitative metrics for each sector:
- Momentum & trend signals (moving averages, RSI, rate of change)
- Risk metrics (volatility, beta, max drawdown)
- Risk-adjusted returns (Sharpe ratio, Sortino ratio)
- Cross-sector analysis (correlation matrix, rankings)
"""

import numpy as np
import pandas as pd
from config import (
    SECTOR_ETFS, BENCHMARK, RISK_FREE_RATE, SHORT_MA, LONG_MA,
    RSI_PERIOD, MOMENTUM_WINDOWS, TRADING_DAYS_PER_YEAR,
    RSI_OVERBOUGHT, RSI_OVERSOLD
)
from data_engine import calculate_daily_returns


def moving_averages(prices, ticker):
    """
    Calculate 50-day and 200-day simple moving averages.

    When the 50-day MA crosses ABOVE the 200-day MA = "Golden Cross" (bullish)
    When the 50-day MA crosses BELOW the 200-day MA = "Death Cross" (bearish)

    These are the most widely watched technical signals on Wall Street.
    """
    if ticker not in prices.columns:
        return None

    series = prices[ticker].dropna()
    ma_short = series.rolling(window=SHORT_MA).mean()
    ma_long = series.rolling(window=LONG_MA).mean()

    current_price = series.iloc[-1]
    current_short = ma_short.iloc[-1]
    current_long = ma_long.iloc[-1]

    if current_short > current_long:
        signal = "GOLDEN CROSS (Bullish)"
    else:
        signal = "DEATH CROSS (Bearish)"

    above_50 = current_price > current_short
    above_200 = current_price > current_long

    return {
        "current_price": round(current_price, 2),
        "ma_50": round(current_short, 2),
        "ma_200": round(current_long, 2),
        "signal": signal,
        "above_50ma": above_50,
        "above_200ma": above_200,
    }


def momentum(prices, ticker, windows=MOMENTUM_WINDOWS):
    """
    Calculate rate of change (momentum) over multiple windows.

    Momentum = (Price_now - Price_n_days_ago) / Price_n_days_ago × 100

    This is fundamentally a derivative — the rate of change of price
    with respect to time. Same concept from AP Calculus, applied to
    stock prices instead of mathematical functions.
    """
    if ticker not in prices.columns:
        return None

    series = prices[ticker].dropna()
    current = series.iloc[-1]
    results = {}

    for w in windows:
        if len(series) > w:
            past_price = series.iloc[-w - 1]
            pct_change = ((current - past_price) / past_price) * 100
            results[f"{w}d_return"] = round(pct_change, 2)
        else:
            results[f"{w}d_return"] = None

    return results


def rsi(prices, ticker, period=RSI_PERIOD):
    """
    Calculate Relative Strength Index (RSI).

    RSI = 100 - (100 / (1 + RS))
    Where RS = Average Gain / Average Loss over the period

    RSI > 70 = Overbought (price may have risen too fast, pullback possible)
    RSI < 30 = Oversold (price may have fallen too fast, bounce possible)

    Every institutional trading desk monitors RSI. It measures whether
    buying or selling pressure has been dominant recently.
    """
    if ticker not in prices.columns:
        return None

    series = prices[ticker].dropna()
    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi_values = 100 - (100 / (1 + rs))

    current_rsi = rsi_values.iloc[-1]

    if current_rsi > RSI_OVERBOUGHT:
        condition = "OVERBOUGHT"
    elif current_rsi < RSI_OVERSOLD:
        condition = "OVERSOLD"
    else:
        condition = "NEUTRAL"

    return {
        "rsi": round(current_rsi, 1),
        "condition": condition,
    }


def volatility(returns, ticker):
    """
    Calculate annualized volatility (standard deviation of returns).

    Volatility = StdDev(daily returns) × √252

    We multiply by √252 (trading days per year) to annualize.
    This is the standard measure of risk in finance.

    Higher volatility = larger price swings = more risk.
    """
    if ticker not in returns.columns:
        return None

    daily_vol = returns[ticker].std()
    annual_vol = daily_vol * np.sqrt(TRADING_DAYS_PER_YEAR)

    return {
        "daily_volatility": round(daily_vol * 100, 3),
        "annualized_volatility": round(annual_vol * 100, 2),
    }


def beta(returns, ticker, benchmark=BENCHMARK):
    """
    Calculate beta — sensitivity to market movements.

    Beta = Covariance(sector, market) / Variance(market)

    Beta = 1.0: Sector moves exactly with the market
    Beta > 1.0: Sector is MORE volatile than the market (amplifies moves)
    Beta < 1.0: Sector is LESS volatile (dampens moves)
    Beta < 0.0: Sector moves OPPOSITE to the market (rare)

    Used in the Capital Asset Pricing Model (CAPM):
    Expected Return = Risk-Free Rate + Beta × (Market Return - Risk-Free Rate)
    """
    if ticker not in returns.columns or benchmark not in returns.columns:
        return None

    sector_returns = returns[ticker].dropna()
    market_returns = returns[benchmark].dropna()

    aligned = pd.concat([sector_returns, market_returns], axis=1).dropna()
    if len(aligned) < 30:
        return None

    covariance = aligned.iloc[:, 0].cov(aligned.iloc[:, 1])
    market_variance = aligned.iloc[:, 1].var()

    if market_variance == 0:
        return None

    beta_value = covariance / market_variance

    if beta_value > 1.0:
        interpretation = "More volatile than market"
    elif beta_value < 1.0:
        interpretation = "Less volatile than market"
    else:
        interpretation = "Moves with market"

    return {
        "beta": round(beta_value, 3),
        "interpretation": interpretation,
    }


def max_drawdown(prices, ticker):
    """
    Calculate maximum drawdown — largest peak-to-trough decline.

    This measures the worst-case loss an investor would have experienced
    if they bought at the peak and sold at the bottom.

    Max Drawdown = (Trough - Peak) / Peak × 100
    """
    if ticker not in prices.columns:
        return None

    series = prices[ticker].dropna()
    rolling_max = series.expanding().max()
    drawdown = (series - rolling_max) / rolling_max * 100
    max_dd = drawdown.min()

    return {"max_drawdown": round(max_dd, 2)}


def sharpe_ratio(returns, ticker, risk_free=RISK_FREE_RATE):
    """
    Calculate the Sharpe Ratio — the most important risk-adjusted
    return metric in all of finance.

    Sharpe = (Annualized Return - Risk-Free Rate) / Annualized Volatility

    Measures: how much excess return are you getting for each unit of
    risk you're taking?

    Sharpe > 2.0 = Excellent
    Sharpe > 1.0 = Good
    Sharpe > 0.0 = Positive but not great
    Sharpe < 0.0 = You'd be better off in Treasury bonds

    William Sharpe won the Nobel Prize in Economics (1990) for this.
    """
    if ticker not in returns.columns:
        return None

    daily_returns = returns[ticker].dropna()
    annual_return = daily_returns.mean() * TRADING_DAYS_PER_YEAR
    annual_vol = daily_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    if annual_vol == 0:
        return None

    sharpe = (annual_return - risk_free) / annual_vol

    if sharpe >= 2.0:
        rating = "EXCELLENT"
    elif sharpe >= 1.0:
        rating = "GOOD"
    elif sharpe >= 0:
        rating = "MODERATE"
    else:
        rating = "POOR — underperforming risk-free rate"

    return {
        "sharpe_ratio": round(sharpe, 3),
        "annualized_return": round(annual_return * 100, 2),
        "annualized_volatility": round(annual_vol * 100, 2),
        "rating": rating,
    }


def sortino_ratio(returns, ticker, risk_free=RISK_FREE_RATE):
    """
    Calculate the Sortino Ratio — a refinement of the Sharpe Ratio.

    Sortino = (Annualized Return - Risk-Free Rate) / Downside Deviation

    Unlike Sharpe, Sortino only penalizes DOWNSIDE volatility.
    Upside volatility (big gains) is not treated as risk.
    This gives a more accurate picture of risk-adjusted returns.
    """
    if ticker not in returns.columns:
        return None

    daily_returns = returns[ticker].dropna()
    annual_return = daily_returns.mean() * TRADING_DAYS_PER_YEAR

    downside_returns = daily_returns[daily_returns < 0]
    downside_dev = downside_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    if downside_dev == 0:
        return None

    sortino = (annual_return - risk_free) / downside_dev

    return {"sortino_ratio": round(sortino, 3)}


def correlation_matrix(returns):
    """
    Calculate cross-sector correlation matrix.

    Correlation measures how sectors move relative to each other:
    +1.0 = Perfect positive correlation (move together exactly)
     0.0 = No correlation (independent movement)
    -1.0 = Perfect negative correlation (move opposite)

    This is the foundation of portfolio diversification theory.
    Harry Markowitz won the Nobel Prize (1990) for showing that
    combining assets with low correlation reduces overall portfolio risk.
    """
    sector_tickers = [t for t in SECTOR_ETFS.keys() if t in returns.columns]
    sector_returns = returns[sector_tickers]
    corr = sector_returns.corr()
    return corr.round(3)


def composite_ranking(prices, returns):
    """
    Rank all sectors using a composite score across multiple metrics.

    Scoring:
    - 30% weight: 60-day momentum (higher = better)
    - 25% weight: Sharpe ratio (higher = better)
    - 20% weight: RSI distance from 50 (closer to 50 = more neutral/stable)
    - 15% weight: Volatility (lower = better, inverted)
    - 10% weight: Beta (lower = more defensive)

    This composite approach mirrors how equity research teams build
    sector rankings — no single metric tells the full story.
    """
    rankings = []

    for ticker, name in SECTOR_ETFS.items():
        if ticker not in prices.columns or ticker not in returns.columns:
            continue

        mom = momentum(prices, ticker)
        sharp = sharpe_ratio(returns, ticker)
        rsi_data = rsi(prices, ticker)
        vol = volatility(returns, ticker)
        beta_data = beta(returns, ticker)

        if not all([mom, sharp, rsi_data, vol, beta_data]):
            continue

        mom_score = mom.get("60d_return", 0) or 0
        sharpe_score = sharp["sharpe_ratio"]
        rsi_neutrality = 100 - abs(rsi_data["rsi"] - 50) * 2
        vol_score = 100 - vol["annualized_volatility"]
        beta_score = 100 - (beta_data["beta"] * 50)

        composite = (
            0.30 * mom_score +
            0.25 * sharpe_score * 20 +
            0.20 * rsi_neutrality * 0.3 +
            0.15 * vol_score * 0.3 +
            0.10 * beta_score * 0.3
        )

        rankings.append({
            "ticker": ticker,
            "name": name,
            "composite_score": round(composite, 2),
            "60d_momentum": mom_score,
            "sharpe": sharpe_score,
            "rsi": rsi_data["rsi"],
            "volatility": vol["annualized_volatility"],
            "beta": beta_data["beta"],
        })

    rankings.sort(key=lambda x: x["composite_score"], reverse=True)

    for i, r in enumerate(rankings):
        r["rank"] = i + 1

    return rankings


def full_sector_analysis(prices, returns):
    """
    Run complete analysis on all sectors.
    Returns a dictionary with all metrics for each sector.
    """
    analysis = {}

    for ticker, name in SECTOR_ETFS.items():
        sector = {"name": name, "ticker": ticker}

        ma = moving_averages(prices, ticker)
        if ma:
            sector.update({"moving_averages": ma})

        mom = momentum(prices, ticker)
        if mom:
            sector.update({"momentum": mom})

        rsi_data = rsi(prices, ticker)
        if rsi_data:
            sector.update({"rsi": rsi_data})

        vol = volatility(returns, ticker)
        if vol:
            sector.update({"volatility": vol})

        beta_data = beta(returns, ticker)
        if beta_data:
            sector.update({"beta": beta_data})

        dd = max_drawdown(prices, ticker)
        if dd:
            sector.update({"max_drawdown": dd})

        sharp = sharpe_ratio(returns, ticker)
        if sharp:
            sector.update({"sharpe": sharp})

        sort = sortino_ratio(returns, ticker)
        if sort:
            sector.update({"sortino": sort})

        analysis[ticker] = sector

    return analysis


def print_full_report(analysis, rankings, corr_matrix):
    """Print comprehensive analysis report."""
    print("=" * 75)
    print("  EQUITY SECTOR ANALYZER — FULL MARKET ANALYSIS")
    print("  Cameron Camarotti | github.com/cameroncc333")
    print("=" * 75)

    print(f"\n{'─' * 75}")
    print(f"  COMPOSITE SECTOR RANKINGS")
    print(f"{'─' * 75}")

    for r in rankings:
        print(f"\n  #{r['rank']} {r['ticker']} — {r['name']}")
        print(f"     Composite Score:   {r['composite_score']:.2f}")
        print(f"     60-Day Momentum:   {r['60d_momentum']:+.2f}%")
        print(f"     Sharpe Ratio:      {r['sharpe']:.3f}")
        print(f"     RSI:               {r['rsi']:.1f}")
        print(f"     Volatility:        {r['volatility']:.2f}%")
        print(f"     Beta:              {r['beta']:.3f}")

    print(f"\n{'─' * 75}")
    print(f"  DETAILED SECTOR ANALYSIS")
    print(f"{'─' * 75}")

    for ticker, data in analysis.items():
        print(f"\n  ━━━ {ticker} — {data['name']} ━━━")

        if "moving_averages" in data:
            ma = data["moving_averages"]
            print(f"  Price: ${ma['current_price']}")
            print(f"  50-Day MA: ${ma['ma_50']}  |  200-Day MA: ${ma['ma_200']}")
            print(f"  Signal: {ma['signal']}")

        if "momentum" in data:
            mom = data["momentum"]
            parts = [f"{k}: {v:+.2f}%" for k, v in mom.items() if v is not None]
            print(f"  Momentum: {' | '.join(parts)}")

        if "rsi" in data:
            print(f"  RSI: {data['rsi']['rsi']} ({data['rsi']['condition']})")

        if "volatility" in data:
            print(f"  Annualized Volatility: {data['volatility']['annualized_volatility']}%")

        if "beta" in data:
            print(f"  Beta: {data['beta']['beta']} ({data['beta']['interpretation']})")

        if "max_drawdown" in data:
            print(f"  Max Drawdown: {data['max_drawdown']['max_drawdown']}%")

        if "sharpe" in data:
            s = data["sharpe"]
            print(f"  Sharpe Ratio: {s['sharpe_ratio']} ({s['rating']})")
            print(f"  Annualized Return: {s['annualized_return']}%")

        if "sortino" in data:
            print(f"  Sortino Ratio: {data['sortino']['sortino_ratio']}")

    print(f"\n{'─' * 75}")
    print(f"  CORRELATION MATRIX (Top Pairs)")
    print(f"{'─' * 75}")

    tickers = list(corr_matrix.columns)
    pairs = []
    for i in range(len(tickers)):
        for j in range(i + 1, len(tickers)):
            pairs.append((tickers[i], tickers[j], corr_matrix.iloc[i, j]))

    pairs.sort(key=lambda x: x[2], reverse=True)

    print("\n  Highest Correlation (move together):")
    for t1, t2, corr in pairs[:5]:
        print(f"    {t1}/{t2}: {corr:.3f}")

    print("\n  Lowest Correlation (diversification opportunity):")
    for t1, t2, corr in pairs[-5:]:
        print(f"    {t1}/{t2}: {corr:.3f}")

    print(f"\n{'=' * 75}")
