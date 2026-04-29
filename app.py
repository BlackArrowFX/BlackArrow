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
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

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

with st.expander("📜 MY TRADING PLAN", expanded=False):
    st.markdown("""
    ### 1. Market Structure Analysis
    * **1H / 15M / 5M Correlation Check.**
    * **Identify: Trend direction, BoS, Liquidity zones.**
    ### 2. Strategic Setup
    * Confirm Swing Highs/Lows and HTF bias.
    ### 3. Footprint Confirmation
    * 300% Imbalance Stack & Shark Absorption.
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
    placeholder="Log your thoughts here..."
)

# ---------------- CONFLUENCE & PHASE 3 ---------------- #
st.markdown("---")
system_unlocked = bias_15m_ok and news_ok
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Trading Zone", ["Select...", "Swing High", "Swing Low", "Supply", "Demand", "OB", "FVG"], disabled=not system_unlocked)
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    trade_dir = st.radio("Position Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True, disabled=not system_unlocked)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    sl_val = st.number_input("Stop Loss Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    
    if entry_val > 0 and sl_val > 0 and trade_dir != "Select...":
        actual_pips = abs(entry_val - sl_val) / pip_factor
        lot_size = (current_risk_usd / (actual_pips * 10)) if actual_pips > 0 else 0
        st.metric("Suggested Lot Size", f"{round(lot_size, 2)}")
        
        if st.button("💾 SAVE TRADE DETAILS", use_container_width=True):
            trade_data = {
                "Time": dt_string, "Asset": symbol, "Dir": trade_dir,
                "Entry": entry_val, "Lots": round(lot_size, 2), "POI": poi_type,
                "Plan": st.session_state.trade_notes
            }
            st.session_state.trade_history.append(trade_data)
            st.toast("Trade Logged!")

# ---------------- 📊 SESSION LOG (MODIFIED ROW) ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log")

if st.session_state.trade_history:
    # 1. Main Table (No Plan column)
    df_log = pd.DataFrame([{k: v for k, v in t.items() if k != "Plan"} for t in st.session_state.trade_history])
    st.table(df_log)

    # 2. Action Row (Delete, Clear, Download, Edit)
    c_del1, c_del2, c_dl, c_ed = st.columns(4)
    
    with c_del1:
        if st.button("🗑️ DELETE LAST", use_container_width=True):
            st.session_state.trade_history.pop()
            st.rerun()
    with c_del2:
        if st.button("🧨 CLEAR ALL", use_container_width=True):
            st.session_state.trade_history = []
            st.rerun()
    with c_dl:
        full_df = pd.DataFrame(st.session_state.trade_history)
        csv = full_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DOWNLOAD CSV", data=csv, file_name="Trade_Log.csv", mime="text/csv", use_container_width=True)
    with c_ed:
        edit_target = st.selectbox("Select Trade # to Edit Notes", range(1, len(st.session_state.trade_history) + 1))
        if st.button("📝 EDIT NOTES", use_container_width=True):
            st.session_state.edit_index = edit_target - 1

    # 3. Big Note Editor (Appears when EDIT is clicked)
    if st.session_state.edit_index is not None:
        st.markdown("---")
        st.subheader(f"🖋️ Editing Notes for Trade #{st.session_state.edit_index + 1}")
        
        updated_note = st.text_area(
            "Full Execution Plan (Big View):",
            value=st.session_state.trade_history[st.session_state.edit_index]["Plan"],
            height=300
        )
        
        col_save, col_cancel = st.columns(2)
        if col_save.button("✅ SAVE CHANGES", use_container_width=True):
            st.session_state.trade_history[st.session_state.edit_index]["Plan"] = updated_note
            st.session_state.edit_index = None
            st.success("Note Updated!")
            st.rerun()
        if col_cancel.button("Cancel", use_container_width=True):
            st.session_state.edit_index = None
            st.rerun()

    # 4. Read-Only Notes View
    st.subheader("📜 Current Execution Plans")
    for i, trade in enumerate(st.session_state.trade_history):
        with st.expander(f"Plan for Trade #{i+1} ({trade['Asset']} @ {trade['Time']})"):
            st.write(trade['Plan'])
else:
    st.info("No trades saved yet.")
