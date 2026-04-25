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

# Initialize Highs, Lows, and Bias for all 3 Timeframes
tfs = ["4H", "1H", "5M"]
for tf in tfs:
    if f"{tf}_bias" not in st.session_state: st.session_state[f"{tf}_bias"] = "Bullish ⬆️"
    if f"{tf}_high" not in st.session_state: st.session_state[f"{tf}_high"] = 0.0
    if f"{tf}_low" not in st.session_state: st.session_state[f"{tf}_low"] = 0.0

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

# ---------------- PHASE 0: HARD FILTERS ---------------- #
st.header("PHASE 0: PRE-FLIGHT CHECK")
col_p0_1, col_p0_2 = st.columns(2)
with col_p0_1:
    trade_limit_ok = st.session_state.trade_count < 3
    st.checkbox("Daily Trade Limit (Max 3)", value=trade_limit_ok, disabled=True)
with col_p0_2:
    st.checkbox("News Cleared", value=news_ok, disabled=True)

if not trade_limit_ok or st.session_state.daily_loss_total >= max_daily_risk_limit:
    st.error("🛑 TRADING LOCKED: Limits reached.")
    st.stop()

# ---------------- TRIPLE TIMEFRAME ANALYSIS (ENHANCED) ---------------- #
st.markdown("---")
c4h, c1h, c5m = st.columns(3)

# Logic Container for Phase Readiness
phase_ready = {"4H": False, "1H": False, "5M": False}
columns = {"4H": c4h, "1H": c1h, "5M": c5m}

for tf in tfs:
    col = columns[tf]
    with col:
        st.subheader(f"⏳ {tf} ANALYSIS")
        
        # 1. BIAS (Driven by Session State)
        st.info(f"Current Bias: **{st.session_state[f'{tf}_bias']}**")
        
        # 2. SWING INPUTS (Linked to Session State)
        st.session_state[f"{tf}_high"] = st.number_input(f"{tf} Swing High", value=st.session_state[f"{tf}_high"], format="%.2f", step=0.0, key=f"h_{tf}")
        st.session_state[f"{tf}_low"] = st.number_input(f"{tf} Swing Low", value=st.session_state[f"{tf}_low"], format="%.2f", step=0.0, key=f"l_{tf}")

        # 3. CONFIRMATION LOGIC
        is_conf = st.checkbox(f"{tf} Confirmed", key=f"conf_{tf}")
        
        if is_conf:
            current_bias = st.session_state[f"{tf}_bias"]
            # Label Assignment Logic
            if "Bullish" in current_bias:
                opt1, opt2 = "BOS (Swing High)", "MSS (Swing Low)"
            else:
                opt1, opt2 = "BOS (Swing Low)", "MSS (Swing High)"
            
            choice = st.radio(f"Structure Broken for {tf}:", [opt1, opt2], key=f"choice_{tf}")
            new_val = st.number_input(f"Enter Price of {choice}", format="%.2f", step=0.0, key=f"val_{tf}")
            
            if st.button(f"Update {tf} Level", key=f"upd_{tf}"):
                if "BOS" in choice:
                    # Update high if choice was high, low if low
                    if "High" in choice: st.session_state[f"{tf}_high"] = new_val
                    else: st.session_state[f"{tf}_low"] = new_val
                    st.toast(f"{tf} BOS Updated!")
                else:
                    # MSS: FLIP THE BIAS
                    new_bias = "Bearish ⬇️" if "Bullish" in current_bias else "Bullish ⬆️"
                    st.session_state[f"{tf}_bias"] = new_bias
                    # Update price too
                    if "High" in choice: st.session_state[f"{tf}_high"] = new_val
                    else: st.session_state[f"{tf}_low"] = new_val
                    st.toast(f"{tf} TREND REVERSED TO {new_bias}")
                st.rerun()

            if new_val > 0:
                phase_ready[tf] = True

# ---------------- POI & EXECUTION ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 POI PLAN")
    raw_text = st.text_area("Paste 1H POI Zones", height=100, placeholder="Example: 1H Demand $2340 - $2345")
    POI_DB = {}
    if raw_text:
        match = re.search(r"(\d{3,5}\.?\d*)\s*-\s*(\d{3,5}\.?\d*)", raw_text)
        if match:
            low, high = float(match.group(1)), float(match.group(2))
            curr_price = st.number_input("Market Price", value=0.0, format="%.2f", step=0.0)
            if low <= curr_price <= high:
                st.success("✅ AT POI")
                inside_zone = True
            else:
                st.error("❌ OUTSIDE POI")
                inside_zone = False
        else: inside_zone = False
    else: inside_zone = False

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
            
            # THE TICK CHECK: All 3 Phases Ready + POI + News
            if all(phase_ready.values()) and inside_zone and news_ok:
                st.success("🔥 ALL TRENDS ALIGNED: EXECUTE")
            else:
                st.error("🚫 DO NOT ENTER: Check Structural Breaks")

    if entry > 0 and sl > 0:
        diff = abs(entry - sl)
        is_buy = entry > sl
        st.write(f"TP1 (1.5R): **{round(entry + (diff * 1.5 if is_buy else -diff * 1.5), 2)}** | TP2 (3.0R): **{round(entry + (diff * 3.0 if is_buy else -diff * 3.0), 2)}**")
