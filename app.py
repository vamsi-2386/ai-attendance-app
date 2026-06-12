
import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.company_screen import company_screen
from src.screens.employee_screen import employee_screen
from src.database.init_db import init_db

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

main()