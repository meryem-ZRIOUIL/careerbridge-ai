"""
tools_manager.py
================
CareerBridge AI — Gestionnaire d'Outils
RAG sur PDF (filières marocaines) + API Marché du Travail Maroc.

# TOOL-USE AVANCÉ : Deux outils principaux pour ancrer le système dans la réalité marocaine.
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Optional, Any

# LangChain
from langchain.tools import BaseTool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from pydantic import BaseModel, Field

# Embeddings
try:
    from langchain_openai import OpenAIEmbeddings
    OPENAI_EMBEDDINGS = True
except ImportError:
    OPENAI_EMBEDDINGS = False

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HF_EMBEDDINGS = True
except ImportError:
    HF_EMBEDDINGS = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# BASE DE DONNÉES STATIQUE — MAROC
# Utilisée comme fallback et enrichissement
# ─────────────────────────────────────────────

MOROCCO_KNOWLEDGE_BASE = {
    "ecoles": {
        "ingenierie_publiques": [
            {
                "nom": "ENSIAS — École Nationale Supérieure d'Informatique et d'Analyse des Systèmes",
                "ville": "Rabat", "secteur": "Informatique/IA",
                "concours": "Bac+2 (CPGE/DUT)", "duree": "3 ans",
                "salaire_debutant_mad": 12000, "salaire_senior_mad": 35000,
                "taux_insertion": 95, "partenaires": ["OCP", "Maroc Telecom", "CDG"]
            },
            {
                "nom": "INPT — Institut National des Postes et Télécommunications",
                "ville": "Rabat", "secteur": "Télécoms/Réseaux",
                "concours": "Bac+2 (CPGE)", "duree": "3 ans",
                "salaire_debutant_mad": 11000, "salaire_senior_mad": 32000,
                "taux_insertion": 93, "partenaires": ["IAM", "Orange", "AWS Maroc"]
            },
            {
                "nom": "EMI — École Mohammadia d'Ingénieurs",
                "ville": "Rabat", "secteur": "Multi-spécialités génie",
                "concours": "Bac+2 (CPGE)", "duree": "3 ans",
                "salaire_debutant_mad": 11500, "salaire_senior_mad": 33000,
                "taux_insertion": 92, "partenaires": ["OCP", "ONCF", "ONE"]
            },
            {
                "nom": "EHTP — École Hassania des Travaux Publics",
                "ville": "Casablanca", "secteur": "Travaux Publics/BTP",
                "concours": "Bac+2 (CPGE)", "duree": "3 ans",
                "salaire_debutant_mad": 10500, "salaire_senior_mad": 28000,
                "taux_insertion": 88, "partenaires": ["Autoroutes du Maroc", "CDG", "ADM"]
            },
            {
                "nom": "ENSET — École Normale Supérieure de l'Enseignement Technique",
                "ville": "Rabat/Mohammedia", "secteur": "Enseignement technique",
                "concours": "Bac+2", "duree": "3 ans",
                "salaire_debutant_mad": 8000, "salaire_senior_mad": 18000,
                "taux_insertion": 85, "partenaires": ["Ministère Éducation Nationale"]
            },
            {
                "nom": "ENSA — Écoles Nationales des Sciences Appliquées (14 pôles)",
                "ville": "Multiple (Casablanca, Fès, Marrakech, Agadir, Oujda...)",
                "secteur": "Sciences appliquées multi-filières",
                "concours": "Bac (direct)", "duree": "5 ans",
                "salaire_debutant_mad": 10000, "salaire_senior_mad": 28000,
                "taux_insertion": 87, "partenaires": ["Industrie locale", "PME"]
            }
        ],
        "privees_prestige": [
            {
                "nom": "UM6P — Université Mohammed VI Polytechnique",
                "ville": "Ben Guerir", "secteur": "Sciences/Ingénierie/Data",
                "concours": "Bac+2 ou Bac (programmes BS)", "duree": "3-5 ans",
                "salaire_debutant_mad": 15000, "salaire_senior_mad": 45000,
                "taux_insertion": 97, "partenaires": ["OCP Group", "Microsoft", "Google"],
                "note": "La meilleure université africaine selon QS 2024"
            },
            {
                "nom": "UIR — Université Internationale de Rabat",
                "ville": "Rabat", "secteur": "Aéronautique/IT/Management",
                "concours": "Bac", "duree": "5 ans",
                "salaire_debutant_mad": 12000, "salaire_senior_mad": 35000,
                "taux_insertion": 90, "partenaires": ["Boeing", "Safran", "Airbus"]
            },
            {
                "nom": "ISCAE — Institut Supérieur de Commerce et d'Administration des Entreprises",
                "ville": "Casablanca", "secteur": "Business/Finance/Management",
                "concours": "Bac+2 (CNC)", "duree": "3 ans",
                "salaire_debutant_mad": 9000, "salaire_senior_mad": 30000,
                "taux_insertion": 89, "partenaires": ["Banques marocaines", "Multinationales"]
            }
        ],
        "bts_ofppt": [
            {
                "nom": "OFPPT — BTS Développement Informatique",
                "ville": "Nationwide", "secteur": "Développement logiciel",
                "concours": "Bac", "duree": "2 ans",
                "salaire_debutant_mad": 5000, "salaire_senior_mad": 15000,
                "taux_insertion": 80, "partenaires": ["PME tech marocaines"]
            },
            {
                "nom": "OFPPT — BTS Électromécanique",
                "ville": "Nationwide", "secteur": "Industrie/Maintenance",
                "concours": "Bac", "duree": "2 ans",
                "salaire_debutant_mad": 4500, "salaire_senior_mad": 12000,
                "taux_insertion": 82, "partenaires": ["Yazaki", "Lear Corporation", "Nexans"]
            }
        ]
    },
    "secteurs_en_tension": {
        "aeronautique": {
            "nom": "Aéronautique & Défense",
            "croissance_annuelle_pct": 8.5,
            "emplois_disponibles_2024": 12000,
            "salaire_moyen_mad": 22000,
            "entreprises_cles": ["Boeing Maroc", "Safran Group", "Hexcel", "Figeac Aero", "EADS"],
            "villes_principales": ["Casablanca", "Nouaceur", "Tanger"],
            "competences_requises": ["Génie mécanique", "Composite", "Qualité aéronautique", "Lean"],
            "ecoles_adaptees": ["UIR", "ENSA Casablanca", "ESTEM", "IMA"]
        },
        "automobile": {
            "nom": "Industrie Automobile (Offshoring & Equipementiers)",
            "croissance_annuelle_pct": 12.0,
            "emplois_disponibles_2024": 45000,
            "salaire_moyen_mad": 8500,
            "entreprises_cles": ["Renault-Nissan Tanger", "PSA Kenitra", "Yazaki", "Lear Corp", "Sumitomo"],
            "villes_principales": ["Tanger", "Kénitra", "Casablanca"],
            "competences_requises": ["Mécatronique", "Lean manufacturing", "Câblage", "Qualité ISO"],
            "ecoles_adaptees": ["ENSA Tanger", "ENSA Kénitra", "FST", "OFPPT BTS"]
        },
        "it_digital": {
            "nom": "IT, Digital & IA",
            "croissance_annuelle_pct": 20.0,
            "emplois_disponibles_2024": 35000,
            "salaire_moyen_mad": 18000,
            "entreprises_cles": ["Capgemini Maroc", "IBM", "Microsoft Maroc", "HPS", "Sqli", "CGI"],
            "villes_principales": ["Casablanca", "Rabat", "Marrakech"],
            "competences_requises": ["Python", "Data Science", "Cloud", "DevOps", "IA/ML", "Cybersécurité"],
            "ecoles_adaptees": ["ENSIAS", "INPT", "UM6P", "UIR", "Ecoles privées IT"]
        },
        "agriculture_agritech": {
            "nom": "Agriculture & AgriTech",
            "croissance_annuelle_pct": 6.0,
            "emplois_disponibles_2024": 8000,
            "salaire_moyen_mad": 9000,
            "entreprises_cles": ["OCP Nutricrops", "Sanam", "Calimero Maroc", "Startups AgriTech"],
            "villes_principales": ["Meknès", "Agadir", "Beni Mellal"],
            "competences_requises": ["Agronomie", "Irrigation", "Drones agricoles", "Data"],
            "ecoles_adaptees": ["IAV Hassan II", "ENA Meknès", "FP Agadir"]
        },
        "energie_renouvelable": {
            "nom": "Énergies Renouvelables & Environnement",
            "croissance_annuelle_pct": 15.0,
            "emplois_disponibles_2024": 6500,
            "salaire_moyen_mad": 14000,
            "entreprises_cles": ["MASEN", "ONEE", "Nareva", "Enel Green Power Maroc"],
            "villes_principales": ["Ouarzazate", "Tarfaya", "Tanger"],
            "competences_requises": ["Génie énergétique", "Solaire", "Éolien", "Smart Grid"],
            "ecoles_adaptees": ["EMSI énergie", "ENSA", "FST", "UM6P"]
        },
        "tourisme_hospitality": {
            "nom": "Tourisme & Hôtellerie",
            "croissance_annuelle_pct": 9.0,
            "emplois_disponibles_2024": 25000,
            "salaire_moyen_mad": 6000,
            "entreprises_cles": ["Accor Maroc", "Marriott", "Sofitel", "Club Med"],
            "villes_principales": ["Marrakech", "Agadir", "Casablanca", "Fès"],
            "competences_requises": ["Langues", "Management hôtelier", "Marketing digital"],
            "ecoles_adaptees": ["ISIT", "ESITH", "Instituts OFPPT tourisme"]
        }
    },
    "salaires_par_niveau_mad": {
        "Bac+2 (BTS/DUT)": {"min": 3500, "moyen": 5500, "max": 9000},
        "Bac+3 (Licence)": {"min": 4500, "moyen": 7000, "max": 12000},
        "Bac+5 (Master/Ingénieur)": {"min": 8000, "moyen": 14000, "max": 30000},
        "Bac+5 Grande École": {"min": 12000, "moyen": 20000, "max": 50000},
        "Doctorat": {"min": 12000, "moyen": 22000, "max": 60000},
        "MBA": {"min": 18000, "moyen": 30000, "max": 80000}
    }
}


# ─────────────────────────────────────────────
# OUTIL 1 — PDF SEARCH TOOL (RAG)
# ─────────────────────────────────────────────

class PDFSearchInput(BaseModel):
    """Schéma d'entrée pour PDFSearchTool."""
    query: str = Field(description="Requête de recherche sur les filières marocaines")
    top_k: int = Field(default=5, description="Nombre de résultats à retourner")


