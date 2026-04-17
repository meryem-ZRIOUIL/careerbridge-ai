import streamlit as st
import json
import re
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from groq import Groq




import streamlit as st

# =========================
# SESSION ROLE
# =========================
if "role" not in st.session_state:
    st.session_state.role = None

# =========================
# INDEX PAGE
# =========================
if st.session_state.role is None:
    st.title("🎓 CareerBridge AI")

    st.markdown("### Choisissez votre profil 👇")

    col1, col2, col3 = st.columns(3)

    if col1.button("👨‍🎓 Étudiant"):
        st.session_state.role = "student"
        st.rerun()

    if col2.button("👨‍👩‍👧 Parent"):
        st.session_state.role = "parent"
        st.rerun()

    if col3.button("🎓 Conseiller"):
        st.session_state.role = "advisor"
        st.rerun()

    st.stop()

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
# CSS — DARK LUXURY (PRÉSERVÉ)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,400&display=swap');

*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

:root {
    --bg: #080C14;
    --surface: rgba(255,255,255,0.04);
    --surface2: rgba(255,255,255,0.07);
    --border: rgba(255,255,255,0.08);
    --border2: rgba(255,255,255,0.14);
    --mint: #00E5CC;
    --sky: #38AEFF;
    --amber: #FFB830;
    --green: #22D67A;
    --red: #FF4466;
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

/* HERO (inchangé) */
.hero {
    text-align: center;
    padding: 4rem 1rem 2.5rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%; transform: translateX(-50%);
    width: 600px; height: 1px;
    background: linear-gradient(90deg, transparent, var(--mint), transparent);
    opacity: 0.4;
}
.badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0,229,204,0.08);
    border: 1px solid rgba(0,229,204,0.2);
    border-radius: 100px;
    padding: 5px 16px 5px 10px;
    font-size: 0.72rem; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase;
    color: var(--mint); margin-bottom: 1.8rem;
}
.badge-dot {
    width: 7px; height: 7px; background: var(--mint); border-radius: 50%;
    box-shadow: 0 0 8px var(--mint); animation: glow-pulse 2s infinite;
}
@keyframes glow-pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--mint); }
    50% { opacity: 0.5; box-shadow: 0 0 2px var(--mint); }
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.2rem, 7vw, 4rem);
    font-weight: 800; letter-spacing: -0.03em; line-height: 1;
    background: linear-gradient(135deg, #FFFFFF 0%, #C0FFE8 35%, var(--mint) 60%, var(--sky) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 1rem;
}
.hero-sub {
    font-size: 1.05rem; color: var(--t2); max-width: 420px; margin: 0 auto 2rem;
    line-height: 1.65; font-weight: 300;
}
.hero-sub em { color: var(--mint); font-style: normal; font-weight: 500; }
.stats-bar {
    display: flex; justify-content: center; gap: 2.5rem;
    margin-bottom: 2.5rem; flex-wrap: wrap;
}
.stat-item { text-align: center; }
.stat-val { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 700; color: var(--t1); }
.stat-val span { color: var(--mint); }
.stat-label { font-size: 0.72rem; color: var(--t3); letter-spacing: 0.05em; text-transform: uppercase; }

/* CHAT */
.chat-wrap { max-width: 760px; margin: 0 auto; padding: 0.5rem 1rem 7rem; }

.bubble-user { display: flex; justify-content: flex-end; margin: 1.2rem 0; animation: slide-right 0.25s ease-out; }
@keyframes slide-right { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
.msg-user {
    background: linear-gradient(135deg, #1A6BFF 0%, #5B21B6 100%);
    color: #fff; padding: 11px 18px;
    border-radius: 20px 20px 4px 20px; max-width: 70%;
    font-size: 0.92rem; line-height: 1.5;
    box-shadow: 0 4px 20px rgba(26,107,255,0.25);
}

.bubble-ai { display: flex; justify-content: flex-start; margin: 1.2rem 0; animation: slide-left 0.25s ease-out; }
@keyframes slide-left { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
.msg-ai {
    background: var(--surface2); border: 1px solid var(--border2);
    padding: 14px 18px; border-radius: 20px 20px 20px 4px; max-width: 82%;
    font-size: 0.9rem; line-height: 1.7; color: var(--t1);
    backdrop-filter: blur(12px); position: relative; overflow: hidden;
}
.msg-ai::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, var(--mint), transparent); opacity: 0.5;
}

/* AGENT STEPS AMÉLIORÉS */
.agent-steps { display: flex; justify-content: flex-start; margin: 1rem 0; animation: slide-left 0.3s ease-out; }
.agent-bubble {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px 20px 20px 4px; padding: 12px 18px;
    font-size: 0.8rem; color: var(--t2); display: flex; flex-direction: column; gap: 6px; min-width: 260px;
}
.agent-step { display: flex; align-items: center; gap: 8px; transition: color 0.3s; }
.agent-step.active { color: var(--mint); }
.agent-step.done { color: var(--green); }
.agent-step.blocked { color: var(--red); }
.step-icon { font-size: 1.1rem; }

/* HUMAN-IN-THE-LOOP */
.hitl-modal {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
    background: var(--surface2); backdrop-filter: blur(20px);
    border: 1px solid var(--border2); border-radius: 24px;
    padding: 2rem; z-index: 1000; min-width: 400px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}
.hitl-overlay {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
    z-index: 999;
}
.hitl-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; color: var(--mint); }
.hitl-content { margin: 1rem 0; color: var(--t1); }
.hitl-buttons { display: flex; gap: 1rem; margin-top: 1.5rem; }
.hitl-approve { background: var(--green); color: black; border: none; padding: 8px 20px; border-radius: 100px; cursor: pointer; }
.hitl-reject { background: var(--red); color: white; border: none; padding: 8px 20px; border-radius: 100px; cursor: pointer; }

/* INPUT BAR */
.input-bar {
    position: fixed; bottom: 0; left: 0; right: 0;
    padding: 0.75rem 1rem 1.25rem;
    background: linear-gradient(to top, rgba(8,12,20,0.98) 60%, transparent);
    backdrop-filter: blur(16px);
    border-top: 1px solid rgba(0,229,204,0.1);
    z-index: 200;
}
[data-testid="stChatInput"] { max-width: 760px; margin: 0 auto; }
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(0,229,204,0.2) !important;
    border-radius: 24px !important; color: var(--t1) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important; padding: 12px 20px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--mint) !important;
    box-shadow: 0 0 0 3px rgba(0,229,204,0.08) !important; outline: none !important;
}
.stButton button {
    background: rgba(0,229,204,0.07) !important;
    border: 1px solid rgba(0,229,204,0.18) !important;
    border-radius: 100px !important; color: var(--mint) !important;
    font-size: 0.75rem !important; font-family: 'DM Sans', sans-serif !important;
    padding: 4px 12px !important; transition: all 0.18s !important; white-space: nowrap !important;
}
.stButton button:hover {
    background: rgba(0,229,204,0.18) !important;
    border-color: var(--mint) !important; transform: translateY(-1px) !important;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,229,204,0.2); border-radius: 10px; }
