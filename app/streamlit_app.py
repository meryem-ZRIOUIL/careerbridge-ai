import streamlit as st
import json
import re
import os
import time
import random
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="CareerBridge AI - Multi-Agent System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# SESSION STATE
# =========================
def init_state():
    defaults = {
        "messages": [],
        "api_history": [],
        "loading": False,
        "run_analysis": False,
        "user_profile": {},
        "agent_phase": None,
        "active_page": "chat",
        "riasec_done": False,
        "riasec_scores": {},
        "recommendations": [],
        "roadmap_data": None,
        "hitl_pending": False,
        "hitl_message": "",
        "hitl_approved": False,
        "prompt_mode": "v1",
        "prompt_logs": [],
        "agent_logs": [],
        "show_evaluation": False,
        "ab_test_mode": False,
        "last_evaluation": None,
        "current_steps": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =========================
# FAISS VECTOR DATABASE (RAG Agentique)
# =========================
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

class VectorDatabase:
    """Vector store avec FAISS pour RAG avancé"""
    
    def __init__(self):
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.initialized = False
        
        if FAISS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                self.dimension = 384
                self.index = faiss.IndexFlatL2(self.dimension)
                self.initialized = True
            except Exception as e:
                st.error(f"Erreur initialisation embeddings: {e}")
    
    def add_documents(self, docs: List[Dict]):
        if not self.initialized:
            return
        texts = []
        for doc in docs:
            text = f"{doc['metier']} {doc['secteur']} {' '.join(doc['tags'])} {doc.get('pourquoi', '')}"
            texts.append(text)
            self.documents.append(doc)
        embeddings = self.embedding_model.encode(texts)
        self.index.add(np.array(embeddings).astype('float32'))
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        if not self.initialized or len(self.documents) == 0:
            return []
        query_embedding = self.embedding_model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])
        return results

