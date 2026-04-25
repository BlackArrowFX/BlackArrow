import streamlit as st
import re
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX POI Engine", layout="wide")

# Real-time Date and Time display
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

st.title("🏹 BlackArrowFX: POI Mechanical Trading Engine")
st.caption(f"Current Server Time: {dt_string}")
st.caption("Paste → Parse → Select → Execute | Robust POI System")
st.markdown("---")


# ---------------- SESSION STATE ---------------- #
if "trade_count" not in st.session_state:
    st.session_state.trade_count = 0
if "loss_amount" not in st.session_state:
    st.session_state.loss_amount = 0.0
if "win_count" not in st.session_state:
    st.session_state.win_count = 0


# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.header("💰 Risk Engine")

    balance = st.number_input("Account Balance ($)", value=2146.11)
    risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 5.0)

    risk_usd = balance * (risk_pct / 100)
    
    # CALCULATE MAX RISK (10% of Total Balance)
    max_daily_risk_usd = balance * 0.10
    remaining_risk = max_daily_risk_usd - st.session_state.loss_amount

    st.info(f"Risk per Trade: ${round(risk_usd,2)}")
    st.warning(f"Max Daily Risk (10%): ${round(max_daily_risk_usd,2)}")

    st.header("⏰ Session Filter")
    session = st.selectbox("Session", ["Asia", "London", "New York"])

    st.header("🌍 News Filter")
    st.markdown("[Open Forex Factory 📅](https://www.forexfactory.com/)")
    news_ok = st.toggle("No High Impact News")

    st.markdown("---")

    st.header("📊 Journal (Max 3 Trades)")
    
    # Display Status
    st.write(f"Trades Taken: {st.session_state.trade_count} / 3")
    st.write(f"Risk Used: ${round(st.session_state.loss_amount,2)} / ${round(max_daily_risk_usd,2)}")
    
    c1, c2 = st.columns(2)

    with c1:
        # Disable button if limits are hit
        loss_disabled = st.session_state.trade_count >= 3 or st.session_state.loss_amount >= max_daily_risk_usd
        if st.button("❌ LOSS", disabled=loss_disabled):
            st.session_state.trade_count += 1
            st.session_state.loss_amount += risk_usd

    with c2:
        win_disabled = st.session_state.trade_count >= 3
        if st.button("✅ WIN", disabled=win_disabled):
            st.session_state.trade_count += 1
            st.session_state.win_count += 1

    if st.button("🔄 Reset Journal"):
        st.session_state.trade_count = 0
        st.session_state.loss_amount = 0.0
        st.session_state.win_count = 0


# ---------------- HARD STOP LOGIC ---------------- #
if st.session_state.trade_count >= 3:
    st.error("🛑 MAX TRADES (3) REACHED FOR TODAY")
    st.stop()

if st.session_state.loss_amount >= max_daily_risk_usd:
    st.error(f"🛑 MAX RISK LIMIT (10%) HIT: -${round(st.session_state.loss_amount,2)}")
    st.stop()


# ---------------- FILTER ---------------- #
st.header("PHASE 0: HARD FILTER")

session_ok = session in ["London", "New York"]
st.checkbox("Valid Session (LDN/NY)", value=session_ok, disabled=True)
st.checkbox("News Cleared", value=news_ok, disabled=True)

hard_ok = session_ok and news_ok


# ---------------- 📋 PASTE POI INPUT ---------------- #
st.markdown("---")
st.header("📋 Paste POI Trading Plan")

raw_text = st.text_area(
    "Paste your POI zones here",
    height=200,
    placeholder="Extreme Supply (Key) $4710 - $4712"
)


# ---------------- 🧠 ROBUST POI PARSER ---------------- #
POI_DB = {}
if raw_text:
    lines = raw_text.split("\n")
    for line in lines:
        line = line.strip()
        if len(line) < 8: continue
        line = line.replace("–", "-")
        match = re.search(r"(\d{3,5}\.?\d*)\s*-\s*(\d{3,5}\.?\d*)", line)
        if not match: continue
        try:
            low, high = float(match.group(1)), float(match.group(2))
        except: continue
        zone_name = line.split("$")[0].strip() or f"Zone {len(POI_DB)+1}"
        POI_DB[zone_name] = {"low": low, "high": high, "desc": line}
    st.success(f"✅ Parsed {len(POI_DB)} POI Zones")


# ---------------- 🏆 POI SELECTOR ---------------- #
st.markdown("---")
st.header("🏆 POI Selection Engine")
price = st.number_input("Current XAUUSD Price", value=0.0, format="%.2f")

selected_poi = "No Man's Land"
inside_zone = False
poi_valid = False

if len(POI_DB) > 0:
    selected_poi = st.selectbox("Select POI Zone", list(POI_DB.keys()))
    poi = POI_DB[selected_poi]
    st.info(f"Analyzing: {poi['desc']}")
    poi_valid = True
    if poi["low"] <= price <= poi["high"]:
        inside_zone = True
        st.success("✅ PRICE INSIDE POI ZONE")
    else:
        st.error("❌ PRICE OUTSIDE ZONE")
else:
    st.warning("⚠️ Paste POI first")


# ---------------- HTF & ENTRY ---------------- #
st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.header("PHASE 1: HTF BIAS")
    trend = st.radio("Market Structure", ["Bullish", "Bearish", "Ranging"])
    htf_confirm = st.checkbox("HTF Confirmed")
    bias_ok = trend != "Ranging" and htf_confirm

with col_b:
    st.header("PHASE 2: ENTRY")
    mss = st.checkbox("MSS / CHoCH")
    sweep = st.checkbox("Liquidity Sweep")
    fvg_ob = st.toggle("FVG or Order Block Present")
    trigger_ok = mss and sweep and fvg_ob


# ---------------- SCORING & EXECUTION ---------------- #
score = 0
if hard_ok: score += 2
if bias_ok: score += 3
if poi_valid: score += 2
if inside_zone: score += 3
if mss: score += 2

if score >= 9: grade = "A+ EXECUTE 🚀"
elif score >= 7: grade = "B SETUP ⚠️"
else: grade = "NO TRADE ❌"

st.markdown("---")
st.header("EXECUTION ENGINE")
st.metric("Trade Quality Score", score)
st.subheader(f"Grade: {grade}")

if score >= 9 and trigger_ok:
    st.success("🔥 ALL CONFLUENCES MET: EXECUTE TRADE")
elif score >= 7:
    st.warning("⚠️ PROCEED WITH CAUTION: Lacks full confluence")
else:
    st.error("🛑 CONDITIONS NOT MET")


# ---------------- POSITION CALCULATOR ---------------- #
st.markdown("---")
st.header("POSITION CALCULATOR")
c1, c2, c3 = st.columns(3)

with c1:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    sl = st.number_input("Stop Loss", value=0.0, format="%.2f")

with c2:
    if entry > 0 and sl > 0:
        pip_dist = abs(entry - sl) * 10
        # standard Gold calculation (0.01 lot = $1 per 10 pips approx, varies by broker)
        lot = risk_usd / (pip_dist * 10) if pip_dist > 0 else 0
        st.metric("Lot Size", round(lot, 2))
        st.write(f"Risking: ${round(risk_usd, 2)}")

with c3:
    if entry > 0 and sl > 0:
        tp1 = entry + ((entry - sl) * 1.5)
        tp2 = entry + ((entry - sl) * 3.0)
        st.write(f"TP1 (1.5R): **{round(tp1,2)}**")
        st.write(f"TP2 (3.0R): **{round(tp2,2)}**")
