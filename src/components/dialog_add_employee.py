import streamlit as st
from PIL import Image
import numpy as np
from src.database.db import create_employee, assign_employee_to_project, get_company_subjects
from src.pipelines.face_pipeline import get_face_embeddings

@st.dialog('Register Employee Manually')
def add_employee_dialog(company_id):
    st.write('Fill out the details to manually onboard an employee.')
    
    with st.form("admin_add_employee_form"):
        employee_code = st.text_input("Employee Code *", placeholder="E.g. EMP-001")
        name = st.text_input("Employee Full Name *", placeholder="E.g. John Doe")
        
        # Get projects
        subjects = get_company_subjects(company_id)
        subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}
        
        selected_project_labels = st.multiselect(
            "Assign to Projects (Optional)", 
            options=list(subject_options.keys()),
            help="Select the projects this employee should be a part of."
        )
        
        submit_btn = st.form_submit_button("Proceed to Face Registration", type="primary", use_container_width=True)
        
    if submit_btn:
        employee_code = employee_code.strip() if employee_code else ""
        name = name.strip() if name else ""
        if not employee_code or not name:
            st.error("Employee Code and Name are required!")
        else:
            st.session_state.admin_registering_employee = {
                "employee_code": employee_code,
                "name": name,
                "projects": [subject_options[lbl] for lbl in selected_project_labels]
            }
            st.rerun()

    if "admin_registering_employee" in st.session_state:
        st.divider()
        st.subheader("Face Registration")
        st.info("Please capture a clear photo of the employee's face.")
        
        photo_source = st.camera_input("Capture Employee Face")
        
        if photo_source:
            if st.button("Finalize Registration", type="primary", use_container_width=True):
                with st.spinner("Analyzing face features..."):
                    img = np.array(Image.open(photo_source))
                    encodings = get_face_embeddings(img)
                    if not encodings:
                        st.error("No face detected! Please try again with a clearer photo.")
                    else:
                        face_emb = encodings[0].tolist()
                        emp_data = st.session_state.admin_registering_employee
                        
                        try:
                            response = create_employee(
                                emp_data['employee_code'], 
                                emp_data['name'], 
                                company_id, 
                                face_embedding=face_emb
                            )
                            new_emp_id = response[0]['employee_id']
                            
                            for proj_id in emp_data['projects']:
                                assign_employee_to_project(new_emp_id, proj_id)
                                
                            st.toast(f"Employee {emp_data['name']} successfully registered!")
                            del st.session_state.admin_registering_employee
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to save employee: {str(e)}")
