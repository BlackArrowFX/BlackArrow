import streamlit as st
from datetime import datetime

# ---------------- 1. INITIALIZE GLOBAL STATE ---------------- #
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11  
if "trades_taken" not in st.session_state:
    st.session_state.trades_taken = 0

# --- NEW: 5M STATE MANAGEMENT ---
if "m5_trend_val" not in st.session_state:
    st.session_state.m5_trend_val = "Select..."
if "m5_mss_price" not in st.session_state:
    st.session_state.m5_mss_price = 0.0
if "m5_bos_price" not in st.session_state:
    st.session_state.m5_bos_price = 0.0

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & SYSTEM ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    asset_type = st.selectbox("Select Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"])
    symbol = st.text_input("Enter Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    st.session_state.balance = st.number_input("Current Balance ($)", value=float(st.session_state.balance), step=10.0, format="%.2f")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)

    st.markdown("---")
    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News Active", value=False) 
    
    # ---------------- 3. THE JOURNAL COMPONENT ---------------- #
    st.markdown("---")
    st.header("📊 Daily Journal")
    st.write(f"Trades Taken: **{st.session_state.trades_taken} / 3**")
    limit_reached = st.session_state.trades_taken >= 3

    if st.button("❌ RECORD LOSS", use_container_width=True, disabled=limit_reached):
        st.session_state.balance -= current_risk_usd 
        st.session_state.trades_taken += 1
        st.rerun()

    with st.expander("✅ RECORD WIN", expanded=False):
        profit_made = st.number_input("Profit Made ($)", min_value=0.0, value=0.0, step=1.0)
        if st.button("Add to Balance", use_container_width=True, disabled=limit_reached):
            st.session_state.balance += profit_made
            st.session_state.trades_taken += 1
            st.rerun()

# ---------------- MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.markdown("---")

# ---------------- QUAD TIMEFRAME ANALYSIS (Condensed for Space) ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)
with c4h:
    htf_bias = st.radio("4H Bias", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t")
    bias_4h_ok = st.checkbox("4H Confirmed")
with c1h:
    itf_trend = st.radio("1H Structure", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", disabled=not bias_4h_ok)
    bias_1h_ok = st.checkbox("1H Confirmed", disabled=not bias_4h_ok)
with c30m:
    t30_trend = st.radio("30M Shift", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t", disabled=not bias_1h_ok)
    bias_30m_ok = st.checkbox("30M Confirmed", disabled=not bias_1h_ok)
with c15m:
    t15_trend = st.radio("15M Entry", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t", disabled=not bias_30m_ok)
    bias_15m_ok = st.checkbox("15M Confirmed", disabled=not bias_30m_ok)

# ---------------- ⚡ 5M MICRO-CONFIRMATION (DYNAMIC) ---------------- #
st.markdown("---")
st.subheader("⚡ 5M MICRO-CONFIRMATION")
c5_1, c5_2, c5_3 = st.columns(3)

with c5_1:
    # Use index to control radio button via session state
    trend_options = ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"]
    current_index = trend_options.index(st.session_state.m5_trend_val)
    
    m5_trend = st.radio(
        "5M Current Trend", 
        trend_options, 
        index=current_index,
        key="m5_trend_radio",
        disabled=not bias_15m_ok
    )
    st.session_state.m5_trend_val = m5_trend

with c5_2:
    label_bos = "BOS Price (HH to break)" if m5_trend == "Bullish ⬆️" else "BOS Price (LL to break)"
    label_mss = "MSS Price (HL to break)" if m5_trend == "Bullish ⬆️" else "MSS Price (LH to break)"
    
    m5_bos_p = st.number_input(label_bos, value=st.session_state.m5_bos_price, format="%.2f")
    m5_mss_p = st.number_input(label_mss, value=st.session_state.m5_mss_price, format="%.2f")
    
    # Update state immediately when user types
    st.session_state.m5_bos_price = m5_bos_p
    st.session_state.m5_mss_price = m5_mss_p

with c5_3:
    st.write("**Confirmation Action**")
    
    # 🧠 THE SMART LOGIC FOR AUTO-UPDATING
    do_bos = st.checkbox("BOS Confirmed (Reset Price)")
    do_mss = st.checkbox("MSS Confirmed (Flip Trend)")

    if do_bos:
        st.session_state.m5_bos_price = 0.0 # Clear price
        st.toast("BOS Acknowledged. Price Reset.")
        st.rerun()

    if do_mss:
        # Flip the Trend logic
        if st.session_state.m5_trend_val == "Bullish ⬆️":
            st.session_state.m5_trend_val = "Bearish ⬇️"
        elif st.session_state.m5_trend_val == "Bearish ⬇️":
            st.session_state.m5_trend_val = "Bullish ⬆️"
        
        st.session_state.m5_mss_price = 0.0 # Clear price
        st.toast("Trend Flipped & MSS Reset!")
        st.rerun()

# ---------------- PHASE 2.5: ORDER FLOW ---------------- #
st.markdown("---")
st.header("🐋 PHASE 2.5: ORDER FLOW")
c_of1, c_of2 = st.columns(2)
with c_of1:
    shark_type = st.radio("Absorption?", ["None", "Shark Buy (Absorbing Sells)", "Shark Sell (Absorbing Buys)"])
with c_of2:
    delta_strength = st.selectbox("Delta Strength", ["Weak", "Moderate", "Strong"])

# Smart Orderflow Logic
orderflow_ok = False
if shark_type == "Shark Buy (Absorbing Sells)" and "Bullish" in htf_bias:
    orderflow_ok = True
elif shark_type == "Shark Sell (Absorbing Buys)" and "Bearish" in htf_bias:
    orderflow_ok = True

# ---------------- PHASE 2 & 3: EXECUTION ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f")
    trade_dir = st.radio("Position Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    pip_factor = 0.1 if "METAL" in asset_type else (0.0001 if "FOREX" in asset_type else 1.0)
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f")
    sl_val = st.number_input("Manual Stop Loss", value=0.0, format="%.2f")
    
    if entry_val > 0 and sl_val > 0 and trade_dir != "Select...":
        pips_dist = abs(entry_val - sl_val) / pip_factor
        
        if not orderflow_ok:
            st.warning("⚠️ WAIT: No institutional confirmation (Order Flow)")
        else:
            lot_size = (current_risk_usd / pips_dist) / 10 if pips_dist > 0 else 0
            st.metric("Calculated Lot Size", f"{round(lot_size, 2)}")
            st.success("🔥 TRADE FULLY VALIDATED")