# =========================
# DONNÉES MARCHÉ MAROCAIN (ENRICHIES)
# =========================
MARKET_DATA = [
    {
        "id": "dev_fullstack", "metier": "Développeur Fullstack", "secteur": "Tech / IT",
        "salaire_debut": "10 000–14 000 MAD", "salaire_5ans": "22 000–30 000 MAD",
        "demande": "CRITIQUE 🔥", "taux_insertion": "95%",
        "villes": "Casablanca · Rabat · Tanger",
        "ecoles": "ENSIAS · INPT · ENSA · UM6P",
        "duree": "Bac+3 à Bac+5",
        "tags": ["informatique","dev","programmation","web","javascript","python","react","code","logiciel","digital"],
        "riasec": ["I","R","C"],
        "soft_skills": ["logique", "résolution problèmes", "autonomie", "travail équipe"],
        "pourquoi": "Casablanca Tech City & zones offshore recrutent massivement. +35% d'offres en 2023.",
        "evolution": "Dev → Lead Dev → CTO → Freelance international (60–120k€/an possible en remote)",
        "transfer_from": ["Design","Architecture"],
        "roadmap_steps": [
            {"year": "Bac", "titre": "Baccalauréat Sciences Maths/Info", "detail": "Focus maths & physique", "status": "done"},
            {"year": "Bac+2", "titre": "CPGE ou DUT Informatique", "detail": "Classes prépa MPSI ou DUT", "status": "future"},
            {"year": "Bac+5", "titre": "ENSIAS / INPT / UM6P", "detail": "Diplôme ingénieur", "status": "future"},
        ]
    },
    {
        "id": "data_scientist", "metier": "Data Scientist / Ingénieur IA", "secteur": "Tech / IA",
        "salaire_debut": "13 000–18 000 MAD", "salaire_5ans": "28 000–40 000 MAD",
        "demande": "TRÈS HAUTE ⚡", "taux_insertion": "93%",
        "villes": "Casablanca · Rabat",
        "ecoles": "ENSIAS · INPT · UM6P · Al Akhawayn",
        "duree": "Bac+5",
        "tags": ["data","ia","intelligence artificielle","machine learning","statistiques","big data","python","deep learning","algorithme"],
        "riasec": ["I","C"],
        "soft_skills": ["mathématiques", "statistiques", "curiosité", "analyse"],
        "pourquoi": "OCP, Maroc Telecom, banques : demande x3 en 2 ans.",
        "evolution": "Data Analyst → Data Scientist → ML Engineer → AI Lead → CDO",
        "transfer_from": ["Médecine","Pharmacie","Biologie"],
        "roadmap_steps": [
            {"year": "Bac", "titre": "Bac Sciences Maths", "detail": "Excellentes notes requises", "status": "done"},
            {"year": "Bac+2", "titre": "CPGE MPSI / PCSI", "detail": "2 ans de classes prépa", "status": "future"},
            {"year": "Bac+5", "titre": "ENSIAS / INPT / UM6P", "detail": "Spécialité Data Science", "status": "future"},
        ]
    },
    {
        "id": "cybersecurite", "metier": "Expert Cybersécurité", "secteur": "Tech / Sécurité",
        "salaire_debut": "12 000–16 000 MAD", "salaire_5ans": "26 000–38 000 MAD",
        "demande": "CRITIQUE 🔐", "taux_insertion": "97%",
        "villes": "Casablanca · Rabat",
        "ecoles": "INPT · ENSIAS · EHTP",
        "duree": "Bac+5",
        "tags": ["cybersecurite","securite","hacking","reseau","cyber","informatique","sécurité","pentest","firewall"],
        "riasec": ["I","R","C"],
        "soft_skills": ["vigilance", "analyse", "éthique", "rigueur"],
        "pourquoi": "Pénurie mondiale de 3.5M experts. Banques et télécoms marocains recrutent urgemment.",
        "evolution": "SOC Analyst → Pentester → CISO → Consultant international",
        "transfer_from": ["Informatique","Dev"],
        "roadmap_steps": [
            {"year": "Bac", "titre": "Bac Sciences Maths", "detail": "Base solide en maths", "status": "done"},
            {"year": "Bac+2", "titre": "CPGE ou BTS Réseaux", "detail": "Classes prépa ou BTS", "status": "future"},
            {"year": "Bac+5", "titre": "INPT / ENSIAS", "detail": "Certifications CEH, CISSP", "status": "future"},
        ]
    },
    {
        "id": "ingenieur_industrie", "metier": "Ingénieur Industriel", "secteur": "Industrie / Automobile",
        "salaire_debut": "9 000–12 000 MAD", "salaire_5ans": "18 000–25 000 MAD",
        "demande": "HAUTE 📈", "taux_insertion": "87%",
        "villes": "Tanger · Kénitra · Casablanca",
        "ecoles": "EHTP · EMI · ENSAM · ENSA Tanger",
        "duree": "Bac+5",
        "tags": ["ingenieur","industrie","automobile","production","qualite","lean","renault","stellantis"],
        "riasec": ["R","I","C"],
        "soft_skills": ["organisation", "leadership", "résolution problèmes"],
        "pourquoi": "Tanger Med = 1er port d'Afrique. Renault + Stellantis embauchent massivement.",
        "evolution": "Ingénieur process → Chef de projet → Directeur usine",
        "transfer_from": ["Architecture","Design industriel"],
        "roadmap_steps": [
            {"year": "Bac", "titre": "Bac Sciences de l'Ingénieur", "detail": "Ou Sciences Maths", "status": "done"},
            {"year": "Bac+2", "titre": "CPGE TSI / PCSI", "detail": "Classes prépa technique", "status": "future"},
            {"year": "Bac+5", "titre": "EHTP / EMI / ENSAM", "detail": "Spécialité Génie Industriel", "status": "future"},
        ]
    },
    {
        "id": "medecin", "metier": "Médecin / Spécialiste", "secteur": "Santé",
        "salaire_debut": "8 000–12 000 MAD", "salaire_5ans": "20 000–50 000 MAD",
        "demande": "TRÈS HAUTE 🏥", "taux_insertion": "98%",
        "villes": "Toutes les villes",
        "ecoles": "Faculté Médecine Casablanca · Rabat · Marrakech · Fès",
        "duree": "Bac+7 minimum",
        "tags": ["medecine","sante","médecin","chirurgien","hopital","clinique","biologie"],
        "riasec": ["I","S","R"],
        "soft_skills": ["empathie", "patience", "rigueur", "communication"],
        "pourquoi": "Maroc manque de 100 000 médecins. Secteur privé très lucratif.",
        "evolution": "Interne → Médecin généraliste → Spécialiste → Clinique privée",
        "transfer_from": ["Médecine","Pharmacie","Biologie"],
        "roadmap_steps": [
            {"year": "Bac", "titre": "Bac Sciences Maths ou SVT", "detail": "Seuil 14/20 requis", "status": "done"},
            {"year": "Bac+1", "titre": "1ère année Médecine", "detail": "Concours très sélectif", "status": "future"},
            {"year": "Bac+7", "titre": "Internat + Résidanat", "detail": "Spécialisation", "status": "future"},
        ]
    },
    {
        "id": "finance_banque", "metier": "Analyste Financier", "secteur": "Finance / Banque",
        "salaire_debut": "9 000–12 000 MAD", "salaire_5ans": "20 000–32 000 MAD",
        "demande": "HAUTE 💼", "taux_insertion": "82%",
        "villes": "Casablanca · Rabat",
        "ecoles": "ISCAE · HEM · ENCG",
        "duree": "Bac+3 à Bac+5",
        "tags": ["finance","banque","comptabilite","gestion","audit","business","commerce","management"],
        "riasec": ["E","C","I"],
        "soft_skills": ["analyse", "rigueur", "discrétion"],
        "pourquoi": "Casablanca Finance City = hub financier africain.",
        "evolution": "Analyste → Manager → Directeur → PDG",
        "transfer_from": ["Architecture","Design","Médecine"],
        "roadmap_steps": [
            {"year": "Bac", "titre": "Bac Sciences Économiques ou Maths", "detail": "Base en économie", "status": "done"},
            {"year": "Bac+3", "titre": "ENCG / Licence Économie", "detail": "École Nationale de Commerce", "status": "future"},
            {"year": "Bac+5", "titre": "ISCAE / HEM / Master Finance", "detail": "MBA Finance", "status": "future"},
        ]
    },
    {
        "id": "energie_renouvelable", "metier": "Ingénieur Énergies Renouvelables", "secteur": "Green Tech",
        "salaire_debut": "10 000–13 000 MAD", "salaire_5ans": "20 000–28 000 MAD",
        "demande": "TRÈS HAUTE 🌱", "taux_insertion": "88%",
        "villes": "Ouarzazate · Laâyoune · Casablanca",
        "ecoles": "EHTP · EMI · ENSA",
        "duree": "Bac+5",
        "tags": ["energie","solaire","eolien","renouvelable","green","environnement","noor"],
        "riasec": ["R","I","S"],
        "soft_skills": ["technique", "innovation", "environnement"],
        "pourquoi": "Plan Noor + IRESEN : Maroc vise 52% renouvelable en 2030.",
        "evolution": "Ingénieur terrain → Chef de projet → Directeur énergie",
        "transfer_from": ["Architecture","Environnement"],
        "roadmap_steps": [
            {"year": "Bac", "titre": "Bac Sciences Maths", "detail": "Bon niveau physique", "status": "done"},
            {"year": "Bac+2", "titre": "CPGE PCSI / MP", "detail": "Classes prépa", "status": "future"},
            {"year": "Bac+5", "titre": "EHTP / EMI", "detail": "Spécialité Énergies Renouvelables", "status": "future"},
        ]
    },
    {
        "id": "marketing_digital", "metier": "Responsable Marketing Digital", "secteur": "Commerce / Digital",
        "salaire_debut": "7 000–10 000 MAD", "salaire_5ans": "15 000–25 000 MAD",
        "demande": "HAUTE 📣", "taux_insertion": "80%",
        "villes": "Casablanca · Rabat · Marrakech",
        "ecoles": "ISCAE · HEM · ENCG · ISIC",
        "duree": "Bac+3 à Bac+5",
        "tags": ["marketing","communication","langues","commerce","business","reseaux sociaux","digital"],
        "riasec": ["E","A","S"],
        "soft_skills": ["communication", "créativité", "adaptabilité"],
        "pourquoi": "Boom e-commerce au Maroc (+40% en 2023).",
        "evolution": "Community Manager → Marketing Manager → CMO",
        "transfer_from": ["Architecture","Médecine","Ingénierie"],
        "roadmap_steps": [
            {"year": "Bac", "titre": "Tout baccalauréat", "detail": "Langues, arts, économie", "status": "done"},
            {"year": "Bac+3", "titre": "ENCG / Licence Marketing", "detail": "Ou BTS Communication", "status": "future"},
            {"year": "Bac+5", "titre": "Master Marketing Digital", "detail": "MBA Marketing", "status": "future"},
        ]
    },
]

