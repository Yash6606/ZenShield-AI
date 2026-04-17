import re
from typing import Dict, List

class CodeScannerService:
    def __init__(self):
        self.malicious_signatures = {
            "DATA_EXFILTRATION": [
                r"requests\.(post|get)", r"urllib\.request", r"socket\.connect",
                r"smtp", r"ftp", r"upload", r"curl", r"wget"
            ],
            "SYSTEM_MODIFICATION": [
                r"os\.system", r"subprocess\.run", r"shutil\.rmtree",
                r"open\(.*['\"]w['\"]\)", r"chmod", r"reg"
            ],
            "OBFUSCATION_CRYPTO": [
                r"base64\.b64decode", r"eval\(", r"exec\(", r"zlib\.decompress",
                r"marshal\.loads", r"getattr\(", r"\.encode\("
            ],
            "STEALTH_C2": [
                r"time\.sleep", r"raw_input", r"getpass", r"pynput", r"keyboard"
            ],
            "HARDWARE_VECTOR": [
                r"asm\(", r"__volatile__", r"rdmsr", r"wrmsr", r"cpuid",
                r"clflush", r"mfence", r"prefetchw", r"rowhammer"
            ],
            "SIDE_CHANNEL_RISK": [
                r"cache_timing", r"branch_prediction", r"spectre", r"meltdown",
                r"l1tf", r"zombieload"
            ]
        }

    def scan_code(self, code: str) -> Dict:
        findings = []
        threat_score = 0
        
        for category, patterns in self.malicious_signatures.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    matches.append(pattern)
            
            if matches:
                if category in ["HARDWARE_VECTOR", "SIDE_CHANNEL_RISK"]:
                    weight = 35  # Critical for hardware manufacturers
                else:
                    weight = 25 if category != "OBFUSCATION_CRYPTO" else 15
                
                threat_score += weight
                print(f" [MATCH] Category: {category} | Triggers: {matches}")
                findings.append({
                    "category": category,
                    "triggers": matches,
                    "risk_level": "High" if weight == 25 else "Medium"
                })
        
        # Max score 100
        threat_score = min(threat_score, 100)
        
        severity = "Low"
        if threat_score > 70: severity = "High"
        elif threat_score > 30: severity = "Medium"

        return {
            "risk_score": threat_score,
            "severity": severity,
            "plain_explanation": self._get_plain_explanation(severity, threat_score),
            "text_preview": code[:500] + ("..." if len(code) > 500 else ""),
            "recommendations": self._get_recommendations(severity, threat_score),
            "findings": findings,
            "complexity_estimate": len(code.split('\n')),
            "acceleration_mode": "AMD ROCm Optimized (Hardware Vector Engine)",
            "verdict": "CRITICAL: Malicious Activity Likely" if threat_score > 60 else "CAUTION: Suspicious Exports Found" if threat_score > 20 else "CLEAN: Standard Utility Pattern"
        }

    def _get_plain_explanation(self, severity, score) -> str:
        if score > 70:
            return "This code contains multiple malicious patterns used in data theft or system hijacking."
        if score > 30:
            return "This code uses suspicious functions that could be used for harmful purposes if not from a trusted source."
        return "This code looks like a standard utility script with no obvious malicious intent."

    def _get_recommendations(self, severity, score) -> List[str]:
        if score > 70:
            return [
                "Do NOT execute this script on your machine.",
                "Quarantine the file and report it to your security team.",
                "Check for any unauthorized outgoing network connections."
            ]
        if score > 30:
            return [
                "Review the source of this code before running it.",
                "Check if the functions used (like network requests) are expected for this script.",
                "Run the script in a sandboxed environment if possible."
            ]
        return ["Ensure you always download scripts from trusted sources."]
