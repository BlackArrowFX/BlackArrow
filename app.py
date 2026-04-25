import streamlit as st
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & ASSET ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    
    # 1. ASSET CLASS AT THE TOP
    asset_type = st.selectbox(
        "Select Asset Class", 
        ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"]
    )
    
    # 2. INSTRUMENT BELOW ASSET CLASS
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

    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News")

    if "trade_count" not in st.session_state:
        st.session_state.trade_count = 0

    st.header("📊 Daily Journal")
    loss_disabled = not news_ok or st.session_state.trade_count >= 3
    
    col_loss, col_win = st.columns(2)
    with col_loss:
        if st.button("❌ LOSS", disabled=loss_disabled, use_container_width=True):
            st.session_state.balance -= current_risk_usd
            st.session_state.trade_count += 1
            st.rerun()
    with col_win:
        if st.button("✅ WIN", disabled=loss_disabled, use_container_width=True):
            st.session_state.balance += (current_risk_usd * 2) 
            st.session_state.trade_count += 1
            st.rerun()

# ---------------- DYNAMIC HEADLINE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Asset: {symbol} | Mode: {asset_type} | Server Time: {dt_string}")
st.markdown("---")

# ---------------- TRIPLE TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c5m = st.columns(3)

# 4H BIAS
c4h.subheader(f"⏳ 4H BIAS")
htf_bias = c4h.radio("4H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", disabled=not news_ok)
s4_h = c4h.number_input("4H Swing High", value=0.0, format="%.2f", key="s4h", disabled=not news_ok)
s4_l = c4h.number_input("4H Swing Low", value=0.0, format="%.2f", key="s4l", disabled=not news_ok)
bias_4h_ok = c4h.checkbox("4H Confirmed", key="4h_c", disabled=not (s4_h > 0 and s4_l > 0) or not news_ok)

# 1H STRUCTURE
c1h.subheader(f"⏱️ 1H STRUCTURE")
itf_trend = c1h.radio("1H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", disabled=not bias_4h_ok)
s1_h = c1h.number_input("1H Swing High", value=0.0, format="%.2f", key="s1h", disabled=not bias_4h_ok)
s1_l = c1h.number_input("1H Swing Low", value=0.0, format="%.2f", key="s1l", disabled=not bias_4h_ok)
bias_1h_ok = c1h.checkbox("1H Confirmed", key="1h_c", disabled=not (s1_h > 0 and s1_l > 0) or not bias_4h_ok)

# 5M SHIFT
c5m.subheader(f"⚡ 5M SHIFT")
ltf_trend = c5m.radio("5M Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="5m_t", disabled=not bias_1h_ok)
s5_h = c5m.number_input("5M Swing High", value=0.0, format="%.2f", key="s5h", disabled=not bias_1h_ok)
s5_l = c5m.number_input("5M Swing Low", value=0.0, format="%.2f", key="s5l", disabled=not bias_1h_ok)
bias_5m_ok = c5m.checkbox("5M Confirmed", key="5m_c", disabled=not (s5_h > 0 and s5_l > 0) or not bias_1h_ok)

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header(f"📋 PHASE 2: POI")
    poi_list = ["Select POI...", "Swing High", "Swing Low", "Supply Zone", "Demand Zone", "Order Block", "FVG / Imbalance"]
    poi_type = st.selectbox("Where am I trading?", poi_list, disabled=not bias_5m_ok)
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f", disabled=not bias_5m_ok)

with col_exec:
    st.header(f"🚀 PHASE 3: EXECUTE")
    
    # Pip Calculation Logic
    if asset_type == "METAL (Gold/Silver)":
        pip_factor = 0.1  # 15 pips = 1.50
    elif asset_type == "FOREX":
        pip_factor = 0.0001
    else:
        pip_factor = 1.0  # US30/NAS100
        
    # Auto SL Calculation
    calculated_sl = 0.0
    if zone_price > 0:
        is_short_poi = any(x in poi_type for x in ["High", "Supply"])
        calculated_sl = zone_price + (15 * pip_factor) if is_short_poi else zone_price - (15 * pip_factor)

    # Reordered Execution Inputs
    sl = st.number_input("Stop Loss (Auto)", value=calculated_sl, format="%.2f", disabled=not (zone_price > 0))
    entry = st.number_input("Entry Price (Manual)", value=0.0, format="%.2f", disabled=not (zone_price > 0))
    
    if entry > 0 and sl > 0:
        pips_diff = abs(entry - sl) / pip_factor
        lot = (current_risk_usd / pips_diff) / 10 if pips_diff > 0 else 0
        st.metric(f"Calculated Lot Size", f"{round(lot, 2)}")
        st.caption(f"Risk Distance: {round(pips_diff, 1)} pips")

# ---------------- FINAL STATUS ---------------- #
if bias_4h_ok and bias_1h_ok and bias_5m_ok and news_ok:
    st.success(f"🔥 {symbol} ALIGNED")
else:
    st.info("Ensure all timeframes are confirmed and news is cleared.")
