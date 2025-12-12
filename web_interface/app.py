# web_interface/app.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the project root to the Python path to import our agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.master_agent import MasterAgent

# Initialize Flask App
app = Flask(__name__)
# Enable CORS for all routes
CORS(app) 

# Create a single instance of the Master Agent to be used across sessions
# In a real product with many users, you'd manage agent instances more carefully
master_agent = MasterAgent()

@app.route('/')
def index():
    """Renders the main chat page."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat messages from the user."""
    # Get the user's message from the POST request
    user_message = request.json.get('message', '')
    
    # For simplicity, we'll manage the conversation state here.
    # A more robust solution would use sessions or a database.
    # We'll simulate the flow based on the message content.
    
    # This is a simplified state machine for the conversation
    if not hasattr(chat, 'state'):
        chat.state = 'AWAITING_PHONE'
        chat.customer_details = None
        chat.loan_details = {}

    response_message = ""
    
    if chat.state == 'AWAITING_PHONE':
        # First message from the user should be the phone number
        if len(user_message) == 10 and user_message.isdigit():
            verification_result = master_agent.verification_agent.verify_customer(user_message)
            if verification_result['status'] == 'success':
                chat.customer_details = verification_result
                chat.state = 'AWAITING_LOAN_AMOUNT'
                response_message = f"Thank you, {chat.customer_details['name']}! I've found your profile. How much would you like to borrow? (e.g., 500000)"
            else:
                response_message = "I'm sorry, but I couldn't find an account associated with that number. Please check and try again."
        else:
            response_message = "That doesn't seem to be a valid 10-digit number. Please provide your mobile number to get started."

    elif chat.state == 'AWAITING_LOAN_AMOUNT':
        try:
            amount = int(user_message)
            chat.loan_details['requested_amount'] = amount
            chat.state = 'AWAITING_TENURE'
            response_message = "Great. And for how many months would you like the tenure? (e.g., 60)"
        except ValueError:
            response_message = "It seems there was an issue with the number. Please enter a numeric loan amount."

    elif chat.state == 'AWAITING_TENURE':
        try:
            tenure = int(user_message)
            chat.loan_details['tenure'] = tenure
            
            # Now, trigger the rest of the agent logic
            sales_result = master_agent.sales_agent.discuss_loan(
                chat.customer_details['phone'], 
                chat.loan_details['requested_amount'],
                chat.loan_details['tenure']
            )
            
            if sales_result['status'] == 'suggestion':
                # This is a simplification. A real UI would present this as buttons.
                chat.loan_details['final_amount'] = sales_result['suggested_amount']
                response_message = sales_result['message'] + " I've taken the liberty of proceeding with the suggested amount for instant approval."
            else:
                chat.loan_details['final_amount'] = sales_result['final_amount']
                response_message = sales_result['message']
            
            # Proceed to underwriting
            underwriting_result = master_agent.underwriting_agent.evaluate_loan(
                chat.customer_details['phone'], 
                chat.loan_details['final_amount']
            )
            
            if underwriting_result['status'] == 'approved_instant':
                # Generate letter
                loan_details_for_letter = {
                    'approved_amount': underwriting_result['approved_amount'],
                    'interest_rate': '10.99%',
                    'tenure': chat.loan_details['tenure']
                }
                letter_result = master_agent.sanction_generator.generate_letter(chat.customer_details, loan_details_for_letter)
                
                if letter_result['status'] == 'success':
                    response_message += f"\n\n🎉 Congratulations! Your loan of ₹{loan_details_for_letter['approved_amount']:,} has been approved. Your sanction letter has been generated."
                    chat.state = 'CONVERSATION_END'
                else:
                    response_message += "\n\nThere was an issue generating your sanction letter. Please contact support."
                    chat.state = 'CONVERSATION_END'
            
            elif underwriting_result['status'] == 'pending_salary_slip':
                # Simulate the salary slip upload and approval
                response_message += "\n\nSimulating salary slip upload and verification... Done! Your loan has been approved after document verification."
                loan_details_for_letter = {
                    'approved_amount': chat.loan_details['final_amount'],
                    'interest_rate': '10.99%',
                    'tenure': chat.loan_details['tenure']
                }
                letter_result = master_agent.sanction_generator.generate_letter(chat.customer_details, loan_details_for_letter)
                if letter_result['status'] == 'success':
                    response_message += f"\n\n🎉 Congratulations! Your loan of ₹{loan_details_for_letter['approved_amount']:,} has been approved. Your sanction letter has been generated."
                    chat.state = 'CONVERSATION_END'
                else:
                    response_message += "\n\nThere was an issue generating your sanction letter. Please contact support."
                    chat.state = 'CONVERSATION_END'

            else: # Rejected
                response_message += f"\n\n{underwriting_result['reason']}"
                chat.state = 'CONVERSATION_END'

        except ValueError:
            response_message = "It seems there was an issue with the number. Please enter a numeric tenure in months."
    
    elif chat.state == 'CONVERSATION_END':
        response_message = "This conversation has concluded. Please refresh the page to start a new one."

    return jsonify({"message": response_message})

if __name__ == '__main__':
    # IMPORTANT: Make sure your mock API server is running in another terminal!
    app.run(port=5000, debug=True)