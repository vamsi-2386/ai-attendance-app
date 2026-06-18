import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_employees, create_employee, get_employee_attendance, get_company_subjects, get_company_by_invite_code, get_subjects_for_employee, get_company_by_id, employee_gps_checkin, employee_gps_checkout, create_leave_request, get_leave_requests_for_employee
from src.utils.location_utils import is_within_radius, calculate_distance, is_suspicious_location
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import pandas as pd
import time

from src.components.subject_card import subject_card
from src.components.dialog_enroll import enroll_dialog
from src.components.dialog_auto_enroll import auto_enroll_dialog
from src.components.dialog_unenroll import unenroll_dialog

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

    # Redesigned using tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard", 
        "📅 Attendance History", 
        "🏖️ Leave Management",
        "💰 Payroll & Payslips",
        "👤 My Profile"
    ])

    subjects = get_subjects_for_employee(employee_id)
    logs = get_employee_attendance(employee_id)
    company = get_company_by_id(company_id)

    with tab1:
        st.header('📍 GPS Attendance')

        from src.database.db import get_offices_for_company
        offices = get_offices_for_company(company_id)

        # Fallback to legacy single-office setup
        if not offices and company.get('office_lat') is not None:
            offices = [{'office_name': 'Main Office',
                        'latitude': company.get('office_lat'),
                        'longitude': company.get('office_lng'),
                        'radius': company.get('office_radius', 100)}]

        if not offices:
            st.warning("⚠️ Your company has not set an office location yet. Contact your administrator.")
        else:
            subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}
            if not subject_options:
                st.info("You don't have any projects to check into.")
            else:
                selected_subject_label = st.selectbox('Select Project', options=list(subject_options.keys()))
                selected_subject_id = subject_options[selected_subject_label]

                today_str = datetime.now().strftime("%Y-%m-%d")
                active_log = None
                for log in logs:
                    if log['subject_id'] == selected_subject_id and log['timestamp'].startswith(today_str) and not log.get('checkout_time'):
                        active_log = log
                        break

                # ── Office info card ──────────────────────────────
                off = offices[0]
                office_lat = float(off['latitude'])
                office_lng = float(off['longitude'])
                office_radius = int(off.get('radius', 100))

                st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#5865F2,#8A2BE2);
                                border-radius:16px; padding:16px 20px; margin-bottom:16px;
                                display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="color:rgba(255,255,255,0.7); font-size:0.75rem;
                                        text-transform:uppercase; letter-spacing:2px;">🏢 Office Location</div>
                            <div style="color:#fff; font-size:1.1rem; font-weight:700; margin-top:4px;">
                                {off.get('office_name','Main Office')}
                            </div>
                            <div style="color:rgba(255,255,255,0.8); font-size:0.85rem; margin-top:2px;">
                                📌 {office_lat:.6f}, {office_lng:.6f}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="color:rgba(255,255,255,0.7); font-size:0.75rem; text-transform:uppercase;">Geofence</div>
                            <div style="color:#fff; font-size:1.4rem; font-weight:900;">{office_radius}m</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # ── Get device location ───────────────────────────
                st.markdown("**📡 Get Your Device Location**")
                
                # Testing toggle for Desktop users
                st.info("💡 **Why am I in Hyderabad?** Desktop computers don't have GPS chips. Browsers fallback to your Internet Provider's location (which is often a major city like Hyderabad). To test real GPS, open this app on your mobile phone on the same Wi-Fi.")
                simulate_office = st.checkbox("🛠️ Simulate being inside Office (for testing on Desktop)")
                
                location = streamlit_geolocation()

                if simulate_office:
                    # Mock coordinates exactly inside the office
                    user_lat = office_lat
                    user_lng = office_lng
                    location = {'latitude': user_lat, 'longitude': user_lng}
                elif location and location.get('latitude') and location.get('longitude'):
                    user_lat = float(location['latitude'])
                    user_lng = float(location['longitude'])

                if location and location.get('latitude') and location.get('longitude'):
                    try:
                        dist = calculate_distance(user_lat, user_lng, office_lat, office_lng)
                        inside_office = is_within_radius(user_lat, user_lng, office_lat, office_lng, office_radius)
                        is_fake_gps = is_suspicious_location(location)
                        status_text = "Inside Office" if inside_office else "Outside Office"

                        # ── Coordinate comparison cards ───────────
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("📱 Your Latitude",  f"{user_lat:.6f}")
                        with c2:
                            st.metric("📱 Your Longitude", f"{user_lng:.6f}")
                        with c3:
                            st.metric("📏 Distance to Office", f"{dist:.1f} m",
                                      delta=f"{'✅ Inside' if inside_office else '❌ Outside'} {office_radius}m zone",
                                      delta_color="normal" if inside_office else "inverse")

                        # ── Folium map — both pins + geofence ring ─
                        import folium
                        from streamlit_folium import st_folium

                        mid_lat = (user_lat + office_lat) / 2
                        mid_lng = (user_lng + office_lng) / 2
                        m = folium.Map(location=[mid_lat, mid_lng], zoom_start=15)

                        # Office marker + geofence circle
                        folium.Marker(
                            [office_lat, office_lng],
                            tooltip=f"🏢 Office: {off.get('office_name','Main Office')}",
                            icon=folium.Icon(color='blue', icon='building', prefix='fa')
                        ).add_to(m)
                        folium.Circle(
                            [office_lat, office_lng],
                            radius=office_radius,
                            color='#5865F2', fill=True, fill_opacity=0.15,
                            tooltip=f"Geofence: {office_radius}m radius"
                        ).add_to(m)

                        # Device marker
                        folium.Marker(
                            [user_lat, user_lng],
                            tooltip=f"📱 You: {user_lat:.5f}, {user_lng:.5f}",
                            icon=folium.Icon(color='red', icon='user', prefix='fa')
                        ).add_to(m)

                        # Line between them
                        folium.PolyLine(
                            [[user_lat, user_lng], [office_lat, office_lng]],
                            color='#EB459E', weight=2, dash_array='6'
                        ).add_to(m)

                        st_folium(m, height=350, use_container_width=True)

                        # ── Status banner ─────────────────────────
                        if is_fake_gps:
                            st.error("🚨 Suspicious Location Detected — Mock GPS apps are not allowed.")
                        elif inside_office:
                            st.success(f"✅ You are **inside** the office geofence ({dist:.1f}m from office centre).")
                        else:
                            st.error(f"❌ You are **{dist:.1f} meters away** from the office. Move within {office_radius}m to check in.")

                        # ── Check-In / Check-Out buttons ──────────
                        st.markdown("---")
                        if not active_log:
                            if st.button("✅ Check-In", type='primary', use_container_width=True):
                                if (not inside_office) or is_fake_gps:
                                    reason = "Suspicious Location" if is_fake_gps else f"Outside Office ({dist:.1f}m away)"
                                    from src.database.db import log_verification_event
                                    log_verification_event(employee_id, company_id, 'GPS Check-In', False, 0.0, reason)
                                    employee_gps_checkin(employee_id, selected_subject_id, datetime.now().isoformat(), user_lat, user_lng, status_text, is_present=False)
                                    st.warning("⚠️ Check-in flagged for HR review — location outside geofence.")
                                else:
                                    from src.database.db import log_verification_event
                                    log_verification_event(employee_id, company_id, 'GPS Check-In', True, 1.0, "Verified Location")
                                    employee_gps_checkin(employee_id, selected_subject_id, datetime.now().isoformat(), user_lat, user_lng, status_text, is_present=True)
                                    st.success("✅ Checked in successfully!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.info(f"🕐 Checked in at **{datetime.fromisoformat(active_log['timestamp']).strftime('%I:%M %p')}**. Ready to check out?")
                            if st.button("🚪 Check-Out", type='secondary', use_container_width=True):
                                employee_gps_checkout(active_log['id'], datetime.now().isoformat())
                                st.success("✅ Checked out successfully!")
                                time.sleep(1)
                                st.rerun()

                    except (ValueError, TypeError) as e:
                        st.error(f"⚠️ GPS calculation error: {e}. Contact your administrator.")
                else:
                    st.info("📡 Click the button above to share your device location. Make sure location access is allowed in your browser.")

        st.divider()
        col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
        with col1:
            st.header('Your Company Projects')
        with col2:
            if st.button('Enroll in Project', icon=':material/add:', use_container_width=True, type='primary'):
                enroll_dialog()

        join_code = st.query_params.get('join-code')
        if join_code:
            auto_enroll_dialog(join_code)

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
                def make_unenroll_callback(name, s_id):
                    def _callback():
                        if st.button('Leave Project', key=f"leave_{s_id}", icon=':material/logout:', use_container_width=True):
                            unenroll_dialog(name, s_id)
                    return _callback

                subject_card(
                    name = sub['name'],
                    code = sub['subject_code'],
                    section = sub['section'],
                    stats = [
                        ('✅', 'Attended', stats['attended']),
                    ],
                    footer_callback=make_unenroll_callback(sub['name'], sub['subject_id'])
                )

    with tab2:
        st.header('Your Attendance Records')
        if not logs:
            st.info("No attendance records found.")
        else:
            data = []
            for r in logs:
                ts = r.get('timestamp')
                check_out = r.get('checkout_time')
                data.append({
                    "Date": ts.split("T")[0] if ts else "N/A",
                    "Check-In Time": datetime.fromisoformat(ts).strftime("%I:%M %p") if ts else "N/A",
                    "Check-Out Time": datetime.fromisoformat(check_out).strftime("%I:%M %p") if check_out else "Still Active",
                    "Project": r.get('subject_name', 'Unknown'),
                    "Status": "✅ Present" if r.get('is_present') else "❌ Absent",
                    "Location": r.get('location_status', 'N/A')
                })
                
            df = pd.DataFrame(data)
            display_df = df.sort_values(by=['Date', 'Check-In Time'], ascending=[False, False])
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    with tab3:
        from src.database.db import get_leave_balance
        balance = get_leave_balance(employee_id)
        st.metric("Annual Leave Balance", f"{balance} Days")
        employee_leave_portal(employee_id, company_id)

    with tab4:
        st.header('Payroll & Payslips')
        daily_rate = float(employee_data.get('daily_rate', 1000.00) or 1000.00)
        present_dates = set()
        for r in logs:
            if r.get('is_present'):
                ts = r.get('timestamp')
                if ts:
                    present_dates.add(ts.split("T")[0])
        present_days = len(present_dates)
        estimated_pay = present_days * daily_rate
        
        st.info("Your estimated payroll is based on your daily rate and recorded present days.")
        st.metric("Estimated Payroll (Current Period)", f"₹ {estimated_pay:,.2f}")
        
        if st.button("Generate Payslip (PDF)", type="primary"):
            st.warning("Payslip Generation requires an admin to finalize the payroll period first.")

    with tab5:
        st.header('Update Profile')
        with st.form("update_profile_form"):
            new_name = st.text_input("Full Name", value=employee_data['name'])
            
            if st.form_submit_button("Save Changes"):
                from src.database.db import supabase
                supabase.table('employees').update({'name': new_name}).eq('employee_id', employee_id).execute()
                st.session_state.employee_data['name'] = new_name
                st.success("Profile updated successfully!")
                time.sleep(1)
                st.rerun()

    footer_dashboard()

def employee_leave_portal(employee_id, company_id):
    st.header('Leave Management')
    
    with st.expander("Apply for Leave", expanded=False):
        with st.form("leave_form"):
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date")
                
            reason = st.text_area("Reason for Leave")
            submit = st.form_submit_button("Submit Leave Request", type="primary")
            
            if submit:
                if start_date > end_date:
                    st.error("End Date cannot be before Start Date!")
                elif not reason.strip():
                    st.error("Please provide a reason.")
                else:
                    create_leave_request(employee_id, company_id, start_date.isoformat(), end_date.isoformat(), reason.strip())
                    st.success("Leave request submitted successfully!")
                    time.sleep(1)
                    st.rerun()
                    
    st.subheader('Your Leave Requests')
    requests = get_leave_requests_for_employee(employee_id)
    if not requests:
        st.info("No leave requests found.")
    else:
        leave_data = []
        for r in requests:
            leave_data.append({
                "Applied On": datetime.fromisoformat(r['created_at'].split('.')[0]).strftime("%Y-%m-%d"),
                "Start Date": r['start_date'],
                "End Date": r['end_date'],
                "Reason": r['reason'],
                "Status": f"⏳ {r['status']}" if r['status'] == 'Pending' else (f"✅ {r['status']}" if r['status'] == 'Approved' else f"❌ {r['status']}")
            })
        st.dataframe(pd.DataFrame(leave_data), use_container_width=True, hide_index=True)

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
        if st.button("Login via FaceID", type="primary" if st.session_state.employee_login_tab == "login" else "secondary", use_container_width=True):
            st.session_state.employee_login_tab = "login"
            st.rerun()
    with tab2:
        if st.button("Register New Profile", type="primary" if st.session_state.employee_login_tab == "register" else "secondary", use_container_width=True):
            st.session_state.employee_login_tab = "register"
            st.rerun()

    st.divider()

    if st.session_state.employee_login_tab == "login":
        st.header('Login using FaceID', text_alignment='center')
        st.space()
        
        photo_source = st.camera_input("Position your face in the center to login")

        if photo_source:
            img = np.array(Image.open(photo_source).convert('RGB'))

            with st.spinner('AI is scanning..'):
                st.image(img, caption="Debug: Image sent to AI. Check if it's black or corrupted.")
                detected, all_ids, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.warning('Face not found!')
                elif num_faces >1:
                    st.warning('Multiple faces found')
                else:
                    if detected:
                        employee_id = list(detected.keys())[0]
                        score = detected[employee_id]['similarity_score']
                        decision = detected[employee_id]['decision']
                        
                        all_employees = get_all_employees()
                        employee = next((s for s in all_employees if s['employee_id']==employee_id), None)

                        if employee:
                            company_id = employee['company_id']
                            from src.database.db import log_verification_event
                            import base64
                            
                            if decision == 'Accepted':
                                photo_b64 = base64.b64encode(photo_source.getvalue()).decode('utf-8')
                                log_reason = f"photo:data:image/jpeg;base64,{photo_b64}"
                                log_verification_event(employee_id, company_id, 'FaceID Login', True, score, log_reason)
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'employee'
                                st.session_state.employee_data = employee
                                st.toast(f"Welcome Back {employee['name']}")
                                time.sleep(1)
                                st.rerun()
                            elif decision == 'Review':
                                log_verification_event(employee_id, company_id, 'FaceID Login', False, score, "Borderline face match")
                                st.warning('Identity match was borderline. A flagged event has been sent to your HR dashboard for manual review.')
                            else:
                                log_verification_event(employee_id, company_id, 'FaceID Login', False, score, "Low similarity score")
                                st.error('Face match score too low. Login blocked.')
                    else:
                        st.error('Face not recognized! Please go to the Register tab if you are a new employee.')
                        
    else:
        st.header('Register new Profile')
        
        if "consent_accepted" not in st.session_state:
            st.session_state.consent_accepted = False
            
        if not st.session_state.consent_accepted:
            st.subheader("Terms of Service & Biometric Consent")
            st.info("To use this service, we must collect and process a 128-dimensional mathematical vector representation of your face and/or voice. This biometric data is used exclusively for attendance verification. It will be securely encrypted and permanently deleted upon the termination of your employment, in accordance with GDPR and DPDP Act principles.")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("I Agree & Consent", type="primary", use_container_width=True):
                    st.session_state.consent_accepted = True
                    st.rerun()
            with c2:
                if st.button("I Decline", type="secondary", use_container_width=True):
                    st.session_state.employee_login_tab = "login"
                    st.rerun()
        else:
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
                            img = np.array(Image.open(photo_source).convert('RGB'))
                            st.image(img, caption="Debug: Image sent to AI during Registration")
                            encodings= get_face_embeddings(img)
                            if encodings:
                                face_emb = encodings[0].tolist()

                                voice_emb = None
                                if audio_data:
                                    voice_emb = get_voice_embedding(audio_data.read())

                                response_data = create_employee(employee_code, new_name, company['id'], face_embedding=face_emb, voice_embedding=voice_emb)

                                if response_data:
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