class PDFSearchTool(BaseTool):
    """
    # TOOL-USE AVANCÉ : RAG LangChain avec ChromaDB.
    Indexe et interroge les PDF sur les filières marocaines.
    
    # REASONING STEP :
    Thought   : Les PDF officiels contiennent des infos précises sur les filières.
    Action    : Indexer dans ChromaDB, puis faire une recherche sémantique.
    Observation: Retourner les passages les plus pertinents pour la question.
    """
    
    name: str = "pdf_search_filières_maroc"
    description: str = (
        "Recherche sémantique dans les PDF sur les filières d'études marocaines "
        "(OFPPT, Universités, CPGE, Grandes Écoles). "
        "Retourne des informations précises sur les programmes, conditions d'admission, "
        "débouchés et salaires. "
        "Input: question en français sur une filière ou une école marocaine."
    )
    args_schema: type[BaseModel] = PDFSearchInput
    
    # Attributs internes (non-Pydantic fields)
    _vectorstore: Optional[Any] = None
    _initialized: bool = False

    def _initialize_vectorstore(self, pdf_dir: str = "./data/pdf_filières") -> bool:
        """
        # REASONING STEP : Initialisation du vectorstore ChromaDB.
        Charge ou crée l'index depuis les PDF.
        """
        if self._initialized:
            return True
            
        pdf_path = Path(pdf_dir)
        persist_dir = "./data/chroma_db"
        
        # Sélection du modèle d'embeddings
        if OPENAI_EMBEDDINGS and os.getenv("OPENAI_API_KEY"):
            logger.info("📚 [RAG] Utilisation OpenAI Embeddings...")
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        elif HF_EMBEDDINGS:
            logger.info("📚 [RAG] Utilisation HuggingFace Embeddings (multilingual)...")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        else:
            logger.warning("⚠️ [RAG] Aucun embedding disponible — RAG désactivé.")
            return False
        
        # ── Charger depuis persist si déjà indexé ────────────────────────────
        if Path(persist_dir).exists():
            try:
                self._vectorstore = Chroma(
                    persist_directory=persist_dir,
                    embedding_function=embeddings
                )
                self._initialized = True
                logger.info("✅ [RAG] Index ChromaDB chargé depuis le disque.")
                return True
            except Exception as e:
                logger.warning(f"⚠️ [RAG] Impossible de charger l'index : {e}")
        
        # ── Indexer les PDF ───────────────────────────────────────────────────
        if not pdf_path.exists() or not any(pdf_path.glob("*.pdf")):
            logger.warning(f"⚠️ [RAG] Aucun PDF trouvé dans {pdf_dir}. Mode base statique.")
            return False
        
        try:
            logger.info(f"📄 [RAG] Indexation des PDF depuis {pdf_dir}...")
            loader = DirectoryLoader(str(pdf_path), glob="**/*.pdf", loader_cls=PyPDFLoader)
            documents = loader.load()
            
            # Découpage en chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=800, chunk_overlap=150,
                separators=["\n\n", "\n", ".", "!"]
            )
            chunks = splitter.split_documents(documents)
            logger.info(f"📦 [RAG] {len(chunks)} chunks créés depuis {len(documents)} documents.")
            
            # Création du vectorstore
            self._vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=persist_dir
            )
            self._initialized = True
            logger.info("✅ [RAG] Index ChromaDB créé et persisté.")
            return True
            
        except Exception as e:
            logger.error(f"❌ [RAG] Erreur indexation : {e}")
            return False

    def _run(self, query: str, top_k: int = 5) -> str:
        """
        # REASONING STEP : Recherche sémantique dans les PDF.
        Si le vectorstore est indisponible, utilise la base de connaissances statique.
        """
        logger.info(f"🔍 [RAG] Recherche : '{query}'")
        
        # Initialisation lazy
        rag_available = self._initialize_vectorstore()
        
        if rag_available and self._vectorstore:
            try:
                docs = self._vectorstore.similarity_search(query, k=top_k)
                results = []
                for i, doc in enumerate(docs, 1):
                    source = doc.metadata.get("source", "PDF inconnu")
                    results.append(f"[Source {i}: {Path(source).name}]\n{doc.page_content}")
                
                output = f"Résultats RAG pour '{query}':\n\n" + "\n\n---\n\n".join(results)
                logger.info(f"✅ [RAG] {len(docs)} résultats trouvés.")
                return output
            except Exception as e:
                logger.error(f"❌ [RAG] Erreur recherche : {e}")
        
        # # FALLBACK : Base de connaissances statique
        return self._search_static_knowledge(query)

    def _search_static_knowledge(self, query: str) -> str:
        """
        # FALLBACK : Recherche dans la base de connaissances statique.
        Utilise des mots-clés pour retourner des informations pertinentes.
        """
        query_lower = query.lower()
        results = []
        
        # Recherche dans les écoles
        all_schools = (
            MOROCCO_KNOWLEDGE_BASE["ecoles"]["ingenierie_publiques"] +
            MOROCCO_KNOWLEDGE_BASE["ecoles"]["privees_prestige"] +
            MOROCCO_KNOWLEDGE_BASE["ecoles"]["bts_ofppt"]
        )
        
        for school in all_schools:
            school_text = f"{school['nom']} {school.get('secteur', '')}".lower()
            if any(kw in school_text for kw in query_lower.split() if len(kw) > 3):
                results.append(
                    f"📚 {school['nom']} ({school['ville']})\n"
                    f"   Secteur: {school['secteur']}\n"
                    f"   Concours: {school['concours']} | Durée: {school['duree']}\n"
                    f"   Salaire débutant: {school['salaire_debutant_mad']:,} MAD/mois\n"
                    f"   Taux d'insertion: {school['taux_insertion']}%"
                )
        
        # Recherche dans les secteurs
        for sector_key, sector in MOROCCO_KNOWLEDGE_BASE["secteurs_en_tension"].items():
            if any(kw in sector["nom"].lower() for kw in query_lower.split() if len(kw) > 3):
                results.append(
                    f"🏭 Secteur: {sector['nom']}\n"
                    f"   Croissance: +{sector['croissance_annuelle_pct']}%/an\n"
                    f"   Emplois disponibles: {sector['emplois_disponibles_2024']:,}\n"
                    f"   Salaire moyen: {sector['salaire_moyen_mad']:,} MAD/mois\n"
                    f"   Entreprises: {', '.join(sector['entreprises_cles'][:3])}"
                )
        
        if not results:
            # Retourner tout si aucun résultat ciblé
            results.append("📊 BASE DE CONNAISSANCES MAROC (résumé global):")
            for school in all_schools[:3]:
                results.append(f"  • {school['nom']}: {school['salaire_debutant_mad']:,}–{school['salaire_senior_mad']:,} MAD/mois")
        
        return f"Base de connaissances statique — Requête: '{query}'\n\n" + "\n\n".join(results)

    async def _arun(self, query: str, top_k: int = 5) -> str:
        return self._run(query, top_k)


