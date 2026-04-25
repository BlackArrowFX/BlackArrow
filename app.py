import streamlit as st
import re

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX POI Engine", layout="wide")

st.title("🏹 BlackArrowFX: POI Mechanical Trading Engine")
st.caption("Paste → Parse → Select → Execute | Robust POI System")
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
    
    # UPDATED: Risk per trade now defaults to 5.0%
    risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 5.0)

    risk_usd = balance * (risk_pct / 100)
    st.info(f"Risk per Trade: ${round(risk_usd,2)}")

    st.header("⏰ Session Filter")
    session = st.selectbox("Session", ["Asia", "London", "New York"])

    st.header("🌍 News Filter")
    # UPDATED: Added Forex Factory link for quick access
    st.markdown("[Open Forex Factory 📅](https://www.forexfactory.com/)")
    news_ok = st.toggle("No High Impact News")

    st.markdown("---")

    st.header("📊 Journal")

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

    if st.button("🔄 Reset"):
        st.session_state.loss_count = 0
        st.session_state.loss_amount = 0.0
        st.session_state.win_count = 0


# ---------------- DAILY LOSS LIMIT ---------------- #
max_loss_usd = balance * 0.03

if st.session_state.loss_count >= 2 or st.session_state.loss_amount >= max_loss_usd:
    st.error("🛑 DAILY LOSS LIMIT HIT — STOP TRADING")
    st.stop()


# ---------------- FILTER ---------------- #
st.header("PHASE 0: HARD FILTER")

session_ok = session in ["London", "New York"]

st.checkbox("Valid Session", value=session_ok, disabled=True)
st.checkbox("News Cleared", value=news_ok, disabled=True)

hard_ok = session_ok and news_ok


# ---------------- 📋 PASTE POI INPUT ---------------- #
st.markdown("---")
st.header("📋 Paste POI Trading Plan")

raw_text = st.text_area(
    "Paste your POI zones here",
    height=250,
    placeholder="Extreme Supply (Key) $4710 - $4712 ... etc"
)


# ---------------- 🧠 ROBUST POI PARSER ---------------- #
POI_DB = {}

if raw_text:

    lines = raw_text.split("\n")

    for line in lines:

        line = line.strip()

        if len(line) < 8:
            continue

        # normalize dash types
        line = line.replace("–", "-")

        # extract price range (handles messy formats)
        match = re.search(r"(\d{3,5}\.?\d*)\s*-\s*(\d{3,5}\.?\d*)", line)

        if not match:
            continue

        try:
            low = float(match.group(1))
            high = float(match.group(2))
        except:
            continue

        # zone name extraction (before $ or price)
        zone_name = line.split("$")[0].strip()

        if zone_name == "":
            zone_name = f"Zone {len(POI_DB)+1}"

        POI_DB[zone_name] = {
            "low": low,
            "high": high,
            "desc": line
        }

    st.success(f"✅ Parsed {len(POI_DB)} POI Zones")


# ---------------- 🏆 POI SELECTOR ---------------- #
st.markdown("---")
st.header("🏆 POI Selection Engine")

price = st.number_input("Current XAUUSD Price", value=0.0)

selected_poi = "No Man's Land"
inside_zone = False
poi_valid = False

if len(POI_DB) > 0:

    selected_poi = st.selectbox("Select POI Zone", list(POI_DB.keys()))
    poi = POI_DB[selected_poi]

    st.write("🧠 Zone Data:")
    st.write(poi["desc"])

    poi_valid = True

    if poi["low"] <= price <= poi["high"]:
        inside_zone = True
        st.success("✅ PRICE INSIDE POI ZONE")
    else:
        st.error("❌ PRICE OUTSIDE ZONE")

else:
    st.warning("⚠️ Paste POI first")


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
fvg = st.checkbox("FVG")
ob = st.checkbox("Order Block")

trigger_ok = mss and sweep and (fvg or ob)


# ---------------- SCORING ---------------- #
score = 0

if hard_ok:
    score += 2

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
if score >= 9:
    grade = "A+ EXECUTE 🚀"
elif score >= 7:
    grade = "B SETUP ⚠️"
else:
    grade = "NO TRADE ❌"


# ---------------- FINAL ENGINE ---------------- #
st.markdown("---")
st.header("EXECUTION ENGINE")

st.metric("Score", score)
st.write(f"Grade: **{grade}**")

if not hard_ok:
    st.error("BLOCKED: Session/News")

elif not poi_valid:
    st.error("NO TRADE: No POI parsed")

elif not bias_ok:
    st.error("NO TRADE: Weak bias")

elif not inside_zone:
    st.error("NO TRADE: Price outside POI")

elif not trigger_ok:
    st.warning("WAIT: No confirmation")

elif score >= 9:
    st.success("🚀 EXECUTE TRADE")

elif score >= 7:
    st.warning("⚠️ Optional Trade")

else:
    st.error("NO TRADE")


# ---------------- POSITION ENGINE ---------------- #
st.markdown("---")
st.header("POSITION CALCULATOR")

c1, c2, c3 = st.columns(3)

with c1:
    entry = st.number_input("Entry Price", key="entry_price", value=0.0)
    sl = st.number_input("Stop Loss", key="sl_price", value=0.0)

with c2:
    if entry > 0 and sl > 0:
        pip_dist = abs(entry - sl) * 10
        # Formula: Lot = Risk_USD / (Pip_Distance * Pip_Value)
        # Note: Pip_Value depends on your broker's contract size
        lot = risk_usd / (pip_dist * 10) if pip_dist > 0 else 0

        st.metric("Lot Size", round(lot,2))
        st.write(f"SL Distance: {round(pip_dist,1)} pips")

with c3:
    if entry > 0 and sl > 0:
        tp1 = entry + ((entry - sl) * 1.5)
        tp2 = entry + ((entry - sl) * 3)

        st.write(f"TP1 (1.5R): {round(tp1,2)}")
        st.write(f"TP2 (3R): {round(tp2,2)}")
