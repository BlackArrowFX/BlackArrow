import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- 1. INITIALIZE GLOBAL STATE ---------------- #
# Keeps track of your balance and trade history throughout the session
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11  
if "trades_taken" not in st.session_state:
    st.session_state.trades_taken = 0
if "trade_notes" not in st.session_state:
    st.session_state.trade_notes = ""
if "trade_history" not in st.session_state:
    st.session_state.trade_history = []

# ---------------- 2. SYSTEM SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide", page_icon="🏹")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- 3. SIDEBAR: RISK & SYSTEM ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    asset_type = st.selectbox("Select Asset Class", ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"])
    symbol = st.text_input("Enter Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")
    st.session_state.balance = st.number_input("Current Balance ($)", value=float(st.session_state.balance), step=10.0, format="%.2f")
    
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
    
    if st.button("❌ RECORD LOSS", use_container_width=True):
        st.session_state.balance -= current_risk_usd 
        st.session_state.trades_taken += 1
        st.rerun()

    with st.expander("✅ RECORD WIN", expanded=False):
        profit_made = st.number_input("Profit Made ($)", min_value=0.0, value=0.0, step=1.0)
        if st.button("Add to Balance", use_container_width=True):
            st.session_state.balance += profit_made
            st.session_state.trades_taken += 1
            st.rerun()

# ---------------- 4. MAIN INTERFACE ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"Server Time: {dt_string} | Mode: {asset_type}")
st.markdown("---")

# ---------------- 5. QUAD TIMEFRAME ANALYSIS ---------------- #
c4h, c1h, c30m, c15m = st.columns(4)

with c4h:
    st.subheader("⏳ 4H BIAS")
    htf_bias = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="4h_t")
    s4_h = st.number_input("Swing High", value=0.0, format="%.2f", key="s4h")
    s4_l = st.number_input("Swing Low", value=0.0, format="%.2f", key="s4l")

with c1h:
    st.subheader("⏱️ 1H STRUC")
    itf_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="1h_t")
    s1_h = st.number_input("1H High", value=0.0, format="%.2f", key="s1h")
    s1_l = st.number_input("1H Low", value=0.0, format="%.2f", key="s1l")

with c30m:
    st.subheader("⚡ 30M SHIFT")
    t30_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="30m_t")
    s30_h = st.number_input("30M High", value=0.0, format="%.2f", key="s30h")
    s30_l = st.number_input("30M Low", value=0.0, format="%.2f", key="s30l")

with c15m:
    st.subheader("🎯 15M ENTRY")
    t15_trend = st.radio("Trend", ["Select...", "Bullish ⬆️", "Bearish ⬇️", "Ranging"], key="15m_t")
    s15_h = st.number_input("15M High", value=0.0, format="%.2f", key="s15h")
    s15_l = st.number_input("15M Low", value=0.0, format="%.2f", key="s15l")

# ---------------- 6. STRATEGY NOTES ---------------- #
st.markdown("---")
st.subheader("📝 POST-SHOCK EXECUTION PLAN")
# This text area holds your narrative plan
st.session_state.trade_notes = st.text_area(
    "Paste Strategic Setup Here:", 
    value=st.session_state.trade_notes, 
    height=250,
    placeholder="Describe Shark behavior, Traps, and your Checklist here..."
)

# ---------------- 7. PHASE 2 & 3: EXECUTION ---------------- #
st.markdown("---")
c_poi, c_exec = st.columns([1, 2])

with c_poi:
    st.header("📋 PHASE 2: POI")
    poi_type = st.selectbox("Trading Zone", ["Select...", "Swing High", "Swing Low", "Supply Zone", "Demand Zone", "Order Block", "FVG"])
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f")
    trade_dir = st.radio("Position Direction", ["Select...", "LONG 🔵", "SHORT 🔴"], horizontal=True)

with c_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    # Dynamic Pip Factor
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    sl_dist_pips = 20
    
    # Auto-calculate SL based on direction
    calc_sl = 0.0
    if zone_price > 0 and trade_dir != "Select...":
        calc_sl = zone_price - (sl_dist_pips * pip_factor) if trade_dir == "LONG 🔵" else zone_price + (sl_dist_pips * pip_factor)
    
    sl_val = st.number_input(f"Stop Loss ({sl_dist_pips} Pips)", value=calc_sl, format="%.2f")
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f")
    
    if entry_val > 0 and sl_val > 0 and trade_dir != "Select...":
        actual_pips = abs(entry_val - sl_val) / pip_factor
        lot_size = (current_risk_usd / actual_pips) / 10 if actual_pips > 0 else 0
        tp1 = entry_val + (actual_pips * 2 * pip_factor) if trade_dir == "LONG 🔵" else entry_val - (actual_pips * 2 * pip_factor)
        
        st.metric("Recommended Lot Size", f"{round(lot_size, 2)}")
        st.success(f"TP1 Target: {round(tp1, 2)} | Total Risk: ${round(current_risk_usd, 2)}")

        if st.button("💾 SAVE TRADE DETAILS", use_container_width=True):
            trade_data = {
                "Time": dt_string,
                "Asset": symbol,
                "Dir": trade_dir,
                "4H (H/L)": f"{s4_h}/{s4_l}",
                "1H (H/L)": f"{s1_h}/{s1_l}",
                "30M (H/L)": f"{s30_h}/{s30_l}",
                "15M (H/L)": f"{s15_h}/{s15_l}",
                "POI": f"{poi_type} @ {zone_price}",
                "Lots": round(lot_size, 2),
                "Entry": entry_val,
                "TP1/BE": f"{round(tp1, 2)} / {entry_val}",
                "Plan": st.session_state.trade_notes # Full text saved here
            }
            st.session_state.trade_history.append(trade_data)
            st.toast("Trade Secured and Logged!")

# ---------------- 8. 📊 SESSION LOG (FORMATTED FOR WORD) ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log")

if st.session_state.trade_history:
    df_full = pd.DataFrame(st.session_state.trade_history)
    
    # DISPLAY PART A: Clean Technical Table
    st.subheader("📈 Technical Data Table")
    # We drop 'Plan' here so the table stays perfectly aligned and compact
    df_technical = df_full.drop(columns=["Plan"])
    st.dataframe(df_technical, use_container_width=True)
    
    # DISPLAY PART B: Execution Plans as Text
    st.subheader("📝 Detailed Execution Plans")
    for i, trade in enumerate(st.session_state.trade_history):
        with st.container():
            st.markdown(f"### Trade #{i+1} Plan: {trade['Asset']} ({trade['Dir']})")
            # Using st.text or st.write to display the plan outside the table
            st.markdown(trade["Plan"]) 
            st.markdown("---") # Visual separator
    
    # DOWNLOAD SECTION
    c_del1, c_del2, c_dl = st.columns([1, 1, 2])
    with c_del1:
        if st.button("🗑️ DELETE LAST", use_container_width=True):
            st.session_state.trade_history.pop()
            st.rerun()
    with c_del2:
        if st.button("🧨 CLEAR ALL", use_container_width=True):
            st.session_state.trade_history = []
            st.rerun()
    with c_dl:
        # Full CSV for your backup (includes Plan column)
        csv = df_full.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 DOWNLOAD FULL CSV",
            data=csv,
            file_name=f"Trade_Log_{now.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    st.info("No trades saved yet. Complete Phase 3 to see the log.")
