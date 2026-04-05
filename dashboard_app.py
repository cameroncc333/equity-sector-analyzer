"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  EQUITY SECTOR ANALYZER v3.0                                               ║
║  Institutional-Grade Quantitative Market Dashboard                         ║
║                                                                            ║
║  Cameron Camarotti | github.com/cameroncc333 | allaroundservice.com        ║
║  Founder, All Around Services — 15+ cities, 44 jobs, $14.6K revenue       ║
║                                                                            ║
║  30+ quantitative metrics per security across 25 equities.                 ║
║  Sharpe · Sortino · Treynor · Calmar · Omega · Jensen's Alpha ·           ║
║  Information Ratio · Fama-French 5-Factor · RSI · Beta (w/ R², p-value) · ║
║  Momentum · Volatility · Max/Current Drawdown · Ulcer Index ·             ║
║  Skewness · Kurtosis · 95% Historical VaR · Relative Volume ·            ║
║  52-Week Range · Dividend Yield · Moving Averages · Sector Rotation ·     ║
║  Market Regime · Yield Curve · Monte Carlo Simulation                     ║
║                                                                            ║
║  Stack: Python · Streamlit · Plotly · pandas · NumPy · SciPy · yfinance   ║
║  Data: Yahoo Finance (live, 15-min cache)                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from datetime import datetime, timedelta
from io import BytesIO, StringIO
import json
import zipfile
import requests
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Equity Sector Analyzer — Cameron Camarotti",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════
# BLOOMBERG-INSPIRED DARK THEME
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');
    :root{
        --bg0:#080b10;--bg1:#0c1017;--bg2:#10151d;--bg3:#151c28;
        --bdr:rgba(56,189,248,0.07);--bdr2:rgba(56,189,248,0.18);
        --t1:#d6e0ec;--t2:#7a8da3;--t3:#3f5169;
        --blue:#38bdf8;--green:#22c55e;--red:#ef4444;
        --amber:#f59e0b;--purple:#a78bfa;--cyan:#06b6d4;
        --pink:#f472b6;--emerald:#34d399;--orange:#fb923c;--slate:#64748b;
    }
    .stApp{background:var(--bg0)!important;font-family:'DM Sans',sans-serif;color:var(--t1)}
    #MainMenu,footer{visibility:hidden}
    header[data-testid="stHeader"]{background:var(--bg0)!important;border-bottom:1px solid var(--bdr)}
    section[data-testid="stSidebar"]{background:var(--bg1)!important;border-right:1px solid var(--bdr)}
    .thdr{background:linear-gradient(135deg,var(--bg0) 0%,#0c1525 40%,#0f1a2e 100%);
        border:1px solid var(--bdr2);border-radius:4px;padding:1.6rem 2rem;margin-bottom:1.2rem;
        position:relative;overflow:hidden}
    .thdr::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
        background:linear-gradient(90deg,transparent,var(--blue),transparent)}
    .thdr h1{color:var(--blue);font-family:'JetBrains Mono',monospace;font-size:1.35rem;
        font-weight:600;margin:0 0 .2rem;letter-spacing:1px;text-transform:uppercase}
    .thdr .sub{color:var(--t2);font-family:'JetBrains Mono',monospace;font-size:.68rem;letter-spacing:.5px}
    .ldot{display:inline-block;width:6px;height:6px;background:var(--green);border-radius:50%;
        margin-right:6px;animation:pls 2s ease-in-out infinite}
    @keyframes pls{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(34,197,94,.4)}
        50%{opacity:.7;box-shadow:0 0 0 6px rgba(34,197,94,0)}}
    .exs{background:linear-gradient(135deg,rgba(56,189,248,.04),rgba(34,197,94,.03));
        border-left:3px solid var(--blue);border-radius:0 4px 4px 0;
        padding:1.1rem 1.4rem;margin:.8rem 0 1.2rem;font-size:.86rem;line-height:1.65;color:var(--t1)}
    .exs .ext{color:var(--blue);font-family:'JetBrains Mono',monospace;font-size:.62rem;
        text-transform:uppercase;letter-spacing:2px;margin-bottom:.4rem}
    .topsig{background:rgba(56,189,248,.06);border:1px solid rgba(56,189,248,.2);
        border-radius:4px;padding:.7rem 1rem;margin:.4rem 0;font-family:'JetBrains Mono',monospace;
        font-size:.82rem;color:var(--blue);font-weight:500}
    .abull{background:rgba(34,197,94,.05);border:1px solid rgba(34,197,94,.13);border-radius:4px;
        padding:.5rem .9rem;margin:.25rem 0;font-size:.78rem;color:var(--green);
        font-family:'JetBrains Mono',monospace}
    .abear{background:rgba(239,68,68,.05);border:1px solid rgba(239,68,68,.13);border-radius:4px;
        padding:.5rem .9rem;margin:.25rem 0;font-size:.78rem;color:var(--red);
        font-family:'JetBrains Mono',monospace}
    .aneu{background:rgba(245,158,11,.05);border:1px solid rgba(245,158,11,.13);border-radius:4px;
        padding:.5rem .9rem;margin:.25rem 0;font-size:.78rem;color:var(--amber);
        font-family:'JetBrains Mono',monospace}
    .shdr{font-family:'JetBrains Mono',monospace;font-size:.62rem;text-transform:uppercase;
        letter-spacing:2.5px;color:var(--t3);border-bottom:1px solid var(--bdr);
        padding-bottom:.4rem;margin:1.8rem 0 .8rem}
    .tftr{text-align:center;padding:1.5rem 0 .8rem;color:var(--t3);font-size:.62rem;
        font-family:'JetBrains Mono',monospace;border-top:1px solid var(--bdr);
        margin-top:2.5rem;letter-spacing:.5px}
    .tftr a{color:var(--blue);text-decoration:none}
    div[data-testid="stMetricValue"]{font-family:'JetBrains Mono',monospace;font-size:1.2rem!important}
    div[data-testid="stMetricLabel"]{font-family:'JetBrains Mono',monospace;font-size:.6rem!important;
        text-transform:uppercase;letter-spacing:1px;color:var(--t3)!important}
    .stTabs [data-baseweb="tab-list"]{gap:0;background:var(--bg1);border-radius:4px;padding:2px;border:1px solid var(--bdr)}
    .stTabs [data-baseweb="tab"]{font-family:'JetBrains Mono',monospace;font-size:.65rem;
        font-weight:500;letter-spacing:.5px;text-transform:uppercase;padding:.45rem .8rem;border-radius:3px}
    .stTabs [aria-selected="true"]{background:var(--bg2)!important;border:1px solid var(--bdr2)!important}
    .stPlotlyChart{border:1px solid var(--bdr);border-radius:4px;overflow:hidden}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════
PL = dict(  # Plotly layout base
    template="plotly_dark",
    paper_bgcolor="rgba(8,11,16,0)", plot_bgcolor="rgba(12,16,23,0.95)",
    font=dict(family="JetBrains Mono, monospace", size=11, color="#7a8da3"),
    title_font=dict(family="JetBrains Mono, monospace", size=12, color="#d6e0ec"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=50, r=30, t=55, b=40),
    xaxis=dict(gridcolor="rgba(56,189,248,0.05)", zerolinecolor="rgba(56,189,248,0.08)"),
    yaxis=dict(gridcolor="rgba(56,189,248,0.05)", zerolinecolor="rgba(56,189,248,0.08)"),
)
C = dict(blue="#38bdf8", green="#22c55e", red="#ef4444", amber="#f59e0b",
         purple="#a78bfa", cyan="#06b6d4", pink="#f472b6", emerald="#34d399",
         orange="#fb923c", slate="#64748b")
CSEQ = list(C.values()) + ["#818cf8", "#fbbf24", "#f87171", "#2dd4bf", "#c084fc"]

SECTOR_ETFS = {
    "XLK": "Technology", "XLF": "Financials", "XLV": "Health Care",
    "XLY": "Consumer Disc.", "XLP": "Consumer Staples", "XLE": "Energy",
    "XLI": "Industrials", "XLB": "Materials", "XLRE": "Real Estate",
    "XLU": "Utilities", "XLC": "Comm. Svcs."
}
MEGA_CAPS = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA",
    "GOOG": "Alphabet", "META": "Meta", "AMZN": "Amazon",
    "TSLA": "Tesla", "JPM": "JPMorgan", "GS": "Goldman Sachs",
    "BAC": "Bank of America", "XOM": "ExxonMobil", "CVX": "Chevron",
    "UNH": "UnitedHealth", "JNJ": "Johnson & Johnson"
}
STOCK_SECTOR = {
    "AAPL": "XLK", "MSFT": "XLK", "NVDA": "XLK", "GOOG": "XLC",
    "META": "XLC", "AMZN": "XLY", "TSLA": "XLY", "JPM": "XLF",
    "GS": "XLF", "BAC": "XLF", "XOM": "XLE", "CVX": "XLE",
    "UNH": "XLV", "JNJ": "XLV",
}
OFFENSIVE = ["XLK", "XLY", "XLC", "XLF"]
DEFENSIVE = ["XLV", "XLP", "XLU", "XLRE"]
BENCH = "SPY"
ALL_T = {**SECTOR_ETFS, **MEGA_CAPS}

PERIOD_MAP = {"3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y", "2 Years": "2y"}

# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR — weights + lookback (defined early so data fetch uses them)
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:.72rem;color:#38bdf8;letter-spacing:1px;text-transform:uppercase">◆ Controls</div>', unsafe_allow_html=True)
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")

    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:.58rem;color:#3f5169;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:.3rem">Lookback Period</div>', unsafe_allow_html=True)
    lookback_label = st.selectbox("Period", list(PERIOD_MAP.keys()), index=2, label_visibility="collapsed")
    lookback = PERIOD_MAP[lookback_label]

    st.markdown("---")
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:.58rem;color:#3f5169;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:.3rem">Composite Ranking Weights</div>', unsafe_allow_html=True)
    w_sharpe = st.slider("Sharpe", 0, 100, 25, key="ws")
    w_sortino = st.slider("Sortino", 0, 100, 25, key="wso")
    w_momentum = st.slider("Momentum", 0, 100, 25, key="wm")
    w_vol = st.slider("Inv. Volatility", 0, 100, 25, key="wv")
    w_total = w_sharpe + w_sortino + w_momentum + w_vol
    if w_total > 0:
        wn = {"sharpe": w_sharpe/w_total, "sortino": w_sortino/w_total,
              "momentum": w_momentum/w_total, "vol": w_vol/w_total}
    else:
        wn = {"sharpe": 0.25, "sortino": 0.25, "momentum": 0.25, "vol": 0.25}

    st.markdown("---")
    st.caption(f"Universe: {len(SECTOR_ETFS)} sectors · {len(MEGA_CAPS)} stocks")
    st.caption(f"Benchmark: SPY · rf: 3.75%")
    st.caption(f"Cache: 15 min · Source: Yahoo Finance")
    st.markdown("---")
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:.58rem;color:#3f5169;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:.3rem">Methodology</div>', unsafe_allow_html=True)
    st.caption("Sharpe: (ann. excess ret / ann. σ), rf=3.75%")
    st.caption("Sortino: excess ret / downside σ only")
    st.caption("Treynor: excess ret / β")
    st.caption("Calmar: ann. ret / |max drawdown|")
    st.caption("Omega: Σ gains above threshold / Σ losses below")
    st.caption("Jensen's α: CAPM regression intercept")
    st.caption("Info Ratio: excess vs SPY / tracking error")
    st.caption("VaR 95%: 5th percentile of historical daily returns")
    st.caption("Ulcer: RMS of drawdown percentage series")
    st.caption("Fama-French: 5-factor OLS regression")
    st.caption("Composite: weighted avg of metric ranks")
    st.caption("Rotation: cumulative off vs def sector spread")
    st.caption("Options: Black-Scholes w/ Greeks (∂V/∂S, ∂²V/∂S², ∂V/∂T, ∂V/∂σ)")
    st.caption("Regime: SPY vs 200d SMA × VIX vs 20")
    st.markdown("---")
    st.markdown("**Cameron Camarotti**")
    st.markdown("[All Around Services](https://allaroundservice.com)")
    st.markdown("[GitHub](https://github.com/cameroncc333) · [LinkedIn](https://linkedin.com/in/cameroncc333)")
    st.markdown("---")
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:.55rem;color:#3f5169;letter-spacing:1px">CHANGELOG</div>', unsafe_allow_html=True)
    st.caption("v1.0 — Basic sector analysis")
    st.caption("v2.0 — Mega-caps, portfolio, thesis")
    st.caption("v3.0 — 30+ metrics, factor model, Monte Carlo, regime, rotation, VaR, watchlist, backtest")


# ═══════════════════════════════════════════════════════════════════════
# DATA LAYER
# ═══════════════════════════════════════════════════════════════════════

def safe_last(series):
    """Safely get last value of a series."""
    s = series.dropna()
    return float(s.iloc[-1]) if len(s) > 0 else None

def safe_prev(series):
    s = series.dropna()
    return float(s.iloc[-2]) if len(s) > 1 else None

