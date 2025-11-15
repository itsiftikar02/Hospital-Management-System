import sqlite3
from datetime import datetime
from config import DATABASE_NAME
from utils import get_int_input, get_date_input
from db import (
    add_appointment, get_appointments_by_doctor, add_medical_report, get_doctors,
    get_appointments_by_patient, get_reports_by_patient, get_all_bills_by_patient,
    get_unpaid_bills_by_patient, add_receipt, update_patient_details, add_user,
    add_billing, get_patients, add_patient_registration
)

def doctor_menu(user):
    """Menu for logged-in doctors."""
    print(f"\n--- Welcome Dr. {user['name']} (Doctor) ---")
    with sqlite3.connect(DATABASE_NAME) as conn:
        while True:
            print("\n[Doctor Menu]")
            print("1. View My Appointments")
            print("2. Add Medical Report for Patient")
            print("3. Logout")
            choice = get_int_input("Enter choice: ")

            if choice == 1:
                # View Appointments
                print("\n-- My Appointments --")
                appts = get_appointments_by_doctor(conn, user['user_id'])
                if not appts:
                    print("You have no upcoming appointments.")
                else:
                    for appt in appts:
                        print(f"ID: {appt[0]} | Date: {appt[1]} | Patient: {appt[2]} (Phone: {appt[3]})")
            
            elif choice == 2:
                # Add Medical Report
                print("\n-- Add Medical Report --")
                patient_id = get_int_input("Enter Patient ID: ")
                report_date = get_date_input("Enter Report Date (YYYY-MM-DD): ")
                details = input("Enter Report Details: ")
                
                try:
                    add_medical_report(conn, details, report_date, patient_id, user['user_id'])
                    conn.commit()
                except sqlite3.IntegrityError:
                    print(f"Error: Patient ID {patient_id} does not exist.")

            elif choice == 3:
                print("Logging out...")
                break
            else:
                print("Invalid choice. Try again.")

def patient_menu(user):
    """Menu for logged-in patients."""
    print(f"\n--- Welcome {user['name']} (Patient) ---")
    with sqlite3.connect(DATABASE_NAME) as conn:
        while True:
            print("\n[Patient Menu]")
            print("1. Book Appointment")
            print("2. View My Appointments")
            print("3. View My Medical Reports")
            print("4. View My Bills")
            print("5. Pay Bill")
            print("6. Update My Profile")
            print("7. Logout")
            choice = get_int_input("Enter choice: ")

            if choice == 1:
                # Book Appointment
                print("\n-- Book Appointment --")
                print("Available Doctors:")
                doctors = get_doctors(conn)
                for doc in doctors:
                    print(f"ID: {doc[0]} | Name: Dr. {doc[1]} | Specialization: {doc[2]}")
                
                doctor_id = get_int_input("Enter Doctor ID: ")
                date = get_date_input("Enter Desired Date (YYYY-MM-DD): ")
                try:
                    add_appointment(conn, date, doctor_id, user['user_id'])
                    conn.commit()
                except sqlite3.IntegrityError:
                    print(f"Error: Doctor ID {doctor_id} does not exist.")

            elif choice == 2:
                # View My Appointments
                print("\n-- My Appointments --")
                appts = get_appointments_by_patient(conn, user['user_id'])
                if not appts:
                    print("You have no appointments.")
                else:
                    for appt in appts:
                        print(f"ID: {appt[0]} | Date: {appt[1]} | Doctor: Dr. {appt[2]} ({appt[3]})")
            
            elif choice == 3:
                # View My Medical Reports
                print("\n-- My Medical Reports --")
                reports = get_reports_by_patient(conn, user['user_id'])
                if not reports:
                    print("You have no medical reports.")
                else:
                    for r in reports:
                        print(f"ID: {r[0]} | Date: {r[1]} | Doctor: Dr. {r[3]}\nDetails: {r[2]}\n---")
            
            elif choice == 4:
                # View My Bills
                print("\n-- My Bills --")
                bills = get_all_bills_by_patient(conn, user['user_id'])
                if not bills:
                    print("You have no bills on file.")
                else:
                    for b in bills:
                        print(f"ID: {b[0]} | Date: {b[1]} | Amount: ${b[3]:.2f} | Status: {b[4]}\nDetails: {b[2]}\n---")

            elif choice == 5:
                # Pay Bill
                print("\n-- Pay Bill --")
                bills = get_unpaid_bills_by_patient(conn, user['user_id'])
                if not bills:
                    print("You have no outstanding bills to pay.")
                    continue
                
                print("Your unpaid bills:")
                for b in bills:
                    print(f"ID: {b[0]} | Date: {b[1]} | Details: {b[2]} | Amount: ${b[3]:.2f}")
                
                bill_id = get_int_input("Enter Bill ID to pay: ")
                # Check if the entered ID is valid
                if bill_id not in [b[0] for b in bills]:
                    print("Invalid Bill ID.")
                    continue

                pay_date = get_date_input("Enter Payment Date (YYYY-MM-DD): ")
                method = input("Enter Payment Method (e.g., Credit Card, Cash): ")
                add_receipt(conn, pay_date, bill_id, method)
                conn.commit()
                print(f"Bill #{bill_id} paid successfully.")

            elif choice == 6:
                # Update My Profile
                print("\n-- Update My Profile --")
                address = input("Enter new address: ")
                phone = input("Enter new phone number: ")
                update_patient_details(conn, user['user_id'], address, phone)
                conn.commit()
            
            elif choice == 7:
                print("Logging out...")
                break
            else:
                print("Invalid choice. Try again.")

