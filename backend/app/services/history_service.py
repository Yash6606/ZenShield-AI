import json
import os
from datetime import datetime
from typing import List, Dict
from app.utils.vercel import get_storage_path

class HistoryService:
    def __init__(self):
        self.data_dir = get_storage_path("data")

    def _get_user_file(self, user_id: int) -> str:
        return os.path.join(self.data_dir, f'history_{user_id}.json')

    def _load_history(self, user_id: int) -> list:
        filepath = self._get_user_file(user_id)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                json.dump([], f)
            return []
        with open(filepath, 'r') as f:
            return json.load(f)

    def _save_history(self, user_id: int, history: list):
        filepath = self._get_user_file(user_id)
        with open(filepath, 'w') as f:
            json.dump(history, f, indent=4)

    def add_entry(self, entry_type: str, result: Dict, user_id: int = 0):
        history = self._load_history(user_id)
        
        new_entry = {
            "id": len(history) + 1,
            "timestamp": datetime.now().isoformat(),
            "type": entry_type,
            "result": result
        }
        history.append(new_entry)
        self._save_history(user_id, history)
        
        return new_entry

    def get_history(self, user_id: int = 0) -> List[Dict]:
        return self._load_history(user_id)

    def get_awareness_stats(self, user_id: int = 0) -> Dict:
        history = self._load_history(user_id)
        # New users start at 100% - score drops for each high risk found
        score = 100
        trend = []
        
        for entry in history:
            risk = entry.get('result', {}).get('risk_score', 0)
            if risk > 70: score -= 5
            elif risk > 30: score -= 2
            
            trend.append({
                "date": entry['timestamp'][:10],
                "score": max(0, score)
            })

        return {
            "current_score": max(0, score),
            "trend": trend[-10:],
            "history_points": [t['score'] for t in trend[-20:]],
            "total_scans": len(history),
            "risk_counts": {
                "high": len([e for e in history if e.get('result', {}).get('risk_score', 0) > 70]),
                "medium": len([e for e in history if 30 < e.get('result', {}).get('risk_score', 0) <= 70]),
                "low": len([e for e in history if e.get('result', {}).get('risk_score', 0) <= 30])
            }
        }