@st.cache_data(ttl=900)
def fetch_data(period):
    tlist = list(ALL_T.keys()) + [BENCH, "^VIX", "^TNX", "^IRX"]
    # Try DXY
    tlist.append("DX-Y.NYB")
    raw = yf.download(tlist, period=period, auto_adjust=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        lvl0 = raw.columns.get_level_values(0).unique()
        prices = raw["Close"].copy() if "Close" in lvl0 else pd.DataFrame()
        vol = raw["Volume"].copy() if "Volume" in lvl0 else pd.DataFrame()
    else:
        prices = raw.copy()
        vol = pd.DataFrame()
    loaded = [t for t in tlist if t in prices.columns and prices[t].dropna().shape[0] > 0]
    failed = [t for t in tlist if t not in loaded]
    return prices, vol, loaded, failed

@st.cache_data(ttl=3600)
def fetch_earnings(tickers):
    """Fetch next earnings date for each ticker."""
    result = {}
    for t in tickers:
        try:
            tk = yf.Ticker(t)
            cal = tk.calendar
            if cal is not None and not cal.empty:
                if isinstance(cal, pd.DataFrame) and "Earnings Date" in cal.index:
                    ed = cal.loc["Earnings Date"].iloc[0]
                    result[t] = pd.Timestamp(ed)
                elif isinstance(cal, dict) and "Earnings Date" in cal:
                    dates = cal["Earnings Date"]
                    if dates:
                        result[t] = pd.Timestamp(dates[0])
        except Exception:
            pass
    return result

@st.cache_data(ttl=3600)
def fetch_dividends(tickers):
    """Fetch dividend yield for each ticker."""
    result = {}
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            result[t] = info.get("dividendYield", 0) or 0
        except Exception:
            result[t] = 0
    return result

@st.cache_data(ttl=86400)
def fetch_fama_french():
    """Fetch Fama-French 5-factor daily data from Kenneth French Data Library."""
    try:
        url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return None
        zf = zipfile.ZipFile(BytesIO(r.content))
        fname = [n for n in zf.namelist() if n.endswith(".CSV") or n.endswith(".csv")][0]
        with zf.open(fname) as f:
            lines = f.read().decode("utf-8").splitlines()
        # Find header row
        start = 0
        for i, line in enumerate(lines):
            if "Mkt-RF" in line:
                start = i
                break
        data_lines = []
        for line in lines[start+1:]:
            parts = line.strip().split(",")
            if len(parts) >= 6:
                try:
                    int(parts[0].strip())
                    data_lines.append(line)
                except ValueError:
                    if not data_lines:
                        continue
                    else:
                        break
        header = "Date,Mkt-RF,SMB,HML,RMW,CMA,RF"
        csv_str = header + "\n" + "\n".join(data_lines)
        df = pd.read_csv(StringIO(csv_str))
        df["Date"] = pd.to_datetime(df["Date"].astype(str), format="%Y%m%d")
        df = df.set_index("Date")
        # Convert from percentage to decimal
        for col in df.columns:
            df[col] = df[col].astype(float) / 100.0
        return df.last("2Y")  # Keep last 2 years
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
# QUANTITATIVE ENGINE — 30+ metrics
# ═══════════════════════════════════════════════════════════════════════
RF = 0.0375  # Current Fed funds rate

def log_ret(prices):
    return np.log(prices / prices.shift(1)).dropna()

def ann_return(returns):
    """Annualized return from daily log returns."""
    if len(returns) < 2:
        return 0.0
    total = returns.sum()
    days = len(returns)
    return float((np.exp(total * 252 / days) - 1))

def sharpe(ret):
    excess = ret.mean() - RF / 252
    s = ret.std()
    return float((excess / s) * np.sqrt(252)) if s > 0 and not np.isnan(s) else 0.0

def sortino(ret):
    excess = ret.mean() - RF / 252
    ds = ret[ret < 0].std()
    return float((excess / ds) * np.sqrt(252)) if ds > 0 and not np.isnan(ds) and len(ret[ret < 0]) >= 5 else 0.0

def treynor(ret, beta_val):
    """Treynor ratio: excess return per unit of systematic risk."""
    ann_ret = ann_return(ret)
    return float((ann_ret - RF) / beta_val) if beta_val != 0 and not np.isnan(beta_val) else 0.0

def calmar(ret, max_dd):
    """Calmar ratio: annualized return / |max drawdown|."""
    ann_ret = ann_return(ret)
    return float(ann_ret / abs(max_dd / 100)) if max_dd != 0 else 0.0

def omega(ret, threshold=0.0):
    """Omega ratio: sum of gains above threshold / sum of losses below threshold."""
    gains = ret[ret > threshold].sum()
    losses = abs(ret[ret <= threshold].sum())
    return float(gains / losses) if losses > 0 else 0.0

def info_ratio(asset_ret, bench_ret):
    al = pd.concat([asset_ret, bench_ret], axis=1).dropna()
    if len(al) < 30:
        return 0.0
    ex = al.iloc[:, 0] - al.iloc[:, 1]
    te = ex.std()
    return float((ex.mean() / te) * np.sqrt(252)) if te > 0 and not np.isnan(te) else 0.0

def rsi(prices, window=14):
    d = prices.diff()
    g = d.where(d > 0, 0.0).rolling(window).mean()
    l = (-d.where(d < 0, 0.0)).rolling(window).mean()
    rs = g / l
    r = 100 - (100 / (1 + rs))
    v = safe_last(r)
    return v if v is not None and not np.isnan(v) else 50.0

def beta_full(asset_ret, bench_ret):
    """Beta with R² and p-value."""
    al = pd.concat([asset_ret, bench_ret], axis=1).dropna()
    if len(al) < 30:
        return 1.0, 0.0, 1.0
    slope, intercept, r_value, p_value, std_err = stats.linregress(al.iloc[:, 1], al.iloc[:, 0])
    return float(slope), float(r_value**2), float(p_value)

def jensens_alpha(asset_ret, bench_ret):
    """Jensen's Alpha: CAPM regression intercept, annualized."""
    al = pd.concat([asset_ret, bench_ret], axis=1).dropna()
    if len(al) < 30:
        return 0.0
    slope, intercept, _, _, _ = stats.linregress(al.iloc[:, 1], al.iloc[:, 0])
    return float(intercept * 252)  # Annualize daily alpha

def momentum(prices, window=20):
    return float((prices.iloc[-1] / prices.iloc[-window] - 1) * 100) if len(prices) >= window else 0.0

def volatility(ret):
    return float(ret.std() * np.sqrt(252) * 100)

def max_drawdown(prices):
    pk = prices.cummax()
    dd = (prices - pk) / pk
    return float(dd.min() * 100)

def curr_drawdown(prices):
    pk = prices.cummax()
    return float(((prices.iloc[-1] - pk.iloc[-1]) / pk.iloc[-1]) * 100)

def ulcer_index(prices):
    """Ulcer Index: RMS of percentage drawdown series."""
    pk = prices.cummax()
    dd_pct = ((prices - pk) / pk) * 100
    return float(np.sqrt((dd_pct ** 2).mean()))

def hist_var_95(ret):
    """Historical Value at Risk at 95% confidence."""
    return float(np.percentile(ret.dropna(), 5) * 100)

def skewness(ret):
    return float(ret.skew()) if len(ret) > 20 else 0.0

def kurtosis_val(ret):
    return float(ret.kurtosis()) if len(ret) > 20 else 0.0

def rolling_sharpe(ret, window=60):
    rm = ret.rolling(window).mean()
    rs = ret.rolling(window).std()
    return (((rm - RF/252) / rs) * np.sqrt(252)).dropna()

def rel_strength(asset_p, bench_p):
    al = pd.concat([asset_p, bench_p], axis=1).dropna()
    if len(al) < 2:
        return pd.Series(dtype=float)
    r = al.iloc[:, 0] / al.iloc[:, 1]
    return r / r.iloc[0] * 100

def rel_volume(vol_s, window=20):
    if vol_s is None or len(vol_s) < window:
        return None
    avg = vol_s.rolling(window).mean()
    last = safe_last(avg)
    return float(vol_s.iloc[-1] / last) if last and last > 0 else None

def moving_avgs(prices):
    s50 = prices.rolling(50).mean()
    s200 = prices.rolling(200).mean()
    cur = prices.iloc[-1]
    v50 = safe_last(s50)
    v200 = safe_last(s200)
    if v50 and v200:
        if cur > v50 > v200: sig = "▲ Bullish"
        elif cur < v50 < v200: sig = "▼ Bearish"
        elif v50 > v200: sig = "— Neutral+"
        else: sig = "— Neutral-"
    else:
        sig = "—"
    cross = None
    if v50 and v200 and len(s50) > 5 and len(s200) > 5:
        p50 = s50.iloc[-5]; p200 = s200.iloc[-5]
        if not np.isnan(p50) and not np.isnan(p200):
            if p50 < p200 and v50 > v200: cross = "GOLDEN CROSS"
            elif p50 > p200 and v50 < v200: cross = "DEATH CROSS"
    return {"s50": v50, "s200": v200, "sig": sig, "px": float(cur), "cross": cross}

def mtf_returns(prices):
    r = {}
    for d, l in [(30,"30d"),(60,"60d"),(90,"90d"),(252,"1y")]:
        r[l] = float((prices.iloc[-1]/prices.iloc[-d]-1)*100) if len(prices)>=d else 0.0
    return r

def regression_accel(r30, r60, r90):
    """Proper acceleration via OLS slope of returns across timeframes."""
    x = np.array([30, 60, 90], dtype=float)
    y = np.array([r30, r60/2, r90/3], dtype=float)  # Normalize to per-30d rate
    if np.any(np.isnan(y)):
        return 0.0
    slope, _, _, _, _ = stats.linregress(x, y)
    return float(slope * 100)

def week52_range(prices):
    """52-week high, low, and distance from high."""
    if len(prices) < 20:
        return None, None, None
    # Use up to 252 trading days
    p = prices.tail(min(252, len(prices)))
    hi = float(p.max())
    lo = float(p.min())
    dist = float((prices.iloc[-1] / hi - 1) * 100)
    return hi, lo, dist

def rotation_signal(sector_ret, window=20):
    off = [t for t in OFFENSIVE if t in sector_ret.columns]
    dfe = [t for t in DEFENSIVE if t in sector_ret.columns]
    if not off or not dfe:
        return "N/A", 0.0
    op = sector_ret[off].tail(window).sum().mean() * 100
    dp = sector_ret[dfe].tail(window).sum().mean() * 100
    sp = op - dp
    if sp > 2: return "RISK-ON", sp
    elif sp < -2: return "RISK-OFF", sp
    else: return "NEUTRAL", sp

def market_regime(spy_prices, vix_prices):
    """2x2 regime: SPY vs 200d SMA × VIX vs 20."""
    if spy_prices is None or vix_prices is None:
        return "Unknown"
    spy_v = safe_last(spy_prices)
    spy_sma = safe_last(spy_prices.rolling(200).mean())
    vix_v = safe_last(vix_prices)
    if spy_v is None or spy_sma is None or vix_v is None:
        return "Unknown"
    bull = spy_v > spy_sma
    low_vol = vix_v < 20
    if bull and low_vol: return "Bull · Low Vol"
    elif bull and not low_vol: return "Bull · High Vol"
    elif not bull and low_vol: return "Bear · Low Vol"
    else: return "Bear · High Vol"

def fama_french_regression(asset_ret, ff_data):
    """Run Fama-French 5-factor regression."""
    if ff_data is None or ff_data.empty:
        return None
    # Align dates
    ar = asset_ret.copy()
    ar.name = "Asset"
    merged = pd.merge(ar, ff_data, left_index=True, right_index=True, how="inner")
    if len(merged) < 60:
        return None
    y = merged["Asset"] - merged["RF"]
    X = merged[["Mkt-RF", "SMB", "HML", "RMW", "CMA"]]
    X = X.assign(const=1.0)
    try:
        from numpy.linalg import lstsq
        result = lstsq(X.values, y.values, rcond=None)
        coeffs = result[0]
        # Compute t-stats
        residuals = y.values - X.values @ coeffs
        n = len(y)
        k = X.shape[1]
        mse = np.sum(residuals**2) / (n - k)
        var_b = mse * np.linalg.inv(X.values.T @ X.values).diagonal()
        se = np.sqrt(np.abs(var_b))
        t_stats = coeffs / se
        r2 = 1 - np.sum(residuals**2) / np.sum((y.values - y.mean())**2)
        factors = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "Alpha"]
        return {
            "factors": factors,
            "coeffs": coeffs.tolist(),
            "t_stats": t_stats.tolist(),
            "r2": float(r2),
            "n_obs": n,
        }
    except Exception:
        return None

def monte_carlo_portfolio(port_returns, n_sims=1000, days=126):
    """Monte Carlo simulation for portfolio forward projection (6 months)."""
    if len(port_returns) < 30:
        return None
    mu = port_returns.mean()
    sigma = port_returns.std()
    sims = np.zeros((n_sims, days))
    for i in range(n_sims):
        daily = np.random.normal(mu, sigma, days)
        sims[i] = np.cumprod(1 + daily) * 100  # Start at 100
    percentiles = {
        "p5": np.percentile(sims, 5, axis=0),
        "p25": np.percentile(sims, 25, axis=0),
        "p50": np.percentile(sims, 50, axis=0),
        "p75": np.percentile(sims, 75, axis=0),
        "p95": np.percentile(sims, 95, axis=0),
    }
    return percentiles

