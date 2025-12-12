# utils/database.py
import json
import os

class CustomerDatabase:
    """A simple class to manage our customer data."""
    def __init__(self):
        self.customers = {}
        self.load_customers()
    
    def load_customers(self):
        """Loads customer data from the JSON file."""
        try:
            # Construct the path relative to the project root
            project_root = os.path.dirname(os.path.dirname(__file__))
            file_path = os.path.join(project_root, 'data', 'customers.json')
            
            with open(file_path, 'r') as f:
                customers_data = json.load(f)
                for customer in customers_data:
                    # Use phone number as the primary key for easy lookup
                    self.customers[customer['phone']] = customer
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
            print("Please ensure the data directory and customers.json file exist.")
        except json.JSONDecodeError:
            print(f"Error: The file {file_path} contains invalid JSON.")
    
    def get_customer_by_phone(self, phone):
        """Retrieves a customer's data using their phone number."""
        return self.customers.get(phone)

# Create a single, global instance of our database to be used across the application
customer_db = CustomerDatabase()