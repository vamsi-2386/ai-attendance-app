from src.database.config import supabase
from datetime import datetime
import json

def log_audit_action(action_type: str, user_id: int, user_role: str, details: dict):
    """
    Logs an action to the audit_logs table for compliance and security monitoring.
    """
    try:
        data = {
            'action_type': action_type,
            'user_id': user_id,
            'user_role': user_role,
            'details': details,
            'created_at': datetime.utcnow().isoformat()
        }
        supabase.table('audit_logs').insert(data).execute()
    except Exception as e:
        print(f"Failed to log audit action: {e}")

def log_verification_event(employee_id: int, step_name: str, pass_fail: bool, score: float = None, failure_reason: str = None, device_id: str = None):
    """
    Logs a step in the attendance verification pipeline.
    """
    try:
        data = {
            'employee_id': employee_id,
            'step_name': step_name,
            'pass_fail': pass_fail,
            'score': score,
            'failure_reason': failure_reason,
            'device_id': device_id,
            'created_at': datetime.utcnow().isoformat()
        }
        return supabase.table('verification_events').insert(data).execute()
    except Exception as e:
        print(f"Failed to log verification event: {e}")