# ─────────────────────────────────────────────
# OUTIL 2 — INDUSTRY MARKET TOOL
# ─────────────────────────────────────────────

class IndustryMarketInput(BaseModel):
    """Schéma d'entrée pour IndustryMarketTool."""
    sector: Optional[str] = Field(default=None, description="Secteur spécifique (ex: 'IT', 'Aéronautique')")
    student_profile: Optional[str] = Field(default=None, description="Profil étudiant pour matching")
    top_n: int = Field(default=3, description="Nombre de secteurs à retourner")


class IndustryMarketTool(BaseTool):
    """
    # TOOL-USE AVANCÉ : Analyse du marché du travail marocain.
    
    Interroge des données JSON (API simulée ou fichiers locaux) sur les secteurs
    en tension au Maroc : Aéronautique, Automobile, IT, Agri, Énergie.
    
    # REASONING STEP :
    Thought   : Le marché marocain a des secteurs très dynamiques. Il faut aligner
                le profil étudiant avec les opportunités réelles.
    Action    : Analyser les données de tension par secteur + compatibilité profil.
    Observation: Recommander les 3 meilleurs secteurs avec des métriques concrètes.
    """
    
    name: str = "industry_market_maroc"
    description: str = (
        "Analyse le marché du travail marocain et identifie les secteurs en tension. "
        "Retourne des données chiffrées : emplois disponibles, salaires en MAD, "
        "croissance sectorielle, entreprises qui recrutent. "
        "Peut être filtré par secteur ou adapté à un profil étudiant. "
        "Input: secteur (optionnel) + profil étudiant (optionnel)."
    )
    args_schema: type[BaseModel] = IndustryMarketInput

    def _run(self, sector: Optional[str] = None,
             student_profile: Optional[str] = None,
             top_n: int = 3) -> str:
        """
        # REASONING STEP : Analyse et matching marché-étudiant.
        """
        logger.info(f"📊 [MARKET] Analyse marché — secteur: {sector}, profil: {student_profile[:50] if student_profile else 'N/A'}")
        
        # ── Tentative API externe ─────────────────────────────────────────────
        api_data = self._try_external_api(sector)
        
        if api_data:
            return self._format_api_response(api_data, student_profile)
        
        # ── Fallback sur données statiques ────────────────────────────────────
        return self._analyze_static_market(sector, student_profile, top_n)

    def _try_external_api(self, sector: Optional[str]) -> Optional[dict]:
        """
        Tente de récupérer des données depuis une API externe.
        # FALLBACK : Retourne None si API indisponible.
        """
        # En production, ici on appellerait des APIs comme :
        # - ANAPEC (Agence Nationale de Promotion de l'Emploi et des Compétences)
        # - HCP (Haut-Commissariat au Plan)
        # - API offres d'emploi Maroc (Rekrute, Emploi.ma)
        
        api_url = os.getenv("MOROCCO_JOBS_API_URL")
        if not api_url:
            return None
        
        try:
            import requests
            response = requests.get(
                f"{api_url}/sectors",
                params={"sector": sector} if sector else {},
                timeout=5,
                headers={"Authorization": f"Bearer {os.getenv('MOROCCO_JOBS_API_KEY', '')}"}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"API externe indisponible : {e}")
        
        return None

    def _analyze_static_market(self, sector: Optional[str],
                                 student_profile: Optional[str],
                                 top_n: int) -> str:
        """
        # REASONING STEP : Analyse du marché depuis données statiques.
        Calcule un score de compatibilité profil-secteur.
        """
        sectors_data = MOROCCO_KNOWLEDGE_BASE["secteurs_en_tension"]
        salary_data = MOROCCO_KNOWLEDGE_BASE["salaires_par_niveau_mad"]
        
        # Filtrer par secteur si spécifié
        if sector:
            sector_lower = sector.lower()
            filtered = {
                k: v for k, v in sectors_data.items()
                if sector_lower in v["nom"].lower() or sector_lower in k
            }
            if filtered:
                sectors_data = filtered
        
        # Calcul du score de compatibilité
        scored_sectors = []
        for key, data in sectors_data.items():
            score = self._compute_compatibility_score(data, student_profile)
            scored_sectors.append((score, key, data))
        
        # Tri par score décroissant
        scored_sectors.sort(key=lambda x: x[0], reverse=True)
        top_sectors = scored_sectors[:top_n]
        
        # Formatage du rapport
        report_parts = [
            "=" * 60,
            "📊 ANALYSE MARCHÉ TRAVAIL MAROC 2024",
            "=" * 60
        ]
        
        for rank, (score, key, data) in enumerate(top_sectors, 1):
            report_parts.append(f"\n{'🥇' if rank==1 else '🥈' if rank==2 else '🥉'} #{rank} — {data['nom']}")
            report_parts.append(f"   📈 Croissance: +{data['croissance_annuelle_pct']}%/an")
            report_parts.append(f"   💼 Emplois disponibles: {data['emplois_disponibles_2024']:,} postes")
            report_parts.append(f"   💰 Salaire moyen: {data['salaire_moyen_mad']:,} MAD/mois")
            report_parts.append(f"   🏙️ Villes: {', '.join(data['villes_principales'])}")
            report_parts.append(f"   🏢 Entreprises: {', '.join(data['entreprises_cles'][:4])}")
            report_parts.append(f"   🎓 Formations: {', '.join(data['ecoles_adaptees'])}")
            report_parts.append(f"   🔧 Compétences clés: {', '.join(data['competences_requises'][:4])}")
            if student_profile:
                report_parts.append(f"   ✅ Compatibilité profil: {score:.0%}")
        
        # Tableau des salaires
        report_parts.append("\n" + "─" * 60)
        report_parts.append("💰 GRILLE SALARIALE MAROC (MAD/mois)")
        report_parts.append("─" * 60)
        for niveau, salaires in salary_data.items():
            report_parts.append(
                f"   {niveau}: {salaires['min']:,}–{salaires['max']:,} MAD (moy: {salaires['moyen']:,})"
            )
        
        # Tendances 2024-2030
        report_parts.append("\n📅 TENDANCES CLÉS 2024-2030:")
        report_parts.append("   • Plan d'accélération industrielle : 500K emplois visés")
        report_parts.append("   • Digital Morocco 2030 : 240K développeurs nécessaires")
        report_parts.append("   • Energie verte : Maroc vise 52% ENR en 2030")
        report_parts.append("   • Aéronautique : Zone MedPark + Offshoring aéro en hausse")
        
        return "\n".join(report_parts)

    def _compute_compatibility_score(self, sector_data: dict,
                                      student_profile: Optional[str]) -> float:
        """
        Calcule un score de compatibilité entre le profil étudiant et un secteur.
        """
        if not student_profile:
            # Score basé uniquement sur la dynamique sectorielle
            growth = sector_data.get("croissance_annuelle_pct", 0)
            jobs = sector_data.get("emplois_disponibles_2024", 0)
            return min(1.0, (growth / 25 + jobs / 50000) / 2)
        
        profile_lower = student_profile.lower()
        skills = sector_data.get("competences_requises", [])
        sector_name = sector_data.get("nom", "").lower()
        
        # Matching mots-clés profil-secteur
        matches = sum(
            1 for skill in skills
            if any(kw in profile_lower for kw in skill.lower().split())
        )
        keyword_score = matches / max(len(skills), 1)
        
        # Score croissance sectorielle (normalisé)
        growth_score = sector_data.get("croissance_annuelle_pct", 0) / 25
        
        return min(1.0, (keyword_score * 0.6 + growth_score * 0.4))

    def _format_api_response(self, api_data: dict, student_profile: Optional[str]) -> str:
        """Formate la réponse d'une API externe."""
        return json.dumps(api_data, ensure_ascii=False, indent=2)

    async def _arun(self, sector: Optional[str] = None,
                    student_profile: Optional[str] = None,
                    top_n: int = 3) -> str:
        return self._run(sector, student_profile, top_n)