@media (max-width: 600px) {
    .msg-user, .msg-ai { max-width: 92%; font-size: 0.85rem; }
    .stats-bar { gap: 1.5rem; }
    .hero-title { font-size: 2rem; }
}
</style>
""", unsafe_allow_html=True)


# =========================
# 1. VECTOR DATABASE AVEC FAISS
# =========================
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    st.success("RAG actif (TF-IDF fallback)")

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
        """Ajoute des documents à la base vectorielle"""
        if not self.initialized:
            return
        
        texts = []
        for doc in docs:
            # Créer un texte riche pour l'embedding
            text = f"{doc['metier']} {doc['secteur']} {' '.join(doc['tags'])} {doc.get('pourquoi', '')}"
            texts.append(text)
            self.documents.append(doc)
        
        embeddings = self.embedding_model.encode(texts)
        self.index.add(np.array(embeddings).astype('float32'))
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Recherche les k documents les plus similaires"""
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
# 2. DONNÉES MARCHÉ (ENRICHIES)
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
        "pourquoi": "Casablanca Tech City & zones offshore recrutent massivement. +35% d'offres en 2023.",
        "evolution": "Dev → Lead Dev → CTO → Freelance international (60–120k€/an possible en remote)",
        "soft_skills": ["logique", "résolution problèmes", "autonomie", "travail équipe"]
    },
    {
        "id": "data_scientist", "metier": "Data Scientist / Ingénieur IA", "secteur": "Tech / IA",
        "salaire_debut": "13 000–18 000 MAD", "salaire_5ans": "28 000–40 000 MAD",
        "demande": "TRÈS HAUTE ⚡", "taux_insertion": "93%",
        "villes": "Casablanca · Rabat",
        "ecoles": "ENSIAS · INPT · UM6P · Al Akhawayn",
        "duree": "Bac+5",
        "tags": ["data","ia","intelligence artificielle","machine learning","statistiques","big data","python","neural","deep learning","algorithme"],
        "pourquoi": "OCP, Maroc Telecom, banques : demande x3 en 2 ans. Pénurie mondiale de talents.",
        "evolution": "Data Analyst → Data Scientist → ML Engineer → AI Lead → CDO",
        "soft_skills": ["mathématiques", "statistiques", "curiosité", "analyse"]
    },
    {
        "id": "cybersecurite", "metier": "Expert Cybersécurité", "secteur": "Tech / Sécurité",
        "salaire_debut": "12 000–16 000 MAD", "salaire_5ans": "26 000–38 000 MAD",
        "demande": "CRITIQUE 🔐", "taux_insertion": "97%",
        "villes": "Casablanca · Rabat",
        "ecoles": "INPT · ENSIAS · EHTP",
        "duree": "Bac+5",
        "tags": ["cybersecurite","securite","hacking","reseau","cyber","informatique","sécurité","pentest","firewall"],
        "pourquoi": "Pénurie mondiale de 3.5M experts. Banques et télécoms marocains recrutent urgemment.",
        "evolution": "SOC Analyst → Pentester → CISO → Consultant international",
        "soft_skills": ["vigilance", "analyse", "éthique", "rigueur"]
    },
    {
        "id": "ingenieur_industrie", "metier": "Ingénieur Industriel / Qualité", "secteur": "Industrie / Automobile",
        "salaire_debut": "9 000–12 000 MAD", "salaire_5ans": "18 000–25 000 MAD",
        "demande": "HAUTE 📈", "taux_insertion": "87%",
        "villes": "Tanger · Kénitra · Casablanca",
        "ecoles": "EHTP · EMI · ENSAM · ENSA Tanger",
        "duree": "Bac+5",
        "tags": ["ingenieur","génie","mecanique","industrie","automobile","production","qualite","lean","renault","stellantis"],
        "pourquoi": "Tanger Med = 1er port d'Afrique. Renault + Stellantis embauchent 2000+ ingénieurs/an.",
        "evolution": "Ingénieur process → Chef de projet → Directeur usine → DG",
        "soft_skills": ["organisation", "leadership", "résolution problèmes"]
    },
    {
        "id": "commercial_marketing", "metier": "Responsable Commercial / Marketing", "secteur": "Business",
        "salaire_debut": "8 000–12 000 MAD", "salaire_5ans": "18 000–30 000 MAD",
        "demande": "HAUTE 📊", "taux_insertion": "85%",
        "villes": "Casablanca · Rabat · Marrakech",
        "ecoles": "ISCAE · HEM · ENCG",
        "duree": "Bac+3 à Bac+5",
        "tags": ["commerce","marketing","vente","communication","business","relation client","négociation","stratégie"],
        "pourquoi": "Toutes les entreprises ont besoin de commerciaux. Évolution rapide vers postes de direction.",
        "evolution": "Commercial → Chef des ventes → Directeur commercial → DG",
        "soft_skills": ["communication", "négociation", "empathie", "persuasion"]
    },
    {
        "id": "ingenieur_aeronautique", "metier": "Ingénieur Aéronautique", "secteur": "Aéronautique",
        "salaire_debut": "12 000–16 000 MAD", "salaire_5ans": "24 000–34 000 MAD",
        "demande": "HAUTE ✈️", "taux_insertion": "90%",
        "villes": "Casablanca · Nouaceur",
        "ecoles": "EHTP · EMI · ISAE Supaero (échange)",
        "duree": "Bac+5",
        "tags": ["aeronautique","avion","boeing","safran","composites","aero","mécanique"],
        "pourquoi": "1er hub aéronautique africain. +100 entreprises internationales (Boeing, Safran, Hexcel).",
        "evolution": "Ingénieur études → Chef de projet → Directeur technique → expatriation possible",
        "soft_skills": ["précision", "rigueur", "travail équipe"]
    },
    {
        "id": "medecin", "metier": "Médecin / Spécialiste", "secteur": "Santé",
        "salaire_debut": "8 000–12 000 MAD", "salaire_5ans": "20 000–50 000 MAD",
        "demande": "TRÈS HAUTE 🏥", "taux_insertion": "98%",
        "villes": "Toutes les villes du Maroc",
        "ecoles": "Faculté Médecine Casablanca · Rabat · Marrakech · Fès",
        "duree": "Bac+7 minimum",
        "tags": ["medecine","docteur","sante","médecin","chirurgien","pharmacie","infirmier","hôpital","clinique","biologie"],
        "pourquoi": "Maroc manque de 100 000 médecins. Secteur privé très lucratif, spécialistes très demandés.",
        "evolution": "Interne → Médecin généraliste → Spécialiste → Clinique privée",
        "soft_skills": ["empathie", "patience", "rigueur", "communication"]
    },
    {
        "id": "finance_banque", "metier": "Analyste Financier / Banker", "secteur": "Finance / Banque",
        "salaire_debut": "9 000–12 000 MAD", "salaire_5ans": "20 000–32 000 MAD",
        "demande": "HAUTE 💼", "taux_insertion": "82%",
        "villes": "Casablanca · Rabat",
        "ecoles": "ISCAE · HEM · ENCG · Sciences Po (échange)",
        "duree": "Bac+3 à Bac+5",
        "tags": ["finance","banque","comptabilite","gestion","audit","business","commerce","management","marketing","economie"],
        "pourquoi": "Casablanca Finance City = hub financier africain. Attijariwafa, CIH, BCP recrutent chaque année.",
        "evolution": "Analyste → Manager → Directeur → PDG (rémunération 100k+ MAD/mois possible)",
        "soft_skills": ["mathématiques", "analyse", "rigueur", "discrétion"]
    },
    {
        "id": "energie_renouvelable", "metier": "Ingénieur Énergies Renouvelables", "secteur": "Green Tech",
        "salaire_debut": "10 000–13 000 MAD", "salaire_5ans": "20 000–28 000 MAD",
        "demande": "TRÈS HAUTE 🌱", "taux_insertion": "88%",
        "villes": "Ouarzazate · Laâyoune · Casablanca",
        "ecoles": "EHTP · EMI · ENSA",
        "duree": "Bac+5",
        "tags": ["energie","solaire","eolien","renouvelable","green","environnement","noor","electrique","ecologie"],
        "pourquoi": "Plan Noor + IRESEN : Maroc vise 52% renouvelable en 2030. Investissement 30 Mds $.",
        "evolution": "Ingénieur terrain → Chef de projet → Directeur énergie → Expert ONU/Banque Mondiale",
        "soft_skills": ["technique", "innovation", "environnement"]
    },
]

