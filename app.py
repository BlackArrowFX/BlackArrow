import streamlit as st
from datetime import datetime
import pandas as pd
import json
import os

# ---------------- 0. PERSISTENCE ENGINE (RESTORE LOGIC) ---------------- #
USER_DATA_FILE = "user_vault_data.json" 

def load_vault():
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                content = f.read()
                return json.loads(content) if content else {}
    except Exception:
        return {}
    return {}

def save_vault(vault_data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(vault_data, f, indent=4)

def sync_user_to_file():
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

# ---------------- 1. LOGIN / RETRIEVAL GATE ---------------- #
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if st.session_state.current_user is None:
    st.title("🏹 BlackArrowFX Access")
    u_input = st.text_input("Enter Username").lower().strip()
    if st.button("Enter Engine"):
        if u_input:
            vault = load_vault()
            if u_input in vault:
                data = vault[u_input]
                st.session_state.balance = data.get("balance", 2146.11)
                st.session_state.trades_taken = data.get("trades_taken", 0)
                st.session_state.trade_notes = data.get("trade_notes", "")
                st.session_state.trade_history = data.get("trade_history", [])
                # Re-load Swing Levels
                for key in ["s4h", "s4l", "s1h", "s1l", "s30h", "s30l", "s15h", "s15l"]:
                    st.session_state[key] = data.get(key, 0.0)
            else:
                st.session_state.balance = 2146.11
                st.session_state.trades_taken = 0
                st.session_state.trade_notes = ""
                st.session_state.trade_history = []
                for key in ["s4h", "s4l", "s1h", "s1l", "s30h", "s30l", "s15h", "s15l"]:
                    st.session_state[key] = 0.0
            
            st.session_state.current_user = u_input
            st.rerun()
    st.stop()

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR: RISK & SYSTEM ---------------- #
with st.sidebar:
    st.header(f"👤 {st.session_state.current_user.upper()}")
    if st.button("Logout"):
        st.session_state.current_user = None
        st.rerun()

    asset_type = st.selectbox("Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"])
    symbol = st.text_input("Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    st.session_state.balance = st.number_input("Balance ($)", value=float(st.session_state.balance), step=10.0, format="%.2f")
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)", "Fixed Lot Size"])
    
    current_risk_usd = 0.0
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk %", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    elif risk_method == "Fixed Amount ($)":
        current_risk_usd = st.number_input("Risk $", min_value=1.0, value=50.0)

    news_ok = st.toggle("No High Impact News Active", value=False) 

# ---------------- MAIN UI ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol}")

# (Note: I kept your Quad Timeframe code in memory, make sure it's present in your file)

# ---------------- PHASE 2 & 3: EXECUTION ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 POI")
    poi_type = st.selectbox("Zone", ["Select...", "Order Block", "FVG", "Supply", "Demand"])
    trade_dir = st.radio("Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True)

with col_exec:
    st.header("🚀 EXECUTE")
    
    # Lot input if Fixed Lot Size is chosen
    if risk_method == "Fixed Lot Size":
        fixed_lot = st.number_input("Fixed Lot Size", min_value=0.01, value=0.10)
    
    # MANUAL TP ON TOP
    manual_tp = st.number_input("Manual Take Profit Price", value=0.0, format="%.2f")
    
    # MANUAL ENTRY
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f")

    # STOP LOSS
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    calc_sl = 0.0
    if entry_val > 0 and trade_dir != "Select...":
        calc_sl = entry_val - (20 * pip_factor) if trade_dir == "LONG 🔵" else entry_val + (20 * pip_factor)
    sl_val = st.number_input("Stop Loss Price", value=calc_sl, format="%.2f")

    if entry_val > 0 and sl_val > 0 and manual_tp > 0 and trade_dir != "Select...":
        dist_sl = abs(entry_val - sl_val) / pip_factor
        dist_tp = abs(entry_val - manual_tp) / pip_factor
        
        if dist_sl > 0:
            if risk_method == "Fixed Lot Size":
                lot_size = fixed_lot
                profit_usd = (lot_size * 10) * dist_tp
            else:
                lot_size = (current_risk_usd / dist_sl) / 10
                profit_usd = current_risk_usd * (dist_tp / dist_sl)

            st.metric("Lot Size", f"{round(lot_size, 2)}")
            st.metric("Target Profit", f"${round(profit_usd, 2)}", delta=f"{round(dist_tp/dist_sl, 2)} RR")
            
            if st.button("💾 SAVE TRADE DETAILS", use_container_width=True):
                trade_data = {
                    "Time": dt_string, "Asset": symbol, "Dir": trade_dir,
                    "Lots": round(lot_size, 2), "Entry": entry_val,
                    "TP": manual_tp, "SL": sl_val, "Plan": st.session_state.trade_notes
                }
                st.session_state.trade_history.append(trade_data)
                sync_user_to_file()
                st.toast("Trade Logged!")

# ---------------- 📂 SESSION LOG (THE RETRIEVAL VIEW) ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log")

if st.session_state.trade_history:
    # 1. Main Table (Hide 'Plan' from the main table for better width)
    display_df = pd.DataFrame([{k: v for k, v in t.items() if k != "Plan"} for t in st.session_state.trade_history])
    st.table(display_df)

    # 2. Execution Plans (Restored Notes)
    st.subheader("📜 Saved Execution Plans")
    for i, t in enumerate(st.session_state.trade_history):
        with st.expander(f"Plan for Trade #{i+1} ({t['Asset']} @ {t['Time']})"):
            st.info(t.get('Plan', "No notes recorded."))

    # 3. Management
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🗑️ DELETE LAST"):
            st.session_state.trade_history.pop(); sync_user_to_file(); st.rerun()
    with c2:
        if st.button("🧨 CLEAR ALL"):
            st.session_state.trade_history = []; sync_user_to_file(); st.rerun()
    with c3:
        csv = pd.DataFrame(st.session_state.trade_history).to_csv(index=False).encode('utf-8')
        st.download_button("📥 DOWNLOAD CSV", data=csv, file_name="Trade_History.csv")
else:
    st.info("No trades saved yet. Log in with your username to see previous data.")
