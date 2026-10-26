"""
Clinical Database Service for Sehat Saathi
Provides relational clinical data storage (SQLite / Cloud SQL ready)
for treatment continuity by Doctors, Nurses, and PHC Healthcare Staff.
Complies with DISHA & ABDM guidelines for explicit patient consent and treatment traceability.
"""

import sqlite3
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from services.storage_config import get_data_dir

DEFAULT_DB_PATH = get_data_dir() / "sehat_saathi.db"


class ClinicalDatabaseService:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """
        Creates the relational clinical schema if it does not already exist.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users table (Patients, Doctors, Hospital Staff)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                google_id TEXT,
                email TEXT,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'patient',
                phone TEXT,
                abha_id TEXT,
                profile_pic TEXT,
                medical_license_no TEXT,
                specialization TEXT,
                hospital_clinic TEXT,
                qualification TEXT,
                staff_designation TEXT,
                employee_id TEXT,
                department_ward TEXT,
                age INTEGER,
                gender TEXT,
                blood_group TEXT,
                emergency_contact TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Dynamic column migration for existing database files
            cursor.execute("PRAGMA table_info(users)")
            existing_cols = {col["name"] for col in cursor.fetchall()}
            new_cols = {
                "medical_license_no": "TEXT",
                "specialization": "TEXT",
                "hospital_clinic": "TEXT",
                "qualification": "TEXT",
                "staff_designation": "TEXT",
                "employee_id": "TEXT",
                "department_ward": "TEXT",
                "age": "INTEGER",
                "gender": "TEXT",
                "blood_group": "TEXT",
                "emergency_contact": "TEXT",
                "address": "TEXT"
            }
            for col_name, col_type in new_cols.items():
                if col_name not in existing_cols:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")

            # 2. Patients table (Linked to user, holds medical profile & consent)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                blood_group TEXT,
                emergency_contact TEXT,
                consent_shared_treatment INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)

            # 3. Clinical Prescriptions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clinical_prescriptions (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                doctor_name TEXT,
                clinic_name TEXT,
                prescription_date TEXT,
                raw_text TEXT,
                verified_medicines_json TEXT,
                status TEXT DEFAULT 'confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
            """)

            # 4. Clinical Vitals Logs table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clinical_vitals (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                device_type TEXT,
                metric_name TEXT,
                value TEXT,
                unit TEXT,
                status_flag TEXT,
                alert_message TEXT,
                timestamp TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
            """)

            # 5. Medication Adherence table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clinical_adherence (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                medicine_name TEXT NOT NULL,
                dosage TEXT,
                timing TEXT,
                scheduled_time TEXT,
                taken_status INTEGER DEFAULT 0,
                taken_at TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
            """)

            # 6. Complication Risk Predictions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clinical_complications (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                risk_score REAL,
                risk_tier TEXT,
                systolic_bp REAL,
                diastolic_bp REAL,
                blood_sugar REAL,
                spo2 REAL,
                adherence_pct REAL,
                trajectory TEXT,
                model_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
            """)

            # 7. Staff Clinical Notes & Triage Observations table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clinical_staff_notes (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                staff_id TEXT,
                staff_name TEXT NOT NULL,
                staff_role TEXT NOT NULL,
                observation_notes TEXT NOT NULL,
                triage_status TEXT DEFAULT 'Normal',
                recommended_action TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
            """)

            # Create Indexes for fast clinical lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pat_user ON patients(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_presc_pat ON clinical_prescriptions(patient_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vitals_pat ON clinical_vitals(patient_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_pat ON clinical_staff_notes(patient_id)")

            conn.commit()

    # ---------------- User & Patient Management ----------------

    def upsert_user(self, user_dict: Dict[str, Any]) -> str:
        """
        Saves or updates a user profile with role-specific attributes.
        """
        user_id = user_dict.get("id") or str(uuid.uuid4())[:8]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (
                id, google_id, email, name, role, phone, abha_id, profile_pic,
                medical_license_no, specialization, hospital_clinic, qualification,
                staff_designation, employee_id, department_ward,
                age, gender, blood_group, emergency_contact, address
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                google_id=COALESCE(excluded.google_id, users.google_id),
                email=COALESCE(excluded.email, users.email),
                name=excluded.name,
                role=excluded.role,
                phone=excluded.phone,
                abha_id=excluded.abha_id,
                profile_pic=excluded.profile_pic,
                medical_license_no=excluded.medical_license_no,
                specialization=excluded.specialization,
                hospital_clinic=excluded.hospital_clinic,
                qualification=excluded.qualification,
                staff_designation=excluded.staff_designation,
                employee_id=excluded.employee_id,
                department_ward=excluded.department_ward,
                age=excluded.age,
                gender=excluded.gender,
                blood_group=excluded.blood_group,
                emergency_contact=excluded.emergency_contact,
                address=excluded.address
            """, (
                user_id,
                user_dict.get("google_id"),
                user_dict.get("email"),
                user_dict.get("name", "User"),
                user_dict.get("role", "patient"),
                user_dict.get("phone"),
                user_dict.get("abha_id"),
                user_dict.get("profile_pic", "👤"),
                user_dict.get("medical_license_no"),
                user_dict.get("specialization"),
                user_dict.get("hospital_clinic"),
                user_dict.get("qualification"),
                user_dict.get("staff_designation"),
                user_dict.get("employee_id"),
                user_dict.get("department_ward"),
                user_dict.get("age"),
                user_dict.get("gender"),
                user_dict.get("blood_group"),
                user_dict.get("emergency_contact"),
                user_dict.get("address")
            ))
            conn.commit()
        return user_id

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def upsert_patient(self, patient_dict: Dict[str, Any]) -> str:
        """
        Saves or updates a patient record.
        """
        pat_id = patient_dict.get("id") or str(uuid.uuid4())[:8]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO patients (id, user_id, name, age, gender, blood_group, emergency_contact, consent_shared_treatment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                age=excluded.age,
                gender=excluded.gender,
                blood_group=excluded.blood_group,
                emergency_contact=excluded.emergency_contact,
                consent_shared_treatment=excluded.consent_shared_treatment
            """, (
                pat_id,
                patient_dict.get("user_id"),
                patient_dict.get("name", "Unknown Patient"),
                patient_dict.get("age", 55),
                patient_dict.get("gender", "Unspecified"),
                patient_dict.get("blood_group", "B+"),
                patient_dict.get("emergency_contact", "108"),
                patient_dict.get("consent_shared_treatment", 1)
            ))
            conn.commit()
        return pat_id

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_patient_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_all_patients(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    # ---------------- Clinical Data Ingestion ----------------

    def save_prescription(
        self,
        patient_id: str,
        doctor_name: Optional[str],
        clinic_name: Optional[str],
        prescription_date: Optional[str],
        raw_text: Optional[str],
        verified_medicines: List[Dict[str, Any]]
    ) -> str:
        presc_id = str(uuid.uuid4())[:8]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO clinical_prescriptions (
                id, patient_id, doctor_name, clinic_name, prescription_date, raw_text, verified_medicines_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                presc_id,
                patient_id,
                doctor_name or "PHC Doctor",
                clinic_name or "Community Health Centre",
                prescription_date or datetime.now().strftime("%Y-%m-%d"),
                raw_text or "",
                json.dumps(verified_medicines, ensure_ascii=False)
            ))
            conn.commit()
        return presc_id

    def get_patient_prescriptions(self, patient_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM clinical_prescriptions WHERE patient_id = ? ORDER BY created_at DESC
            """, (patient_id,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                item = dict(r)
                try:
                    item["verified_medicines"] = json.loads(item.get("verified_medicines_json") or "[]")
                except Exception:
                    item["verified_medicines"] = []
                result.append(item)
            return result

    def save_vital(
        self,
        patient_id: str,
        device_type: str,
        metric_name: str,
        value: str,
        unit: str,
        status_flag: str,
        alert_message: Optional[str] = None
    ) -> str:
        vital_id = str(uuid.uuid4())[:8]
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO clinical_vitals (
                id, patient_id, device_type, metric_name, value, unit, status_flag, alert_message, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vital_id, patient_id, device_type, metric_name, value, unit, status_flag, alert_message, now_str
            ))
            conn.commit()
        return vital_id

    def get_patient_vitals(self, patient_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM clinical_vitals WHERE patient_id = ? ORDER BY timestamp DESC LIMIT ?
            """, (patient_id, limit))
            return [dict(r) for r in cursor.fetchall()]

    def record_adherence(
        self,
        patient_id: str,
        medicine_name: str,
        dosage: str,
        timing: str,
        scheduled_time: str,
        taken_status: bool = True
    ) -> str:
        log_id = str(uuid.uuid4())[:8]
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M") if taken_status else None
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO clinical_adherence (
                id, patient_id, medicine_name, dosage, timing, scheduled_time, taken_status, taken_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_id, patient_id, medicine_name, dosage, timing, scheduled_time, 1 if taken_status else 0, now_str
            ))
            conn.commit()
        return log_id

    def get_patient_adherence_rate(self, patient_id: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM clinical_adherence WHERE patient_id = ?", (patient_id,))
            total = cursor.fetchone()["total"]
            cursor.execute("SELECT COUNT(*) as taken FROM clinical_adherence WHERE patient_id = ? AND taken_status = 1", (patient_id,))
            taken = cursor.fetchone()["taken"]
            pct = int((taken / total) * 100) if total > 0 else 0
            return {"total_scheduled": total, "total_taken": taken, "percentage": pct}

    def save_complication_prediction(
        self,
        patient_id: str,
        risk_score: float,
        risk_tier: str,
        systolic_bp: float,
        diastolic_bp: float,
        blood_sugar: float,
        spo2: float,
        adherence_pct: float,
        trajectory: str,
        model_name: str
    ) -> str:
        pred_id = str(uuid.uuid4())[:8]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO clinical_complications (
                id, patient_id, risk_score, risk_tier, systolic_bp, diastolic_bp, blood_sugar, spo2, adherence_pct, trajectory, model_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pred_id, patient_id, risk_score, risk_tier, systolic_bp, diastolic_bp, blood_sugar, spo2, adherence_pct, trajectory, model_name
            ))
            conn.commit()
        return pred_id

    def get_latest_complication_prediction(self, patient_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM clinical_complications WHERE patient_id = ? ORDER BY created_at DESC LIMIT 1
            """, (patient_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # ---------------- Staff Clinical Notes & Triage ----------------

    def add_staff_clinical_note(
        self,
        patient_id: str,
        staff_id: Optional[str],
        staff_name: str,
        staff_role: str,
        observation_notes: str,
        triage_status: str = "Normal",
        recommended_action: Optional[str] = None
    ) -> str:
        note_id = str(uuid.uuid4())[:8]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO clinical_staff_notes (
                id, patient_id, staff_id, staff_name, staff_role, observation_notes, triage_status, recommended_action
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                note_id, patient_id, staff_id or "staff", staff_name, staff_role, observation_notes, triage_status, recommended_action
            ))
            conn.commit()
        return note_id

    def get_staff_clinical_notes(self, patient_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM clinical_staff_notes WHERE patient_id = ? ORDER BY created_at DESC
            """, (patient_id,))
            return [dict(r) for r in cursor.fetchall()]

    # ---------------- Treatment Summary Export (ABDM / PHC) ----------------

    def export_patient_clinical_summary(self, patient_id: str) -> Dict[str, Any]:
        """
        Builds a comprehensive treatment summary formatted for Doctors, Nurses, and PHC EHR records.
        """
        patient = self.get_patient(patient_id)
        if not patient:
            return {"error": "Patient not found"}

        prescriptions = self.get_patient_prescriptions(patient_id)
        vitals = self.get_patient_vitals(patient_id, limit=10)
        adherence = self.get_patient_adherence_rate(patient_id)
        pred = self.get_latest_complication_prediction(patient_id)
        notes = self.get_staff_clinical_notes(patient_id)

        return {
            "record_type": "SehatSaathi_Clinical_Treatment_Card",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "patient_profile": {
                "id": patient["id"],
                "name": patient["name"],
                "age": patient["age"],
                "gender": patient["gender"],
                "blood_group": patient["blood_group"],
                "consent_shared_treatment": bool(patient["consent_shared_treatment"])
            },
            "active_prescriptions_count": len(prescriptions),
            "recent_prescriptions": prescriptions[:3],
            "recent_vitals": vitals,
            "adherence_summary": adherence,
            "ai_complication_prediction": pred,
            "staff_treatment_notes": notes,
            "compliance_notice": "DISHA & ABDM Treatment Continuity Standard. Strictly assistive medical record."
        }
