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

# ---------------- SESSION STATE INITIALIZATION ---------------- #
if "balance" not in st.session_state: st.session_state.balance = 2146.11
if "trade_count" not in st.session_state: st.session_state.trade_count = 0
if "daily_loss_total" not in st.session_state: st.session_state.daily_loss_total = 0.0

# Trend and Structure States
tfs = ["4H", "1H", "5M"]
for tf in tfs:
    if f"{tf}_bias" not in st.session_state: st.session_state[f"{tf}_bias"] = "Bullish ⬆️"
    if f"{tf}_high" not in st.session_state: st.session_state[f"{tf}_high"] = 0.0
    if f"{tf}_low" not in st.session_state: st.session_state[f"{tf}_low"] = 0.0

# ---------------- SIDEBAR: RISK & JOURNAL ---------------- #
with st.sidebar:
    st.header("💰 Risk Engine")
    st.metric("Balance", f"${round(st.session_state.balance, 2)}")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 5.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0, step=0.0)

    news_ok = st.toggle("No High Impact News", value=True)
    
    if st.button("🔄 Reset Data"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()

# ---------------- PHASE 0: HARD FILTERS ---------------- #
if st.session_state.trade_count >= 3:
    st.error("🛑 TRADING LOCKED: Daily Limit Reached.")
    st.stop()

# ---------------- TRIPLE TIMEFRAME ANALYSIS ---------------- #
st.markdown("### 📊 Market Structure Analysis")
cols = st.columns(3)

phase_readiness = {}

for i, tf in enumerate(tfs):
    with cols[i]:
        st.subheader(f"{tf} Analysis")
        
        # 1. Bias Display
        current_bias = st.session_state[f"{tf}_bias"]
        st.info(f"Current Bias: **{current_bias}**")
        
        # 2. Manual Swing Inputs
        st.session_state[f"{tf}_high"] = st.number_input(f"{tf} Swing High", value=st.session_state[f"{tf}_high"], format="%.2f", step=0.0, key=f"in_h_{tf}")
        st.session_state[f"{tf}_low"] = st.number_input(f"{tf} Swing Low", value=st.session_state[f"{tf}_low"], format="%.2f", step=0.0, key=f"in_l_{tf}")
        
        # 3. Confirmation Trigger
        conf = st.checkbox(f"Confirm {tf} Structure Break", key=f"conf_box_{tf}")
        
        ready = False
        if conf:
            # Logic: If Bullish, High is BOS, Low is MSS. If Bearish, Low is BOS, High is MSS.
            if "Bullish" in current_bias:
                options = ["BOS (Swing High)", "MSS (Swing Low)"]
            else:
                options = ["BOS (Swing Low)", "MSS (Swing High)"]
            
            choice = st.radio("What broke?", options, key=f"choice_{tf}")
            new_price = st.number_input("Break Price", step=0.0, format="%.2f", key=f"new_p_{tf}")
            
            if st.button(f"Update {tf} Structure", key=f"btn_{tf}"):
                if "BOS" in choice:
                    # Update the relevant High/Low with the new price
                    if "High" in choice: st.session_state[f"{tf}_high"] = new_price
                    else: st.session_state[f"{tf}_low"] = new_price
                    st.toast(f"{tf} BOS Confirmed!")
                else:
                    # MSS Logic: FLIP THE BIAS
                    new_bias = "Bearish ⬇️" if "Bullish" in current_bias else "Bullish ⬆️"
                    st.session_state[f"{tf}_bias"] = new_bias
                    if "High" in choice: st.session_state[f"{tf}_high"] = new_price
                    else: st.session_state[f"{tf}_low"] = new_price
                    st.toast(f"{tf} TREND FLIPPED TO {new_bias}!")
                st.rerun()
            
            if new_price > 0:
                ready = True
        
        phase_readiness[tf] = ready

# ---------------- POI & EXECUTION ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 POI PLAN")
    raw_text = st.text_area("Paste 1H POI Zones", placeholder="1H Demand $2340 - $2345")
    inside_zone = False
    if raw_text:
        match = re.search(r"(\d{3,5}\.?\d*)\s*-\s*(\d{3,5}\.?\d*)", raw_text)
        if match:
            low, high = float(match.group(1)), float(match.group(2))
            curr_price = st.number_input("Market Price", value=0.0, format="%.2f", step=0.0)
            if low <= curr_price <= high:
                st.success("✅ AT POI")
                inside_zone = True
            else: st.error("❌ OUTSIDE POI")

with col_exec:
    st.header("🚀 EXECUTION")
    c1, c2 = st.columns(2)
    entry = c1.number_input("Entry", value=0.0, format="%.2f", step=0.0)
    sl = c1.number_input("Stop Loss", value=0.0, format="%.2f", step=0.0)
    
    if entry > 0 and sl > 0:
        pips = abs(entry - sl) * 10
        lot = current_risk_usd / (pips * 10) if pips > 0 else 0
        c2.metric("Lot Size", round(lot, 2))
        
        # The Final Condition
        if all(phase_readiness.values()) and inside_zone and news_ok:
            st.success("🔥 ALL CONFLUENCES MET: EXECUTE")
        else:
            st.warning("🚫 LOCKED: Check Structure Confirmations")

    if entry > 0 and sl > 0:
        diff = abs(entry - sl)
        is_buy = entry > sl
        st.write(f"TP1 (1.5R): **{round(entry + (diff * 1.5 if is_buy else -diff * 1.5), 2)}** | TP2 (3.0R): **{round(entry + (diff * 3.0 if is_buy else -diff * 3.0), 2)}**")
