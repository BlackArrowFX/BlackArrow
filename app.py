import streamlit as st
from datetime import datetime
import pandas as pd
import json
import os

# ---------------- 0. PERSISTENCE ENGINE (STABLE VERSION) ---------------- #
USER_DATA_FILE = "user_vault_data.json" 

def load_vault():
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
    except Exception:
        return {}
    return {}

def save_vault(vault_data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(vault_data, f)

def sync_user_to_file():
    """Saves session state and current inputs to the local file."""
    if st.session_state.get("current_user"):
        vault = load_vault()
        vault[st.session_state.current_user] = {
            "balance": st.session_state.balance,
            "trades_taken": st.session_state.trades_taken,
            "trade_notes": st.session_state.trade_notes,
            "trade_history": st.session_state.trade_history,
            "s4h": st.session_state.get("s4h", 0.0),
            "s4l": st.session_state.get("s4l", 0.0),
            "s1h": st.session_state.get("s1h", 0.0),
            "s1l": st.session_state.get("s1l", 0.0),
            "s30h": st.session_state.get("s30h", 0.0),
            "s30l": st.session_state.get("s30l", 0.0),
            "s15h": st.session_state.get("s15h", 0.0),
            "s15l": st.session_state.get("s15l", 0.0)
        }
        save_vault(vault)

# ---------------- 1. LOGIN / ACCESS GATE ---------------- #
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if st.session_state.current_user is None:
    st.title("🏹 BlackArrowFX Access")
    u_input = st.text_input("Enter Username to Start / Register").lower().strip()
    if st.button("Enter Engine"):
        if u_input:
            vault = load_vault()
            if u_input in vault:
                data = vault[u_input]
                st.session_state.balance = data.get("balance", 2146.11)
                st.session_state.trades_taken = data.get("trades_taken", 0)
                st.session_state.trade_notes = data.get("trade_notes", "")
                st.session_state.trade_history = data.get("trade_history", [])
                st.session_state.s4h = data.get("s4h", 0.0)
                st.session_state.s4l = data.get("s4l", 0.0)
                st.session_state.s1h = data.get("s1h", 0.0)
                st.session_state.s1l = data.get("s1l", 0.0)
                st.session_state.s30h = data.get("s30h", 0.0)
                st.session_state.s30l = data.get("s30l", 0.0)
                st.session_state.s15h = data.get("s15h", 0.0)
                st.session_state.s15l = data.get("s15l", 0.0)
            else:
                st.session_state.balance = 2146.11
                st.session_state.trades_taken = 0
                st.session_state.trade_notes = ""
                st.session_state.trade_history = []
                for key in ["s4h", "s4l", "s1h", "s1l", "s30h", "s30l", "s15h", "s15l"]:
                    st.session_state[key] = 0.0
            
            st.session_state.current_user = u_input
            sync_user_to_file()
            st.rerun()
    st.stop()

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & SYSTEM ---------------- #
with st.sidebar:
    st.header(f"👤 User: {st.session_state.current_user.upper()}")
    if st.button("Logout"):
        st.session_state.current_user = None
        st.rerun()

    st.header("⚙️ System Config")
    asset_type = st.selectbox("Select Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"], index=0)
    symbol = st.text_input("Enter Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    st.session_state.balance = st.number_input("Current Balance ($)", value=float(st.session_state.balance), step=10.0, format="%.2f")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)", "Fixed Lot Size"])
    current_risk_usd = 0.0
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    elif risk_method == "Fixed Amount ($)":
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)

    st.markdown("---")
    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News Active", value=False) 
    
    st.header("📊 Daily Journal")
    st.write(f"Trades Taken: **{st.session_state.trades_taken} / 3**")
    limit_reached = st.session_state.trades_taken >= 3

    if st.button("❌ RECORD LOSS", use_container_width=True, disabled=limit_reached):
        st.session_state.balance -= current_risk_usd if risk_method != "Fixed Lot Size" else 0.0
        st.session_state.trades_taken += 1
        sync_user_to_file()
        st.rerun()

    with st.expander("✅ RECORD WIN", expanded=False):
        profit_made = st.number_input("Profit Made ($)", min_value=0.0, value=0.0, step=1.0)
        if st.button("Add to Balance", use_container_width=True, disabled=limit_reached):
            st.session_state.balance += profit_made
            st.session_state.trades_taken += 1
            sync_user_to_file()
            st.rerun()

# ---------------- MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Asset: {symbol} | Mode: {asset_type} | Server Time: {dt_string}")

