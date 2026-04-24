import streamlit as st

st.set_page_config(page_title="BlackArrowFX PRO", layout="wide")

st.title("🏹 BlackArrowFX: SMC Execution Engine PRO")
st.caption("Institutional Logic | Precision Execution")
st.markdown("---")

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.header("💰 Risk Management")
    balance = st.number_input("Account Balance ($)", value=2146.11)

    daily_loss_count = st.number_input("Losses Today", min_value=0, step=1, value=0)
    if daily_loss_count >= 2:
        st.error("🛑 DAILY STOP HIT")
        st.stop()

    risk_pct = st.slider("Risk %", 0.25, 1.0, 1.0, step=0.25)
    risk_usd = balance * (risk_pct / 100)
    st.info(f"Risk: ${round(risk_usd, 2)}")

    st.header("⏰ Session Filter")
    session = st.selectbox("Trading Session", ["Asia", "London", "New York"])

    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News?")

# ---------------- PHASE 1 ---------------- #
st.header("Phase 1: HTF Bias")

col1, col2 = st.columns(2)

with col1:
    trend = st.radio("Trend", ["Bullish", "Bearish", "Ranging"])

with col2:
    htf_confirm = st.checkbox("HTF Structure Confirmed")

# ---------------- PHASE 2 ---------------- #
st.header("Phase 2: LTF Confirmation")

c1, c2 = st.columns(2)

with c1:
    mss = st.checkbox("MSS / CHoCH")
    sweep = st.checkbox("Liquidity Sweep")

with c2:
    ob = st.checkbox("Valid Order Block")
    fvg = st.checkbox("FVG Present")

# ---------------- SCORING ENGINE ---------------- #
score = 0

if trend != "Ranging" and htf_confirm:
    score += 3

if mss:
    score += 2

if sweep:
    score += 2

if ob:
    score += 2

if fvg:
    score += 1

# ---------------- TRADE GRADE ---------------- #
if score >= 8:
    grade = "A+ SETUP 🚀"
elif score >= 6:
    grade = "B SETUP ⚠️"
else:
    grade = "NO TRADE ❌"

# ---------------- SESSION FILTER ---------------- #
session_ok = session in ["London", "New York"]

# ---------------- FINAL LOGIC ---------------- #
st.markdown("---")
st.header("Execution Decision")

st.metric("Setup Score", score)
st.write(f"Trade Grade: **{grade}**")

if trend == "Ranging":
    st.error("Market is ranging — NO TRADE")

elif not session_ok:
    st.warning("Avoid Asia session for Gold")

elif not news_ok:
    st.warning("High impact news risk")

elif score >= 8:
    st.success("EXECUTE TRADE")
    st.balloons()

elif score >= 6:
    st.warning("Optional Trade — Lower Confidence")

else:
    st.error("NO TRADE — Conditions not met")

# ---------------- POSITION CALC ---------------- #
st.markdown("---")
st.header("Position Calculator")

entry = st.number_input("Entry", value=0.0)
sl = st.number_input("SL", value=0.0)

if entry > 0 and sl > 0:
    pip_dist = abs(entry - sl) * 10
    lot = risk_usd / (pip_dist * 10) if pip_dist > 0 else 0

    tp1 = entry + (entry - sl) * 1.5
    tp2 = entry + (entry - sl) * 3

    st.write(f"Lot Size: {round(lot,2)}")
    st.write(f"TP1 (1.5R): {round(tp1,2)}")
    st.write(f"TP2 (3R): {round(tp2,2)}")
