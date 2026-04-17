import pandas as pd
import numpy as np
import os

def generate_sample_data():
    data = [
        # Phishing
        {"text": "Urgent: Your account has been suspended. Click here to verify your identity now!", "label": "Phishing"},
        {"text": "Security Alert: Unusual login detected. Please update your password immediately.", "label": "Phishing"},
        {"text": "Final Notice: Your subscription will expire tonight. Renew at this link to avoid service interruption.", "label": "Phishing"},
        
        # Internship Scam (Aggressive)
        {"text": "Urgent Google Internship: You are selected for a Software Engineering role. Claim your offer within 24 hours. A security deposit of ₹2000 is required for laptop shipping. Visit: http://google-career.support/verify", "label": "Internship Scam"},
        {"text": "Congratulations! Selected for Microsoft Remote Internship. Salary $2000/week. Pay ₹500 orientation fee to start immediately. Enroll at: http://msft.bit.ly/enroll", "label": "Internship Scam"},
        {"text": "Internship opportunity at Amazon. Contact on WhatsApp +91-XXXXXXXXXX for the trainee program. Registration fee ₹1500 must be paid today to confirm slot.", "label": "Internship Scam"},
        {"text": "Work from home and earn $500/day. Send bank details and ID proof to HR portal: http://work-campus.xyz/login", "label": "Internship Scam"},
        {"text": "Final Warning: Your internship application with Government of India will expire in 2 hours. Complete your KYC here: http://gov-india.info/kyc", "label": "Internship Scam"},

        # Payment Fraud
        {"text": "Request for payment: Your library fine is overdue. Pay via this crypto link to avoid enrollment hold.", "label": "Payment Fraud"},
        {"text": "Refund processing: We owe you $200. Please provide your credit card info to receive the funds.", "label": "Payment Fraud"},
        {"text": "Emergency: Your student fee transaction failed. Please re-send the payment to this personal account.", "label": "Payment Fraud"},

        # Credential Harvesting
        {"text": "New shared document: 'Final Exam Answers'. Login to your university portal here to view.", "label": "Credential Harvesting"},
        {"text": "IT Support: We are upgrading our email servers. Please sign in to confirm your mailbox migration.", "label": "Credential Harvesting"},
        {"text": "Survey: Win a $50 Amazon gift card by logging into our research portal with your campus credentials.", "label": "Credential Harvesting"},

        # Legitimate
        {"text": "Reminder: Your Computer Science lecture starts at 10:00 AM in Hall B.", "label": "Legitimate"},
        {"text": "The library will be closed this Friday for maintenance. Please plan accordingly.", "label": "Legitimate"},
        {"text": "Your grades for the Midterm exam have been posted on the student dashboard.", "label": "Legitimate"},
        {"text": "Meeting invite: Student Council weekly sync, Wednesday at 4 PM.", "label": "Legitimate"},
        {"text": "Hello, this is Prof. Smith. Please remember to submit your assignments by tomorrow.", "label": "Legitimate"},
    ]

    # Generate more synthetic data to make it 'trainable'
    synthetic_data = []
    for _ in range(20):
        for item in data:
            # Add some noise or variations if needed
            synthetic_data.append(item)

    df = pd.DataFrame(synthetic_data)
    
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    os.makedirs(data_dir, exist_ok=True)
    df.to_csv(os.path.join(data_dir, 'sample_threats.csv'), index=False)
    print(f"Sample dataset generated at {os.path.join(data_dir, 'sample_threats.csv')}")

if __name__ == "__main__":
    generate_sample_data()
