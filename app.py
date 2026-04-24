import streamlit as st

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="BlackArrowFX Mechanical Engine", layout="wide")

st.title("🏹 BlackArrowFX: Mechanical Trading Engine")
st.caption("Rule-Based Execution | POI Confluence System | Zero Emotion")
st.markdown("---")

# ---------------- SESSION STATE ---------------- #
if "loss_count" not in st.session_state:
    st.session_state.loss_count = 0

if "loss_amount" not in st.session_state:
    st.session_state.loss_amount = 0.0

if "win_count" not in st.session_state:
    st.session_state.win_count = 0


# ---------------- POI LEDGER ---------------- #
POI_ZONES = {
    "Extreme Supply": (4710.00, 4712.50, "SWING SELL ONLY"),
    "Decisionary Supply": (4695.00, 4700.00, "CHoCH SELL ONLY"),
    "Bearish OB": (4685.00, 4688.00, "PRIMARY SELL ZONE"),
    "Internal Pivot": (4678.00, 4680.00, "SCALP ONLY"),
    "Demand Sweep": (4657.00, 4662.00, "HIGH RISK BUY ZONE")
}


def get_zone(price):
    for zone, (low, high, action) in POI_ZONES.items():
        if low <= price <= high:
            return zone, action
    return "No Man's Land", "NO TRADE"


# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.header("💰 Risk Engine")

    balance = st.number_input("Account Balance ($)", value=2146.11)

    risk_pct = st.slider("Risk per Trade (%)", 0.25, 1.0, 1.0, step=0.25)
    risk_usd = balance * (risk_pct / 100)

    st.info(f"Risk per Trade: ${round(risk_usd,2)}")

    st.header("⏰ Session Filter")
    session = st.selectbox("Session", ["Asia", "London", "New York"])

    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News")

    st.markdown("---")

    st.header("📊 Trade Journal")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("❌ LOSS"):
            st.session_state.loss_count += 1
            st.session_state.loss_amount += risk_usd

    with col2:
        if st.button("✅ WIN"):
            st.session_state.win_count += 1

    st.write(f"Losses: {st.session_state.loss_count}")
    st.write(f"Loss Amount: ${round(st.session_state.loss_amount,2)}")
    st.write(f"Wins: {st.session_state.win_count}")

    if st.button("🔄 RESET"):
        st.session_state.loss_count = 0
        st.session_state.loss_amount = 0.0
        st.session_state.win_count = 0


# ---------------- HARD LIMIT ---------------- #
max_loss_pct = 3
max_loss_usd = balance * (max_loss_pct / 100)

if st.session_state.loss_count >= 2 or st.session_state.loss_amount >= max_loss_usd:
    st.error("🛑 DAILY LOSS LIMIT HIT — STOP TRADING")
    st.stop()


# ---------------- PRICE INPUT ---------------- #
st.header("📍 LIVE POI ENGINE")

price = st.number_input("Current Gold Price (XAUUSD)", value=0.0, format="%.2f")

zone, action = get_zone(price)

st.metric("Detected Zone", zone)
st.write(f"Recommended Action: **{action}**")


# ---------------- PHASE 0 ---------------- #
st.markdown("---")
st.header("PHASE 0: HARD FILTER")

session_ok = session in ["London", "New York"]

col1, col2 = st.columns(2)

with col1:
    st.checkbox("Valid Session", value=session_ok, disabled=True)

with col2:
    st.checkbox("News Filter Active", value=news_ok, disabled=True)

hard_filter = session_ok and news_ok


# ---------------- PHASE 1 ---------------- #
st.markdown("---")
st.header("PHASE 1: HTF BIAS")

col1, col2 = st.columns(2)

with col1:
    trend = st.radio("Market Structure", ["Bullish", "Bearish", "Ranging"])

with col2:
    htf_confirm = st.checkbox("HTF Confirmed")

bias_valid = trend != "Ranging" and htf_confirm


# ---------------- PHASE 2 ---------------- #
st.markdown("---")
st.header("PHASE 2: POI CONFIRMATION")

displacement = st.checkbox("Displacement")
liquidity = st.checkbox("Liquidity Sweep")
bos = st.checkbox("Break of Structure")

poi_valid = displacement and liquidity and bos


# ---------------- PHASE 3 ---------------- #
st.markdown("---")
st.header("PHASE 3: ENTRY TRIGGER")

mss = st.checkbox("MSS / CHoCH")
fvg = st.checkbox("FVG")
ob = st.checkbox("Order Block Touch")

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

# Zone bonus
if zone != "No Man's Land":
    score += 1


# ---------------- GRADE ---------------- #
if score >= 9:
    grade = "A+ EXECUTION 🚀"
elif score >= 7:
    grade = "B SETUP ⚠️"
else:
    grade = "NO TRADE ❌"


# ---------------- FINAL ENGINE ---------------- #
st.markdown("---")
st.header("FINAL DECISION ENGINE")

st.metric("Setup Score", score)
st.write(f"Grade: **{grade}**")

if not hard_filter:
    st.error("BLOCKED: Session/News invalid")

elif zone == "No Man's Land":
    st.error("NO TRADE: Outside POI zones")

elif not bias_valid:
    st.error("NO TRADE: Weak HTF bias")

elif not poi_valid:
    st.error("NO TRADE: Weak POI structure")

elif not trigger_valid:
    st.warning("WAIT: No entry confirmation")

elif score >= 9:
    st.success("🚀 EXECUTE TRADE")

elif score >= 7:
    st.warning("⚠️ OPTIONAL TRADE")

else:
    st.error("NO TRADE")


# ---------------- POSITION CALCULATOR ---------------- #
st.markdown("---")
st.header("POSITION ENGINE")

c1, c2, c3 = st.columns(3)

with c1:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    sl = st.number_input("Stop Loss", value=0.0, format="%.2f")

with c2:
    if entry > 0 and sl > 0:
        pip_dist = abs(entry - sl) * 10
        lot = risk_usd / (pip_dist * 10) if pip_dist > 0 else 0

        st.metric("Lot Size", round(lot, 2))
        st.write(f"SL Distance: {round(pip_dist,1)} pips")

with c3:
    if entry > 0 and sl > 0:
        tp1 = entry + ((entry - sl) * 1.5)
        tp2 = entry + ((entry - sl) * 3)

        st.write(f"TP1: {round(tp1,2)}")
        st.write(f"TP2: {round(tp2,2)}")
