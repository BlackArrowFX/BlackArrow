import streamlit as st
from datetime import datetime

# ---------------- 1. INITIALIZE GLOBAL STATE ---------------- #
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11  
if "trades_taken" not in st.session_state:
    st.session_state.trades_taken = 0

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
    
    st.session_state.balance = st.number_input(
        "Current Balance ($)", 
        value=float(st.session_state.balance), 
        step=10.0, 
        format="%.2f"
    )
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)

    # ---------------- 2. NEWS FILTER ---------------- #
    st.markdown("---")
    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News Active", value=False) 
    
    if not news_ok:
        st.error("🚨 SYSTEM LOCKED: Confirm no news.")
    else:
        st.success("✅ News Cleared")

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

    if st.button("Reset Daily Limits", use_container_width=True):
        st.session_state.trades_taken = 0
        st.rerun()

# ---------------- MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Asset: {symbol} | Mode: {asset_type} | Server Time: {dt_string}")
st.markdown("---")

# ---------------- QUAD TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)

with c4h:
    st.subheader("⏳ 4H BIAS")
    htf_bias = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", disabled=not news_ok)
    h_lock = not news_ok or htf_bias == "Select..."
    s4_h = st.number_input("Swing High", value=0.0, format="%.2f", key="s4h", disabled=h_lock)
    s4_l = st.number_input("Swing Low", value=0.0, format="%.2f", key="s4l", disabled=h_lock)
    bias_4h_ok = st.checkbox("4H Confirmed", key="4h_c", disabled=h_lock or not (s4_h > 0 and s4_l > 0))

with c1h:
    st.subheader("⏱️ 1H STRUC")
    itf_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", disabled=not bias_4h_ok)
    i_lock = not bias_4h_ok or itf_trend == "Select..."
    s1_h = st.number_input("1H High", value=0.0, format="%.2f", key="s1h", disabled=i_lock)
    s1_l = st.number_input("1H Low", value=0.0, format="%.2f", key="s1l", disabled=i_lock)
    bias_1h_ok = st.checkbox("1H Confirmed", key="1h_c", disabled=i_lock or not (s1_h > 0 and s1_l > 0))

with c30m:
    st.subheader("⚡ 30M SHIFT")
    t30_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t", disabled=not bias_1h_ok)
    m30_lock = not bias_1h_ok or t30_trend == "Select..."
    s30_h = st.number_input("30M High", value=0.0, format="%.2f", key="s30h", disabled=m30_lock)
    s30_l = st.number_input("30M Low", value=0.0, format="%.2f", key="s30l", disabled=m30_lock)
    bias_30m_ok = st.checkbox("30M Confirmed", key="30m_c", disabled=m30_lock or not (s30_h > 0 and s30_l > 0))

with c15m:
    st.subheader("🎯 15M ENTRY")
    t15_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t", disabled=not bias_30m_ok)
    m15_lock = not bias_30m_ok or t15_trend == "Select..."
    s15_h = st.number_input("15M High", value=0.0, format="%.2f", key="s15h", disabled=m15_lock)
    s15_l = st.number_input("15M Low", value=0.0, format="%.2f", key="s15l", disabled=m15_lock)
    bias_15m_ok = st.checkbox("15M Confirmed", key="15m_c", disabled=m15_lock or not (s15_h > 0 and s15_l > 0))

# ---------------- 5M MICRO-CONFIRMATION ---------------- #
st.markdown("---")
st.subheader("⚡ 5M MICRO-CONFIRMATION")
c5_1, c5_2, c5_3 = st.columns(3)

with c5_1:
    m5_trend = st.radio("5M Current Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="m5_t", disabled=not bias_15m_ok)
    m5_lock = not bias_15m_ok or m5_trend == "Select..."

with c5_2:
    label_bos = "BOS Price"
    label_mss = "MSS Price"
    if m5_trend == "Bearish ⬇️":
        label_bos = "BOS Price (LL to break)"
        label_mss = "MSS Price (LH to break)"
    elif m5_trend == "Bullish ⬆️":
        label_bos = "BOS Price (HH to break)"
        label_mss = "MSS Price (HL to break)"
    
    m5_bos_p = st.number_input(label_bos, value=0.0, format="%.2f", disabled=m5_lock)
    m5_mss_p = st.number_input(label_mss, value=0.0, format="%.2f", disabled=m5_lock)

with c5_3:
    st.write("**Confirmation Type**")
    m5_bos_ok = st.checkbox("BOS Confirmed", disabled=m5_bos_p == 0)
    m5_mss_ok = st.checkbox("MSS Confirmed", disabled=m5_mss_p == 0)

# ---------------- PHASE 2.5: ORDER FLOW (NEW) ---------------- #
st.markdown("---")
st.header("🐋 PHASE 2.5: ORDER FLOW (FOOTPRINT)")
system_unlocked = bias_15m_ok and news_ok

c_of1, c_of2 = st.columns(2)
with c_of1:
    shark_type = st.radio(
        "Absorption Detected?",
        ["None", "Shark Buy (Absorbing Sells)", "Shark Sell (Absorbing Buys)"],
        disabled=not system_unlocked
    )

with c_of2:
    delta_strength = st.selectbox(
        "Delta Strength",
        ["Weak", "Moderate", "Strong"],
        disabled=not system_unlocked
    )

# --- SMART LOGIC ---
orderflow_ok = False
if shark_type == "Shark Buy (Absorbing Sells)" and "Bullish" in htf_bias:
    orderflow_ok = True
elif shark_type == "Shark Sell (Absorbing Buys)" and "Bearish" in htf_bias:
    orderflow_ok = True

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Trading Zone", ["Select...", "Swing High", "Swing Low", "Supply Zone", "Demand Zone", "Order Block", "FVG"], disabled=not system_unlocked)
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    trade_dir = st.radio("Position Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True, disabled=not system_unlocked)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    
    calc_sl = 0.0
    if zone_price > 0 and trade_dir != "Select...":
        calc_sl = zone_price - (15 * pip_factor) if trade_dir == "LONG 🔵" else zone_price + (15 * pip_factor)

    sl_val = st.number_input("Stop Loss (15 Pips)", value=calc_sl, format="%.2f", disabled=not system_unlocked)
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    
    if entry_val > 0 and sl_val > 0 and trade_dir != "Select...":
        pips_dist = abs(entry_val - sl_val) / pip_factor
        
        # FINAL VALIDATION GATE
        if not orderflow_ok:
            st.warning("⚠️ WAIT: No institutional confirmation (Order Flow)")
        elif pips_dist > 0:
            lot_size = (current_risk_usd / pips_dist) / 10
            st.metric("Calculated Lot Size", f"{round(lot_size, 2)}")
            st.write(f"📏 Dist: {round(pips_dist, 1)} pips | 💵 Risk: ${round(current_risk_usd, 2)}")
            
            if m5_bos_ok: st.success("📈 BOS Confirmed")
            if m5_mss_ok: st.info("🎯 MSS Confirmed")
            st.success("🔥 TRADE FULLY VALIDATED")
