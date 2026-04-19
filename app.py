import streamlit as st

# App Config
st.set_page_config(page_title="BlackArrowFX Confluence Pro", page_icon="🏹")

st.title("🏹 BlackArrowFX Confluence Pro")
st.markdown("---")

# 1. SMC Context
st.subheader("Step 1: SMC Context")
col1, col2 = st.columns(2)

with col1:
    zone = st.selectbox("Current Zone", ["None", "1m Bullish OB", "1m Bearish OB", "Liquidity Sweep", "FVG Tap"])
with col2:
    bias = st.toggle("HTF Bias Alignment ✅")

# 2. Order Flow Section (The Shark Signature)
st.subheader("Step 2: Footprint Confirmation")
c1, c2, c3 = st.columns(3)

with c1:
    zero_print = st.checkbox("Zero Print")
with c2:
    imbalance = st.checkbox("Stacked Imbalance")
with c3:
    poc_flip = st.checkbox("Delta Flip / POC")

# 3. Risk Calculator
st.subheader("Step 3: Risk & Lot Size")
col_e, col_sl, col_r = st.columns(3)

with col_e:
    entry = st.number_input("Entry Price", value=4835.50, step=0.10)
with col_sl:
    sl = st.number_input("Stop Loss", value=4832.00, step=0.10)
with col_r:
    risk_usd = st.number_input("Risk ($)", value=50)

# Lot Size Logic
if entry != sl:
    points = abs(entry - sl)
    # For Gold (XAUUSD): 1.00 move with 1.00 lot = $100. 
    # Therefore, Lots = Risk / (Points * 100)
    lots = risk_usd / (points * 100)
    
    st.info(f"**Calculated Lot Size:** {round(lots, 2)} Lots")
else:
    st.warning("Entry and SL cannot be the same.")

# 4. Final Verdict Logic
st.markdown("---")
confluence_met = all([zone != "None", bias, zero_print, imbalance, poc_flip])

if confluence_met:
    st.balloons()
    st.success("🚀 **SHARK SIGNATURE DETECTED: EXECUTE TRADE!**")
else:
    # Calculating progress
    checks = [zone != "None", bias, zero_print, imbalance, poc_flip]
    progress = sum(checks) / len(checks)
    st.progress(progress)
    st.warning("🔴 **SIGNAL: WAITING...** (System requires full confluence)")

# Footer Sidebar
st.sidebar.title("BlackArrowFX Settings")
st.sidebar.write("Asset: **XAUUSD (GOLD)**")
st.sidebar.write(f"Account Risk: {risk_usd}$")
