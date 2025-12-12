# test_apis.py
import requests
import json

# The base URL for our mock API server
API_BASE_URL = "http://127.0.0.1:5001"

def test_api_endpoints():
    print("--- Testing Mock API Endpoints ---")
    
    # --- Test Case 1: Valid Customer ---
    print("\n[TEST 1] Fetching data for a valid customer (Rajesh Kumar)...")
    test_phone = "9876543210"
    
    try:
        # Test Credit Bureau API
        credit_url = f"{API_BASE_URL}/api/credit-bureau/score?phone={test_phone}"
        credit_response = requests.get(credit_url)
        print(f"✅ Credit Bureau API Status: {credit_response.status_code}")
        print(f"   Response: {credit_response.json()}")
        
        # Test Offer Mart API
        offer_url = f"{API_BASE_URL}/api/offer-mart/pre-approved?phone={test_phone}"
        offer_response = requests.get(offer_url)
        print(f"✅ Offer Mart API Status: {offer_response.status_code}")
        print(f"   Response: {offer_response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Connection Error. Is the API server running?")
        print("   Please run 'python mock_apis/server.py' in another terminal.")
        return

    # --- Test Case 2: Invalid Customer ---
    print("\n[TEST 2] Fetching data for a non-existent customer...")
    invalid_phone = "1234567890"
    
    credit_url = f"{API_BASE_URL}/api/credit-bureau/score?phone={invalid_phone}"
    credit_response = requests.get(credit_url)
    print(f"✅ Credit Bureau API Status: {credit_response.status_code}")
    print(f"   Response: {credit_response.json()}")

    print("\n--- API Testing Complete ---")


if __name__ == "__main__":
    test_api_endpoints()