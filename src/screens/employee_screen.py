import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_employees, create_employee, get_employee_subjects, get_employee_attendance, unenroll_employee_to_subject
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card

def employee_dashboard():
    employee_data = st.session_state.employee_data
    employee_id = employee_data['employee_id']
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

    c1, c2 =st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()


    st.divider()


    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_employee_subjects(employee_id)
        logs = get_employee_attendance(employee_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1


    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']


        stats = stats_map.get(sid,{"total":0, "attended": 0} )
        def unenroll_button():
                if st.button("Unenroll from tihs course", type='tertiary', width='stretch', icon=':material/delete_forever:'):
                    unenroll_employee_to_subject(employee_id, sid)
                    st.toast(f'Unenrolled from {sub['name']} successfully!')
                    st.rerun()

        with cols[i % 2]:

            subject_card(
                name = sub['name'],
                code =sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=unenroll_button
            )
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

    st.header('Login using FaceID', text_alignment='center')
    st.space()
    st.space()
    
    show_registration = False
    photo_source = st.camera_input("Position your face in the center")

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
                        st.toast(f'Welcome Back {employee['name']}')
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info('Face not recognized! You might be a new employee!')
                    show_registration = True
    if show_registration:
        with st.container(border=True):
            st.header('Register new Profile')
            new_name = st.text_input("Enter your name", placeholder='E.g. Hamza Rizvi')

            st.subheader('Optional : Voice Enrollment')
            st.info("Enroll your for voice only attendance")


            audio_data = None

            try:
                audio_data = st.audio_input('Record a short phrase like I am present, My name is Akash.')
            except Exception:
                st.error('Audio Data failed!')

            if st.button('Create Account', type='primary'):
                if new_name:
                    with st.spinner('Creating profile..'):
                        img = np.array(Image.open(photo_source))
                        encodings= get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_employee(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'employee'
                                st.session_state.employee_data = response_data[0]
                                st.toast(f'Profile Created! Hi {new_name}!')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Couldnt capture your facial features for registration')

                else:
                    st.warning('Please enter your name!')


        
    footer_dashboard()