import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- 1. INITIALIZE GLOBAL STATE ---------------- #
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
    st.header("📊 Daily Journal")
    st.write(f"Trades Taken: **{st.session_state.trades_taken} / 3**")
    
    if st.button("❌ RECORD LOSS", use_container_width=True):
        st.session_state.balance -= current_risk_usd 
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
    s4_h = st.number_input("Swing High", value=0.0, format="%.2f", key="s4h")
    s4_l = st.number_input("Swing Low", value=0.0, format="%.2f", key="s4l")

with c1h:
    st.subheader("⏱️ 1H STRUC")
    s1_h = st.number_input("1H High", value=0.0, format="%.2f", key="s1h")
    s1_l = st.number_input("1H Low", value=0.0, format="%.2f", key="s1l")

with c30m:
    st.subheader("⚡ 30M SHIFT")
    s30_h = st.number_input("30M High", value=0.0, format="%.2f", key="s30h")
    s30_l = st.number_input("30M Low", value=0.0, format="%.2f", key="s30l")

with c15m:
    st.subheader("🎯 15M ENTRY")
    s15_h = st.number_input("15M High", value=0.0, format="%.2f", key="s15h")
    s15_l = st.number_input("15M Low", value=0.0, format="%.2f", key="s15l")

# ---------------- 6. STRATEGY NOTES (THE PLAN) ---------------- #
st.markdown("---")
st.subheader("📝 POST-SHOCK EXECUTION PLAN")
st.session_state.trade_notes = st.text_area(
    "Paste Strategic Setup Here:", 
    value=st.session_state.trade_notes, 
    height=200
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
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    sl_dist_pips = 20
    
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
                "Plan": st.session_state.trade_notes 
            }
            st.session_state.trade_history.append(trade_data)
            st.toast("Trade Secured!")

# ---------------- 8. 📊 SESSION LOG (FORMATTED FOR WORD) ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log")

if st.session_state.trade_history:
    df_full = pd.DataFrame(st.session_state.trade_history)
    
    # --- TECHNICAL DATA TABLE ---
    # We use st.table here because it formats much cleaner for copying to Word
    st.subheader("📈 Technical Data Table")
    df_technical = df_full.drop(columns=["Plan"])
    st.table(df_technical)
    
    # --- PLAN TEXT SECTION ---
    # Display the plan as plain text/markdown below the table
    st.subheader("📝 Execution Plans")
    for i, trade in enumerate(st.session_state.trade_history):
        st.markdown(f"**Plan for Trade #{i+1} ({trade['Asset']})**")
        st.text(trade["Plan"]) # Use st.text to keep raw formatting
        st.markdown("---")
    
    # --- CLEAN DOWNLOAD ---
    c1, c2 = st.columns(2)
    with c1:
        # Technical-only CSV (No messy Plan column)
        csv_clean = df_technical.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 DOWNLOAD CLEAN TABLE (CSV)",
            data=csv_clean,
            file_name=f"Technical_Log_{now.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c2:
        if st.button("🧨 CLEAR ALL LOGS", use_container_width=True):
            st.session_state.trade_history = []
            st.rerun()
else:
    st.info("No trades saved yet. Log a trade in Phase 3 to see the data.")
