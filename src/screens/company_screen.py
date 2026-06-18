import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_company_exists, create_company, company_login, get_company_subjects, get_attendance_for_company, get_all_employees_for_company, update_company_location, get_leave_requests_for_company, update_leave_status, update_employee_designation, update_attendance_status, log_audit_action, update_employee_rate, get_audit_logs_for_company
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_share_subject import share_subject_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np

from datetime import datetime
import pandas as pd
import altair as alt
from fpdf import FPDF

from src.components.dialog_voice_attendance import voice_attendance_dialog

def company_screen():

    style_background_dashboard()
    style_base_layout()

    if "company_data" in st.session_state:
        company_dashboard()
    elif 'company_login_type' not in st.session_state or st.session_state.company_login_type=="login":
        company_screen_login()
    elif st.session_state.company_login_type == "register":
        company_screen_register()

def company_dashboard():
    company_data = st.session_state.company_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {company_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.company_data 
            st.rerun()

    # Custom HTML for Invite Code Box to match the reference image
    st.markdown(f"""
        <div style="background-color: #DDE2FC; padding: 20px; border-radius: 10px; margin-bottom: 20px; width: 100%;">
            <span style="font-weight: bold; color: #14258A; font-size: 16px;">Your Company Invite Code:</span> 
            <span style="color: #14258A; font-size: 16px;">{company_data['company_invite_code']}</span> 
            <span style="color: #14258A; font-size: 16px;">(Share this with your employees so they can join)</span>
        </div>
    """, unsafe_allow_html=True)

    # Simple native tabs — equal width, icons aligned, zero CSS fighting
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "📸 Attendance",
        "📋 Projects",
        "👥 Employees",
        "📁 Records",
        "⚙️ Settings",
        "🏖️ Leaves",
        "💰 Payroll",
        "🔍 Audit",
        "📊 Analytics",
        "⚖️ Overrides",
    ])

    with tab1:
        company_tab_take_attendance()
    with tab2:
        company_tab_manage_subjects()
    with tab3:
        company_tab_manage_employees()
    with tab4:
        company_tab_attendance_records()
    with tab5:
        company_tab_settings()
    with tab6:
        company_tab_leave_requests()
    with tab7:
        company_tab_payroll_preview()
    with tab8:
        company_tab_audit_logs()
    with tab9:
        company_tab_analytics()
    with tab10:
        company_tab_overrides()

    footer_dashboard()

def company_tab_overrides():
    st.header('Attendance Overrides (HR Review Queue)')
    company_id = st.session_state.company_data['company_id']
    from src.database.db import supabase
    
    st.info("Review attendance attempts that failed GPS or Facial Recognition verification.")
    
    # Fetch pending overrides
    response = supabase.table('attendance_overrides').select('*, verification_events(*)').eq('company_id', company_id).eq('status', 'Pending').execute()
    overrides = response.data
    
    if not overrides:
        st.success("No pending attendance overrides to review! Great job.")
        return
        
    for o in overrides:
        event = o.get('verification_events', {})
        with st.container(border=True):
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown(f"**Employee ID:** {o['employee_id']}")
                st.markdown(f"**Failed Step:** {event.get('step_name', 'Unknown')}")
                st.markdown(f"**Reason:** {event.get('failure_reason', 'N/A')}")
                st.caption(f"Event Time: {event.get('created_at')}")
            with col2:
                notes = st.text_input("HR Notes", key=f"notes_{o['id']}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Approve", key=f"app_ovr_{o['id']}", type="primary", use_container_width=True):
                        supabase.table('attendance_overrides').update({
                            'status': 'Approved',
                            'hr_notes': notes,
                            'reviewer_id': company_id,
                            'resolved_at': 'now()'
                        }).eq('id', o['id']).execute()
                        st.rerun()
                with c2:
                    if st.button("Reject", key=f"rej_ovr_{o['id']}", type="secondary", use_container_width=True):
                        supabase.table('attendance_overrides').update({
                            'status': 'Rejected',
                            'hr_notes': notes,
                            'reviewer_id': company_id,
                            'resolved_at': 'now()'
                        }).eq('id', o['id']).execute()
                        st.rerun()

