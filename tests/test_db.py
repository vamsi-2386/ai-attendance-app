"""
Comprehensive unit tests for the SQLite database layer (db.py).
Covers: company registration, login, duplicate detection, employee management,
subject creation, enrollment/unenrollment, attendance logging, and edge cases.
"""

import unittest
import os
import sys
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import src.database.config as config
import src.database.init_db as init_mod

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'test_app.db')


def get_db():
    """Import all db functions (after config path is patched)."""
    from src.database import db
    return db


class TestDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.DB_PATH = TEST_DB_PATH
        init_mod.DB_PATH = TEST_DB_PATH

    def setUp(self):
        """Re-initialise schema and wipe all rows before every test."""
        init_mod.init_db()
        conn = sqlite3.connect(TEST_DB_PATH)
        conn.executescript("""
            DELETE FROM attendance_logs;
            DELETE FROM subject_employees;
            DELETE FROM subjects;
            DELETE FROM employees;
            DELETE FROM companys;
        """)
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        try:
            if os.path.exists(TEST_DB_PATH):
                os.remove(TEST_DB_PATH)
        except PermissionError:
            pass

    # ------------------------------------------------------------------ helpers
    def _make_company(self, uname='co1'):
        db = get_db()
        db.create_company(uname, 'pw', 'Co')
        return db.company_login(uname, 'pw')['company_id']

    def _make_employee(self, name='Emp1'):
        db = get_db()
        return db.create_employee(name)[0]['employee_id']

    # ------------------------------------------------------------------ company

    def test_company_not_exists_initially(self):
        self.assertFalse(get_db().check_company_exists('acme'))

    def test_company_creation_sets_flag(self):
        db = get_db()
        db.create_company('acme', 'secret', 'Acme Corp')
        self.assertTrue(db.check_company_exists('acme'))

    def test_company_login_success(self):
        db = get_db()
        db.create_company('alpha', 'mypass', 'Alpha Inc')
        result = db.company_login('alpha', 'mypass')
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], 'alpha')
        self.assertIn('company_id', result)

    def test_company_login_wrong_password(self):
        db = get_db()
        db.create_company('beta', 'correctpass', 'Beta LLC')
        self.assertIsNone(db.company_login('beta', 'wrongpass'))

    def test_company_login_nonexistent_user(self):
        self.assertIsNone(get_db().company_login('ghost', 'pass'))

    def test_duplicate_company_raises_integrity_error(self):
        db = get_db()
        db.create_company('dupco', 'pass', 'Dup')
        with self.assertRaises(sqlite3.IntegrityError):
            db.create_company('dupco', 'pass2', 'Dup2')

    def test_company_password_is_hashed(self):
        db = get_db()
        db.create_company('hashco', 'plaintextpw', 'Hash Co')
        conn = sqlite3.connect(TEST_DB_PATH)
        row = conn.execute(
            "SELECT password FROM companys WHERE username='hashco'"
        ).fetchone()
        conn.close()
        self.assertNotEqual(row[0], 'plaintextpw')

    def test_sql_injection_in_username(self):
        db = get_db()
        result = db.check_company_exists("' OR '1'='1")
        self.assertFalse(result)

    # ------------------------------------------------------------------ employee

    def test_create_employee_basic(self):
        db = get_db()
        res = db.create_employee('Alice')
        self.assertEqual(res[0]['name'], 'Alice')
        employees = db.get_all_employees()
        self.assertEqual(len(employees), 1)

    def test_create_employee_with_embeddings(self):
        db = get_db()
        face = [0.1, 0.2, 0.3]
        voice = [0.9, 0.8]
        db.create_employee('Bob', face, voice)
        emp = db.get_all_employees()[0]
        self.assertEqual(emp['face_embedding'], face)
        self.assertEqual(emp['voice_embedding'], voice)

    def test_employee_no_embeddings_returns_none(self):
        db = get_db()
        db.create_employee('Charlie')
        emp = db.get_all_employees()[0]
        self.assertIsNone(emp['face_embedding'])
        self.assertIsNone(emp['voice_embedding'])

    def test_multiple_employees(self):
        db = get_db()
        db.create_employee('Dave')
        db.create_employee('Eve')
        self.assertEqual(len(db.get_all_employees()), 2)

    def test_embedding_large_vector_round_trip(self):
        """512-float embedding must survive JSON serialization round-trip."""
        db = get_db()
        big = [round(i * 0.001, 5) for i in range(512)]
        db.create_employee('LargeVec', big, None)
        emp = db.get_all_employees()[0]
        self.assertEqual(emp['face_embedding'], big)

    # ------------------------------------------------------------------ subjects

    def test_create_and_retrieve_subject(self):
        db = get_db()
        cid = self._make_company()
        db.create_subject('CS101', 'Intro CS', 'A', cid)
        subjects = db.get_company_subjects(cid)
        self.assertEqual(len(subjects), 1)
        self.assertEqual(subjects[0]['name'], 'Intro CS')
        self.assertEqual(subjects[0]['total_employees'], 0)
        self.assertEqual(subjects[0]['total_classes'], 0)

    def test_no_subjects_for_unknown_company(self):
        self.assertEqual(get_db().get_company_subjects(9999), [])

    # ------------------------------------------------------------------ enrollment

    def test_enroll_and_get_subjects(self):
        db = get_db()
        cid = self._make_company()
        eid = self._make_employee()
        db.create_subject('ENG1', 'English', 'B', cid)
        sid = db.get_company_subjects(cid)[0]['subject_id']

        db.enroll_employee_to_subject(eid, sid)

        e_subs = db.get_employee_subjects(eid)
        self.assertEqual(len(e_subs), 1)
        self.assertEqual(e_subs[0]['subjects']['subject_code'], 'ENG1')

        c_subs = db.get_company_subjects(cid)
        self.assertEqual(c_subs[0]['total_employees'], 1)

    def test_double_enrollment_silently_ignored(self):
        db = get_db()
        cid = self._make_company()
        eid = self._make_employee()
        db.create_subject('MATH1', 'Math', 'A', cid)
        sid = db.get_company_subjects(cid)[0]['subject_id']

        db.enroll_employee_to_subject(eid, sid)
        db.enroll_employee_to_subject(eid, sid)  # Must NOT raise

        conn = sqlite3.connect(TEST_DB_PATH)
        count = conn.execute(
            "SELECT COUNT(*) FROM subject_employees WHERE employee_id=? AND subject_id=?",
            (eid, sid)
        ).fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)

    def test_unenroll_removes_from_list(self):
        db = get_db()
        cid = self._make_company()
        eid = self._make_employee()
        db.create_subject('PHY1', 'Physics', 'C', cid)
        sid = db.get_company_subjects(cid)[0]['subject_id']

        db.enroll_employee_to_subject(eid, sid)
        self.assertEqual(len(db.get_employee_subjects(eid)), 1)
        db.unenroll_employee_to_subject(eid, sid)
        self.assertEqual(len(db.get_employee_subjects(eid)), 0)

    def test_unenroll_nonexistent_does_not_raise(self):
        get_db().unenroll_employee_to_subject(9999, 9999)  # Must NOT raise

    # ------------------------------------------------------------------ attendance

    def test_log_and_retrieve_attendance(self):
        db = get_db()
        cid = self._make_company()
        eid = self._make_employee('AttEmp')
        db.create_subject('BIO1', 'Biology', 'A', cid)
        sid = db.get_company_subjects(cid)[0]['subject_id']
        db.enroll_employee_to_subject(eid, sid)

        db.create_attendance([
            {'employee_id': eid, 'subject_id': sid,
             'timestamp': '2024-01-10T09:00:00', 'is_present': True}
        ])

        emp_att = db.get_employee_attendance(eid)
        self.assertEqual(len(emp_att), 1)
        self.assertTrue(emp_att[0]['is_present'])

        comp_att = db.get_attendance_for_company(cid)
        self.assertEqual(len(comp_att), 1)
        self.assertEqual(comp_att[0]['subjects']['name'], 'Biology')

    def test_absent_flag_stored_correctly(self):
        db = get_db()
        cid = self._make_company()
        eid = self._make_employee('AbsEmp')
        db.create_subject('CHM1', 'Chemistry', 'A', cid)
        sid = db.get_company_subjects(cid)[0]['subject_id']
        db.enroll_employee_to_subject(eid, sid)

        db.create_attendance([
            {'employee_id': eid, 'subject_id': sid,
             'timestamp': '2024-01-11T09:00:00', 'is_present': False}
        ])
        emp_att = db.get_employee_attendance(eid)
        self.assertFalse(emp_att[0]['is_present'])

    def test_class_count_counts_distinct_sessions(self):
        db = get_db()
        cid = self._make_company()
        eid = self._make_employee('ClassEmp')
        db.create_subject('HIS1', 'History', 'A', cid)
        sid = db.get_company_subjects(cid)[0]['subject_id']
        db.enroll_employee_to_subject(eid, sid)

        db.create_attendance([
            {'employee_id': eid, 'subject_id': sid,
             'timestamp': '2024-01-12T09:00:00', 'is_present': True},
            {'employee_id': eid, 'subject_id': sid,
             'timestamp': '2024-01-13T09:00:00', 'is_present': False},
        ])

        subjects = db.get_company_subjects(cid)
        self.assertEqual(subjects[0]['total_classes'], 2)

    def test_empty_attendance_for_new_employee(self):
        db = get_db()
        eid = self._make_employee('NoAttEmp')
        self.assertEqual(db.get_employee_attendance(eid), [])

    def test_empty_attendance_for_unknown_company(self):
        self.assertEqual(get_db().get_attendance_for_company(9999), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
