# Updated Execute Logic for Phase 3
with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    
    # 1. ADD: Manual override for Long/Short to ensure math is perfect
    trade_type = st.radio("Direction", ["LONG 🔵", "SHORT 🔴"], horizontal=True)
    
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    
    # 2. Automated SL based on Direction
    calculated_sl = 0.0
    if zone_price > 0:
        if trade_type == "SHORT 🔴":
            calculated_sl = zone_price + (15 * pip_factor)
        else:
            calculated_sl = zone_price - (15 * pip_factor)

    sl_input = st.number_input("Stop Loss", value=calculated_sl, format="%.2f")
    entry_input = st.number_input("Entry Price (Manual)", value=0.0, format="%.2f")
    
    # 3. Calculation Display
    if entry_input > 0 and sl_input > 0:
        pips_diff = abs(entry_input - sl_input) / pip_factor
        
        if pips_diff > 0:
            lot_size = (current_risk_usd / pips_diff) / 10
            st.metric("Recommended Lot Size", f"{round(lot_size, 2)}")
            
            # Smart Comment for this specific alignment
            if trade_type == "LONG 🔵" and htf_bias == "Bullish ⬆️":
                st.success("✅ BULLISH ALIGNMENT: You are trading with the 4H Tide!")
            elif trade_type == "SHORT 🔴" and htf_bias == "Bullish ⬆️":
                st.warning("⚠️ COUNTER-TREND: You are selling into a Bullish 4H Trend.")
