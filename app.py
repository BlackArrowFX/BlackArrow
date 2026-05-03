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
    
    st.session_state.balance = st.number_input(
        "Current Balance ($)", 
        value=float(st.session_state.balance), 
        step=10.0, 
        format="%.2f"
    )
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)", "Fixed Lot Size"])
    
    current_risk_usd = 0.0
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    elif risk_method == "Fixed Amount ($)":
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)
    else:
        st.info("📊 Fixed Lot Mode Active")

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

    if st.button("Reset Daily Limits", use_container_width=True):
        st.session_state.trades_taken = 0
        sync_user_to_file()
        st.rerun()

# ---------------- MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Asset: {symbol} | Mode: {asset_type} | Server Time: {dt_string}")

with st.expander("📜 MY TRADING PLAN", expanded=False):
    st.markdown("""
    ### 1. Market Structure Analysis | 2. Strategic Setup | 3. Execution | 4. Risk | 5. Footprint
    """)

st.markdown("---")

# ---------------- QUAD TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)
with c4h:
    st.subheader("⏳ 4H BIAS")
    htf_bias = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", disabled=not news_ok)
    h_lock = not news_ok or htf_bias == "Select..."
    s4h = st.number_input("Swing High", value=st.session_state.s4h, format="%.2f", key="s4h_in", disabled=h_lock)
    s4l = st.number_input("Swing Low", value=st.session_state.s4l, format="%.2f", key="s4l_in", disabled=h_lock)
    st.session_state.s4h, st.session_state.s4l = s4h, s4l
    bias_4h_ok = st.checkbox("4H Confirmed", key="4h_c", disabled=h_lock or not (s4h > 0 and s4l > 0))

with c1h:
    st.subheader("⏱️ 1H STRUC")
    itf_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", disabled=not bias_4h_ok)
    i_lock = not bias_4h_ok or itf_trend == "Select..."
    s1h = st.number_input("1H High", value=st.session_state.s1h, format="%.2f", key="s1h_in", disabled=i_lock)
    s1l = st.number_input("1H Low", value=st.session_state.s1l, format="%.2f", key="s1l_in", disabled=i_lock)
    st.session_state.s1h, st.session_state.s1l = s1h, s1l
    bias_1h_ok = st.checkbox("1H Confirmed", key="1h_c", disabled=i_lock or not (s1h > 0 and s1l > 0))

with c30m:
    st.subheader("⚡ 30M SHIFT")
    t30_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t", disabled=not bias_1h_ok)
    m30_lock = not bias_1h_ok or t30_trend == "Select..."
    s30h = st.number_input("30M High", value=st.session_state.s30h, format="%.2f", key="s30h_in", disabled=m30_lock)
    s30l = st.number_input("30M Low", value=st.session_state.s30l, format="%.2f", key="s30l_in", disabled=m30_lock)
    st.session_state.s30h, st.session_state.s30l = s30h, s30l
    bias_30m_ok = st.checkbox("30M Confirmed", key="30m_c", disabled=m30_lock or not (s30h > 0 and s30l > 0))

with c15m:
    st.subheader("🎯 15M ENTRY")
    t15_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t", disabled=not bias_30m_ok)
    m15_lock = not bias_30m_ok or t15_trend == "Select..."
    s15h = st.number_input("15M High", value=st.session_state.s15h, format="%.2f", key="s15h_in", disabled=m15_lock)
    s15l = st.number_input("15M Low", value=st.session_state.s15l, format="%.2f", key="s15l_in", disabled=m15_lock)
    st.session_state.s15h, st.session_state.s15l = s15h, s15l
    bias_15m_ok = st.checkbox("15M Confirmed", key="15m_c", disabled=m15_lock or not (s15h > 0 and s15l > 0))