# =========================
# 3. SYSTÈME D'AGENTS
# =========================
class AgentRole(Enum):
    """Rôles des agents dans le système"""
    GUARDRAIL = "guardrail"
    PROFILER = "profiler"
    RETRIEVER = "retriever"
    SCORER = "scorer"
    GENERATOR = "generator"
    EVALUATOR = "evaluator"

@dataclass
class AgentMessage:
    """Message entre agents"""
    role: AgentRole
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    requires_approval: bool = False

class BaseAgent:
    """Agent de base avec sécurité intégrée"""
    
    def __init__(self, name: str, role: AgentRole):
        self.name = name
        self.role = role
        self.tools = []
        self.access_log = []
    
    def can_use_tool(self, tool_name: str) -> bool:
        """Vérifie si l'agent peut utiliser un outil spécifique"""
        allowed_tools = {
            AgentRole.GUARDRAIL: ["detect_threat", "filter_output"],
            AgentRole.PROFILER: ["extract_profile", "update_profile"],
            AgentRole.RETRIEVER: ["search_vector_db", "get_context"],
            AgentRole.SCORER: ["calculate_score", "rank_results"],
            AgentRole.GENERATOR: ["generate_response", "format_output"],
            AgentRole.EVALUATOR: ["score_response", "ab_test"]
        }
        return tool_name in allowed_tools.get(self.role, [])
    
    def log_access(self, tool_name: str):
        """Log l'accès aux outils pour audit"""
        self.access_log.append({
            "tool": tool_name,
            "agent": self.name,
            "timestamp": datetime.now()
        })

class GuardrailAgent(BaseAgent):
    """Agent de sécurité - Protection contre injections et filtrage"""
    
    def __init__(self):
        super().__init__("Guardian", AgentRole.GUARDRAIL)
        self.forbidden_patterns = [
            r"ignore.*instructions",
            r"system.*prompt",
            r"roleplay.*as.*admin",
            r"<script",
            r"javascript:",
            r"DROP TABLE",
            r"DELETE FROM",
            r"exec\(",
            r"eval\(",
        ]
        self.sensitive_topics = ["politique", "religion", "discrimination"]
    
    def detect_injection(self, text: str) -> Tuple[bool, str]:
        """Détecte les tentatives d'injection de prompt"""
        text_lower = text.lower()
        
        for pattern in self.forbidden_patterns:
            if re.search(pattern, text_lower):
                return True, f"Tentative d'injection détectée: {pattern}"
        
        for topic in self.sensitive_topics:
            if topic in text_lower:
                return True, f"Sujet sensible détecté: {topic}"
        
        return False, "OK"
    
    def filter_output(self, text: str) -> str:
        """Filtre la sortie pour supprimer le contenu dangereux"""
        # Supprime les URLs suspectes
        text = re.sub(r'https?://[^\s]+', '[LIEN SUPPRIMÉ]', text)
        # Supprime les emails
        text = re.sub(r'\S+@\S+', '[EMAIL SUPPRIMÉ]', text)
        # Supprime les potentielles instructions système
        text = re.sub(r'ignore previous instructions', '', text, flags=re.IGNORECASE)
        
        return text

