import streamlit as st

# Setup & Branding
st.set_page_config(page_title="BlackArrowFX | SMC Execution", layout="wide")

st.title("🏹 BlackArrowFX: SMC Execution Engine")
st.markdown("---")

# --- SIDEBAR: ACCOUNT & RISK ---
with st.sidebar:
    st.header("💰 Risk Management")
    balance = st.number_input("Account Balance ($)", value=2146.11)
    risk_pct = 1.0 # Fixed at 1% per your plan
    st.info(f"Risk per Trade: {risk_pct}% (${round(balance * (risk_pct/100), 2)})")
    
    st.header("📊 Strategy Params")
    st.write("**Management:** SL to BE at 1:2 RR")
    st.write("**Asset:** XAUUSD / GOLD")

# --- PHASE 1: HTF FRAMEWORK ---
st.header("Phase 1: 4H HTF Framework")
col_bias, col_poi = st.columns(2)

with col_bias:
    bias = st.radio("Analyze 4H Bias", ["Bullish 🟢", "Bearish 🔴", "Neutral ⚪"])
with col_poi:
    poi_type = st.multiselect("HTF Point of Interest (POI)", 
                               ["Major High/Low", "4H Order Block", "4H Imbalance"])

# --- PHASE 2: LTF REFINEMENT (15M/5M) ---
st.header("Phase 2: LTF Refinement & Entry")
col_liquidity, col_structure = st.columns(2)

with col_liquidity:
    st.subheader("The Purge")
    purge = st.toggle("Liquidity Purged within POI? 💧")
    
with col_structure:
    st.subheader("The Shift")
    mss = st.toggle("Market Structure Shift (Impulsive) ⚡")
    fvg_created = st.checkbox("Clear Imbalance Created?")

# --- PHASE 3: THE ORDER BLOCK CHECKLIST ---
st.subheader("Phase 3: The Entry OB Validation")
c1, c2, c3 = st.columns(3)
ob_bos = c1.checkbox("OB caused the BOS/MSS")
ob_extreme = c2.checkbox("OB is in the Extreme Zone")
ob_imbalance = c3.checkbox("OB created Imbalance")

# --- POSITION CALCULATOR ---
st.markdown("---")
st.header("Phase 4: Calculate & Execute")
calc_col1, calc_col2 = st.columns(2)

with calc_col1:
    entry = st.number_input("Entry Price", value=0.00, format="%.2f")
    sl = st.number_input("Stop Loss", value=0.00, format="%.2f")

with calc_col2:
    if entry != sl:
        risk_usd = balance * (risk_pct / 100)
        pips = abs(entry - sl)
        lots = risk_usd / (pips * 100)
        
        st.metric("Suggested Lot Size", f"{round(lots, 2)} Lots")
        tp_target = entry + ((entry - sl) * 2) if bias == "Bullish 🟢" else entry - ((sl - entry) * 2)
        st.write(f"**Breakeven Target (1:2 RR):** {round(tp_target, 2)}")

# --- FINAL VERDICT ---
all_confluence = all([purge, mss, fvg_created, ob_bos, ob_extreme, ob_imbalance])

if all_confluence and bias != "Neutral ⚪":
    st.balloons()
    st.success("🚀 SMC SETUP VALIDATED: SHARK SIGNATURE DETECTED!")
else:
    st.warning("⚠️ PATIENCE: Waiting for all SMC criteria to align...")
