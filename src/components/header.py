"""
header.py — Lumenor AI Attendance Platform
Logo is baked as a base64 constant — no file I/O at runtime.
"""
import streamlit as st
from src.components._logo_const import LUMENOR_DATA_URI


def header_home():
    """Centered Lumenor logo + wordmark for home screen."""
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center;
                    justify-content:center; padding:2rem 0 0.75rem 0;">
            <img src="{LUMENOR_DATA_URI}"
                 style="width:96px; height:auto; object-fit:contain;
                        border-radius:20px;
                        box-shadow:0 8px 32px rgba(0,0,0,0.4), 0 0 0 2px rgba(255,255,255,0.15);
                        background:#fff; padding:6px;" />
            <div style="margin-top:14px; text-align:center;">
                <div style="font-family:'Inter','Segoe UI',sans-serif;
                            font-size:1.6rem; font-weight:900; color:#fff;
                            letter-spacing:4px; line-height:1;">LUMENOR</div>
                <div style="font-family:'Inter','Segoe UI',sans-serif;
                            font-size:0.7rem; color:rgba(255,255,255,0.5);
                            letter-spacing:3px; text-transform:uppercase;
                            margin-top:4px;">AI Attendance Platform</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def header_dashboard():
    """Compact Lumenor logo for dashboard header."""
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px;
                    padding:0.25rem 0 0.5rem 0;">
            <img src="{LUMENOR_DATA_URI}"
                 style="width:48px; height:auto; object-fit:contain;
                        image-rendering: crisp-edges;" />
            <div>
                <div style="font-family:'Inter','Segoe UI',sans-serif;
                            font-size:1.1rem; font-weight:900; color:#1e1b4b;
                            letter-spacing:3px; line-height:1;">LUMENOR</div>
                <div style="font-family:'Inter','Segoe UI',sans-serif;
                            font-size:0.58rem; color:#6d28d9; letter-spacing:2px;
                            text-transform:uppercase; font-weight:600;">AI Attendance</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