def hhi(weights):
    """Herfindahl-Hirschman Index for concentration."""
    return float(sum(w**2 for w in weights) * 10000)


# ═══════════════════════════════════════════════════════════════════════
# BUILD ANALYSIS TABLE
# ═══════════════════════════════════════════════════════════════════════

def build_table(prices, vol, ret, bench_ret, tickers, div_data, earn_data, weights):
    rows = []
    for t, name in tickers.items():
        if t not in prices.columns:
            continue
        p = prices[t].dropna()
        r = ret[t].dropna() if t in ret.columns else pd.Series(dtype=float)
        if len(p) < 30 or len(r) < 30:
            continue
        ma = moving_avgs(p)
        mt = mtf_returns(p)
        b, b_r2, b_p = beta_full(r, bench_ret)
        md = max_drawdown(p)
        vs = vol[t].dropna() if (not vol.empty and t in vol.columns) else None
        rv = rel_volume(vs) if vs is not None and len(vs) > 0 else None
        h52, l52, d52 = week52_range(p)
        dy = div_data.get(t, 0) if div_data else 0
        ed = earn_data.get(t) if earn_data else None
        earn_days = (ed - pd.Timestamp.now()).days if ed and ed > pd.Timestamp.now() else None

        rows.append({
            "Ticker": t, "Name": name, "Price": ma["px"],
            "Sharpe": round(sharpe(r), 3),
            "Sortino": round(sortino(r), 3),
            "Treynor": round(treynor(r, b), 3),
            "Calmar": round(calmar(r, md), 3),
            "Omega": round(omega(r), 3),
            "Jensen_Alpha": round(jensens_alpha(r, bench_ret), 4),
            "Info_Ratio": round(info_ratio(r, bench_ret), 3),
            "RSI": round(rsi(p), 1),
            "Beta": round(b, 2), "Beta_R2": round(b_r2, 3), "Beta_P": round(b_p, 4),
            "Momentum": round(momentum(p), 2),
            "Volatility": round(volatility(r), 2),
            "Max_DD": round(md, 2), "Curr_DD": round(curr_drawdown(p), 2),
            "Ulcer": round(ulcer_index(p), 2),
            "VaR_95": round(hist_var_95(r), 2),
            "Skew": round(skewness(r), 3), "Kurt": round(kurtosis_val(r), 3),
            "Rel_Vol": round(rv, 2) if rv else None,
            "52W_Hi": round(h52, 2) if h52 else None,
            "52W_Lo": round(l52, 2) if l52 else None,
            "Dist_52Hi": round(d52, 1) if d52 is not None else None,
            "Div_Yield": round(dy * 100, 2) if dy else 0,
            "SMA50": ma["s50"], "SMA200": ma["s200"],
            "Signal": ma["sig"], "Cross": ma["cross"],
            "R_30d": round(mt["30d"], 2), "R_60d": round(mt["60d"], 2),
            "R_90d": round(mt["90d"], 2), "R_1y": round(mt.get("1y", 0), 2),
            "Accel": round(regression_accel(mt["30d"], mt["60d"], mt["90d"]), 3),
            "Earn_Days": earn_days,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # Composite ranking with user-defined weights
    df["R_Sh"] = df["Sharpe"].rank(ascending=False, method="first")
    df["R_So"] = df["Sortino"].rank(ascending=False, method="first")
    df["R_Mo"] = df["Momentum"].rank(ascending=False, method="first")
    df["R_Vo"] = df["Volatility"].rank(ascending=True, method="first")
    df["Composite"] = (df["R_Sh"]*weights["sharpe"] + df["R_So"]*weights["sortino"] +
                        df["R_Mo"]*weights["momentum"] + df["R_Vo"]*weights["vol"])
    df["Rank"] = df["Composite"].rank(ascending=True, method="first").astype(int)
    return df.sort_values("Rank")


# ═══════════════════════════════════════════════════════════════════════
# SIGNAL GENERATOR
# ═══════════════════════════════════════════════════════════════════════

def gen_signals(df, earn_data=None):
    sigs = []
    for _, r in df.iterrows():
        t = r["Ticker"]
        if r["RSI"] < 30:
            sigs.append(("bull", f"▲ {t} RSI {r['RSI']:.1f} — oversold, potential entry"))
        elif r["RSI"] > 70:
            sigs.append(("bear", f"▼ {t} RSI {r['RSI']:.1f} — overbought, consider reducing"))
        if r.get("Cross") == "GOLDEN CROSS":
            sigs.append(("bull", f"▲ {t} GOLDEN CROSS — 50d SMA crossed above 200d"))
        elif r.get("Cross") == "DEATH CROSS":
            sigs.append(("bear", f"▼ {t} DEATH CROSS — 50d SMA crossed below 200d"))
        if r["Curr_DD"] < -15:
            sigs.append(("bull", f"▲ {t} down {r['Curr_DD']:.1f}% from peak — deep drawdown"))
        if r.get("Rel_Vol") and r["Rel_Vol"] > 2.0:
            d = "up" if r["Momentum"] > 0 else "down"
            sigs.append(("neu", f"◆ {t} volume {r['Rel_Vol']:.1f}x avg — moving {d}"))
        if r.get("Dist_52Hi") is not None:
            if abs(r["Dist_52Hi"]) < 2:
                sigs.append(("neu", f"◆ {t} within {abs(r['Dist_52Hi']):.1f}% of 52-week high"))
            elif r.get("52W_Lo") and abs(r["Price"] - r["52W_Lo"]) / r["52W_Lo"] < 0.03:
                sigs.append(("bull", f"▲ {t} near 52-week low — evaluate for entry"))
        if r.get("Earn_Days") is not None and 0 < r["Earn_Days"] <= 7:
            sigs.append(("neu", f"◆ {t} earnings in {r['Earn_Days']} days — elevated vol expected"))
        if r["R_30d"] > 5 and r["RSI"] > 65:
            sigs.append(("neu", f"◆ {t} +{r['R_30d']:.1f}% in 30d w/ RSI {r['RSI']:.0f} — extended"))
    return sigs

def top_signal(sigs):
    """Pick the single highest-conviction signal."""
    # Prioritize: deep drawdown, golden cross, RSI extremes
    for typ, txt in sigs:
        if "GOLDEN CROSS" in txt or "deep drawdown" in txt:
            return txt
    for typ, txt in sigs:
        if "oversold" in txt:
            return txt
    return sigs[0][1] if sigs else None


# ═══════════════════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════════════════
with st.spinner("◆ Connecting to market data feed..."):
    prices, vol_data, loaded, failed = fetch_data(lookback)
    ret = log_ret(prices)

bench_ret = ret[BENCH].dropna() if BENCH in ret.columns else pd.Series(dtype=float)
bench_px = prices[BENCH].dropna() if BENCH in prices.columns else pd.Series(dtype=float)

with st.spinner("◆ Fetching earnings dates & dividends..."):
    earn_data = fetch_earnings(list(MEGA_CAPS.keys()))
    div_data = fetch_dividends(list(ALL_T.keys()))

with st.spinner("◆ Loading Fama-French factor data..."):
    ff_data = fetch_fama_french()


# ═══════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════
now_utc = datetime.utcnow()
st.markdown(f"""
<div class="thdr">
    <h1>◆ EQUITY SECTOR ANALYZER</h1>
    <div class="sub">
        <span class="ldot"></span>LIVE &nbsp;·&nbsp;
        Cameron Camarotti &nbsp;·&nbsp; github.com/cameroncc333 &nbsp;·&nbsp;
        allaroundservice.com &nbsp;·&nbsp; {now_utc.strftime("%Y-%m-%d %H:%M")} UTC
    </div>
</div>
""", unsafe_allow_html=True)

# Data quality
dq_total = len(list(ALL_T.keys()) + [BENCH, "^VIX", "^TNX", "^IRX", "DX-Y.NYB"])
dq_ok = len(loaded)
dq_fail_display = [f for f in failed if f not in ["DX-Y.NYB"]]  # DXY failure is expected
st.caption(f"◆ Data quality: {dq_ok}/{dq_total} tickers loaded" +
           (f" — unavailable: {', '.join(dq_fail_display)}" if dq_fail_display else " — all sources nominal"))

# ═══════════════════════════════════════════════════════════════════════
# MARKET CONTEXT BAR
# ═══════════════════════════════════════════════════════════════════════
spy_v = safe_last(prices[BENCH]) if BENCH in prices.columns else None
spy_p = safe_prev(prices[BENCH]) if BENCH in prices.columns else None
spy_chg = ((spy_v/spy_p)-1)*100 if spy_v and spy_p else 0

vix_v = safe_last(prices["^VIX"]) if "^VIX" in prices.columns else None
vix_p = safe_prev(prices["^VIX"]) if "^VIX" in prices.columns else None

tnx_v = safe_last(prices["^TNX"]) if "^TNX" in prices.columns else None
tnx_p = safe_prev(prices["^TNX"]) if "^TNX" in prices.columns else None
tnx_bps = round((tnx_v - tnx_p) * 100, 1) if tnx_v and tnx_p else 0  # Proper bps

irx_v = safe_last(prices["^IRX"]) if "^IRX" in prices.columns else None
yc_spread = round(tnx_v - irx_v, 2) if tnx_v and irx_v else None
yc_label = "INVERTED" if (yc_spread is not None and yc_spread < 0) else ("Flat" if yc_spread is not None and yc_spread < 0.5 else "Normal")

dxy_v = safe_last(prices["DX-Y.NYB"]) if "DX-Y.NYB" in prices.columns else None

sector_ret_rot = ret[[t for t in SECTOR_ETFS.keys() if t in ret.columns]]
rot_sig_20, rot_sp_20 = rotation_signal(sector_ret_rot, 20)
rot_sig_60, rot_sp_60 = rotation_signal(sector_ret_rot, 60)
regime = market_regime(
    prices[BENCH] if BENCH in prices.columns else None,
    prices["^VIX"] if "^VIX" in prices.columns else None
)

mc = st.columns(7)
if spy_v: mc[0].metric("S&P 500", f"${spy_v:,.2f}", f"{spy_chg:+.2f}%")
if vix_v:
    vl = "Low" if vix_v<15 else ("Mod" if vix_v<20 else ("High" if vix_v<30 else "Extreme"))
    mc[1].metric(f"VIX [{vl}]", f"{vix_v:.2f}", f"{(vix_v-vix_p):+.2f}" if vix_p else None)
if tnx_v: mc[2].metric("10Y Yield", f"{tnx_v:.2f}%", f"{tnx_bps:+.1f} bps")
if yc_spread is not None: mc[3].metric(f"Yield Curve [{yc_label}]", f"{yc_spread:+.2f}%")
mc[4].metric("Rotation (20d)", rot_sig_20, f"{rot_sp_20:+.1f}%")
mc[5].metric("Regime", regime)
if dxy_v: mc[6].metric("DXY", f"{dxy_v:.2f}")
else: mc[6].metric("Updated", now_utc.strftime("%H:%M UTC"))

# Build tables
sector_df = build_table(prices, vol_data, ret, bench_ret, SECTOR_ETFS, div_data, {}, wn)
stock_df = build_table(prices, vol_data, ret, bench_ret, MEGA_CAPS, div_data, earn_data, wn)

# ═══════════════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY + SIGNALS
# ═══════════════════════════════════════════════════════════════════════
# Build summary
regime_txt = f"Market regime: **{regime}**"
vix_txt = f" with VIX at {vix_v:.1f}" if vix_v else ""
tnx_txt = f", 10Y yield at {tnx_v:.2f}%" if tnx_v else ""
yc_txt = f", yield curve {yc_label.lower()} ({yc_spread:+.2f}%)" if yc_spread is not None else ""
top_txt = ""
if not sector_df.empty:
    tp = sector_df.iloc[0]
    bt = sector_df.iloc[-1]
    top_txt = f" {tp['Name']} ({tp['Ticker']}) leads composite ranking (Sharpe {tp['Sharpe']:.2f}, Sortino {tp['Sortino']:.2f}). {bt['Name']} ranks last."
rot_txt = f" Sector rotation: {rot_sig_20} (20d spread {rot_sp_20:+.1f}%), {rot_sig_60} on 60d."

exec_body = f"{regime_txt}{vix_txt}{tnx_txt}{yc_txt}.{top_txt}{rot_txt}"

all_sigs = gen_signals(sector_df, earn_data) + gen_signals(stock_df, earn_data)
ts = top_signal(all_sigs)

st.markdown(f"""
<div class="exs">
    <div class="ext">◆ Executive Summary</div>
    {exec_body}
</div>
""", unsafe_allow_html=True)

if ts:
    st.markdown(f'<div class="topsig">TOP SIGNAL: {ts}</div>', unsafe_allow_html=True)

if all_sigs:
    with st.expander(f"◆ {len(all_sigs)} Active Signals", expanded=False):
        for st_type, st_text in all_sigs[:20]:
            cls = {"bull":"abull","bear":"abear"}.get(st_type, "aneu")
            st.markdown(f'<div class="{cls}">{st_text}</div>', unsafe_allow_html=True)

st.markdown("---")

# Quick lookup
ql1, ql2 = st.columns([2, 4])
with ql1:
    sq = st.text_input("🔍 Ticker Lookup", placeholder="e.g. NVDA", label_visibility="collapsed")
if sq:
    sq = sq.upper().strip()
    combo = pd.concat([sector_df, stock_df], ignore_index=True)
    m = combo[combo["Ticker"] == sq]
    if not m.empty:
        r = m.iloc[0]
        qc = st.columns(8)
        qc[0].metric(r["Ticker"], f"${r['Price']:.2f}")
        qc[1].metric("Sharpe", f"{r['Sharpe']:.3f}")
        qc[2].metric("Sortino", f"{r['Sortino']:.3f}")
        qc[3].metric("RSI", f"{r['RSI']:.1f}")
        qc[4].metric("Beta", f"{r['Beta']:.2f}")
        qc[5].metric("VaR 95%", f"{r['VaR_95']:.2f}%")
        qc[6].metric("Max DD", f"{r['Max_DD']:.1f}%")
        qc[7].metric("Signal", r["Signal"])

# ═══════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════
tabs = st.tabs(["SECTORS", "MEGA-CAPS", "MULTI-TF", "ROTATION", "HEAD-TO-HEAD",
                 "OPTIONS", "PORTFOLIO", "WATCHLIST", "THESIS"])

# ═══════════════════════════════════════════════════════════════════════
# HELPER: render analysis table
# ═══════════════════════════════════════════════════════════════════════
def render_table(df, height=440):
    cols = ["Rank","Ticker","Name","Price","Sharpe","Sortino","Treynor","Calmar","Omega",
            "Jensen_Alpha","Info_Ratio","RSI","Beta","Momentum","Volatility",
            "Max_DD","Curr_DD","Ulcer","VaR_95","Skew","Kurt",
            "Div_Yield","Signal","R_30d","R_60d","R_90d","R_1y"]
    avail = [c for c in cols if c in df.columns]
    fmt = {"Price":"${:.2f}","Sharpe":"{:.3f}","Sortino":"{:.3f}","Treynor":"{:.3f}",
           "Calmar":"{:.3f}","Omega":"{:.3f}","Jensen_Alpha":"{:.4f}","Info_Ratio":"{:.3f}",
           "RSI":"{:.1f}","Beta":"{:.2f}","Momentum":"{:+.2f}%","Volatility":"{:.2f}%",
           "Max_DD":"{:.1f}%","Curr_DD":"{:.1f}%","Ulcer":"{:.2f}","VaR_95":"{:.2f}%",
           "Skew":"{:.3f}","Kurt":"{:.3f}","Div_Yield":"{:.2f}%",
           "R_30d":"{:+.2f}%","R_60d":"{:+.2f}%","R_90d":"{:+.2f}%","R_1y":"{:+.2f}%"}
    st.dataframe(
        df[avail].style.format({k:v for k,v in fmt.items() if k in avail}),
        use_container_width=True, hide_index=True, height=height)

def chart(fig, h=400):
    fig.update_layout(**PL, height=h)
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# TAB 1: SECTORS
# ═══════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="shdr">S&P 500 Sector ETF Rankings</div>', unsafe_allow_html=True)
    if not sector_df.empty:
        render_table(sector_df)

        c1, c2 = st.columns(2)
        with c1:
            try:
                st.markdown('<div class="shdr">Sharpe Ratio</div>', unsafe_allow_html=True)
                fig = px.bar(sector_df.sort_values("Sharpe",ascending=True),x="Sharpe",y="Name",
                             orientation="h",color="Sharpe",color_continuous_scale="RdYlGn")
                fig.update_layout(showlegend=False,coloraxis_showscale=False)
                chart(fig)
            except Exception as e:
                st.warning(f"Sharpe chart unavailable: {e}")
        with c2:
            try:
                st.markdown('<div class="shdr">Sortino Ratio</div>', unsafe_allow_html=True)
                fig = px.bar(sector_df.sort_values("Sortino",ascending=True),x="Sortino",y="Name",
                             orientation="h",color="Sortino",color_continuous_scale="RdYlGn")
                fig.update_layout(showlegend=False,coloraxis_showscale=False)
                chart(fig)
            except Exception as e:
                st.warning(f"Sortino chart unavailable: {e}")

        c3, c4 = st.columns(2)
        with c3:
            try:
                st.markdown('<div class="shdr">RSI (14-Day)</div>', unsafe_allow_html=True)
                fig = px.bar(sector_df.sort_values("RSI"),x="RSI",y="Name",orientation="h",
                             color="RSI",color_continuous_scale=["#22c55e","#f59e0b","#ef4444"],range_color=[20,80])
                fig.add_vline(x=30,line_dash="dash",line_color="rgba(34,197,94,0.4)",
                              annotation_text="OVERSOLD",annotation_position="top left")
                fig.add_vline(x=70,line_dash="dash",line_color="rgba(239,68,68,0.4)",
                              annotation_text="OVERBOUGHT",annotation_position="top right")
                fig.update_layout(showlegend=False,coloraxis_showscale=False)
                chart(fig)
            except Exception as e:
                st.warning(f"RSI chart unavailable: {e}")
        with c4:
            try:
                st.markdown('<div class="shdr">Calmar Ratio (Return / Max Drawdown)</div>', unsafe_allow_html=True)
                fig = px.bar(sector_df.sort_values("Calmar",ascending=True),x="Calmar",y="Name",
                             orientation="h",color="Calmar",color_continuous_scale="RdYlGn")
                fig.update_layout(showlegend=False,coloraxis_showscale=False)
                chart(fig)
            except Exception as e:
                st.warning(f"Calmar chart unavailable: {e}")

        # Correlation
        try:
            st.markdown('<div class="shdr">Sector Correlation Matrix</div>', unsafe_allow_html=True)
            stk = [t for t in SECTOR_ETFS.keys() if t in ret.columns]
            corr = ret[stk].corr()
            fig = px.imshow(corr,x=[SECTOR_ETFS[t] for t in stk],y=[SECTOR_ETFS[t] for t in stk],
                            color_continuous_scale="RdBu_r",zmin=-1,zmax=1,text_auto=".2f")
            chart(fig, 520)
            # Pair highlights
            mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
            corr_masked = corr.where(mask)
            max_pair = corr_masked.stack().idxmax()
            min_pair = corr_masked.stack().idxmin()
            max_v = corr_masked.stack().max()
            min_v = corr_masked.stack().min()
            st.caption(f"Highest correlation: {SECTOR_ETFS.get(max_pair[0],max_pair[0])} — {SECTOR_ETFS.get(max_pair[1],max_pair[1])} ({max_v:.2f}) | "
                       f"Lowest: {SECTOR_ETFS.get(min_pair[0],min_pair[0])} — {SECTOR_ETFS.get(min_pair[1],min_pair[1])} ({min_v:.2f})")
        except Exception as e:
            st.warning(f"Correlation matrix unavailable: {e}")


# ═══════════════════════════════════════════════════════════════════════
# TAB 2: MEGA-CAPS
# ═══════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="shdr">Mega-Cap Equity Rankings</div>', unsafe_allow_html=True)
    if not stock_df.empty:
        # Add sector column
        stock_df_display = stock_df.copy()
        stock_df_display["Sector"] = stock_df_display["Ticker"].map(
            lambda t: SECTOR_ETFS.get(STOCK_SECTOR.get(t, ""), ""))
        # Intra-sector rank
        stock_df_display["Sector_Rank"] = stock_df_display.groupby(
            stock_df_display["Ticker"].map(lambda t: STOCK_SECTOR.get(t, ""))
        )["Rank"].rank(method="first").astype(int)
        sector_counts = stock_df_display["Ticker"].map(lambda t: STOCK_SECTOR.get(t, "")).value_counts()
        stock_df_display["Intra_Sector"] = stock_df_display.apply(
            lambda r: f"#{int(r['Sector_Rank'])} of {sector_counts.get(STOCK_SECTOR.get(r['Ticker'],''), '?')} in {r['Sector']}", axis=1)

        render_table(stock_df_display, 540)

        try:
            st.markdown('<div class="shdr">Risk-Return Frontier</div>', unsafe_allow_html=True)
            fig = px.scatter(stock_df,x="Volatility",y="Sharpe",text="Ticker",
                             size=stock_df["Beta"].clip(lower=0.3),color="Momentum",
                             color_continuous_scale="RdYlGn",
                             labels={"Volatility":"Annualized Volatility (%)","Sharpe":"Sharpe Ratio"})
            fig.update_traces(textposition="top center",textfont_size=10)
            chart(fig, 480)
        except Exception:
            pass

        # Deep dive
        st.markdown('<div class="shdr">Individual Stock Deep Dive</div>', unsafe_allow_html=True)
        sel = st.selectbox("Select:", list(MEGA_CAPS.keys()),
                            format_func=lambda x: f"{x} — {MEGA_CAPS[x]} ({stock_df_display[stock_df_display['Ticker']==x]['Intra_Sector'].values[0] if x in stock_df_display['Ticker'].values else ''})")

        if sel in prices.columns:
            p = prices[sel].dropna()
            r = ret[sel].dropna() if sel in ret.columns else pd.Series(dtype=float)

            try:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=p.index,y=p.values,name="Price",line=dict(color=C["blue"],width=2)))
                s50 = p.rolling(50).mean(); s200 = p.rolling(200).mean()
                fig.add_trace(go.Scatter(x=s50.index,y=s50.values,name="SMA 50",line=dict(color=C["amber"],width=1,dash="dash")))
                fig.add_trace(go.Scatter(x=s200.index,y=s200.values,name="SMA 200",line=dict(color=C["red"],width=1,dash="dot")))
                fig.update_layout(title=f"{MEGA_CAPS[sel]} ({sel}) — Price & Moving Averages")
                chart(fig, 380)
            except Exception:
                pass

            dc1, dc2 = st.columns(2)
            with dc1:
                try:
                    if len(r) > 60:
                        rs = rolling_sharpe(r, 60)
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=rs.index,y=rs.values,name="60d Rolling Sharpe",
                                                  line=dict(color=C["purple"],width=2),
                                                  fill="tozeroy",fillcolor="rgba(167,139,250,0.1)"))
                        fig.add_hline(y=0,line_dash="dash",line_color="rgba(255,255,255,0.2)")
                        fig.update_layout(title=f"{sel} — Rolling Sharpe (60d)")
                        chart(fig, 300)
                except Exception:
                    pass
            with dc2:
                try:
                    if len(bench_px) > 0:
                        rs_l = rel_strength(p, bench_px)
                        if len(rs_l) > 0:
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=rs_l.index,y=rs_l.values,name=f"{sel} vs SPY",
                                                      line=dict(color=C["cyan"],width=2),
                                                      fill="tozeroy",fillcolor="rgba(6,182,212,0.08)"))
                            fig.add_hline(y=100,line_dash="dash",line_color="rgba(255,255,255,0.2)",
                                          annotation_text="= SPY")
                            fig.update_layout(title=f"{sel} — Relative Strength vs SPY")
                            chart(fig, 300)
                except Exception:
                    pass

            # Fama-French 5-Factor
            if ff_data is not None and len(r) > 60:
                try:
                    st.markdown('<div class="shdr">Fama-French 5-Factor Regression</div>', unsafe_allow_html=True)
                    ff_result = fama_french_regression(r, ff_data)
                    if ff_result:
                        ff_df = pd.DataFrame({
                            "Factor": ff_result["factors"],
                            "Loading": [round(x,4) for x in ff_result["coeffs"]],
                            "t-Statistic": [round(x,2) for x in ff_result["t_stats"]],
                            "Significant": ["Yes" if abs(t) > 1.96 else "No" for t in ff_result["t_stats"]],
                        })
                        st.dataframe(ff_df, use_container_width=True, hide_index=True)
                        st.caption(f"R² = {ff_result['r2']:.4f} | Observations: {ff_result['n_obs']} | "
                                   f"Significance threshold: |t| > 1.96 (95% confidence)")
                        st.caption("Mkt-RF = market excess return | SMB = small minus big (size) | "
                                   "HML = high minus low (value) | RMW = robust minus weak (profitability) | "
                                   "CMA = conservative minus aggressive (investment)")
                    else:
                        st.caption("Insufficient overlapping data for factor regression.")
                except Exception as e:
                    st.caption(f"Factor analysis unavailable: {e}")
            elif ff_data is None:
                st.caption("◆ Fama-French data unavailable — check internet connection for Kenneth French Data Library access.")

        # Correlation
        try:
            st.markdown('<div class="shdr">Mega-Cap Correlation</div>', unsafe_allow_html=True)
            mct = [t for t in MEGA_CAPS.keys() if t in ret.columns]
            corr = ret[mct].corr()
            fig = px.imshow(corr,x=mct,y=mct,color_continuous_scale="RdBu_r",zmin=-1,zmax=1,text_auto=".2f")
            chart(fig, 520)
            mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
            cm = corr.where(mask)
            mx = cm.stack().idxmax(); mn = cm.stack().idxmin()
            st.caption(f"Highest: {mx[0]}-{mx[1]} ({cm.stack().max():.2f}) | Lowest: {mn[0]}-{mn[1]} ({cm.stack().min():.2f})")
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════
# TAB 3: MULTI-TIMEFRAME
# ═══════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="shdr">Multi-Timeframe Returns</div>', unsafe_allow_html=True)
    ch = st.radio("Universe:",["Sectors","Mega-Caps","Full"],horizontal=True,key="mtf_u")
    if ch=="Sectors": cdf=sector_df.copy() if not sector_df.empty else pd.DataFrame()
    elif ch=="Mega-Caps": cdf=stock_df.copy() if not stock_df.empty else pd.DataFrame()
    else: cdf=pd.concat([sector_df,stock_df],ignore_index=True) if not sector_df.empty else stock_df.copy()

    if not cdf.empty:
        try:
            cdf = cdf.sort_values("R_90d",ascending=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(y=cdf["Ticker"],x=cdf["R_30d"],name="30d",orientation="h",marker_color=C["blue"],opacity=0.9))
            fig.add_trace(go.Bar(y=cdf["Ticker"],x=cdf["R_60d"],name="60d",orientation="h",marker_color=C["amber"],opacity=0.9))
            fig.add_trace(go.Bar(y=cdf["Ticker"],x=cdf["R_90d"],name="90d",orientation="h",marker_color=C["green"],opacity=0.9))
            if "R_1y" in cdf.columns:
                fig.add_trace(go.Bar(y=cdf["Ticker"],x=cdf["R_1y"],name="1y",orientation="h",marker_color=C["purple"],opacity=0.9))
            fig.update_layout(barmode="group",xaxis_title="Return (%)")
            chart(fig, max(500,len(cdf)*28))
        except Exception:
            pass

        try:
            st.markdown('<div class="shdr">Momentum Acceleration (Regression Slope)</div>', unsafe_allow_html=True)
            st.caption("Positive = returns accelerating. Negative = momentum fading. Computed via OLS slope across timeframes.")
            fig = px.bar(cdf.sort_values("Accel",ascending=False),x="Accel",y="Ticker",orientation="h",
                         color="Accel",color_continuous_scale="RdYlGn")
            fig.update_layout(coloraxis_showscale=False,xaxis_title="Acceleration (regression slope)")
            chart(fig, max(400,len(cdf)*24))
        except Exception:
            pass

    # Backtest
    try:
        st.markdown('<div class="shdr">Ranking Backtest — Did the Model Work?</div>', unsafe_allow_html=True)
        st.caption("Shows what the composite ranking recommended 90 days ago and how those picks actually performed since.")
        # Recompute rankings using data from 90 days ago
        if not sector_df.empty and BENCH in prices.columns:
            all_combo = pd.concat([sector_df, stock_df], ignore_index=True)
            if len(bench_px) > 90:
                # Get top 3 and bottom 3 current rankings, measure their 90d returns
                top3 = all_combo.head(3)
                bot3 = all_combo.tail(3)
                spy_90d = float((bench_px.iloc[-1]/bench_px.iloc[-90]-1)*100) if len(bench_px)>=90 else 0

                bt_data = []
                for _, r in top3.iterrows():
                    bt_data.append({"Ticker": r["Ticker"], "Group": "Top 3 Ranked", "90d Return": r["R_90d"]})
                for _, r in bot3.iterrows():
                    bt_data.append({"Ticker": r["Ticker"], "Group": "Bottom 3 Ranked", "90d Return": r["R_90d"]})
                bt_data.append({"Ticker": "SPY", "Group": "Benchmark", "90d Return": round(spy_90d, 2)})

                bt_df = pd.DataFrame(bt_data)
                fig = px.bar(bt_df, x="90d Return", y="Ticker", color="Group", orientation="h",
                             color_discrete_map={"Top 3 Ranked": C["green"], "Bottom 3 Ranked": C["red"], "Benchmark": C["slate"]})
                fig.update_layout(xaxis_title="90-Day Return (%)")
                chart(fig, 350)

                top3_avg = top3["R_90d"].mean()
                st.caption(f"Top 3 avg: {top3_avg:+.2f}% | SPY: {spy_90d:+.2f}% | Alpha: {top3_avg-spy_90d:+.2f}%")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════