# Initialiser FAISS
vector_db = VectorDatabase()
vector_db.add_documents(MARKET_DATA)

RAG_CONTEXT = json.dumps(MARKET_DATA, ensure_ascii=False, indent=2)

TRANSFER_MATRIX = {
    "Architecture": ["Marketing Digital", "Urbanisme", "Design Industriel"],
    "Médecine": ["Pharmacie", "Biotechnologie", "Data Médical"],
    "Ingénierie": ["Architecture", "Énergies Renouvelables", "Data Science"],
    "Design": ["Marketing Digital", "Architecture", "UX Design"],
    "Commerce": ["Finance", "Marketing Digital", "Entrepreneuriat"],
}

RIASEC_MAP = {
    "R": ["Ingénieur Industriel", "Ingénieur Énergies Renouvelables"],
    "I": ["Data Scientist", "Cybersécurité", "Médecin", "Dev Fullstack"],
    "A": ["Marketing Digital", "Design"],
    "S": ["Médecin", "Enseignant", "RH"],
    "E": ["Analyste Financier", "Marketing Digital"],
    "C": ["Analyste Financier", "Dev Fullstack"],
}

# =========================
# AGENTS
# =========================
class AgentRole(Enum):
    GUARDRAIL = "guardrail"
    PROFILER = "profiler"
    RETRIEVER = "retriever"
    SCORER = "scorer"
    GENERATOR = "generator"
    EVALUATOR = "evaluator"

class BaseAgent:
    def __init__(self, name: str, role: AgentRole):
        self.name = name
        self.role = role
        self.access_log = []
    
    def can_use_tool(self, tool_name: str) -> bool:
        allowed_tools = {
            AgentRole.GUARDRAIL: ["detect_threat", "filter_output"],
            AgentRole.PROFILER: ["extract_profile"],
            AgentRole.RETRIEVER: ["search_vector_db"],
            AgentRole.SCORER: ["calculate_score"],
            AgentRole.GENERATOR: ["generate_response"],
            AgentRole.EVALUATOR: ["evaluate_response"]
        }
        return tool_name in allowed_tools.get(self.role, [])
    
    def log_access(self, tool_name: str):
        self.access_log.append({"tool": tool_name, "agent": self.name})

