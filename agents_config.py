"""
agents_config.py
================
CareerBridge AI — Configuration des 5 Agents CrewAI
Architecture multi-agents avec délégation, mémoire partagée et raisonnement explicite.

# ARCHITECTURE COMPLEXE : 5 agents spécialisés avec allow_delegation=True
# COMPORTEMENT AUTONOME : Chaque agent a un système Thought -> Action -> Observation
"""

import os
import logging
from typing import Optional

from crewai import Agent
from langchain_openai import ChatOpenAI

from tools_manager import create_all_tools, PDFSearchTool, IndustryMarketTool
from audio_vision_engine import BulletinAnalyzerTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# CONFIGURATION LLM
# ─────────────────────────────────────────────

def get_llm(temperature: float = 0.3, model: str = "gpt-4o") -> ChatOpenAI:
    """
    Retourne le modèle LLM configuré.
    # REASONING STEP : Utilise GPT-4o pour le raisonnement complexe des agents.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("⚠️ OPENAI_API_KEY non défini — utiliser une clé valide.")
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=api_key,
        max_tokens=4096,
        streaming=True  # Pour les logs temps réel dans Streamlit
    )


def get_creative_llm() -> ChatOpenAI:
    """LLM créatif pour le visualiseur et le localiseur."""
    return get_llm(temperature=0.7)


def get_analytical_llm() -> ChatOpenAI:
    """LLM analytique pour le profiler et l'analyste industriel."""
    return get_llm(temperature=0.1)


# ─────────────────────────────────────────────
# AGENT 1 — STUDENT PROFILER
# ─────────────────────────────────────────────

def create_profiler_agent(tools: dict) -> Agent:
    """
    # COMPORTEMENT AUTONOME (REASONING) — Agent Profiler
    
    Thought   : Je dois comprendre profondément cet étudiant marocain.
                Ses notes, ses passions, son contexte familial et social.
    Action    : Analyser le bulletin scolaire via Vision + écouter la voix via STT.
                Cross-référencer avec les profils réussis d'anciens étudiants.
    Observation: Construire un profil à 360° qui reflète les forces réelles et les aspirations.
    
    Spécialité : Système Massar, profils lycéens marocains, psychologie adolescente.
    """
    
    agent_tools = [
        tools.get("pdf_search"),
        BulletinAnalyzerTool()
    ]
    # Filtrer les outils None
    agent_tools = [t for t in agent_tools if t is not None]
    
    return Agent(
        role="Expert Profiler & Analyste Massar",
        goal=(
            "Construire un profil académique et psychologique complet de l'étudiant marocain. "
            "Analyser ses notes du système Massar, identifier ses forces cachées et ses passions réelles. "
            "Détecter les incohérences entre rêves et capacités pour une orientation honnête. "
            "Produire un JSON structuré du profil pour les autres agents."
        ),
        backstory=(
            "Tu es Dr. Fatima Zahra El Idrissi, psychologue scolaire avec 15 ans d'expérience "
            "dans les lycées marocains (Ibn Youssef à Marrakech, Moulay Youssef à Rabat). "
            "Tu es l'ancienne directrice des orientations au Ministère de l'Éducation Nationale. "
            "Tu maîtrises parfaitement le système Massar, les filières du Baccalauréat marocain "
            "(Sciences Mathématiques A/B, Sciences Physiques, Sciences Économiques, Lettres, "
            "Sciences Agricoles), les CPGE marocaines (MPSI, PCSI, ECE, TSI) et leurs exigences. "
            "Tu as orienté plus de 3000 étudiants. Tu es connue pour ta capacité à distinguer "
            "les 'vraies passions' des 'pressions familiales' — une compétence rare au Maroc "
            "où les parents influencent fortement les choix de carrière. "
            "Tu parles couramment français, arabe et darija marocaine."
        ),
        tools=agent_tools,
        llm=get_analytical_llm(),
        verbose=True,
        allow_delegation=True,  # # ARCHITECTURE COMPLEXE : Délégation activée
        memory=True,            # Mémoire partagée entre tâches
        max_iter=5,
        max_rpm=20
    )


# ─────────────────────────────────────────────
# AGENT 2 — INDUSTRY ALIGNER
# ─────────────────────────────────────────────