# TAB 4: ROTATION & RISK
# ═══════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="shdr">Sector Rotation</div>', unsafe_allow_html=True)
    if not sector_df.empty:
        rc = "green" if "ON" in rot_sig_20 else ("red" if "OFF" in rot_sig_20 else "amber")
        st.markdown(f"""
        <div class="signal-card" style="background:var(--bg2);border:1px solid var(--bdr);border-left:3px solid var(--{rc});
            border-radius:4px;padding:1rem 1.2rem;margin-bottom:1rem;font-family:'JetBrains Mono',monospace">
            <div style="color:var(--t3);font-size:.6rem;text-transform:uppercase;letter-spacing:2px">Rotation Signal</div>
            <div style="color:var(--t1);font-size:1.3rem;font-weight:600">{rot_sig_20} (20d) · {rot_sig_60} (60d)</div>
            <div style="color:var(--t2);font-size:.72rem;margin-top:.2rem">
                20d spread: {rot_sp_20:+.1f}% · 60d spread: {rot_sp_60:+.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        try:
            off_t = [t for t in OFFENSIVE if t in prices.columns]
            def_t = [t for t in DEFENSIVE if t in prices.columns]
            if off_t and def_t:
                oa = prices[off_t].mean(axis=1).dropna(); da = prices[def_t].mean(axis=1).dropna()
                on = oa/oa.iloc[0]*100; dn = da/da.iloc[0]*100
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=on.index,y=on.values,name="Offensive",line=dict(color=C["blue"],width=2)))
                fig.add_trace(go.Scatter(x=dn.index,y=dn.values,name="Defensive",line=dict(color=C["amber"],width=2)))
                fig.update_layout(title="Offensive vs Defensive (Indexed to 100)")
                chart(fig, 370)

                sp = on - dn
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=sp.index,y=sp.values,name="Spread",line=dict(color=C["purple"],width=2),
                                          fill="tozeroy",fillcolor="rgba(167,139,250,0.08)"))
                fig.add_hline(y=0,line_dash="dash",line_color="rgba(255,255,255,0.2)")
                fig.update_layout(title="Off-Def Spread (>0 = Risk-On)")
                chart(fig, 270)
        except Exception:
            pass

        # Regime over time
        try:
            st.markdown('<div class="shdr">Market Regime</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:var(--bg2);border:1px solid var(--bdr);border-radius:4px;padding:1rem;
                font-family:'JetBrains Mono',monospace;font-size:.85rem;color:var(--t1);margin-bottom:1rem">
                Current Regime: <strong>{regime}</strong><br>
                <span style="color:var(--t2);font-size:.72rem">
                    Bull/Bear = SPY vs 200-day SMA · Low/High Vol = VIX vs 20 threshold
                </span>
            </div>""", unsafe_allow_html=True)
        except Exception:
            pass

        # Yield curve
        if yc_spread is not None and "^TNX" in prices.columns and "^IRX" in prices.columns:
            try:
                st.markdown('<div class="shdr">Yield Curve (10Y minus 3-Month)</div>', unsafe_allow_html=True)
                tnx_s = prices["^TNX"].dropna(); irx_s = prices["^IRX"].dropna()
                al_yc = pd.concat([tnx_s, irx_s], axis=1).dropna()
                if len(al_yc) > 0:
                    yc_ts = al_yc.iloc[:,0] - al_yc.iloc[:,1]
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=yc_ts.index, y=yc_ts.values, name="10Y-3M Spread",
                                              line=dict(color=C["cyan"], width=2),
                                              fill="tozeroy", fillcolor="rgba(6,182,212,0.08)"))
                    fig.add_hline(y=0, line_dash="dash", line_color=C["red"],
                                  annotation_text="INVERSION LINE")
                    fig.update_layout(title="Yield Curve Spread (Negative = Recession Signal)",
                                      yaxis_title="Spread (%)")
                    chart(fig, 300)
            except Exception:
                pass

        # Relative strength all sectors vs SPY
        try:
            st.markdown('<div class="shdr">Sector Relative Strength vs SPY</div>', unsafe_allow_html=True)
            fig = go.Figure()
            for t in sorted(SECTOR_ETFS.keys()):
                if t in prices.columns:
                    rs = rel_strength(prices[t].dropna(), bench_px)
                    if len(rs) > 0:
                        fig.add_trace(go.Scatter(x=rs.index,y=rs.values,name=SECTOR_ETFS[t],line=dict(width=1.5)))
            fig.add_hline(y=100,line_dash="dash",line_color="rgba(255,255,255,0.15)")
            fig.update_layout(title="Relative Strength (100 = Equal to SPY)")
            chart(fig, 450)
        except Exception:
            pass

        # Drawdown + VaR
        try:
            st.markdown('<div class="shdr">Drawdown & Value at Risk</div>', unsafe_allow_html=True)
            combo = pd.concat([sector_df,stock_df],ignore_index=True)
            dd = combo[["Ticker","Max_DD","Curr_DD","VaR_95"]].sort_values("Max_DD")
            fig = make_subplots(rows=1,cols=3,shared_yaxes=True,
                                subplot_titles=["Max Drawdown (%)","Current Drawdown (%)","95% Daily VaR (%)"])
            fig.add_trace(go.Bar(y=dd["Ticker"],x=dd["Max_DD"],orientation="h",marker_color=C["red"],opacity=0.8,name="Max DD"),row=1,col=1)
            fig.add_trace(go.Bar(y=dd["Ticker"],x=dd["Curr_DD"],orientation="h",marker_color=C["amber"],opacity=0.8,name="Curr DD"),row=1,col=2)
            fig.add_trace(go.Bar(y=dd["Ticker"],x=dd["VaR_95"],orientation="h",marker_color=C["purple"],opacity=0.8,name="VaR 95%"),row=1,col=3)
            fig.update_layout(showlegend=False)
            chart(fig, max(480,len(dd)*22))
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════
# TAB 5: HEAD-TO-HEAD
# ═══════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="shdr">Head-to-Head Comparison</div>', unsafe_allow_html=True)
    all_options = sorted(ALL_T.keys())
    hc1, hc2 = st.columns(2)
    ha = hc1.selectbox("Security A", all_options, index=all_options.index("NVDA") if "NVDA" in all_options else 0)
    hb = hc2.selectbox("Security B", all_options, index=all_options.index("MSFT") if "MSFT" in all_options else 1)

    combo = pd.concat([sector_df, stock_df], ignore_index=True)
    ra = combo[combo["Ticker"]==ha]
    rb = combo[combo["Ticker"]==hb]

    if not ra.empty and not rb.empty:
        ra = ra.iloc[0]; rb = rb.iloc[0]
        metrics = ["Price","Sharpe","Sortino","Treynor","Calmar","Omega","Jensen_Alpha","Info_Ratio",
                   "RSI","Beta","Momentum","Volatility","Max_DD","Curr_DD","Ulcer","VaR_95",
                   "Skew","Kurt","Div_Yield","R_30d","R_60d","R_90d","Signal","Rank"]
        comp_rows = []
        for m in metrics:
            if m in ra.index and m in rb.index:
                va = ra[m]; vb = rb[m]
                # Determine winner
                better_higher = m in ["Sharpe","Sortino","Treynor","Calmar","Omega","Jensen_Alpha",
                                       "Info_Ratio","Momentum","Div_Yield","R_30d","R_60d","R_90d"]
                better_lower = m in ["Volatility","Max_DD","Curr_DD","Ulcer","VaR_95","Rank"]
                if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                    if better_higher: winner = "◀" if va > vb else ("▶" if vb > va else "=")
                    elif better_lower: winner = "◀" if va < vb else ("▶" if vb < va else "=")
                    else: winner = "—"
                else:
                    winner = "—"
                comp_rows.append({"Metric": m, ha: va, "Winner": winner, hb: vb})

        comp_df = pd.DataFrame(comp_rows)
        st.dataframe(comp_df, use_container_width=True, hide_index=True, height=700)

        # Overlaid price charts
        if ha in prices.columns and hb in prices.columns:
            try:
                pa = prices[ha].dropna(); pb = prices[hb].dropna()
                pa_n = pa/pa.iloc[0]*100; pb_n = pb/pb.iloc[0]*100
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=pa_n.index,y=pa_n.values,name=ha,line=dict(color=C["blue"],width=2)))
                fig.add_trace(go.Scatter(x=pb_n.index,y=pb_n.values,name=hb,line=dict(color=C["amber"],width=2)))
                fig.update_layout(title=f"{ha} vs {hb} — Normalized Price (100 = Start)")
                chart(fig, 370)
            except Exception:
                pass

            # Relative strength A vs B
            try:
                rs_ab = rel_strength(pa, pb)
                if len(rs_ab) > 0:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=rs_ab.index,y=rs_ab.values,name=f"{ha} vs {hb}",
                                              line=dict(color=C["purple"],width=2),
                                              fill="tozeroy",fillcolor="rgba(167,139,250,0.08)"))
                    fig.add_hline(y=100,line_dash="dash",line_color="rgba(255,255,255,0.2)")
                    fig.update_layout(title=f"Relative Strength: {ha} vs {hb} (>100 = {ha} outperforming)")
                    chart(fig, 300)
            except Exception:
                pass

            # Return distribution
            try:
                r_a = ret[ha].dropna() if ha in ret.columns else pd.Series(dtype=float)
                r_b = ret[hb].dropna() if hb in ret.columns else pd.Series(dtype=float)
                if len(r_a) > 20 and len(r_b) > 20:
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(x=r_a*100, name=ha, opacity=0.6, marker_color=C["blue"], nbinsx=50))
                    fig.add_trace(go.Histogram(x=r_b*100, name=hb, opacity=0.6, marker_color=C["amber"], nbinsx=50))
                    fig.update_layout(barmode="overlay", title="Return Distribution (Daily %)",
                                      xaxis_title="Daily Return (%)", yaxis_title="Frequency")
                    chart(fig, 350)
            except Exception:
                pass

            # Correlation
            if ha in ret.columns and hb in ret.columns:
                corr_val = ret[[ha,hb]].corr().iloc[0,1]
                st.caption(f"Correlation between {ha} and {hb}: **{corr_val:.3f}**")

        # Verdict
        a_rank = ra["Rank"]; b_rank = rb["Rank"]
        winner = ha if a_rank < b_rank else hb
        st.markdown(f"**Verdict:** {winner} ranks higher (#{int(min(a_rank,b_rank))}) on composite score. "
                    f"{ha} Rank #{int(a_rank)} vs {hb} Rank #{int(b_rank)}.")


