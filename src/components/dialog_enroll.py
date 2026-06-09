import streamlit as st
from src.database.db import enroll_employee_to_subject, get_subject_by_code, is_employee_enrolled
import time


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write('Enter the subject code provided by your company to enroll')
    join_code = st.text_input('Subject Code', placeholder='Eg. CS101')

    if st.button('Enroll now', type='primary', width='stretch'):
        if join_code:
            subject = get_subject_by_code(join_code)
            if subject:
                employee_id = st.session_state.employee_data['employee_id']
                if is_employee_enrolled(employee_id, subject['subject_id']):
                    st.warning('You are already enrolled in this program')
                else:
                    enroll_employee_to_subject(employee_id, subject['subject_id'])
                    st.success('Successfully enrolled!')
                    time.sleep(1)
                    st.rerun()
            else:
                st.error('Subject code not found!')
        else:
            st.warning('Please enter a subject code')