import streamlit as st


def footer_home():
    st.markdown("""
        <div style="margin-top:2.5rem; display:flex; justify-content:center; align-items:center;">
            <p style="font-size:0.8rem; color:rgba(255,255,255,0.45); letter-spacing:2px; text-transform:uppercase;">
                Lumenor Enterprise &nbsp;·&nbsp; AI Attendance Platform
            </p>
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    st.markdown("""
        <div style="margin-top:3rem; padding-top:1.5rem; border-top: 1px solid rgba(0,0,0,0.08);
                    display:flex; justify-content:center; align-items:center;">
            <p style="font-size:0.8rem; color:#94a3b8; letter-spacing:2px; text-transform:uppercase;">
                Lumenor Enterprise &nbsp;·&nbsp; AI Attendance Platform
            </p>
        </div>
    """, unsafe_allow_html=True)
