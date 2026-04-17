# 🛡️ ZenShield AI: Next-Gen Cybersecurity Awareness Platform

**Winning the fight against phishing with AMD-Accelerated AI.**

---

## 🚀 Project Overview
ZenShield AI is a professional-grade cybersecurity platform designed to protect users from modern phishing and social engineering threats. Unlike traditional security tools that only block threats, ZenShield **educates** users through interactive exams and **audits** security posture using hardware-accelerated AI on **AMD ROCm**.

---

## 🛠️ Detailed File & Architecture Breakdown

### 📂 Backend (FastAPI / Python)
The backend is built with a modular service-oriented architecture, ensuring separation of concerns and scalability.

#### 📍 Entry Points
*   **`agent.py`**: The "Heart" of ZenShield. 
    *   Starts the FastAPI server in a background thread.
    *   Creates a **Windows System Tray Icon** for easy access.
    *   Initializes the **Real-time Folder Monitor** to watch for malicious file downloads.
*   **`main.py`**: The API Gateway.
    *   Defines all RESTful endpoints (Phishing analysis, Training, History, Reports).
    *   Handles JWT-based authentication middleware.

#### ⚙️ Core Services (`backend/app/services/`)
*   **`auth_service.py`**: Manages user identity. Handles password hashing (SHA-256), session token generation, and secure login/signup workflows.
*   **`protection_service.py`**: A background watcher using the `watchdog` library. It monitors the **Project Directory** and **Windows Downloads Folder** for new files.
*   **`code_scanner.py`**: The heuristic engine for script analysis. It looks for dangerous API calls (socket connections, system commands, obfuscation) and assigns a risk score to `.py`, `.js`, and `.bat` files.
*   **`ai_service.py`**: Orchestrates high-level AI analysis. It combines NLP (text analysis) and heuristic scores to determine if a message is a phish.
*   **`intelligence.py`**: Orchestrates threat-intelligence gathering, combining internal heuristic data with external intelligence signals.
*   **`feature_engineering.py`**: A specialized engine that converts raw text and email headers into mathematical vectors (TF-IDF) for the machine learning models.
*   **`training_service.py`**: Powers the **Security Awareness Exam**. contains the 10 core scenarios and checks user answers against security best practices.
*   **`history_service.py`**: Implements **Data Isolation**. Each user has their own `history_{user_id}.json` file, ensuring their scan history and scores are private.
*   **`vision_service.py`**: Analyzes uploaded images/screenshots for visual forgery markers, deepfake UI elements, and malicious metadata.
*   **`reporting.py`**: A PDF generation engine built with `FPDF`. Creates professional, brand-ready security audit reports with one click.
*   **`url_risk_engine.py`**: Performs real-time domain reputation checks and WHOIS age analysis to identify "burner" domains used in phishing.
*   **`risk_engine.py`**: The "Decider". It weights inputs from the AI engine, URL engine, and vision service to produce the final **Multi-Vector Risk Score**.
*   **`feedback_service.py`**: Allows users to "teach" the AI. When a user marks a result as correct/incorrect, this service logs the data for future model retraining.
*   **`explainability.py`**: The **XAI (Explainable AI)** layer. It translates complex model weights into "Plain English" explanations that users can understand.

#### 🗃️ Data & Models
*   **`data/users.json`**: Persistent storage for encrypted user credentials.
*   **`models/*.joblib`**: Pre-trained Random Forest and TF-IDF models used for text and forgery classification.

---

### 📂 Frontend (React / Tailwind / Framer Motion)
The frontend is a premium, dark-themed dashboard designed for maximum visual impact and smooth user experience.

*   **`src/App.jsx`**: The main application logic.
    *   **State Management**: Tracks current scan results, user session, and training progress.
    *   **Component Logic**: Houses the Sidebar, Dashboard, Phishing Audit Tab, Script Audit Tab, and the new **Security Exam** module.
    *   **Animations**: Uses `Framer Motion` for all transitions, giving it a high-end feel.
*   **`src/index.css`**: Contains the design system, including Glassmorphism effects, custom gradients, and Tailwind utilities.

---

## 🏆 Hardware Acceleration (AMD ROCm)
ZenShield is uniquely optimized for **AMD hardware**:
1.  **Local Inference**: No data ever leaves the local machine. All AI scans happen on the AMD NPU/GPU.
2.  **ROCm Integration**: We leverage `onnxruntime-rocm` and `bitsandbytes` (where applicable) to ensure high-speed tensor operations on Radeon™ systems.
3.  **Low Latency**: Analysis that takes seconds on a CPU happens in milliseconds on AMD hardware.

---

## ⚙️ How to Run

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python agent.py
```
*(Check your system tray for the ZenShield icon!)*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*(Open http://localhost:5173)*

---

## 🌟 Pitch Highlights for Judges
*   **AI Explainability**: We don't just say "Threat Detected"; we explain *why* in plain English.
*   **Gamified Learning**: The 10-question exam turns security into a challenge rather than a chore.
*   **Real-time Protection**: The moment a user downloads a malicious `.py` file, ZenShield notifies them via Windows Desktop Alerts.
*   **Data Integrity**: Per-user isolation and SHA-256 security ensure a professional-ready architecture.

---

**ZenShield AI — Because the best firewall is a well-trained user with hardware-accelerated protection.**
