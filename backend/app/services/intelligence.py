import re
import urllib.parse

class FeatureEngine:
    def __init__(self):
        self.urgency_keywords = ['urgent', 'immediately', 'now', 'soon', 'deadline', 'expire', 'suspended', 'limited time']
        self.financial_keywords = ['payment', 'bank', 'credit card', 'refund', 'money', 'transaction', 'crypto', 'invoice']
        self.authority_keywords = ['official', 'admin', 'it support', 'government', 'university', 'dean', 'security alert']
        self.suspicious_url_patterns = [r'bit\.ly', r't\.co', r'goo\.gl', r'tinyurl\.com', r'verify', r'login-', r'secure-']

    def extract_features(self, text: str):
        text_lower = text.lower()
        
        # 1. Urgency Score
        urgency_count = sum(1 for word in self.urgency_keywords if word in text_lower)
        urgency_score = min(urgency_count / 3, 1.0) # Cap at 1.0

        # 2. Financial Trigger Index
        financial_count = sum(1 for word in self.financial_keywords if word in text_lower)
        financial_score = min(financial_count / 3, 1.0)

        # 3. Authority Impersonation Score
        authority_count = sum(1 for word in self.authority_keywords if word in text_lower)
        authority_score = min(authority_count / 2, 1.0)

        # 4. Suspicious URL Pattern Detector
        # (Simulating URL detection in text)
        url_match = re.search(r'https?://\S+', text)
        url_detected = 0
        is_shortened = 0
        if url_match:
            url_detected = 1
            url = url_match.group(0)
            if any(re.search(pattern, url) for pattern in self.suspicious_url_patterns):
                is_shortened = 1

        # 5. Excessive Capitalization
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if len(text) > 0 else 0
        caps_indicator = 1 if caps_ratio > 0.3 else 0

        # 6. Grammar/Anomaly Heuristic (Simple)
        # Check for multiple exclamation marks or weird symbols
        anomaly_score = 1 if '!!!' in text or '$$$' in text or '???' in text else 0

        features = {
            "urgency_score": urgency_score,
            "financial_score": financial_score,
            "authority_score": authority_score,
            "url_detected": url_detected,
            "is_shortened": is_shortened,
            "caps_indicator": caps_indicator,
            "anomaly_score": anomaly_score
        }
        
        return features

    def get_explanation(self, features: dict, category: str, probability: float):
        reasons = []
        if features['urgency_score'] > 0.5:
            reasons.append("High urgency and time-pressure language detected")
        if features['financial_score'] > 0.5:
            reasons.append("Suspicious financial or payment requests identified")
        if features['authority_score'] > 0.5:
            reasons.append("Potential authority impersonation (Admin/Official)")
        if features['is_shortened']:
            reasons.append("Suspicious shortened URL found")
        if features['caps_indicator']:
            reasons.append("Excessive capitalization often used in scams")
        if features['anomaly_score']:
            reasons.append("Unusual punctuation and formatting detected")

        # Top 3 contributing signals
        top_reasons = reasons[:3] if reasons else ["General threat patterns detected"]
        
        suggested_action = "Do not click any links. Report this to campus IT immediately."
        if category == "Legitimate":
            suggested_action = "This message appears safe, but always remain cautious."
            top_reasons = ["No significant threat markers found"]

        return {
            "risk_score": round(probability * 100, 2),
            "top_signals": top_reasons,
            "suggested_action": suggested_action
        }