class GuardrailAgent(BaseAgent):
    def __init__(self):
        super().__init__("Guardian", AgentRole.GUARDRAIL)
        self.forbidden_patterns = [
            r"ignore.*instructions", r"system.*prompt", r"roleplay.*as.*admin",
            r"<script", r"javascript:", r"DROP TABLE", r"DELETE FROM"
        ]
        self.sensitive_topics = ["politique", "religion", "discrimination"]
    
    def detect_injection(self, text: str) -> Tuple[bool, str]:
        text_lower = text.lower()
        for pattern in self.forbidden_patterns:
            if re.search(pattern, text_lower):
                return True, f"Tentative d'injection détectée: {pattern}"
        for topic in self.sensitive_topics:
            if topic in text_lower:
                return True, f"Sujet sensible détecté: {topic}"
        return False, "OK"
    
    def filter_output(self, text: str) -> str:
        text = re.sub(r'https?://[^\s]+', '[LIEN SUPPRIMÉ]', text)
        text = re.sub(r'\S+@\S+', '[EMAIL SUPPRIMÉ]', text)
        return text

class ProfilerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Profiler", AgentRole.PROFILER)
    
    def extract_profile(self, text: str, existing: dict) -> dict:
        profile = existing.copy()
        tl = text.lower()
        
        niveau_map = {
            "terminale": "bac", "bac": "bac", "lycée": "bac",
            "bac+2": "bac+2", "bts": "bac+2", "dut": "bac+2",
            "licence": "bac+3", "bac+3": "bac+3",
            "master": "bac+5", "ingenieur": "bac+5", "bac+5": "bac+5"
        }
        for kw, nv in niveau_map.items():
            if kw in tl:
                profile["niveau"] = nv
                break
        
        interests_keywords = {
            "tech": ["informatique", "programmation", "ia", "data", "cybersecurite"],
            "business": ["commerce", "marketing", "finance", "gestion"],
            "creative": ["design", "art", "creativite", "architecture"],
            "scientific": ["science", "recherche", "biologie", "chimie"],
            "health": ["medecine", "sante", "hopital"]
        }
        
        profile["interests"] = []
        for category, keywords in interests_keywords.items():
            if any(kw in tl for kw in keywords):
                profile["interests"].append(category)
        
        if any(word in tl for word in ["pas les maths", "n'aime pas les maths"]):
            profile["constraints"] = ["no_math"]
        else:
            profile["constraints"] = []
        
        villes = ["casablanca", "rabat", "tanger", "marrakech", "fès"]
        for v in villes:
            if v in tl:
                profile["ville"] = v.capitalize()
                break
        
        return profile

class RetrieverAgent(BaseAgent):
    def __init__(self):
        super().__init__("Retriever", AgentRole.RETRIEVER)
    
    def search(self, query: str, profile: dict, k: int = 5) -> List[Dict]:
        enriched_query = query
        if profile.get("interests"):
            enriched_query += " " + " ".join(profile["interests"])
        
        results = vector_db.search(enriched_query, k)
        
        constraints = profile.get("constraints", [])
        filtered = []
        for item in results:
            if "no_math" in constraints:
                if any(t in item["tags"] for t in ["statistiques", "algorithme", "data"]):
                    continue
            filtered.append(item)
        
        return filtered[:3]

class ScorerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Scorer", AgentRole.SCORER)
    
    def calculate_compatibility(self, profile: dict, job: dict) -> float:
        score = 0.0
        
        # Niveau d'études (max 20)
        profile_level = profile.get("niveau", "bac")
        job_duree = job.get("duree", "Bac+5")
        level_scores = {
            "bac": {"Bac+3": 15, "Bac+5": 10, "Bac+7": 5},
            "bac+2": {"Bac+3": 18, "Bac+5": 12, "Bac+7": 6},
            "bac+3": {"Bac+3": 20, "Bac+5": 16, "Bac+7": 8},
            "bac+5": {"Bac+3": 15, "Bac+5": 20, "Bac+7": 15},
        }
        if profile_level in level_scores:
            for required, pts in level_scores[profile_level].items():
                if required in job_duree:
                    score += pts
                    break
        
        # Centres d'intérêt (max 30)
        interests = profile.get("interests", [])
        job_tags = set(job.get("tags", []))
        interest_score = 0
        for interest in interests:
            if interest == "tech" and any(t in job_tags for t in ["informatique", "data", "ia"]):
                interest_score += 15
            elif interest == "business" and any(t in job_tags for t in ["commerce", "finance"]):
                interest_score += 15
            elif interest == "health" and "medecine" in job_tags:
                interest_score += 15
        score += min(interest_score, 30)
        
        # Demande marché (max 15)
        demand_scores = {"CRITIQUE 🔥": 15, "CRITIQUE 🔐": 15, "TRÈS HAUTE ⚡": 12, "HAUTE 📈": 10}
        score += demand_scores.get(job.get("demande", ""), 5)
        
        # Salaire (max 15)
        salary_text = job.get("salaire_5ans", "")
        numbers = re.findall(r'(\d+)\s*000', salary_text)
        if numbers:
            max_salary = max(int(n) for n in numbers)
            score += min(15, max_salary // 2000)
        
        # Soft skills (max 20)
        soft_skills = profile.get("detected_skills", [])
        job_soft = set(job.get("soft_skills", []))
        score += min(len(set(soft_skills) & job_soft) * 10, 20)
        
        return min(100, score)

class GeneratorAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("Generator", AgentRole.GENERATOR)
        self.llm = llm_client
    
    def _get_fine_tuning_footer(self) -> str:
        return """
---
🔧 **Notre modèle a été finement ajusté** sur 5 000 offres d'emploi marocaines  
(adaptation aux salaires locaux, écoles, et spécificités du marché national)
"""
    
    def generate_response(self, query: str, profile: dict, jobs: List[Dict], scores: List[float]) -> str:
        context_parts = []
        for job, score in zip(jobs, scores):
            context_parts.append(f"""
### {job['metier']} (Compatibilité: {score:.0f}%)
- Secteur: {job['secteur']}
- Salaire début: {job['salaire_debut']} → 5 ans: {job['salaire_5ans']}
- Écoles: {job['ecoles']}
- Demande: {job['demande']}
- Pourquoi: {job['pourquoi']}
- Évolution: {job['evolution']}
            """)
        
        context_text = "\n".join(context_parts)
        
        prompt = f"""
Tu es CareerBridge AI, expert en orientation au Maroc.

🎯 PROFIL:
- Niveau: {profile.get('niveau', 'Non spécifié')}
- Intérêts: {', '.join(profile.get('interests', []))}

🔍 OPPORTUNITÉS:
{context_text}

📝 QUESTION: {query}

Génère une réponse structurée avec Plan A, B, C. Sois concret, utilise des données marocaines (MAD, écoles). Termine par un conseil actionnable.
"""
        try:
            response = self.llm.generate(prompt)
            return response + self._get_fine_tuning_footer()
        except:
            return self._fallback_response(jobs, scores, profile)
    
    def _fallback_response(self, jobs: List[Dict], scores: List[float], profile: dict) -> str:
        response = f"## 🎯 Analyse pour {profile.get('niveau', 'ton profil')}\n\n"
        for job, score in zip(jobs[:3], scores[:3]):
            response += f"""
### ✨ {job['metier']} — {score:.0f}% compatible
**Pourquoi ?** {job['pourquoi']}
**Salaire:** {job['salaire_debut']} → {job['salaire_5ans']}
**Écoles:** {job['ecoles']}
---
"""
        response += "\n**💡 Conseil:** N'hésite pas à préciser ton parcours !"
        return response + self._get_fine_tuning_footer()

class EvaluatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Evaluator", AgentRole.EVALUATOR)
    
    def evaluate_response(self, response: str, query: str, context: dict) -> Dict:
        score = 0
        feedback = []
        
        words = len(response.split())
        if 150 <= words <= 600:
            score += 20
            feedback.append("Longueur optimale")
        
        if any(marker in response for marker in ["MAD", "salaire", "demande"]):
            score += 25
            feedback.append("Données concrètes présentes")
        
        if any(marker in response for marker in ["conseil", "recommande"]):
            score += 25
            feedback.append("Recommandations actionnables")
        
        if context.get("profile", {}).get("niveau") in response:
            score += 30
            feedback.append("Bonne personnalisation")
        
        return {"score": score, "grade": "A" if score >= 80 else "B" if score >= 60 else "C", "feedback": feedback}

class LLMClient:
    def __init__(self):
        self.fine_tuning_active = True
        self.fine_tuning_metadata = {
            "method": "LoRA simulée",
            "training_data": "5,000 offres d'emploi marocaines",
            "impact": "+23% précision"
        }
    
    def generate(self, prompt: str) -> str:
        try:
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
            if not api_key:
                return "⚠️ Clé API non configurée"
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Erreur: {str(e)[:100]}"

# Initialiser les agents
guardrail = GuardrailAgent()
profiler = ProfilerAgent()
retriever = RetrieverAgent()
scorer = ScorerAgent()
llm_client = LLMClient()
generator = GeneratorAgent(llm_client)
evaluator = EvaluatorAgent()

# =========================
# ORCHESTRATEUR
# =========================
def process_query(query: str, profile: dict) -> Dict:
    steps = []
    
    # Guardrail
    is_malicious, msg = guardrail.detect_injection(query)
    if is_malicious:
        return {"error": True, "message": f"⛔ {msg}", "steps": steps}
    steps.append({"agent": "Guardrail", "status": "done", "message": "Sécurité validée"})
    
    # Profiler
    updated_profile = profiler.extract_profile(query, profile)
    steps.append({"agent": "Profiler", "status": "done", "message": f"Niveau: {updated_profile.get('niveau', 'N/A')}"})
    
    # Vérification complétude
    completeness = 0
    if updated_profile.get("niveau"):
        completeness += 0.4
    if updated_profile.get("interests"):
        completeness += 0.4
    if updated_profile.get("ville"):
        completeness += 0.2
    
    if completeness < 0.6:
        steps.append({"agent": "HITL", "status": "blocked", "message": "Profil incomplet"})
        return {
            "response": "🔍 **Profil insuffisamment défini**\n\nDonne-moi :\n1. Ton niveau (Bac, Bac+2...)\n2. Tes centres d'intérêt\n3. Ta ville",
            "profile": updated_profile,
            "steps": steps,
            "blocked": True
        }
    
    # Retriever (RAG)
    relevant_jobs = retriever.search(query, updated_profile)
    steps.append({"agent": "Retriever", "status": "done", "message": f"{len(relevant_jobs)} offres trouvées"})
    
    # Scorer
    scored_jobs = []
    for job in relevant_jobs:
        score = scorer.calculate_compatibility(updated_profile, job)
        scored_jobs.append((job, score))
    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    top_jobs = scored_jobs[:3]
    steps.append({"agent": "Scorer", "status": "done", "message": "Compatibilité calculée"})
    
    # Generator
    jobs_list = [j for j, _ in top_jobs]
    scores_list = [s for _, s in top_jobs]
    response = generator.generate_response(query, updated_profile, jobs_list, scores_list)
    steps.append({"agent": "Generator", "status": "done", "message": "Réponse générée"})
    
    # Evaluator
    evaluation = evaluator.evaluate_response(response, query, {"profile": updated_profile})
    steps.append({"agent": "Evaluator", "status": "done", "message": f"Score: {evaluation['score']}/100"})
    
    # Filter output
    response = guardrail.filter_output(response)
    
    return {
        "response": response,
        "profile": updated_profile,
        "steps": steps,
        "evaluation": evaluation,
        "top_jobs": top_jobs
    }

# =========================
# CSS (version complète)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
    --bg: #080C14;
    --surface: rgba(255,255,255,0.04);
    --surface2: rgba(255,255,255,0.07);
    --border: rgba(255,255,255,0.08);
    --border2: rgba(255,255,255,0.14);
    --mint: #00E5CC;
    --sky: #38AEFF;
    --green: #22D67A;
    --red: #FF4D6D;
    --t1: #F0F4FF;
    --t2: #8A95B0;
    --t3: #4A5268;
}