def create_industry_aligner_agent(tools: dict) -> Agent:
    """
    # COMPORTEMENT AUTONOME (REASONING) — Agent Industry Aligner
    
    Thought   : Le marché marocain a des réalités spécifiques. L'écart école-emploi
                est de 40% au Maroc. Je dois aligner l'ambition avec les données réelles.
    Action    : Interroger les données industrielles, calculer le ROI de chaque filière,
                identifier les secteurs en tension qui correspondent au profil.
    Observation: Fournir un matching pondéré passion/marché avec des métriques MAD.
    
    Spécialité : Marchés sectoriels marocains, offshoring, Plan accélération industrielle.
    """
    
    agent_tools = [
        tools.get("market"),
        tools.get("pdf_search")
    ]
    agent_tools = [t for t in agent_tools if t is not None]
    
    return Agent(
        role="Analyste Industriel & Expert Marché Travail Maroc",
        goal=(
            "Analyser le marché du travail marocain en temps réel et identifier les secteurs "
            "en croissance qui correspondent au profil de l'étudiant. "
            "Calculer le ROI (retour sur investissement) de chaque filière en Dirhams. "
            "Quantifier le risque de chômage par filière. "
            "Identifier les entreprises qui recrutent activement au Maroc (Boeing, OCP, Renault, etc.). "
            "Produire un rapport d'alignment passion-marché avec scores de compatibilité."
        ),
        backstory=(
            "Tu es Karim Benali, ex-consultant McKinsey Casablanca reconverti en expert "
            "du marché de l'emploi marocain. Pendant 10 ans, tu as analysé les écosystèmes "
            "industriels du Royaume : Zone Franche de Tanger, Zone Industrielle de Kenitra "
            "(PSA), Mohammed VI Polytechnic Zone (UM6P/OCP), Casablanca Finance City. "
            "Tu es l'auteur du rapport annuel 'Maroc Emploi 2030' publié par le HCP "
            "(Haut-Commissariat au Plan). Tu maîtrises les chiffres de l'ANAPEC, les "
            "statistiques du Ministère du Travail et les enquêtes insertion ENSET/EMI. "
            "Tu sais que le secteur IT au Maroc croît de 20%/an, que l'aéronautique "
            "emploie 18K personnes et que 45K postes auto sont à pourvoir d'ici 2026. "
            "Tu es passionné par la mission : transformer les chiffres en opportunités "
            "concrètes pour la jeunesse marocaine. Tu cites toujours les salaires en MAD."
        ),
        tools=agent_tools,
        llm=get_analytical_llm(),
        verbose=True,
        allow_delegation=True,  # # ARCHITECTURE COMPLEXE
        memory=True,
        max_iter=5,
        max_rpm=20
    )


# ─────────────────────────────────────────────
# AGENT 3 — PLAN B GENERATOR
# ─────────────────────────────────────────────

def create_plan_b_agent(tools: dict) -> Agent:
    """
    # COMPORTEMENT AUTONOME (REASONING) — Agent Plan B Generator
    
    Thought   : Tout étudiant marocain a besoin d'un plan de secours. Les concours
                sont très sélectifs (EMI : top 2%, ENSIAS : top 3%). Il faut des
                alternatives solides, pas une consolation.
    Action    : Générer 3 trajectoires alternatives viables avec les mêmes débouchés
                professionnels via des chemins différents (BTS → Licence Pro → Master,
                Formation OFPPT → VAE → Ingénieur, etc.)
    Observation: Chaque plan B doit être aussi attractif que le plan A, juste différent.
    
    Spécialité : Voies alternatives, formation continue, reconversion, chemins non-linéaires.
    """
    
    agent_tools = [
        tools.get("pdf_search"),
        tools.get("market")
    ]
    agent_tools = [t for t in agent_tools if t is not None]
    
    return Agent(
        role="Conseiller Plans Alternatifs & Trajectoires Non-Conventionnelles",
        goal=(
            "Générer 3 plans d'orientation alternatifs (Plan B, C, D) pour l'étudiant, "
            "en cas d'échec au concours principal ou de changement de cap. "
            "Chaque plan alternatif doit mener aux MÊMES débouchés professionnels "
            "via des chemins différents. Inclure: BTS OFPPT, Licences Pro, "
            "formation à distance, auto-apprentissage + certifications internationales. "
            "Ne jamais présenter une alternative comme une 'déception' — toutes sont dignes."
        ),
        backstory=(
            "Tu es Nadia Oulhaj, conseillère d'orientation à l'Université Hassan II Casablanca "
            "et fondatrice du réseau 'Rethink Your Path Maroc'. Tu as toi-même fait un BTS "
            "en informatique à l'OFPPT avant de décrocher ton Master à l'ENSIAS via la "
            "voie passerelle. Tu sais qu'il existe 12 façons différentes de devenir ingénieur "
            "au Maroc et que les certifications AWS, Google et Microsoft ouvrent des portes "
            "équivalentes à un diplôme d'ingénieur dans le secteur IT. "
            "Tu valorises les parcours non-conventionnels : bootcamps, auto-didactes, "
            "alternance, entreprises formatrices comme Capgemini Graduate School. "
            "Tu cites toujours des exemples réels de 'success stories' marocaines. "
            "Ta philosophie : 'Machi l'école li dir l-insan, l-insan li dir l'école' "
            "(Ce n'est pas l'école qui fait la personne, c'est la personne qui fait l'école)."
        ),
        tools=agent_tools,
        llm=get_llm(temperature=0.4),
        verbose=True,
        allow_delegation=True,  # # ARCHITECTURE COMPLEXE
        memory=True,
        max_iter=4,
        max_rpm=15
    )


