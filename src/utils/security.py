import streamlit as st
from functools import wraps
import time

def require_role(allowed_roles: list):
    """
    Decorator to enforce Role-Based Access Control on Streamlit pages/functions.
    Usage: @require_role(['company', 'admin'])
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine the user's role from session state
            user_role = None
            if 'company_data' in st.session_state and st.session_state.company_data:
                user_role = 'company' # Or extract 'role' if admins are implemented
            elif 'employee_data' in st.session_state and st.session_state.employee_data:
                user_role = st.session_state.employee_data.get('role', 'employee')
                
            if user_role not in allowed_roles:
                st.error(f"Access Denied. Your role '{user_role}' does not have permission to view this section.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit(key: str, max_calls: int, period_seconds: int):
    """
    Simple rate limiting for Streamlit buttons or actions using session state.
    """
    state_key = f"rate_limit_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = []
        
    now = time.time()
    # Filter out old calls
    st.session_state[state_key] = [t for t in st.session_state[state_key] if now - t < period_seconds]
    
    if len(st.session_state[state_key]) >= max_calls:
        return False # Rate limit exceeded
        
    # Add new call
    st.session_state[state_key].append(now)
    return True