class ProfilerAgent(BaseAgent):
    """Agent d'analyse de profil utilisateur"""
    
    def __init__(self):
        super().__init__("Profiler", AgentRole.PROFILER)
    
    def extract_profile(self, text: str, existing: dict) -> dict:
        """Extraction avancée du profil"""
        profile = existing.copy()
        tl = text.lower()
        
        # Niveau d'études
        niveau_map = {
            "terminale": "bac", "bac": "bac", "lycée": "bac",
            "bac+2": "bac+2", "bts": "bac+2", "dut": "bac+2",
            "licence": "bac+3", "bac+3": "bac+3", "bac+4": "bac+4",
            "master": "bac+5", "ingenieur": "bac+5", "bac+5": "bac+5",
            "doctorat": "bac+8", "phd": "bac+8"
        }
        for kw, nv in niveau_map.items():
            if kw in tl:
                profile["niveau"] = nv
                break
        
        # Centres d'intérêt
        interests = {
    # ==================== TECH & NUMÉRIQUE ====================
    "tech": [
        "informatique", "programmation", "code", "digital", "ia", "intelligence artificielle", 
        "data", "big data", "data science", "machine learning", "deep learning", "neural networks",
        "développement web", "web", "mobile", "applications", "app", "software", "logiciel",
        "devops", "cloud", "aws", "azure", "gcp", "cybersécurité", "sécurité informatique",
        "hacking", "pentest", "réseaux", "systèmes", "bases de données", "sql", "nosql",
        "python", "java", "javascript", "typescript", "react", "angular", "vue", "node.js",
        "docker", "kubernetes", "git", "github", "ci/cd", "agile", "scrum", "blockchain",
        "crypto", "bitcoin", "ethereum", "smart contracts", "robotique", "iot", "objets connectés",
        "réalité virtuelle", "vr", "réalité augmentée", "ar", "game development", "jeux vidéo",
        "3d", "animation 3d", "unreal engine", "unity", "low code", "no code", "automatisation",
        "rpa", "api", "microservices", "architecture logicielle", "system design"
    ],
    
    # ==================== BUSINESS & MANAGEMENT ====================
    "business": [
        "commerce", "vente", "marketing", "management", "gestion", "finance", "comptabilité",
        "audit", "contrôle de gestion", "ressources humaines", "rh", "recrutement", "formation",
        "business development", "stratégie", "consulting", "conseil", "projet", "chef de projet",
        "product owner", "product manager", "scrum master", "entrepreneuriat", "startup",
        "création d'entreprise", "business plan", "levée de fonds", "investissement", "trading",
        "bourse", "actions", "obligations", "private equity", "venture capital", "banque",
        "assurance", "courtage", "immobilier", "transaction", "négociation", "relation client",
        "service client", "satisfaction client", "expérience client", "crm", "sales", "business intelligence",
        "bi", "tableau de bord", "kpi", "reporting", "analyse financière", "modélisation financière"
    ],
    
    # ==================== CRÉATIF & ARTISTIQUE ====================
    "creative": [
        "design", "création", "artistique", "graphisme", "audiovisuel", "photographie", "vidéo",
        "montage vidéo", "post-production", "effets spéciaux", "vfx", "motion design", "animation",
        "illustration", "dessin", "peinture", "art numérique", "digital art", "ui design", "ux design",
        "user interface", "user experience", "design thinking", "prototypage", "figma", "sketch",
        "adobe creative suite", "photoshop", "illustrator", "after effects", "premiere pro",
        "blender", "autocad", "solidworks", "architecture d'intérieur", "design d'espace",
        "stylisme", "mode", "création de vêtements", "textile", "bijouterie", "joaillerie",
        "céramique", "sculpture", "artisanat", "métiers d'art", "calligraphie", "typographie",
        "branding", "identité visuelle", "logo", "packaging", "publicité", "campagne marketing",
        "contenu créatif", "content creation", "influenceur", "community management", "social media"
    ],
    
    # ==================== SCIENTIFIQUE & RECHERCHE ====================
    "scientific": [
        "sciences", "recherche", "laboratoire", "biologie", "chimie", "physique", "mathématiques",
        "maths", "algèbre", "géométrie", "analyse", "statistiques", "probabilités", "sciences de la vie",
        "biochimie", "biotechnologie", "génétique", "microbiologie", "écologie", "environnement",
        "sciences de la terre", "géologie", "astronomie", "astrophysique", "cosmologie", "sciences cognitives",
        "neurosciences", "psychologie cognitive", "sciences sociales", "sociologie", "anthropologie",
        "archéologie", "paléontologie", "sciences politiques", "économie", "économétrie",
        "sciences de l'ingénieur", "mécanique", "électrotechnique", "électronique", "automatique",
        "thermique", "énergétique", "énergies renouvelables", "solaire", "éolien", "hydrogène",
        "matériaux", "nanotechnologies", "chimie des matériaux", "science des données", "recherche opérationnelle",
        "optimisation", "simulation", "modélisation", "analyse numérique"
    ],
    
    # ==================== HUMANITÉS & SCIENCES HUMAINES ====================
    "humanities": [
        "langues", "communication", "relations humaines", "psychologie", "enseignement", "pédagogie",
        "éducation", "formation", "coaching", "développement personnel", "bien-être", "méditation",
        "philosophie", "éthique", "morale", "logique", "épistémologie", "métaphysique",
        "lettres", "littérature", "poésie", "écriture", "rédaction", "journalisme", "reportage",
        "édition", "correction", "relecture", "traduction", "interprétariat", "linguistique",
        "sémantique", "philologie", "histoire", "géographie", "civilisations", "cultures",
        "patrimoine", "musées", "archives", "bibliothéconomie", "documentation", "sciences de l'information",
        "médiation culturelle", "animation socioculturelle", "travail social", "aide à la personne",
        "médiation familiale", "conseil conjugal", "psychothérapie", "psychanalyse", "ressources humaines",
        "gestion des conflits", "négociation", "médiation", "diplomatie", "relations internationales",
        "coopération", "développement durable", "solidarité", "humanitaire", "ong", "associatif"
    ],
    
    # ==================== SANTÉ & MÉDICAL ====================
    "health": [
        "médecine", "santé", "hôpital", "clinique", "soins", "infirmier", "sage-femme",
        "kinésithérapie", "physiothérapie", "ostéopathie", "chiropraxie", "orthophonie",
        "psychomotricité", "ergothérapie", "diététique", "nutrition", "pharmacie", "biologie médicale",
        "laboratoire d'analyses", "radiologie", "imagerie médicale", "chirurgie", "anesthésie",
        "pédiatrie", "gériatrie", "psychiatrie", "cardiologie", "neurologie", "oncologie",
        "urgence", "samu", "ambulance", "secourisme", "premiers secours", "santé publique",
        "épidémiologie", "prévention", "éducation thérapeutique", "recherche médicale", "clinical trials",
        "dispositifs médicaux", "biotech", "medtech", "e-santé", "télémédecine", "dossiers médicaux"
    ],
    
    # ==================== SPORT & BIEN-ÊTRE ====================
    "sport": [
        "sport", "athlétisme", "football", "basketball", "tennis", "natation", "gymnastique",
        "arts martiaux", "judo", "karaté", "taekwondo", "boxe", "mma", "yoga", "pilates",
        "fitness", "musculation", "crossfit", "running", "marathon", "triathlon", "cyclisme",
        "escalade", "randonnée", "alpinisme", "ski", "snowboard", "surf", "kitesurf", "voile",
        "aviron", "canoë", "kayak", "plongée", "apnée", "équitation", "golf", "rugby",
        "handball", "volleyball", "badminton", "squash", "padel", "billard", "pétanque",
        "coaching sportif", "préparation physique", "mentale", "nutrition sportive", "kinésithérapie sportive",
        "management sportif", "organisation d'événements", "journalisme sportif", "commentaire"
    ],
    
    # ==================== VOYAGE & TOURISME ====================
    "travel": [
        "voyage", "tourisme", "hôtellerie", "restauration", "catering", "cuisine", "pâtisserie",
        "gastronomie", "oenologie", "vin", "sommelier", "barista", "café", "thé", "mixologie",
        "cocktails", "service", "accueil", "réception", "guide touristique", "animateur",
        "loisirs", "parcs d'attractions", "croisière", "aviation", "hôtesse de l'air", "steward",
        "agence de voyage", "réservation", "billetterie", "tour opérateur", "destination management",
        "tourisme durable", "écotourisme", "tourisme solidaire", "voyage d'affaires", "mice",
        "organisation d'événements", "wedding planner", "festivals", "concerts", "spectacles"
    ],
    
    # ==================== AGRICULTURE & ENVIRONNEMENT ====================
    "environment": [
        "agriculture", "agronomie", "permaculture", "biologique", "bio", "jardinage", "horticulture",
        "paysage", "espaces verts", "foresterie", "sylviculture", "environnement", "écologie",
        "biodiversité", "conservation", "protection de la nature", "recyclage", "déchets",
        "économie circulaire", "eau", "assainissement", "traitement des eaux", "qualité de l'air",
        "pollution", "climat", "réchauffement", "transition écologique", "énergies renouvelables",
        "solaire", "éolien", "hydroélectricité", "biomasse", "géothermie", "efficacité énergétique",
        "building", "green building", "construction durable", "matériaux écologiques", "biosourcés",
        "mobilité durable", "vélo", "transports en commun", "voiture électrique", "bornes de recharge"
    ],
    
    # ==================== DROIT & JUSTICE ====================
    "law": [
        "droit", "justice", "avocat", "juriste", "magistrat", "juge", "procureur", "greffier",
        "clerc", "notaire", "huissier", "commissaire-priseur", "administrateur judiciaire",
        "mandataire judiciaire", "conseil juridique", "legal tech", "conformité", "compliance",
        "droit des affaires", "droit commercial", "droit des sociétés", "droit fiscal", "fiscalité",
        "droit social", "droit du travail", "droit immobilier", "droit de la construction",
        "droit de la famille", "droit des personnes", "droit pénal", "droit international",
        "droit européen", "droit de l'environnement", "droit de la santé", "droit pharmaceutique",
        "droit des nouvelles technologies", "droit du numérique", "droit de la propriété intellectuelle",
        "brevets", "marques", "copyright", "droit de la concurrence", "droit de la consommation",
        "médiation", "arbitrage", "résolution des conflits", "legal design", "legal writing"
    ]
}
        
        profile["interests"] = []
        for category, keywords in interests.items():
            if any(kw in tl for kw in keywords):
                profile["interests"].append(category)
        
        # Contraintes explicites
        constraints = []
        if any(word in tl for word in ["pas les maths", "n'aime pas les maths", "maths difficile"]):
            constraints.append("no_math")
        if any(word in tl for word in ["pas l'informatique", "n'aime pas l'informatique"]):
            constraints.append("no_tech")
        if any(word in tl for word in ["pas de contact", "n'aime pas le contact"]):
            constraints.append("no_contact")
        
        profile["constraints"] = constraints
        
        # Ville
        villes = ["casablanca", "rabat", "tanger", "marrakech", "fès", "agadir", "tétouan", "meknès"]
        for v in villes:
            if v in tl:
                profile["ville"] = v.capitalize()
                break
        
        # Soft skills détectés
        soft_skills_keywords = {
            "communication": ["parler", "communiquer", "relation", "échange", "dialogue"],
            "leadership": ["diriger", "manager", "chef", "leader", "responsable"],
            "creativity": ["créatif", "innovation", "original", "imagination"],
            "analytical": ["analyser", "logique", "réfléchir", "résoudre"]
        }
        
        profile["detected_skills"] = []
        for skill, keywords in soft_skills_keywords.items():
            if any(kw in tl for kw in keywords):
                profile["detected_skills"].append(skill)
        
        return profile