from src.components.dialog_add_employee import add_employee_dialog

def company_tab_manage_employees():
    company_id = st.session_state.company_data['company_id']
    
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Employees')
    with col2:
        if st.button('Register New Employee', use_container_width=True, icon=':material/person_add:'):
            add_employee_dialog(company_id)
            
    employees = get_all_employees_for_company(company_id)
    if not employees:
        st.warning("No employees have joined your company yet. Register them above or share your Invite Code with them!")
        return
        
    df = pd.DataFrame(employees)
    if 'designation' not in df.columns:
        df['designation'] = 'Employee'
        
    display_df = df[['employee_id', 'employee_code', 'name', 'designation']]
    
    st.markdown("**Employee Directory (Edit Designations below)**")
    
    edited_df = st.data_editor(
        display_df,
        column_config={
            "employee_id": None, # Hide ID
            "employee_code": st.column_config.TextColumn("Employee Code", disabled=True),
            "name": st.column_config.TextColumn("Name", disabled=True),
            "designation": st.column_config.TextColumn("Designation", required=True)
        },
        hide_index=True,
        use_container_width=True,
        key="emp_editor"
    )
    
    if st.button("Save Designations", type="primary"):
        changes = 0
        for index, row in edited_df.iterrows():
            orig_row = display_df.iloc[index]
            if row['designation'] != orig_row['designation']:
                update_employee_designation(row['employee_id'], row['designation'])
                changes += 1
        if changes > 0:
            st.success(f"Updated {changes} designations!")
            time.sleep(1)
            st.rerun()
        else:
            st.info("No changes detected.")


