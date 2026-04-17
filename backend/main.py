from fastapi import FastAPI, HTTPException, Response, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.services.ai_service import AIService
from app.services.reporting import ReportingService
from app.services.feedback_service import FeedbackService
from app.services.external_intel import ExternalIntelService
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import time
import os
from app.services.history_service import HistoryService
from app.services.training_service import TrainingService
from app.services.auth_service import AuthService
from app.utils.vercel import sync_data_to_tmp, get_storage_path

# Sync local data to /tmp on Vercel deployment
sync_data_to_tmp()

app = FastAPI(title="ZenShield AI Backend", description="Next-Gen Hardware-Accelerated Cybersecurity Platform")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService()
reporting_service = ReportingService()
feedback_service = FeedbackService()
external_intel = ExternalIntelService()
history_service = HistoryService()
training_service = TrainingService(history_service=history_service)
auth_service = AuthService()

class MessageRequest(BaseModel):
    text: str
    model_type: Optional[str] = 'rf'
    token: Optional[str] = None

class FeedbackRequest(BaseModel):
    text: str
    initial_score: float
    user_label: str
    confidence: float

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
async def root():
    return {"status": "online", "message": "ZenShield AI Engine is running"}

@app.post("/auth/signup")
async def signup(request: SignupRequest):
    result = auth_service.signup(request.username, request.email, request.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/auth/login")
async def login(request: LoginRequest):
    result = auth_service.login(request.username, request.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

@app.post("/auth/logout")
async def logout(token: str):
    auth_service.logout(token)
    return {"success": True}

@app.get("/auth/validate")
async def validate_token(token: str):
    user = auth_service.validate_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"success": True, "user": user}

@app.post("/analyze")
async def analyze(request: MessageRequest):
    start_time = time.time()
    result = ai_service.analyze_message(request.text, request.model_type)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    user = auth_service.validate_token(request.token) if request.token else None
    user_id = user["id"] if user else 0

    history_service.add_entry("phishing", {
        "text_preview": request.text[:50],
        "risk_score": result.get('risk_score', 0),
        "severity": result.get('severity', 'Low'),
        "verdict": result.get('verdict', 'Safe')
    }, user_id=user_id)
    end_time = time.time()
    result["latency"] = f"{int((end_time - start_time) * 1000)}ms"
    return result

@app.post("/vision/analyze")
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    result = ai_service.analyze_image_threat(contents)
    return result

@app.post("/script/analyze")
async def analyze_script(request: Dict):
    if "code" not in request:
        raise HTTPException(status_code=400, detail="Missing code field")
    return ai_service.scan_script(request["code"])



# --- New Features Routes ---

@app.post("/report/generate")
async def generate_report(analysis_result: Dict):
    filename, path = reporting_service.generate_threat_report(analysis_result)
    return {"filename": filename, "download_url": f"/report/download/{filename}"}

@app.get("/report/download/{filename}")
async def download_report(filename: str):
    path = get_storage_path("reports", filename)
    if os.path.exists(path):
        return FileResponse(path, media_type='application/pdf', filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

@app.post("/feedback")
async def save_feedback(request: FeedbackRequest):
    return feedback_service.save_feedback(request.text, request.initial_score, request.user_label, request.confidence)



# --- Existing Metrics ---

@app.get("/metrics")
async def get_metrics(token: Optional[str] = None):
    user = auth_service.validate_token(token) if token else None
    user_id = user["id"] if user else 0
    
    m = ai_service.get_metrics()
    m["feedback_stats"] = feedback_service.get_feedback_stats()
    m["awareness_stats"] = history_service.get_awareness_stats(user_id=user_id)
    return m

@app.get("/history")
async def get_history(token: Optional[str] = None):
    user = auth_service.validate_token(token) if token else None
    user_id = user["id"] if user else 0
    return history_service.get_history(user_id=user_id)

@app.get("/training/scenarios")
async def get_scenarios():
    return training_service.get_scenarios()

@app.post("/training/check")
async def check_training(scenario_id: int, verdict: str, token: Optional[str] = None):
    user = auth_service.validate_token(token) if token else None
    user_id = user["id"] if user else 0
    return training_service.check_answer(scenario_id, verdict, user_id=user_id)

@app.get("/report/awareness")
async def get_awareness_report(token: Optional[str] = None):
    user = auth_service.validate_token(token) if token else None
    user_id = user["id"] if user else 0
    
    stats = history_service.get_awareness_stats(user_id=user_id)
    # Mock analysis result for a general awareness report
    report_data = {
        "risk_score": 100 - stats["current_score"],
        "text_preview": "Aggregated User Awareness Audit",
        "breakdown": {
            "overall_security_score": stats["current_score"],
            "total_incidents": len(history_service.get_history(user_id=user_id))
        },
        "signals": [f"Current User Awareness Score: {stats['current_score']}%"],
        "suggested_action": "Continue with interactive training modules to improve survival rate."
    }
    filename, path = reporting_service.generate_threat_report(report_data)
    return FileResponse(path, filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