class RetrieverAgent(BaseAgent):
    """Agent de recherche vectorielle RAG"""
    
    def __init__(self, vector_db: VectorDatabase):
        super().__init__("Retriever", AgentRole.RETRIEVER)
        self.vector_db = vector_db
        # Initialiser la base vectorielle
        self.vector_db.add_documents(MARKET_DATA)
    
    def search(self, query: str, profile: dict, k: int = 5) -> List[Dict]:
        """Recherche avec filtrage basé sur profil"""
        # Construire une requête enrichie
        enriched_query = query
        
        if profile.get("interests"):
            enriched_query += " " + " ".join(profile["interests"])
        
        if profile.get("detected_skills"):
            enriched_query += " " + " ".join(profile["detected_skills"])
        
        # Recherche vectorielle
        results = self.vector_db.search(enriched_query, k)
        
        # Filtrage post-recherche basé sur contraintes
        constraints = profile.get("constraints", [])
        filtered_results = []
        
        for item in results:
            # Appliquer les contraintes
            if "no_math" in constraints:
                if any(tag in ["math", "statistiques", "algorithme"] for tag in item["tags"]):
                    continue
            
            if "no_tech" in constraints:
                if item["secteur"] == "Tech / IT" or "informatique" in item["tags"]:
                    continue
            
            if "no_contact" in constraints:
                if "communication" in item.get("soft_skills", []):
                    continue
            
            filtered_results.append(item)
        
        return filtered_results