def admin_menu(user):
    """Menu for logged-in administrators."""
    print(f"\n--- Welcome {user['name']} (Admin) ---")
    with sqlite3.connect(DATABASE_NAME) as conn:
        while True:
            print("\n[Admin Menu]")
            print("1. Register New User")
            print("2. Create Bill for Patient")
            print("3. View All Patients")
            print("4. View All Doctors")
            print("5. Logout")
            choice = get_int_input("Enter choice: ")

            if choice == 1:
                # Register New User
                print("\n-- Register New User --")
                name = input("Enter user's name: ")
                email = input("Enter user's email: ")
                password = input("Enter user's password: ")
                print("Select role: (1) Doctor, (2) Patient, (3) Admin")
                role_choice = get_int_input("Role: ")
                
                user_id = None
                if role_choice == 1:
                    spec = input("Enter doctor's specialization: ")
                    user_id = add_user(conn, name, email, password, "doctor", specialization=spec)
                elif role_choice == 2:
                    addr = input("Enter patient's address: ")
                    ph = input("Enter patient's phone: ")
                    user_id = add_user(conn, name, email, password, "patient", address=addr, phone=ph)
                elif role_choice == 3:
                    user_id = add_user(conn, name, email, password, "admin")
                else:
                    print("Invalid role choice.")
                
                if user_id:
                    conn.commit()

            elif choice == 2:
                # Create Bill
                print("\n-- Create Bill --")
                patient_id = get_int_input("Enter Patient ID to bill: ")
                amount = float(input("Enter bill amount: $"))
                date = get_date_input("Enter Bill Date (YYYY-MM-DD): ")
                details = input("Enter bill details (e.g., 'Consultation Fee'): ")
                
                try:
                    add_billing(conn, amount, date, patient_id, details)
                    conn.commit()
                except sqlite3.IntegrityError:
                    print(f"Error: Patient ID {patient_id} does not exist.")

            elif choice == 3:
                # View All Patients
                print("\n-- All Patients --")
                patients = get_patients(conn)
                if not patients:
                    print("No patients found.")
                else:
                    for p in patients:
                        print(f"ID: {p[0]} | Name: {p[1]} | Phone: {p[2]} | Address: {p[3]}")
            
            elif choice == 4:
                # View All Doctors
                print("\n-- All Doctors --")
                doctors = get_doctors(conn)
                if not doctors:
                    print("No doctors found.")
                else:
                    for d in doctors:
                        print(f"ID: {d[0]} | Name: Dr. {d[1]} | Specialization: {d[2]}")
            
            elif choice == 5:
                print("Logging out...")
                break
            else:
                print("Invalid choice. Try again.")

def main_registration():
    """Handles the main menu patient registration flow."""
    print("\n--- New Patient Registration ---")
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Create a password: ")
    address = input("Enter your address: ")
    phone = input("Enter your phone number: ")
    history = input("Enter any brief medical history (or 'None'): ")
    reg_date = datetime.now().strftime('%Y-%m-%d')
    
    with sqlite3.connect(DATABASE_NAME) as conn:
        # Add the user and patient records
        patient_id = add_user(conn, name, email, password, "patient", address=address, phone=phone)
        
        if patient_id:
            # Add the registration history record
            add_patient_registration(conn, reg_date, history, patient_id)
            conn.commit()
            print(f"Registration successful! Your Patient ID is: {patient_id}")
        else:
            conn.rollback()
            print("Registration failed. Please try again.")