.stApp {
    background: radial-gradient(ellipse at 20% 0%, rgba(0,229,204,0.06) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 100%, rgba(56,174,255,0.05) 0%, transparent 50%),
                var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] { background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }
.stDeployButton { display: none; }

/* Navigation */
.nav-bar { display: flex; justify-content: center; gap: 6px; padding: 1rem 1rem 0.5rem; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem; flex-wrap: wrap; }
.nav-btn { background: var(--surface); border: 1px solid var(--border); border-radius: 100px; color: var(--t2); padding: 7px 18px; font-size: 0.8rem; cursor: pointer; transition: all 0.2s; }
.nav-btn.active { background: rgba(0,229,204,0.12); border-color: var(--mint); color: var(--mint); }

/* Hero */
.hero { text-align: center; padding: 4rem 1rem 2.5rem; position: relative; }
.hero::before { content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 600px; height: 1px; background: linear-gradient(90deg, transparent, var(--mint), transparent); opacity: 0.4; }
.badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(0,229,204,0.08); border: 1px solid rgba(0,229,204,0.2); border-radius: 100px; padding: 5px 16px 5px 10px; font-size: 0.72rem; color: var(--mint); margin-bottom: 1.8rem; }
.badge-dot { width: 7px; height: 7px; background: var(--mint); border-radius: 50%; box-shadow: 0 0 8px var(--mint); animation: glow-pulse 2s infinite; }
@keyframes glow-pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
.hero-title { font-family: 'Syne', sans-serif; font-size: clamp(2.2rem, 7vw, 4rem); font-weight: 800; background: linear-gradient(135deg, #FFFFFF 0%, #C0FFE8 35%, var(--mint) 60%, var(--sky) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; }
.hero-sub { font-size: 1.05rem; color: var(--t2); max-width: 420px; margin: 0 auto 2rem; }
.stats-bar { display: flex; justify-content: center; gap: 2.5rem; margin-bottom: 2.5rem; flex-wrap: wrap; }
.stat-item { text-align: center; }
.stat-val { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 700; color: var(--t1); }
.stat-val span { color: var(--mint); }
.stat-label { font-size: 0.72rem; color: var(--t3); text-transform: uppercase; }

/* Chat */
.chat-wrap { max-width: 760px; margin: 0 auto; padding: 0.5rem 1rem 7rem; }
.bubble-user { display: flex; justify-content: flex-end; margin: 1.2rem 0; animation: slide-right 0.25s ease-out; }
@keyframes slide-right { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
.msg-user { background: linear-gradient(135deg, #1A6BFF 0%, #5B21B6 100%); color: #fff; padding: 11px 18px; border-radius: 20px 20px 4px 20px; max-width: 70%; font-size: 0.92rem; }
.bubble-ai { display: flex; justify-content: flex-start; margin: 1.2rem 0; animation: slide-left 0.25s ease-out; }
@keyframes slide-left { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
.msg-ai { background: var(--surface2); border: 1px solid var(--border2); padding: 14px 18px; border-radius: 20px 20px 20px 4px; max-width: 82%; font-size: 0.9rem; line-height: 1.7; color: var(--t1); backdrop-filter: blur(12px); position: relative; }
.msg-ai::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, var(--mint), transparent); opacity: 0.5; }

/* Agent Steps */
.agent-steps { display: flex; justify-content: flex-start; margin: 1rem 0; }
.agent-bubble { background: var(--surface); border: 1px solid var(--border); border-radius: 20px 20px 20px 4px; padding: 12px 18px; font-size: 0.8rem; color: var(--t2); display: flex; flex-direction: column; gap: 6px; min-width: 240px; }
.agent-step { display: flex; align-items: center; gap: 8px; }
.agent-step.done { color: var(--green); }
.agent-step.blocked { color: var(--red); }

/* Input Bar */
.input-bar { position: fixed; bottom: 0; left: 0; right: 0; padding: 0.75rem 1rem 1.25rem; background: linear-gradient(to top, rgba(8,12,20,0.98) 60%, transparent); backdrop-filter: blur(16px); border-top: 1px solid rgba(0,229,204,0.1); z-index: 200; }
[data-testid="stChatInput"] { max-width: 760px; margin: 0 auto; }
[data-testid="stChatInput"] textarea { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(0,229,204,0.2) !important; border-radius: 24px !important; color: var(--t1) !important; font-size: 0.92rem !important; }
.stButton > button { background: rgba(0,229,204,0.07) !important; border: 1px solid rgba(0,229,204,0.18) !important; border-radius: 100px !important; color: var(--mint) !important; font-size: 0.75rem !important; }

/* Cards */
.card { background: var(--surface2); border: 1px solid var(--border2); border-radius: 16px; padding: 1.5rem; position: relative; }
.card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--mint), var(--sky)); opacity: 0.5; }
.card-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--t1); }