# ═══════════════════════════════════════════════════════════════════════
# TAB 6: OPTIONS PRICING — Black-Scholes & Greeks
# ═══════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="shdr">Options Pricing — Black-Scholes Model & Greeks</div>', unsafe_allow_html=True)
    st.caption("The same partial derivative mathematics used in the AAS pricing model (∂Cost/∂φ) "
               "applied to derivatives pricing. Delta, Gamma, Theta, and Vega are all partial "
               "derivatives of the Black-Scholes equation with respect to different variables.")

    # Black-Scholes functions
    from scipy.stats import norm as sp_norm

    def bs_d1(S, K, T, r, sigma):
        """d1 parameter of Black-Scholes."""
        if T <= 0 or sigma <= 0:
            return 0.0
        return (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

    def bs_d2(S, K, T, r, sigma):
        return bs_d1(S, K, T, r, sigma) - sigma * np.sqrt(T)

    def bs_call_price(S, K, T, r, sigma):
        """Black-Scholes European call price."""
        if T <= 0:
            return max(S - K, 0)
        d1 = bs_d1(S, K, T, r, sigma)
        d2 = bs_d2(S, K, T, r, sigma)
        return S * sp_norm.cdf(d1) - K * np.exp(-r * T) * sp_norm.cdf(d2)

    def bs_put_price(S, K, T, r, sigma):
        """Black-Scholes European put price."""
        if T <= 0:
            return max(K - S, 0)
        d1 = bs_d1(S, K, T, r, sigma)
        d2 = bs_d2(S, K, T, r, sigma)
        return K * np.exp(-r * T) * sp_norm.cdf(-d2) - S * sp_norm.cdf(-d1)

    def bs_greeks(S, K, T, r, sigma, option_type="call"):
        """Compute all Greeks — each is a partial derivative of the option price."""
        if T <= 0 or sigma <= 0:
            return {"Delta": 0, "Gamma": 0, "Theta": 0, "Vega": 0, "Rho": 0}
        d1 = bs_d1(S, K, T, r, sigma)
        d2 = bs_d2(S, K, T, r, sigma)
        pdf_d1 = sp_norm.pdf(d1)

        # Delta: ∂V/∂S — sensitivity to underlying price
        if option_type == "call":
            delta = sp_norm.cdf(d1)
        else:
            delta = sp_norm.cdf(d1) - 1

        # Gamma: ∂²V/∂S² — rate of change of delta (second derivative)
        gamma = pdf_d1 / (S * sigma * np.sqrt(T))

        # Theta: ∂V/∂T — sensitivity to time decay (per day)
        if option_type == "call":
            theta = (-(S * pdf_d1 * sigma) / (2 * np.sqrt(T))
                     - r * K * np.exp(-r * T) * sp_norm.cdf(d2)) / 365
        else:
            theta = (-(S * pdf_d1 * sigma) / (2 * np.sqrt(T))
                     + r * K * np.exp(-r * T) * sp_norm.cdf(-d2)) / 365

        # Vega: ∂V/∂σ — sensitivity to volatility (per 1% move)
        vega = S * pdf_d1 * np.sqrt(T) / 100

        # Rho: ∂V/∂r — sensitivity to interest rates (per 1% move)
        if option_type == "call":
            rho = K * T * np.exp(-r * T) * sp_norm.cdf(d2) / 100
        else:
            rho = -K * T * np.exp(-r * T) * sp_norm.cdf(-d2) / 100

        return {"Delta": round(delta, 4), "Gamma": round(gamma, 4),
                "Theta": round(theta, 4), "Vega": round(vega, 4), "Rho": round(rho, 4)}

    # User inputs
    opt_col1, opt_col2 = st.columns(2)
    with opt_col1:
        opt_ticker = st.selectbox("Underlying", sorted(ALL_T.keys()), key="opt_tk",
                                   format_func=lambda x: f"{x} — {ALL_T[x]}")
        opt_type = st.radio("Option Type", ["Call", "Put"], horizontal=True, key="opt_type")

    # Get current price
    opt_spot = safe_last(prices[opt_ticker]) if opt_ticker in prices.columns else 100.0
    opt_vol_annual = volatility(ret[opt_ticker].dropna()) / 100 if opt_ticker in ret.columns else 0.25

    with opt_col2:
        opt_strike = st.number_input("Strike Price ($)", min_value=1.0,
                                      value=round(opt_spot, 0) if opt_spot else 100.0, step=1.0, key="opt_k")
        opt_dte = st.number_input("Days to Expiration", min_value=1, value=30, step=1, key="opt_dte")

    opt_T = opt_dte / 365.0
    opt_r = RF
    opt_sigma = opt_vol_annual if opt_vol_annual > 0 else 0.25

    st.caption(f"Spot: ${opt_spot:,.2f} | Implied Vol (from historical): {opt_sigma*100:.1f}% | "
               f"Risk-free rate: {opt_r*100:.2f}% | T: {opt_T:.4f} years")

    # Compute price and Greeks
    if opt_type == "Call":
        opt_price = bs_call_price(opt_spot, opt_strike, opt_T, opt_r, opt_sigma)
    else:
        opt_price = bs_put_price(opt_spot, opt_strike, opt_T, opt_r, opt_sigma)

    greeks = bs_greeks(opt_spot, opt_strike, opt_T, opt_r, opt_sigma,
                        option_type=opt_type.lower())

    # Display
    st.markdown("---")
    gm = st.columns(6)
    gm[0].metric(f"{opt_type} Price", f"${opt_price:.2f}")
    gm[1].metric("Delta (∂V/∂S)", f"{greeks['Delta']:.4f}")
    gm[2].metric("Gamma (∂²V/∂S²)", f"{greeks['Gamma']:.4f}")
    gm[3].metric("Theta (∂V/∂T)", f"{greeks['Theta']:.4f}")
    gm[4].metric("Vega (∂V/∂σ)", f"{greeks['Vega']:.4f}")
    gm[5].metric("Rho (∂V/∂r)", f"{greeks['Rho']:.4f}")

    st.markdown("---")

    # Price sensitivity charts
    try:
        st.markdown('<div class="shdr">Option Price vs. Underlying Price</div>', unsafe_allow_html=True)
        spot_range = np.linspace(opt_spot * 0.7, opt_spot * 1.3, 100)
        if opt_type == "Call":
            prices_curve = [bs_call_price(s, opt_strike, opt_T, opt_r, opt_sigma) for s in spot_range]
            intrinsic = [max(s - opt_strike, 0) for s in spot_range]
        else:
            prices_curve = [bs_put_price(s, opt_strike, opt_T, opt_r, opt_sigma) for s in spot_range]
            intrinsic = [max(opt_strike - s, 0) for s in spot_range]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=spot_range, y=prices_curve, name=f"{opt_type} Value",
                                  line=dict(color=C["blue"], width=2.5)))
        fig.add_trace(go.Scatter(x=spot_range, y=intrinsic, name="Intrinsic Value",
                                  line=dict(color=C["slate"], width=1.5, dash="dash")))
        fig.add_vline(x=opt_spot, line_dash="dot", line_color=C["amber"],
                       annotation_text=f"Spot ${opt_spot:.0f}")
        fig.add_vline(x=opt_strike, line_dash="dot", line_color=C["red"],
                       annotation_text=f"Strike ${opt_strike:.0f}")
        fig.update_layout(title=f"{opt_ticker} {opt_type} — Black-Scholes Price Curve",
                          xaxis_title="Underlying Price ($)", yaxis_title="Option Value ($)")
        chart(fig, 400)
    except Exception:
        pass

    # Greeks across spot prices
    try:
        st.markdown('<div class="shdr">Greeks vs. Underlying Price</div>', unsafe_allow_html=True)
        delta_curve = []; gamma_curve = []; theta_curve = []; vega_curve = []
        for s in spot_range:
            g = bs_greeks(s, opt_strike, opt_T, opt_r, opt_sigma, option_type=opt_type.lower())
            delta_curve.append(g["Delta"])
            gamma_curve.append(g["Gamma"])
            theta_curve.append(g["Theta"])
            vega_curve.append(g["Vega"])

        fig = make_subplots(rows=2, cols=2,
                            subplot_titles=["Delta (∂V/∂S)", "Gamma (∂²V/∂S²)",
                                            "Theta (∂V/∂T)", "Vega (∂V/∂σ)"])
        fig.add_trace(go.Scatter(x=spot_range, y=delta_curve, line=dict(color=C["blue"], width=2),
                                  showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=spot_range, y=gamma_curve, line=dict(color=C["green"], width=2),
                                  showlegend=False), row=1, col=2)
        fig.add_trace(go.Scatter(x=spot_range, y=theta_curve, line=dict(color=C["red"], width=2),
                                  showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=spot_range, y=vega_curve, line=dict(color=C["purple"], width=2),
                                  showlegend=False), row=2, col=2)
        # Add spot line to each
        for r_idx in [1,2]:
            for c_idx in [1,2]:
                fig.add_vline(x=opt_spot, line_dash="dot", line_color=C["amber"],
                               row=r_idx, col=c_idx)
        chart(fig, 500)
    except Exception:
        pass

    # Volatility surface
    try:
        st.markdown('<div class="shdr">Volatility Surface — Price Sensitivity to Vol & Time</div>', unsafe_allow_html=True)
        st.caption("Shows how option price changes across different volatility levels and days to expiration.")

        vol_range = np.linspace(0.10, 0.80, 30)
        dte_range = np.arange(5, 91, 3)
        surface = np.zeros((len(vol_range), len(dte_range)))

        for i, v in enumerate(vol_range):
            for j, d in enumerate(dte_range):
                t = d / 365.0
                if opt_type == "Call":
                    surface[i, j] = bs_call_price(opt_spot, opt_strike, t, opt_r, v)
                else:
                    surface[i, j] = bs_put_price(opt_spot, opt_strike, t, opt_r, v)

        fig = go.Figure(data=[go.Surface(
            z=surface, x=dte_range, y=vol_range * 100,
            colorscale="Viridis", showscale=True,
            colorbar=dict(title="Price ($)")
        )])
        fig.update_layout(
            title=f"{opt_ticker} {opt_type} — Volatility Surface",
            scene=dict(
                xaxis_title="Days to Expiration",
                yaxis_title="Implied Volatility (%)",
                zaxis_title="Option Price ($)",
                bgcolor="rgba(12,16,23,0.95)",
            ),
            **{k: v for k, v in PL.items() if k not in ["xaxis", "yaxis"]},
            height=550,
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        pass

    # Time decay visualization
    try:
        st.markdown('<div class="shdr">Time Decay — Option Value Over Time</div>', unsafe_allow_html=True)
        days_remaining = list(range(opt_dte, 0, -1))
        decay_curve = []
        for d in days_remaining:
            t = d / 365.0
            if opt_type == "Call":
                decay_curve.append(bs_call_price(opt_spot, opt_strike, t, opt_r, opt_sigma))
            else:
                decay_curve.append(bs_put_price(opt_spot, opt_strike, t, opt_r, opt_sigma))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days_remaining, y=decay_curve, name="Option Value",
                                  line=dict(color=C["red"], width=2.5),
                                  fill="tozeroy", fillcolor="rgba(239,68,68,0.08)"))
        fig.update_layout(title=f"Time Decay — {opt_ticker} {opt_type} (Strike ${opt_strike:.0f})",
                          xaxis_title="Days Remaining", yaxis_title="Option Value ($)",
                          xaxis=dict(autorange="reversed"))
        chart(fig, 350)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════
