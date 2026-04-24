import streamlit as st

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX POI Mechanical Engine", layout="wide")

st.title("🏹 BlackArrowFX: POI Mechanical Trading Engine")
st.caption("SMC Execution System | Embedded POI Ledger | Zero Emotion Trading")
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
    st.header("💰 Risk Engine")

    balance = st.number_input("Account Balance ($)", value=2146.11)
    risk_pct = st.slider("Risk per Trade (%)", 0.25, 1.0, 1.0, step=0.25)

    risk_usd = balance * (risk_pct / 100)
    st.info(f"Risk: ${round(risk_usd,2)}")

    st.header("⏰ Session Filter")
    session = st.selectbox("Session", ["Asia", "London", "New York"])

    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News (30–60min)")

    st.markdown("---")
    st.header("📊 Trade Journal")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("❌ LOSS"):
            st.session_state.loss_count += 1
            st.session_state.loss_amount += risk_usd

    with c2:
        if st.button("✅ WIN"):
            st.session_state.win_count += 1

    st.write(f"Losses: {st.session_state.loss_count}")
    st.write(f"Loss $: {round(st.session_state.loss_amount,2)}")
    st.write(f"Wins: {st.session_state.win_count}")

    if st.button("🔄 Reset Day"):
        st.session_state.loss_count = 0
        st.session_state.loss_amount = 0.0
        st.session_state.win_count = 0

# ---------------- DAILY LIMIT ---------------- #
max_loss_usd = balance * 0.03

if st.session_state.loss_count >= 2 or st.session_state.loss_amount >= max_loss_usd:
    st.error("🛑 DAILY LOSS LIMIT HIT — STOP TRADING")
    st.stop()

# ---------------- PHASE 0 ---------------- #
st.header("PHASE 0: HARD FILTER")

session_ok = session in ["London", "New York"]

st.checkbox("Valid Session (London/NY)", value=session_ok, disabled=True)
st.checkbox("News Cleared", value=news_ok, disabled=True)

hard_ok = session_ok and news_ok

# ---------------- HTF BIAS ---------------- #
st.markdown("---")
st.header("PHASE 1: HTF BIAS")

trend = st.radio("Market Structure", ["Bullish", "Bearish", "Ranging"])
htf_confirm = st.checkbox("HTF Structure Confirmed")

bias_ok = trend != "Ranging" and htf_confirm

# ---------------- 🏆 POI LEDGER (CORE UPGRADE) ---------------- #
st.markdown("---")
st.header("🏆 High-Probability POI Ledger (XAUUSD)")

st.info("Trade ONLY when price is inside these zones")

poi_zone = st.selectbox(
    "Current Price Location",
    [
        "No Man's Land",
        "4657 – 4662 (Demand)",
        "4678 – 4680 (Internal Pivot)",
        "4685 – 4688 (Bearish OB)",
        "4695 – 4700 (Decisionary Supply)",
        "4710 – 4712 (Extreme Supply)"
    ]
)

# POI logic mapping
poi_valid = poi_zone != "No Man's Land"

sell_zones = [
    "4685 – 4688 (Bearish OB)",
    "4695 – 4700 (Decisionary Supply)",
    "4710 – 4712 (Extreme Supply)"
]

buy_zone = "4657 – 4662 (Demand)"

# Direction filter
if trend == "Bearish" and poi_zone in sell_zones:
    poi_direction_ok = True
elif trend == "Bullish" and poi_zone == buy_zone:
    poi_direction_ok = True
else:
    poi_direction_ok = False

# ---------------- PHASE 3: ENTRY CONFIRMATION ---------------- #
st.markdown("---")
st.header("PHASE 3: ENTRY CONFIRMATION")

mss = st.checkbox("MSS / CHoCH")
sweep = st.checkbox("Liquidity Sweep")
fvg = st.checkbox("FVG Present")
ob = st.checkbox("Order Block Confirmed")

trigger_ok = mss and sweep and (fvg or ob)

# ---------------- SCORING ---------------- #
score = 0

if bias_ok:
    score += 3
if poi_valid:
    score += 2
if poi_direction_ok:
    score += 2
if mss:
    score += 2
if fvg or ob:
    score += 1

if score >= 8:
    grade = "A+ SETUP 🚀"
elif score >= 6:
    grade = "B SETUP ⚠️"
else:
    grade = "NO TRADE ❌"

# ---------------- FINAL DECISION ---------------- #
st.markdown("---")
st.header("EXECUTION ENGINE")

st.metric("Setup Score", score)
st.write(f"Trade Grade: **{grade}**")

if not hard_ok:
    st.error("❌ BLOCKED: Session / News Filter")

elif not bias_ok:
    st.error("❌ NO TRADE: HTF Bias Invalid")

elif not poi_valid:
    st.error("❌ NO TRADE: Not in POI Zone")

elif not poi_direction_ok:
    st.error("❌ NO TRADE: Wrong direction vs POI")

elif not trigger_ok:
    st.warning("⚠️ WAIT: No confirmation yet")

elif score >= 8:
    st.success("🚀 EXECUTE TRADE — ALL CONDITIONS MET")
    st.balloons()

elif score >= 6:
    st.warning("⚠️ Optional Setup (Lower Confidence)")

else:
    st.error("❌ NO TRADE")

# ---------------- POSITION CALCULATOR ---------------- #
st.markdown("---")
st.header("POSITION MANAGEMENT")

c1, c2, c3 = st.columns(3)

with c1:
    entry = st.number_input("Entry Price", value=0.0)
    sl = st.number_input("SL Price", value=0.0)

with c2:
    if entry > 0 and sl > 0:
        pip_dist = abs(entry - sl) * 10
        lot = risk_usd / (pip_dist * 10) if pip_dist > 0 else 0

        st.metric("Lot Size", round(lot,2))
        st.write(f"SL Distance: {round(pip_dist,1)} pips")

with c3:
    if entry > 0 and sl > 0:
        tp1 = entry + ((entry - sl) * 1.5)
        tp2 = entry + ((entry - sl) * 3)

        st.write(f"TP1 (1.5R): {round(tp1,2)}")
        st.write(f"TP2 (3R): {round(tp2,2)}")
