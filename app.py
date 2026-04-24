import streamlit as st

# Setup & Branding
st.set_page_config(page_title="BlackArrowFX | SMC Execution", layout="wide")

st.title("🏹 BlackArrowFX: SMC Execution Engine")
st.caption("Precision-Based Smart Money Execution | 2026 Edition")
st.markdown("---")

# --- SIDEBAR: ACCOUNT & RISK ---
with st.sidebar:
    st.header("💰 Risk Management")
    balance = st.number_input("Account Balance ($)", value=2146.11)
    risk_pct = 1.0 
    
    st.header("⚙️ Execution Method")
    method = st.selectbox("Strategy Edge", 
                        ["Trend Following (Continuation)", 
                         "Pullback (Mean Reversion)", 
                         "Reversal (Counter Trend)"])
    
    st.header("📊 Asset Specs")
    st.write("**Asset:** XAUUSD / GOLD")
    st.write("**Buffer:** +15 Pips (Built-in)")
    
    risk_usd = balance * (risk_pct / 100)
    st.info(f"Risk per Trade: ${round(risk_usd, 2)} (1.0%)")

# --- PHASE 1: THE ANCHOR (HTF) ---
st.header("Phase 1: The Anchor (HTF Framework)")
a1, a2, a3 = st.columns(3)

with a1:
    htf_bias = st.radio("Major Bias (H4/H1)", ["Uptrend 📈", "Downtrend 📉", "Ranging ↔️"])
with a2:
    market_cond = st.radio("Market Condition", ["High Volatility", "Established Trend", "Trend Exhaustion"])
with a3:
    st.write("**HTF Uploads Check**")
    st.checkbox("Major H1 & H4 Loaded")
    st.checkbox("Middle M30 & M15 Loaded")
    st.checkbox("Minor M5 Loaded")

# --- PHASE 2: LTF REFINEMENT (M5) ---
st.header("Phase 2: LTF Refinement & Swing Points")

col_structure, col_confluence = st.columns(2)

with col_structure:
    st.subheader("Swing Point Mapping (M5)")
    swing_points = st.multiselect("Identify Points", ["HH (Higher High)", "HL (Higher Low)", "LH (Lower High)", "LL (Lower Low)"])
    mss = st.toggle("MSS / ChoCh Detected (The Shift) ⚡")

with col_confluence:
    st.subheader("The Purge & Imbalance")
    purge = st.toggle("Liquidity Purged (The Anchor) 💧")
    fvg = st.checkbox("Fair Value Gap (FVG) Created?")
    ob_valid = st.checkbox("OB/POI Validation (BOS + Extreme)")

# --- PHASE 3: CALCULATE & EXECUTE ---
st.markdown("---")
st.header("Phase 3: Position Sizing")
calc1, calc2, calc3 = st.columns(3)

with calc1:
    entry = st.number_input("Entry Price", value=0.00, format="%.2f")
    structural_sl = st.number_input("Structural SL", value=0.00, format="%.2f")

with calc2:
    # Adding the 15 pip buffer as requested
    # Gold 1.00 pip = 0.10 price movement (e.g. 2000.00 to 2000.10)
    # 15 pips = 1.50 price points
    buffer_val = 1.50
    
    if entry != 0 and structural_sl != 0:
        if htf_bias == "Uptrend 📈":
            final_sl = structural_sl - buffer_val
        else:
            final_sl = structural_sl + buffer_val
            
        pips_dist = abs(entry - final_sl) * 10 # Converting price diff to Gold pips
        lots = risk_usd / (pips_dist * 10) if pips_dist > 0 else 0
        
        st.metric("Suggested Lot Size", f"{round(lots, 2)} Lots")
        st.caption(f"SL Distance (inc. buffer): {round(pips_dist, 1)} pips")

with calc3:
    if entry != 0 and structural_sl != 0:
        tp_2 = entry + ((entry - final_sl) * 2)
        tp_3 = entry + ((entry - final_sl) * 3)
        st.write(f"**BE Target (1:2):** {round(tp_2, 2)}")
        st.write(f"**Target (1:3):** {round(tp_3, 2)}")

# --- FINAL VERDICT ---
ready = all([mss, purge, fvg, ob_valid]) and htf_bias != "Ranging ↔️"

if ready:
    st.success(f"🚀 EDGE DETECTED: {method} Setup Validated.")
    st.balloons()
else:
    st.warning("⚠️ PATIENCE: Market Structure Alignment required.")
