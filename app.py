# ---------------- AMENDED TRADING PLAN SECTION ---------------- #
with st.expander("📜 MY TRADING PLAN", expanded=False):
    st.markdown(f"""
    ### 1. Market Structure Analysis
    * **1H:** Analyze overall market structure.
    * **15M:** Confirm short-term direction and intraday zones.
    * **5M:** Precise entry execution.

    ### 2. BlackArrowFX Strategic Setup
    * Confirm and mark all **Swing Highs and Swing Lows**.
    * Ensure setup aligns with HTF bias before execution.

    ### 3. BlackArrowClick Execution
    * Select **Fixed Lot** or **Risk Amount** before placing trade.

    ### 4. Risk Management
    * **Max Risk:** 3% to 5% or **$100 maximum**.

    ### 5. Footprint Monitoring
    * **Monitor:** Shark Absorption on 4H/1H & 15M/30M (+ or -) Delta Check.
    * **Zones:** 15M & 30M Footprint Charts at key reversal zones.
    * **Buy Imbalances:** <span style='color:#2962FF; font-weight:bold;'>██ Blue Highlights</span>
    * **Sell Imbalances:** <span style='color:#FFEB3B; font-weight:bold; background-color:#333; padding:2px;'>██ Yellow Highlights</span>
    * **Confirmation:** Focus on **300% Imbalance Stack** for strong order flow.
    * **Execution:** Use delta shifts, absorption, and imbalance clusters.
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------- FOOTPRINT ORDER FLOW UI ---------------- #
st.subheader("👣 FOOTPRINT ORDER FLOW")
cf1, cf2, cf3 = st.columns(3)

with cf1:
    st.markdown("**Shark Absorption**")
    shark_4h = st.checkbox("4H/1H Absorption confirmed")
    shark_ltf = st.checkbox("15M/30M Delta confirmed")

with cf2:
    st.markdown("**Imbalance Check**")
    # Using HTML for the radio labels to show the color
    buy_label = ":blue[Blue Imbalance] (Buy)"
    sell_label = ":orange[Yellow Imbalance] (Sell)" # Streamlit 'orange' is closest to Yellow in native markdown
    
    imb_type = st.radio("Active Imbalance", ["None", "Blue (Buy)", "Yellow (Sell)"], horizontal=True)
    stack_300 = st.toggle("300% Imbalance Stack")

with cf3:
    st.markdown("**Execution Triggers**")
    triggers = st.multiselect("Select Triggers", ["Delta Shift", "Absorption", "Imbalance Cluster"])

# Logic for Confluence Meter (Update score to include these)
footprint_ok = (shark_4h or shark_ltf) and stack_300 and imb_type != "None"
