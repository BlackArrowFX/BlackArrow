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
    symbol = st.text_input("Enter Instrument (e.g., XAUUSD, EURUSD, US30)", value="XAUUSD").upper()
    
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
    st.info(f"Active Risk: ${round(current_risk_usd, 2)}")
    
    st.header("🌍 News Filter")
    st.markdown(f"[Check Forex Factory for {symbol} 📅](https://www.forexfactory.com/)")
    news_ok = st.toggle("No High Impact News")

    if "trade_count" not in st.session_state:
        st.session_state.trade_count = 0
    if "daily_loss_total" not in st.session_state:
        st.session_state.daily_loss_total = 0.0

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

# ---------------- DYNAMIC HEADLINE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Asset: {symbol} | Server Time: {dt_string}")
st.markdown("---")

# ---------------- PHASE 0: HARD FILTERS ---------------- #
st.header("PHASE 0: PRE-FLIGHT CHECK")
col_p0_1, col_p0_2 = st.columns(2)
with col_p0_1:
    trade_limit_ok = st.session_state.trade_count < 3
    st.checkbox("Daily Trade Limit (Max 3)", value=trade_limit_ok, disabled=True)
with col_p0_2:
    st.checkbox(f"{symbol} News Cleared", value=news_ok, disabled=True)

if not trade_limit_ok or st.session_state.daily_loss_total >= max_daily_risk_limit:
    st.error(f"🛑 TRADING LOCKED: Daily limits reached.")
    st.stop()

# ---------------- TRIPLE TIMEFRAME ANALYSIS ---------------- #
st.markdown("---")
c4h, c1h, c5m = st.columns(3)

c4h.subheader(f"⏳ 4H BIAS")
c1h.subheader(f"⏱️ 1H STRUCT")
c5m.subheader(f"⚡ 5M SHIFT")

htf_bias = c4h.radio("4H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", label_visibility="collapsed")
itf_trend = c1h.radio("1H Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", label_visibility="collapsed")
ltf_trend = c5m.radio("5M Trend", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="5m_t", label_visibility="collapsed")

s4_h = c4h.number_input("4H Swing High", value=0.0, format="%.2f", key="s4h")
s1_h = c1h.number_input("1H Swing High", value=0.0, format="%.2f", key="s1h")
s5_h = c5m.number_input("5M Swing High", value=0.0, format="%.2f", key="s5h")

s4_l = c4h.number_input("4H Swing Low", value=0.0, format="%.2f", key="s4l")
s1_l = c1h.number_input("1H Swing Low", value=0.0, format="%.2f", key="s1l")
s5_l = c5m.number_input("5M Swing Low", value=0.0, format="%.2f", key="s5l")

bias_4h_ok = c4h.checkbox("4H Confirmed", disabled=not (s4_h > 0 and s4_l > 0))
bias_1h_ok = c1h.checkbox("1H Confirmed", disabled=not (s1_h > 0 and s1_l > 0))
bias_5m_ok = c5m.checkbox("5M Confirmed", disabled=not (s5_h > 0 and s5_l > 0))

phase1_ready = bias_4h_ok and htf_bias != "Ranging"
phase2_ready = bias_1h_ok and itf_trend != "Ranging"
phase3_ready = bias_5m_ok and ltf_trend != "Ranging"

# ---------------- PHASE 2: POI PLAN (EXPANDED) ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header(f"📋 PHASE 2: {symbol} POI")
    
    # ADDED SWING HIGH / SWING LOW TO SELECTBOX
    poi_type = st.selectbox("Where am I trading?", [
        "Select POI...", 
        "Supply Zone", 
        "Demand Zone", 
        "Order Block", 
        "FVG / Imbalance",
        "HTF Swing High (Liquidity)", 
        "HTF Swing Low (Liquidity)",
        "Equal Highs/Lows (BSL/SSL)"
    ])
    
    # Requirement: Liquidity Sweep Check
    liq_sweep = st.toggle("Liquidity Swept? (Grab & Reverse)")

    raw_text = st.text_area(f"Paste 1H {symbol} POI Zones", height=100, placeholder="Example: 1H Demand 2340.50 - 2345.00")
    POI_DB = {}
    if raw_text:
        lines = raw_text.split("\n")
        for line in lines:
            line = line.strip().replace("–", "-")
            match = re.search(r"(\d{1,6}\.?\d*)\s*-\s*(\d{1,6}\.?\d*)", line)
            if match:
                low, high = float(match.group(1)), float(match.group(2))
                name = line.split("$")[0].strip() or f"Zone {len(POI_DB)+1}"
                POI_DB[name] = {"low": low, "high": high}

    inside_zone = False
    if POI_DB:
        selected_poi = st.selectbox("Active Zone", list(POI_DB.keys()))
        curr_price = st.number_input(f"Current {symbol} Price", value=0.0, format="%.2f")
        target = POI_DB[selected_poi]
        if target["low"] <= curr_price <= target["high"]:
            st.success(f"✅ PRICE IN {symbol} POI")
            inside_zone = True
        else:
            st.error(f"❌ PRICE OUTSIDE {symbol} POI")
    
    poi_confirmed = poi_type != "Select POI..." and inside_zone

# ---------------- PHASE 3: EXECUTION ---------------- #
with col_exec:
    st.header(f"🚀 PHASE 3: {symbol} EXECUTE")
    calc_c1, calc_c2 = st.columns(2)
    with calc_c1:
        entry = st.number_input("Entry Price", value=0.0, format="%.2f")
        sl = st.number_input("Stop Loss", value=0.0, format="%.2f")
    
    with calc_c2:
        if entry > 0 and sl > 0:
            raw_diff = abs(entry - sl)
            if any(x in symbol for x in ["XAU", "GOLD", "JPY"]):
                pips = raw_diff * 100 
            elif any(x in symbol for x in ["US30", "NAS100", "GER40", "BTC", "ETH"]):
                pips = raw_diff
            else:
                pips = raw_diff * 10000 

            lot = (current_risk_usd / pips) / 10 if pips > 0 else 0
            st.metric(f"{symbol} Lot Size", f"{round(lot, 2)} Lots")

    # CONFLUENCE CHECKLIST
    st.markdown("---")
    with st.expander("🔍 Confluence Checklist", expanded=True):
        c1 = st.checkbox(f"{symbol} Trends Aligned", value=phase1_ready and phase2_ready and phase3_ready, disabled=True)
        c2 = st.checkbox(f"{symbol} POI Confirmed", value=poi_confirmed, disabled=True)
        c3 = st.checkbox("Liquidity Grab Confirmed", value=liq_sweep)
        
        if c1 and c2 and c3 and news_ok:
            st.success(f"🔥 {symbol} HIGH PROBABILITY SETUP")
        else:
            st.warning(f"⚠️ {symbol} CHECK ALIGNMENT / LIQUIDITY")

    if entry > 0 and sl > 0:
        is_buy = entry > sl
        diff = abs(entry - sl)
        tp1 = round(entry + (diff * 1.5 if is_buy else -diff * 1.5), 2)
        tp2 = round(entry + (diff * 3.0 if is_buy else -diff * 3.0), 2)
        
        st.subheader("🎯 Profit Targets")
        r_col1, r_col2 = st.columns(2)
        r_col1.metric("TP 1 (1.5R)", f"{tp1}", f"+${round(current_risk_usd * 1.5, 2)}")
        r_col2.metric("TP 2 (3.0R)", f"{tp2}", f"+${round(current_risk_usd * 3.0, 2)}")
