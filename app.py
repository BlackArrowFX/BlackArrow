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
st.markdown("---")


# ---------------- SESSION STATE ---------------- #
# We track the balance in session state so it persists and updates
if "balance" not in st.session_state:
    st.session_state.balance = 2146.11
if "trade_count" not in st.session_state:
    st.session_state.trade_count = 0
if "daily_loss_total" not in st.session_state:
    st.session_state.daily_loss_total = 0.0
if "win_count" not in st.session_state:
    st.session_state.win_count = 0


# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.header("💰 Risk Engine")

    # The balance is now tied to the session state
    st.metric("Current Account Balance", f"${round(st.session_state.balance, 2)}")
    
    risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 5.0)
    risk_usd = st.session_state.balance * (risk_pct / 100)
    
    # Max Risk logic (10% of balance)
    max_daily_risk_usd = st.session_state.balance * 0.10

    st.info(f"Risk per Trade: ${round(risk_usd, 2)}")
    st.warning(f"Max Daily Risk (10%): ${round(max_daily_risk_usd, 2)}")

    st.header("⏰ Session")
    session = st.selectbox("Session", ["Asia", "London", "New York"])

    st.header("🌍 News")
    st.markdown("[Open Forex Factory 📅](https://www.forexfactory.com/)")
    news_ok = st.toggle("No High Impact News")

    st.markdown("---")
    st.header("📊 Journal (Max 3 Trades)")
    
    st.write(f"Trades Taken: {st.session_state.trade_count} / 3")
    
    # LOSS BUTTON
    loss_disabled = st.session_state.trade_count >= 3 or st.session_state.daily_loss_total >= max_daily_risk_usd
    if st.button("❌ RECORD LOSS", disabled=loss_disabled, use_container_width=True):
        st.session_state.balance -= risk_usd
        st.session_state.daily_loss_total += risk_usd
        st.session_state.trade_count += 1
        st.rerun()

    # WIN SECTION
    win_disabled = st.session_state.trade_count >= 3
    with st.expander("✅ RECORD WIN", expanded=not win_disabled):
        win_amount = st.number_input("Profit Amount ($)", min_value=0.0, value=risk_usd * 2, step=10.0)
        if st.button("Add Win to Balance", disabled=win_disabled):
            st.session_state.balance += win_amount
            st.session_state.win_count += 1
            st.session_state.trade_count += 1
            st.rerun()

    if st.button("🔄 Reset Daily Journal"):
        st.session_state.trade_count = 0
        st.session_state.daily_loss_total = 0.0
        st.session_state.win_count = 0
        st.rerun()


# ---------------- HARD STOP LOGIC ---------------- #
if st.session_state.trade_count >= 3:
    st.error("🛑 MAX TRADES (3) REACHED FOR TODAY")
    st.stop()

if st.session_state.daily_loss_total >= max_daily_risk_usd:
    st.error(f"🛑 MAX RISK LIMIT (10%) HIT: -${round(st.session_state.daily_loss_total, 2)}")
    st.stop()


# ---------------- FILTER ---------------- #
st.header("PHASE 0: HARD FILTER")
session_ok = session in ["London", "New York"]
st.checkbox("Valid Session (LDN/NY)", value=session_ok, disabled=True)
st.checkbox("News Cleared", value=news_ok, disabled=True)
hard_ok = session_ok and news_ok


# ---------------- 📋 POI INPUT ---------------- #
st.markdown("---")
st.header("📋 Paste POI Trading Plan")
raw_text = st.text_area("Paste POI zones here", height=150, placeholder="Extreme Supply $4710 - $4712")


# ---------------- 🧠 POI PARSER ---------------- #
POI_DB = {}
if raw_text:
    lines = raw_text.split("\n")
    for line in lines:
        line = line.strip().replace("–", "-")
        match = re.search(r"(\d{3,5}\.?\d*)\s*-\s*(\d{3,5}\.?\d*)", line)
        if match:
            low, high = float(match.group(1)), float(match.group(2))
            name = line.split("$")[0].strip() or f"Zone {len(POI_DB)+1}"
            POI_DB[name] = {"low": low, "high": high, "desc": line}
    st.success(f"✅ Parsed {len(POI_DB)} Zones")


# ---------------- 🏆 POI SELECTOR ---------------- #
st.markdown("---")
st.header("🏆 POI Selection Engine")
price = st.number_input("Current XAUUSD Price", value=0.0, format="%.2f")

inside_zone = False
poi_valid = False

if POI_DB:
    selected_poi = st.selectbox("Select POI Zone", list(POI_DB.keys()))
    poi = POI_DB[selected_poi]
    poi_valid = True
    if poi["low"] <= price <= poi["high"]:
        inside_zone = True
        st.success("✅ PRICE INSIDE POI")
    else:
        st.error("❌ PRICE OUTSIDE POI")


# ---------------- HTF & ENTRY ---------------- #
st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.header("PHASE 1: HTF BIAS")
    trend = st.radio("Structure", ["Bullish", "Bearish", "Ranging"])
    htf_confirm = st.checkbox("HTF Confirmed")
    bias_ok = trend != "Ranging" and htf_confirm

with col_b:
    st.header("PHASE 2: ENTRY")
    mss = st.checkbox("MSS / CHoCH")
    sweep = st.checkbox("Liquidity Sweep")
    fvg_ob = st.toggle("FVG or OB Present")
    trigger_ok = mss and sweep and fvg_ob


# ---------------- SCORING ---------------- #
score = 0
if hard_ok: score += 2
if bias_ok: score += 3
if poi_valid: score += 2
if inside_zone: score += 3
if mss: score += 2

st.markdown("---")
st.header("EXECUTION ENGINE")
st.metric("Trade Quality Score", score)

if score >= 9 and trigger_ok:
    st.success("🚀 A+ SETUP: EXECUTE")
elif score >= 7:
    st.warning("⚠️ B SETUP: CAUTION")
else:
    st.error("🛑 NO TRADE")


# ---------------- POSITION CALCULATOR ---------------- #
st.markdown("---")
st.header("POSITION CALCULATOR")
c1, c2, c3 = st.columns(3)

with c1:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    sl = st.number_input("Stop Loss", value=0.0, format="%.2f")

with c2:
    if entry > 0 and sl > 0:
        pips = abs(entry - sl) * 10
        lot = risk_usd / (pips * 10) if pips > 0 else 0
        st.metric("Lot Size", round(lot, 2))
        st.write(f"Risking: ${round(risk_usd, 2)}")

with c3:
    if entry > 0 and sl > 0:
        st.write(f"TP1 (1.5R): **{round(entry + (entry-sl)*1.5, 2)}**")
        st.write(f"TP2 (3.0R): **{round(entry + (entry-sl)*3.0, 2)}**")