st.markdown("---")
# ---------------- 5M MICRO-CONFIRMATION ---------------- #
st.subheader("⚡ 5M MICRO-CONFIRMATION")
c5_1, c5_2, c5_3 = st.columns(3)
with c5_1:
    m5_trend = st.radio("5M Current Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="m5_t", disabled=not bias_15m_ok)
    m5_lock = not bias_15m_ok or m5_trend == "Select..."
with c5_2:
    m5_bos_p = st.number_input("BOS Price", value=0.0, format="%.2f", disabled=m5_lock)
    m5_mss_p = st.number_input("MSS Price", value=0.0, format="%.2f", disabled=m5_lock)
with c5_3:
    st.write("**Confirmation Type**")
    m5_bos_ok = st.checkbox("BOS Confirmed", disabled=m5_bos_p == 0)
    m5_mss_ok = st.checkbox("MSS Confirmed", disabled=m5_mss_p == 0)

st.markdown("---")
# ---------------- PHASE 2 & 3 ---------------- #
system_unlocked = bias_15m_ok and news_ok
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Trading Zone", ["Select...", "Order Block", "FVG", "Supply", "Demand"], disabled=not system_unlocked)
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    trade_dir = st.radio("Position Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True, disabled=not system_unlocked)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    
    # Lot input if Fixed Lot Size is chosen in sidebar
    fixed_lot_val = 0.10
    if risk_method == "Fixed Lot Size":
        fixed_lot_val = st.number_input("Enter Fixed Lot Size", min_value=0.01, max_value=100.0, value=0.10, step=0.01, disabled=not system_unlocked)
    
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    
    # Manual Take Profit Input (NEW: On top of Entry Price)
    tp_val = st.number_input("Manual Take Profit Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    
    # Manual Entry Price
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f", disabled=not system_unlocked)

    # Stop Loss
    sl_distance_pips = 20
    calc_sl = 0.0
    if entry_val > 0 and trade_dir != "Select...":
        calc_sl = entry_val - (sl_distance_pips * pip_factor) if trade_dir == "LONG 🔵" else entry_val + (sl_distance_pips * pip_factor)
    sl_val = st.number_input(f"Stop Loss (Default {sl_distance_pips} Pips)", value=calc_sl, format="%.2f", disabled=not system_unlocked)
    
    if entry_val > 0 and sl_val > 0 and tp_val > 0 and trade_dir != "Select...":
        actual_sl_pips = abs(entry_val - sl_val) / pip_factor
        actual_tp_pips = abs(entry_val - tp_val) / pip_factor
        
        if actual_sl_pips > 0:
            if risk_method == "Fixed Lot Size":
                lot_size = fixed_lot_val
                # Profit = (Lots * 10) * Pips
                profit_usd = (lot_size * 10) * actual_tp_pips
            else:
                lot_size = (current_risk_usd / actual_sl_pips) / 10
                # Profit based on RR relative to risk
                rr_ratio = actual_tp_pips / actual_sl_pips
                profit_usd = current_risk_usd * rr_ratio

            m1, m2 = st.columns(2)
            m1.metric("Calculated Lot Size", f"{round(lot_size, 2)}")
            m2.metric("Target Profit", f"${round(profit_usd, 2)}", delta=f"{round(actual_tp_pips / actual_sl_pips, 2)} RR")
            
            if st.button("💾 SAVE TRADE DETAILS", use_container_width=True):
                trade_data = {
                    "Time": dt_string, "Asset": symbol, "Dir": trade_dir,
                    "Lots": round(lot_size, 2), "Entry": entry_val,
                    "TP": round(tp_val, 2), "SL": round(sl_val, 2)
                }
                st.session_state.trade_history.append(trade_data)
                sync_user_to_file(); st.toast("Trade Logged!")

# ---------------- SESSION LOG ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log")
if st.session_state.trade_history:
    st.table(pd.DataFrame(st.session_state.trade_history))
    if st.button("🧨 CLEAR ALL"):
        st.session_state.trade_history = []; sync_user_to_file(); st.rerun()
else:
    st.info("No trades saved yet.")
