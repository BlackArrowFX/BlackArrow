import streamlit as st
from datetime import datetime
import pandas as pd

# ---------------- 1. INITIALIZE GLOBAL STATE ---------------- #
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11  
if "trades_taken" not in st.session_state:
    st.session_state.trades_taken = 0
if "trade_history" not in st.session_state:
    st.session_state.trade_history = []

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
    news_ok = st.toggle("No High Impact News Active", value=False) 
    
    if not news_ok:
        st.error("🚨 SYSTEM LOCKED")
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

    if st.button("Reset Daily Limits", use_container_width=True):
        st.session_state.trades_taken = 0
        st.rerun()

# ---------------- MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")

# ---------------- QUAD TIMEFRAME ANALYSIS (Simplified for brevity) ---------------- #
# (Keeping your existing timeframe logic variables bias_4h_ok, s4_h, etc.)
c4h, c1h, c30m, c15m = st.columns(4)
with c4h:
    htf_bias = st.radio("4H Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️"], key="4h_t")
    s4_h = st.number_input("4H High", value=0.0, key="s4h")
    s4_l = st.number_input("4H Low", value=0.0, key="s4l")
    bias_4h_ok = htf_bias != "Select..." and s4_h > 0
with c1h:
    itf_trend = st.radio("1H Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️"], key="1h_t")
    s1_h = st.number_input("1H High", value=0.0, key="s1h")
    s1_l = st.number_input("1H Low", value=0.0, key="s1l")
    bias_1h_ok = itf_trend != "Select..." and s1_h > 0
with c30m:
    t30_trend = st.radio("30M Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️"], key="30m_t")
    s30_h = st.number_input("30M High", value=0.0, key="s30h")
    s30_l = st.number_input("30M Low", value=0.0, key="s30l")
    bias_30m_ok = t30_trend != "Select..." and s30_h > 0
with c15m:
    t15_trend = st.radio("15M Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️"], key="15m_t")
    s15_h = st.number_input("15M High", value=0.0, key="s15h")
    s15_l = st.number_input("15M Low", value=0.0, key="s15l")
    bias_15m_ok = t15_trend != "Select..." and s15_h > 0

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
system_unlocked = bias_15m_ok and news_ok
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Zone", ["Select...", "Swing High", "Swing Low", "Supply", "Demand"], disabled=not system_unlocked)
    zone_price = st.number_input("Entry Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    trade_dir = st.radio("Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True, disabled=not system_unlocked)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else 0.0001
    entry_val = st.number_input("Manual Entry", value=zone_price, format="%.2f", disabled=not system_unlocked)
    sl_val = st.number_input("Stop Loss", value=0.0, format="%.2f", disabled=not system_unlocked)
    
    if entry_val > 0 and sl_val > 0 and trade_dir != "Select...":
        diff = abs(entry_val - sl_val)
        lot_size = (current_risk_usd / (diff / pip_factor)) / 10
        tp1 = entry_val + (diff * 2) if trade_dir == "LONG 🔵" else entry_val - (diff * 2)

        st.metric("Lots", round(lot_size, 4))
        if st.button("💾 SAVE TRADE DETAILS", use_container_width=True):
            trade_data = {
                "Time": dt_string,
                "Asset": symbol,
                "Dir": trade_dir,
                "4H": f"{s4_h}/{s4_l}",
                "1H": f"{s1_h}/{s1_l}",
                "30M": f"{s30_h}/{s30_l}",
                "15M": f"{s15_h}/{s15_l}",
                "POI": f"{poi_type} @ {zone_price}",
                "Lots": round(lot_size, 4),
                "Entry": entry_val,
                "TP1/BE": f"{round(tp1, 2)} / {round(entry_val, 2)}",
                "Plan": "Enter notes here..."
            }
            st.session_state.trade_history.append(trade_data)
            st.toast("Trade Logged!")

# ---------------- 📊 UPDATED SESSION LOG & NOTE MANAGER ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log & Note Manager")

if st.session_state.trade_history:
    # 1. Table Display
    df_log = pd.DataFrame(st.session_state.trade_history).drop(columns=["Plan"])
    st.table(df_log)

    # 2. Dynamic Note Editor (Edit, Save, Delete per trade)
    st.subheader("📝 Execution Plans & Notes")
    
    indices_to_remove = []
    for i, trade in enumerate(st.session_state.trade_history):
        with st.expander(f"Trade #{i+1} | {trade['Asset']} | {trade['Time']}", expanded=False):
            # Edit Note
            new_note = st.text_area(f"Edit Plan for Trade {i+1}", value=trade['Plan'], key=f"note_{i}")
            
            c1, c2, c3 = st.columns([1, 1, 4])
            if c1.button("💾 Update Note", key=f"save_{i}"):
                st.session_state.trade_history[i]['Plan'] = new_note
                st.success("Note saved!")
            
            if c2.button("🗑️ Delete Trade", key=f"del_{i}"):
                indices_to_remove.append(i)
                st.rerun()

    # Handle deletion
    for index in sorted(indices_to_remove, reverse=True):
        st.session_state.trade_history.pop(index)

    # 3. Global Actions
    st.markdown("---")
    full_df = pd.DataFrame(st.session_state.trade_history)
    csv = full_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DOWNLOAD CSV (All Details + Notes)", data=csv, file_name="Trade_Log_Full.csv", mime="text/csv", use_container_width=True)
else:
    st.info("No trades saved yet.")