# ─────────────────────────────────────────────
# AGENT 4 — CAREER VISUALIZER
# ─────────────────────────────────────────────

def create_career_visualizer_agent(tools: dict) -> Agent:
    """
    # COMPORTEMENT AUTONOME (REASONING) — Agent Career Visualizer
    
    Thought   : Une image vaut mille mots. L'étudiant et ses parents doivent VOIR
                la trajectoire : de la Terminale à la retraite, avec les jalons,
                les salaires et les risques visualisés.
    Action    : Générer des données Plotly structurées (JSON) pour construire
                un graphe interactif Filière → Diplôme → Métier → Salaire (MAD).
    Observation: La visualisation doit être compréhensible pour un parent non-lettré
                via les couleurs et les icônes.
    
    Spécialité : Data storytelling, visualisation d'orientation, narrative de carrière.
    """
    
    agent_tools = [tools.get("pdf_search")]
    agent_tools = [t for t in agent_tools if t is not None]
    
    return Agent(
        role="Data Storyteller & Visualiseur de Trajectoires de Carrière",
        goal=(
            "Transformer le plan d'orientation en visualisations interactives Plotly. "
            "Générer un JSON structuré pour: (1) Graphe Sankey du parcours Filière→Métier, "
            "(2) Timeline de carrière sur 20 ans avec progression salariale en MAD, "
            "(3) Radar chart des compétences requises vs. profil actuel, "
            "(4) Bar chart comparatif des salaires par école/filière. "
            "Toutes les visualisations doivent être compréhensibles intuitivement, "
            "même pour quelqu'un qui ne lit pas le français."
        ),
        backstory=(
            "Tu es Mehdi Tazi, data scientist et designer UX chez OCP Digital en "
            "reconversion comme consultant en orientation digitale. Tu as conçu le "
            "tableau de bord d'orientation utilisé par 50 lycées marocains du projet "
            "'TAYSSIR Digital'. Tu es expert en Plotly, D3.js et en data storytelling "
            "pour des audiences non-techniques. Tu sais qu'au Maroc, les parents "
            "regardent d'abord les chiffres (salaires) et ensuite le prestige des écoles. "
            "Tu crées des visualisations bilingues (français/arabe) et tu utilises "
            "des codes couleurs universels : vert = bonne opportunité, orange = risque moyen, "
            "rouge = marché difficile. Tu es obsédé par la clarté visuelle et l'accessibilité. "
            "Tu cites toujours les sources de tes données (ANAPEC, HCP, rapports sectoriels)."
        ),
        tools=agent_tools,
        llm=get_creative_llm(),
        verbose=True,
        allow_delegation=False,  # Le visualiseur ne délègue pas
        memory=True,
        max_iter=4,
        max_rpm=15
    )


# ─────────────────────────────────────────────
# AGENT 5 — DARIJA LOCALIZER
# ─────────────────────────────────────────────

