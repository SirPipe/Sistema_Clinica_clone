# Sistema Clínica

Implementación base para las historias de usuario de **Clínica "Última Asignatura"**. Todo se almacena en una base de datos SQLite local (`app/db/clinic.sqlite3`).

## Contenido

- `app/clinic_db.py`: funciones para registrar pacientes, expedientes, consultas, citas, facturación, recetas e internaciones.
- `app/example_usage.py`: script de demostración que recorre el flujo principal y genera datos de ejemplo en la base de datos.

## Historias cubiertas

- CUA-HU-01/02/04/05/08: creación de expedientes y consultas con notas, diagnóstico y plan de tratamiento.
- CUA-HU-03: consulta del historial médico consolidado por paciente (`get_patient_history`).
- CUA-HU-06/07: registro de estudios de imagen y resultados de laboratorio.
- CUA-HU-09/10/15: programación, cancelación y reprogramación de citas.
- CUA-HU-11: generación de facturas y recibos de pago.
- CUA-HU-12/13: actualización de tratamientos y emisión de recetas.
- CUA-HU-14: registro de hospitalizaciones y altas médicas.

## Requisitos

- Python 3.11+ (incluye `sqlite3` en la librería estándar).

## Uso rápido

```bash
python -m app.clinic_db  # crea la base de datos vacía
python app/example_usage.py  # ejecuta el flujo de ejemplo y persiste datos
```

El script de ejemplo imprime el historial médico y la facturación del paciente de prueba para verificar que los datos quedan guardados.
