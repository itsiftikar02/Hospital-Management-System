import sys
from db import init_db, login
from menus import doctor_menu, patient_menu, admin_menu, main_registration
from utils import get_int_input, get_yes_no_input
from seed import seed_data

if __name__ == "__main__":
    init_db()
    
    # Ask to seed data only if DB was likely just created (or on request)
    if get_yes_no_input("Do you want to add initial sample data (for testing)?"):
        seed_data()

    print("\n--- Hospital Management System ---")
    
    while True:
        print("\n[Main Menu]")
        print("1. Login")
        print("2. New Patient Registration")
        print("3. Exit")
        main_choice = get_int_input("Enter choice: ")
        
        if main_choice == 1:
            email = input("Email: ")
            password = input("Password: ")
            
            user = login(email, password)
            
            if user:
                print(f"\nLogin successful! Welcome, {user['name']}.")
                if user['role'] == "doctor":
                    doctor_menu(user)
                elif user['role'] == "patient":
                    patient_menu(user)
                elif user['role'] == "admin":
                    admin_menu(user)
            else:
                print("Invalid email or password. Try again.")
                
        elif main_choice == 2:
            main_registration()
            
        elif main_choice == 3:
            print("Goodbye!")
            sys.exit()
            
        else:
            print("Invalid choice. Try again.")