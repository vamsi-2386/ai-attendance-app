# FlowX HRMS Integration Guide

This document outlines the integration points between the AI Attendance Prototype and the FlowX HRMS.

## Webhooks / API Endpoints Needed

To achieve real-time synchronization between this attendance system and FlowX, the following integrations should be built in Phase 4.5:

### 1. Attendance Sync
- **Trigger**: When an employee successfully checks in or HR overrides an attendance record.
- **Payload Shape** (FlowX-like format):
  ```json
  {
    "event_type": "attendance.logged",
    "employee_code": "EMP-001",
    "timestamp": "2026-06-15T10:50:34Z",
    "status": "Present",
    "source": "AI_Camera",
    "liveness_verified": true,
    "gps_verified": true,
    "location": {
      "lat": 20.5937,
      "lng": 78.9629
    }
  }
  ```

### 2. Leave Request Sync
- **Trigger**: When a leave request is created, approved, or rejected in the prototype.
- **Payload Shape**:
  ```json
  {
    "event_type": "leave.status_updated",
    "employee_code": "EMP-001",
    "leave_id": 102,
    "start_date": "2026-06-20",
    "end_date": "2026-06-22",
    "reason": "Medical",
    "status": "Approved",
    "approved_by": "HR-Admin"
  }
  ```

### 3. Employee Roster Sync
- **Trigger**: FlowX pushes new employee profiles to the attendance database, or vice versa when a new FaceID is registered.
- **Payload Shape**:
  ```json
  {
    "event_type": "employee.created",
    "employee_code": "EMP-001",
    "name": "Hamza Rizvi",
    "designation": "Software Engineer",
    "daily_rate": 1500.00,
    "status": "Active"
  }
  ```

## Security & Hardening
- **Authentication**: All API requests should be authenticated using an API Key and standard OAuth2 M2M (Machine-to-Machine) tokens.
- **Audit Logs**: The system logs every manual override and daily rate change in the `audit_logs` table. This table can be pulled periodically by FlowX for compliance.
