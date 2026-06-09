
import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.company_screen import company_screen
from src.screens.employee_screen import employee_screen
from src.database.init_db import init_db

from src.components.dialog_auto_enroll import auto_enroll_dialog

def main():
    init_db()
    st.set_page_config(
        page_title='SnapClass - Making Attendance faster using AI',
        page_icon= "https://i.ibb.co/YTYGn5qV/logo.png"
    )
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'company':
            company_screen()

        case 'employee':
            employee_screen()
        
        case None:
            home_screen()


    join_code = st.query_params.get('join-code')
    if join_code:
        if st.session_state.login_type != 'employee':
            st.session_state.login_type = 'employee'
            st.rerun()
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'employee':
            auto_enroll_dialog(join_code)
main()