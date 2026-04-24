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
    
    daily_loss_count = st.number_input("Losses Today", min_value=0, step=1, value=0)
    if daily_loss_count >= 2:
        st.error("🛑 DAILY STOP REACHED: Terminal Closed.")
        st.stop()
    
    risk_pct = st.slider("Risk per Trade (%)", 0.25, 1.0, 1.0, step=0.25)
    risk_usd = balance * (risk_pct / 100)
    st.info(f"Risk per Trade: ${round(risk_usd, 2)}")

    st.header("⚙️ Execution Method")
    method = st.selectbox("Strategy Edge", 
                        ["Trend Following (Continuation)", 
                         "Pullback (Mean Reversion)", 
                         "Reversal (Counter Trend)"])
    
    st.header("🌍 Macro Filter")
    news_checked = st.toggle("High-Impact News Checked?")
    if not news_checked:
        st.warning("Check ForexFactory first!")

# --- PHASE 1: MAJOR STRUCTURE (H4/H1) ---
st.header("Phase 1: Major Structural Box (The Anchor)")
m_col1, m_col2 = st.columns(2)

with m_col1:
    major_trend = st.radio("Major Trend Direction", ["Bullish (HH/HL) 📈", "Bearish (LH/LL) 📉", "Ranging ↔️"])
    
with m_col2:
    st.subheader("Major Swing Points")
    major_swing = st.multiselect("Confirm Major Points", 
                                ["Major HH (Broken)", "Major HL (Protected)", 
                                 "Major LL (Broken)", "Major LH (Protected)"])
    major_aligned = st.checkbox("HTF Trend Identified & Confirmed")

# --- PHASE 2: MINOR STRUCTURE (M5) ---
st.header("Phase 2: Minor Structural Box (The Trigger)")

l_col1, l_col2 = st.columns(2)

with l_col1:
    st.subheader("Internal Swing Mapping")
    minor_points = st.multiselect("M5 Internal Points", ["Minor HH", "Minor HL", "Minor LH", "Minor LL"])
    mss = st.toggle("MSS / ChoCh (Trend Flip) ⚡")

with l_col2:
    st.subheader("SMC Confluence")
    purge = st.toggle("Liquidity Purge (Sweep) 💧")
    fvg = st.checkbox("FVG / Imbalance Created?")
    ob_valid = st.checkbox("OB Validation (BOS + Extreme)")

# --- PHASE 3: POSITION CALCULATOR ---
st.markdown("---")
st.header("Phase 3: Execution & Safety")
calc1, calc2, calc3 = st.columns(3)

with calc1:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    # Rule: This is usually the most recent MINOR swing point
    structural_sl = st.number_input("Structural SL (Minor HL/LH)", value=0.0, format="%.2f")

with calc2:
    buffer_val = 1.50 # +15 Pips for Gold
    
    if entry != 0 and structural_sl != 0:
        if "Bullish" in major_trend:
            final_sl = structural_sl - buffer_val
        else:
            final_sl = structural_sl + buffer_val
            
        pips_dist = abs(entry - final_sl) * 10
        lots = risk_usd / (pips_dist * 10) if pips_dist > 0 else 0
        
        st.metric("Suggested Lot Size", f"{round(lots, 2)} Lots")
        st.write(f"**Final SL Price:** {round(final_sl, 2)}")
        st.caption(f"SL Distance: {round(pips_dist, 1)} pips")

with calc3:
    if entry != 0 and structural_sl != 0:
        tp_be = entry + ((entry - final_sl) * 1.5) # 1.5 RR for BE
        tp_final = entry + ((entry - final_sl) * 3) # 1:3 RR Target
        
        st.write(f"**Breakeven Target (1.5R):** {round(tp_be, 2)}")
        st.write(f"**Final Target (1:3R):** {round(tp_final, 2)}")

# --- FINAL VERDICT ---
st.markdown("---")
# Logic: Must have Major Alignment + Minor Trigger
alignment_ok = major_aligned and major_trend != "Ranging ↔️"
trigger_ok = mss and purge and fvg and ob_valid

if alignment_ok and trigger_ok and news_checked:
    st.balloons()
    st.success(f"🚀 BLACKARROW EXECUTION: {method} Protocol Active")
    st.info("Checklist: Major Trend confirmed + Minor MSS detected. Risk is locked.")
elif major_trend == "Ranging ↔️":
    st.error("🛑 NO TRADE: Market is Ranging. Wait for a Major Swing break.")
else:
    st.warning("⚠️ WAITING: Ensure Major Alignment and Minor Trigger are both confirmed.")
