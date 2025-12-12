# verify_setup.py
from utils.database import customer_db

def main():
    print("--- Tata Capital Chatbot: Setup Verification ---")
    
    # Test 1: Check if the database loaded
    all_customers = customer_db.customers
    if not all_customers:
        print("❌ FAILED: Customer database is empty.")
        return
    else:
        print(f"✅ SUCCESS: Loaded {len(all_customers)} customers into the database.")

    # Test 2: Check if we can retrieve a specific customer
    test_phone = "9876543210" # Rajesh Kumar's phone
    customer = customer_db.get_customer_by_phone(test_phone)
    
    if customer:
        print(f"✅ SUCCESS: Found customer '{customer['name']}' with phone {test_phone}.")
        print(f"   - Credit Score: {customer['credit_score']}")
        print(f"   - Pre-Approved Limit: ₹{customer['pre_approved_limit']:,}")
    else:
        print(f"❌ FAILED: Could not find customer with phone {test_phone}.")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    main()