import streamlit as st

# Setup & Branding
st.set_page_config(page_title="BlackArrowFX | SMC Execution", layout="wide")

st.title("🏹 BlackArrowFX: SMC Execution Engine")
st.caption("Precision-Based Smart Money Execution | Axi Select Standard")
st.markdown("---")

# --- SIDEBAR: ACCOUNT & RISK ---
with st.sidebar:
    st.header("💰 Risk Management")
    balance = st.number_input("Account Balance ($)", value=2146.11)
    
    # New: Daily Stop Circuit Breaker
    daily_loss_count = st.number_input("Losses Today", min_value=0, step=1, value=0)
    if daily_loss_count >= 2:
        st.error("🛑 DAILY STOP REACHED: Terminal Closed. See you tomorrow!")
        st.stop()
    
    risk_pct = st.slider("Risk per Trade (%)", 0.25, 1.0, 1.0, step=0.25)
    risk_usd = balance * (risk_pct / 100)
    st.info(f"Risk per Trade: ${round(risk_usd, 2)}")

    st.header("⚙️ Execution Method")
    method = st.selectbox("Strategy Edge", 
                        ["Trend Following (Continuation)", 
                         "Pullback (Mean Reversion)", 
                         "Reversal (Counter Trend)"])
    
    # New: News Filter
    st.header("🌍 Macro Filter")
    news_checked = st.toggle("High-Impact News Checked? (Red Folder)")
    if not news_checked:
        st.warning("Check ForexFactory before executing!")

# --- PHASE 1: THE ANCHOR (HTF) ---
st.header("Phase 1: The Major Box (H4/H1)")
a1, a2, a3 = st.columns(3)

with a1:
    htf_bias = st.radio("Major Structure", ["Uptrend (HH/HL) 📈", "Downtrend (LL/LH) 📉", "Ranging ↔️"])
with a2:
    market_cond = st.radio("Market Condition", ["Established Trend", "High Volatility", "Trend Exhaustion"])
with a3:
    st.write("**Box Alignment Check**")
    major_check = st.checkbox("H4/H1 Trend Identified")
    middle_check = st.checkbox("M30/M15 Path Clear (No Obstacles)")

# --- PHASE 2: THE TRIGGER (M5) ---
st.header("Phase 2: The Minor Box (M5 Execution)")
col_structure, col_confluence = st.columns(2)

with col_structure:
    st.subheader("Swing Point Mapping")
    points = st.multiselect("M5 Points Identifed", ["HH", "HL", "LH", "LL"])
    mss = st.toggle("MSS / ChoCh (The Shift) ⚡")

with col_confluence:
    st.subheader("SMC Checklist")
    purge = st.toggle("Liquidity Purge (The Anchor) 💧")
    fvg = st.checkbox("FVG / Imbalance Created?")
    ob_valid = st.checkbox("OB Validation (BOS + Extreme Zone)")

# --- PHASE 3: CALCULATE & EXECUTE ---
st.markdown("---")
st.header("Phase 3: Risk & Position Sizing")
calc1, calc2, calc3 = st.columns(3)

with calc1:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    structural_sl = st.number_input("Structural SL (Anchor Point)", value=0.0, format="%.2f")

with calc2:
    # Gold 15-pip buffer (1.50 points)
    buffer_val = 1.50
    
    if entry != 0 and structural_sl != 0:
        # Automated SL adjustment based on Bias
        if "Uptrend" in htf_bias:
            final_sl = structural_sl - buffer_val
        else:
            final_sl = structural_sl + buffer_val
            
        pips_dist = abs(entry - final_sl) * 10 # Convert to Gold pips
        # Lot sizing for Gold: Risk / (Pips * Pip Value)
        lots = risk_usd / (pips_dist * 10) if pips_dist > 0 else 0
        
        st.metric("Suggested Lot Size", f"{round(lots, 2)} Lots")
        st.write(f"**Final SL (with +15pips):** {round(final_sl, 2)}")
        st.caption(f"Risking: {round(pips_dist, 1)} Pips")

with calc3:
    if entry != 0 and structural_sl != 0:
        # Trade Management Targets
        tp_1 = entry + ((entry - final_sl) * 1)
        tp_2 = entry + ((entry - final_sl) * 2)
        
        st.write(f"**Target 1 (1:1 - Move to BE):** {round(tp_1, 2)}")
        st.write(f"**Target 2 (1:2 - Partial/Exit):** {round(tp_2, 2)}")

# --- FINAL VERDICT ---
st.markdown("---")
# Alignment check based on your Step 1 rule
no_trade_bias = htf_bias == "Ranging ↔️"
all_confluence = all([mss, purge, fvg, ob_valid, news_checked, major_check, middle_check])

if all_confluence and not no_trade_bias:
    st.balloons()
    st.success(f"🚀 SMC SETUP VALIDATED: Executing {method}")
    st.markdown(f"> **Final Confirmation:** H4 Trend matches M5 Shift. Risk is set to {risk_pct}%.")
elif no_trade_bias:
    st.error("🛑 NO TRADE: H4/H1 is Ranging. Wait for alignment.")
else:
    st.warning("⚠️ PATIENCE: Waiting for all Phase 1 & 2 criteria to align...")