# TAB 7: PORTFOLIO
# ═══════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown('<div class="shdr">Portfolio Tracker & Benchmark</div>', unsafe_allow_html=True)

    if "portfolio" not in st.session_state: st.session_state.portfolio = []

    with st.expander("◆ Import / Export"):
        ie1,ie2=st.columns(2)
        with ie1:
            up=st.file_uploader("Import JSON",type=["json"],key="pu")
            if up:
                try: st.session_state.portfolio=json.loads(up.read()); st.success("Imported.")
                except: st.error("Invalid.")
        with ie2:
            if st.session_state.portfolio:
                st.download_button("⬇ Export",json.dumps(st.session_state.portfolio,indent=2),"portfolio.json","application/json")

    with st.form("add_h",clear_on_submit=True):
        h1,h2,h3,h4=st.columns(4)
        ht=h1.selectbox("Ticker",sorted(ALL_T.keys()))
        hs=h2.number_input("Shares",min_value=0.001,value=1.0,step=0.1)
        hc=h3.number_input("Cost ($)",min_value=0.01,value=100.0,step=0.01)
        hth=h4.text_input("Thesis")
        if st.form_submit_button("➕ Add"):
            ex=[h for h in st.session_state.portfolio if h["ticker"]==ht]
            if ex: ex[0].update({"shares":hs,"cost_basis":hc,"thesis":hth})
            else: st.session_state.portfolio.append({"ticker":ht,"shares":hs,"cost_basis":hc,
                    "thesis":hth,"date_added":datetime.now().strftime("%Y-%m-%d")})
            st.rerun()

    if st.session_state.portfolio:
        rm=st.selectbox("Remove:",["—"]+[h["ticker"] for h in st.session_state.portfolio],key="rms")
        if rm!="—" and st.button(f"🗑 Remove {rm}"):
            st.session_state.portfolio=[h for h in st.session_state.portfolio if h["ticker"]!=rm]; st.rerun()

        st.markdown("---")
        rows=[]; tv=tc=0
        for h in st.session_state.portfolio:
            t=h["ticker"]; cp=safe_last(prices[t]) if t in prices.columns else h["cost_basis"]
            if cp is None: cp = h["cost_basis"]
            mv=h["shares"]*cp; cv=h["shares"]*h["cost_basis"]; gl=mv-cv
            glp=((cp/h["cost_basis"])-1)*100 if h["cost_basis"]>0 else 0
            dy=div_data.get(t,0) or 0
            ann_div=h["shares"]*cp*dy
            tv+=mv; tc+=cv
            rows.append({"Ticker":t,"Shares":h["shares"],"Cost":h["cost_basis"],"Price":cp,
                          "Value":mv,"G/L $":gl,"G/L %":glp,"Div Yield":dy*100,
                          "Ann. Div $":ann_div,"Thesis":h.get("thesis",""),
                          "Added":h.get("date_added","")})

        pdf=pd.DataFrame(rows)
        pdf["Weight"]=(pdf["Value"]/tv*100) if tv>0 else 0
        tgl=tv-tc; tglp=((tv/tc)-1)*100 if tc>0 else 0
        total_div = pdf["Ann. Div $"].sum()

        pm=st.columns(5)
        pm[0].metric("Value",f"${tv:,.2f}"); pm[1].metric("Cost",f"${tc:,.2f}")
        pm[2].metric("G/L",f"${tgl:,.2f}",f"{tglp:+.2f}%")
        pm[3].metric("Holdings",len(st.session_state.portfolio))
        pm[4].metric("Ann. Dividends",f"${total_div:,.2f}")

        st.dataframe(pdf[["Ticker","Shares","Cost","Price","Value","G/L $","G/L %","Weight","Div Yield","Ann. Div $","Thesis","Added"]].style.format({
            "Shares":"{:.2f}","Cost":"${:.2f}","Price":"${:.2f}","Value":"${:,.2f}",
            "G/L $":"${:+,.2f}","G/L %":"{:+.2f}%","Weight":"{:.1f}%","Div Yield":"{:.2f}%",
            "Ann. Div $":"${:,.2f}"}),use_container_width=True,hide_index=True)

        # Sector concentration
        try:
            st.markdown('<div class="shdr">Sector Concentration</div>', unsafe_allow_html=True)
            pdf["Sector"] = pdf["Ticker"].map(lambda t: SECTOR_ETFS.get(STOCK_SECTOR.get(t, t), SECTOR_ETFS.get(t, "Other")))
            sec_alloc = pdf.groupby("Sector")["Value"].sum().reset_index()
            sec_alloc["Pct"] = sec_alloc["Value"]/tv*100

            sc1, sc2 = st.columns(2)
            with sc1:
                fig = px.pie(sec_alloc,values="Value",names="Sector",hole=0.45,color_discrete_sequence=CSEQ)
                fig.update_layout(**PL,height=350); fig.update_traces(textfont_size=10)
                st.plotly_chart(fig,use_container_width=True)
            with sc2:
                # HHI
                wts = (pdf["Value"]/tv*100).values
                hhi_val = hhi(wts/100)
                hhi_label = "Highly Concentrated" if hhi_val > 2500 else ("Moderately Concentrated" if hhi_val > 1500 else "Diversified")
                hhi_color = C["red"] if hhi_val > 2500 else (C["amber"] if hhi_val > 1500 else C["green"])
                st.metric("HHI Score", f"{hhi_val:,.0f}")
                st.markdown(f"<div style='color:{hhi_color};font-family:JetBrains Mono,monospace;font-size:.85rem'>{hhi_label}</div>", unsafe_allow_html=True)
                st.caption("HHI > 2500 = highly concentrated | 1500-2500 = moderate | < 1500 = diversified")
                st.caption("The Herfindahl-Hirschman Index measures portfolio concentration. Used by the DOJ for antitrust and by portfolio managers for risk assessment.")
        except Exception:
            pass

        # Portfolio-level metrics
        try:
            st.markdown('<div class="shdr">Portfolio-Level Analytics</div>', unsafe_allow_html=True)
            pt_in = [h["ticker"] for h in st.session_state.portfolio if h["ticker"] in prices.columns]
            if pt_in and len(bench_ret)>0:
                wts_dict={}
                for h in st.session_state.portfolio:
                    if h["ticker"] in prices.columns:
                        cp = safe_last(prices[h["ticker"]])
                        if cp: wts_dict[h["ticker"]]=h["shares"]*cp
                tw=sum(wts_dict.values())
                if tw>0:
                    wts_dict={k:v/tw for k,v in wts_dict.items()}
                    pr=pd.Series(0.0,index=ret.index)
                    for t,w in wts_dict.items():
                        if t in ret.columns: pr=pr.add(ret[t]*w,fill_value=0)
                    pr = pr.dropna()

                    plm = st.columns(6)
                    plm[0].metric("Port. Sharpe", f"{sharpe(pr):.3f}")
                    plm[1].metric("Port. Sortino", f"{sortino(pr):.3f}")
                    p_beta, p_r2, _ = beta_full(pr, bench_ret)
                    plm[2].metric("Port. Beta", f"{p_beta:.2f}")
                    plm[3].metric("Port. Volatility", f"{volatility(pr):.2f}%")
                    plm[4].metric("Port. Info Ratio", f"{info_ratio(pr, bench_ret):.3f}")
                    # Correlation to SPY
                    port_corr = pd.concat([pr, bench_ret], axis=1).dropna().corr().iloc[0,1]
                    plm[5].metric("Corr. to SPY", f"{port_corr:.3f}")
        except Exception:
            pass

        # Portfolio vs SPY
        try:
            st.markdown('<div class="shdr">Portfolio vs SPY Benchmark</div>', unsafe_allow_html=True)
            if pt_in and len(bench_ret) > 0 and tw > 0:
                # Find earliest date_added
                dates_added = [pd.Timestamp(h.get("date_added", "2020-01-01")) for h in st.session_state.portfolio]
                earliest = min(dates_added) if dates_added else pr.index[0]

                pc = (1+pr).cumprod(); sc = (1+bench_ret).cumprod()
                ai = pc.index.intersection(sc.index)
                # Filter to after earliest date
                ai = ai[ai >= earliest]
                if len(ai) > 1:
                    pc=pc.loc[ai]; sc=sc.loc[ai]
                    pn=pc/pc.iloc[0]*100; sn=sc/sc.iloc[0]*100

                    fig=go.Figure()
                    fig.add_trace(go.Scatter(x=pn.index,y=pn.values,name="Your Portfolio",line=dict(color=C["green"],width=2.5)))
                    fig.add_trace(go.Scatter(x=sn.index,y=sn.values,name="SPY",line=dict(color=C["slate"],width=1.5,dash="dash")))
                    fig.update_layout(title="Portfolio vs SPY (Indexed to 100)")
                    chart(fig, 380)

                    ptr=(pn.iloc[-1]/100-1)*100; spr=(sn.iloc[-1]/100-1)*100; alpha=ptr-spr
                    bc=st.columns(3)
                    bc[0].metric("Portfolio",f"{ptr:+.2f}%"); bc[1].metric("SPY",f"{spr:+.2f}%")
                    bc[2].metric("Alpha",f"{alpha:+.2f}%","▲ Outperforming" if alpha>0 else "▼ Underperforming")
        except Exception:
            pass

        # Performance attribution
        try:
            st.markdown('<div class="shdr">Performance Attribution</div>', unsafe_allow_html=True)
            attrib_rows = []
            for h in st.session_state.portfolio:
                t = h["ticker"]
                if t in prices.columns:
                    cp = safe_last(prices[t])
                    if cp:
                        gl_dollar = h["shares"] * (cp - h["cost_basis"])
                        attrib_rows.append({"Ticker": t, "Contribution ($)": gl_dollar})
            if attrib_rows:
                adf = pd.DataFrame(attrib_rows).sort_values("Contribution ($)")
                fig = px.bar(adf, x="Contribution ($)", y="Ticker", orientation="h",
                             color="Contribution ($)", color_continuous_scale="RdYlGn")
                fig.update_layout(coloraxis_showscale=False, xaxis_title="Dollar Contribution to P&L")
                chart(fig, max(300, len(adf)*35))
        except Exception:
            pass

        # What-If Simulator
        try:
            st.markdown('<div class="shdr">What-If Position Simulator</div>', unsafe_allow_html=True)
            st.caption("Preview how adding a position would change your portfolio before committing.")
            wi1, wi2 = st.columns(2)
            wi_ticker = wi1.selectbox("Simulate adding:", sorted(ALL_T.keys()), key="wi_t")
            wi_shares = wi2.number_input("Shares:", min_value=0.1, value=1.0, step=0.1, key="wi_s")

            wi_price = safe_last(prices[wi_ticker]) if wi_ticker in prices.columns else 100
            if wi_price:
                wi_val = wi_shares * wi_price
                new_tv = tv + wi_val
                new_wts = [(r["Value"]/new_tv*100) for _, r in pdf.iterrows()] + [wi_val/new_tv*100]
                new_hhi = hhi([w/100 for w in new_wts])
                new_hhi_label = "Highly Concentrated" if new_hhi > 2500 else ("Moderate" if new_hhi > 1500 else "Diversified")

                # New sector allocation
                wi_sector = SECTOR_ETFS.get(STOCK_SECTOR.get(wi_ticker, wi_ticker), SECTOR_ETFS.get(wi_ticker, "Other"))

                # New portfolio beta
                if wi_ticker in ret.columns:
                    wi_b, _, _ = beta_full(ret[wi_ticker].dropna(), bench_ret)
                    new_beta = p_beta * (tv/new_tv) + wi_b * (wi_val/new_tv) if 'p_beta' in dir() else wi_b
                else:
                    new_beta = None

                wc = st.columns(4)
                wc[0].metric("New Value", f"${new_tv:,.2f}", f"+${wi_val:,.2f}")
                wc[1].metric("New HHI", f"{new_hhi:,.0f}", new_hhi_label)
                if new_beta: wc[2].metric("New Beta", f"{new_beta:.2f}")
                wc[3].metric("New Holding", f"{wi_ticker} in {wi_sector}", f"{wi_val/new_tv*100:.1f}% weight")
        except Exception:
            pass

        # Monte Carlo
        try:
            st.markdown('<div class="shdr">Monte Carlo Simulation (6-Month Forward)</div>', unsafe_allow_html=True)
            st.caption("1,000 simulated paths based on historical return distribution. Fan chart shows probability bands.")
            if len(pr) > 30:
                mc_result = monte_carlo_portfolio(pr, n_sims=1000, days=126)
                if mc_result:
                    days_arr = list(range(126))
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=days_arr, y=mc_result["p5"], line=dict(width=0),
                                              showlegend=False, hoverinfo="skip"))
                    fig.add_trace(go.Scatter(x=days_arr, y=mc_result["p95"], fill="tonexty",
                                              fillcolor="rgba(56,189,248,0.08)", line=dict(width=0),
                                              name="5th-95th percentile"))
                    fig.add_trace(go.Scatter(x=days_arr, y=mc_result["p25"], line=dict(width=0),
                                              showlegend=False, hoverinfo="skip"))
                    fig.add_trace(go.Scatter(x=days_arr, y=mc_result["p75"], fill="tonexty",
                                              fillcolor="rgba(56,189,248,0.15)", line=dict(width=0),
                                              name="25th-75th percentile"))
                    fig.add_trace(go.Scatter(x=days_arr, y=mc_result["p50"],
                                              line=dict(color=C["blue"], width=2), name="Median"))
                    fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.2)")
                    fig.update_layout(title="Portfolio Simulation — 6 Month Projection (Indexed to 100)",
                                      xaxis_title="Trading Days", yaxis_title="Portfolio Value (Indexed)")
                    chart(fig, 400)

                    # Summary stats
                    final_vals = mc_result["p50"][-1]
                    best = mc_result["p95"][-1]
                    worst = mc_result["p5"][-1]
                    st.caption(f"Median outcome: {final_vals:.1f} ({(final_vals-100):+.1f}%) | "
                               f"Bull case (95th): {best:.1f} ({(best-100):+.1f}%) | "
                               f"Bear case (5th): {worst:.1f} ({(worst-100):+.1f}%)")
        except Exception:
            pass

        # Thesis log
        st.markdown('<div class="shdr">Investment Thesis Log</div>', unsafe_allow_html=True)
        for _, r in pdf.iterrows():
            th = r["Thesis"] if r["Thesis"] else "No thesis"
            e = "▲" if r["G/L %"] >= 0 else "▼"
            st.markdown(f"**{r['Ticker']}** {e} {r['G/L %']:+.2f}% — _{th}_")
    else:
        st.caption("No holdings yet. Add your first position above.")