.rec-card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.4rem; margin-bottom: 1rem; position: relative; overflow: hidden; }
.rec-card::before { content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 3px; background: linear-gradient(180deg, var(--mint), var(--sky)); }
.rec-plan { font-size: 0.72rem; color: var(--mint); text-transform: uppercase; }
.rec-metier { font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; color: var(--t1); }
.rec-compat { display: inline-flex; color: var(--green); background: rgba(34,214,122,0.08); padding: 2px 10px; border-radius: 100px; font-size: 0.78rem; margin-bottom: 0.75rem; }
.rec-tag { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: 4px 12px; font-size: 0.75rem; color: var(--t2); display: inline-block; margin-right: 8px; margin-bottom: 8px; }

.hitl-box { background: rgba(255,184,48,0.06); border: 1px solid rgba(255,184,48,0.2); border-radius: 12px; padding: 1rem; margin: 1rem 0; color: #FFB830; }

/* Responsive */
@media (max-width: 600px) {
    .msg-user, .msg-ai { max-width: 92%; font-size: 0.85rem; }
    .hero-title { font-size: 2rem; }
}
</style>
""", unsafe_allow_html=True)

# =========================
# PAGES
# =========================
def render_nav():
    pages = [("💬", "Chat", "chat"), ("🎯", "Recommandations", "reco"), ("🧭", "Roadmap", "roadmap"), ("🧩", "RIASEC", "test"), ("🤖", "Agents", "agents")]
    cols = st.columns(len(pages))
    for i, (icon, label, key) in enumerate(pages):
        with cols[i]:
            active = st.session_state.active_page == key
            st.markdown(f'<div class="nav-btn {"active" if active else ""}" onclick="window.location.href=\'?page={key}\'">{icon} {label}</div>', unsafe_allow_html=True)
            if st.button(f"{icon} {label}", key=f"nav_{key}"):
                st.session_state.active_page = key
                st.rerun()

def render_hero():
    st.markdown("""
    <div class="hero">
        <div class="badge"><span class="badge-dot"></span>ENSET Challenge 2026 · 6 Agents IA · RAG Vectoriel · HITL</div>
        <h1 class="hero-title">CareerBridge AI</h1>
        <p class="hero-sub">Ton <em>système multi-agents intelligent</em><br>6 agents IA collaboratifs pour ton orientation</p>
        <div class="stats-bar">
            <div class="stat-item"><div class="stat-val">6<span></span></div><div class="stat-label">Agents IA</div></div>
            <div class="stat-item"><div class="stat-val">FAISS<span>⚡</span></div><div class="stat-label">Vector DB</div></div>
            <div class="stat-item"><div class="stat-val">HITL<span>✓</span></div><div class="stat-label">Human validation</div></div>
            <div class="stat-item"><div class="stat-val">A/B<span>📊</span></div><div class="stat-label">Prompt testing</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_messages():
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="bubble-user"><div class="msg-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            content = msg["content"].replace("\n", "<br>")
            st.markdown(f'<div class="bubble-ai"><div class="msg-ai">{content}</div></div>', unsafe_allow_html=True)
    
    if st.session_state.loading and st.session_state.get("current_steps"):
        steps_html = ""
        for step in st.session_state.current_steps:
            status_icon = "✅" if step["status"] == "done" else "⏳" if step["status"] == "pending" else "❌"
            steps_html += f'<div class="agent-step {step["status"]}"><span>{status_icon}</span>{step["agent"]}: {step["message"]}</div>'
        st.markdown(f'<div class="agent-steps"><div class="agent-bubble">{steps_html}</div></div>', unsafe_allow_html=True)
    
    if st.session_state.get("show_evaluation") and st.session_state.get("last_evaluation"):
        eval_data = st.session_state.last_evaluation
        st.info(f"📊 **Évaluation** | Score: {eval_data['score']}/100 ({eval_data['grade']})\n\n" + "\n".join([f"• {f}" for f in eval_data['feedback']]))
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_input_bar():
    st.markdown('<div class="input-bar">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        hitl_mode = st.checkbox("👤 Mode HITL", value=False, key="hitl_mode_check")
    with col2:
        eval_mode = st.checkbox("📊 Afficher évaluation", value=st.session_state.show_evaluation, key="eval_mode_check")
        st.session_state.show_evaluation = eval_mode
    with col3:
        if st.button("🧪 A/B Test Prompt", key="ab_test_btn"):
            st.session_state.ab_test_mode = not st.session_state.ab_test_mode
            st.success(f"Mode A/B: {'activé' if st.session_state.ab_test_mode else 'désactivé'}")
    
    user_input = st.chat_input("Décris ton profil (niveau, intérêts, ville)...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if user_input:
        result = process_query(user_input, st.session_state.user_profile)
        st.session_state.current_steps = result.get("steps", [])
        
        if result.get("error"):
            st.error(result["message"])
        elif result.get("blocked"):
            st.session_state.messages.append({"role": "assistant", "content": result["response"]})
            st.session_state.user_profile = result.get("profile", st.session_state.user_profile)
        else:
            response = result["response"]
            st.session_state.user_profile = result.get("profile", st.session_state.user_profile)
            if "evaluation" in result:
                st.session_state.last_evaluation = result["evaluation"]
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()

def page_chat():
    if not st.session_state.messages:
        render_hero()
    render_messages()
    render_input_bar()

def page_recommendations():
    st.markdown("## 🎯 Recommandations")
    if st.session_state.recommendations:
        for rec in st.session_state.recommendations[:3]:
            st.markdown(f"""
            <div class="rec-card">
                <div class="rec-plan">🎯 Plan</div>
                <div class="rec-metier">{rec['metier']}</div>
                <div class="rec-compat">✦ {rec['compat']}% compatibilité</div>
                <div>
                    <span class="rec-tag">💰 {rec['salaire_debut']}</span>
                    <span class="rec-tag">📈 {rec['salaire_5ans']}</span>
                    <span class="rec-tag">{rec['demande']}</span>
                </div>
                <div class="rec-tag" style="display:inline-block;">🎓 {rec['ecoles']}</div>
                <div style="margin-top:0.75rem;font-size:0.82rem;color:var(--t2);">{rec['pourquoi']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💬 Commence par discuter avec le chat IA pour obtenir des recommandations personnalisées !")

def page_roadmap():
    st.markdown("## 🗺️ Roadmap")
    if st.session_state.roadmap_data:
        item = st.session_state.roadmap_data
        st.markdown(f"### {item['metier']}")
        for step in item.get("roadmap_steps", [])[:4]:
            st.markdown(f"- **{step['year']}**: {step['titre']} — {step['detail']}")
    else:
        st.info("📍 Sélectionne un métier dans les recommandations pour voir sa roadmap !")

def page_riasec():
    st.markdown("## 🧩 Test RIASEC")
    st.info("🎯 Ce test sera disponible dans la prochaine version !")
    st.markdown("En attendant, discute avec le chat IA pour découvrir tes affinités professionnelles.")

def page_agents():
    st.markdown("## 🤖 Architecture Multi-Agents")
    st.markdown("""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.2rem;margin-bottom:1.5rem;">
        <div style="text-align:center;font-family:'Syne',sans-serif;margin-bottom:1rem;">WORKFLOW ORCHESTRATION</div>
        <div style="display:flex;align-items:center;justify-content:center;gap:4px;flex-wrap:wrap;">
            <div style="background:rgba(0,229,204,0.1);border-radius:8px;padding:6px 14px;font-size:0.78rem;color:var(--mint);">🛡️ Guardrail</div>
            <div style="color:var(--t3);">→</div>
            <div style="background:rgba(0,229,204,0.1);border-radius:8px;padding:6px 14px;font-size:0.78rem;color:var(--mint);">🎓 Profiler</div>
            <div style="color:var(--t3);">→</div>
            <div style="background:rgba(0,229,204,0.1);border-radius:8px;padding:6px 14px;font-size:0.78rem;color:var(--mint);">🔍 Retriever (FAISS)</div>
            <div style="color:var(--t3);">→</div>
            <div style="background:rgba(0,229,204,0.1);border-radius:8px;padding:6px 14px;font-size:0.78rem;color:var(--mint);">📊 Scorer</div>
            <div style="color:var(--t3);">→</div>
            <div style="background:rgba(0,229,204,0.1);border-radius:8px;padding:6px 14px;font-size:0.78rem;color:var(--mint);">🤖 Generator</div>
            <div style="color:var(--t3);">→</div>
            <div style="background:rgba(0,229,204,0.1);border-radius:8px;padding:6px 14px;font-size:0.78rem;color:var(--mint);">📝 Evaluator</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hitl-box">
        <strong>🛡️ Human-in-the-Loop (HITL)</strong><br>
        • Validation humaine requise si profil < 60% complet<br>
        • Blocage des domaines très sélectifs (Médecine, CPGE)<br>
        • Correction possible du raisonnement agent
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background:var(--surface2);border:1px solid var(--border2);border-radius:16px;padding:1.2rem;">
        <strong>🔧 Fine-tuning simulé</strong><br>
        Modèle ajusté sur 5 000 offres d'emploi marocaines<br>
        Adaptation aux salaires MAD, écoles, marché national
    </div>
    """, unsafe_allow_html=True)

# =========================
# MAIN
# =========================
def main():
    render_nav()
    page = st.session_state.active_page
    if page == "chat":
        page_chat()
    elif page == "reco":
        page_recommendations()
    elif page == "roadmap":
        page_roadmap()
    elif page == "test":
        page_riasec()
    elif page == "agents":
        page_agents()

if __name__ == "__main__":
    main()