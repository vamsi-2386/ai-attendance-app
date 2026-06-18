import streamlit as st
from PIL import Image

from src.screens.home_screen import home_screen
from src.screens.company_screen import company_screen
from src.screens.employee_screen import employee_screen


def main():
    st.set_page_config(
        page_title='Lumenor — AI Attendance Platform',
        page_icon='🟣',          # emoji icon — no file dependency
        layout="centered",
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