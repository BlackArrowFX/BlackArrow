import streamlit as st
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & ASSET ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    asset_type = st.selectbox("Select Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"])
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
    news_ok = st.toggle("No High Impact News", value=False)
    
    if not news_ok:
        st.warning("⚠️ System Locked: Confirm news is clear.")

    if "trade_count" not in st.session_state: st.session_state.trade_count = 0

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

# ---------------- QUAD TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)

# --- 4H BIAS ---
c4h.subheader("⏳ 4H BIAS")
htf_bias = c4h.radio("Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", disabled=not news_ok)
s4_h = c4h.number_input("Swing High", value=0.0, format="%.2f", key="s4h", disabled=not news_ok)
s4_l = c4h.number_input("Swing Low", value=0.0, format="%.2f", key="s4l", disabled=not news_ok)
bias_4h_ok = c4h.checkbox("4H Confirmed", key="4h_c", disabled=not (s4_h > 0 and s4_l > 0) or not news_ok)

# --- 1H STRUC (Shortened for alignment) ---
c1h.subheader("⏱️ 1H STRUC")
itf_trend = c1h.radio("Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", disabled=not bias_4h_ok)
s1_h = c1h.number_input("Swing High", value=0.0, format="%.2f", key="s1h", disabled=not bias_4h_ok)
s1_l = c1h.number_input("Swing Low", value=0.0, format="%.2f", key="s1l", disabled=not bias_4h_ok)
bias_1h_ok = c1h.checkbox("1H Confirmed", key="1h_c", disabled=not (s1_h > 0 and s1_l > 0) or not bias_4h_ok)

# --- 30M SHIFT ---
c30m.subheader("⚡ 30M SHIFT")
t30_trend = c30m.radio("Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t", disabled=not bias_1h_ok)
s30_h = c30m.number_input("Swing High", value=0.0, format="%.2f", key="s30h", disabled=not bias_1h_ok)
s30_l = c30m.number_input("Swing Low", value=0.0, format="%.2f", key="s30l", disabled=not bias_1h_ok)
bias_30m_ok = c30m.checkbox("30M Confirmed", key="30m_c", disabled=not (s30_h > 0 and s30_l > 0) or not bias_1h_ok)

# --- 15M ENTRY ---
c15m.subheader("🎯 15M ENTRY")
t15_trend = c15m.radio("Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t", disabled=not bias_30m_ok)
s15_h = c15m.number_input("Swing High", value=0.0, format="%.2f", key="s15h", disabled=not bias_30m_ok)
s15_l = c15m.number_input("Swing Low", value=0.0, format="%.2f", key="s15l", disabled=not bias_30m_ok)
bias_15m_ok = c15m.checkbox("15M Confirmed", key="15m_c", disabled=not (s15_h > 0 and s15_l > 0) or not bias_30m_ok)

# ---------------- MARKET INTELLIGENCE ---------------- #
st.markdown("---")
st.subheader("🧠 Market Intelligence")

if bias_15m_ok:
    if htf_bias == "Bullish ⬆️":
        if itf_trend == "Bearish ⬇️":
            st.info("📉 COMMENT: 4H BULLISH PULLBACK. Lower timeframes are bearish as price hunts for a 4H Higher Low.")
        elif itf_trend == "Bullish ⬆️" and t15_trend == "Bullish ⬆️":
            st.success("🚀 COMMENT: QUAD-TIMEFRAME BULLISH ALIGNMENT. High probability continuation.")
    elif htf_bias == "Bearish ⬇️":
        if itf_trend == "Bullish ⬆️":
            st.info("📈 COMMENT: 4H BEARISH RETRACEMENT. Lower timeframes are bullish as price hunts for a 4H Lower High.")
        elif itf_trend == "Bearish ⬇️" and t15_trend == "Bearish ⬇️":
            st.success("🔥 COMMENT: QUAD-TIMEFRAME BEARISH ALIGNMENT. Perfect synchronization for shorts.")
else:
    st.write("⏳ Follow confirmation sequence (4H -> 1H -> 30M -> 15M) to unlock.")

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Where am I trading?", ["Select POI...", "Swing High", "Swing Low", "Supply Zone", "Demand Zone", "Order Block", "FVG / Imbalance"], disabled=not bias_15m_ok)
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f", disabled=not bias_15m_ok)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
        
    calculated_sl = 0.0
    if zone_price > 0:
        is_short_poi = any(x in poi_type for x in ["High", "Supply"])
        calculated_sl = zone_price + (15 * pip_factor) if is_short_poi else zone_price - (15 * pip_factor)

    sl = st.number_input("Stop Loss (Auto)", value=calculated_sl, format="%.2f", disabled=not (zone_price > 0))
    entry = st.number_input("Entry Price (Manual)", value=0.0, format="%.2f", disabled=not (zone_price > 0))
    
    if entry > 0 and sl > 0:
        pips_diff = abs(entry - sl) / pip_factor
        lot = (current_risk_usd / pips_diff) / 10 if pips_diff > 0 else 0
        st.metric("Calculated Lot Size", f"{round(lot, 2)}")
        st.caption(f"Risk Distance: {round(pips_diff, 1)} pips")
