import streamlit as st
import re
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

st.title("🏹 BlackArrowFX: Triple-Timeframe Execution Engine")
st.caption(f"Current Server Time: {dt_string}")
st.markdown("---")

# ---------------- SESSION STATE INITIALIZATION ---------------- #
if "balance" not in st.session_state: st.session_state.balance = 2146.11
if "trade_count" not in st.session_state: st.session_state.trade_count = 0
if "daily_loss_total" not in st.session_state: st.session_state.daily_loss_total = 0.0

tfs = ["4H", "1H", "5M"]
for tf in tfs:
    if f"{tf}_bias" not in st.session_state: st.session_state[f"{tf}_bias"] = "Bullish ⬆️"
    if f"{tf}_high" not in st.session_state: st.session_state[f"{tf}_high"] = 0.0
    if f"{tf}_low" not in st.session_state: st.session_state[f"{tf}_low"] = 0.0

# ---------------- SIDEBAR: RISK & JOURNAL ---------------- #
with st.sidebar:
    st.header("💰 Risk Engine")
    st.metric("Current Balance", f"${round(st.session_state.balance, 2)}")
    
    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)

    max_daily_risk = st.session_state.balance * 0.10
    st.info(f"Active Risk: ${round(current_risk_usd, 2)}")
    
    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News", value=True)

    st.markdown("---")
    st.header("📊 Daily Journal")
    st.write(f"Trades Taken: **{st.session_state.trade_count} / 3**")
    
    col_l, col_w = st.columns(2)
    if col_l.button("❌ LOSS", use_container_width=True):
        st.session_state.balance -= current_risk_usd
        st.session_state.daily_loss_total += current_risk_usd
        st.session_state.trade_count += 1
        st.rerun()

    if col_w.button("✅ WIN", use_container_width=True):
        st.session_state.balance += (current_risk_usd * 2) # Default 2R
        st.session_state.trade_count += 1
        st.rerun()

# ---------------- PHASE 0: FILTERS ---------------- #
if st.session_state.trade_count >= 3 or st.session_state.daily_loss_total >= max_daily_risk:
    st.error("🛑 TRADING LOCKED: Daily limits reached.")
    st.stop()

# ---------------- TRIPLE TIMEFRAME ANALYSIS ---------------- #
st.markdown("### 📊 Structural Alignment")
c4h, c1h, c5m = st.columns(3)
phase_ready = {"4H": False, "1H": False, "5M": False}
columns = {"4H": c4h, "1H": c1h, "5M": c5m}

for tf in tfs:
    with columns[tf]:
        st.subheader(f"{tf} Analysis")
        bias = st.session_state[f"{tf}_bias"]
        st.info(f"Bias: **{bias}**")
        
        # Display/Input current swings
        st.session_state[f"{tf}_high"] = st.number_input(f"High", value=st.session_state[f"{tf}_high"], format="%.2f", key=f"h_{tf}")
        st.session_state[f"{tf}_low"] = st.number_input(f"Low", value=st.session_state[f"{tf}_low"], format="%.2f", key=f"l_{tf}")

        is_conf = st.checkbox("Confirmed Break?", key=f"conf_{tf}")
        if is_conf:
            options = ["BOS (High)", "MSS (Low)"] if "Bullish" in bias else ["BOS (Low)", "MSS (High)"]
            choice = st.radio("Structure:", options, key=f"ch_{tf}", horizontal=True)
            new_val = st.number_input("Break Price", format="%.2f", key=f"v_{tf}")
            
            if st.button(f"Update {tf}", key=f"btn_{tf}", use_container_width=True):
                if "BOS" in choice:
                    if "High" in choice: st.session_state[f"{tf}_high"] = new_val
                    else: st.session_state[f"{tf}_low"] = new_val
                else: # MSS Logic
                    st.session_state[f"{tf}_bias"] = "Bearish ⬇️" if "Bullish" in bias else "Bullish ⬆️"
                    if "High" in choice: st.session_state[f"{tf}_high"] = new_val
                    else: st.session_state[f"{tf}_low"] = new_val
                st.rerun()
            
            if new_val > 0: phase_ready[tf] = True

# ---------------- POI & EXECUTION ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 POI Zone")
    raw_text = st.text_area("1H POI (Price Range)", height=80, placeholder="Example: 2340.50 - 2345.00")
    inside_zone = False
    if raw_text:
        match = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", raw_text)
        if match:
            low, high = sorted([float(match.group(1)), float(match.group(2))])
            curr_price = st.number_input("Market Price", value=0.0, format="%.2f")
            if low <= curr_price <= high:
                st.success("✅ Price at POI")
                inside_zone = True
            else: st.error("❌ Price Outside POI")

with col_exec:
    st.header("🚀 Execution Engine")
    e_col, s_col = st.columns(2)
    entry = e_col.number_input("Entry Price", value=0.0, format="%.2f")
    sl = s_col.number_input("Stop Loss", value=0.0, format="%.2f")
    
    if entry > 0 and sl > 0:
        pips = abs(entry - sl) * 10
        lot = current_risk_usd / (pips * 10) if pips > 0 else 0
        
        st.metric("Required Lot Size", f"{round(lot, 2)} Lots")
        
        # Confluence Check
        if all(phase_ready.values()) and inside_zone and news_ok:
            st.success("🔥 TRADE CONFIRMED: BIAS + STRUCTURE + POI ALIGNED")
        else:
            st.warning("⚠️ CONFLUENCE MISSING: Ensure all TFs are confirmed and price is at POI.")

        # TP Targets
        diff = abs(entry - sl)
        is_buy = entry > sl
        tp1 = round(entry + (diff * 1.5 if is_buy else -diff * 1.5), 2)
        tp2 = round(entry + (diff * 3.0 if is_buy else -diff * 3.0), 2)
        
        st.markdown(f"""
        | Target | Price | Reward |
        | :--- | :--- | :--- |
        | **TP1 (1.5R)** | `{tp1}` | `${round(current_risk_usd * 1.5, 2)}` |
        | **TP2 (3.0R)** | `{tp2}` | `${round(current_risk_usd * 3.0, 2)}` |
        """)
