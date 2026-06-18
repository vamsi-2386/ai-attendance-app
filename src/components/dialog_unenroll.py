import streamlit as st
from src.database.db import unenroll_employee_from_subject
import time

@st.dialog("Leave Project")
def unenroll_dialog(subject_name, subject_id):
    st.warning(f"Are you sure you want to leave the project **{subject_name}**?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel"):
            st.rerun()
    with col2:
        if st.button("Leave Project", type="primary", use_container_width=True):
            employee_id = st.session_state.employee_data['employee_id']
            unenroll_employee_from_subject(employee_id, subject_id)
            st.success("Successfully unenrolled!")
            time.sleep(1)
            st.rerun()