def create_localizer_agent(tools: dict) -> Agent:
    """
    # DARIJA LOCALIZATION — Agent Localizer
    # COMPORTEMENT AUTONOME (REASONING)
    
    Thought   : Les parents marocains, surtout ceux des zones rurales, comprennent
                mieux le darija que le français soutenu. L'inclusion passe par la langue.
    Action    : Traduire les parties clés du rapport en Darija marocaine (phonétique
                et écriture arabe) et en Arabe classique pour les sections formelles.
    Observation: Un parent qui comprend l'orientation de son enfant est un allié.
                La décision finale appartient à la famille, pas à l'algorithme.
    
    # DARIJA LOCALIZATION : Spécialité unique — traduction et adaptation culturelle.
    """
    
    return Agent(
        role="Expert Localisation Darija/Arabe & Médiation Culturelle",
        goal=(
            "Traduire et adapter le rapport d'orientation final en deux versions: "
            "(1) Darija marocaine (écrite en transcription phonétique + arabe dialectal) "
            "pour expliquer le plan aux parents et à l'étudiant. "
            "(2) Arabe classique (الفصحى) pour la section formelle et administrative. "
            "Adapter le vocabulaire au niveau culturel des parents. "
            "Expliquer les concepts compliqués avec des métaphores marocaines. "
            "Ajouter une section 'نصيحة للوالدين' (conseil aux parents) en arabe et darija."
        ),
        backstory=(
            "Tu es Aicha Bennani, linguiste spécialisée en darija marocaine et professeure "
            "à l'Institut Royal de la Culture Amazighe (IRCAM). Tu as travaillé avec le "
            "Ministère de l'Éducation pour arabiser et 'darijiser' les supports pédagogiques "
            "des zones rurales du Maroc (Haut Atlas, Rif, Souss). "
            "Tu maîtrises : la darija casablancaise, fassie, marrakchia et rifaine. "
            "Tu comprends que dans une famille marocaine traditionnelle, c'est souvent "
            "le père qui prend la décision finale d'orientation — et il faut lui parler "
            "avec respect et avec les bonnes références culturelles. "
            "Tu utilises des expressions comme 'ouldi mzyan f les maths' (mon fils est fort "
            "en maths), 'ghir diro l'école li khassou' (il faut juste faire l'école qu'il "
            "lui faut), 'had l-filière ghadi tjib lih l-khdma' (cette filière va lui trouver "
            "du travail). Tu t'assures que CHAQUE parent marocain, quel que soit son niveau "
            "d'éducation, comprend le plan d'avenir de son enfant. "
            "C'est ta mission la plus importante : l'inclusion par la langue."
        ),
        tools=[],  # Le localiseur travaille sur le texte produit par les autres agents
        llm=get_creative_llm(),
        verbose=True,
        allow_delegation=True,  # Peut demander des clarifications aux autres agents
        memory=True,
        max_iter=3,
        max_rpm=10
    )


# ─────────────────────────────────────────────
# FACTORY — Création de tous les agents
# ─────────────────────────────────────────────

def create_all_agents() -> dict:
    """
    # ARCHITECTURE COMPLEXE : Crée et retourne les 5 agents CrewAI.
    
    Initialise les outils une seule fois et les partage entre les agents.
    Active la mémoire partagée pour la cohérence entre les tâches.
    
    Returns:
        dict: {
            'profiler': Agent,
            'industry_aligner': Agent,
            'plan_b': Agent,
            'visualizer': Agent,
            'localizer': Agent
        }
    """
    logger.info("🤖 [AGENTS] Initialisation des 5 agents CareerBridge AI...")
    
    # Créer les outils partagés une seule fois
    tools = create_all_tools()
    
    agents = {
        "profiler": create_profiler_agent(tools),
        "industry_aligner": create_industry_aligner_agent(tools),
        "plan_b": create_plan_b_agent(tools),
        "visualizer": create_career_visualizer_agent(tools),
        "localizer": create_localizer_agent(tools)
    }
    
    logger.info("✅ [AGENTS] 5 agents créés avec succès :")
    for name, agent in agents.items():
        logger.info(f"   • {name}: {agent.role}")
    
    return agents


# ─────────────────────────────────────────────
# AGENT BACKSTORIES EXPORT (pour Streamlit)
# ─────────────────────────────────────────────

AGENT_METADATA = {
    "profiler": {
        "emoji": "🎓",
        "display_name": "Dr. Fatima Zahra — Profiler",
        "color": "#4A90D9",
        "specialty": "Analyse Massar & Psychologie"
    },
    "industry_aligner": {
        "emoji": "📊",
        "display_name": "Karim Benali — Analyste Marché",
        "color": "#E67E22",
        "specialty": "Marché du travail Maroc"
    },
    "plan_b": {
        "emoji": "🔄",
        "display_name": "Nadia Oulhaj — Plans Alternatifs",
        "color": "#27AE60",
        "specialty": "Parcours non-conventionnels"
    },
    "visualizer": {
        "emoji": "📈",
        "display_name": "Mehdi Tazi — Visualiseur",
        "color": "#8E44AD",
        "specialty": "Data Storytelling & Plotly"
    },
    "localizer": {
        "emoji": "🌍",
        "display_name": "Aicha Bennani — Darija Expert",
        "color": "#C0392B",
        "specialty": "Localisation Darija/Arabe"
    }
}


if __name__ == "__main__":
    print("=" * 60)
    print("TEST — agents_config.py")
    print("=" * 60)
    
    # Test création des agents (sans appel LLM)
    print("\n[INFO] Vérification de la configuration des agents...")
    for agent_key, meta in AGENT_METADATA.items():
        print(f"  {meta['emoji']} {meta['display_name']} ({meta['specialty']})")
    
    print("\n✅ agents_config.py configuré correctement.")
    print("⚠️  Pour tester les agents en live, définir OPENAI_API_KEY.")
