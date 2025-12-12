# agents/underwriting_agent.py
import requests
import sys
import os

# Add the project root to the Python path to import our database utility
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import customer_db

# Base URL for our mock APIs
API_BASE_URL = "http://127.0.0.1:5001"

class UnderwritingAgent:
    """
    Evaluates loan applications based on credit score and pre-approved limits.
    This agent calls external mock APIs to fetch necessary data.
    """
    def __init__(self):
        pass

    def evaluate_loan(self, phone_number, requested_amount):
        """
        Evaluates a loan request against business rules.
        
        Args:
            phone_number (str): The customer's phone number.
            requested_amount (int): The loan amount requested by the customer.
            
        Returns:
            dict: A dictionary with the decision, reason, and details.
        """
        print(f"[Underwriting Agent] Evaluating loan request for ₹{requested_amount:,} for phone: {phone_number}")
        
        # --- Step 1: Fetch data from Mock APIs ---
        try:
            # Get credit score from the mock Credit Bureau API
            credit_response = requests.get(f"{API_BASE_URL}/api/credit-bureau/score?phone={phone_number}")
            credit_response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
            credit_data = credit_response.json()
            credit_score = credit_data['credit_score']
            print(f"[Underwriting Agent] Fetched Credit Score: {credit_score}")

            # Get pre-approved limit from the mock Offer Mart API
            offer_response = requests.get(f"{API_BASE_URL}/api/offer-mart/pre-approved?phone={phone_number}")
            offer_response.raise_for_status()
            offer_data = offer_response.json()
            pre_approved_limit = offer_data['pre_approved_limit']
            print(f"[Underwriting Agent] Fetched Pre-Approved Limit: ₹{pre_approved_limit:,}")

        except requests.exceptions.RequestException as e:
            print(f"[Underwriting Agent] ❌ Error connecting to APIs: {e}")
            return {"status": "error", "message": "Could not connect to verification services."}
        except KeyError:
            print("[Underwriting Agent] ❌ Error: Unexpected response format from APIs.")
            return {"status": "error", "message": "A system error occurred."}

        # --- Step 2: Apply Business Rules ---
        
        # Rule 1: Check minimum credit score
        if credit_score < 700:
            print(f"[Underwriting Agent] ❌ REJECTED: Credit score {credit_score} is below the minimum threshold of 700.")
            return {
                "status": "rejected",
                "reason": f"Unfortunately, your application could not be approved as your credit score ({credit_score}) is below our minimum requirement.",
                "credit_score": credit_score
            }

        # Rule 2: Check loan amount against pre-approved limit
        if requested_amount <= pre_approved_limit:
            print("[Underwriting Agent] ✅ APPROVED (Instant): Loan amount is within pre-approved limit.")
            return {
                "status": "approved_instant",
                "reason": "Congratulations! Your loan has been instantly approved based on your pre-approved offer.",
                "approved_amount": requested_amount,
                "credit_score": credit_score
            }
        
        # Rule 3: Check if amount is between 1x and 2x the limit
        elif requested_amount <= (2 * pre_approved_limit):
            print("[Underwriting Agent] ⏳ PENDING: Requires salary slip verification.")
            return {
                "status": "pending_salary_slip",
                "reason": "Your request is being processed. To proceed, please upload your latest salary slip for verification.",
                "max_emi_percent": 50, # EMI must be <= 50% of salary
                "credit_score": credit_score
            }
        
        # Rule 4: Reject if amount is too high
        else: # requested_amount > 2 * pre_approved_limit
            print(f"[Underwriting Agent] ❌ REJECTED: Loan amount ₹{requested_amount:,} exceeds 2x the pre-approved limit (₹{2 * pre_approved_limit:,}).")
            return {
                "status": "rejected",
                "reason": f"Unfortunately, we cannot approve the requested amount. The maximum amount we can offer is ₹{2 * pre_approved_limit:,}.",
                "credit_score": credit_score
            }

# --- Self-test for the agent ---
if __name__ == '__main__':
    agent = UnderwritingAgent()
    
    # --- Test Case 1: Instant Approval (Priya Sharma) ---
    print("\n--- TEST 1: Instant Approval ---")
    # Priya has a limit of 750,000. Requesting 600,000 should be instant.
    result = agent.evaluate_loan("9876543211", 600000)
    print(f"Result: {result}\n")

    # --- Test Case 2: Requires Salary Slip (Neha Singh) ---
    print("--- TEST 2: Requires Salary Slip ---")
    # Neha has a limit of 600,000. Requesting 1,000,000 (<= 2x limit) should require a slip.
    result = agent.evaluate_loan("9876543213", 1000000)
    print(f"Result: {result}\n")

    # --- Test Case 3: Rejection (Amit Patel) ---
    print("--- TEST 3: Rejection due to Credit Score ---")
    # Amit has a credit score of 680.
    result = agent.evaluate_loan("9876543212", 100000)
    print(f"Result: {result}\n")

    # --- Test Case 4: Rejection due to High Amount ---
    print("--- TEST 4: Rejection due to High Amount ---")
    # Rajesh has a limit of 500,000. Requesting 1,200,000 (> 2x limit) should be rejected.
    result = agent.evaluate_loan("9876543210", 1200000)
    print(f"Result: {result}\n")