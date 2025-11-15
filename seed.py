import sqlite3
from datetime import datetime
from config import DATABASE_NAME
from db import add_user, add_patient_registration, add_appointment, add_billing

def seed_data():
    """Adds initial data to the database for testing."""
    print("Seeding database with initial data...")
    with sqlite3.connect(DATABASE_NAME) as conn:
        try:
            # Add users
            doc_id = add_user(conn, "Alice Smith", "asmith@example.com", "pass123", "doctor", specialization="Cardiology")
            pat_id = add_user(conn, "Bob Johnson", "bjohnson@example.com", "pass123", "patient", address="123 Main St", phone="555-1212")
            admin_id = add_user(conn, "Admin User", "admin@example.com", "adminpass", "admin")
            
            if pat_id:
                # Add registration details
                add_patient_registration(conn, "2023-01-01", "Mild pollen allergy", pat_id)
            
            if doc_id and pat_id:
                # Add sample appointment
                add_appointment(conn, "2024-05-10", doc_id, pat_id)
            
            if pat_id:
                # Add a sample bill
                add_billing(conn, 150.00, "2024-05-10", pat_id, "Initial Consultation")
            
            conn.commit()
            print("Seed data added successfully.")
        except Exception as e:
            print(f"An error occurred during seeding (data might already exist): {e}")
            conn.rollback()