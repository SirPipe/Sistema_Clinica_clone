"""
Small driver to exercise clinic_db helpers to persist data in SQLite.
"""
from datetime import datetime, timedelta

from clinic_db import (
    add_consultation,
    add_imaging_result,
    add_lab_result,
    add_prescription,
    create_bill,
    create_medical_record,
    discharge_patient,
    get_billing_summary,
    get_patient_history,
    init_schema,
    record_appointment,
    record_payment,
    register_hospitalization,
    register_patient,
    register_staff,
    reschedule_appointment,
    update_appointment_status,
)


if __name__ == "__main__":
    init_schema()

    receptionist_id = register_staff("Ana Torres", "recepcionista")
    doctor_id = register_staff("Dr. Rivera", "medico")

    patient_id = register_patient(
        "Carlos Ruiz",
        document_id="ABC123",
        birthdate="1980-05-06",
        contact="carlos@example.com",
        emergency_contact="Lucia Ruiz",
    )

    record_id = create_medical_record(patient_id, doctor_id, summary="Paciente con dolor lumbar crónico")

    consultation_id = add_consultation(
        record_id,
        performed_by=doctor_id,
        notes="Dolor en zona lumbar, movilidad limitada",
        diagnosis="Lumbalgia",
        treatment_plan="Fisioterapia y analgésicos",
    )

    add_imaging_result(record_id, description="Radiografía lumbar", report="Sin fracturas")
    add_lab_result(record_id, "Hemograma", "Valores dentro de rango")
    add_prescription(
        record_id,
        medication="Ibuprofeno",
        dosage="400mg",
        duration="7 días",
        instructions="Tomar cada 8 horas con alimentos",
        prescribed_by=doctor_id,
    )

    appointment_id = record_appointment(
        patient_id,
        scheduled_by=receptionist_id,
        scheduled_for=doctor_id,
        appointment_time=datetime.now() + timedelta(days=1),
        reason="Revisión y plan de tratamiento",
    )

    reschedule_appointment(appointment_id, datetime.now() + timedelta(days=2))
    update_appointment_status(appointment_id, "confirmada")

    bill_id = create_bill(patient_id, appointment_id, total=120.0)
    record_payment(bill_id, amount=60.0, method="tarjeta")
    record_payment(bill_id, amount=60.0, method="efectivo")

    hospitalization_id = register_hospitalization(
        patient_id,
        attending_id=doctor_id,
        room="101",
        bed="A",
        notes="Monitoreo por dolor agudo",
    )
    discharge_patient(hospitalization_id, notes="Estable, continuar terapia física")

    print("Historial médico:")
    for row in get_patient_history(patient_id):
        print(dict(row))

    print("\nFacturación:")
    for row in get_billing_summary(patient_id):
        print(dict(row))

    print("\nDatos almacenados en la base de datos SQLite.")
