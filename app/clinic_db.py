"""
Clinic database helper covering core user stories.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

DB_FILE = Path(__file__).resolve().parent / "db" / "clinic.sqlite3"


@dataclass
class Appointment:
    id: int
    patient_id: int
    scheduled_for: str
    scheduled_by: int
    appointment_time: str
    status: str
    reason: Optional[str]


@contextmanager
def db_cursor():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        yield conn.cursor()
        conn.commit()


def init_schema() -> None:
    """Create tables if they do not exist."""
    with db_cursor() as cur:
        cur.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                contact TEXT
            );
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                document_id TEXT,
                birthdate TEXT,
                contact TEXT,
                emergency_contact TEXT,
                insurance_info TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id),
                created_by INTEGER REFERENCES staff(id),
                summary TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL REFERENCES medical_records(id),
                performed_by INTEGER REFERENCES staff(id),
                notes TEXT,
                diagnosis TEXT,
                treatment_plan TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS imaging_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL REFERENCES medical_records(id),
                description TEXT,
                report TEXT,
                image_path TEXT,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS lab_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL REFERENCES medical_records(id),
                test_name TEXT,
                result TEXT,
                performed_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL REFERENCES medical_records(id),
                medication TEXT NOT NULL,
                dosage TEXT,
                duration TEXT,
                instructions TEXT,
                prescribed_by INTEGER REFERENCES staff(id),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id),
                scheduled_by INTEGER REFERENCES staff(id),
                scheduled_for INTEGER REFERENCES staff(id),
                appointment_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'scheduled',
                reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS billing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id),
                appointment_id INTEGER REFERENCES appointments(id),
                total NUMERIC NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                billing_id INTEGER NOT NULL REFERENCES billing(id),
                amount NUMERIC NOT NULL,
                method TEXT,
                paid_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS hospitalizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id),
                attending_id INTEGER REFERENCES staff(id),
                room TEXT,
                bed TEXT,
                start_date TEXT DEFAULT CURRENT_TIMESTAMP,
                end_date TEXT,
                notes TEXT
            );
            """
        )


def register_staff(name: str, role: str, contact: str | None = None) -> int:
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO staff (name, role, contact) VALUES (?, ?, ?)",
            (name, role, contact),
        )
        return cur.lastrowid


def register_patient(
    full_name: str,
    document_id: str | None = None,
    birthdate: str | None = None,
    contact: str | None = None,
    emergency_contact: str | None = None,
    insurance_info: str | None = None,
) -> int:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO patients (full_name, document_id, birthdate, contact, emergency_contact, insurance_info)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (full_name, document_id, birthdate, contact, emergency_contact, insurance_info),
        )
        return cur.lastrowid


def create_medical_record(patient_id: int, created_by: int, summary: str | None = None) -> int:
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO medical_records (patient_id, created_by, summary) VALUES (?, ?, ?)",
            (patient_id, created_by, summary),
        )
        return cur.lastrowid


def add_consultation(
    record_id: int,
    performed_by: int,
    notes: str,
    diagnosis: str | None = None,
    treatment_plan: str | None = None,
) -> int:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO consultations (record_id, performed_by, notes, diagnosis, treatment_plan)
            VALUES (?, ?, ?, ?, ?)
            """,
            (record_id, performed_by, notes, diagnosis, treatment_plan),
        )
        return cur.lastrowid


def add_imaging_result(record_id: int, description: str, report: str, image_path: str | None = None) -> int:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO imaging_results (record_id, description, report, image_path)
            VALUES (?, ?, ?, ?)
            """,
            (record_id, description, report, image_path),
        )
        return cur.lastrowid


def add_lab_result(record_id: int, test_name: str, result: str, performed_at: Optional[str] = None) -> int:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO lab_results (record_id, test_name, result, performed_at)
            VALUES (?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
            """,
            (record_id, test_name, result, performed_at),
        )
        return cur.lastrowid


def add_prescription(
    record_id: int,
    medication: str,
    dosage: str,
    duration: str,
    instructions: str,
    prescribed_by: int,
) -> int:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO prescriptions (record_id, medication, dosage, duration, instructions, prescribed_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (record_id, medication, dosage, duration, instructions, prescribed_by),
        )
        return cur.lastrowid


def record_appointment(
    patient_id: int,
    scheduled_by: int,
    scheduled_for: int,
    appointment_time: datetime,
    reason: str | None = None,
) -> int:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO appointments (patient_id, scheduled_by, scheduled_for, appointment_time, reason)
            VALUES (?, ?, ?, ?, ?)
            """,
            (patient_id, scheduled_by, scheduled_for, appointment_time.isoformat(), reason),
        )
        return cur.lastrowid


