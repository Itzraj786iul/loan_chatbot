# agents/master_agent.py
import sys
import os

# Add the project root to the Python path to import our other agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.verification_agent import VerificationAgent
from agents.sales_agent import SalesAgent
from agents.underwriting_agent import UnderwritingAgent
from agents.sanction_letter_generator import SanctionLetterGenerator

class MasterAgent:
    """
    The main orchestrator for the loan sales process.
    Manages the conversation flow and coordinates the Worker Agents.
    """
    def __init__(self):
        # Initialize all worker agents
        self.verification_agent = VerificationAgent()
        self.sales_agent = SalesAgent()
        self.underwriting_agent = UnderwritingAgent()
        self.sanction_generator = SanctionLetterGenerator()
        
        # Store conversation state
        self.customer_details = None
        self.loan_details = {}

    def start_conversation(self):
        """Initiates the conversation with the customer."""
        print("Chatbot: Welcome to Tata Capital! I'm here to help you with your personal loan needs.")
        print("Chatbot: To get started, could you please provide your 10-digit mobile number?")
        
        # In a real web app, this would be an input field.
        # For our prototype, we'll simulate user input.
        phone = input("You: ")
        
        # Simple validation
        if len(phone) == 10 and phone.isdigit():
            self.handle_verification(phone)
        else:
            print("Chatbot: That doesn't seem to be a valid 10-digit number. Let's try again.")
            self.start_conversation() # Restart the flow

    def handle_verification(self, phone):
        """Handles the customer verification step."""
        print("\n[Master Agent] Verifying customer...")
        verification_result = self.verification_agent.verify_customer(phone)
        
        if verification_result['status'] == 'success':
            self.customer_details = verification_result
            print(f"Chatbot: Thank you, {self.customer_details['name']}! I've found your profile.")
            self.handle_loan_request()
        else:
            print("Chatbot: I'm sorry, but I couldn't find an account associated with that number. Please check and try again.")
            self.start_conversation()

    def handle_loan_request(self):
        """Handles the loan amount and tenure request."""
        print("Chatbot: How much would you like to borrow? (e.g., 500000)")
        amount_str = input("You: ")
        
        print("Chatbot: And for how many months would you like the tenure? (e.g., 60)")
        tenure_str = input("You: ")

        try:
            amount = int(amount_str)
            tenure = int(tenure_str)
            self.loan_details['requested_amount'] = amount
            self.loan_details['tenure'] = tenure
            self.handle_sales_discussion()
        except ValueError:
            print("Chatbot: It seems there was an issue with the numbers. Please enter numeric values only.")
            self.handle_loan_request()

    def handle_sales_discussion(self):
        """Discusses the loan options with the sales agent."""
        print("\n[Master Agent] Discussing loan options...")
        sales_result = self.sales_agent.discuss_loan(
            self.customer_details['phone'], 
            self.loan_details['requested_amount'],
            self.loan_details['tenure']
        )
        
        print(f"Chatbot: {sales_result['message']}")
        
        if sales_result['status'] == 'suggestion':
            # In a real app, this would be a button click. Here we simulate with text.
            choice = input("Type 'yes' to accept the suggested amount, or 'no' to continue with your original request: ").lower()
            if choice == 'yes':
                self.loan_details['final_amount'] = sales_result['suggested_amount']
            else:
                self.loan_details['final_amount'] = self.loan_details['requested_amount']
        else:
            self.loan_details['final_amount'] = sales_result['final_amount']
        
        self.loan_details['final_tenure'] = sales_result['final_tenure']
        self.handle_underwriting()

    def handle_underwriting(self):
        """Handles the underwriting and approval process."""
        print("\n[Master Agent] Sending your application for evaluation...")
        underwriting_result = self.underwriting_agent.evaluate_loan(
            self.customer_details['phone'], 
            self.loan_details['final_amount']
        )
        
        status = underwriting_result['status']
        print(f"Chatbot: {underwriting_result['reason']}")

        if status == 'approved_instant':
            self.handle_approval(underwriting_result)
        elif status == 'pending_salary_slip':
            self.handle_salary_slip_upload()
        elif status == 'rejected':
            self.end_conversation("rejected")
        else:
            self.end_conversation("error")

    def handle_salary_slip_upload(self):
        """Handles the simulation of a salary slip upload."""
        print("Chatbot: Please upload a clear copy of your latest salary slip.")
        # Simulate file upload
        input("Press Enter after uploading the file...")
        
        # In a real product, we would parse the PDF/image here.
        # For the prototype, we assume the upload is successful and the salary is sufficient.
        print("\n[Master Agent] Verifying uploaded document... (Simulated)")
        print("[Master Agent] ✅ Document verified. EMI is within the 50% salary limit.")
        
        # Re-run underwriting with a flag to indicate documents are verified
        print("[Master Agent] Re-evaluating loan request...")
        # We'll just assume approval now for simplicity.
        # A more complex agent might call the underwriting agent with a new parameter.
        approval_result = {
            "status": "approved_instant",
            "reason": "Congratulations! Your loan has been approved after document verification.",
            "approved_amount": self.loan_details['final_amount']
        }
        self.handle_approval(approval_result)

    def handle_approval(self, approval_result):
        """Handles the final approval and generates the sanction letter."""
        self.loan_details['approved_amount'] = approval_result['approved_amount']
        self.loan_details['interest_rate'] = "10.99%" # Get from offer mart API in a real product
        
        print("\n[Master Agent] Generating your sanction letter...")
        letter_result = self.sanction_generator.generate_letter(self.customer_details, self.loan_details)
        
        if letter_result['status'] == 'success':
            print(f"Chatbot: 🎉 Congratulations! Your loan of ₹{self.loan_details['approved_amount']:,} has been approved.")
            print(f"Chatbot: Your sanction letter '{letter_result['filename']}' has been generated.")
            print("Chatbot: You will receive a copy on your email and SMS shortly. Thank you for choosing Tata Capital!")
            self.end_conversation("approved")
        else:
            print("Chatbot: There was an issue generating your sanction letter. Please contact support.")
            self.end_conversation("error")

    def end_conversation(self, outcome):
        """Ends the conversation."""
        print("\n--- Conversation End ---")
        if outcome == "approved":
            print("Outcome: Loan Approved and Letter Generated.")
        elif outcome == "rejected":
            print("Outcome: Loan Rejected.")
        else:
            print("Outcome: Error during process.")
        print("Chatbot: Is there anything else I can help you with today?")

# --- Driver script to run the Master Agent ---
if __name__ == '__main__':
    # IMPORTANT: Make sure your mock API server is running in another terminal!
    master = MasterAgent()
    master.start_conversation()