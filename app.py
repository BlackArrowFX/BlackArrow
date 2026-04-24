import streamlit as st

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX POI Mechanical Engine", layout="wide")

st.title("🏹 BlackArrowFX: POI Mechanical Trading Engine")
st.caption("SMC Execution System | Upload-Based POI Engine | Zero Emotion Trading")
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

st.checkbox("Valid Session", value=session_ok, disabled=True)
st.checkbox("News Cleared", value=news_ok, disabled=True)

hard_ok = session_ok and news_ok


# ---------------- 📂 POI UPLOAD ENGINE ---------------- #
st.markdown("---")
st.header("📂 Upload POI Trading Plan")

uploaded_file = st.file_uploader("Upload POI File (.txt)", type=["txt"])

POI_DB = {}

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    lines = content.split("\n")

    for line in lines:
        if "|" in line:
            parts = line.split("|")

            if len(parts) == 3:
                name = parts[0].strip()
                price_range = parts[1].strip()
                desc = parts[2].strip()

                try:
                    low, high = price_range.split("-")
                    POI_DB[name] = {
                        "range": price_range,
                        "low": float(low),
                        "high": float(high),
                        "desc": desc
                    }
                except:
                    pass

    st.success("✅ POI Ledger Loaded")


# ---------------- 🏆 POI ENGINE ---------------- #
st.markdown("---")
st.header("🏆 POI Zone Selector")

inside_zone = False
poi_valid = False
selected_poi = "No Man's Land"

if len(POI_DB) > 0:

    selected_poi = st.selectbox("Select POI Zone", list(POI_DB.keys()))
    poi = POI_DB[selected_poi]

    st.write(f"📌 Range: {poi['range']}")
    st.write(f"🧠 Logic: {poi['desc']}")

    poi_valid = True

    price = st.number_input("Current XAUUSD Price", value=0.0)

    if poi["low"] <= price <= poi["high"]:
        inside_zone = True
        st.success("✅ PRICE INSIDE POI")
    else:
        st.error("❌ PRICE OUTSIDE POI")

else:
    st.warning("⚠️ Upload POI file to activate system")


# ---------------- HTF BIAS ---------------- #
st.markdown("---")
st.header("PHASE 1: HTF BIAS")

trend = st.radio("Market Structure", ["Bullish", "Bearish", "Ranging"])
htf_confirm = st.checkbox("HTF Confirmed")

bias_ok = trend != "Ranging" and htf_confirm


# ---------------- ENTRY CONFIRMATION ---------------- #
st.markdown("---")
st.header("PHASE 2: ENTRY CONFIRMATION")

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

if inside_zone:
    score += 3

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


# ---------------- FINAL ENGINE ---------------- #
st.markdown("---")
st.header("EXECUTION ENGINE")

st.metric("Setup Score", score)
st.write(f"Grade: **{grade}**")

if not hard_ok:
    st.error("❌ BLOCKED: Session/News")

elif not poi_valid:
    st.error("❌ NO TRADE: No POI loaded")

elif not bias_ok:
    st.error("❌ NO TRADE: Weak HTF bias")

elif not inside_zone:
    st.error("❌ NO TRADE: Price not inside POI")

elif not trigger_ok:
    st.warning("⚠️ WAIT: No entry confirmation")

elif score >= 8:
    st.success("🚀 EXECUTE TRADE")

elif score >= 6:
    st.warning("⚠️ Optional Setup")

else:
    st.error("❌ NO TRADE")


# ---------------- POSITION ENGINE ---------------- #
st.markdown("---")
st.header("POSITION CALCULATOR")

c1, c2, c3 = st.columns(3)

with c1:
    entry = st.number_input("Entry Price", value=0.0)
    sl = st.number_input("Stop Loss", value=0.0)

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

        st.write(f"TP1: {round(tp1,2)}")
        st.write(f"TP2: {round(tp2,2)}")