# ---------------- TIMEFRAME ANALYSIS (OMITTED FOR BREVITY - KEEP YOURS) ---------------- #
# [Keep your c4h, c1h, c30m, c15m columns here exactly as they were]

# ---------------- STRATEGY NOTES (PERSISTENT) ---------------- #
st.markdown("---")
st.subheader("📝 EXECUTION PLANS & NOTES")
with st.expander("📌 VIEW/EDIT TRADE NOTES", expanded=True):
    note_input = st.text_area("Strategic Setup:", value=st.session_state.trade_notes, height=200, key="note_area")
    if st.button("💾 SAVE STRATEGIC NOTES", use_container_width=True):
        st.session_state.trade_notes = note_input
        sync_user_to_file()
        st.toast("Saved!")

# ---------------- PHASE 2 & 3 ---------------- #
system_unlocked = news_ok # Simplified for this block
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Trading Zone", ["Select...", "Order Block", "FVG", "Supply", "Demand"], disabled=not system_unlocked)
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    trade_dir = st.radio("Position Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True, disabled=not system_unlocked)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    
    if risk_method == "Fixed Lot Size":
        fixed_lot_val = st.number_input("Enter Fixed Lot Size", min_value=0.01, value=0.10, step=0.01)
    
    tp_val = st.number_input("Manual Take Profit Price", value=0.0, format="%.2f")
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f")
    
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    sl_distance_pips = 20
    calc_sl = 0.0
    if entry_val > 0 and trade_dir != "Select...":
        calc_sl = entry_val - (sl_distance_pips * pip_factor) if trade_dir == "LONG 🔵" else entry_val + (sl_distance_pips * pip_factor)
    
    sl_val = st.number_input(f"Stop Loss Price", value=calc_sl, format="%.2f")

    if entry_val > 0 and sl_val > 0 and tp_val > 0 and trade_dir != "Select...":
        dist_sl = abs(entry_val - sl_val) / pip_factor
        dist_tp = abs(entry_val - tp_val) / pip_factor
        
        if dist_sl > 0:
            if risk_method == "Fixed Lot Size":
                lot_size = fixed_lot_val
                profit_usd = (lot_size * 10) * dist_tp
            else:
                lot_size = (current_risk_usd / dist_sl) / 10
                profit_usd = current_risk_usd * (dist_tp / dist_sl)

            m1, m2 = st.columns(2)
            m1.metric("Lot Size", f"{round(lot_size, 2)}")
            m2.metric("Target Profit", f"${round(profit_usd, 2)}", delta=f"{round(dist_tp/dist_sl, 2)} RR")
            
            if st.button("💾 SAVE TRADE DETAILS", use_container_width=True):
                trade_data = {
                    "Time": dt_string, "Asset": symbol, "Dir": trade_dir,
                    "Lots": round(lot_size, 2), "Entry": entry_val,
                    "TP": tp_val, "SL": sl_val, "Plan": st.session_state.trade_notes
                }
                st.session_state.trade_history.append(trade_data)
                sync_user_to_file()
                st.toast("Trade Logged!")

# ---------------- 📊 RESTORED SESSION LOG ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log")

if st.session_state.trade_history:
    # 1. Main Table
    display_df = pd.DataFrame([{k: v for k, v in t.items() if k != "Plan"} for t in st.session_state.trade_history])
    st.table(display_df)

    # 2. Re-show individual Plans
    st.subheader("📜 Execution Plans")
    for i, trade in enumerate(st.session_state.trade_history):
        with st.expander(f"Plan for Trade #{i+1} ({trade['Asset']} @ {trade['Time']})"):
            st.write(trade.get('Plan', "No notes recorded."))

    # 3. Management Buttons
    st.markdown("### 🛠️ Log Management")
    c_del1, c_del2, c_dl = st.columns(3)
    with c_del1:
        if st.button("🗑️ DELETE LAST", use_container_width=True):
            if st.session_state.trade_history:
                st.session_state.trade_history.pop(); sync_user_to_file(); st.rerun()
    with c_del2:
        if st.button("🧨 CLEAR ALL", use_container_width=True):
            st.session_state.trade_history = []; sync_user_to_file(); st.rerun()
    with c_dl:
        csv = pd.DataFrame(st.session_state.trade_history).to_csv(index=False).encode('utf-8')
        st.download_button("📥 DOWNLOAD CSV", data=csv, file_name="Trade_Log.csv", mime="text/csv", use_container_width=True)
else:
    st.info("No trades saved yet.")