# ═══════════════════════════════════════════════════════════════════════
# TAB 7: WATCHLIST
# ═══════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown('<div class="shdr">Watchlist</div>', unsafe_allow_html=True)
    st.caption("Track securities you're monitoring but haven't bought. Define triggers for when to enter.")

    if "watchlist" not in st.session_state: st.session_state.watchlist = []

    with st.expander("◆ Import / Export Watchlist"):
        we1,we2=st.columns(2)
        with we1:
            wu=st.file_uploader("Import",type=["json"],key="wu")
            if wu:
                try: st.session_state.watchlist=json.loads(wu.read()); st.success("Imported.")
                except: st.error("Invalid.")
        with we2:
            if st.session_state.watchlist:
                st.download_button("⬇ Export",json.dumps(st.session_state.watchlist,indent=2),"watchlist.json","application/json")

    with st.form("add_w", clear_on_submit=True):
        wf1,wf2 = st.columns(2)
        wt = wf1.selectbox("Ticker", sorted(ALL_T.keys()), key="wt_add")
        wtr = wf2.text_input("Trigger Condition", placeholder="e.g., Buy if RSI drops below 35")
        wreason = st.text_input("Why watching?", placeholder="e.g., Strong Sharpe but overbought — waiting for pullback")
        if st.form_submit_button("◆ Add to Watchlist"):
            st.session_state.watchlist.append({
                "ticker": wt, "trigger": wtr, "reason": wreason,
                "date_added": datetime.now().strftime("%Y-%m-%d"),
            })
            st.rerun()

    if st.session_state.watchlist:
        for i, w in enumerate(st.session_state.watchlist):
            t = w["ticker"]
            combo = pd.concat([sector_df, stock_df], ignore_index=True)
            m = combo[combo["Ticker"]==t]

            # Check trigger
            trigger_met = False
            if m is not None and not m.empty and w.get("trigger"):
                r = m.iloc[0]
                trig = w["trigger"].lower()
                if "rsi" in trig and "below" in trig:
                    try:
                        threshold = float(''.join(c for c in trig.split("below")[-1] if c.isdigit() or c=='.'))
                        trigger_met = r["RSI"] < threshold
                    except: pass
                elif "rsi" in trig and "above" in trig:
                    try:
                        threshold = float(''.join(c for c in trig.split("above")[-1] if c.isdigit() or c=='.'))
                        trigger_met = r["RSI"] > threshold
                    except: pass

            # Correlation to portfolio
            port_corr_val = None
            if st.session_state.portfolio and t in ret.columns:
                pt_in = [h["ticker"] for h in st.session_state.portfolio if h["ticker"] in ret.columns]
                if pt_in:
                    wts_d = {}
                    for h in st.session_state.portfolio:
                        if h["ticker"] in prices.columns:
                            cp = safe_last(prices[h["ticker"]])
                            if cp: wts_d[h["ticker"]] = h["shares"] * cp
                    tw_d = sum(wts_d.values())
                    if tw_d > 0:
                        wts_d = {k:v/tw_d for k,v in wts_d.items()}
                        pr_w = pd.Series(0.0, index=ret.index)
                        for tk, wt_v in wts_d.items():
                            if tk in ret.columns: pr_w = pr_w.add(ret[tk]*wt_v, fill_value=0)
                        corr_df = pd.concat([ret[t], pr_w], axis=1).dropna()
                        if len(corr_df) > 20:
                            port_corr_val = corr_df.corr().iloc[0,1]

            status_icon = "🟢 TRIGGER MET" if trigger_met else "⏳ Watching"
            with st.expander(f"**{t}** — {ALL_T.get(t,t)} | {status_icon}", expanded=trigger_met):
                if not m.empty:
                    r = m.iloc[0]
                    wm = st.columns(6)
                    wm[0].metric("Price", f"${r['Price']:.2f}")
                    wm[1].metric("RSI", f"{r['RSI']:.1f}")
                    wm[2].metric("Sharpe", f"{r['Sharpe']:.3f}")
                    wm[3].metric("Rank", f"#{int(r['Rank'])}")
                    wm[4].metric("30d Return", f"{r['R_30d']:+.2f}%")
                    if port_corr_val is not None:
                        wm[5].metric("Corr. to Portfolio", f"{port_corr_val:.3f}")

                st.markdown(f"**Why watching:** {w.get('reason', 'N/A')}")
                st.markdown(f"**Trigger:** {w.get('trigger', 'N/A')}")
                st.caption(f"Added: {w.get('date_added', 'N/A')}")
                if st.button(f"🗑 Remove", key=f"rw_{i}"):
                    st.session_state.watchlist.pop(i); st.rerun()
    else:
        st.caption("No tickers on watchlist yet. Add securities above.")


