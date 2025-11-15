import sqlite3
from config import DATABASE_NAME

def init_db():
    """Initializes all database tables."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()

        # User Table (Central)
        c.execute("""
            CREATE TABLE IF NOT EXISTS User (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT CHECK(role IN ('doctor','patient','admin')) NOT NULL
            );
        """)

        # Doctor Table (Links to User)
        c.execute("""
            CREATE TABLE IF NOT EXISTS Doctor (
                doctor_id INTEGER PRIMARY KEY,
                specialization TEXT,
                FOREIGN KEY(doctor_id) REFERENCES User(user_id)
            );
        """)

        # Patient Table (Links to User)
        c.execute("""
            CREATE TABLE IF NOT EXISTS Patient (
                patient_id INTEGER PRIMARY KEY,
                address TEXT,
                phone TEXT,
                FOREIGN KEY(patient_id) REFERENCES User(user_id)
            );
        """)

        # Administrator Table (Links to User)
        c.execute("""
            CREATE TABLE IF NOT EXISTS Administrator (
                admin_id INTEGER PRIMARY KEY,
                FOREIGN KEY(admin_id) REFERENCES User(user_id)
            );
        """)

        # Appointment Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS Appointment (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_date TEXT NOT NULL,
                doctor_id INTEGER NOT NULL,
                patient_id INTEGER NOT NULL,
                FOREIGN KEY(doctor_id) REFERENCES Doctor(doctor_id),
                FOREIGN KEY(patient_id) REFERENCES Patient(patient_id)
            );
        """)

        # Medical Report Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS MedicalReport (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_details TEXT NOT NULL,
                report_date TEXT NOT NULL,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                FOREIGN KEY(patient_id) REFERENCES Patient(patient_id),
                FOREIGN KEY(doctor_id) REFERENCES Doctor(doctor_id)
            );
        """)

        # Billing Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS Billing (
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                patient_id INTEGER NOT NULL,
                details TEXT,
                FOREIGN KEY(patient_id) REFERENCES Patient(patient_id)
            );
        """)

        # Receipt Table (Links to Billing)
        c.execute("""
            CREATE TABLE IF NOT EXISTS Receipt (
                receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                bill_id INTEGER UNIQUE NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                FOREIGN KEY(bill_id) REFERENCES Billing(bill_id)
            );
        """)

        # Patient Registration Details Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS PatientRegistration (
                regn_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                patient_history TEXT,
                patient_id INTEGER UNIQUE NOT NULL,
                FOREIGN KEY(patient_id) REFERENCES Patient(patient_id)
            );
        """)
        
        conn.commit()
    print("Database initialized successfully.")


# --- Core Database Functions ---

def login(email, password):
    """Attempts to log a user in. Returns user info dict or None."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT user_id, role, name, password FROM User WHERE email=?", (email,))
        result = c.fetchone()
        
        if result:
            user_id, role, name, stored_password = result
            if stored_password == password:
                return {"user_id": user_id, "role": role, "name": name}
    return None

def add_user(conn, name, email, password, role, **kwargs):
    """
    specialization (for doctor)
    address, phone (for patient)
    """
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO User (name, email, password, role) VALUES (?, ?, ?, ?)",
                  (name, email, password, role))
        user_id = c.lastrowid
        
        if role == "doctor":
            spec = kwargs.get("specialization", "General")
            c.execute("INSERT INTO Doctor (doctor_id, specialization) VALUES (?, ?)", (user_id, spec))
        
        elif role == "patient":
            addr = kwargs.get("address", "N/A")
            ph = kwargs.get("phone", "N/A")
            c.execute("INSERT INTO Patient (patient_id, address, phone) VALUES (?, ?, ?)", (user_id, addr, ph))
        
        elif role == "admin":
            c.execute("INSERT INTO Administrator (admin_id) VALUES (?)", (user_id,))
            
        print(f"User '{name}' ({role}) created with ID: {user_id}")
        return user_id
        
    except sqlite3.IntegrityError:
        print(f"Error: Email '{email}' already exists.")
        return None

def add_patient_registration(conn, date, history, patient_id):
    """Adds details to the PatientRegistration table."""
    c = conn.cursor()
    c.execute("INSERT INTO PatientRegistration (date, patient_history, patient_id) VALUES (?, ?, ?)",
              (date, history, patient_id))
    print(f"Registration details added for patient ID: {patient_id}")

def add_appointment(conn, date, doctor_id, patient_id):
    """Adds a new appointment."""
    c = conn.cursor()
    c.execute("INSERT INTO Appointment (appointment_date, doctor_id, patient_id) VALUES (?, ?, ?)",
              (date, doctor_id, patient_id))
    print("Appointment added successfully.")

