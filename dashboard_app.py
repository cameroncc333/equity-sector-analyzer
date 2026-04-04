"""
Equity Sector Analyzer — Live Interactive Dashboard
Cameron Camarotti | github.com/cameroncc333

A real-time equity analysis dashboard that pulls live S&P 500 sector
data and displays institutional-grade quantitative metrics in an
interactive web interface.

Run: streamlit run dashboard_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ── Configuration ──
SECTOR_ETFS = {
    "XLK": "Technology", "XLF": "Financials", "XLE": "Energy",
    "XLV": "Healthcare", "XLY": "Consumer Disc.", "XLP": "Consumer Staples",
    "XLI": "Industrials", "XLB": "Materials", "XLRE": "Real Estate",
    "XLU": "Utilities", "XLC": "Communication",
}
BENCHMARK = "SPY"
RISK_FREE_RATE = 0.045
TRADING_DAYS = 252


# ── Data Functions ──
@st.cache_data(ttl=3600)
def load_data(lookback_years=2):
    """Download sector ETF data with 1-hour cache."""
    end = datetime.today()
    start = end - timedelta(days=lookback_years * 365)
    tickers = list(SECTOR_ETFS.keys()) + [BENCHMARK]
    data = yf.download(tickers, start=start, end=end, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data
    return prices.dropna(how="all")


def calc_returns(prices):
    return prices.pct_change().dropna()


# ── Metric Functions ──
def calc_momentum(prices, ticker, window):
    s = prices[ticker].dropna()
    if len(s) <= window:
        return None
    return ((s.iloc[-1] - s.iloc[-window - 1]) / s.iloc[-window - 1]) * 100


def calc_rsi(prices, ticker, period=14):
    s = prices[ticker].dropna()
    delta = s.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta).where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 1)


def calc_volatility(returns, ticker):
    return returns[ticker].std() * np.sqrt(TRADING_DAYS) * 100


def calc_beta(returns, ticker):
    if ticker not in returns.columns or BENCHMARK not in returns.columns:
        return None
    aligned = pd.concat([returns[ticker], returns[BENCHMARK]], axis=1).dropna()
    if len(aligned) < 30:
        return None
    cov = aligned.iloc[:, 0].cov(aligned.iloc[:, 1])
    var = aligned.iloc[:, 1].var()
    return cov / var if var != 0 else None


def calc_sharpe(returns, ticker):
    r = returns[ticker].dropna()
    ann_ret = r.mean() * TRADING_DAYS
    ann_vol = r.std() * np.sqrt(TRADING_DAYS)
    return (ann_ret - RISK_FREE_RATE) / ann_vol if ann_vol != 0 else 0


def calc_max_drawdown(prices, ticker):
    s = prices[ticker].dropna()
    rolling_max = s.expanding().max()
    dd = (s - rolling_max) / rolling_max * 100
    return dd.min()


def calc_moving_averages(prices, ticker):
    s = prices[ticker].dropna()
    ma50 = s.rolling(50).mean().iloc[-1]
    ma200 = s.rolling(200).mean().iloc[-1]
    price = s.iloc[-1]
    signal = "🟢 Golden Cross" if ma50 > ma200 else "🔴 Death Cross"
    return price, ma50, ma200, signal


def build_analysis(prices, returns):
    """Build complete analysis for all sectors."""
    rows = []
    for ticker, name in SECTOR_ETFS.items():
        if ticker not in prices.columns:
            continue
        price, ma50, ma200, signal = calc_moving_averages(prices, ticker)
        mom30 = calc_momentum(prices, ticker, 30)
        mom60 = calc_momentum(prices, ticker, 60)
        mom90 = calc_momentum(prices, ticker, 90)
        rsi_val = calc_rsi(prices, ticker)
        vol = calc_volatility(returns, ticker)
        beta_val = calc_beta(returns, ticker)
        sharpe = calc_sharpe(returns, ticker)
        mdd = calc_max_drawdown(prices, ticker)

        rows.append({
            "Ticker": ticker, "Sector": name, "Price": round(price, 2),
            "50-Day MA": round(ma50, 2), "200-Day MA": round(ma200, 2),
            "Signal": signal,
            "30d Return %": round(mom30, 2) if mom30 else None,
            "60d Return %": round(mom60, 2) if mom60 else None,
            "90d Return %": round(mom90, 2) if mom90 else None,
            "RSI": rsi_val,
            "Volatility %": round(vol, 2),
            "Beta": round(beta_val, 3) if beta_val else None,
            "Sharpe Ratio": round(sharpe, 3),
            "Max Drawdown %": round(mdd, 2),
        })
    return pd.DataFrame(rows)


# ── Page Config ──
st.set_page_config(
    page_title="Equity Sector Analyzer | Cameron Camarotti",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.85;
    }
    .positive { color: #00c853; font-weight: 600; }
    .negative { color: #ff1744; font-weight: 600; }
    .signal-bull { color: #00c853; font-weight: 700; }
    .signal-bear { color: #ff1744; font-weight: 700; }
    .footer {
        text-align: center;
        color: #888;
        font-size: 0.8rem;
        margin-top: 40px;
        padding: 20px;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    lookback = st.selectbox("Lookback Period", [1, 2, 3], index=1, format_func=lambda x: f"{x} Year{'s' if x > 1 else ''}")
    momentum_window = st.selectbox("Momentum Window", [30, 60, 90], index=1, format_func=lambda x: f"{x} Days")

    st.markdown("---")
    st.markdown("## 📋 About")
    st.markdown("""
    **Equity Sector Analyzer**
    Built by Cameron Camarotti

    Pulls live S&P 500 sector data and
    calculates institutional-grade
    quantitative metrics.

    [GitHub](https://github.com/cameroncc333)
    · [All Around Services](https://allaroundservice.com)
    """)

    st.markdown("---")
    st.markdown("## 📊 Metrics Explained")
    with st.expander("Sharpe Ratio"):
        st.markdown("Return per unit of risk. Above 1.0 = good. Nobel Prize-winning metric.")
    with st.expander("RSI"):
        st.markdown("Momentum oscillator (0-100). >70 = overbought. <30 = oversold.")
    with st.expander("Beta"):
        st.markdown("Market sensitivity. >1.0 = amplifies moves. <1.0 = dampens moves.")
    with st.expander("Golden/Death Cross"):
        st.markdown("50-day MA vs 200-day MA. Golden = bullish. Death = bearish.")


# ── Main Content ──
st.markdown('<p class="main-header">📊 Equity Sector Analyzer</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">Live S&P 500 Sector Analysis · {datetime.now().strftime("%B %d, %Y %I:%M %p")} · Cameron Camarotti</p>', unsafe_allow_html=True)

# Load data
with st.spinner("Downloading live market data..."):
    prices = load_data(lookback)
    returns = calc_returns(prices)
    df = build_analysis(prices, returns)

if df.empty:
    st.error("Could not load market data. Check your internet connection.")
    st.stop()

# ── Top Metrics Row ──
col1, col2, col3, col4 = st.columns(4)

best = df.loc[df[f"{momentum_window}d Return %"].idxmax()]
worst = df.loc[df[f"{momentum_window}d Return %"].idxmin()]
best_sharpe = df.loc[df["Sharpe Ratio"].idxmax()]
avg_vol = df["Volatility %"].mean()

with col1:
    st.metric(
        label=f"🏆 Strongest Sector ({momentum_window}d)",
        value=f"{best['Ticker']}",
        delta=f"{best[f'{momentum_window}d Return %']:+.2f}%"
    )
with col2:
    st.metric(
        label=f"📉 Weakest Sector ({momentum_window}d)",
        value=f"{worst['Ticker']}",
        delta=f"{worst[f'{momentum_window}d Return %']:+.2f}%"
    )
with col3:
    st.metric(
        label="⭐ Best Risk-Adjusted",
        value=f"{best_sharpe['Ticker']}",
        delta=f"Sharpe: {best_sharpe['Sharpe Ratio']:.3f}"
    )
with col4:
    st.metric(
        label="📊 Avg Market Volatility",
        value=f"{avg_vol:.1f}%",
        delta="Annualized"
    )

st.markdown("---")

# ── Sector Rankings Table ──
st.markdown("### 🏅 Sector Rankings")

display_df = df[["Ticker", "Sector", "Price", f"{momentum_window}d Return %",
                  "Sharpe Ratio", "RSI", "Volatility %", "Beta", "Signal"]].copy()
display_df = display_df.sort_values(f"{momentum_window}d Return %", ascending=False)
display_df = display_df.reset_index(drop=True)
display_df.index = display_df.index + 1
display_df.index.name = "Rank"

st.dataframe(
    display_df.style.format({
        "Price": "${:.2f}",
        f"{momentum_window}d Return %": "{:+.2f}%",
        "Sharpe Ratio": "{:.3f}",
        "RSI": "{:.1f}",
        "Volatility %": "{:.2f}%",
        "Beta": "{:.3f}",
    }).background_gradient(subset=[f"{momentum_window}d Return %"], cmap="RdYlGn")
    .background_gradient(subset=["Sharpe Ratio"], cmap="RdYlGn")
    .background_gradient(subset=["RSI"], cmap="RdYlBu_r", vmin=20, vmax=80),
    use_container_width=True,
    height=430
)

st.markdown("---")

# ── Charts Row 1 ──
if HAS_PLOTLY:
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 📈 Sector Performance")
        sorted_df = df.sort_values(f"{momentum_window}d Return %", ascending=True)
        colors = ["#00c853" if x >= 0 else "#ff1744" for x in sorted_df[f"{momentum_window}d Return %"]]

        fig_perf = go.Figure(go.Bar(
            x=sorted_df[f"{momentum_window}d Return %"],
            y=sorted_df["Sector"],
            orientation="h",
            marker_color=colors,
            text=[f"{x:+.1f}%" for x in sorted_df[f"{momentum_window}d Return %"]],
            textposition="outside"
        ))
        fig_perf.update_layout(
            height=450, xaxis_title=f"{momentum_window}-Day Return (%)",
            yaxis_title="", margin=dict(l=0, r=60, t=10, b=40),
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_perf, use_container_width=True)

    with col_right:
        st.markdown("### 🎯 Risk vs Return")
        fig_rr = px.scatter(
            df, x="Volatility %", y=f"{momentum_window}d Return %",
            text="Ticker", size="Beta", color="Sharpe Ratio",
            color_continuous_scale="RdYlGn",
            hover_data=["Sector", "RSI", "Sharpe Ratio"]
        )
        fig_rr.update_traces(textposition="top center", marker=dict(sizemin=8, sizeref=0.3))
        fig_rr.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig_rr.update_layout(
            height=450, margin=dict(l=0, r=0, t=10, b=40),
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_rr, use_container_width=True)

    st.markdown("---")

    # ── Charts Row 2 ──
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.markdown("### 🔥 RSI Signals")
        rsi_sorted = df.sort_values("RSI", ascending=False)
        rsi_colors = []
        for val in rsi_sorted["RSI"]:
            if val > 70:
                rsi_colors.append("#ff1744")
            elif val < 30:
                rsi_colors.append("#00c853")
            else:
                rsi_colors.append("#2196F3")

        fig_rsi = go.Figure(go.Bar(
            x=rsi_sorted["Sector"], y=rsi_sorted["RSI"],
            marker_color=rsi_colors,
            text=[f"{x:.0f}" for x in rsi_sorted["RSI"]],
            textposition="outside"
        ))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ff1744",
                          annotation_text="Overbought (70)")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00c853",
                          annotation_text="Oversold (30)")
        fig_rsi.update_layout(
            height=400, yaxis_range=[0, 100], yaxis_title="RSI",
            margin=dict(l=0, r=0, t=10, b=40), plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_rsi, use_container_width=True)

    with col_right2:
        st.markdown("### 📊 Sharpe Ratio Comparison")
        sharpe_sorted = df.sort_values("Sharpe Ratio", ascending=True)
        sharpe_colors = []
        for val in sharpe_sorted["Sharpe Ratio"]:
            if val >= 1.0:
                sharpe_colors.append("#00c853")
            elif val >= 0:
                sharpe_colors.append("#FFC107")
            else:
                sharpe_colors.append("#ff1744")

        fig_sharpe = go.Figure(go.Bar(
            x=sharpe_sorted["Sharpe Ratio"], y=sharpe_sorted["Sector"],
            orientation="h", marker_color=sharpe_colors,
            text=[f"{x:.2f}" for x in sharpe_sorted["Sharpe Ratio"]],
            textposition="outside"
        ))
        fig_sharpe.add_vline(x=1.0, line_dash="dash", line_color="#00c853",
                             annotation_text="Good (1.0)")
        fig_sharpe.add_vline(x=0, line_dash="solid", line_color="gray")
        fig_sharpe.update_layout(
            height=400, xaxis_title="Sharpe Ratio",
            margin=dict(l=0, r=60, t=10, b=40), plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_sharpe, use_container_width=True)

    st.markdown("---")

    # ── Correlation Heatmap ──
    st.markdown("### 🔗 Sector Correlation Matrix")
    st.markdown("*How sectors move relative to each other. Low correlation = diversification opportunity.*")

    sector_tickers = [t for t in SECTOR_ETFS.keys() if t in returns.columns]
    corr = returns[sector_tickers].corr()
    sector_names = [SECTOR_ETFS[t] for t in sector_tickers]

    fig_corr = go.Figure(go.Heatmap(
        z=corr.values, x=sector_names, y=sector_names,
        colorscale="RdYlGn", zmid=0, zmin=-1, zmax=1,
        text=np.round(corr.values, 2), texttemplate="%{text}",
        textfont={"size": 10}
    ))
    fig_corr.update_layout(height=550, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("---")

    # ── Individual Sector Deep Dive ──
    st.markdown("### 🔍 Sector Deep Dive")
    selected = st.selectbox("Select a sector to analyze:", list(SECTOR_ETFS.keys()),
                            format_func=lambda x: f"{x} — {SECTOR_ETFS[x]}")

    if selected in prices.columns:
        sector_data = df[df["Ticker"] == selected].iloc[0]

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Price", f"${sector_data['Price']:.2f}")
        with col_b:
            ret_val = sector_data[f"{momentum_window}d Return %"]
            st.metric(f"{momentum_window}d Return", f"{ret_val:+.2f}%")
        with col_c:
            st.metric("Sharpe Ratio", f"{sector_data['Sharpe Ratio']:.3f}")
        with col_d:
            st.metric("RSI", f"{sector_data['RSI']:.1f}")

        col_e, col_f, col_g, col_h = st.columns(4)
        with col_e:
            st.metric("Beta", f"{sector_data['Beta']:.3f}")
        with col_f:
            st.metric("Volatility", f"{sector_data['Volatility %']:.2f}%")
        with col_g:
            st.metric("Max Drawdown", f"{sector_data['Max Drawdown %']:.2f}%")
        with col_h:
            st.metric("Trend Signal", sector_data["Signal"])

        # Price chart with moving averages
        s = prices[selected].dropna()
        ma50 = s.rolling(50).mean()
        ma200 = s.rolling(200).mean()

        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=s.index, y=s.values, name="Price",
                                        line=dict(color="#2196F3", width=2)))
        fig_price.add_trace(go.Scatter(x=ma50.index, y=ma50.values, name="50-Day MA",
                                        line=dict(color="#FF9800", width=1.5, dash="dash")))
        fig_price.add_trace(go.Scatter(x=ma200.index, y=ma200.values, name="200-Day MA",
                                        line=dict(color="#f44336", width=1.5, dash="dash")))
        fig_price.update_layout(
            height=400,
            title=f"{selected} — {SECTOR_ETFS[selected]} Price History with Moving Averages",
            yaxis_title="Price ($)", xaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified"
        )
        st.plotly_chart(fig_price, use_container_width=True)

else:
    st.warning("Install plotly for interactive charts: pip3 install plotly")
    st.markdown("### Sector Data")
    st.dataframe(df)

# ── Footer ──
st.markdown("---")
st.markdown("""
<div class="footer">
    <strong>Equity Sector Analyzer</strong> · Built by Cameron Camarotti<br>
    <a href="https://github.com/cameroncc333">GitHub</a> ·
    <a href="https://allaroundservice.com">All Around Services</a> ·
    <a href="https://www.facebook.com/profile.php?id=61588386760982">Facebook</a><br><br>
    <em>This dashboard is for educational and informational purposes only.
    It is not investment advice. Past performance does not guarantee future results.</em>
</div>
""", unsafe_allow_html=True)
