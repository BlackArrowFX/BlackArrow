import streamlit as st

# Setup & BlackArrow Branding
st.set_page_config(page_title="BlackArrowFX Multi-Engine", layout="wide")

st.title("🏹 BlackArrowFX: Tiered Execution Engine")

# --- STEP 1: SELECT YOUR WARRIOR CLASS ---
st.header("Step 1: Choose Your Setup Tier")
setup_type = st.selectbox("Trading Style", ["Day Scalper", "Day Trader", "Swing Trader"])

st.markdown("---")

# --- STEP 2: DYNAMIC LOGIC BASED ON TIER ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"🛠 {setup_type} Checklist")
    
    if setup_type == "Day Scalper":
        # Scalper needs micro-confluence
        c1 = st.checkbox("1m Liquidity Sweep")
        c2 = st.checkbox("Footprint: Zero Print at Wick")
        c3 = st.checkbox("Footprint: Delta Flip (Aggressive)")
        c4 = st.checkbox("Session: London/NY Open")
        logic_gate = all([c1, c2, c3, c4])
        risk_default = 0.5

    elif setup_type == "Day Trader":
        # Day Trader needs structural alignment
        c1 = st.checkbox("H1 Trend Alignment")
        c2 = st.checkbox("15m CHoCH (Change of Character)")
        c3 = st.checkbox("Price Tapped 15m FVG/OB")
        c4 = st.checkbox("Premium/Discount Zone Validation")
        logic_gate = all([c1, c2, c3, c4])
        risk_default = 1.0

    else: # Swing Trader
        # Swing Trader needs high-timeframe confirmation
        c1 = st.checkbox("Daily Market Structure Break (BOS)")
        c2 = st.checkbox("H4 POI (Point of Interest) Tap")
        c3 = st.checkbox("Weekly Bias Alignment")
        c4 = st.checkbox("Macro Economic Driver (News/DXY)")
        logic_gate = all([c1, c2, c3, c4])
        risk_default = 2.0

with col2:
    st.subheader("💰 Risk Manager")
    balance = st.number_input("Account Balance ($)", value=2146.11)
    risk_pct = st.slider("Risk %", 0.1, 5.0, risk_default)
    entry = st.number_input("Entry Price", format="%.2f")
    sl = st.number_input("Stop Loss", format="%.2f")

    # Math Engine
    if entry != sl:
        risk_usd = balance * (risk_pct / 100)
        pips = abs(entry - sl)
        lots = risk_usd / (pips * 100) # Gold Standard
        st.metric("Calculated Lot Size", f"{round(lots, 2)} Lots")
        st.metric("Risk in Dollars", f"${round(risk_usd, 2)}")

# --- STEP 3: THE VERDICT ---
st.markdown("---")
if logic_gate:
    st.balloons()
    st.success(f"🔥 {setup_type.upper()} SETUP VALIDATED: EXECUTE WITH DISCIPLINE")
else:
    st.warning(f"🛑 SETUP INCOMPLETE: Waiting for {setup_type} confluence...")

# Sidebar Info
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2533/2533503.png", width=100)
st.sidebar.write(f"**Mode:** {setup_type}")
st.sidebar.write("**Asset:** XAUUSD")