def company_tab_take_attendance():
    company_id = st.session_state.company_data['company_id']
    st.header('Take AI Attendance')

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_company_subjects(company_id)

    if not subjects:
        st.warning('You havent created any projects yet! Please create one to begin!')
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Project', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', use_container_width=True):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, use_container_width=True, caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', use_container_width=True, type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button('Run Face Analysis', use_container_width=True, type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning meeting photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, num_faces = predict_attendance(img_np, company_id, selected_subject_id)
                    st.info(f"Debug Info for Photo {idx+1}: {num_faces} face(s) found in image. Matches: {detected}")

                    if detected:
                        for sid, data in detected.items():
                            student_id = int(sid)
                            score = data['similarity_score']
                            decision = data['decision']
                            from src.database.db import log_verification_event
                            
                            if decision == 'Review':
                                log_verification_event(student_id, company_id, 'Meeting Photo Scan', False, score, "Borderline face match in meeting photo")
                                all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1} (Flagged)")
                            elif decision == 'Accepted':
                                log_verification_event(student_id, company_id, 'Meeting Photo Scan', True, score)
                                all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                from src.database.db import get_enrolled_employees_for_subject
                company_employees = get_enrolled_employees_for_subject(selected_subject_id)

                if not company_employees:
                    st.warning('No employees assigned to this project!')
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for emp in company_employees:
                        sources = all_detected_ids.get(int(emp['employee_id']), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name": emp['name'],
                            "ID": emp['employee_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'employee_id': emp['employee_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', use_container_width=True, icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)

def company_tab_manage_subjects():
    company_id = st.session_state.company_data['company_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Projects')

    with col2:
        if st.button('Create New Project', use_container_width=True):
            create_subject_dialog(company_id)

    # LIST all SUBJECTS
    subjects = get_company_subjects(company_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🕰️", "Meetings", sub['total_classes']),
            ]
            
            def make_share_callback(sub_name, sub_code):
                def _callback():
                    if st.button('Share Project Link', key=f"share_{sub_code}", icon=':material/share:', use_container_width=True):
                        share_subject_dialog(sub_name, sub_code)
                return _callback
            
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats=stats,
                footer_callback=make_share_callback(sub['name'], sub['subject_code'])
            )
    else:
        st.info("NO PROJECTS FOUND. CREATE ONE ABOVE")

def generate_pdf_report(df, summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=16, style='B')
    pdf.cell(0, 10, text="Monthly Attendance Report", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font("helvetica", size=10)
    pdf.cell(0, 10, text=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT", align='C')
    
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("helvetica", size=10, style='B')
    col_widths = [35, 35, 45, 45, 30]
    df_columns = ['Check-In Time', 'Check-Out Time', 'Project', 'Employee', 'Status']
    display_headers = ['Check-In', 'Check-Out', 'Project', 'Employee', 'Status']
    for i, header in enumerate(display_headers):
        pdf.cell(col_widths[i], 10, text=str(header), border=1)
    pdf.ln(10)
    
    # Table Rows
    pdf.set_font("helvetica", size=9)
    for index, row in df.iterrows():
        for i, col in enumerate(df_columns):
            text = str(row[col])[:25] # Truncate to fit
            # Clean up text for FPDF compatibility
            text = text.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(col_widths[i], 10, text=text, border=1)
        pdf.ln(10)
        
    return bytes(pdf.output())

def company_tab_attendance_records():
    st.header('Attendance Records')

    company_id = st.session_state.company_data['company_id']

    records = get_attendance_for_company(company_id)

    if not records:
        st.info("No attendance records found yet. Once employees check in, they will appear here.")
        return
    
    data = []

    for r in records:
        ts = r.get('timestamp')
        check_out = r.get('checkout_time')
        
        data.append({
            "id": r.get('id'),
            "ts_group": ts.split(".")[0] if ts else None,
            "Check-In Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Check-Out Time": datetime.fromisoformat(check_out).strftime("%Y-%m-%d %I:%M %p") if check_out else "Still Active",
            "Project": r['subjects']['name'],
            "Employee": r['employee_name'],
            "is_present": bool(r.get('is_present', False)),
            "Status": r.get('location_status', 'Unknown')
        })

    df = pd.DataFrame(data)

    summary = (
        df.groupby(['ts_group', 'Check-In Time', 'Project'])
        .agg(
            Present_Count = ('is_present', 'sum'),
            Total_Count =('is_present', 'count')
        ).reset_index()

    )

    summary['Attendance Stats'] = (
        "✅ " + summary['Present_Count'].astype(str) + " / "
        + summary['Total_Count'].astype(str) + ' Employees'
    )

    display_df = ( df.sort_values(by='ts_group' ,ascending=False)
                  [['Check-In Time', 'Check-Out Time', 'Project', 'Employee', 'Status']]
                  )
                  
    st.subheader("Analytics Dashboard")
    
    total_records = len(display_df)
    total_present = df['is_present'].sum()
    total_absent = total_records - total_present
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Logs", total_records)
    m2.metric("Total Present", total_present)
    m3.metric("Total Absent", total_absent)
    
    st.space()
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Attendance by Project**")
        project_counts = df.groupby('Project')['is_present'].sum().reset_index()
        st.bar_chart(project_counts.set_index('Project'))
        
    with c2:
        st.markdown("**Overall Attendance Ratio**")
        pie_data = pd.DataFrame({
            "Status": ["Present", "Absent"],
            "Count": [total_present, total_absent]
        })
        pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
            theta="Count",
            color="Status",
            tooltip=["Status", "Count"]
        ).properties(height=300)
        st.altair_chart(pie_chart, use_container_width=True)
        
    st.divider()
    st.subheader("Detailed Records")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("Flagged Events & Overrides")
    flagged_df = df[(~df['is_present']) | (df['Status'] == 'Outside Office') | (df['Status'] == 'Unknown')]
    
    if flagged_df.empty:
        st.success("No flagged events found! All records seem normal.")
    else:
        st.warning(f"Found {len(flagged_df)} flagged record(s) requiring HR attention.")
        for idx, row in flagged_df.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{row['Employee']}** | Project: {row['Project']} | Check-in: {row['Check-In Time']}")
                    st.write(f"Status: `{row['Status']}` | Present: `{'Yes' if row['is_present'] else 'No'}`")
                with col2:
                    if st.button("Override Present", key=f"ov_pr_{row['id']}", type="primary"):
                        update_attendance_status(row['id'], True)
                        log_audit_action('override_attendance', st.session_state.company_data['company_id'], 'company', {'log_id': int(row['id']), 'is_present': True, 'employee': row['Employee']})
                        st.success("Overridden to Present!")
                        import time
                        time.sleep(1)
                        st.rerun()
                with col3:
                    if st.button("Override Absent", key=f"ov_ab_{row['id']}", type="secondary"):
                        update_attendance_status(row['id'], False)
                        log_audit_action('override_attendance', st.session_state.company_data['company_id'], 'company', {'log_id': int(row['id']), 'is_present': False, 'employee': row['Employee']})
                        st.warning("Overridden to Absent!")
                        import time
                        time.sleep(1)
                        st.rerun()
    
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name='attendance_records.csv',
            mime='text/csv',
            icon=':material/download:',
            type='secondary',
            use_container_width=True
        )
        
    with dl_col2:
        pdf_bytes_raw = generate_pdf_report(display_df, summary)
        
        # 3. Print the type of that variable for debugging
        print("DEBUG: Type of raw PDF data:", type(pdf_bytes_raw))
        
        # 4. If the variable is a bytearray, convert it to bytes
        if isinstance(pdf_bytes_raw, bytearray):
            download_data = bytes(pdf_bytes_raw)
            print("DEBUG: Converted bytearray to standard bytes.")
        else:
            download_data = pdf_bytes_raw
            
        print("DEBUG: Final type passed to button:", type(download_data))
        
        # 6. Update the download button (Keeping PDF mime instead of XLSX since it's a PDF generator)
        st.download_button(
            label="Download PDF Report",
            data=download_data,
            file_name='attendance_report.pdf',
            mime='application/pdf',
            icon=':material/picture_as_pdf:',
            type='primary',
            use_container_width=True
        )

def company_tab_settings():
    st.header('Office Site Management')
    company_data = st.session_state.company_data
    company_id = company_data['company_id']
    
    from src.database.db import get_offices_for_company, create_office, delete_office
    
    st.info("Manage all your office locations and geofences below.")
    
    # List existing offices
    offices = get_offices_for_company(company_id)
    
    if offices:
        st.subheader("Current Offices")
        for off in offices:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{off['office_name']}**")
                    st.write(f"Lat: {off['latitude']}, Lng: {off['longitude']} | Radius: {off['radius']}m")
                with col2:
                    if st.button("Delete", key=f"del_off_{off['id']}", type="secondary"):
                        delete_office(off['id'])
                        st.rerun()
                        
    st.divider()
    st.subheader("Add New Office")
    
    import folium
    from streamlit_folium import st_folium
    
    st.write("Click on the map to pin a new office location:")
    m = folium.Map(location=[15.775217, 77.483096], zoom_start=15)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=400, width=700, key="new_office_map")
    
    clicked_lat, clicked_lng = 0.0, 0.0
    if map_data and map_data.get('last_clicked'):
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']

    with st.form("add_office_form"):
        office_name = st.text_input("Office Name", placeholder="e.g. Headquarters")
        col1, col2, col3 = st.columns(3)
        with col1:
            lat = st.number_input("Latitude", value=float(clicked_lat), format="%.6f")
        with col2:
            lng = st.number_input("Longitude", value=float(clicked_lng), format="%.6f")
        with col3:
            radius = st.number_input("Geofence Radius (m)", value=100, step=10)
            
        submit = st.form_submit_button("Add Office", type="primary")
        if submit:
            if not office_name:
                st.error("Office name is required!")
            else:
                create_office(company_id, office_name, lat, lng, radius)
                st.success(f"Office '{office_name}' created successfully!")
                st.rerun()

