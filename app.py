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

# --- PERSISTENT SWING LEVELS ---
levels = ["s4h", "s4l", "s1h", "s1l", "s30h", "s30l", "s15h", "s15l"]
for level in levels:
    if level not in st.session_state:
        st.session_state[level] = 0.0

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & SYSTEM ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    asset_type = st.selectbox("Select Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"])
    symbol = st.text_input("Enter Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    st.session_state.balance = st.number_input("Balance ($)", value=float(st.session_state.balance), step=10.0, format="%.2f")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)

    st.markdown("---")
    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News Active", value=False) 
    
    st.markdown("---")
    st.header("📊 Daily Journal")
    st.write(f"Trades Taken: **{st.session_state.trades_taken} / 3**")
    limit_reached = st.session_state.trades_taken >= 3

    if st.button("❌ RECORD LOSS", use_container_width=True, disabled=limit_reached):
        st.session_state.balance -= current_risk_usd 
        st.session_state.trades_taken += 1
        st.rerun()

    if st.button("Reset Daily Limits", use_container_width=True):
        st.session_state.trades_taken = 0
        st.rerun()

# ---------------- MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Server Time: {dt_string}")
st.markdown("---")

# ---------------- QUAD TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)

with c4h:
    st.subheader("⏳ 4H BIAS")
    st.session_state.s4h = st.number_input("Swing High", value=st.session_state.s4h, format="%.2f")
    st.session_state.s4l = st.number_input("Swing Low", value=st.session_state.s4l, format="%.2f")
    bias_4h_ok = st.checkbox("4H Confirmed", key="4h_c")

with c1h:
    st.subheader("⏱️ 1H STRUC")
    st.session_state.s1h = st.number_input("1H High", value=st.session_state.s1h, format="%.2f")
    st.session_state.s1l = st.number_input("1H Low", value=st.session_state.s1l, format="%.2f")
    bias_1h_ok = st.checkbox("1H Confirmed", key="1h_c")

with c30m:
    st.subheader("⚡ 30M SHIFT")
    st.session_state.s30h = st.number_input("30M High", value=st.session_state.s30h, format="%.2f")
    st.session_state.s30l = st.number_input("30M Low", value=st.session_state.s30l, format="%.2f")
    bias_30m_ok = st.checkbox("30M Confirmed", key="30m_c")

with c15m:
    st.subheader("🎯 15M ENTRY")
    st.session_state.s15h = st.number_input("15M High", value=st.session_state.s15h, format="%.2f")
    st.session_state.s15l = st.number_input("15M Low", value=st.session_state.s15l, format="%.2f")
    bias_15m_ok = st.checkbox("15M Confirmed", key="15m_c")

# ---------------- STRATEGY NOTES ---------------- #
st.markdown("---")
st.subheader("📝 POST-SHOCK EXECUTION PLAN")
st.session_state.trade_notes = st.text_area("Paste Strategic Setup Here:", value=st.session_state.trade_notes, height=200)

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Zone", ["Select...", "Swing High", "Swing Low", "Order Block", "FVG"])
    zone_price = st.number_input("Zone Price", value=0.0, format="%.2f")
    trade_dir = st.radio("Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f")
    sl_val = st.number_input("Stop Loss", value=0.0, format="%.2f")
    
    if entry_val > 0 and sl_val > 0:
        actual_pips = abs(entry_val - sl_val) / pip_factor
        lot_size = (current_risk_usd / actual_pips) / 10 if actual_pips > 0 else 0
        tp1 = entry_val + (actual_pips * 2 * pip_factor) if trade_dir == "LONG 🔵" else entry_val - (actual_pips * 2 * pip_factor)
        
        m1, m2 = st.columns(2)
        m1.metric("Lot Size", f"{round(lot_size, 2)}")
        m2.metric("TP 1 (1:2)", f"{round(tp1, 2)}")

        if st.button("💾 SAVE TRADE DETAILS", use_container_width=True):
            trade_data = {
                "Time": dt_string, "Asset": symbol, "Dir": trade_dir,
                "4H": f"H:{st.session_state.s4h}/L:{st.session_state.s4l}",
                "1H": f"H:{st.session_state.s1h}/L:{st.session_state.s1l}",
                "30M": f"H:{st.session_state.s30h}/L:{st.session_state.s30l}",
                "15M": f"H:{st.session_state.s15h}/L:{st.session_state.s15l}",
                "Entry": entry_val, "SL": sl_val, "TP1": round(tp1, 2),
                "POI": f"{poi_type} @ {zone_price}", "Lots": round(lot_size, 2),
                "Notes": st.session_state.trade_notes
            }
            st.session_state.trade_history.append(trade_data)
            st.toast("Trade Logged!")

# ---------------- 📊 SESSION LOG & ALIGNED REPORT ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log")

if st.session_state.trade_history:
    df_log = pd.DataFrame(st.session_state.trade_history)
    
    # DISPLAY TABLE: Hide 'Notes' to keep columns aligned and neat
    st.subheader("📜 Summary Journal (Aligned)")
    st.dataframe(df_log.drop(columns=['Notes']), use_container_width=True)

    # DETAILED ALIGNED REPORT
    st.markdown("---")
    st.subheader("📑 Detailed Execution Report (Last Entry)")
    
    last = st.session_state.trade_history[-1]
    rep1, rep2, rep3 = st.columns(3)
    
    with rep1:
        st.markdown(f"**CORE DATA**\n- **Asset:** `{last.get('Asset')}`\n- **Dir:** `{last.get('Dir')}`\n- **Entry:** `{last.get('Entry')}`\n- **Lots:** `{last.get('Lots')}`")
    with rep2:
        st.markdown(f"**SWING LEVELS**\n- **4H:** `{last.get('4H')}`\n- **1H:** `{last.get('1H')}`\n- **30M:** `{last.get('30M')}`\n- **15M:** `{last.get('15M')}`")
    with rep3:
        st.markdown(f"**TARGETS**\n- **SL:** `{last.get('SL')}`\n- **TP1/BE:** `{last.get('TP1')}`\n- **POI:** `{last.get('POI')}`")
    
    st.success(f"**📝 STRATEGIC EXECUTION NOTES:**\n\n{last.get('Notes')}")

    if st.button("🧨 CLEAR ALL LOGS", use_container_width=True):
        st.session_state.trade_history = []
        st.rerun()
else:
    st.info("Journal is empty.")
