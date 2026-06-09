import streamlit as st
from src.database.db import enroll_employee_to_subject, get_subject_by_code, is_employee_enrolled
import time


@st.dialog("Quick Join")
def auto_enroll_dialog(subject_code):
    employee_id = st.session_state.employee_data['employee_id']

    subject = get_subject_by_code(subject_code)
    if not subject:
        st.error('Project Code not found!')
        if st.button('Close'):
            st.query_params.clear()
            st.rerun()
        return

    if is_employee_enrolled(employee_id, subject['subject_id']):
        st.info("You've already joined!")
        if st.button('Got it!'):
            st.query_params.clear()
            st.rerun()
        return

    st.markdown(f"Would you like to join **{subject['name']}**?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button('No thanks'):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button('Yes join now!', type='primary', width='stretch'):
            enroll_employee_to_subject(employee_id, subject['subject_id'])
            st.success('Joined successfully!')
            st.query_params.clear()
            time.sleep(2)
            st.rerun()
