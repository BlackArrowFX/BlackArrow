import streamlit as st
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & ASSET ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    symbol = st.text_input("Enter Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    if "balance" not in st.session_state:
        st.session_state.balance = 2146.11
    
    st.metric("Current Balance", f"${round(st.session_state.balance, 2)}")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)

    max_daily_risk_limit = st.session_state.balance * 0.10
    
    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News")

    if "trade_count" not in st.session_state:
        st.session_state.trade_count = 0
    if "daily_loss_total" not in st.session_state:
        st.session_state.daily_loss_total = 0.0

    st.header("📊 Daily Journal")
    # Locked if no news cleared or limit reached
    loss_disabled = not news_ok or st.session_state.trade_count >= 3 or st.session_state.daily_loss_total >= max_daily_risk_limit
    if st.button("❌ RECORD LOSS", disabled=loss_disabled, use_container_width=True):
        st.session_state.balance -= current_risk_usd
        st.session_state.daily_loss_total += current_risk_usd
        st.session_state.trade_count += 1
        st.rerun()

    win_disabled = not news_ok or st.session_state.trade_count >= 3
    if st.button("✅ RECORD WIN", disabled=win_disabled, use_container_width=True):
        st.session_state.balance += (current_risk_usd * 2) 
        st.session_state.trade_count += 1
        st.rerun()

# ---------------- DYNAMIC HEADLINE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Asset: {symbol} | Server Time: {dt_string}")
st.markdown("---")

# ---------------- TRIPLE TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c5m = st.columns(3)

# --- 4H BIAS SECTION ---
c4h.subheader(f"⏳ 4H BIAS")
htf_bias = c4h.radio("4H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", disabled=not news_ok)
s4_h = c4h.number_input("4H Swing High", value=0.0, format="%.2f", key="s4h", disabled=not news_ok)
s4_l = c4h.number_input("4H Swing Low", value=0.0, format="%.2f", key="s4l", disabled=not news_ok)
bias_4h_ok = c4h.checkbox("4H Confirmed", value=False, key="4h_conf", disabled=not (s4_h > 0 and s4_l > 0) or not news_ok)

# --- 1H STRUCTURE SECTION (Unlocks only if 4H Confirmed) ---
c1h.subheader(f"⏱️ 1H STRUCTURE")
itf_trend = c1h.radio("1H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", disabled=not bias_4h_ok)
s1_h = c1h.number_input("1H Swing High", value=0.0, format="%.2f", key="s1h", disabled=not bias_4h_ok)
s1_l = c1h.number_input("1H Swing Low", value=0.0, format="%.2f", key="s1l", disabled=not bias_4h_ok)
bias_1h_ok = c1h.checkbox("1H Confirmed", value=False, key="1h_conf", disabled=not (s1_h > 0 and s1_l > 0) or not bias_4h_ok)

# --- 5M SHIFT SECTION (Unlocks only if 1H Confirmed) ---
c5m.subheader(f"⚡ 5M SHIFT")
ltf_trend = c5m.radio("5M Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="5m_t", disabled=not bias_1h_ok)
s5_h = c5m.number_input("5M Swing High", value=0.0, format="%.2f", key="s5h", disabled=not bias_1h_ok)
s5_l = c5m.number_input("5M Swing Low", value=0.0, format="%.2f", key="s5l", disabled=not bias_1h_ok)
bias_5m_ok = c5m.checkbox("5M Confirmed", value=False, key="5m_conf", disabled=not (s5_h > 0 and s5_l > 0) or not bias_1h_ok)

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header(f"📋 PHASE 2: POI")
    # Updated POI List with requested names
    poi_type = st.selectbox("Where am I trading?", [
        "Select POI...", 
        "Swing High", 
        "Swing Low", 
        "Supply Zone", 
        "Demand Zone", 
        "Order Block", 
        "FVG / Imbalance"
    ], disabled=not bias_5m_ok)
    
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f", disabled=not bias_5m_ok)

with col_exec:
    st.header(f"🚀 PHASE 3: EXECUTE")
    # Pip Calculation Logic
    if any(x in symbol for x in ["XAU", "GOLD", "JPY"]): pip_factor = 0.01
    elif any(x in symbol for x in ["US30", "NAS100", "GER40"]): pip_factor = 1.0
    else: pip_factor = 0.0001
        
    calculated_entry = 0.0
    if zone_price > 0:
        is_short_poi = any(x in poi_type for x in ["High", "Supply"])
        calculated_entry = zone_price - (15 * pip_factor) if is_short_poi else zone_price + (15 * pip_factor)

    calc_c1, calc_c2 = st.columns(2)
    with calc_c1:
        entry = st.number_input("Entry Price", value=calculated_entry, format="%.2f", disabled=not (zone_price > 0))
        sl = st.number_input("Stop Loss", value=0.0, format="%.2f", disabled=not (zone_price > 0))
    
    with calc_c2:
        if entry > 0 and sl > 0:
            pips = abs(entry - sl) / pip_factor
            lot = (current_risk_usd / pips) / 10 if pips > 0 else 0
            st.metric(f"Lot Size", f"{round(lot, 2)}")
            st.caption(f"Risk: {round(pips, 1)} pips")

# ---------------- FINAL STATUS ---------------- #
if bias_4h_ok and bias_1h_ok and bias_5m_ok and news_ok:
    st.success(f"🔥 {symbol} HIGH PROBABILITY SETUP READY")
elif not news_ok:
    st.warning("⚠️ ACTION REQUIRED: Clear 'High Impact News' filter in sidebar.")
else:
    st.info("Awaiting timeframe confirmation sequence...")
