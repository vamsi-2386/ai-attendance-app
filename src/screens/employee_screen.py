import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_employees, create_employee, get_employee_attendance, get_company_subjects, get_company_by_invite_code, get_subjects_for_employee, get_company_by_id, employee_gps_checkin, employee_gps_checkout
from src.utils.location_utils import is_within_radius, calculate_distance
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import pandas as pd
import time

from src.components.subject_card import subject_card

def employee_dashboard():
    employee_data = st.session_state.employee_data
    employee_id = employee_data['employee_id']
    company_id = employee_data['company_id']
    
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {employee_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.employee_data 
            st.rerun()

    st.space()

    st.header('Your Company Projects')

    st.divider()

    with st.spinner('Loading your active projects..'):
        subjects = get_subjects_for_employee(employee_id)
        logs = get_employee_attendance(employee_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    if not subjects:
        st.info("Your company hasn't created any projects yet.")
        
    cols = st.columns(2)
    for i, sub in enumerate(subjects):
        sid = sub['subject_id']

        stats = stats_map.get(sid, {"total":0, "attended": 0})
        
        with cols[i % 2]:
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('✅', 'Attended', stats['attended']),
                ]
            )

    st.divider()
    st.header('GPS Attendance Check-In / Check-Out')
    company = get_company_by_id(company_id)
    office_lat = company.get('office_lat')
    office_lng = company.get('office_lng')
    office_radius = company.get('office_radius', 100)

    if not office_lat or not office_lng:
        st.warning("Your company has not set an office location yet. You cannot check-in via GPS.")
    else:
        subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}
        if not subject_options:
            st.info("You don't have any projects to check into.")
        else:
            selected_subject_label = st.selectbox('Select Project for Attendance', options=list(subject_options.keys()))
            selected_subject_id = subject_options[selected_subject_label]

            today_str = datetime.now().strftime("%Y-%m-%d")
            active_log = None
            for log in logs:
                if log['subject_id'] == selected_subject_id and log['timestamp'].startswith(today_str) and not log.get('checkout_time'):
                    active_log = log
                    break

            st.write("Click the button below to get your location:")
            location = streamlit_geolocation()

            if location and location.get('latitude') and location.get('longitude'):
                user_lat = location['latitude']
                user_lng = location['longitude']
                
                st.map(pd.DataFrame({"lat": [user_lat], "lon": [user_lng]}))
                
                dist = calculate_distance(user_lat, user_lng, office_lat, office_lng)
                inside_office = is_within_radius(user_lat, user_lng, office_lat, office_lng, office_radius)
                status_text = "Inside Office" if inside_office else "Outside Office"
                
                if inside_office:
                    st.success(f"Location Status: {status_text} ({dist:.1f} meters away)")
                else:
                    st.error(f"Location Status: {status_text} ({dist:.1f} meters away)")
                
                if not active_log:
                    if st.button("Check-In", type='primary', disabled=not inside_office):
                        employee_gps_checkin(employee_id, selected_subject_id, datetime.now().isoformat(), user_lat, user_lng, status_text)
                        st.success("Checked in successfully!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info(f"You checked in at {datetime.fromisoformat(active_log['timestamp']).strftime('%I:%M %p')}.")
                    if st.button("Check-Out", type='secondary'):
                        employee_gps_checkout(active_log['id'], datetime.now().isoformat())
                        st.success("Checked out successfully!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.info("Please allow location access to check in/out.")
            
    footer_dashboard()

def employee_screen():

    style_background_dashboard()
    style_base_layout()

    if "employee_data" in st.session_state:
        employee_dashboard()
        return
    
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    if "employee_login_tab" not in st.session_state:
        st.session_state.employee_login_tab = "login"

    tab1, tab2 = st.columns(2)
    with tab1:
        if st.button("Login via FaceID", type="primary" if st.session_state.employee_login_tab == "login" else "secondary", width="stretch"):
            st.session_state.employee_login_tab = "login"
            st.rerun()
    with tab2:
        if st.button("Register New Profile", type="primary" if st.session_state.employee_login_tab == "register" else "secondary", width="stretch"):
            st.session_state.employee_login_tab = "register"
            st.rerun()

    st.divider()

    if st.session_state.employee_login_tab == "login":
        st.header('Login using FaceID', text_alignment='center')
        st.space()
        
        photo_source = st.camera_input("Position your face in the center to login")

        if photo_source:
            img = np.array(Image.open(photo_source))

            with st.spinner('AI is scanning..'):
                detected, all_ids, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.warning('Face not found!')
                elif num_faces >1:
                    st.warning('Multiple faces found')
                else:
                    if detected:
                        employee_id = list(detected.keys())[0]
                        all_employees = get_all_employees()
                        employee = next((s for s in all_employees if s['employee_id']==employee_id), None)

                        if employee:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'employee'
                            st.session_state.employee_data = employee
                            st.toast(f"Welcome Back {employee['name']}")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error('Face not recognized! Please go to the Register tab if you are a new employee.')
                        
    else:
        st.header('Register new Profile')
        
        photo_source = st.camera_input("Take a clear photo for FaceID *")
        st.subheader('Optional : Voice Enrollment')
        st.info("Register for voice only attendance")
        audio_data = st.audio_input('Record a short phrase like I am present, My name is Akash.')
        
        with st.form("employee_register_form"):
            new_name = st.text_input("Enter your full name *", placeholder='E.g. Hamza Rizvi')
            employee_code = st.text_input("Enter your Employee Code *", placeholder="E.g. EMP-001")
            invite_code = st.text_input("Enter Company Invite Code *", placeholder="E.g. 8XYZ9A")

            submit_btn = st.form_submit_button('Create Account', type='primary')

        if submit_btn:
            new_name = new_name.strip() if new_name else ""
            employee_code = employee_code.strip() if employee_code else ""
            invite_code = invite_code.strip() if invite_code else ""
            
            if not photo_source:
                st.error("Please take a photo for FaceID registration.")
            elif new_name and employee_code and invite_code:
                company = get_company_by_invite_code(invite_code)
                if not company:
                    st.error("Invalid Company Invite Code! Please ask your administrator.")
                else:
                    with st.spinner('Creating profile..'):
                        img = np.array(Image.open(photo_source))
                        encodings= get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_employee(employee_code, new_name, company['id'], face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'employee'
                                st.session_state.employee_data = response_data[0]
                                st.toast(f"Profile Created! Hi {new_name}!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Couldnt capture your facial features for registration')
            else:
                st.warning('Please fill in all mandatory fields (Name, Employee Code, Invite Code)!')

    footer_dashboard()