from typing import Dict, List

class ExplainabilityEngine:
    def generate_explanation(self, ml_prob: float, url_risk: float, url_signals: List[str], features: Dict[str, float], final_risk: float, trigger_words: List[str] = None) -> Dict:
        analysis_signals = []
        severity = "Low"
        if final_risk > 0.7: severity = "High"
        elif final_risk > 0.3: severity = "Medium"

        # --- Determine threat type ---
        threat_type = self._classify_threat_type(features, ml_prob, url_risk)

        # 1. URL Intelligence
        if url_risk > 0.3:
            analysis_signals.append({
                "type": "URL_INTELLIGENCE",
                "severity": "Critical" if final_risk > 0.8 else "High",
                "message": "The web link uses a suspicious pattern: " + (" | ".join(url_signals) if url_signals else "Generic risk detected")
            })

        # 2. ML Contribution
        if ml_prob > 0.6:
            analysis_signals.append({
                "type": "NLP_ANALYSIS",
                "severity": "High",
                "message": f"Our AI model identified language patterns common in scams ({(ml_prob*100):.1f}% match)."
            })

        # 3. Urgency signals
        if features.get("urgency_score", 0) > 0.5:
            analysis_signals.append({
                "type": "URGENCY",
                "severity": "Medium",
                "message": "This message tries to rush you into making a decision using time pressure."
            })

        # 4. Financial signals
        if features.get("financial_score", 0) > 0.5:
            analysis_signals.append({
                "type": "FINANCIAL",
                "severity": "High",
                "message": "Detected requests for unusual payments, bank details, or cryptocurrency."
            })

        # 5. Social engineering signals
        if features.get("social_engineering_score", 0) > 0.3:
            analysis_signals.append({
                "type": "SOCIAL_ENGINEERING",
                "severity": "High",
                "message": "This message uses psychological manipulation tactics like fake authority, trust-building, or call-to-action pressure."
            })

        # 6. Credential harvesting signals
        if features.get("credential_harvest_score", 0) > 0.3:
            analysis_signals.append({
                "type": "CREDENTIAL_HARVEST",
                "severity": "Critical",
                "message": "This message is attempting to steal your login credentials, passwords, OTPs, or personal identification data."
            })

        # 7. Structural anomalies
        if features.get("structural_score", 0) > 0.3:
            analysis_signals.append({
                "type": "STRUCTURAL",
                "severity": "Medium",
                "message": "The message has structural red flags: excessive caps, generic greetings, or embedded code/IP addresses."
            })

        # 8. Brand impersonation
        if features.get("impersonation_score", 0) > 0.3:
            analysis_signals.append({
                "type": "IMPERSONATION",
                "severity": "Critical",
                "message": "A trusted brand name was found but the source doesn't match the official domain. This is likely brand impersonation."
            })

        # Summary output
        return {
            "final_risk_score": round(final_risk * 100, 2),
            "severity": severity,
            "threat_type": threat_type,
            "plain_explanation": self._get_plain_explanation(severity, final_risk, threat_type, features),
            "breakdown": {
                "ml_probability": round(ml_prob * 100, 2),
                "url_risk": round(url_risk * 100, 2),
                "text_heuristic": {k: round(v * 100, 2) for k, v in features.items()}
            },
            "signals": analysis_signals,
            "recommendations": self._get_recommendations(severity, final_risk, threat_type, features)
        }

    def _classify_threat_type(self, features: Dict, ml_prob: float, url_risk: float) -> str:
        """Determine the primary threat category."""
        scores = {
            "Phishing": (
                features.get("impersonation_score", 0) * 0.4 +
                features.get("credential_harvest_score", 0) * 0.3 +
                url_risk * 0.3
            ),
            "Social Engineering": (
                features.get("social_engineering_score", 0) * 0.4 +
                features.get("urgency_score", 0) * 0.3 +
                features.get("structural_score", 0) * 0.3
            ),
            "Financial Fraud": (
                features.get("financial_score", 0) * 0.5 +
                features.get("urgency_score", 0) * 0.25 +
                features.get("social_engineering_score", 0) * 0.25
            ),
            "Credential Theft": (
                features.get("credential_harvest_score", 0) * 0.5 +
                url_risk * 0.3 +
                features.get("urgency_score", 0) * 0.2
            )
        }
        
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        if best_score < 0.15:
            return "Safe"
        return best_type

    def _get_plain_explanation(self, severity, risk, threat_type, features) -> str:
        if threat_type == "Safe" or risk < 0.2:
            return "This message appears safe. No significant threat indicators were detected by our AI engine."
        
        explanations = {
            "Phishing": {
                "High": "DANGER: This is a phishing attack. The sender is pretending to be a trusted brand or organization to trick you into revealing personal information. The link provided does NOT belong to the real company. Do NOT click any links or provide any data.",
                "Medium": "WARNING: This message shows signs of a phishing attempt. Someone may be impersonating a known brand. Verify the sender's identity through official channels before taking any action.",
                "Low": "A few minor phishing indicators were found, but the threat level is low. Stay cautious and verify any links before clicking."
            },
            "Social Engineering": {
                "High": "DANGER: This is a social engineering attack. The sender is using psychological manipulation - creating urgency, fear, or false authority - to make you act without thinking. This is a common tactic used by scammers.",
                "Medium": "WARNING: This message uses manipulation tactics like time pressure and emotional triggers. Be skeptical and verify claims through independent channels.",
                "Low": "Some manipulation language was detected, but it may not be malicious. Proceed with normal caution."
            },
            "Financial Fraud": {
                "High": "DANGER: This is a financial fraud attempt. The message is trying to extract money from you through fake fees, prizes, refunds, or payment requests. Legitimate organizations never ask for money this way.",
                "Medium": "WARNING: This message contains financial requests that are suspicious. Never send money or share financial details based on unsolicited messages.",
                "Low": "Minor financial language detected. This may be legitimate, but verify any payment requests independently."
            },
            "Credential Theft": {
                "High": "DANGER: This message is trying to steal your login credentials. It wants your password, OTP, or security codes. No legitimate service will ever ask for these via email or text message.",
                "Medium": "WARNING: This message is asking for sensitive authentication data. Never share passwords, PINs, or OTPs through messages or emails.",
                "Low": "Some credential-related language detected. Be careful about sharing login information."
            }
        }
        
        category = explanations.get(threat_type, explanations["Phishing"])
        return category.get(severity, category.get("Low", "Exercise caution with this message."))

    def _get_recommendations(self, severity, risk, threat_type="Phishing", features=None) -> List[str]:
        base_recs = []
        
        if risk > 0.7:
            base_recs = [
                "Do NOT click any links or download attachments.",
                "Report this sender to your IT department immediately.",
                "Delete the message after reporting.",
                "If you already clicked a link, change your passwords immediately."
            ]
        elif risk > 0.3:
            base_recs = [
                "Verify the sender's identity through a different channel (phone call or official website).",
                "Hover over any links to see the real destination URL.",
                "Be cautious if they are asking for personal information.",
                "Check the sender's email address carefully for misspellings."
            ]
        else:
            return ["Always stay vigilant, but this message looks okay."]

        # Add threat-specific recommendations
        if features:
            if features.get("credential_harvest_score", 0) > 0.3:
                base_recs.append("NEVER share passwords, OTPs, or PINs via email or text. Legitimate services never ask for these.")
            if features.get("financial_score", 0) > 0.3:
                base_recs.append("Verify any payment requests by contacting the organization directly through their official website.")
            if features.get("impersonation_score", 0) > 0.5:
                base_recs.append("Type the company's URL directly into your browser instead of clicking the link in this message.")

        return base_recs
