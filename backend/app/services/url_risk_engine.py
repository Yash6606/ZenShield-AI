import re
from urllib.parse import urlparse
from typing import Dict, List, Tuple

class URLRiskEngine:
    def __init__(self):
        self.brands = ["google", "microsoft", "government", "bank", "university", "amazon", "paypal"]
        self.high_risk_tlds = [".xyz", ".support", ".info", ".top", ".online", ".site", ".icu"]
        self.shorteners = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "rebrand.ly"]
        self.risk_keyword_combos = [
            ("payment", "verify"),
            ("login", "security"),
            ("internship", "deposit"),
            ("refund", "claim"),
            ("account", "suspended"),
            ("verify", "identity"),
            ("account", "deleted")
        ]
        self.substitutions = {'0': 'o', '1': 'l', '4': 'a', '3': 'e', '5': 's', '8': 'b'}

    def levenshtein(self, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return self.levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def extract_urls(self, text: str) -> List[str]:
        return re.findall(r'https?://\S+', text)

    def analyze_url(self, url: str) -> Dict:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # 1. Domain Extraction
        parts = netloc.split('.')
        tld = "." + parts[-1] if len(parts) > 1 else ""
        domain = parts[-2] if len(parts) > 1 else parts[0]
        subdomain = ".".join(parts[:-2]) if len(parts) > 2 else ""

        risk_score = 0.0
        signals = []
        brand_impersonation = False
        suspicious_typo = False

        # 2. Brand Similarity & Typosquatting
        normalized_domain = domain
        for digit, char in self.substitutions.items():
            normalized_domain = normalized_domain.replace(digit, char)

        for brand in self.brands:
            # Direct mention check but not exact match
            if brand in normalized_domain and normalized_domain != brand:
                risk_score += 0.35
                brand_impersonation = True
                signals.append(f"Brand similarity detected: {brand}")
            
            # Levenshtein distance check for typo domains
            if 0 < self.levenshtein(normalized_domain, brand) <= 2 and normalized_domain != brand:
                risk_score += 0.35
                suspicious_typo = True
                signals.append(f"Potential typosquatting detected for: {brand}")

        # 3. Suspicious TLD
        if tld in self.high_risk_tlds:
            risk_score += 0.2
            signals.append(f"High-risk TLD detected: {tld}")

        # 4. HTTP Protocol Check
        if parsed.scheme == "http":
            risk_score += 0.15
            signals.append("Insecure protocol: HTTP used instead of HTTPS")

        # 5. Excessive Subdomain Length
        if subdomain.count('-') > 2 or len(subdomain) > 20:
            risk_score += 0.15
            signals.append("Suspicious subdomain complexity")

        # 6. Shortened URL Detection
        if netloc in self.shorteners:
            risk_score += 0.25
            signals.append("Shortened URL hiding destination")

        # 7. Keyword Combo Risk
        url_text = domain + path
        for k1, k2 in self.risk_keyword_combos:
            if k1 in url_text and k2 in url_text:
                risk_score += 0.25
                signals.append(f"Malicious keyword combo in URL: {k1}, {k2}")

        # Hard Override Rule
        is_hard_override = False
        if brand_impersonation and (tld in self.high_risk_tlds or suspicious_typo):
            is_hard_override = True

        return {
            "url": url,
            "risk_score": min(risk_score, 1.0),
            "signals": signals,
            "is_hard_override": is_hard_override
        }

    def get_aggregate_risk(self, text: str) -> Tuple[float, List[str], bool]:
        urls = self.extract_urls(text)
        if not urls:
            return 0.0, [], False
        
        max_risk = 0.0
        all_signals = []
        any_override = False
        
        for url in urls:
            analysis = self.analyze_url(url)
            if analysis["risk_score"] > max_risk:
                max_risk = analysis["risk_score"]
            all_signals.extend(analysis["signals"])
            if analysis["is_hard_override"]:
                any_override = True
                
        return max_risk, list(set(all_signals)), any_override