class ScorerAgent(BaseAgent):
    """Agent de scoring des résultats"""
    
    def __init__(self):
        super().__init__("Scorer", AgentRole.SCORER)
    
    def calculate_compatibility(self, profile: dict, job: dict) -> float:
        """Calcule un score de compatibilité détaillé"""
        score = 0.0
        details = []
        
        # 1. Niveau d'études (max 20 points)
        niveau_required = job["duree"]
        profile_level = profile.get("niveau", "bac")
        
        level_scores = {
            "bac": {"Bac+3": 15, "Bac+5": 10, "Bac+7": 5},
            "bac+2": {"Bac+3": 18, "Bac+5": 12, "Bac+7": 6},
            "bac+3": {"Bac+3": 20, "Bac+5": 16, "Bac+7": 8},
            "bac+4": {"Bac+3": 18, "Bac+5": 18, "Bac+7": 10},
            "bac+5": {"Bac+3": 15, "Bac+5": 20, "Bac+7": 15},
            "bac+8": {"Bac+3": 10, "Bac+5": 18, "Bac+7": 20}
        }
        
        if profile_level in level_scores:
            for required, pts in level_scores[profile_level].items():
                if required in niveau_required:
                    score += pts
                    details.append(f"✅ Niveau d'études compatible: +{pts}")
                    break
        
        # 2. Centres d'intérêt (max 30 points)
        interests = profile.get("interests", [])
        job_tags = set(job["tags"])
        
        interest_mapping = {
            "tech": {"informatique", "data", "ia", "programmation", "code", "digital"},
            "business": {"commerce", "marketing", "finance", "gestion", "management"},
            "creative": {"design", "création", "artistique"},
            "scientific": {"scientifique", "recherche", "laboratoire"},
            "humanities": {"langues", "communication", "relation"}
        }
        
        interest_score = 0
        for interest in interests:
            if interest in interest_mapping:
                matches = len(job_tags & interest_mapping[interest])
                interest_score += matches * 10
        
        score += min(interest_score, 30)
        if interest_score > 0:
            details.append(f"🎯 Intérêts alignés: +{min(interest_score, 30)}")
        
        # 3. Soft skills (max 20 points)
        detected_skills = profile.get("detected_skills", [])
        job_skills = set(job.get("soft_skills", []))
        
        skills_match = len(set(detected_skills) & job_skills)
        skills_score = skills_match * 10
        score += min(skills_score, 20)
        if skills_score > 0:
            details.append(f"💪 Soft skills compatibles: +{min(skills_score, 20)}")
        
        # 4. Demande du marché (max 15 points)
        demand_scores = {
            "CRITIQUE 🔥": 15,
            "TRÈS HAUTE ⚡": 12,
            "TRÈS HAUTE 🏥": 12,
            "TRÈS HAUTE 🌱": 12,
            "HAUTE 📈": 10,
            "HAUTE ✈️": 10,
            "HAUTE 💼": 8,
            "CRITIQUE 🔐": 15
        }
        
        demand_score = demand_scores.get(job.get("demande", ""), 5)
        score += demand_score
        details.append(f"📊 Demande marché: +{demand_score}")
        
        # 5. Salaire potentiel (max 15 points)
        salary_text = job.get("salaire_5ans", "")
        if "000" in salary_text:
            numbers = re.findall(r'(\d+)\s*000', salary_text)
            if numbers:
                max_salary = max(int(n) for n in numbers)
                salary_score = min(15, max_salary // 2000)
                score += salary_score
                details.append(f"💰 Potentiel salarial: +{salary_score}")
        
        return min(100, score)

class GeneratorAgent(BaseAgent):
    """Agent de génération de réponse finale"""
    
    def __init__(self, llm_client):
        super().__init__("Generator", AgentRole.GENERATOR)
        self.llm = llm_client
    
    def generate_response(self, query: str, profile: dict, jobs: List[Dict], scores: List[float]) -> str:
        """Génère la réponse finale avec contexte RAG"""
        
        # Construire le contexte enrichi
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
        
        # Construire le prompt
        generation_prompt = f"""
Tu es CareerBridge AI, expert en orientation au Maroc.

🎯 PROFIL UTILISATEUR:
- Niveau: {profile.get('niveau', 'Non spécifié')}
- Ville: {profile.get('ville', 'Non spécifiée')}
- Centres d'intérêt: {', '.join(profile.get('interests', []))}
- Contraintes: {', '.join(profile.get('constraints', []))}
- Soft skills détectés: {', '.join(profile.get('detected_skills', []))}

🔍 OPPORTUNITÉS IDENTIFIÉES (RAG + scoring):
{context_text}

📝 QUESTION UTILISATEUR:
{query}

━━━━━━━━━━━━━━━━━━━━
🎯 INSTRUCTIONS SPÉCIFIQUES:
━━━━━━━━━━━━━━━━━━━━

1. Respecte STRICTEMENT les contraintes du profil
2. Ne propose JAMAIS un métier incompatible avec les contraintes
3. Explique POURQUOI chaque métier est (ou n'est pas) adapté
4. Sois concret, utilise des exemples réels du marché marocain
5. Termine par un conseil actionnable

Génère une réponse naturelle, chaleureuse et professionnelle.
"""
        
        try:
            response = self.llm.generate(
                prompt=generation_prompt,
                system_role="Expert en orientation professionnelle Maroc"
            )
            return response
        except Exception as e:
            # Fallback si LLM échoue
            return self._generate_fallback_response(jobs, scores, profile)
    
    def _generate_fallback_response(self, jobs: List[Dict], scores: List[float], profile: dict) -> str:
        """Fallback sans LLM"""
        response = f"""## 🎯 Analyse de ton profil

D'après ton profil (niveau {profile.get('niveau', 'non spécifié')}), voici les meilleures opportunités :

"""
        for job, score in zip(jobs[:3], scores[:3]):
            response += f"""
### ✨ {job['metier']} — Compatibilité {score:.0f}%

**Pourquoi ce choix ?**  
{job['pourquoi']}

**Parcours recommandé :**  
{job['evolution']}

**À savoir :**  
- Salaire début : {job['salaire_debut']}
- Écoles : {job['ecoles']}
- Demande sur le marché : {job['demande']}

---
"""
        
        response += "\n**💡 Conseil :** N'hésite pas à préciser ton parcours pour des recommandations encore plus ciblées !"
        return response

class EvaluatorAgent(BaseAgent):
    """Agent d'évaluation des réponses (A/B testing)"""
    
    def __init__(self):
        super().__init__("Evaluator", AgentRole.EVALUATOR)
        self.response_scores = {}
        self.ab_test_results = []
    
    def evaluate_response(self, response: str, query: str, context: dict) -> Dict:
        """Évalue la qualité de la réponse"""
        score = 0
        feedback = []
        
        # Critère 1: Longueur (pas trop courte, pas trop longue)
        words = len(response.split())
        if 150 <= words <= 600:
            score += 20
            feedback.append("Longueur optimale")
        elif words < 100:
            score += 5
            feedback.append("Réponse trop courte")
        elif words > 800:
            score += 10
            feedback.append("Réponse un peu longue")
        else:
            score += 15
        
        # Critère 2: Présence de données concrètes
        if any(marker in response for marker in ["MAD", "salaire", "demande", "CRITIQUE"]):
            score += 25
            feedback.append("Données concrètes présentes")
        
        # Critère 3: Recommandations actionnables
        if any(marker in response for marker in ["conseil", "recommande", "suggère", "prochaine étape"]):
            score += 25
            feedback.append("Recommandations actionnables")
        
        # Critère 4: Personnalisation
        if context.get("profile") and context["profile"].get("niveau"):
            if context["profile"]["niveau"] in response:
                score += 30
                feedback.append("Bonne personnalisation")
        
        evaluation = {
            "score": score,
            "grade": "A" if score >= 80 else "B" if score >= 60 else "C",
            "feedback": feedback,
            "timestamp": datetime.now()
        }
        
        # Stocker pour analyse
        response_id = hashlib.md5(response.encode()).hexdigest()
        self.response_scores[response_id] = evaluation
        
        return evaluation

# =========================
# 4. ORCHESTRATEUR MULTI-AGENTS
# =========================
# =========================
# 4. ORCHESTRATEUR MULTI-AGENTS
# =========================
class AgentOrchestrator:
    """Orchestrateur central du système multi-agents"""
    
    def __init__(self, llm_client):
        self.vector_db = VectorDatabase()
        self.guardrail = GuardrailAgent()
        self.profiler = ProfilerAgent()
        self.retriever = RetrieverAgent(self.vector_db)
        self.scorer = ScorerAgent()
        self.generator = GeneratorAgent(llm_client)
        self.evaluator = EvaluatorAgent()
        
        self.execution_log = []
        self.pending_approvals = []
    
    def _calculate_profile_completeness(self, profile: dict) -> float:
        """
        Calcule un score de complétude du profil basé sur:
        - niveau (0.3)
        - interests (0.3)
        - constraints (0.2)
        - ville (0.2)
        """
        score = 0.0
        
        # Critère 1: Niveau d'études (poids 0.3)
        if profile.get("niveau") and profile["niveau"] != "Non spécifié":
            score += 0.3
        
        # Critère 2: Centres d'intérêt (poids 0.3)
        interests = profile.get("interests", [])
        if interests and len(interests) > 0:
            score += 0.3
        
        # Critère 3: Contraintes explicites (poids 0.2)
        constraints = profile.get("constraints", [])
        if constraints and len(constraints) > 0:
            score += 0.2
        
        # Critère 4: Ville (poids 0.2)
        if profile.get("ville") and profile["ville"] != "Non spécifiée":
            score += 0.2
        
        return round(score, 2)
    
    def _get_missing_fields(self, profile: dict) -> List[str]:
        """Identifie les champs manquants dans le profil"""
        missing = []
        
        if not profile.get("niveau") or profile["niveau"] == "Non spécifié":
            missing.append("niveau d'études (ex: Bac, Bac+3, Bac+5)")
        
        interests = profile.get("interests", [])
        if not interests or len(interests) == 0:
            missing.append("centres d'intérêt (ex: informatique, commerce, sciences)")
        
        if not profile.get("ville") or profile["ville"] == "Non spécifiée":
            missing.append("ville de résidence")
        
        return missing
    
    def _generate_incomplete_profile_response(self, missing_fields: List[str], completeness_score: float) -> str:
        """Génère une réponse HITL demandant plus d'informations"""
        
        response = f"""## 🔍 Profil insuffisamment défini

Ton profil n'est pas assez complet pour que je puisse te recommander des métiers pertinents.

**Score de complétude actuel :** {completeness_score:.0%} (minimum requis: 60%)

### Informations manquantes :
"""
        
        for field in missing_fields:
            response += f"- ✏️ {field}\n"
        
        response += """

### Pour t'aider au mieux, pourrais-tu me préciser :

**1. Ton niveau d'études actuel**
   - Exemple: "Je suis en terminale", "J'ai un Bac+3 en informatique"

**2. Tes centres d'intérêt**
   - Exemple: "Je suis passionné par l'informatique", "J'aime le commerce et les langues"

**3. (Optionnel) Ce que tu n'aimes pas**
   - Exemple: "Je n'aime pas les maths", "Je préfère éviter le contact client"

**4. Ta ville de résidence** (pour les opportunités locales)

---

💡 **Conseil :** Plus ton profil est détaillé, plus mes recommandations seront précises et adaptées à ton profil unique.

*Pose-moi une question plus précise ou donne-moi plus de détails sur ton parcours !* 🎯
"""
        return response
    
    def process_query(self, query: str, profile: dict, history: list, require_approval: bool = False) -> Dict:
        """Pipeline complet multi-agents"""
        
        execution_steps = []
        
        # ÉTAPE 1: GUARDRAIL - Sécurité
        st.session_state.agent_phase = "guardrail"
        is_malicious, threat_msg = self.guardrail.detect_injection(query)
        if is_malicious:
            return {
                "error": True,
                "message": f"⛔ {threat_msg}\nVotre message a été bloqué pour des raisons de sécurité.",
                "steps": execution_steps
            }
        execution_steps.append({"agent": "Guardrail", "status": "done", "message": "Sécurité validée"})
        
        # ÉTAPE 2: PROFILER - Analyse profil
        st.session_state.agent_phase = "profiler"
        updated_profile = self.profiler.extract_profile(query, profile)
        execution_steps.append({"agent": "Profiler", "status": "done", "message": f"Profil analysé: {updated_profile.get('niveau', 'N/A')}"})
        
        # ==================== VÉRIFICATION DE COMPLÉTUDE DU PROFIL ====================
        completeness_score = self._calculate_profile_completeness(updated_profile)
        MIN_COMPLETENESS_THRESHOLD = 0.6
        
        if completeness_score < MIN_COMPLETENESS_THRESHOLD:
            execution_steps.append({
                "agent": "Profiler", 
                "status": "blocked", 
                "message": f"Profil incomplet ({completeness_score:.0%}) — HITL déclenché"
            })
            
            missing_fields = self._get_missing_fields(updated_profile)
            hitl_response = self._generate_incomplete_profile_response(missing_fields, completeness_score)
            
            self.execution_log.append({
                "timestamp": datetime.now(),
                "query": query,
                "steps": execution_steps,
                "profile_completeness": completeness_score,
                "blocked": True
            })
            
            return {
                "response": hitl_response,
                "profile": updated_profile,
                "steps": execution_steps,
                "blocked": True,
                "completeness_score": completeness_score,
                "missing_fields": missing_fields
            }
        
        execution_steps.append({
            "agent": "Profiler", 
            "status": "done", 
            "message": f"Profil complet ({completeness_score:.0%}) — Pipeline continue"
        })
        # ====================================================================================
        
        # ÉTAPE 3: RETRIEVER - Recherche RAG
        st.session_state.agent_phase = "retriever"
        relevant_jobs = self.retriever.search(query, updated_profile, k=8)
        execution_steps.append({"agent": "Retriever", "status": "done", "message": f"{len(relevant_jobs)} offres pertinentes trouvées"})
        
        # ÉTAPE 4: SCORER - Scoring
        st.session_state.agent_phase = "scorer"
        scored_jobs = []
        for job in relevant_jobs:
            score = self.scorer.calculate_compatibility(updated_profile, job)
            scored_jobs.append((job, score))
        scored_jobs.sort(key=lambda x: x[1], reverse=True)
        top_jobs = scored_jobs[:3]
        execution_steps.append({"agent": "Scorer", "status": "done", "message": "Compatibilité calculée"})
        
        # HUMAN-IN-THE-LOOP
        if require_approval and top_jobs:
            st.session_state.pending_approval = {
                "jobs": [(j["metier"], s) for j, s in top_jobs],
                "profile": updated_profile,
                "query": query
            }
            execution_steps.append({"agent": "HITL", "status": "pending", "message": "En attente validation utilisateur"})
            return {
                "requires_approval": True,
                "approval_data": st.session_state.pending_approval,
                "steps": execution_steps
            }
        
        # ÉTAPE 5: GENERATOR
        st.session_state.agent_phase = "generator"
        jobs_list = [j for j, _ in top_jobs]
        scores_list = [s for _, s in top_jobs]
        response = self.generator.generate_response(query, updated_profile, jobs_list, scores_list)
        execution_steps.append({"agent": "Generator", "status": "done", "message": "Réponse générée"})
        
        # ÉTAPE 6: EVALUATOR
        st.session_state.agent_phase = "evaluator"
        eval_context = {"profile": updated_profile, "query": query}
        evaluation = self.evaluator.evaluate_response(response, query, eval_context)
        execution_steps.append({"agent": "Evaluator", "status": "done", "message": f"Score qualité: {evaluation['score']}/100 ({evaluation['grade']})"})
        
        response = self.guardrail.filter_output(response)
        
        self.execution_log.append({
            "timestamp": datetime.now(),
            "query": query,
            "steps": execution_steps,
            "evaluation": evaluation,
            "profile_completeness": completeness_score
        })
        
        return {
            "response": response,
            "profile": updated_profile,
            "steps": execution_steps,
            "evaluation": evaluation,
            "top_jobs": top_jobs,
            "completeness_score": completeness_score
        }
class LLMClient:
    """Client LLM sécurisé avec prompt evaluation"""
    
    def __init__(self):
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.prompt_templates = {
            "default": "Tu es un expert en orientation professionnelle.",
            "creative": "Tu es un mentor bienveillant et inspirant.",
            "analytical": "Tu es un analyste de données précis et factuel."
        }
        self.current_template = "default"
        self.ab_test_active = False
    
    def generate(self, prompt: str, system_role: str = None, template: str = None) -> str:
        """Génère une réponse avec le template choisi"""
        
        system_content = system_role or self.prompt_templates.get(template or self.current_template, self.prompt_templates["default"])
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Erreur de génération: {str(e)}"
    
    def ab_test(self, prompt: str) -> Tuple[str, str]:
        """Compare deux templates différents"""
        response_a = self.generate(prompt, template="default")
        response_b = self.generate(prompt, template="creative")
        return response_a, response_b

# =========================
# 6. SESSION STATE
# =========================
def init_state():
    defaults = {
        "messages": [],
        "api_history": [],
        "loading": False,
        "run_analysis": False,
        "user_profile": {},
        "agent_phase": None,
        "orchestrator": None,
        "llm_client": None,
        "pending_approval": None,
        "show_evaluation": False,
        "ab_test_mode": False,
        "last_evaluation": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# Initialiser les clients
if st.session_state.llm_client is None:
    st.session_state.llm_client = LLMClient()

if st.session_state.orchestrator is None:
    st.session_state.orchestrator = AgentOrchestrator(st.session_state.llm_client)

# =========================
# 7. UI COMPONENTS
# =========================
def render_hero():
    st.markdown("""
    <div class="hero">
        <div class="badge"><span class="badge-dot"></span>Multi-Agent System · RAG Vectoriel · HITL · Guardrails</div>
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

def render_agent_steps(steps: list):
    """Affiche les étapes des agents"""
    steps_html = ""
    for step in steps:
        status_icon = "✅" if step["status"] == "done" else "⏳" if step["status"] == "pending" else "❌"
        status_class = "done" if step["status"] == "done" else "active" if step["status"] == "pending" else "blocked"
        steps_html += f'<div class="agent-step {status_class}"><span class="step-icon">{status_icon}</span>{step["agent"]}: {step["message"]}</div>'
    
    st.markdown(
        f'<div class="agent-steps"><div class="agent-bubble">{steps_html}</div></div>',
        unsafe_allow_html=True
    )

def render_messages():
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="bubble-user"><div class="msg-user">{msg["content"]}</div></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="bubble-ai"><div class="msg-ai">{msg["content"]}</div></div>',
                unsafe_allow_html=True
            )
    
    # Afficher les étapes agents si loading
    if st.session_state.loading and st.session_state.get("current_steps"):
        render_agent_steps(st.session_state.current_steps)
    
    # Afficher l'évaluation si disponible
    if st.session_state.get("show_evaluation") and st.session_state.get("last_evaluation"):
        eval_data = st.session_state.last_evaluation
        st.info(f"📊 **Évaluation de la réponse** | Score: {eval_data['score']}/100 ({eval_data['grade']})\n\n" + 
                "\n".join([f"• {f}" for f in eval_data['feedback']]))
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_hitl_modal():
    """Modal pour human-in-the-loop"""
    if st.session_state.get("pending_approval"):
        data = st.session_state.pending_approval
        
        st.markdown('<div class="hitl-overlay"></div>', unsafe_allow_html=True)
        st.markdown(f'''
        <div class="hitl-modal">
            <div class="hitl-title">👤 Validation utilisateur requise</div>
            <div class="hitl-content">
                <strong>Analyse de ton profil :</strong><br>
                Niveau: {data["profile"].get("niveau", "Non spécifié")}<br>
                Intérêts: {", ".join(data["profile"].get("interests", []))}<br><br>
                
                <strong>Top 3 métiers identifiés :</strong><br>
                {", ".join([f"{j[0]} ({j[1]:.0f}%)" for j in data["jobs"]])}<br><br>
                
                <strong>Question :</strong> {data["query"]}<br><br>
                
                Ces recommandations te semblent-elles pertinentes ?
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Oui, continuer", key="hitl_approve"):
                st.session_state.pending_approval = None
                st.session_state.run_analysis = True
                st.session_state.pending_query = data["query"]
                st.rerun()
        with col2:
            if st.button("❌ Non, réessayer", key="hitl_reject"):
                st.session_state.pending_approval = None
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "D'accord, peux-tu me donner plus de détails sur ton profil pour que je puisse mieux t'aider ? Quelles sont tes passions, ton niveau d'études, ou tes contraintes spécifiques ?"
                })
                st.rerun()

def render_input_bar():
    st.markdown('<div class="input-bar">', unsafe_allow_html=True)
    
    # Options avancées
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        hitl_mode = st.checkbox("👤 Mode validation", value=False, help="Active la validation humaine avant génération")
    with col2:
        eval_mode = st.checkbox("📊 Afficher évaluation", value=st.session_state.show_evaluation, help="Affiche le score de qualité")
        st.session_state.show_evaluation = eval_mode
    with col3:
        if st.button("🧪 A/B Test Prompt", help="Compare deux styles de réponse"):
            st.session_state.ab_test_mode = not st.session_state.ab_test_mode
    
    # Quick chips
    selected_quick = None
    if len(st.session_state.messages) < 3:
        quick_items = [
            "🎓 Terminale Maths, passionné IA",
            "💻 Je n'aime pas les maths, que faire ?",
            "💰 Meilleurs salaires au Maroc",
            "🔐 Cybersécurité, bon choix ?",
        ]
        cols = st.columns(4)
        for i, q in enumerate(quick_items):
            with cols[i]:
                if st.button(q, key=f"chip_{i}"):
                    selected_quick = q
    
    user_input = st.chat_input("Décris ton profil ou pose ta question...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if selected_quick:
        user_input = selected_quick
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.loading = True
        st.session_state.run_analysis = True
        st.session_state.pending_query = user_input
        st.session_state.hitl_mode = hitl_mode
        st.rerun()

# =========================
# 8. MAIN PIPELINE
# =========================
def main():
    # Afficher HITL modal si nécessaire
    if st.session_state.get("pending_approval"):
        render_hitl_modal()
    
    if not st.session_state.messages:
        render_hero()
    
    render_messages()
    render_input_bar()
    
    # Pipeline de traitement
    if st.session_state.get("run_analysis") and st.session_state.get("pending_query"):
        st.session_state.run_analysis = False
        query = st.session_state.pop("pending_query")
        hitl_mode = st.session_state.get("hitl_mode", False)
        
        # Exécuter le pipeline multi-agents
        result = st.session_state.orchestrator.process_query(
            query=query,
            profile=st.session_state.user_profile,
            history=st.session_state.api_history,
            require_approval=hitl_mode
        )
        
        # Stocker les étapes pour affichage
        st.session_state.current_steps = result.get("steps", [])
        
        # Gérer le cas HITL
        if result.get("requires_approval"):
            st.session_state.loading = False
            st.rerun()
        
        # Cas normal avec réponse
        if "response" in result:
            response = result["response"]
            st.session_state.user_profile = result.get("profile", st.session_state.user_profile)
            
            # Stocker l'évaluation
            if "evaluation" in result:
                st.session_state.last_evaluation = result["evaluation"]
            
            # Historique
            st.session_state.api_history.append({"role": "user", "content": query})
            st.session_state.api_history.append({"role": "assistant", "content": response})
            
            if len(st.session_state.api_history) > 16:
                st.session_state.api_history = st.session_state.api_history[-16:]
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Mode A/B test
            if st.session_state.ab_test_mode and len(st.session_state.messages) % 2 == 0:
                # Générer une réponse alternative pour test
                alt_response = st.session_state.llm_client.generate(
                    f"Réponds à cette question d'orientation: {query}",
                    template="creative"
                )
                with st.expander("🧪 Version alternative (A/B Test)"):
                    st.write(alt_response)
                    if st.button("👍 Préférer cette version"):
                        st.session_state.llm_client.current_template = "creative"
                        st.success("Template changé pour les futures réponses !")
        
        st.session_state.loading = False
        st.rerun()

if __name__ == "__main__":
    main()