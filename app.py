import streamlit as st

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="BlackArrowFX Mechanical Engine", layout="wide")

st.title("🏹 BlackArrowFX: Mechanical Trading Engine")
st.caption("Rule-Based Execution | Zero Emotion | SMC Framework")
st.markdown("---")

# ---------------- SESSION STATE ---------------- #
if "loss_count" not in st.session_state:
    st.session_state.loss_count = 0

if "loss_amount" not in st.session_state:
    st.session_state.loss_amount = 0.0

if "win_count" not in st.session_state:
    st.session_state.win_count = 0

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.header("💰 Risk Management")

    balance = st.number_input("Account Balance ($)", value=2146.11)

    risk_pct = st.slider("Risk per Trade (%)", 0.25, 1.0, 1.0, step=0.25)
    risk_usd = balance * (risk_pct / 100)

    st.info(f"Risk per Trade: ${round(risk_usd,2)}")

    st.header("⏰ Session Filter")
    session = st.selectbox("Session", ["Asia", "London", "New York"])

    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News (30–60min)")

    st.markdown("---")
    st.header("📊 Trade Journal")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("❌ Record LOSS"):
            st.session_state.loss_count += 1
            st.session_state.loss_amount += risk_usd

    with col2:
        if st.button("✅ Record WIN"):
            st.session_state.win_count += 1

    st.write(f"Loss Count: {st.session_state.loss_count}")
    st.write(f"Loss Amount: ${round(st.session_state.loss_amount,2)}")
    st.write(f"Wins: {st.session_state.win_count}")

    if st.button("🔄 Reset Day"):
        st.session_state.loss_count = 0
        st.session_state.loss_amount = 0.0
        st.session_state.win_count = 0

# ---------------- HARD LIMIT ---------------- #
max_loss_pct = 3
max_loss_usd = balance * (max_loss_pct / 100)

if st.session_state.loss_count >= 2 or st.session_state.loss_amount >= max_loss_usd:
    st.error("🛑 DAILY LOSS LIMIT HIT — STOP TRADING")
    st.stop()

# ---------------- PHASE 0 ---------------- #
st.header("PHASE 0: HARD FILTER")

f1, f2 = st.columns(2)

with f1:
    session_ok = session in ["London", "New York"]
    st.checkbox("Valid Session (London/NY)", value=session_ok, disabled=True)

with f2:
    st.checkbox("No High Impact News", value=news_ok, disabled=True)

hard_filter = session_ok and news_ok

# ---------------- PHASE 1 ---------------- #
st.markdown("---")
st.header("PHASE 1: HTF BIAS (H1/H4)")

col1, col2 = st.columns(2)

with col1:
    trend = st.radio("Market Structure", ["Bullish", "Bearish", "Ranging"])

with col2:
    htf_confirm = st.checkbox("HTF Structure Confirmed")

bias_valid = trend != "Ranging" and htf_confirm

# ---------------- PHASE 2 ---------------- #
st.markdown("---")
st.header("PHASE 2: POI VALIDATION")

p1, p2, p3 = st.columns(3)

with p1:
    displacement = st.checkbox("Strong Displacement")

with p2:
    liquidity = st.checkbox("Liquidity Sweep")

with p3:
    bos = st.checkbox("Break of Structure (BOS)")

poi_valid = displacement and liquidity and bos

# ---------------- PHASE 3 ---------------- #
st.markdown("---")
st.header("PHASE 3: ENTRY TRIGGER (M5)")

t1, t2, t3 = st.columns(3)

with t1:
    mss = st.checkbox("MSS / CHoCH")

with t2:
    fvg = st.checkbox("FVG Present")

with t3:
    ob = st.checkbox("Valid Order Block")

trigger_valid = mss and fvg and ob

# ---------------- SCORING ---------------- #
score = 0

if bias_valid:
    score += 3
if poi_valid:
    score += 2
if liquidity:
    score += 2
if mss:
    score += 2
if fvg or ob:
    score += 1

# ---------------- GRADE ---------------- #
if score >= 8:
    grade = "A+ SETUP 🚀"
elif score >= 6:
    grade = "B SETUP ⚠️"
else:
    grade = "NO TRADE ❌"

# ---------------- DECISION ---------------- #
st.markdown("---")
st.header("FINAL DECISION ENGINE")

st.metric("Setup Score", score)
st.write(f"Trade Grade: **{grade}**")

if not hard_filter:
    st.error("❌ BLOCKED: Session or News invalid")

elif not bias_valid:
    st.error("❌ NO TRADE: HTF bias not clear")

elif not poi_valid:
    st.error("❌ NO TRADE: Weak POI")

elif not trigger_valid:
    st.warning("⚠️ WAIT: No entry confirmation")

elif score >= 8:
    st.success("🚀 EXECUTE TRADE")
    st.balloons()

elif score >= 6:
    st.warning("⚠️ Optional Trade")

else:
    st.error("❌ NO TRADE")

# ---------------- POSITION CALCULATOR ---------------- #
st.markdown("---")
st.header("POSITION EXECUTION")

c1, c2, c3 = st.columns(3)

with c1:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    sl_input = st.number_input("Structural SL", value=0.0, format="%.2f")

with c2:
    if entry > 0 and sl_input > 0:
        buffer = 1.5

        if trend == "Bullish":
            final_sl = sl_input - buffer
        else:
            final_sl = sl_input + buffer

        pip_dist = abs(entry - final_sl) * 10
        lot = risk_usd / (pip_dist * 10) if pip_dist > 0 else 0

        st.metric("Lot Size", f"{round(lot,2)}")
        st.write(f"Final SL: {round(final_sl,2)}")
        st.caption(f"SL Distance: {round(pip_dist,1)} pips")

with c3:
    if entry > 0 and sl_input > 0:
        tp1 = entry + ((entry - final_sl) * 1.5)
        tp2 = entry + ((entry - final_sl) * 3)

        st.write(f"TP1 (1.5R): {round(tp1,2)}")
        st.write(f"TP2 (3R): {round(tp2,2)}")
