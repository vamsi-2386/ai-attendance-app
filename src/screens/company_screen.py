import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_company_exists, create_company, company_login, get_company_subjects, get_attendance_for_company, get_all_employees_for_company, update_company_location
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np

from datetime import datetime
import pandas as pd

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

    st.info(f"**Your Company Invite Code:** `{company_data['company_invite_code']}` (Share this with your employees so they can join)")
    st.space()

    if "current_company_tab" not in st.session_state:
        st.session_state.current_company_tab = 'take_attendance'
    tab1, tab2, tab3, tab4, tab5 = st.columns(5)

    with tab1:
        type1 = "primary" if st.session_state.current_company_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance',type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_company_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_company_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Projects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_company_tab = 'manage_subjects'
            st.rerun()
            
    with tab3:
        type3 = "primary" if st.session_state.current_company_tab == 'manage_employees' else "tertiary"
        if st.button('Employees', type=type3, width='stretch', icon=':material/group:'):
            st.session_state.current_company_tab = 'manage_employees'
            st.rerun()

    with tab4:
        type4 = "primary" if st.session_state.current_company_tab == 'attendance_records' else "tertiary"
        if st.button('Records',type=type4, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_company_tab = 'attendance_records'
            st.rerun()
            
    with tab5:
        type5 = "primary" if st.session_state.current_company_tab == 'settings' else "tertiary"
        if st.button('Settings',type=type5, width='stretch', icon=':material/settings:'):
            st.session_state.current_company_tab = 'settings'
            st.rerun()

    st.divider()

    if st.session_state.current_company_tab == "take_attendance":
        company_tab_take_attendance()
    if st.session_state.current_company_tab == "manage_subjects":
        company_tab_manage_subjects()
    if st.session_state.current_company_tab == "manage_employees":
        company_tab_manage_employees()
    if st.session_state.current_company_tab == "attendance_records":
        company_tab_attendance_records()
    if st.session_state.current_company_tab == "settings":
        company_tab_settings()

    footer_dashboard()

from src.components.dialog_add_employee import add_employee_dialog

def company_tab_manage_employees():
    company_id = st.session_state.company_data['company_id']
    
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Employees')
    with col2:
        if st.button('Register New Employee', width='stretch', icon=':material/person_add:'):
            add_employee_dialog(company_id)
            
    employees = get_all_employees_for_company(company_id)
    if not employees:
        st.warning("No employees have joined your company yet. Register them above or share your Invite Code with them!")
        return
        
    df = pd.DataFrame(employees)
    display_df = df[['employee_code', 'name']]
    display_df.columns = ['Employee Code', 'Name']
    st.dataframe(display_df, width='stretch', hide_index=True)


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
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning meeting photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np, company_id, selected_subject_id)

                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
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
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)

def company_tab_manage_subjects():
    company_id = st.session_state.company_data['company_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Projects', width='stretch')

    with col2:
        if st.button('Create New Project', width='stretch'):
            create_subject_dialog(company_id)

    # LIST all SUBJECTS
    subjects = get_company_subjects(company_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🕰️", "Meetings", sub['total_classes']),
            ]
            
            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats=stats
            )
    else:
        st.info("NO PROJECTS FOUND. CREATE ONE ABOVE")

def company_tab_attendance_records():
    st.header('Attendance Records')

    company_id = st.session_state.company_data['company_id']

    records = get_attendance_for_company(company_id)

    if not records:
        return
    
    data = []

    for r in records:
        ts = r.get('timestamp')
        check_out = r.get('checkout_time')
        
        data.append({
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
    
    st.dataframe(display_df, width='stretch', hide_index=True)

def company_tab_settings():
    st.header('Company Settings')
    company_data = st.session_state.company_data
    company_id = company_data['company_id']

    st.subheader('Office Location for GPS Tracking')
    st.info("Set your office coordinates to allow employees to check-in via GPS. Employees must be within the specified radius to successfully check-in.")
    
    with st.form("office_location_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            lat = st.number_input("Office Latitude", value=float(company_data.get('office_lat', 0.0) or 0.0), format="%.6f")
        with col2:
            lng = st.number_input("Office Longitude", value=float(company_data.get('office_lng', 0.0) or 0.0), format="%.6f")
        with col3:
            radius = st.number_input("Allowed Radius (meters)", value=int(company_data.get('office_radius', 100) or 100), step=10)
            
        submit = st.form_submit_button("Save Location Settings", type="primary")
        
        if submit:
            update_company_location(company_id, lat, lng, radius)
            # Update session state
            st.session_state.company_data['office_lat'] = lat
            st.session_state.company_data['office_lng'] = lng
            st.session_state.company_data['office_radius'] = radius
            st.success("Office location updated successfully!")


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
        submit_btn = st.form_submit_button('Login', icon=':material/passkey:', width='stretch')

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
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
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
        return False, "Unexpected Error!"
    
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

        submit_btn = st.form_submit_button('Register now', icon=':material/passkey:', width='stretch')

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
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.company_login_type = 'login'

    footer_dashboard()