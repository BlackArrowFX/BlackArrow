# ... (Sidebar and Quad-Timeframe code remains the same) ...

# ---------------- PHASE 2: POI ---------------- #
st.markdown("---")
col_poi, col_exec = st.columns([1, 2])

with col_poi:
    st.header("📋 PHASE 2: POI")
    # This only unlocks if 15M Confirmed is checked
    ready_to_trade = news_ok and bias_15m_ok
    
    poi_type = st.selectbox(
        "Where am I trading?", 
        ["Select POI...", "Swing High", "Swing Low", "Supply Zone", "Demand Zone", "Order Block", "FVG"], 
        disabled=not ready_to_trade
    )
    
    zone_price = st.number_input(
        "Entry Zone Price", 
        value=0.0, 
        format="%.2f", 
        disabled=not ready_to_trade
    )

# ---------------- PHASE 3: EXECUTE ---------------- #
with col_exec:
    st.header("🚀 PHASE 3: EXECUTE")
    
    # 1. Pip Factor for Gold (0.1)
    pip_factor = 0.1 if asset_type == "METAL (Gold/Silver)" else (0.0001 if asset_type == "FOREX" else 1.0)
    
    # 2. Automated Stop Loss Calculation
    # If trading a High/Supply, SL goes ABOVE. If Low/Demand, SL goes BELOW.
    calculated_sl = 0.0
    if zone_price > 0:
        is_short_setup = any(x in poi_type for x in ["High", "Supply"])
        # 15 pips for Gold = 1.5 points
        if is_short_setup:
            calculated_sl = zone_price + (15 * pip_factor)
        else:
            calculated_sl = zone_price - (15 * pip_factor)

    # 3. Inputs for SL and Entry
    sl_input = st.number_input(
        "Stop Loss (Auto 15 pips)", 
        value=calculated_sl, 
        format="%.2f", 
        disabled=not (zone_price > 0)
    )
    
    entry_input = st.number_input(
        "Entry Price (Manual)", 
        value=0.0, 
        format="%.2f", 
        disabled=not (zone_price > 0)
    )
    
    # 4. Lot Size Calculation Display
    if entry_input > 0 and sl_input > 0:
        pips_to_sl = abs(entry_input - sl_input) / pip_factor
        
        if pips_to_sl > 0:
            # Calculation based on your Risk Amount ($50.00 in screenshot)
            # Formula: Risk / (Pips * Value per Pip)
            lot_size = (current_risk_usd / pips_to_sl) / 10 
            
            st.metric("Calculated Lot Size", f"{round(lot_size, 2)}")
            st.info(f"📏 Risk: {round(pips_to_sl, 1)} pips | 💵 Total Risk: ${round(current_risk_usd, 2)}")
