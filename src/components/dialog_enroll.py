import streamlit as st
from src.database.db import enroll_employee_to_subject, get_subject_by_code, is_employee_enrolled
import time


@st.dialog("Join Project")
def enroll_dialog():
    st.write('Enter the project code provided by your company to join')
    join_code = st.text_input('Project Code', placeholder='Eg. PRJ101')

    if st.button('Join now', type='primary', width='stretch'):
        if join_code:
            subject = get_subject_by_code(join_code)
            if subject:
                employee_id = st.session_state.employee_data['employee_id']
                if is_employee_enrolled(employee_id, subject['subject_id']):
                    st.warning('You have already joined this project')
                else:
                    enroll_employee_to_subject(employee_id, subject['subject_id'])
                    st.success('Successfully joined!')
                    time.sleep(1)
                    st.rerun()
            else:
                st.error('Project code not found!')
        else:
            st.warning('Please enter a project code')