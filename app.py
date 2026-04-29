import streamlit as st
from datetime import datetime
import pandas as pd

# ---------------- 1. INITIALIZE GLOBAL STATE ---------------- #
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11  
if "trades_taken" not in st.session_state:
    st.session_state.trades_taken = 0
if "trade_notes" not in st.session_state:
    st.session_state.trade_notes = ""
if "trade_history" not in st.session_state:
    st.session_state.trade_history = []
if "editing_index" not in st.session_state:
    st.session_state.editing_index = None

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & SYSTEM ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    asset_type = st.selectbox("Select Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"], index=0)
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

    st.markdown("---")
    st.header("🌍 News Filter")
    st.link_button("📊 Check Forex Factory", "https://www.forexfactory.com/", use_container_width=True)
    news_ok = st.toggle("No High Impact News Active", value=False) 
    
    if not news_ok:
        st.error("🚨 SYSTEM LOCKED: Confirm no news.")
    else:
        st.success("✅ News Cleared")

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

# ---------------- TRADING PLAN SECTION ---------------- #
with st.expander("📜 MY TRADING PLAN", expanded=False):
    st.markdown("""
    ### 1. Market Structure Analysis
    * **1H:** HTF Structure | **15M:** Intraday Zones | **5M:** Entry Execution.
    ### 2. Strategic Setup
    * Mark Swing Highs/Lows. Align with HTF POIs.
    ### 3. Risk & Footprint
    * **Max Risk:** $100. **Footprint:** 300% Imbalance Stacks & Delta Shifts.
    """)

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

# ---------------- STRATEGY NOTES ---------------- #
st.markdown("---")
st.subheader("📝 POST-SHOCK EXECUTION PLAN")
st.session_state.trade_notes = st.text_area(
    "Paste Strategic Setup Here:",
    value=st.session_state.trade_notes,
    height=150,
    placeholder="Watch for Liquidity Sweep..."
)

# ---------------- CONFLUENCE METER ---------------- #
m5_bos_ok = st.checkbox("5M BOS/MSS Confirmed", disabled=not bias_15m_ok)
confluences = [bias_4h_ok, bias_1h_ok, bias_30m_ok, bias_15m_ok, m5_bos_ok]
progress = sum(confluences) / 5
st.progress(progress)
st.write(f"**Setup Strength: {int(progress*100)}%**")

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
system_unlocked = bias_15m_ok and news_ok
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Zone", ["Select...", "Order Block", "FVG", "Supply/Demand"], disabled=not system_unlocked)
    zone_price = st.number_input("Entry Zone", value=0.0, format="%.2f", disabled=not system_unlocked)
    trade_dir = st.radio("Dir", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True, disabled=not system_unlocked)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    entry_val = st.number_input("Entry Price", value=zone_price, format="%.2f", disabled=not system_unlocked)
    sl_val = st.number_input("Stop Loss", value=0.0, format="%.2f", disabled=not system_unlocked)
    
    if entry_val > 0 and sl_val > 0 and trade_dir != "Select...":
        dist = abs(entry_val - sl_val) / pip_factor
        if dist > 0:
            lots = round((current_risk_usd / dist) / 10, 2)
            tp1 = round(entry_val + (dist * 2 * pip_factor) if trade_dir == "LONG 🔵" else entry_val - (dist * 2 * pip_factor), 2)
            st.metric("Recommended Lots", f"{lots}")
            st.metric("TP1 (1:2 RR)", f"{tp1}")
            
            if st.button("💾 SAVE TRADE DETAILS", use_container_width=True):
                trade_data = {
                    "Time": dt_string, "Asset": symbol, "Dir": trade_dir,
                    "POI": f"{poi_type} @ {zone_price}", "Lots": lots,
                    "Entry": entry_val, "SL": sl_val, "TP1": tp1,
                    "Plan": st.session_state.trade_notes
                }
                st.session_state.trade_history.append(trade_data)
                st.toast("Trade Logged!")

# ---------------- 📊 SESSION LOG ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log")

if st.session_state.trade_history:
    to_delete = []
    
    # Header for the custom list
    st.write("---")
    for i, trade in enumerate(st.session_state.trade_history):
        c_tick, c_txt, c_ed = st.columns([0.5, 7, 1])
        with c_tick:
            if st.checkbox("", key=f"del_{i}"):
                to_delete.append(i)
        with c_txt:
            st.write(f"**#{i+1} | {trade['Asset']} {trade['Dir']}** ({trade['Time']})")
            with st.expander("View Plan"):
                st.info(trade['Plan'])
        with c_ed:
            if st.button("📝 Edit", key=f"edit_{i}"):
                st.session_state.editing_index = i
                st.session_state.temp_notes = trade['Plan']

    # --- EDIT OVERLAY ---
    if st.session_state.editing_index is not None:
        idx = st.session_state.editing_index
        st.markdown(f"### ✏️ Editing Trade #{idx+1}")
        updated_text = st.text_area("Modify Notes:", value=st.session_state.temp_notes)
        
        ce1, ce2 = st.columns(2)
        if ce1.button("Save Changes"):
            st.session_state.trade_history[idx]['Plan'] = updated_text
            st.session_state.editing_index = None
            st.rerun()
        if ce2.button("Cancel Edit"):
            st.session_state.editing_index = None
            st.rerun()

    st.markdown("---")
    # Action Buttons
    cb1, cb2, cb3 = st.columns(3)
    with cb1:
        if st.button("🗑️ DELETE SELECTED", use_container_width=True):
            for index in sorted(to_delete, reverse=True):
                st.session_state.trade_history.pop(index)
            st.rerun()
    with cb2:
        if st.button("🧨 CLEAR ALL", use_container_width=True):
            st.session_state.trade_history = []
            st.rerun()
    with cb3:
        df = pd.DataFrame(st.session_state.trade_history)
        st.download_button("📥 DOWNLOAD CSV", data=df.to_csv(index=False), file_name="Trades.csv", use_container_width=True)
else:
    st.info("No trades saved yet.")
