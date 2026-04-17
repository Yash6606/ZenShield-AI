import json
import os
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Optional
from app.utils.vercel import get_storage_path

class AuthService:
    def __init__(self):
        self.users_file = get_storage_path("data", "users.json")
        self.sessions_file = get_storage_path("data", "sessions.json")
        
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w') as f:
                json.dump({}, f)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _load_users(self) -> list:
        with open(self.users_file, 'r') as f:
            return json.load(f)

    def _save_users(self, users: list):
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=4)

    def _load_sessions(self) -> dict:
        with open(self.sessions_file, 'r') as f:
            return json.load(f)

    def _save_sessions(self, sessions: dict):
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=4)

    def signup(self, username: str, email: str, password: str) -> Dict:
        users = self._load_users()
        
        # Check if username or email already exists
        for user in users:
            if user['username'].lower() == username.lower():
                return {"success": False, "error": "Username already taken"}
            if user['email'].lower() == email.lower():
                return {"success": False, "error": "Email already registered"}
        
        # Validate inputs
        if len(username) < 3:
            return {"success": False, "error": "Username must be at least 3 characters"}
        if len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        if '@' not in email or '.' not in email:
            return {"success": False, "error": "Invalid email address"}

        new_user = {
            "id": len(users) + 1,
            "username": username,
            "email": email,
            "password_hash": self._hash_password(password),
            "created_at": datetime.now().isoformat(),
            "role": "analyst"
        }
        users.append(new_user)
        self._save_users(users)

        # Auto-login after signup
        token = self._create_session(new_user)
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": new_user["id"],
                "username": new_user["username"],
                "email": new_user["email"],
                "role": new_user["role"]
            }
        }

    def login(self, username: str, password: str) -> Dict:
        users = self._load_users()
        password_hash = self._hash_password(password)
        
        for user in users:
            if (user['username'].lower() == username.lower() or 
                user['email'].lower() == username.lower()):
                if user['password_hash'] == password_hash:
                    token = self._create_session(user)
                    return {
                        "success": True,
                        "token": token,
                        "user": {
                            "id": user["id"],
                            "username": user["username"],
                            "email": user["email"],
                            "role": user["role"]
                        }
                    }
                else:
                    return {"success": False, "error": "Incorrect password"}
        
        return {"success": False, "error": "User not found"}

    def _create_session(self, user: dict) -> str:
        token = secrets.token_hex(32)
        sessions = self._load_sessions()
        sessions[token] = {
            "user_id": user["id"],
            "username": user["username"],
            "created_at": datetime.now().isoformat()
        }
        self._save_sessions(sessions)
        return token

    def validate_token(self, token: str) -> Optional[Dict]:
        sessions = self._load_sessions()
        session = sessions.get(token)
        if not session:
            return None
        
        users = self._load_users()
        for user in users:
            if user["id"] == session["user_id"]:
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"]
                }
        return None

    def logout(self, token: str) -> bool:
        sessions = self._load_sessions()
        if token in sessions:
            del sessions[token]
            self._save_sessions(sessions)
            return True
        return False
