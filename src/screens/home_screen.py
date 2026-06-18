import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():
    style_background_home()
    style_base_layout()
    header_home()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
            <div style="margin-bottom:8px;">
                <div style="font-size:2rem; margin-bottom:4px;">👤</div>
                <div style="font-family:'Inter',sans-serif; font-size:1.3rem;
                     font-weight:700; color:#fff; margin-bottom:6px;">Employee</div>
                <div style="font-family:'Inter',sans-serif; font-size:0.85rem;
                     color:rgba(255,255,255,0.55); line-height:1.5;">
                     Check in/out via GPS or Face ID.<br>View attendance & payslips.
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button('Employee Portal  →', type='primary',
                     use_container_width=True, key='emp_btn'):
            st.session_state['login_type'] = 'employee'
            st.rerun()

    with col2:
        st.markdown("""
            <div style="margin-bottom:8px;">
                <div style="font-size:2rem; margin-bottom:4px;">🏢</div>
                <div style="font-family:'Inter',sans-serif; font-size:1.3rem;
                     font-weight:700; color:#fff; margin-bottom:6px;">Company</div>
                <div style="font-family:'Inter',sans-serif; font-size:0.85rem;
                     color:rgba(255,255,255,0.55); line-height:1.5;">
                     Manage teams, projects & records.<br>AI-powered HR tools.
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button('Company Portal  →', type='primary',
                     use_container_width=True, key='comp_btn'):
            st.session_state['login_type'] = 'company'
            st.rerun()

    footer_home()