def add_medical_report(conn, details, date, patient_id, doctor_id):
    """Adds a new medical report."""
    c = conn.cursor()
    c.execute("INSERT INTO MedicalReport (report_details, report_date, patient_id, doctor_id) VALUES (?, ?, ?, ?)",
              (details, date, patient_id, doctor_id))
    print("Medical report added successfully.")

def add_billing(conn, amount, date, patient_id, details):
    """Adds a new bill for a patient."""
    c = conn.cursor()
    c.execute("INSERT INTO Billing (amount, date, patient_id, details) VALUES (?, ?, ?, ?)",
              (amount, date, patient_id, details))
    bill_id = c.lastrowid
    print(f"Bill #{bill_id} created for patient ID {patient_id} for ${amount}.")
    return bill_id

def add_receipt(conn, date, bill_id, payment_method):
    """Adds a receipt, marking a bill as paid."""
    c = conn.cursor()
    try:
        c.execute("INSERT INTO Receipt (date, bill_id, payment_method) VALUES (?, ?, ?)",
                  (date, bill_id, payment_method))
        print(f"Receipt created for Bill #{bill_id} via {payment_method}.")
    except sqlite3.IntegrityError:
        print(f"Error: Bill #{bill_id} has already been paid or does not exist.")

def get_doctors(conn):
    """Returns a list of all doctors."""
    c = conn.cursor()
    c.execute("""
        SELECT U.user_id, U.name, D.specialization 
        FROM User U
        JOIN Doctor D ON U.user_id = D.doctor_id
    """)
    return c.fetchall()

def get_patients(conn):
    """Returns a list of all patients."""
    c = conn.cursor()
    c.execute("""
        SELECT U.user_id, U.name, P.phone, P.address
        FROM User U
        JOIN Patient P ON U.user_id = P.patient_id
    """)
    return c.fetchall()

def get_appointments_by_doctor(conn, doctor_id):
    """Gets all appointments for a specific doctor."""
    c = conn.cursor()
    c.execute("""
        SELECT A.appointment_id, A.appointment_date, U.name AS patient_name, P.phone
        FROM Appointment A
        JOIN Patient P ON A.patient_id = P.patient_id
        JOIN User U ON P.patient_id = U.user_id
        WHERE A.doctor_id = ?
    """, (doctor_id,))
    return c.fetchall()

def get_appointments_by_patient(conn, patient_id):
    """Gets all appointments for a specific patient."""
    c = conn.cursor()
    c.execute("""
        SELECT A.appointment_id, A.appointment_date, U.name AS doctor_name, D.specialization
        FROM Appointment A
        JOIN Doctor D ON A.doctor_id = D.doctor_id
        JOIN User U ON D.doctor_id = U.user_id
        WHERE A.patient_id = ?
    """, (patient_id,))
    return c.fetchall()

def get_reports_by_patient(conn, patient_id):
    """Gets all medical reports for a specific patient."""
    c = conn.cursor()
    c.execute("""
        SELECT R.report_id, R.report_date, R.report_details, U.name AS doctor_name
        FROM MedicalReport R
        JOIN User U ON R.doctor_id = U.user_id
        WHERE R.patient_id = ?
    """, (patient_id,))
    return c.fetchall()

def get_unpaid_bills_by_patient(conn, patient_id):
    """Gets all bills for a patient that do not have a receipt."""
    c = conn.cursor()
    c.execute("""
        SELECT B.bill_id, B.date, B.details, B.amount
        FROM Billing B
        LEFT JOIN Receipt R ON B.bill_id = R.bill_id
        WHERE B.patient_id = ? AND R.receipt_id IS NULL
    """, (patient_id,))
    return c.fetchall()

def get_all_bills_by_patient(conn, patient_id):
    """Gets all bills for a patient, indicating if paid."""
    c = conn.cursor()
    c.execute("""
        SELECT B.bill_id, B.date, B.details, B.amount,
               CASE WHEN R.receipt_id IS NOT NULL THEN 'Paid' ELSE 'Unpaid' END AS status
        FROM Billing B
        LEFT JOIN Receipt R ON B.bill_id = R.bill_id
        WHERE B.patient_id = ?
    """, (patient_id,))
    return c.fetchall()

def update_patient_details(conn, patient_id, address, phone):
    """Updates a patient's address and phone."""
    c = conn.cursor()
    c.execute("UPDATE Patient SET address = ?, phone = ? WHERE patient_id = ?",
              (address, phone, patient_id))
    print("Patient details updated.")