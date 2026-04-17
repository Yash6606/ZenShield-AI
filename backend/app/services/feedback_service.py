import json
import os
from datetime import datetime

class FeedbackService:
    def __init__(self):
        self.feedback_file = os.path.join(os.path.dirname(__file__), '../../data/user_feedback.json')
        os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w') as f:
                json.dump([], f)

    def save_feedback(self, text: str, initial_score: float, user_label: str, confidence: float):
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "initial_score": initial_score,
            "user_label": user_label, # 'correct' or 'incorrect'
            "confidence": confidence
        }
        
        with open(self.feedback_file, 'r+') as f:
            data = json.load(f)
            data.append(feedback_entry)
            f.seek(0)
            json.dump(data, f, indent=4)
        
        return {"status": "success", "message": "Feedback captured for model refinement."}

    def get_feedback_stats(self):
        with open(self.feedback_file, 'r') as f:
            data = json.load(f)
        return {
            "total_reports": len(data),
            "false_positives": len([x for x in data if x['user_label'] == 'incorrect']),
            "verified_threats": len([x for x in data if x['user_label'] == 'correct'])
        }
