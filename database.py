import json
import uuid
from datetime import datetime

PATIENTS_FILE     = 'data/patients.json'
DOCTORS_FILE      = 'data/doctors.json'
APPOINTMENTS_FILE = 'data/appointments.json'
DIAGNOSES_FILE    = 'data/diagnoses.json'

def read_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def write_data(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# ── PATIENTS ──────────────────────────────────────────
def register_patient(name, age, email, password, blood_type, phone):
    patients = read_data(PATIENTS_FILE)
    for p in patients:
        if p['Email'] == email:
            return None, "Email already registered"
    patient = {
        "PatientID":      "P-" + str(uuid.uuid4())[:6].upper(),
        "Name":           name,
        "Age":            age,
        "Email":          email,
        "Password":       password,
        "BloodType":      blood_type,
        "Phone":          phone,
        "MedicalHistory": [],
        "RegisteredOn":   datetime.now().strftime("%Y-%m-%d")
    }
    patients.append(patient)
    write_data(PATIENTS_FILE, patients)
    return patient, "Success"

def login_patient(email, password):
    for p in read_data(PATIENTS_FILE):
        if p['Email'] == email and p['Password'] == password:
            return p
    return None

def get_patient_by_id(patient_id):
    for p in read_data(PATIENTS_FILE):
        if p['PatientID'] == patient_id:
            return p
    return None

# ── DOCTORS ───────────────────────────────────────────
def login_doctor(email, password):
    for d in read_data(DOCTORS_FILE):
        if d['Email'] == email and d['Password'] == password:
            return d
    return None

def get_all_doctors():
    return read_data(DOCTORS_FILE)

def get_doctor_by_id(doctor_id):
    for d in read_data(DOCTORS_FILE):
        if d['DoctorID'] == doctor_id:
            return d
    return None

# ── APPOINTMENTS ──────────────────────────────────────
def book_appointment(patient_id, doctor_id, date, time_slot, reason):
    appointments = read_data(APPOINTMENTS_FILE)
    appointment = {
        "AppointmentID": "APT-" + str(uuid.uuid4())[:6].upper(),
        "PatientID":     patient_id,
        "DoctorID":      doctor_id,
        "Date":          date,
        "TimeSlot":      time_slot,
        "Reason":        reason,
        "Status":        "Scheduled",
        "Diagnosis":     None,
        "BookedOn":      datetime.now().strftime("%Y-%m-%d")
    }
    appointments.append(appointment)
    write_data(APPOINTMENTS_FILE, appointments)
    return appointment

def get_patient_appointments(patient_id):
    result = []
    for apt in read_data(APPOINTMENTS_FILE):
        if apt['PatientID'] == patient_id:
            doctor = get_doctor_by_id(apt['DoctorID'])
            apt['DoctorName'] = doctor['Name'] if doctor else 'Unknown'
            apt['Specialization'] = doctor['Specialization'] if doctor else ''
            result.append(apt)
    return result

def get_doctor_appointments(doctor_id):
    result = []
    for apt in read_data(APPOINTMENTS_FILE):
        if apt['DoctorID'] == doctor_id:
            patient = get_patient_by_id(apt['PatientID'])
            apt['PatientName'] = patient['Name'] if patient else 'Unknown'
            apt['PatientAge']  = patient['Age'] if patient else ''
            result.append(apt)
    return result

# ── DIAGNOSES ─────────────────────────────────────────
def add_diagnosis(appointment_id, patient_id, doctor_id, condition, prescription, notes):
    diagnoses    = read_data(DIAGNOSES_FILE)
    appointments = read_data(APPOINTMENTS_FILE)
    diagnosis = {
        "DiagnosisID":   "DX-" + str(uuid.uuid4())[:6].upper(),
        "AppointmentID": appointment_id,
        "PatientID":     patient_id,
        "DoctorID":      doctor_id,
        "Condition":     condition,
        "Prescription":  prescription,
        "Notes":         notes,
        "Date":          datetime.now().strftime("%Y-%m-%d")
    }
    diagnoses.append(diagnosis)
    write_data(DIAGNOSES_FILE, diagnoses)
    for apt in appointments:
        if apt['AppointmentID'] == appointment_id:
            apt['Status']    = "Completed"
            apt['Diagnosis'] = condition
            break
    write_data(APPOINTMENTS_FILE, appointments)
    return diagnosis

def get_patient_diagnoses(patient_id):
    result = []
    for dx in read_data(DIAGNOSES_FILE):
        if dx['PatientID'] == patient_id:
            doctor = get_doctor_by_id(dx['DoctorID'])
            dx['DoctorName'] = doctor['Name'] if doctor else 'Unknown'
            result.append(dx)
    return result