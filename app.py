# ---------------- PHASE 2 & 3 ---------------- #
st.markdown("---")

# CHANGE: Phase 2 and 3 now only require 15M Confirmation and News to be OK
phase2_ready = bias_15m_ok and news_ok 

if m5_confirmed:
    if m5_bos_ok: st.success("📈 5M TREND CONTINUATION: BOS Confirmed.")
    if m5_mss_ok: st.info("🎯 5M TREND REVERSAL: MSS Confirmed.")
else:
    st.warning("⚠️ 5M Micro-Confirmation not yet set (Optional Info).")

col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    # CHANGED: disabled=not phase2_ready
    poi_type = st.selectbox("Trading Zone", ["Select...", "Swing High", "Swing Low", "Supply Zone", "Demand Zone", "Order Block", "FVG"], disabled=not phase2_ready)
    zone_price = st.number_input("Entry Zone Price", value=0.0, format="%.2f", disabled=not phase2_ready)

with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    # CHANGED: disabled=not phase2_ready
    trade_dir = st.radio("Position Direction", ["LONG 🔵", "SHORT 🔴"], horizontal=True, disabled=not phase2_ready)
    
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    
    # Auto SL (15 pips)
    calc_sl = 0.0
    if zone_price > 0:
        calc_sl = zone_price - (15 * pip_factor) if trade_dir == "LONG 🔵" else zone_price + (15 * pip_factor)

    sl_val = st.number_input("Stop Loss", value=calc_sl, format="%.2f", disabled=not phase2_ready)
    entry_val = st.number_input("Manual Entry Price", value=0.0, format="%.2f", disabled=not phase2_ready)
    
    if entry_val > 0 and sl_val > 0:
        pips_dist = abs(entry_val - sl_val) / pip_factor
        if pips_dist > 0:
            lot_size = (current_risk_usd / pips_dist) / 10
            st.metric("Calculated Lot Size", f"{round(lot_size, 2)}")
            st.write(f"📏 Dist: {round(pips_dist, 1)} pips | 💵 Total Risk: ${round(current_risk_usd, 2)}")
