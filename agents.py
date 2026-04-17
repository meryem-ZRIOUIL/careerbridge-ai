# agents.py - Version avec dialogue intelligent (sans blocage)
import re
import json
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime
from rag import VectorDatabase
from llm import LLMClient

# =========================
# DONNÉES MARCHÉ
# =========================
def load_market_data():
    data_path = "data/market_ma.json"
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

MARKET_DATA = load_market_data()


# =========================
# GUARDRAIL AGENT
# =========================
class GuardrailAgent:
    def run(self, query: str) -> Dict:
        blocked_words = [
            "hack", "illegal", "fraude", "ignore instructions", 
            "system prompt", "roleplay", "drop table", "delete from"
        ]
        query_lower = query.lower()
        
        for word in blocked_words:
            if word in query_lower:
                return {"valid": False, "reason": f"Requête non autorisée: {word}"}
        
        return {"valid": True}


# =========================
# PROFILER AGENT
# =========================
class ProfilerAgent:
    def __init__(self):
        self.interests_map = {
            "tech": ["informatique", "programmation", "code", "ia", "data", "python", "web", "digital", "dev", "software", "cybersecurite", "securite", "hacking"],
            "business": ["commerce", "vente", "marketing", "finance", "gestion", "management", "business", "economie"],
            "creative": ["design", "création", "artistique", "photographie", "video", "graphisme"],
            "scientific": ["sciences", "biologie", "chimie", "physique", "mathematiques", "recherche"],
            "humanities": ["langues", "communication", "psychologie", "enseignement", "lettres", "philosophie"]
        }
        
        self.niveau_map = {
            "terminale": "bac", "bac": "bac", "lycee": "bac",
            "bac+2": "bac+2", "bts": "bac+2", "dut": "bac+2",
            "licence": "bac+3", "bac+3": "bac+3", 
            "master": "bac+5", "ingenieur": "bac+5", "bac+5": "bac+5"
        }
        
        self.villes = ["casablanca", "rabat", "tanger", "marrakech", "fes", "agadir", "kenitra", "tetouan"]
    
    def run(self, query: str, profile: Dict) -> Dict:
        query_lower = query.lower()
        
        # Extraire niveau
        niveau = profile.get("niveau", "")
        for kw, nv in self.niveau_map.items():
            if kw in query_lower:
                niveau = nv
                break
        
        # Extraire intérêts
        current_interests = set(profile.get("interests", []))
        for category, keywords in self.interests_map.items():
            if any(kw in query_lower for kw in keywords):
                current_interests.add(category)
        
        # Extraire ville
        ville = profile.get("ville", "")
        for v in self.villes:
            if v in query_lower:
                ville = v.capitalize()
                break
        
        # Extraire contraintes
        constraints = set(profile.get("constraints", []))
        if any(w in query_lower for w in ["pas les maths", "n'aime pas les maths", "deteste les maths"]):
            constraints.add("no_math")
        if any(w in query_lower for w in ["pas l'informatique", "n'aime pas l'informatique"]):
            constraints.add("no_tech")
        
        profile["niveau"] = niveau
        profile["interests"] = list(current_interests)
        profile["ville"] = ville
        profile["constraints"] = list(constraints)
        
        # Calcul de complétude
        completeness = 0.0
        if profile.get("niveau"): completeness += 0.35
        if profile.get("interests"): completeness += 0.45
        if profile.get("ville"): completeness += 0.20
        
        # Identifier les champs manquants
        missing = []
        if not profile.get("niveau"): missing.append("niveau d'études")
        if not profile.get("interests"): missing.append("centres d'intérêt")
        if not profile.get("ville"): missing.append("ville")
        
        return {
            "profile": profile,
            "completeness": completeness,
            "missing": missing
        }


# =========================
# RETRIEVER AGENT
# =========================
class RetrieverAgent:
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
    
    def run(self, query: str, profile: Dict = None) -> List[Dict]:
        enriched_query = query
        if profile and profile.get("interests"):
            enriched_query += " " + " ".join(profile["interests"])
        if profile and profile.get("ville"):
            enriched_query += " " + profile["ville"]
        
        results = self.vector_db.search(enriched_query, k=8)
        
        if not results and MARKET_DATA:
            return MARKET_DATA[:5]
        
        return results


