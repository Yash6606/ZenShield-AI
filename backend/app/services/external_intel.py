import requests
import re
from typing import Dict, List

class ExternalIntelService:
    def __init__(self):
        # In a real app, you'd load these from .env
        self.vt_api_key = None 
        self.ip_api_url = "http://ip-api.com/json/"

    def get_url_intel(self, url: str) -> Dict:
        """
        Simulates VirusTotal + WHOIS lookup
        """
        # Extract domain
        domain_match = re.search(r'https?://([a-zA-Z0-9.-]+)', url)
        domain = domain_match.group(1) if domain_match else "unknown"
        
        # Mocking External Scores
        # In real world: requests.get(f"https://www.virustotal.com/api/v3/domains/{domain}")
        mock_score = 0
        if "bit.ly" in domain or "xyz" in domain or "univeristy" in domain:
            mock_score = 42 # 42/70 engines flagged it
        
        return {
            "domain": domain,
            "vt_score": f"{mock_score}/70",
            "engines_flagged": ["Kaspersky", "Symantec", "Google Safe Browsing"] if mock_score > 0 else [],
            "whois_age": "23 days" if mock_score > 0 else "4 years",
            "registrar": "NameCheap (Private)" if mock_score > 0 else "Google LLC",
            "global_rank": "None" if mock_score > 0 else "Top 1M"
        }

    def get_ip_location(self, ip_address: str = "") -> Dict:
        """
        Get geolocation for map visualization
        """
        try:
            # Using a public API for demo purposes
            # If ip_address is empty, it uses the server's IP
            resp = requests.get(self.ip_api_url + ip_address, timeout=2)
            data = resp.json()
            return {
                "lat": data.get("lat", 0),
                "lon": data.get("lon", 0),
                "city": data.get("city", "Unknown"),
                "country": data.get("country", "Unknown"),
                "isp": data.get("isp", "Local")
            }
        except:
            return {"lat": 20, "lon": 77, "city": "Mumbai", "country": "India", "isp": "Local"}