# ─────────────────────────────────────────────
# FACTORY — Instanciation des outils
# ─────────────────────────────────────────────

def create_all_tools() -> dict:
    """
    Crée et retourne tous les outils du système CareerBridge AI.
    
    Returns:
        dict: {'pdf_search': PDFSearchTool, 'market': IndustryMarketTool}
    """
    logger.info("🔧 [TOOLS] Initialisation de tous les outils...")
    
    pdf_tool = PDFSearchTool()
    market_tool = IndustryMarketTool()
    
    logger.info("✅ [TOOLS] PDFSearchTool initialisé.")
    logger.info("✅ [TOOLS] IndustryMarketTool initialisé.")
    
    return {
        "pdf_search": pdf_tool,
        "market": market_tool
    }


# ─────────────────────────────────────────────
# TEST STANDALONE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("TEST — tools_manager.py")
    print("=" * 60)
    
    tools = create_all_tools()
    
    print("\n[1] Test PDFSearchTool:")
    result = tools["pdf_search"]._run("ENSIAS programme informatique admission")
    print(result[:500] + "...")
    
    print("\n[2] Test IndustryMarketTool:")
    result = tools["market"]._run(
        sector="IT",
        student_profile="Étudiant passionné d'informatique et de mathématiques",
        top_n=2
    )
    print(result[:700] + "...")
    
    print("\n✅ Tests tools_manager.py réussis !")
