# agents/sanction_letter_generator.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os
import datetime

class SanctionLetterGenerator:
    """
    Generates a PDF sanction letter for an approved loan.
    """
    def __init__(self):
        # Ensure the directory for generated letters exists
        self.output_dir = "generated_letters"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_letter(self, customer_details, loan_details):
        """
        Creates a PDF sanction letter.
        
        Args:
            customer_details (dict): Customer's KYC information.
            loan_details (dict): Approved loan details (amount, tenure, etc.).
            
        Returns:
            dict: A dictionary containing the status and the path to the generated PDF.
        """
        print("[Sanction Letter Generator] Generating sanction letter...")
        
        # Create a unique filename for the PDF
        customer_name = customer_details['name'].replace(" ", "_")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Sanction_Letter_{customer_name}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create the PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # --- Add content to the PDF ---
        
        # Header
        p = Paragraph("<b>Tata Capital Loan Sanction Letter</b>", styles['h1'])
        story.append(p)
        story.append(Spacer(1, 0.2 * inch))
        
        # Date
        p = Paragraph(f"Date: {datetime.datetime.now().strftime('%d-%B-%Y')}", styles['Normal'])
        story.append(p)
        story.append(Spacer(1, 0.3 * inch))

        # Customer Details
        p = Paragraph("<b>To,</b>", styles['Normal'])
        story.append(p)
        p = Paragraph(f"{customer_details['name']}", styles['Normal'])
        story.append(p)
        p = Paragraph(f"{customer_details['address']}", styles['Normal'])
        story.append(p)
        p = Paragraph(f"Phone: {customer_details['phone']}", styles['Normal'])
        story.append(p)
        p = Paragraph(f"Email: {customer_details['email']}", styles['Normal'])
        story.append(p)
        story.append(Spacer(1, 0.3 * inch))

        # Loan Sanction Details
        p = Paragraph("<b>Subject: Personal Loan Sanction</b>", styles['h2'])
        story.append(p)
        story.append(Spacer(1, 0.2 * inch))
        
        # Main body text
        body_text = f"""
        Dear {customer_details['name']},<br/><br/>
        We are pleased to inform you that your personal loan application has been approved. 
        The sanction details are as follows:<br/><br/>
        <b>Sanctioned Loan Amount:</b> ₹{loan_details['approved_amount']:,}<br/>
        <b>Interest Rate:</b> {loan_details.get('interest_rate', '10.99%')}<br/>
        <b>Tenure:</b> {loan_details.get('tenure', 'Not Specified')} months<br/>
        <b>Customer ID:</b> {customer_details['customer_id']}<br/><br/>
        This sanction letter is valid for 30 days from the date of issue. 
        Please contact our branch to proceed with the disbursement process.<br/><br/>
        Congratulations on your loan approval!<br/><br/>
        Sincerely,<br/>
        Tata Capital Loan Team
        """
        p = Paragraph(body_text, styles['Normal'])
        story.append(p)
        
        # Build the PDF
        doc.build(story)
        
        print(f"[Sanction Letter Generator] ✅ Successfully generated PDF at: {filepath}")
        return {
            "status": "success",
            "message": "Sanction letter generated successfully.",
            "filepath": filepath,
            "filename": filename
        }

# --- Self-test for the agent ---
if __name__ == '__main__':
    agent = SanctionLetterGenerator()
    
    # Mock data for testing
    mock_customer = {
        "customer_id": "CUST001",
        "name": "Rajesh Kumar",
        "phone": "9876543210",
        "email": "rajesh.kumar@email.com",
        "address": "123, Bandra West, Mumbai - 400050"
    }
    
    mock_loan = {
        "approved_amount": 500000,
        "interest_rate": "10.99%",
        "tenure": 60
    }
    
    print("--- Testing Sanction Letter Generation ---")
    result = agent.generate_letter(mock_customer, mock_loan)
    print(f"Result: {result}")
    print(f"Please check the '{agent.output_dir}' folder for the generated PDF.")