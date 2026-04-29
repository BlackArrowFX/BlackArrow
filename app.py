# ---------------- 📊 SESSION LOG ---------------- #
st.markdown("---")
st.header("📂 Session Trade Log")

if st.session_state.trade_history:
    # 1. Selection & Deletion Logic
    # We create a list of indices the user wants to delete
    to_delete = []
    
    for i, trade in enumerate(st.session_state.trade_history):
        col_tick, col_info, col_edit = st.columns([0.5, 6, 1])
        
        with col_tick:
            # The "Tick" to delete
            if st.checkbox("", key=f"tick_{i}"):
                to_delete.append(i)
        
        with col_info:
            st.write(f"**#{i+1}: {trade['Asset']} {trade['Dir']}** | POI: {trade['POI']} | Time: {trade['Time']}")
        
        with col_edit:
            # Edit Button
            if st.button("📝 Edit", key=f"edit_btn_{i}"):
                st.session_state.editing_index = i
                st.session_state.temp_notes = trade['Plan']

    # 2. The Edit Modal (Appears when 'Edit' is clicked)
    if "editing_index" in st.session_state:
        idx = st.session_state.editing_index
        st.markdown(f"### ✏️ Editing Trade #{idx + 1} Notes")
        new_notes = st.text_area("Update Plan:", value=st.session_state.temp_notes, height=150)
        
        c_save, c_cancel = st.columns(2)
        if c_save.button("Update & Save"):
            st.session_state.trade_history[idx]['Plan'] = new_notes
            del st.session_state.editing_index # Close edit mode
            st.rerun()
        if c_cancel.button("Cancel"):
            del st.session_state.editing_index
            st.rerun()

    st.markdown("---")
    
    # 3. Action Buttons
    c_del, c_clr, c_dl = st.columns([1, 1, 1])
    
    with c_del:
        if st.button("🗑️ DELETE SELECTED", use_container_width=True):
            # Delete from back to front to avoid index shifting issues
            for index in sorted(to_delete, reverse=True):
                st.session_state.trade_history.pop(index)
            st.rerun()
            
    with c_clr:
        if st.button("🧨 CLEAR ALL", use_container_width=True):
            st.session_state.trade_history = []
            st.rerun()
            
    with c_dl:
        full_df = pd.DataFrame(st.session_state.trade_history)
        csv = full_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DOWNLOAD CSV", data=csv, file_name="Trade_Log.csv", mime="text/csv", use_container_width=True)

else:
    st.info("No trades saved yet.")
