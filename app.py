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

# ---------------- AMENDED TRADING PLAN SECTION ---------------- #
with st.expander("📜 MY TRADING PLAN", expanded=False):
    st.markdown("""
    ### 1. Market Structure Analysis
    * **1H:** Analyze overall market structure.
    * **15M:** Confirm short-term direction and intraday zones.
    * **5M:** Precise entry execution.
    
    ### 2. BlackArrowFX Strategic Setup
    * Confirm Swing Highs/Lows on all timeframes.
    * Align with HTF bias (POI & Key Levels).
    """)

st.markdown("---")

# ---------------- QUAD TIMEFRAME ANALYSIS (Original Logic) ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)
with c4h:
    st.subheader("⏳ 4H BIAS")
    htf_bias = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t", disabled=not news_ok)
    s4_h = st.number_input("Swing High", value=0.0, format="%.2f", key="s4h")
    s4_l = st.number_input("Swing Low", value=0.0, format="%.2f", key="s4l")
    bias_4h_ok = st.checkbox("4H Confirmed", key="4h_c", disabled=not (s4_h > 0))

with c1h:
    st.subheader("⏱️ 1H STRUC")
    itf_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t", disabled=not bias_4h_ok)
    s1_h = st.number_input("1H High", value=0.0, format="%.2f", key="s1h")
    s1_l = st.number_input("1H Low", value=0.0, format="%.2f", key="s1l")
    bias_1h_ok = st.checkbox("1H Confirmed", key="1h_c", disabled=not (s1_h > 0))

with c30m:
    st.subheader("⚡ 30M SHIFT")
    t30_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t", disabled=not bias_1h_ok)
    s30_h = st.number_input("30M High", value=0.0, format="%.2f", key="s30h")
    s30_l = st.number_input("30M Low", value=0.0, format="%.2f", key="s30l")
    bias_30m_ok = st.checkbox("30M Confirmed", key="30m_c", disabled=not (s30_h > 0))

with c15m:
    st.subheader("🎯 15M ENTRY")
    t15_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t", disabled=not bias_30m_ok)
    s15_h = st.number_input("15M High", value=0.0, format="%.2f", key="s15h")
    s15_l = st.number_input("15M Low", value=0.0, format="%.2f", key="s15l")
    bias_15m_ok = st.checkbox("15M Confirmed", key="15m_c", disabled=not (s15_h > 0))

# ---------------- LIVE STRATEGY NOTES ---------------- #
st.markdown("---")
st.subheader("📝 PRE-ENTRY EXECUTION PLAN")
st.session_state.trade_notes = st.text_area(
    "Paste Setup Details Here:",
    value=st.session_state.trade_notes,
    height=150,
    placeholder="Triggers, Imbalances, Shark Absorption..."
)

# ---------------- PHASE 2 & 3 ---------------- #
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
    sl_distance_pips = 20
    calc_sl = 0.0
    if zone_price > 0 and trade_dir != "Select...":
        calc_sl = zone_price - (sl_distance_pips * pip_factor) if trade_dir == "LONG 🔵" else zone_price + (sl_distance_pips * pip_factor)

    sl_val = st.number_input(f"Stop Loss", value=calc_sl, format="%.2f", disabled=not system_unlocked)
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f", disabled=not system_unlocked)
    
    if entry_val > 0 and sl_val > 0 and trade_dir != "Select...":
        actual_pips_dist = abs(entry_val - sl_val) / pip_factor
        if actual_pips_dist > 0:
            lot_size = (current_risk_usd / actual_pips_dist) / 10
            tp1 = entry_val + (actual_pips_dist * 2 * pip_factor) if trade_dir == "LONG 🔵" else entry_val - (actual_pips_dist * 2 * pip_factor)
            
            m1, m2 = st.columns(2)
            m1.metric("Lot Size", f"{round(lot_size, 4)}")
            m2.metric("TP 1 (1:2)", f"{round(tp1, 2)}")
            
            if st.button("💾 SAVE TRADE DETAILS", use_container_width=True):
                trade_data = {
                    "Time": dt_string,
                    "Asset": symbol,
                    "Dir": trade_dir,
                    "POI": f"{poi_type} @ {zone_price}",
                    "Lots": round(lot_size, 4),
                    "Entry": entry_val,
                    "TP1/BE": f"{round(tp1, 2)} / {round(entry_val, 2)}",
                    "Plan": st.session_state.trade_notes
                }
                st.session_state.trade_history.append(trade_data)
                st.toast("Trade Logged!")

# ---------------- 📊 LIVE HYBRID DATA EDITOR ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log (Live Hybrid Editor)")
st.info("💡 You can edit any cell below directly. Changes save automatically.")

if st.session_state.trade_history:
    # Convert history to DataFrame
    df_history = pd.DataFrame(st.session_state.trade_history)

    # USE DATA_EDITOR: This allows editing and viewing at the same time
    edited_df = st.data_editor(
        df_history,
        column_config={
            "Plan": st.column_config.TextColumn("Execution Plan & Notes", width="large", required=True),
            "Time": st.column_config.TextColumn(disabled=True), # Lock the timestamp
        },
        num_rows="dynamic", # Allows you to add/delete rows directly in the table
        use_container_width=True,
        key="history_editor"
    )

    # Sync changes back to session state
    if st.button("🔄 Commit Changes to History", use_container_width=True):
        st.session_state.trade_history = edited_df.to_dict('records')
        st.rerun()

    # DOWNLOAD LOG
    csv = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DOWNLOAD EDITED CSV", data=csv
