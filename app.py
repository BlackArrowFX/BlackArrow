import streamlit as st
import re
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

st.title("🏹 BlackArrowFX: Triple-Timeframe Execution Engine")
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

# ---------------- TRIPLE TIMEFRAME ANALYSIS ---------------- #
st.header("PHASE 1: MARKET STRUCTURE")
c4h, c1h, c5m = st.columns(3)

def process_tf(col, tf_name, key):
    with col:
        st.subheader(f"⏳ {tf_name}")
        bias = st.radio(f"{tf_name} Bias", ["Bullish ⬆️", "Bearish ⬇️", "Ranging"], key=f"bias_{key}")
        
        # Confirmation Logic
        is_confirmed = st.checkbox(f"{tf_name} Confirmed", key=f"conf_{key}")
        
        tf_ready = False
        if is_confirmed and bias != "Ranging":
            # Dynamic Labeling based on Bias
            if bias == "Bullish ⬆️":
                label_high, label_low = "BOS (Swing High)", "MSS (Swing Low)"
            else:
                label_high, label_low = "MSS (Swing High)", "BOS (Swing Low)"
            
            struct_choice = st.radio("Structure Broken:", [label_high, label_low], key=f"struct_{key}")
            price_input = st.number_input(f"Confirm {struct_choice} Price", step=0.0, format="%.2f", key=f"price_{key}")
            
            if price_input > 0:
                tf_ready = True
                st.success(f"{tf_name} Alignment: OK")
        
        return tf_ready

phase1_ready = process_tf(c4h, "4H", "4h")
phase2_ready = process_tf(c1h, "1H", "1h")
phase3_ready = process_tf(c5m, "5M", "5m")

# ---------------- POI & EXECUTION ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 POI PLAN")
    raw_text = st.text_area("Paste 1H POI Zones", height=100, placeholder="Example: 1H Demand $2340 - $2345")
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
        selected_poi = st.selectbox("Active POI", list(POI_DB.keys()))
        curr_market_price = st.number_input("Market Price", value=0.0, format="%.2f", step=0.0)
        target = POI_DB[selected_poi]
        if target["low"] <= curr_market_price <= target["high"]:
            st.success("✅ AT POI")
            inside_zone = True
        else:
            st.error("❌ OUTSIDE POI")

with col_exec:
    st.header("🚀 EXECUTION ENGINE")
    calc_c1, calc_c2 = st.columns(2)
    with calc_c1:
        entry = st.number_input("Entry Price", value=0.0, format="%.2f", step=0.0)
        sl = st.number_input("Stop Loss", value=0.0, format="%.2f", step=0.0)
    
    with calc_c2:
        if entry > 0 and sl > 0:
            pips = abs(entry - sl) * 10
            lot = current_risk_usd / (pips * 10) if pips > 0 else 0
            st.metric("Lot Size", round(lot, 2))
            
            # THE TICK CHECK: All TFs confirmed + POI + News
            if phase1_ready and phase2_ready and phase3_ready and inside_zone and news_ok:
                st.success("🔥 ALL CONFLUENCES MET: EXECUTE")
            else:
                st.error("🚫 DO NOT ENTER: Check Structural Confirmation")

    if entry > 0 and sl > 0:
        diff = abs(entry - sl)
        is_buy = entry > sl
        st.write(f"TP1 (1.5R): **{round(entry + (diff * 1.5 if is_buy else -diff * 1.5), 2)}** | TP2 (3.0R): **{round(entry + (diff * 3.0 if is_buy else -diff * 3.0), 2)}**")
