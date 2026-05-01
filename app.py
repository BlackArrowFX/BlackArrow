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

# ---------------- AMENDED TRADING PLAN SECTION ---------------- #
with st.expander("📜 MY TRADING PLAN", expanded=False):
    st.markdown("""
    ### 1. Market Structure Analysis
    * **1H:** Analyze overall market structure.
    * **15M:** Confirm short-term direction and intraday zones.
    * **5M:** Precise entry execution.
    * *Identify: Trend direction, BoS, Liquidity zones, and Reversal areas.*

    ### 2. BlackArrowFX Strategic Setup
    * Confirm and mark all **Swing Highs and Swing Lows** on every timeframe.
    * Ensure setup aligns with HTF bias before execution (POI & Key Levels).

    ### 3. BlackArrowClick Execution
    * Select **Fixed Lot** or **Risk Amount** before placing trade.
    * Pre-plan entry price and double-check **SL/TP** levels.

    ### 4. Risk Management
    * **Max Risk:** 3% to 5% or **$100 maximum**.
    * Maintain discipline; never exceed daily limits.

    ### 5. Footprint Monitoring
    * **Monitor:** **SHARK ABSORPTION 🦈 on 4H/1H & 15M/30M (+ or -) Delta Check.**
    * **Zones:** 15M & 30M Footprint Charts at key reversal zones.
    * **Buy Imbalances:** 🔵 **Blue Highlights** 
    * **Sell Imbalances:** 🟡 **Yellow Highlights** 
    * **Confirmation:** Focus on **300% Imbalance Stack** for strong order flow.
    * **Execution:** Use delta shifts, absorption, and imbalance clusters.
    
    **Final Rule:** Only execute when Structure + POI + Footprint + Risk are aligned.
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

# ---------------- STRATEGY NOTES (PERSISTENT) ---------------- #
st.markdown("---")
st.subheader("📝 EXECUTION PLANS & NOTES")

with st.expander("📌 VIEW/EDIT TRADE NOTES", expanded=True):
    note_input = st.text_area("Strategic Setup:", value=st.session_state.trade_notes, height=450, key="note_area")
    if st.button("💾 SAVE STRATEGIC NOTES", use_container_width=True):
        st.session_state.trade_notes = note_input
        sync_user_to_file()
        st.toast("Saved!")

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

# ---------------- CONFLUENCE METER ---------------- #
st.markdown("---")
confluences = [bias_4h_ok, bias_1h_ok, bias_30m_ok, bias_15m_ok, (m5_bos_ok or m5_mss_ok)]
score = sum(confluences)
progress = score / 5

col_met, col_stat = st.columns([3, 1])
with col_met:
    st.progress(progress)
with col_stat:
    st.write(f"**Setup Strength: {int(progress*100)}%**")

# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")
system_unlocked = bias_15m_ok and news_ok
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Trading Zone", ["Select...", "Swing High", "Swing Low", "Supply Zone", "Demand Zone", "Order Block", "FVG"], disabled=not system_unlocked)
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    trade_dir = st.radio("Position Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True, disabled=not system_unlocked)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    sl_distance_pips = 20
    calc_sl = 0.0
    if zone_price > 0 and trade_dir != "Select...":
        calc_sl = zone_price - (sl_distance_pips * pip_factor) if trade_dir == "LONG 🔵" else zone_price + (sl_distance_pips * pip_factor)

    sl_val = st.number_input(f"Stop Loss ({sl_distance_pips} Pips)", value=calc_sl, format="%.2f", disabled=not system_unlocked)
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    
    if entry_val > 0 and sl_val > 0 and trade_dir != "Select...":
        actual_pips_dist = abs(entry_val - sl_val) / pip_factor
        if actual_pips_dist > 0:
            lot_size = (current_risk_usd / actual_pips_dist) / 10
            tp1 = entry_val + (actual_pips_dist * 2 * pip_factor) if trade_dir == "LONG 🔵" else entry_val - (actual_pips_dist * 2 * pip_factor)
            be_price = entry_val 
            profit_tp1 = current_risk_usd * 2

            m1, m2 = st.columns(2)
            m1.metric("Lot Size", f"{round(lot_size, 2)}")
            m2.metric("TP 1 (1:2)", f"{round(tp1, 2)}", delta=f"+${round(profit_tp1, 2)}")
            
            st.info(f"🛡️ **PROTOCOL:** SL to BE at {round(tp1, 2)}.")
            
            if st.button("💾 SAVE TRADE DETAILS", use_container_width=True):
                trade_data = {
                    "Time": dt_string, "Asset": symbol, "Dir": trade_dir,
                    "Lots": round(lot_size, 2), "Entry": entry_val,
                    "TP1/BE": f"{round(tp1, 2)} / {round(be_price, 2)}",
                    "Plan": st.session_state.trade_notes
                }
                st.session_state.trade_history.append(trade_data)
                sync_user_to_file()
                st.toast("Trade Logged!")

# ---------------- 📊 SESSION LOG (RESTRUCTURED) ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log")

if st.session_state.trade_history:
    # 1. Create the Table first
    display_data = [{k: v for k, v in t.items() if k != "Plan"} for t in st.session_state.trade_history]
    df_log = pd.DataFrame(display_data)
    st.table(df_log)

    # 2. Show the Notes/Plans in a clean layout
    st.subheader("📜 Execution Plans & Notes")
    for i, trade in enumerate(st.session_state.trade_history):
        # Use a unique key for each expander to prevent state loss
        with st.expander(f"Plan for Trade #{i+1} ({trade['Asset']} @ {trade['Time']})"):
            st.write(trade.get('Plan', "No notes recorded for this trade."))

    # 3. FIX THE BUTTONS: Place them in a container to keep them grouped
    st.markdown("### 🛠️ Log Management")
    c_del1, c_del2, c_dl = st.columns([1, 1, 1]) # Equal widths often look better
    
    with c_del1:
        if st.button("🗑️ DELETE LAST", use_container_width=True):
            if st.session_state.trade_history:
                st.session_state.trade_history.pop()
                sync_user_to_file()
                st.rerun()
    
    with c_del2:
        if st.button("🧨 CLEAR ALL", use_container_width=True):
            st.session_state.trade_history = []
            sync_user_to_file()
            st.rerun()
            
    with c_dl:
        full_df = pd.DataFrame(st.session_state.trade_history)
        csv = full_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DOWNLOAD CSV", data=csv, file_name="Trade_Log.csv", mime="text/csv", use_container_width=True)
else:
    st.info("No trades saved yet.")