# ═══════════════════════════════════════════════════════════════════════
# TAB 8: THESIS JOURNAL
# ═══════════════════════════════════════════════════════════════════════
with tabs[8]:
    st.markdown('<div class="shdr">Investment Thesis Journal</div>', unsafe_allow_html=True)

    if "theses" not in st.session_state: st.session_state.theses = []

    with st.form("tf", clear_on_submit=True):
        tc1,tc2 = st.columns([1,3])
        tm=tc1.text_input("Month",value=datetime.now().strftime("%B %Y"))
        tt=tc2.text_input("Title",placeholder="e.g., Defensive Rotation — Overweighting Healthcare")
        tb=st.text_area("Market Outlook & Analysis",height=200,placeholder="What does the data show? What are you doing and why? Be specific. Reference metrics.")
        tp=st.text_input("Actions Taken",placeholder="e.g., Added XLV 5 shares at $490")
        tl=st.text_area("Lessons Learned (from last month)",height=80,placeholder="What did I get right? What did I get wrong? What would I do differently?")
        if st.form_submit_button("◆ Save Thesis") and tb:
            # Snapshot portfolio + watchlist + market
            port_snap = json.dumps(st.session_state.portfolio) if st.session_state.portfolio else "[]"
            watch_snap = json.dumps(st.session_state.watchlist) if st.session_state.watchlist else "[]"
            st.session_state.theses.insert(0,{
                "month":tm,"title":tt,"body":tb,"positions":tp,"lessons":tl,
                "saved":datetime.now().strftime("%Y-%m-%d %H:%M"),
                "snapshot":{"spy":spy_v,"vix":vix_v,"tnx":tnx_v,"regime":regime,
                            "rotation":rot_sig_20,"yc_spread":yc_spread},
                "portfolio_snapshot": port_snap,
                "watchlist_snapshot": watch_snap,
            })
            st.success("Thesis saved with portfolio + watchlist snapshot.")

    if st.session_state.theses:
        te1,te2=st.columns(2)
        with te1: st.download_button("⬇ Export Theses",json.dumps(st.session_state.theses,indent=2),"theses.json","application/json")
        with te2:
            tu=st.file_uploader("Import",type=["json"],key="tu")
            if tu:
                try: st.session_state.theses=json.loads(tu.read()); st.success("Imported.")
                except: st.error("Invalid.")
        st.markdown("---")
        for i,t in enumerate(st.session_state.theses):
            sn=t.get("snapshot",{})
            ss_parts=[]
            if sn.get("spy"): ss_parts.append(f"SPY ${sn['spy']:,.2f}")
            if sn.get("vix"): ss_parts.append(f"VIX {sn['vix']:.1f}")
            if sn.get("tnx"): ss_parts.append(f"10Y {sn['tnx']:.2f}%")
            if sn.get("regime"): ss_parts.append(sn["regime"])
            if sn.get("rotation"): ss_parts.append(f"Rotation: {sn['rotation']}")
            if sn.get("yc_spread") is not None: ss_parts.append(f"YC: {sn['yc_spread']:+.2f}%")
            ss = " · ".join(ss_parts)

            with st.expander(f"◆ {t['month']} — {t.get('title','Untitled')}",expanded=(i==0)):
                if ss: st.caption(f"Market snapshot: {ss}")
                st.markdown(t["body"])
                if t.get("positions"): st.markdown(f"**Actions:** {t['positions']}")
                if t.get("lessons"): st.markdown(f"**Lessons Learned:** {t['lessons']}")
                # Show portfolio at time of writing
                if t.get("portfolio_snapshot"):
                    try:
                        ps = json.loads(t["portfolio_snapshot"])
                        if ps:
                            with st.expander("Portfolio at time of writing"):
                                st.json(ps)
                    except: pass
                st.caption(f"Saved: {t.get('saved','')}")
                if st.button("🗑 Delete",key=f"dt{i}"): st.session_state.theses.pop(i); st.rerun()
    else:
        st.caption("No thesis entries yet. Write your first monthly outlook above.")

# PDF Export
try:
    st.markdown("---")
    st.markdown('<div class="shdr">PDF Research Snapshot</div>', unsafe_allow_html=True)
    st.caption("Generate a text snapshot of the current dashboard state to save or share.")
    if st.button("📄 Generate Research Snapshot"):
        snapshot_lines = [
            f"EQUITY SECTOR ANALYZER — Research Snapshot",
            f"Generated: {now_utc.strftime('%Y-%m-%d %H:%M')} UTC",
            f"By: Cameron Camarotti | github.com/cameroncc333 | allaroundservice.com",
            f"",
            f"=== MARKET CONTEXT ===",
            f"S&P 500: ${spy_v:,.2f} ({spy_chg:+.2f}%)" if spy_v else "",
            f"VIX: {vix_v:.2f}" if vix_v else "",
            f"10Y Yield: {tnx_v:.2f}%" if tnx_v else "",
            f"Yield Curve (10Y-3M): {yc_spread:+.2f}% [{yc_label}]" if yc_spread is not None else "",
            f"Regime: {regime}",
            f"Rotation: {rot_sig_20} (20d), {rot_sig_60} (60d)",
            f"",
            f"=== TOP SIGNAL ===",
            ts if ts else "No signals",
            f"",
            f"=== SECTOR RANKINGS ===",
        ]
        if not sector_df.empty:
            for _, r in sector_df.iterrows():
                snapshot_lines.append(f"  #{int(r['Rank'])} {r['Ticker']} ({r['Name']}) — Sharpe {r['Sharpe']:.3f}, RSI {r['RSI']:.1f}, {r['Signal']}")
        snapshot_lines += [f"", f"=== MEGA-CAP RANKINGS ==="]
        if not stock_df.empty:
            for _, r in stock_df.iterrows():
                snapshot_lines.append(f"  #{int(r['Rank'])} {r['Ticker']} ({r['Name']}) — Sharpe {r['Sharpe']:.3f}, RSI {r['RSI']:.1f}, {r['Signal']}")

        if st.session_state.portfolio:
            snapshot_lines += [f"", f"=== PORTFOLIO ===", f"Total Value: ${tv:,.2f} | G/L: ${tgl:,.2f} ({tglp:+.2f}%)"]
            for h in st.session_state.portfolio:
                snapshot_lines.append(f"  {h['ticker']}: {h['shares']} shares @ ${h['cost_basis']:.2f} — {h.get('thesis','')}")

        if st.session_state.theses:
            latest = st.session_state.theses[0]
            snapshot_lines += [f"", f"=== LATEST THESIS ({latest['month']}) ===", latest.get("body","")]

        snapshot_text = "\n".join(snapshot_lines)
        st.download_button("⬇ Download Snapshot (.txt)", snapshot_text, "research_snapshot.txt", "text/plain")
        st.text_area("Preview:", snapshot_text, height=300)
except Exception:
    pass


# ═══════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="tftr">
    ◆ EQUITY SECTOR ANALYZER v3.0 &nbsp;·&nbsp; Cameron Camarotti &nbsp;·&nbsp;
    <a href="https://github.com/cameroncc333">github.com/cameroncc333</a> &nbsp;·&nbsp;
    <a href="https://allaroundservice.com">allaroundservice.com</a><br>
    30+ metrics · Fama-French 5-factor · Black-Scholes · Monte Carlo · Live data · Not financial advice<br>
    {datetime.now().strftime("%Y")} · Mill Creek High School · Hoschton, GA
</div>
""", unsafe_allow_html=True)
