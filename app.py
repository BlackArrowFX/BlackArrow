import streamlit as st
from datetime import datetime

# ---------------- SETUP ---------------- #
st.set_page_config(page_title="BlackArrowFX Precision Engine", layout="wide")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.header("⚙️ System Config")
    
    asset_type = st.selectbox(
        "Select Asset Class", 
        ["METAL (Gold/Silver)", "FOREX", "INDICES / CRYPTO"]
    )
    
    symbol = st.text_input("Enter Instrument", value="XAUUSD").upper()
    
    st.markdown("---")
    st.header("💰 Risk Engine")

    if "balance" not in st.session_state:
        st.session_state.balance = 2146.11

    st.metric("Current Balance", f"${round(st.session_state.balance, 2)}")

    risk_method = st.radio("Risk Method", ["Percentage (%)", "Fixed Amount ($)"])
    
    if risk_method == "Percentage (%)":
        risk_pct = st.slider("Risk per Trade (%)", 0.25, 10.0, 1.0)
        current_risk_usd = st.session_state.balance * (risk_pct / 100)
    else:
        current_risk_usd = st.number_input("Risk Amount ($)", min_value=1.0, value=50.0)

    st.header("🌍 News Filter")
    news_ok = st.toggle("No High Impact News", value=False)

    if not news_ok:
        st.warning("⚠️ Confirm news to unlock system")

    if "trade_count" not in st.session_state:
        st.session_state.trade_count = 0

    st.header("📊 Journal")

    col_loss, col_win = st.columns(2)

    with col_loss:
        if st.button("❌ LOSS", disabled=not news_ok or st.session_state.trade_count >= 3):
            st.session_state.balance -= current_risk_usd
            st.session_state.trade_count += 1
            st.rerun()

    with col_win:
        if st.button("✅ WIN", disabled=not news_ok or st.session_state.trade_count >= 3):
            st.session_state.balance += current_risk_usd * 2
            st.session_state.trade_count += 1
            st.rerun()

# ---------------- HEADER ---------------- #
st.title(f"🏹 BlackArrowFX: {symbol} Precision Engine")
st.caption(f"{symbol} | {asset_type} | {dt_string}")
st.markdown("---")

# ---------------- TIMEFRAME ---------------- #
c4h, c1h, c5m = st.columns(3)

# 4H
c4h.subheader("⏳ 4H BIAS")
trend_4h = c4h.radio("4H Trend", ["Bullish", "Bearish", "Ranging"], key="4h")
h4_ok = c4h.checkbox("4H Confirmed")

# 1H
c1h.subheader("⏱️ 1H STRUCTURE")
trend_1h = c1h.radio("1H Trend", ["Bullish", "Bearish", "Ranging"], key="1h", disabled=not h4_ok)
h1_ok = c1h.checkbox("1H Confirmed", disabled=not h4_ok)

# 5M
c5m.subheader("⚡ 5M SHIFT")
trend_5m = c5m.radio("5M Trend", ["Bullish", "Bearish", "Ranging"], key="5m", disabled=not h1_ok)
m5_ok = c5m.checkbox("5M Confirmed", disabled=not h1_ok)

# ---------------- AUTO MODE DETECTION ---------------- #
mode = "NONE"

if trend_4h == trend_1h == trend_5m and trend_4h != "Ranging":
    mode = "TREND CONTINUATION (EXTERNAL)"
elif trend_4h != trend_1h and trend_1h == trend_5m:
    mode = "PULLBACK (INTERNAL)"

# ---------------- PHASE 2 ---------------- #
st.markdown("---")
col1, col2 = st.columns([1,2])

with col1:
    st.header("📍 PHASE 2: POI")

    poi_type = st.selectbox(
        "Select POI",
        ["Select...", "Swing High", "Swing Low", "Supply", "Demand", "Order Block", "FVG"],
        disabled=not m5_ok
    )

    zone_price = st.number_input("Zone Price", value=0.0, disabled=not m5_ok)

    # STRUCTURE TYPE (NEW)
    structure_type = st.radio(
        "Structure Type",
        ["External (Safe)", "Internal (Aggressive)"],
        disabled=not (poi_type != "Select..." and zone_price > 0)
    )

# ---------------- PHASE 3 ---------------- #
with col2:
    st.header("🚀 PHASE 3: EXECUTION")

    if asset_type == "METAL (Gold/Silver)":
        pip_factor = 0.1
    elif asset_type == "FOREX":
        pip_factor = 0.0001
    else:
        pip_factor = 1

    sl = 0.0

    if zone_price > 0:
        if "High" in poi_type or "Supply" in poi_type:
            sl = zone_price + (15 * pip_factor)
        else:
            sl = zone_price - (15 * pip_factor)

    sl = st.number_input("Stop Loss", value=sl)
    entry = st.number_input("Entry Price", value=0.0)

    if entry > 0 and sl > 0:
        pips = abs(entry - sl) / pip_factor
        lot = (current_risk_usd / pips) / 10 if pips > 0 else 0

        st.metric("Lot Size", round(lot,2))
        st.caption(f"Risk: {round(pips,1)} pips")

# ---------------- FINAL LOGIC ---------------- #
st.markdown("---")

# Direction validation
direction_ok = False

if mode == "TREND CONTINUATION (EXTERNAL)":
    if trend_4h == "Bullish" and poi_type in ["Demand", "Swing Low"]:
        direction_ok = True
    elif trend_4h == "Bearish" and poi_type in ["Supply", "Swing High"]:
        direction_ok = True

if mode == "PULLBACK (INTERNAL)":
    if trend_1h == "Bearish" and poi_type in ["Supply", "Swing High"]:
        direction_ok = True
    elif trend_1h == "Bullish" and poi_type in ["Demand", "Swing Low"]:
        direction_ok = True

# ---------------- STATUS ---------------- #
if not news_ok:
    st.error("❌ BLOCKED: News not cleared")

elif not (h4_ok and h1_ok and m5_ok):
    st.warning("⚠️ WAIT: Confirm all timeframes")

elif mode == "NONE":
    st.warning("⚠️ No clear market mode")

elif poi_type == "Select..." or zone_price == 0:
    st.warning("⚠️ Define POI")

elif not direction_ok:
    st.error("❌ WRONG DIRECTION vs POI")

else:
    st.success(f"🔥 READY TO TRADE → {mode}")
