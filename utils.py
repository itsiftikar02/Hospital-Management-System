from datetime import datetime

def get_int_input(prompt):
    """Gets validated integer input from the user."""
    while True:
        try:
            value = input(prompt)
            return int(value)
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_date_input(prompt):
    """Gets validated date input (YYYY-MM-DD) from the user."""
    while True:
        date_str = input(prompt)
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def get_yes_no_input(prompt):
    """Gets a 'y' or 'n' response from the user."""
    while True:
        choice = input(prompt + " (y/n): ").lower().strip()
        if choice in ['y', 'n']:
            return choice == 'y'
        print("Invalid input. Please enter 'y' or 'n'.")