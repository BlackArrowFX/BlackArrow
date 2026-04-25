import streamlit as st
import re
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX POI Engine", layout="wide")

# Real-time Date and Time
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

st.title("🏹 BlackArrowFX: POI Mechanical Trading Engine")
st.caption(f"Current Server Time: {dt_string}")
st.markdown("---")


# ---------------- SESSION STATE ---------------- #
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11
if "trade_count" not in st.session_state:
    st.session_state.trade_count = 0
if "daily_loss_total" not in st.session_state:
    st.session_state.daily_loss_total = 0.0
if "win_count" not in st.session_state:
    st.session_state.win_count = 0


# ---------------- SIDEBAR: RISK & JOURNAL ---------------- #
with st.sidebar:
    st.header("💰 Risk Engine")

    st.metric("Current Balance", f"${round(st.session_state.balance, 2)}")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 5.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)

    # Calculate 10% Max Daily Drawdown
    max_daily_risk_limit = st.session_state.balance * 0.10

    st.info(f"Active Risk: ${round(current_risk_usd, 2)}")
    
    st.header("🌍 News Filter")
    st.markdown("[Check Forex Factory 📅](https://www.forexfactory.com/)")
    news_ok = st.toggle("No High Impact News")

    st.markdown("---")
    st.header("📊 Daily Journal")
    
    st.write(f"Trades Taken: **{st.session_state.trade_count} / 3**")
    st.write(f"Daily Drawdown: **-${round(st.session_state.daily_loss_total, 2)}**")

    # 1. Record Loss Button
    loss_disabled = st.session_state.trade_count >= 3 or st.session_state.daily_loss_total >= max_daily_risk_limit
    if st.button("❌ RECORD LOSS", disabled=loss_disabled, use_container_width=True):
        st.session_state.balance -= current_risk_usd
        st.session_state.daily_loss_total += current_risk_usd
        st.session_state.trade_count += 1
        st.rerun()

    # 2. Record Win (Manual Input)
    win_disabled = st.session_state.trade_count >= 3
    with st.expander("✅ RECORD WIN", expanded=not win_disabled):
        manual_profit = st.number_input("Profit Made ($)", min_value=0.0, value=current_risk_usd * 2)
        if st.button("Add to Balance", disabled=win_disabled):
            st.session_state.balance += manual_profit
            st.session_state.win_count += 1
            st.session_state.trade_count += 1
            st.rerun()

    if st.button("🔄 Reset Daily Limits"):
        st.session_state.trade_count = 0
        st.session_state.daily_loss_total = 0.0
        st.session_state.win_count = 0
        st.rerun()


# ---------------- PHASE 0: HARD STOP LOGIC ---------------- #
st.header("PHASE 0: HARD FILTERS")
col1, col2 = st.columns(2)

with col1:
    trade_limit_ok = st.session_state.trade_count < 3
    st.checkbox("Daily Trade Limit (Max 3)", value=trade_limit_ok, disabled=True)
    if not trade_limit_ok:
        st.error("🛑 MAX TRADES REACHED")

with col2:
    st.checkbox("News Cleared", value=news_ok, disabled=True)
    if not news_ok:
        st.warning("⚠️ AWAITING NEWS CLEARANCE")

# Final Phase 0 Check
if not trade_limit_ok:
    st.stop()

if st.session_state.daily_loss_total >= max_daily_risk_limit:
    st.error(f"🛑 10% DAILY DRAWDOWN HIT (-${round(st.session_state.daily_loss_total, 2)})")
    st.stop()


# ---------------- PHASE 1: POI PLAN ---------------- #
st.markdown("---")
st.header("📋 POI Trading Plan")
raw_text = st.text_area("Paste POI zones here", height=150, placeholder="Extreme Supply $4710 - $4712")

POI_DB = {}
if raw_text:
    lines = raw_text.split("\n")
    for line in lines:
        line = line.strip().replace("–", "-")
        match = re.search(r"(\d{3,5}\.?\d*)\s*-\s*(\d{3,5}\.?\d*)", line)
        if match:
            low, high = float(match.group(1)), float(match.group(2))
            name = line.split("$")[0].strip() or f"Zone {len(POI_DB)+1}"
            POI_DB[name] = {"low": low, "high": high}

if POI_DB:
    st.success(f"Parsed {len(POI_DB)} Zones")
    selected_poi = st.selectbox("Select Target POI", list(POI_DB.keys()))
    price = st.number_input("Current XAUUSD Price", value=0.0, format="%.2f")
    
    target = POI_DB[selected_poi]
    if target["low"] <= price <= target["high"]:
        st.success("✅ PRICE INSIDE POI")
        inside_zone = True
    else:
        st.error("❌ PRICE OUTSIDE POI")
        inside_zone = False
else:
    inside_zone = False


# ---------------- PHASE 2: CONFLUENCE ---------------- #
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.header("HTF BIAS")
    trend = st.radio("Structure", ["Bullish", "Bearish", "Ranging"])
    htf_confirm = st.checkbox("HTF Confirmed")
with col_b:
    st.header("ENTRY TRIGGERS")
    mss = st.checkbox("MSS / CHoCH")
    sweep = st.checkbox("Liquidity Sweep")
    fvg_ob = st.toggle("FVG or OB Present")


# ---------------- POSITION CALCULATOR ---------------- #
st.markdown("---")
st.header("POSITION CALCULATOR")
calc_c1, calc_c2, calc_c3 = st.columns(3)

with calc_c1:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    sl = st.number_input("Stop Loss", value=0.0, format="%.2f")

with calc_c2:
    if entry > 0 and sl > 0:
        pips = abs(entry - sl) * 10
        lot_size = current_risk_usd / (pips * 10) if pips > 0 else 0
        st.metric("Lot Size", round(lot_size, 2))
        st.write(f"Total Risk: ${round(current_risk_usd, 2)}")

with calc_c3:
    if entry > 0 and sl > 0:
        diff = abs(entry - sl)
        st.write(f"TP1 (1.5R): **{round(entry + (diff * 1.5 if entry > sl else -diff * 1.5), 2)}**")
        st.write(f"TP2 (3.0R): **{round(entry + (diff * 3.0 if entry > sl else -diff * 3.0), 2)}**")
