# auth.py - Version optimisée avec design épuré et couleurs attractives
import hashlib
import json
import os
import re
from datetime import datetime
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass, asdict

@dataclass
class UserProfile:
    """Structure de données pour le profil utilisateur"""
    username: str
    email: str = ""
    full_name: str = ""
    niveau: str = ""
    interests: List[str] = None
    ville: str = ""
    avatar_color: str = "#FF6B6B"
    created_at: str = ""
    last_login: str = ""
    preferences: Dict = None
    
    def __post_init__(self):
        if self.interests is None:
            self.interests = []
        if self.preferences is None:
            self.preferences = {"theme": "light", "notifications": True}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class AuthManager:
    """Gestionnaire d'authentification simple et efficace"""

    def __init__(self, storage_path: str = "users.json"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        """Crée le fichier de stockage s'il n'existe pas"""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

    def _load_users(self) -> Dict:
        """Charge les utilisateurs"""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_users(self, users: Dict):
        """Sauvegarde les utilisateurs"""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)

    def _hash_password(self, password: str) -> str:
        """Hashage simple du mot de passe"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str) -> Tuple[bool, str]:
        """Inscription d'un nouvel utilisateur"""
        username = username.strip().lower()
        
        if not username or len(username) < 3:
            return False, "❌ Nom d'utilisateur trop court (min 3 caractères)"
        
        if not password or len(password) < 4:
            return False, "❌ Mot de passe trop court (min 4 caractères)"
        
        users = self._load_users()
        
        if username in users:
            return False, "❌ Ce nom d'utilisateur existe déjà"
        
        users[username] = {
            "password": self._hash_password(password),
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "profile": {
                "username": username,
                "interests": [],
                "ville": "",
                "niveau": ""
            },
            "login_count": 1
        }
        
        self._save_users(users)
        return True, "✅ Inscription réussie ! Bienvenue sur CareerBridge AI 🎉"

    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        """Connexion utilisateur"""
        username = username.strip().lower()
        users = self._load_users()
        
        user = users.get(username)
        
        if not user:
            return False, "❌ Utilisateur non trouvé", None
        
        if user["password"] != self._hash_password(password):
            return False, "❌ Mot de passe incorrect", None
        
        # Mise à jour de la dernière connexion
        user["last_login"] = datetime.now().isoformat()
        user["login_count"] = user.get("login_count", 0) + 1
        self._save_users(users)
        
        return True, "✅ Connexion réussie !", user.get("profile", {})

    def update_profile(self, username: str, profile_data: dict) -> bool:
        """Met à jour le profil utilisateur"""
        username = username.strip().lower()
        users = self._load_users()
        
        if username not in users:
            return False
        
        current_profile = users[username].get("profile", {})
        current_profile.update(profile_data)
        users[username]["profile"] = current_profile
        users[username]["updated_at"] = datetime.now().isoformat()
        
        self._save_users(users)
        return True

    def get_profile(self, username: str) -> dict:
        """Récupère le profil utilisateur"""
        username = username.strip().lower()
        users = self._load_users()
        return users.get(username, {}).get("profile", {})
    
    def get_user_stats(self, username: str) -> dict:
        """Récupère les statistiques utilisateur"""
        username = username.strip().lower()
        users = self._load_users()
        user = users.get(username, {})
        
        return {
            "login_count": user.get("login_count", 0),
            "created_at": user.get("created_at", ""),
            "last_login": user.get("last_login", "")
        }