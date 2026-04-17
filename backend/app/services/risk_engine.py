from typing import Dict

class RiskEngine:
    def __init__(self):
        # Weight distribution across all signal sources
        self.weights = {
            "ml_weight": 0.30,
            "url_weight": 0.25,
            "text_heuristic_weight": 0.45
        }

    def calculate_risk(self, ml_prob: float, url_risk: float, text_features: Dict[str, float], url_override: bool) -> float:
        """
        Final Risk = (ML * 0.30) + (URL * 0.25) + (Heuristic_Composite * 0.45)
        
        Heuristic composite now includes 6 sub-signals:
        - urgency, financial, impersonation, social engineering, credential harvesting, structural
        """
        
        # Calculate composite text heuristic risk from all sub-signals
        text_heuristic_risk = (
            text_features.get("urgency_score", 0.0) * 0.20 +
            text_features.get("financial_score", 0.0) * 0.15 +
            text_features.get("impersonation_score", 0.0) * 0.25 +
            text_features.get("social_engineering_score", 0.0) * 0.20 +
            text_features.get("credential_harvest_score", 0.0) * 0.10 +
            text_features.get("structural_score", 0.0) * 0.10
        )
        text_heuristic_risk = min(text_heuristic_risk, 1.0)

        # Base hybrid score
        weighted_score = (
            (ml_prob * self.weights["ml_weight"]) +
            (url_risk * self.weights["url_weight"]) +
            (text_heuristic_risk * self.weights["text_heuristic_weight"])
        )

        # --- Override Rules (hard floor for high-confidence detections) ---

        # 1. Brand impersonation + suspicious TLD/typo = almost certainly phishing
        if url_override:
            weighted_score = max(weighted_score, 0.95)
        
        # 2. Strong brand impersonation alone
        if text_features.get("impersonation_score", 0) > 0.8:
            weighted_score = max(weighted_score, 0.88)

        # 3. Classic phishing trifecta: urgency + financial + impersonation
        if (text_features.get("urgency_score", 0) > 0.5 and 
            text_features.get("financial_score", 0) > 0.5 and 
            text_features.get("impersonation_score", 0) > 0.5):
            weighted_score = max(weighted_score, 0.85)

        # 4. Social engineering + credential harvesting = credential phishing
        if (text_features.get("social_engineering_score", 0) > 0.5 and
            text_features.get("credential_harvest_score", 0) > 0.5):
            weighted_score = max(weighted_score, 0.80)

        # 5. Urgency + credential harvesting = account takeover attempt
        if (text_features.get("urgency_score", 0) > 0.5 and
            text_features.get("credential_harvest_score", 0) > 0.5):
            weighted_score = max(weighted_score, 0.78)

        # 6. Multiple moderate signals stacking = suspicious
        moderate_count = sum(1 for v in text_features.values() if v > 0.3)
        if moderate_count >= 4:
            weighted_score = max(weighted_score, 0.70)

        # Ensure normalized range 0.0 - 1.0
        final_score = max(0.0, min(weighted_score, 1.0))
        
        return final_score