def company_tab_analytics():
    st.header('HR Analytics Dashboard')
    company_id = st.session_state.company_data['company_id']
    from src.database.db import get_attendance_for_company
    records = get_attendance_for_company(company_id)
    
    if not records:
        st.info("Not enough data to display analytics.")
        return
        
    import pandas as pd
    import plotly.express as px
    
    df = pd.DataFrame(records)
    
    # KPI Cards
    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    today_records = df[df['timestamp'].str.startswith(today)] if not df.empty else pd.DataFrame()
    
    present_today = len(today_records)
    total_records = len(df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Present Today", present_today)
    col2.metric("Total Recorded Checks", total_records)
    
    # Simple Chart
    st.subheader("Attendance Over Time")
    df['date'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce').dt.date
    daily_counts = df.groupby('date').size().reset_index(name='counts')
    fig = px.line(daily_counts, x='date', y='counts', title='Daily Check-ins')
    st.plotly_chart(fig, use_container_width=True)

def company_tab_leave_requests():
    st.header('Leave Approvals')
    company_id = st.session_state.company_data['company_id']
    
    requests = get_leave_requests_for_company(company_id)
    if not requests:
        st.info("No leave requests found.")
        return
        
    for r in requests:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{r['employee_name']}** has requested leave from **{r['start_date']}** to **{r['end_date']}**")
                st.markdown(f"*Reason:* {r['reason']}")
            with col2:
                if r['status'] == 'Pending':
                    if st.button("Approve", key=f"app_{r['id']}", type="primary", use_container_width=True):
                        update_leave_status(r['id'], 'Approved')
                        st.rerun()
                    if st.button("Reject", key=f"rej_{r['id']}", type="secondary", use_container_width=True):
                        update_leave_status(r['id'], 'Rejected')
                        st.rerun()
                else:
                    status_icon = "✅" if r['status'] == 'Approved' else "❌"
                    st.markdown(f"**Status:** {status_icon} {r['status']}")


def login_company(username, password):
    username = username.strip() if username else ""
    password = password.strip() if password else ""

    if not username or not password:
        return False
    
    company = company_login(username, password)

    if company:
        st.session_state.user_role ='company'
        st.session_state.company_data = company
        st.session_state.is_logged_in = True
        return True
    
    return False

def company_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()

    with st.form("login_form"):
        company_username = st.text_input("Enter username", placeholder='ananyaroy')
        company_pass = st.text_input("Enter password", type='password', placeholder="Enter password")
        st.divider()
        submit_btn = st.form_submit_button('Login', icon=':material/passkey:', use_container_width=True)

    if submit_btn:
        if login_company(company_username, company_pass):
            st.toast("welcome back!", icon="👋")
            import time
            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid username and password combo")

    btnc1, btnc2 = st.columns(2)
    with btnc1:
        pass
        if st.button('Register Instead', type="primary", icon=':material/passkey:', use_container_width=True):
            st.session_state.company_login_type = 'register'

    footer_dashboard()

def register_company(company_username, company_name, company_pass, company_pass_confirm):
    company_username = company_username.strip() if company_username else ""
    company_name = company_name.strip() if company_name else ""
    company_pass = company_pass.strip() if company_pass else ""
    company_pass_confirm = company_pass_confirm.strip() if company_pass_confirm else ""

    if not company_username or not company_name or not company_pass:
        return False, "All Fields are required!"
    if check_company_exists(company_username):
        return False, "Username already taken"
    if company_pass != company_pass_confirm:
        return False, f"Password doesn't match"
    
    try:
        create_company(company_username, company_pass, company_name)
        return True, "Sucessfully Created! Login Now"
    except Exception as e:
        return False, f"Error: {str(e)}"
    
def company_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Register your company profile')

    st.space()
    st.space()
    
    with st.form("register_form"):
        company_username = st.text_input("Enter username", placeholder='ananyaroy')
        company_name = st.text_input("Enter name", placeholder='Ananya Roy')
        company_pass = st.text_input("Enter password", type='password', placeholder="Enter password")
        company_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

        st.divider()

        submit_btn = st.form_submit_button('Register now', icon=':material/passkey:', use_container_width=True)

    if submit_btn:
        success, message = register_company(company_username, company_name, company_pass, company_pass_confirm)
        if success:
            st.success(message)
            import time
            time.sleep(2)
            st.session_state.company_login_type = "login"
            st.rerun()
        else:
            st.error(message)

    btnc1, btnc2 = st.columns(2)
    with btnc1:
        pass # Empty to balance layout
    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', use_container_width=True):
            st.session_state.company_login_type = 'login'

    footer_dashboard()

def company_tab_payroll_preview():
    st.header('Payroll Preview')
    company_id = st.session_state.company_data['company_id']
    
    st.info("Calculate estimated payroll based on attendance records and employee daily rates.")
    
    employees = get_all_employees_for_company(company_id)
    if not employees:
        st.warning("No employees found.")
        return
        
    records = get_attendance_for_company(company_id)
    
    payroll_data = []
    
    for emp in employees:
        emp_id = emp['employee_id']
        daily_rate = float(emp.get('daily_rate', 1000.00) or 1000.00)
        
        # Count present days (unique dates where is_present is true)
        present_dates = set()
        for r in records:
            if r['employee_id'] == emp_id and r.get('is_present'):
                ts = r.get('timestamp')
                if ts:
                    date_str = ts.split("T")[0]
                    present_dates.add(date_str)
                    
        present_days = len(present_dates)
        estimated_pay = present_days * daily_rate
        
        payroll_data.append({
            "Employee ID": emp['employee_code'],
            "Name": emp['name'],
            "Designation": emp.get('designation', 'Employee'),
            "Daily Rate (₹)": daily_rate,
            "Present Days": present_days,
            "Estimated Payroll (₹)": estimated_pay
        })
        
    df = pd.DataFrame(payroll_data)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.dataframe(df, hide_index=True, use_container_width=True)
    with col2:
        st.metric("Total Estimated Payroll", f"₹ {df['Estimated Payroll (₹)'].sum():,.2f}")
        
    st.divider()
    st.subheader("Update Daily Rates")
    st.write("To update an employee's daily rate, enter the new rate below:")
    
    with st.form("update_rate_form"):
        emp_options = {f"{e['name']} ({e['employee_code']})": e['employee_id'] for e in employees}
        selected_emp = st.selectbox("Select Employee", options=list(emp_options.keys()))
        new_rate = st.number_input("New Daily Rate (₹)", min_value=0.0, value=1000.0, step=100.0)
        
        if st.form_submit_button("Update Rate", type="primary"):
            emp_id = emp_options[selected_emp]
            update_employee_rate(emp_id, new_rate)
            log_audit_action('update_daily_rate', company_id, 'company', {'employee_id': emp_id, 'new_rate': new_rate})
            st.success("Rate updated successfully!")
            import time
            time.sleep(1)
            st.rerun()

def company_tab_audit_logs():
    st.header('Audit Logs')
    company_id = st.session_state.company_data['company_id']
    
    st.info("Tracking sensitive HR actions and system events for security and compliance.")
    
    logs = get_audit_logs_for_company(company_id)
    if not logs:
        st.info("No audit logs found.")
        return
        
    log_data = []
    for log in logs:
        log_data.append({
            "Timestamp": datetime.fromisoformat(log['created_at'].split('.')[0]).strftime("%Y-%m-%d %H:%M:%S"),
            "Action": log['action_type'],
            "Role": log['user_role'],
            "User ID": log['user_id'],
            "Details": str(log['details'])
        })
        
    df = pd.DataFrame(log_data)
    st.dataframe(df, hide_index=True, use_container_width=True)