def update_appointment_status(appointment_id: int, status: str) -> None:
    with db_cursor() as cur:
        cur.execute(
            "UPDATE appointments SET status = ? WHERE id = ?",
            (status, appointment_id),
        )


def cancel_appointment(appointment_id: int) -> None:
    """Mark an appointment as cancelled."""
    update_appointment_status(appointment_id, "cancelled")


def reschedule_appointment(appointment_id: int, new_time: datetime) -> None:
    with db_cursor() as cur:
        cur.execute(
            "UPDATE appointments SET appointment_time = ?, status = 'rescheduled' WHERE id = ?",
            (new_time.isoformat(), appointment_id),
        )


def create_bill(patient_id: int, appointment_id: int | None, total: float) -> int:
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO billing (patient_id, appointment_id, total) VALUES (?, ?, ?)",
            (patient_id, appointment_id, total),
        )
        return cur.lastrowid


def record_payment(billing_id: int, amount: float, method: str) -> int:
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO payments (billing_id, amount, method) VALUES (?, ?, ?)",
            (billing_id, amount, method),
        )
        cur.execute(
            "UPDATE billing SET status = CASE WHEN (SELECT SUM(amount) FROM payments WHERE billing_id = ?) >= total THEN 'paid' ELSE status END WHERE id = ?",
            (billing_id, billing_id),
        )
        return cur.lastrowid


def register_hospitalization(
    patient_id: int,
    attending_id: int,
    room: str,
    bed: str,
    start_date: datetime | None = None,
    notes: str | None = None,
) -> int:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO hospitalizations (patient_id, attending_id, room, bed, start_date, notes)
            VALUES (?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), ?)
            """,
            (patient_id, attending_id, room, bed, start_date.isoformat() if start_date else None, notes),
        )
        return cur.lastrowid


def discharge_patient(hospitalization_id: int, end_date: datetime | None = None, notes: str | None = None) -> None:
    with db_cursor() as cur:
        cur.execute(
            "UPDATE hospitalizations SET end_date = COALESCE(?, CURRENT_TIMESTAMP), notes = COALESCE(?, notes) WHERE id = ?",
            (end_date.isoformat() if end_date else None, notes, hospitalization_id),
        )


def get_patient_history(patient_id: int) -> List[sqlite3.Row]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT mr.id AS record_id, mr.created_at, mr.summary, c.notes, c.diagnosis, c.treatment_plan
            FROM medical_records mr
            LEFT JOIN consultations c ON c.record_id = mr.id
            WHERE mr.patient_id = ?
            ORDER BY mr.created_at DESC, c.created_at DESC
            """,
            (patient_id,),
        )
        return cur.fetchall()


def list_patient_appointments(patient_id: int, include_cancelled: bool = False) -> List[Appointment]:
    clause = "" if include_cancelled else " WHERE status != 'cancelled'"
    with db_cursor() as cur:
        cur.execute(
            f"SELECT * FROM appointments{clause} AND patient_id = ?" if clause else "SELECT * FROM appointments WHERE patient_id = ?",
            (patient_id,),
        )
        return [
            Appointment(
                id=row["id"],
                patient_id=row["patient_id"],
                scheduled_for=row["scheduled_for"],
                scheduled_by=row["scheduled_by"],
                appointment_time=row["appointment_time"],
                status=row["status"],
                reason=row["reason"],
            )
            for row in cur.fetchall()
        ]


def get_billing_summary(patient_id: int) -> Iterable[sqlite3.Row]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT b.id, b.total, b.status, b.created_at, IFNULL(SUM(p.amount), 0) AS paid
            FROM billing b
            LEFT JOIN payments p ON p.billing_id = b.id
            WHERE b.patient_id = ?
            GROUP BY b.id
            ORDER BY b.created_at DESC
            """,
            (patient_id,),
        )
        return cur.fetchall()


if __name__ == "__main__":
    init_schema()
    print(f"Database initialized at {DB_FILE}")
