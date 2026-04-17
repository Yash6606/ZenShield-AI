import re
from typing import Dict, Optional

class FeatureEngineer:
    def __init__(self):
        self.urgency_keywords = [
            'urgent', 'immediately', 'within', 'hours', 'minutes', 'deadline', 
            'final warning', 'act now', 'soon', 'expire', 'suspended', 'deleted',
            'identity', 'verify', 'lost', 'forever', 'suspicious', 'locked',
            'last chance', 'action required', 'respond now', 'time-sensitive',
            'limited time', 'don\'t delay', 'asap', 'right away', 'closing',
            'failure to', 'will be', 'must be', 'termination', 'deactivated',
            'unauthorized', 'unusual activity', 'confirm your', 'update your',
            'reactivate', 'restore access', 'without delay'
        ]
        self.financial_keywords = [
            'deposit', 'payment', 'refund', 'security amount', 'bank', 
            'upi', '₹', 'fee', 'money', 'transaction', 'credit card', 'invoice',
            'wire transfer', 'bitcoin', 'crypto', 'wallet', 'prize', 'lottery',
            'won', 'claim', 'cash', 'gift card', 'bonus', 'compensation',
            'salary', 'payroll', 'billing', 'overdue', 'outstanding',
            'account number', 'routing number', 'ssn', 'social security',
            'tax refund', 'irs', 'revenue', 'customs', 'shipping fee'
        ]
        self.social_engineering_keywords = [
            'click here', 'click below', 'download', 'open attachment',
            'enable macros', 'enable content', 'log in', 'sign in',
            'update now', 'confirm now', 'click the link', 'tap here',
            'dear customer', 'dear user', 'dear sir', 'dear madam',
            'congratulations', 'you have been selected', 'you are a winner',
            'help me', 'confidential', 'secret', 'private', 'personal',
            'do not share', 'keep this between us', 'trust me',
            'i am a prince', 'inheritance', 'beneficiary', 'next of kin'
        ]
        self.credential_harvest_keywords = [
            'password', 'username', 'login credentials', 'otp',
            'one time', 'verification code', 'security code', 'pin',
            'cvv', 'expiry date', 'date of birth', 'mother\'s maiden',
            'security question', 'reset password', 'change password',
            'two-factor', '2fa', 'authentication', 'token'
        ]
        self.brands = {
            'google': 'google.com',
            'microsoft': 'microsoft.com',
            'amazon': 'amazon.com',
            'apple': 'apple.com',
            'paypal': 'paypal.com',
            'netflix': 'netflix.com',
            'facebook': 'facebook.com',
            'instagram': 'instagram.com',
            'whatsapp': 'whatsapp.com',
            'linkedin': 'linkedin.com',
            'twitter': 'twitter.com',
            'university': 'edu.in',
            'government': 'gov.in',
            'bank': 'bank.com',
            'hdfc': 'hdfcbank.com',
            'icici': 'icicibank.com',
            'sbi': 'sbi.co.in',
            'wells fargo': 'wellsfargo.com',
            'chase': 'chase.com'
        }
        self.suspicious_tlds = [
            '.xyz', '.support', '.info', '.top', '.icu', '.club',
            '.buzz', '.work', '.online', '.site', '.fun', '.space',
            '.click', '.link', '.win', '.loan', '.racing', '.review',
            '.stream', '.gq', '.ml', '.cf', '.tk', '.ga'
        ]
        self.shorteners = [
            'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'rebrand.ly',
            'is.gd', 'v.gd', 'cutt.ly', 'shorturl.at', 'rb.gy',
            'tiny.cc', 'ow.ly'
        ]

    def extract_all(self, text: str) -> tuple[Dict[str, float], list[str]]:
        text_lower = text.lower()
        
        trigger_words = []
        
        urg_s, urg_w = self.get_urgency_score(text_lower)
        fin_s, fin_w = self.get_financial_score(text_lower)
        imp_s, imp_w = self.get_impersonation_score(text_lower, text)
        url_s, url_w = self.get_url_risk_score(text_lower)
        soc_s, soc_w = self.get_social_engineering_score(text_lower)
        cred_s, cred_w = self.get_credential_harvest_score(text_lower)
        struct_s = self.get_structural_score(text)
        
        trigger_words.extend(urg_w)
        trigger_words.extend(fin_w)
        trigger_words.extend(imp_w)
        trigger_words.extend(url_w)
        trigger_words.extend(soc_w)
        trigger_words.extend(cred_w)
        
        # Unique and cleaned
        trigger_words = list(set([w for w in trigger_words if w]))

        features = {
            "urgency_score": urg_s,
            "financial_score": fin_s,
            "impersonation_score": imp_s,
            "url_risk_score": url_s,
            "social_engineering_score": soc_s,
            "credential_harvest_score": cred_s,
            "structural_score": struct_s
        }
        
        return features, trigger_words

    def get_urgency_score(self, text: str) -> tuple[float, list[str]]:
        words = [word for word in self.urgency_keywords if word in text]
        # More aggressive scaling - even 2 urgency words is suspicious
        return min(len(words) / 2.0, 1.0), words

    def get_financial_score(self, text: str) -> tuple[float, list[str]]:
        words = [word for word in self.financial_keywords if word in text]
        return min(len(words) / 2.0, 1.0), words

    def get_social_engineering_score(self, text: str) -> tuple[float, list[str]]:
        words = [word for word in self.social_engineering_keywords if word in text]
        return min(len(words) / 2.0, 1.0), words

    def get_credential_harvest_score(self, text: str) -> tuple[float, list[str]]:
        words = [word for word in self.credential_harvest_keywords if word in text]
        return min(len(words) / 2.0, 1.0), words

    def get_structural_score(self, text: str) -> float:
        """Analyze text structure for phishing indicators."""
        score = 0.0
        
        # Excessive caps (shouting)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            score += 0.3
        
        # Multiple exclamation/question marks
        if text.count('!') >= 3 or text.count('?') >= 3:
            score += 0.2
        
        # Grammar red flags: generic greetings
        generic_greetings = ['dear customer', 'dear user', 'dear valued', 'dear account holder', 'dear sir/madam']
        if any(g in text.lower() for g in generic_greetings):
            score += 0.3
        
        # Presence of IP addresses in text (common in phishing)
        if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', text):
            score += 0.4
        
        # HTML tags in plain text (phishing attempt)
        if re.search(r'<a\s+href|<img\s+src|<form|onclick', text, re.IGNORECASE):
            score += 0.5
        
        # Unusual character mixing (e.g., Cyrillic lookalikes)
        if re.search(r'[а-яА-Я]', text):
            score += 0.4

        return min(score, 1.0)

    def get_impersonation_score(self, text_lower: str, original_text: str) -> tuple[float, list[str]]:
        # Check for brand mentions
        found_brands = [brand for brand in self.brands if brand in text_lower]
        if not found_brands:
            return 0.0, []

        # Try to find a URL/Domain in the text to compare
        urls = re.findall(r'https?://([a-zA-Z0-9.-]+)', original_text)
        if not urls:
            # Brand mentioned but no URL - slightly suspicious
            return 0.4, found_brands
        
        for url in urls:
            url_domain = url.lower()
            for brand in found_brands:
                official_domain = self.brands[brand]
                
                # Brand name in text but NOT in the actual URL domain
                if brand in text_lower and brand not in url_domain:
                    return 1.0, found_brands
                
                # Check for lookalike/homoglyph domains
                lookalike_patterns = [
                    brand.replace('o', '0'), brand.replace('i', '1'),
                    brand.replace('l', '1'), brand.replace('a', '4'),
                    brand.replace('e', '3'), brand.replace('s', '5'),
                    brand.replace('g', '9'), brand + '-', '-' + brand
                ]
                if any(p in url_domain for p in lookalike_patterns if p != brand):
                    return 1.0, [url_domain] + found_brands

                # Check if the brand appears as a subdomain of a different domain
                # e.g., google.malicious-site.com
                if brand in url_domain and official_domain not in url_domain:
                    return 0.9, [url_domain] + found_brands

        return 0.2, found_brands

    def get_url_risk_score(self, text: str) -> tuple[float, list[str]]:
        score = 0.0
        words = []
        # Check for shortened URLs
        for s in self.shorteners:
            if s in text:
                score += 0.5
                words.append(s)
        
        # Check for suspicious TLDs
        for tld in self.suspicious_tlds:
            if tld in text:
                score += 0.5
                words.append(tld)
            
        # Check for misspelled/lookalike domains (simple heuristic)
        match = re.search(r'[0-9]+[a-z]{5,}', text)
        if match:
            score += 0.3
            words.append(match.group())

        # Check for @ symbol in URL (credential stuffing)
        if re.search(r'https?://[^/]*@', text):
            score += 0.6
            words.append('@-in-url')

        # Very long URLs (> 75 chars) are suspicious
        long_urls = re.findall(r'https?://\S{75,}', text)
        if long_urls:
            score += 0.3
            words.append('very-long-url')

        return min(score, 1.0), words
