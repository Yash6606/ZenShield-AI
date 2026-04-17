from typing import List, Dict

class TrainingService:
    def __init__(self, history_service=None):
        self.history_service = history_service
        self.scenarios = [
            {
                "id": 1,
                "title": "The Urgent IT Upgrade",
                "difficulty": "Easy",
                "content": "From: IT Service Desk <it-support@corp-update.net>\nSubject: CRITICAL: Mandatory Security Update Required\n\nDear Employee, your workstation requires an urgent security patch. Failure to install by 5 PM will result in account lockout. Click here: http://bit.ly/update-corp-99",
                "is_phishing": True,
                "explanation": "This is a classic 'Urgency' phishing attack. The link (bit.ly) hides the real destination, and the sender domain 'corp-update.net' is not your official company domain.",
                "red_flags": ["Suspicious urgency", "Unofficial sender domain", "Shortened URL"]
            },
            {
                "id": 2,
                "title": "Security Awareness Quiz",
                "difficulty": "Easy",
                "content": "From: Training Dept <learning@zenshield-corp.ai>\nSubject: Annual Security Training Reminder\n\nHi Team, just a reminder to complete your security modules before the end of the month. You can access the portal via the HR dashboard link you usually use.",
                "is_phishing": False,
                "explanation": "This is a legitimate internal notification. It doesn't use external links or pressure you into clicking a suspicious URL immediately.",
                "red_flags": []
            },
            {
                "id": 3,
                "title": "Microsoft 365 Account Suspension",
                "difficulty": "Medium",
                "content": "From: Microsoft Admin <no-reply@microsoft-security-verify.com>\nSubject: Unusual Login Activity Detected\n\nSomeone recently tried to log in to your account from a new location (IP: 192.168.1.50). If this wasn't you, please secure your account at https://microsoft-account-security.net/verify",
                "is_phishing": True,
                "explanation": "Microsoft uses 'microsoft.com' or 'office.com'. The domain 'microsoft-security-verify.com' is a look-alike domain used to steal passwords.",
                "red_flags": ["Look-alike domain", "Suspicious URL", "Security-themed lure"]
            },
            {
                "id": 4,
                "title": "Company Holiday List 2024",
                "difficulty": "Easy",
                "content": "From: Ops Manager <ops@zenshield-corp.ai>\nSubject: Holiday Calendar 2024\n\nHi everyone, please find the list of upcoming holidays for the next year. This is for your planning purposes. No action required.",
                "is_phishing": False,
                "explanation": "Internal announcement with no call to action, originating from a verified internal address.",
                "red_flags": []
            },
            {
                "id": 5,
                "title": "Unclaimed Tax Refund",
                "difficulty": "Medium",
                "content": "From: Government Revenue <refunds@gov-tax-portal.biz>\nSubject: Final Notice: Your Tax Refund is Ready\n\nOur records show you are entitled to a refund of $1,240.25. To claim your funds, please provide your bank details at http://tax-refund-portal.biz/claim-now",
                "is_phishing": True,
                "explanation": "Government agencies do not use '.biz' domains, nor do they notify people of refunds via email with direct links to bank forms.",
                "red_flags": ["Suspicious .biz domain", "Financial bait", "Request for banking info"]
            },
            {
                "id": 6,
                "title": "Netflix Billing Issue",
                "difficulty": "Easy",
                "content": "From: Netflix Help <support@netflix-billing.com>\nSubject: Your Membership is on Hold\n\nWe're having some trouble with your current billing information. We'll try again, but in the meantime, you may want to update your payment details: https://www.netflix-account-fix.com",
                "is_phishing": True,
                "explanation": "Deceptive URL 'netflix-account-fix.com' is not 'netflix.com'. This is a subscription-themed phishing attempt.",
                "red_flags": ["Inaccurate official domain", "Payment pressure"]
            },
            {
                "id": 7,
                "title": "New Shared Document",
                "difficulty": "Medium",
                "content": "From: Dropbox <no-reply@dropbox-docs.com>\nSubject: Venil shared 'Project_Blueprint.zip' with you\n\nHi, a colleague has shared a confidential file with you via Dropbox. Please login to view the contents: http://dropbox-docs.com/s/abcdef123",
                "is_phishing": True,
                "explanation": "Official Dropbox communications come from 'dropbox.com'. The use of 'dropbox-docs.com' is a clever typo-squatting attempt.",
                "red_flags": ["Domain mismatch (dropbox-docs.com vs dropbox.com)", "Zip files can be risky"]
            },
            {
                "id": 8,
                "title": "Internal Slack Notification",
                "difficulty": "Medium",
                "content": "From: Slack Notifications <notifications@slack.com>\nSubject: New message from #general channel\n\n@Venil mentioned you in #general: 'Hey, did anyone see the new security policy posted on the company wiki?'",
                "is_phishing": False,
                "explanation": "Legitimate automated notification from a verified platform (slack.com) referencing internal discussion.",
                "red_flags": []
            },
            {
                "id": 9,
                "title": "LinkedIn Connection Request",
                "difficulty": "Hard",
                "content": "From: LinkedIn <member@linkedin-mail.net>\nSubject: You have a new invitation to connect\n\nJohn Doe (CEO at TechCorp) wants to connect with you. View Profile: https://www.linkedin.com/in/johndoe/invitation-accept",
                "is_phishing": False,
                "explanation": "LinkedIn sends mail from 'linkedin.com' and 'linkedin-mail.com'. This specific scenario (though tricky) uses standard invite formats.",
                "red_flags": []
            },
            {
                "id": 10,
                "title": "Urgent Bank Transfer",
                "difficulty": "Hard",
                "content": "From: Fraud Department <no-reply@chase-alert-security.com>\nSubject: URGENT: Fraudulent Transfer of $5,000\n\nA transfer of $5,000 to an unknown account in Russia was initiated. If you did not authorize this, log in immediately to CANCEL: https://chaseonline.security-login.com/cancel",
                "is_phishing": True,
                "explanation": "The domain 'security-login.com' is the main domain here, NOT 'chaseonline'. This is a high-pressure financial alert intended to steal banking credentials.",
                "red_flags": ["Deceptive sub-domain", "Extreme urgency", "Fear-based social engineering"]
            }
        ]

    def get_scenarios(self) -> List[Dict]:
        return [
            {
                "id": s["id"],
                "title": s["title"],
                "difficulty": s["difficulty"],
                "content": s["content"]
            } for s in self.scenarios
        ]

    def check_answer(self, scenario_id: int, verdict: str, user_id: int = 0) -> Dict:
        scenario = next((s for s in self.scenarios if s["id"] == scenario_id), None)
        if not scenario:
            return {"error": "Scenario not found"}
        
        is_phishing_answered = (verdict == "danger")
        correct = (is_phishing_answered == scenario["is_phishing"])
        
        if self.history_service:
            mock_result = {
                "risk_score": 100 if scenario["is_phishing"] else 0,
                "verdict": "Training Result",
                "severity": "High" if scenario["is_phishing"] else "Low",
                "text_preview": scenario["content"][:100]
            }
            if not correct:
                self.history_service.add_entry("training_failure", mock_result, user_id=user_id)
            else:
                self.history_service.add_entry("training_success", mock_result, user_id=user_id)

        return {
            "is_correct": correct,
            "explanation": scenario["explanation"],
            "red_flags": scenario["red_flags"]
        }
