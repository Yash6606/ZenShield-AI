import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import io
import os
from datetime import datetime

class VisionService:
    def __init__(self):
        # Tesseract path might need to be set for Windows
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.model_path = os.path.join(os.path.dirname(__file__), '../../models/forgery_model.joblib')
        self.forgery_model = None
        if os.path.exists(self.model_path):
            try:
                import joblib
                self.forgery_model = joblib.load(self.model_path)
                print("Forgery detection model loaded.")
            except:
                print("Failed to load forgery model.")

    def perform_ela(self, image_bytes, quality=90):
        original = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Optimization: Use BytesIO instead of disk
        temp_buffer = io.BytesIO()
        original.save(temp_buffer, 'JPEG', quality=quality)
        temp_buffer.seek(0)
        temporary = Image.open(temp_buffer)
        
        diff = ImageChops.difference(original, temporary)
        diff_np = np.array(diff)
        
        # Baseline manipulation score
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0: max_diff = 1
        
        # ML score if model available
        ml_score = 0
        if self.forgery_model:
            features = [np.mean(diff_np), np.max(diff_np), np.std(diff_np)]
            prob = self.forgery_model.predict_proba([features])[0][1]
            ml_score = int(prob * 100)
            
        scale = 255.0 / max_diff
        diff = ImageEnhance.Brightness(diff).enhance(scale)
        
        # Combine scores
        ela_score = min(100, max_diff * 2)
        final_score = max(ela_score, ml_score) if ml_score > 0 else ela_score
        
        return diff, final_score

    def deep_ui_audit(self, img):
        """
        Detects anomalies in UI elements that suggest spoofing (Deepfake UI).
        """
        if img is None: return 0
        
        score = 0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Edge Density Analysis (Spoofed logos often have jagged edges)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges) / (img.shape[0] * img.shape[1])
        if edge_density > 50: score += 15
        
        # 2. Color Histogram Variance (Fake login pages often have inconsistent LUTs)
        hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        if np.std(hist) > 1000: score += 20
        
        return min(score, 100)

    def extract_intel(self, image_bytes):
        # 0. Optimization: Fast Resize for Speed
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            h, w = img.shape[:2]
            if w > 1000: # Resize if too large
                scale = 1000 / w
                img = cv2.resize(img, (int(w*scale), int(h*scale)))
                # Re-encode for ELA
                _, buffer = cv2.imencode('.jpg', img)
                image_bytes = buffer.tobytes()
        except:
            img = None

        # 1. OCR (Fast Mode) - Fail Safe
        text = ""
        try:
            if img is not None:
                text = pytesseract.image_to_string(img, config='--psm 3')
        except Exception as e:
            text = ""

        # 2. QR Code Detection
        qr_results = []
        try:
            if img is not None:
                detector = cv2.QRCodeDetector()
                data, _, _ = detector.detectAndDecode(img)
                if data:
                    qr_results.append({"data": data, "type": "URL/Text"})
        except:
            pass
        
        # 3. Deepfake UI Audit
        deepfake_score = self.deep_ui_audit(img)

        # 4. Forgery Analysis (ELA)
        manipulation_score = 0
        try:
            _, manipulation_score = self.perform_ela(image_bytes)
        except:
            pass

        return {
            "extracted_text": text.strip(),
            "qr_codes": qr_results,
            "manipulation_score": manipulation_score,
            "deepfake_ui_score": deepfake_score,
            "analysis_timestamp": datetime.now().isoformat(),
            "verdict": "CRITICAL: UI Manipulation Detected" if deepfake_score > 30 else "Suspicious" if manipulation_score > 30 else "Likely Clean"
        }