# =========================
# SCORER AGENT
# =========================
class ScorerAgent:
    def run(self, jobs: List[Dict], profile: Dict) -> List[Dict]:
        results = []
        
        for job in jobs:
            score = 30.0
            
            # Bonus intérêts
            interests = profile.get("interests", [])
            job_tags = set(job.get("tags", []))
            
            interest_match = {
                "tech": {"informatique", "data", "ia", "python", "web", "tech", "dev", "securite", "cybersecurite"},
                "business": {"commerce", "marketing", "finance", "gestion", "business"},
                "creative": {"design", "creation", "artistique"},
                "scientific": {"sciences", "biologie", "chimie", "physique"},
                "humanities": {"langues", "communication", "psychologie"}
            }
            
            match_score = 0
            for interest in interests:
                if interest in interest_match:
                    match_score += len(job_tags & interest_match[interest]) * 7
            score += min(match_score, 35)
            
            # Bonus salaire
            salaire_max = 0
            if "salaire_max" in job:
                salaire_max = job.get("salaire_max", 0)
            elif "salaire_debutant" in job:
                import re
                numbers = re.findall(r'(\d+)', job.get("salaire_debutant", ""))
                if len(numbers) >= 2:
                    salaire_max = int(numbers[1])
            
            if salaire_max > 15000:
                score += 20
            elif salaire_max > 12000:
                score += 15
            elif salaire_max > 10000:
                score += 10
            elif salaire_max > 8000:
                score += 5
            
            # Bonus demande marché
            demand_scores = {
                "Critique": 15, "CRITIQUE": 15,
                "Très Haute": 12, "TRÈS HAUTE": 12,
                "Haute": 8, "HAUTE": 8,
                "Moyenne": 4
            }
            demande = job.get("demande", "Moyenne")
            score += demand_scores.get(demande, 4)
            
            results.append({
                "job": job,
                "score": min(100, score),
                "salaire": job.get("salaire_debutant", job.get("salaire_debut", "N/C"))
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)


# =========================
# GENERATOR AGENT (VERSION INTELLIGENTE)
# =========================
class GeneratorAgent:
    def __init__(self, llm: LLMClient = None):
        self.llm = llm
    
    def run(self, query: str, scored_jobs: List[Dict], profile: Dict, missing: List[str] = None) -> str:
        # 🔥 SI DES INFOS MANQUENT, POSER DES QUESTIONS (PAS BLOQUER)
        if missing and len(missing) > 0:
            return self._ask_missing_info(query, profile, missing)
        
        # Si pas de résultats, proposer des métiers par défaut
        if not scored_jobs:
            return self._default_response(query, profile)
        
        # Essayer d'utiliser le LLM si disponible
        if self.llm and self.llm.client:
            try:
                prompt = self._build_prompt(query, scored_jobs, profile)
                response = self.llm.generate(prompt)
                if response:
                    return response
            except Exception as e:
                print(f"LLM error: {e}")
        
        # Fallback intelligent
        return self._fallback_response(query, scored_jobs, profile)
    
    def _ask_missing_info(self, query: str, profile: Dict, missing: List[str]) -> str:
        """Pose des questions ciblées au lieu de bloquer"""
        
        missing_text = {
            "niveau d'études": "🎓 Quel est votre niveau d'études ? (ex: terminale, Bac+3, Bac+5)",
            "centres d'intérêt": "❤️ Quels sont vos centres d'intérêt ? (ex: informatique, commerce, sciences)",
            "ville": "📍 Dans quelle ville habitez-vous ? (ex: Casablanca, Rabat, Tanger)"
        }
        
        # Déterminer ce qui manque
        questions = [missing_text.get(m, m) for m in missing if m in missing_text]
        
        if not questions:
            questions = ["Pourriez-vous me donner plus de détails sur votre profil ?"]
        
        response = f"""## 🔍 Pour mieux vous orienter

Je vois que vous êtes intéressé(e) par **{query[:50]}**.

Pour vous donner des recommandations précises et adaptées au marché marocain, j'aurais besoin de quelques informations :

"""
        for q in questions:
            response += f"{q}\n\n"
        
        response += """
💡 **Pourquoi ces informations ?**
- Le **niveau d'études** détermine les formations accessibles
- Les **centres d'intérêt** orientent vers les bons secteurs
- La **ville** permet de cibler les opportunités locales

Donnez-moi ces informations et je vous ferai des recommandations personnalisées ! 🎯"""
        
        return response
    
    def _default_response(self, query: str, profile: Dict) -> str:
        """Réponse par défaut quand aucun métier n'est trouvé"""
        return f"""## 💡 Suggestions pour "{query}"

Je vous propose de commencer par explorer ces secteurs porteurs au Maroc :

### 🚀 Secteurs en forte croissance
- **IT / Digital** : +20%/an, 35 000 postes
- **Énergies Renouvelables** : +25%/an, 18 000 postes
- **Aéronautique** : +15%/an, 12 000 postes

### 📌 Prochaines étapes
1. Précisez votre niveau d'études
2. Dites-moi ce qui vous passionne
3. Indiquez votre ville

Avec ces infos, je pourrai vous recommander des métiers précis ! 🎯"""
    
    def _build_prompt(self, query: str, scored_jobs: List[Dict], profile: Dict) -> str:
        jobs_text = "\n".join([
            f"- {j['job']['metier']} | Salaire: {j.get('salaire', '?')} | Score: {j['score']:.0f}%"
            for j in scored_jobs[:5]
        ])
        
        return f"""Tu es CareerBridge AI, conseiller d'orientation expert.

Profil utilisateur:
- Niveau: {profile.get('niveau', 'Non spécifié')}
- Intérêts: {', '.join(profile.get('interests', []))}
- Ville: {profile.get('ville', 'Non spécifiée')}

Question: {query}

Métiers recommandés (RAG + scoring):
{jobs_text}

Réponds de façon naturelle, structurée et utile. Donne des conseils personnalisés."""
    
    def _fallback_response(self, query: str, scored_jobs: List[Dict], profile: Dict) -> str:
        response = f"""## 🎯 Recommandations personnalisées

### Pour votre profil
- **Niveau:** {profile.get('niveau', 'Non spécifié')}
- **Intérêts:** {', '.join(profile.get('interests', []))}
- **Ville:** {profile.get('ville', 'Non spécifiée')}

### 🏆 Top métiers recommandés

"""
        for j in scored_jobs[:3]:
            job = j["job"]
            response += f"""
**{job.get('metier', '?')}** | {j.get('salaire', '?')} | Score: {j['score']:.0f}%
- 📍 {job.get('ville', 'Casablanca, Rabat')}
- 🎓 {job.get('ecoles', 'ENSIAS, INPT, ENSA')}
- 📈 Demande: {job.get('demande', 'Haute')}

"""
        
        response += """
### 💡 Conseil
N'hésitez pas à me poser des questions sur les salaires, les écoles ou les débouchés !

Souhaitez-vous plus de détails sur un métier en particulier ?"""
        
        return response


# =========================
# EVALUATOR AGENT
# =========================
class EvaluatorAgent:
    def run(self, response: str) -> Dict:
        score = 50
        feedback = []
        
        if "MAD" in response or "salaire" in response.lower():
            score += 25
            feedback.append("✅ Salaires inclus")
        
        if len(response) > 200:
            score += 15
            feedback.append("✅ Réponse détaillée")
        
        if any(w in response.lower() for w in ["conseil", "plan", "recommand"]):
            score += 10
            feedback.append("✅ Conseils actionnables")
        
        grade = "A" if score >= 80 else "B" if score >= 60 else "C"
        
        return {"score": min(100, score), "grade": grade, "feedback": feedback}


# =========================
# ORCHESTRATEUR (VERSION FLEXIBLE)
# =========================
class AgentOrchestrator:
    def __init__(self, llm: LLMClient, vector_db: VectorDatabase):
        self.guardrail = GuardrailAgent()
        self.profiler = ProfilerAgent()
        self.retriever = RetrieverAgent(vector_db)
        self.scorer = ScorerAgent()
        self.generator = GeneratorAgent(llm)
        self.evaluator = EvaluatorAgent()
        self.execution_log = []

    def process_query(self, query: str, profile: Dict, require_approval: bool = False) -> Dict:
        steps = {}
        
        # 1. Guardrail
        guard = self.guardrail.run(query)
        steps["guardrail"] = guard
        if not guard["valid"]:
            return {"response": f"⛔ {guard['reason']}", "steps": steps}
        
        # 2. Profiler
        prof = self.profiler.run(query, profile)
        profile = prof["profile"]
        missing = prof.get("missing", [])
        steps["profiler"] = prof
        
        # 3. Retriever (toujours essayer de chercher)
        jobs = self.retriever.run(query, profile)
        steps["retriever"] = jobs
        
        # 4. Scorer
        scored = self.scorer.run(jobs, profile)
        steps["scorer"] = scored
        
        # 5. Generator (pose des questions si info manquante)
        response = self.generator.run(query, scored, profile, missing)
        steps["generator"] = response
        
        # 6. Evaluator
        evaluation = self.evaluator.run(response)
        steps["evaluation"] = evaluation
        
        return {
            "response": response,
            "profile": profile,
            "steps": steps,
            "evaluation": evaluation,
            "top_jobs": scored[:3],
            "missing": missing
        }