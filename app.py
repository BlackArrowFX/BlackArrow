import streamlit as st
import re
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX 4H/1H Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

st.title("🏹 BlackArrowFX: Multi-Timeframe Execution Engine")
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
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0, step=0.0)

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
        manual_profit = st.number_input("Profit Made ($)", min_value=0.0, value=current_risk_usd * 2, step=0.0)
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
col_p0_1, col_p0_2 = st.columns(2)
with col_p0_1:
    trade_limit_ok = st.session_state.trade_count < 3
    st.checkbox("Daily Trade Limit (Max 3)", value=trade_limit_ok, disabled=True)
with col_p0_2:
    st.checkbox("News Cleared", value=news_ok, disabled=True)

if not trade_limit_ok or st.session_state.daily_loss_total >= max_daily_risk_limit:
    st.error("🛑 TRADING LOCKED: Daily limits reached.")
    st.stop()

# ---------------- SIDE-BY-SIDE ANALYSIS (4H & 1H) ---------------- #
st.markdown("---")
col_4h, col_1h = st.columns(2)

with col_4h:
    st.header("⏳ PHASE 1: 4H BIAS")
    htf_bias = st.radio("4H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging ↔️"], key="4h_trend")
    
    s4_h = st.number_input("4H Swing High Price", value=0.0, format="%.2f", step=0.0, key="s4h")
    s4_l = st.number_input("4H Swing Low Price", value=0.0, format="%.2f", step=0.0, key="s4l")
    
    u4_ready = s4_h > 0 and s4_l > 0
    bias_4h_ok = st.checkbox("4H Trend Confirmed", disabled=not u4_ready, key="c4h")
    
    liq_4h = st.toggle("4H Liquidity Taken", key="l4h")
    
    if bias_4h_ok and htf_bias != "Ranging ↔️" and liq_4h:
        st.success("✅ 4H BIAS VALID")
        phase1_ready = True
    else:
        st.warning("⏳ Complete 4H Analysis")
        phase1_ready = False

with col_1h:
    st.header("⏱️ PHASE 2: 1H STRUCTURE")
    itf_trend = st.radio("1H Structure", ["Bullish ⬆️", "Bearish ⬇️", "Ranging ↔️"], key="1h_trend")
    
    s1_h = st.number_input("1H Swing High Price", value=0.0, format="%.2f", step=0.0, key="s1h")
    s1_l = st.number_input("1H Swing Low Price", value=0.0, format="%.2f", step=0.0, key="s1l")
    
    u1_ready = s1_h > 0 and s1_l > 0
    bias_1h_ok = st.checkbox("1H Structure Confirmed", disabled=not u1_ready, key="c1h")
    
    # Premium/Discount check for 1H
    p_d = st.radio("Price Value (1H Range)", ["Discount (Buy)", "Premium (Sell)", "Equilibrium"], key="pd")

    if bias_1h_ok and itf_trend != "Ranging ↔️":
        st.success("✅ 1H STRUCTURE VALID")
        phase2_ready = True
    else:
        st.warning("⏳ Complete 1H Analysis")
        phase2_ready = False

# ---------------- POI SELECTION ---------------- #
st.markdown("---")
st.header("📋 POI TRADING PLAN")
raw_text = st.text_area("Paste 1H POI Zones", height=80, placeholder="Example: 1H Order Block $2340 - $2345")

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
    selected_poi = st.selectbox("Select Active 1H POI", list(POI_DB.keys()))
    price = st.number_input("Current Market Price", value=0.0, format="%.2f", step=0.0)
    target = POI_DB[selected_poi]
    if target["low"] <= price <= target["high"]:
        st.success("✅ PRICE AT POI")
        inside_zone = True
    else:
        st.error("❌ PRICE OUTSIDE POI")

# ---------------- LTF TRIGGER ---------------- #
st.markdown("---")
st.header("⚡ PHASE 3: LTF ENTRY (1M/5M)")
c_mss = st.checkbox("MSS / CHoCH Confirmed")
c_fvg = st.toggle("FVG/OB Present for Entry")

# All confluences check
all_confluences = phase1_ready and phase2_ready and inside_zone and c_mss and c_fvg

# ---------------- POSITION CALCULATOR ---------------- #
st.markdown("---")
st.header("🚀 PHASE 4: EXECUTION ENGINE")
calc_c1, calc_c2, calc_c3 = st.columns(3)

with calc_c1:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f", step=0.0, key="entry")
    sl = st.number_input("Stop Loss", value=0.0, format="%.2f", step=0.0, key="sl")

with calc_c2:
    if entry > 0 and sl > 0:
        pips = abs(entry - sl) * 10
        lot_size = current_risk_usd / (pips * 10) if pips > 0 else 0
        st.metric("Lot Size", round(lot_size, 2))
        
        if all_confluences and news_ok:
            st.success("🔥 ALL CONFLUENCES MET: EXECUTE")
        else:
            st.error("🚫 DO NOT ENTER: Missing Confluences")

with calc_c3:
    if entry > 0 and sl > 0:
        diff = abs(entry - sl)
        is_buy = entry > sl
        st.write(f"TP1 (1.5R): **{round(entry + (diff * 1.5 if is_buy else -diff * 1.5), 2)}**")
        st.write(f"TP2 (3.0R): **{round(entry + (diff * 3.0 if is_buy else -diff * 3.0), 2)}**")
