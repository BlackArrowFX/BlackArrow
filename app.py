import streamlit as st
import re
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX POI Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

st.title("🏹 BlackArrowFX: Top-Down Execution Engine")
st.caption(f"Current Server Time: {dt_string}")
st.markdown("---")

# ---------------- SESSION STATE ---------------- #
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11
if "trade_count" not in st.session_state:
    st.session_state.trade_count = 0
if "daily_loss_total" not in st.session_state:
    st.session_state.daily_loss_total = 0.0

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

    max_daily_risk_limit = st.session_state.balance * 0.10
    st.info(f"Active Risk: ${round(current_risk_usd, 2)}")
    
    st.header("🌍 News Filter")
    st.markdown("[Check Forex Factory 📅](https://www.forexfactory.com/)")
    news_ok = st.toggle("No High Impact News")

    st.markdown("---")
    st.header("📊 Daily Journal")
    st.write(f"Trades Taken: **{st.session_state.trade_count} / 3**")
    
    loss_disabled = st.session_state.trade_count >= 3 or st.session_state.daily_loss_total >= max_daily_risk_limit
    if st.button("❌ RECORD LOSS", disabled=loss_disabled, use_container_width=True):
        st.session_state.balance -= current_risk_usd
        st.session_state.daily_loss_total += current_risk_usd
        st.session_state.trade_count += 1
        st.rerun()

    win_disabled = st.session_state.trade_count >= 3
    with st.expander("✅ RECORD WIN", expanded=not win_disabled):
        manual_profit = st.number_input("Profit Made ($)", min_value=0.0, value=current_risk_usd * 2)
        if st.button("Add to Balance", disabled=win_disabled):
            st.session_state.balance += manual_profit
            st.session_state.trade_count += 1
            st.rerun()

    if st.button("🔄 Reset Daily Limits"):
        st.session_state.trade_count = 0
        st.session_state.daily_loss_total = 0.0
        st.rerun()

# ---------------- PHASE 0: HARD FILTERS ---------------- #
st.header("PHASE 0: PRE-FLIGHT CHECK")
col1, col2 = st.columns(2)
with col1:
    trade_limit_ok = st.session_state.trade_count < 3
    st.checkbox("Daily Trade Limit (Max 3)", value=trade_limit_ok, disabled=True)
with col2:
    st.checkbox("News Cleared", value=news_ok, disabled=True)

if not trade_limit_ok or st.session_state.daily_loss_total >= max_daily_risk_limit:
    st.error("🛑 TRADING LOCKED: Limits Reached.")
    st.stop()

# ---------------- PHASE 1: TOP-DOWN ANALYSIS ---------------- #
st.markdown("---")
st.header("PHASE 1: TOP-DOWN NARRATIVE")
col_htf1, col_htf2 = st.columns(2)

with col_htf1:
    htf_trend = st.radio("Daily/4H Trend (Order Flow)", ["Bullish ⬆️", "Bearish ⬇️", "Ranging ↔️"])
    htf_confirm = st.checkbox("Structure Break Confirmed on HTF?")

with col_htf2:
    liq_sweep = st.toggle("Liquidity Taken? (PDH/PDL/Equal Levels)")
    market_bias_ok = htf_trend != "Ranging ↔️" and htf_confirm and liq_sweep

if market_bias_ok:
    st.success("🎯 NARRATIVE ALIGNED: Proceed to POI Selection")
else:
    st.warning("⚠️ WAITING FOR CLEAR BIAS & LIQUIDITY SWEEP")

# ---------------- PHASE 2: POI PLAN ---------------- #
st.markdown("---")
st.header("PHASE 2: POI TRADING PLAN")
raw_text = st.text_area("Paste POI zones from Analysis", height=100, placeholder="Example: 1H Demand $2340 - $2345")

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

inside_zone = False
if POI_DB:
    selected_poi = st.selectbox("Select Active POI", list(POI_DB.keys()))
    price = st.number_input("Current Market Price", value=0.0, format="%.2f")
    target = POI_DB[selected_poi]
    if target["low"] <= price <= target["high"]:
        st.success("✅ PRICE AT POINT OF INTEREST")
        inside_zone = True
    else:
        st.error("❌ PRICE OUTSIDE POI")

# ---------------- PHASE 3: LTF CONFIRMATION ---------------- #
st.markdown("---")
st.header("PHASE 3: LTF ENTRY TRIGGER (1M/5M)")
c_mss = st.checkbox("MSS / CHoCH (Lower Timeframe Shift)")
c_fvg = st.toggle("FVG/OB Refinement Entry")

trigger_ok = c_mss and c_fvg and inside_zone and market_bias_ok

# ---------------- POSITION CALCULATOR ---------------- #
st.markdown("---")
st.header("PHASE 4: EXECUTION & POSITION")
calc_c1, calc_c2, calc_c3 = st.columns(3)

with calc_c1:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    sl = st.number_input("Stop Loss", value=0.0, format="%.2f")

with calc_c2:
    if entry > 0 and sl > 0:
        pips = abs(entry - sl) * 10
        lot_size = current_risk_usd / (pips * 10) if pips > 0 else 0
        st.metric("Lot Size", round(lot_size, 2))
        if trigger_ok and news_ok:
            st.success("🚀 EXECUTE TRADE")
        else:
            st.error("🚫 DO NOT ENTER")

with calc_c3:
    if entry > 0 and sl > 0:
        diff = abs(entry - sl)
        st.write(f"TP1 (1.5R): **{round(entry + (diff * 1.5 if entry > sl else -diff * 1.5), 2)}**")
        st.write(f"TP2 (3.0R): **{round(entry + (diff * 3.0 if entry > sl else -diff * 3.0), 2)}**")
