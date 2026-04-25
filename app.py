import streamlit as st
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SESSION STATE INITIALIZATION ---------------- #
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11
if "trades_taken" not in st.session_state:
    st.session_state.trades_taken = 0

# ---------------- SIDEBAR: RISK & SYSTEM ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    asset_type = st.selectbox("Select Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"])
    symbol = st.text_input("Enter Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    
    st.metric("Current Balance", f"${round(st.session_state.balance, 2)}")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 5.0) # Matches your image (5.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=100.0)

    st.info(f"Active Risk: ${round(current_risk_usd, 2)}")

    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News", value=False)
    if not news_ok:
        st.error("🚨 SYSTEM LOCKED: News must be cleared.")

    # ---------------- DAILY JOURNAL (AS PER IMAGE) ---------------- #
    st.markdown("---")
    st.header("📊 Daily Journal")
    st.write(f"Trades Taken: **{st.session_state.trades_taken} / 3**")
    
    # Logic: Disable recording if limit reached
    limit_reached = st.session_state.trades_taken >= 3

    # Loss Recording
    if st.button("❌ RECORD LOSS", use_container_width=True, disabled=limit_reached):
        st.session_state.balance -= current_risk_usd
        st.session_state.trades_taken += 1
        st.rerun()

    # Win Recording
    with st.expander("✅ RECORD WIN", expanded=False):
        profit_made = st.number_input("Profit Made ($)", min_value=0.0, value=0.0, step=10.0)
        if st.button("Add to Balance", use_container_width=True, disabled=limit_reached):
            st.session_state.balance += profit_made
            st.session_state.trades_taken += 1
            st.rerun()

    st.markdown("---")
    if st.button("Reset Daily Limits", use_container_width=True):
        st.session_state.trades_taken = 0
        st.rerun()

# ---------------- MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Asset: {symbol} | Mode: {asset_type} | Server Time: {dt_string}")
st.markdown("---")

# ---------------- PHASE 0: PRE-FLIGHT CHECK ---------------- #
st.header("PHASE 0: PRE-FLIGHT CHECK")
c_check1, c_check2 = st.columns(2)
with c_check1:
    st.checkbox("Daily Trade Limit (Max 3)", value=st.session_state.trades_taken < 3, disabled=True)
with c_check2:
    st.checkbox("News Cleared", value=news_ok, disabled=True)

st.markdown("---")

# ---------------- QUAD TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c5m = st.columns(3) # Matching the image layout (4H, 1H, 5M)

# --- 4H BIAS ---
with c4h:
    st.subheader("⏳ 4H BIAS")
    htf_bias = st.radio("Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t")
    s4_h = st.number_input("4H Swing High", value=4743.63, format="%.2f", key="s4h")
    s4_l = st.number_input("4H Swing Low", value=4644.59, format="%.2f", key="s4l")
    bias_4h_ok = st.checkbox("4H Confirmed", key="4h_c", value=True)

# --- 1H STRUC ---
with c1h:
    st.subheader("⏱️ 1H STRUCTURE")
    itf_trend = st.radio("Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", index=1)
    s1_h = st.number_input("1H Swing High", value=4772.51, format="%.2f", key="s1h")
    s1_l = st.number_input("1H Swing Low", value=4657.52, format="%.2f", key="s1l")
    bias_1h_ok = st.checkbox("1H Confirmed", key="1h_c", value=True)

# --- 5M SHIFT ---
with c5m:
    st.subheader("⚡ 5M SHIFT")
    t5_trend = st.radio("Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="5m_t", index=1)
    s5_h = st.number_input("5M Swing High", value=4743.28, format="%.2f", key="s5h")
    s5_l = st.number_input("5M Swing Low", value=4657.52, format="%.2f", key="s5l")
    bias_5m_ok = st.checkbox("5M Confirmed", key="5m_c", value=True)

# ---------------- PHASE 2 & 3: EXECUTION ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns(2)

with col_poi:
    st.header("📋 POI PLAN")
    poi_notes = st.text_area("Paste 1H POI Zones", placeholder="Example: 1H Demand $2340 - $2345")

with col_exec:
    st.header("🚀 EXECUTION ENGINE")
    entry_p = st.number_input("Entry Price", value=0.0, format="%.2f")
    sl_p = st.number_input("Stop Loss", value=0.0, format="%.2f")
    
    # Lot Size Calculation (Standard Forex/Metal Logic)
    if entry_p > 0 and sl_p > 0:
        pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
        pips_dist = abs(entry_p - sl_p) / pip_factor
        if pips_dist > 0:
            # Standard calculation for lot size based on risk
            lot_size = (current_risk_usd / pips_dist) / 10
            st.metric("Calculated Lot Size", f"{round(lot_size, 2)}")
            st.write(f"📏 Distance: {round(pips_dist, 1)} pips")
