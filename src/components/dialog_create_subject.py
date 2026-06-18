import streamlit as st
from src.database.db import create_subject



@st.dialog("Create New Project")
def create_subject_dialog(company_id):
    st.write("Enter the details of new project")
    sub_id = st.text_input("Project Code *", placeholder="PRJ101")
    sub_name = st.text_input("Project Name *", placeholder="AI Development")

    if st.button("Create Project Now", type='primary', use_container_width=True):
        if sub_id and sub_name:
            try:
                create_subject(sub_id, sub_name, "", company_id)
                st.toast("Project Created Succesfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please fill all the fields")
