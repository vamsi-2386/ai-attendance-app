import streamlit as st
from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.db import get_enrolled_employees_for_subject
from src.components.dialog_attendance_results import show_attendance_result
import pandas as pd
from datetime import datetime


@st.dialog('Voice Attendance')
def voice_attendance_dialog(selected_subject_id):
    st.write('Record audio of employees saying "I am present". The AI will recognize them.')

    audio_data = st.audio_input("Record classroom audio")

    if st.button('Analyze Audio', width='stretch', type='primary'):
        with st.spinner('Processing audio data...'):
            enrolled_employees = get_enrolled_employees_for_subject(selected_subject_id)

            if not enrolled_employees:
                st.warning('No employees enrolled in this course')
                return

            candidates_dict = {
                emp['employee_id']: emp['voice_embedding']
                for emp in enrolled_employees if emp.get('voice_embedding')
            }

            if not candidates_dict:
                st.error('No enrolled employees have voice profiles registered')
                return

            audio_bytes = audio_data.read()
            detected_scores = process_bulk_audio(audio_bytes, candidates_dict)

            results, attendance_to_log = [], []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for emp in enrolled_employees:
                score = detected_scores.get(emp['employee_id'], 0.0)
                is_present = bool(score > 0)

                results.append({
                    "Name": emp['name'],
                    "ID": emp['employee_id'],
                    "Score": score if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    'employee_id': emp['employee_id'],
                    'subject_id': selected_subject_id,
                    'timestamp': current_timestamp,
                    'is_present': bool(is_present)
                })

            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)
