import streamlit as st
import re
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX 4H/1H Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

st.title("🏹 BlackArrowFX: 4H/1H Execution Engine")
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
        # Changed to 0.0 step for easier manual key-in
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
        # Changed to 0.0 step for manual key-in
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
col1, col2 = st.columns(2)
with col1:
    trade_limit_ok = st.session_state.trade_count < 3
    st.checkbox("Daily Trade Limit (Max 3)", value=trade_limit_ok, disabled=True)
with col2:
    st.checkbox("News Cleared", value=news_ok, disabled=True)

if not trade_limit_ok or st.session_state.daily_loss_total >= max_daily_risk_limit:
    st.error("🛑 TRADING LOCKED: Daily limits reached.")
    st.stop()

# ---------------- PHASE 1: 4H BIAS & SWING POINTS ---------------- #
st.markdown("---")
st.header("PHASE 1: 4H DIRECTIONAL BIAS")
col_bias1, col_bias2 = st.columns(2)

with col_bias1:
    st.subheader("4H Market Structure")
    htf_bias = st.radio("Current Trend", ["Bullish (HH/HL) ⬆️", "Bearish (LH/LL) ⬇️", "Ranging/Unclear ↔️"])
    
    # KEY FIX: Step=0.0 removes the +/- buttons and allows direct typing
    swing_h_val = st.number_input("Input 4H Swing High Price", value=0.0, format="%.2f", step=0.0)
    swing_l_val = st.number_input("Input 4H Swing Low Price", value=0.0, format="%.2f", step=0.0)
    
    inputs_ready = swing_h_val > 0 and swing_l_val > 0
    
    bias_confirmed = st.checkbox(
        "4H Trend Confirmed", 
        disabled=not inputs_ready,
        help="Type in the High/Low prices to unlock."
    )
    
    if bias_confirmed and htf_bias != "Ranging/Unclear ↔️":
        st.success("✅ 4H TREND VALIDATED")
        trend_tick = True
    else:
        st.warning("⏳ Enter Prices & Confirm Trend")
        trend_tick = False

with col_bias2:
    st.subheader("Liquidity & Value")
    liq_sweep = st.toggle("Liquidity Taken (PDH/PDL or Equal Levels)")
    premium_discount = st.radio("Price Location", ["Discount (Buy Zone)", "Premium (Sell Zone)", "Equilibrium (No Trade)"])

bias_ok = trend_tick and liq_sweep

# ---------------- PHASE 2: 1H POI TRADING PLAN ---------------- #
st.markdown("---")
st.header("PHASE 2: 1H POI TRADING PLAN")
raw_text = st.text_area("Paste 1H POI Zones", height=100, placeholder="Example: 1H Order Block $2340 - $2345")

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
    st.success(f"Parsed {len(POI_DB)} Zones")
    selected_poi = st.selectbox("Select Active 1H POI", list(POI_DB.keys()))
    # Step=0.0 for manual typing
    price = st.number_input("Current Market Price", value=0.0, format="%.2f", step=0.0)
    target = POI_DB[selected_poi]
    if target["low"] <= price <= target["high"]:
        st.success("✅ PRICE AT 1H POI")
        inside_zone = True
    else:
        st.error("❌ PRICE OUTSIDE 1H POI")

# ---------------- PHASE 3: LTF TRIGGER (1M/5M) ---------------- #
st.markdown("---")
st.header("PHASE 3: LTF ENTRY TRIGGER")
c_mss = st.checkbox("MSS / CHoCH (1M/5M Shift)")
c_fvg = st.toggle("FVG/OB Refinement Present")

trigger_ok = c_mss and c_fvg and inside_zone and bias_ok

# ---------------- PHASE 4: EXECUTION & POSITION ---------------- #
st.markdown("---")
st.header("PHASE 4: EXECUTION ENGINE")
calc_c1, calc_c2, calc_c3 = st.columns(3)

with calc_c1:
    # Step=0.0 for manual typing
    entry = st.number_input("Entry Price", value=0.0, format="%.2f", step=0.0)
    sl = st.number_input("Stop Loss", value=0.0, format="%.2f", step=0.0)

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
        is_buy = entry > sl
        st.write(f"TP1 (1.5R): **{round(entry + (diff * 1.5 if is_buy else -diff * 1.5), 2)}**")
        st.write(f"TP2 (3.0R): **{round(entry + (diff * 3.0 if is_buy else -diff * 3.0), 2)}**")
