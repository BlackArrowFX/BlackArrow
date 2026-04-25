import streamlit as st
import re
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
    
    st.header("📊 Daily Journal")
    if "trade_count" not in st.session_state:
        st.session_state.trade_count = 0
    st.write(f"Trades Taken: **{st.session_state.trade_count} / 3**")
    
    if st.button("🔄 Reset Daily Limits"):
        st.session_state.trade_count = 0
        st.rerun()

# ---------------- DYNAMIC HEADLINE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Asset: {symbol} | Server Time: {dt_string}")
st.markdown("---")

# ---------------- TRIPLE TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c5m = st.columns(3)

htf_bias = c4h.radio("4H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t")
itf_trend = c1h.radio("1H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t")
ltf_trend = c5m.radio("5M Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="5m_t")

# Simple check for alignment
trends_aligned = (htf_bias == itf_trend == ltf_trend) and htf_bias != "Ranging"

# ---------------- PHASE 2: POI & ENTRY ZONE ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header(f"📋 PHASE 2: {symbol} POI")
    
    poi_type = st.selectbox("Where am I trading?", [
        "Select POI...", 
        "Supply Zone", 
        "Demand Zone", 
        "Order Block", 
        "FVG / Imbalance",
        "HTF Swing High", 
        "HTF Swing Low",
        "Equal Highs/Lows"
    ])
    
    # NEW: Entry Zone Price Input
    zone_price = st.number_input("Entry Zone Price (The Level)", value=0.0, format="%.2f")
    
    st.info("System will calculate +15 pips from this level for your entry.")

# ---------------- PHASE 3: EXECUTION (+15 PIPS LOGIC) ---------------- #
with col_exec:
    st.header(f"🚀 PHASE 3: {symbol} EXECUTE")
    
    # Determine if we are Buying or Selling based on POI
    # (Demand/Swing Low = Buy | Supply/Swing High = Sell)
    is_buy_poi = "Demand" in poi_type or "Low" in poi_type or "Bullish" in htf_bias
    
    # PIP Factor Calculation
    if any(x in symbol for x in ["XAU", "GOLD", "JPY"]):
        pip_value = 0.01
    elif any(x in symbol for x in ["US30", "NAS100", "GER40", "BTC", "ETH"]):
        pip_value = 1.0
    else:
        pip_value = 0.0001
    
    # Calculate Auto-Entry: Zone Price + 15 Pips
    # For Buys, we enter 15 pips ABOVE the zone. For Sells, 15 pips BELOW the zone.
    if zone_price > 0:
        offset = 15 * pip_value
        auto_entry = zone_price + offset if is_buy_poi else zone_price - offset
    else:
        auto_entry = 0.0

    calc_c1, calc_c2 = st.columns(2)
    with calc_c1:
        entry_price = st.number_input("Entry Price (Auto-Filled)", value=auto_entry, format="%.2f")
        sl_price = st.number_input("Stop Loss", value=0.0, format="%.2f")
    
    with calc_c2:
        if entry_price > 0 and sl_price > 0:
            raw_diff = abs(entry_price - sl_price)
            pips_at_risk = raw_diff / pip_value
            
            # Lot size: (Risk Amount / Pips) / 10
            lot = (current_risk_usd / pips_at_risk) / 10 if pips_at_risk > 0 else 0
            st.metric(f"{symbol} Lot Size", f"{round(lot, 2)} Lots")
            st.caption(f"Risking {round(pips_at_risk, 1)} pips")

    # CONFLUENCE CHECKLIST
    st.markdown("---")
    with st.expander("🔍 Confluence Checklist", expanded=True):
        c1 = st.checkbox(f"{symbol} Trends Aligned", value=trends_aligned)
        c2 = st.checkbox(f"{symbol} Zone Set", value=zone_price > 0)
        c3 = st.checkbox("POI Type Selected", value=poi_type != "Select POI...")
        
        if c1 and c2 and c3:
            st.success(f"🔥 {symbol} READY: ENTER AT {round(entry_price, 2)}")
        else:
            st.warning("⚠️ WAITING FOR ALIGNMENT")

    if entry_price > 0 and sl_price > 0:
        diff = abs(entry_price - sl_price)
        is_actually_buy = entry_price > sl_price
        
        tp1 = round(entry_price + (diff * 1.5 if is_actually_buy else -diff * 1.5), 2)
        tp2 = round(entry_price + (diff * 3.0 if is_actually_buy else -diff * 3.0), 2)
        
        st.subheader("🎯 Profit Targets")
        r_col1, r_col2 = st.columns(2)
        r_col1.metric("TP 1 (1.5R)", f"{tp1}", f"+${round(current_risk_usd * 1.5, 2)}")
        r_col2.metric("TP 2 (3.0R)", f"{tp2}", f"+${round(current_risk_usd * 3.0, 2)}")
