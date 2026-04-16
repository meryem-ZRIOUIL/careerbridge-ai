"""
tasks_definition.py
===================
CareerBridge AI — Définition des Tâches CrewAI
Tâches séquentielles avec expected_output structurés (JSON + Markdown).

# ARCHITECTURE COMPLEXE : Processus séquentiel optimisé avec context passing.
"""

import logging
from typing import Optional
from pydantic import BaseModel, Field

from crewai import Task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# MODÈLES PYDANTIC — Sorties structurées
# ─────────────────────────────────────────────

class StudentProfileOutput(BaseModel):
    """Sortie structurée de la tâche de profilage."""
    student_id: str = Field(description="Identifiant anonymisé")
    nom_prenom: Optional[str] = Field(default=None)
    niveau: str = Field(description="Niveau scolaire actuel")
    filiere_bac: str = Field(description="Filière Bac marocaine")
    moyenne_generale: float = Field(description="Moyenne sur 20")
    notes_detaillees: dict = Field(default_factory=dict)
    passions_declarees: list[str] = Field(default_factory=list)
    passions_implicites: list[str] = Field(default_factory=list)
    forces_academiques: list[str] = Field(default_factory=list)
    faiblesses_academiques: list[str] = Field(default_factory=list)
    profil_psychologique: str = Field(description="Analyse du profil (analytique/créatif/social)")
    biais_familiaux: list[str] = Field(default_factory=list, description="Pressions familiales détectées")
    score_global: float = Field(description="Score académique global 0-100")
    recommandation_initiale: str = Field(description="Recommandation préliminaire d'orientation")


class MarketAlignmentOutput(BaseModel):
    """Sortie structurée de l'analyse marché."""
    top_secteurs: list[dict] = Field(description="Top 3 secteurs compatibles avec le profil")
    score_alignment: dict = Field(description="Scores de compatibilité profil-marché")
    opportunites_court_terme: list[str] = Field(description="Opportunités dans 0-2 ans")
    opportunites_moyen_terme: list[str] = Field(description="Opportunités dans 2-5 ans")
    risques_identifies: list[str] = Field(description="Risques de chômage ou saturation")
    salaire_estime_debut_mad: int = Field(description="Salaire estimé à la sortie d'études (MAD)")
    salaire_estime_5ans_mad: int = Field(description="Salaire estimé après 5 ans (MAD)")
    roi_formation_mois: int = Field(description="ROI en mois pour récupérer le coût des études")


class CareerPlanOutput(BaseModel):
    """Plan d'orientation complet."""
    plan_principal: dict = Field(description="Plan A - Voie recommandée")
    plans_alternatifs: list[dict] = Field(description="Plans B, C, D alternatifs")
    etapes_immediates: list[str] = Field(description="Actions à faire dans les 3 prochains mois")
    ressources_maroc: list[dict] = Field(description="Ressources et écoles au Maroc")
    certifications_recommandees: list[str] = Field(description="Certifications internationales utiles")


class PlotlyVisualizationOutput(BaseModel):
    """Données structurées pour les visualisations Plotly."""
    sankey_data: dict = Field(description="Données pour graphe Sankey Plotly")
    timeline_data: list[dict] = Field(description="Timeline de carrière 20 ans")
    radar_data: dict = Field(description="Données pour radar chart compétences")
    salary_comparison: list[dict] = Field(description="Comparaison salaires par école")
    kpi_summary: dict = Field(description="KPIs principaux pour affichage dashboard")


# ─────────────────────────────────────────────
# TÂCHE 1 — PROFILAGE ÉTUDIANT
# ─────────────────────────────────────────────

def create_profiling_task(agent, student_data: dict) -> Task:
    """
    # REASONING STEP — Tâche de Profilage
    
    Mission : Comprendre l'étudiant à 360° avant toute recommandation.
    Contexte : Données brutes (audio + bulletin + formulaire).
    Output   : JSON structuré StudentProfileOutput.
    """
    
    student_summary = _format_student_data(student_data)
    
    return Task(
        description=f"""
# MISSION : Profilage Complet de l'Étudiant Marocain

## Données Disponibles :
{student_summary}

## Ta mission :

### ÉTAPE 1 (THOUGHT) — Analyse initiale :
Avant de produire une recommendation, prends du recul et réfléchis :
- Quelles sont les VRAIES forces de cet étudiant (pas juste les notes) ?
- Y a-t-il un écart entre ses passions déclarées et ses aptitudes révélées ?
- Quels biais familiaux (pression pour médecine/ingénierie) pourraient influencer ses choix ?
- Son niveau de Terminale (notes, filière) est-il cohérent avec ses ambitions ?

### ÉTAPE 2 (ACTION) — Analyse détaillée :
1. **Analyse bulletin** : Utilise l'outil BulletinAnalyzer si une image est disponible.
   Identifie les matières fortes (>15/20) et faibles (<12/20).
2. **Transcription vocale** : Analyse les passions déclarées à l'oral.
   Cherche les mots émotionnellement chargés, les répétitions, les exemples concrets.
3. **Cross-validation** : Les notes en Maths 18/20 mais passion déclarée pour "design" ?
   C'est une dualité créatif-analytique → orientation Design industriel, UX, Architecture.
4. **Recherche PDF** : Cherche dans la base documentaire les profils similaires et leurs
   trajectoires réelles au Maroc.

### ÉTAPE 3 (OBSERVATION) — Synthèse :
Identifie le type de profil parmi :
- 🔬 **Scientifique pur** : Maths/Physique ≥16 → CPGE/ENSA/ENSIAS
- 💻 **Techno-créatif** : Info+Maths ≥15 → ENSIAS/INPT/UM6P Digital
- 🏗️ **Ingénieur bâtisseur** : Sciences ingé ≥15 → EHTP/EMI/ENSA
- 💼 **Business stratège** : Éco/Compta ≥16 → ENCG/ISCAE/HEM
- 🎨 **Créatif appliqué** : Art+Tech → Écoles de design, Architecture
- 🌱 **Nature & Sciences** : Bio/SVT ≥16 → Médecine/Pharmacie/IAV/Agro
- 🌍 **Global & Langues** : Langues ≥17 → Commerce international/Relations intl.

## Output Requis (JSON strict) :
```json
{{
  "student_id": "anonymisé",
  "niveau": "Terminale Bac Sciences Maths A",
  "filiere_bac": "Sciences Mathématiques A",
  "moyenne_generale": 16.75,
  "notes_detaillees": {{"Maths": 18.5, "Physique": 17.0, "...": "..."}},
  "passions_declarees": ["informatique", "mathématiques"],
  "passions_implicites": ["résolution de problèmes complexes", "créer des outils"],
  "forces_academiques": ["Maths", "Informatique", "Physique"],
  "faiblesses_academiques": ["Français", "Histoire-Géo"],
  "profil_psychologique": "Analytique-Créatif / Autonome / Orienté solutions",
  "biais_familiaux": ["Pression pour médecine", "Preference Ingénierie EHTP"],
  "score_global": 84.5,
  "recommandation_initiale": "Profil ingénieur informatique de haut niveau. CPGE MPSI recommandé."
}}
```

**Important** : Sois honnête sur les lacunes. Un étudiant avec 12/20 en Maths ne peut
pas intégrer une CPGE scientifique sans travail intense. Dis-le clairement mais
avec bienveillance, en proposant une voie de rattrapage.
""",
        expected_output="""
Un JSON structuré complet du profil étudiant avec :
- Notes détaillées par matière
- Passions explicites ET implicites identifiées
- Profil psychologique (analytique/créatif/social/etc.)
- Score global sur 100
- Première recommandation d'orientation motivée
- Biais familiaux identifiés pour les neutraliser
Format : JSON valide, parsable par les agents suivants.
""",
        agent=agent,
        output_pydantic=StudentProfileOutput
    )


# ─────────────────────────────────────────────
# TÂCHE 2 — ALIGNMENT INDUSTRIEL
# ─────────────────────────────────────────────

def create_market_alignment_task(agent, context_tasks: list) -> Task:
    """
    # REASONING STEP — Tâche d'Alignment Marché
    
    Mission : Aligner le profil (Tâche 1) avec les réalités du marché marocain.
    Contexte : Résultats de la tâche de profilage.
    Output   : Rapport d'alignment passion/marché avec métriques MAD.
    """
    
    return Task(
        description="""
# MISSION : Alignment Ambition ↔ Réalité Marché Marocain

## Contexte :
Tu reçois le profil complet de l'étudiant de l'agent Profiler.
Ta mission est d'aligner ses aspirations avec les DONNÉES RÉELLES du marché marocain 2024.

### ÉTAPE 1 (THOUGHT) — Diagnostic de l'écart école-emploi :
Le Maroc fait face à un paradoxe : 13% de chômage officiel MAIS 45 000 postes
non-pourvus dans l'automobile, 12 000 dans l'aéronautique, 35 000 dans l'IT.
L'écart n'est pas un manque d'emplois, c'est un désalignement de compétences.
Pour cet étudiant spécifique, quel est le risque de tomber dans ce piège ?

### ÉTAPE 2 (ACTION) — Analyse sectorielle approfondie :
1. **Interroger l'outil IndustryMarket** avec le profil de l'étudiant :
   - Cherche les 3 secteurs les plus compatibles
   - Calcule le score de compatibilité (passions × compétences × marché)
   - Identifie les entreprises qui recrutent activement ces profils

2. **Analyse ROI par filière** (à inclure) :
   - Coût total des études (frais + opportunité)
   - Salaire débutant estimé
   - Break-even point en mois
   
3. **Recherche PDF** sur les débouchés des filières recommandées :
   - Taux d'insertion à 6 mois, 1 an, 3 ans
   - Salaires moyens en MAD selon les enquêtes ENSET/EMI/ENSIAS
   - Témoignages d'alumni marocains

4. **Analyse des risques** :
   - Saturation du marché ? (Ex: Droit civil = très saturé)
   - Risque géographique ? (Emplois concentrés à Casablanca/Rabat ?)
   - Risque technologique ? (Filière menacée par l'IA dans 10 ans ?)

### ÉTAPE 3 (OBSERVATION) — Scoring et recommandations :
Calcule pour chaque filière identifiée :
- Score Passion-Compétences : 0-10
- Score Marché-Emploi : 0-10
- Score Salaire-Ambitions : 0-10
- Score Impact-Social : 0-10
- SCORE TOTAL PONDÉRÉ : /10

## Output Requis :
```json
{{
  "top_secteurs": [
    {{
      "rang": 1,
      "secteur": "IT & Data Science",
      "ecoles_recommandees": ["ENSIAS", "INPT", "UM6P"],
      "score_total": 9.2,
      "detail_scores": {{"passion": 9, "marche": 10, "salaire": 8, "impact": 9}},
      "salaire_debut_mad": 14000,
      "salaire_5ans_mad": 28000,
      "entreprises_cibles": ["Capgemini", "OCP Digital", "HPS", "Startups"],
      "risques": ["Concurrence internationale remote", "Évolution rapide"],
      "opportunites_uniques": ["UM6P AI Lab", "Microsoft Africa Dev Hub Casablanca"]
    }}
  ],
  "salaire_estime_debut_mad": 14000,
  "salaire_estime_5ans_mad": 28000,
  "roi_formation_mois": 18,
  "risques_identifies": ["Saturation possible IT junior en 3 ans"],
  "verdict_alignment": "FORT ALIGNMENT — Ambition = Marché = Compétences ✅"
}}
```

Chaque chiffre DOIT être sourcé (ANAPEC, HCP, enquêtes insertion, Rekrute.com).
""",
        expected_output="""
Un rapport d'alignment structuré contenant :
- Top 3 secteurs avec scores pondérés passion/marché/salaire
- Salaires précis en MAD (débutant, 5 ans, 10 ans)
- ROI calculé en mois
- Risques et opportunités chiffrés
- Verdict final : FORT / MOYEN / FAIBLE alignment
Sources citées pour tous les chiffres.
""",
        agent=agent,
        context=context_tasks,
        output_pydantic=MarketAlignmentOutput
    )


# ─────────────────────────────────────────────
# TÂCHE 3 — GÉNÉRATION PLAN B
# ─────────────────────────────────────────────

def create_plan_b_task(agent, context_tasks: list) -> Task:
    """
    # REASONING STEP — Tâche Génération Plans Alternatifs
    
    Mission : Créer 3 parcours alternatifs solides si le plan A échoue.
    """
    
    return Task(
        description="""
# MISSION : Génération des Plans Alternatifs B, C, D

## Contexte :
Tu reçois : (1) le profil étudiant complet, (2) l'analyse d'alignment marché.
Ta mission : Créer 3 plans alternatifs AUSSI AMBITIEUX que le plan A, juste différents.

### ÉTAPE 1 (THOUGHT) — Philosophie des plans alternatifs :
Au Maroc, les concours des grandes écoles sont TRÈS sélectifs :
- ENSIAS : ~3% de taux d'admission au concours national
- UM6P : très sélectif, frais élevés (100K MAD+/an)
- CPGE : abandon de 30% en 1ère année

La plupart des étudiants brillants n'intègrent PAS leur première école de rêve.
Cela NE SIGNIFIE PAS qu'ils ont échoué. Il existe des chemins alternatifs
qui mènent au MÊME destination professionnelle.

### ÉTAPE 2 (ACTION) — Construction des 3 plans alternatifs :

**Plan B — La voie de la deuxième chance :**
- Filière alternative de même niveau (ex: ENSA si ENSIAS échoue)
- Classe prépa privée pour retenter l'année suivante
- Licences Pro à FST/FP avec passerelle Master

**Plan C — La voie rapide (BTS → Marché → Master) :**
- BTS OFPPT en 2 ans → Expérience pro 1-2 ans → Licence Pro → Master
- Intégrer Renault, Safran, ou une startup dès Bac+2 et se former en interne
- Certifications internationales : AWS Cloud Practitioner, Google IT Support, etc.
- Coût : GRATUIT (OFPPT) ou très réduit vs écoles privées

**Plan D — La voie internationale :**
- Classes prépa en France (CPGE Lycée Henri IV, Louis-le-Grand si Bac>17)
- Universités canadiennes (Québec, programmes francophones avec équivalences)
- Bourses OCP Foundation, OCP Innov (pour les profils STEM+)
- Bourses Excellence Maroc (Ministère enseignement supérieur)

### ÉTAPE 3 (OBSERVATION) — Critères de qualité des plans alternatifs :
Chaque plan DOIT :
✅ Mener à des débouchés équivalents au plan A (même type de poste, ±15% de salaire)
✅ Être réaliste compte tenu du niveau actuel de l'étudiant
✅ Avoir un coût accessible (ou des bourses disponibles)
✅ Avoir des exemples RÉELS d'alumni marocains qui ont réussi via cette voie
✅ Inclure les ÉTAPES CONCRÈTES des 6 prochains mois

## Output Requis :
```json
{{
  "plan_principal": {{
    "label": "Plan A — CPGE MPSI → ENSIAS/INPT",
    "description": "2 ans CPGE scientifique + concours national",
    "probabilite_succes": 0.35,
    "cout_total_mad": 40000,
    "duree_annees": 5,
    "salaire_cible_mad": 14000,
    "ecoles_cibles": ["ENSIAS", "INPT", "UM6P"],
    "etapes_6_mois": ["S'inscrire CPGE dès résultats Bac", "Préparer concours maths"],
    "alumni_exemple": "Mohamed Benali (ENSIAS 2020), CTO chez HPS Casablanca"
  }},
  "plans_alternatifs": [
    {{
      "label": "Plan B — ENSA/FST + Certification Cloud",
      "probabilite_succes": 0.70,
      "cout_total_mad": 20000,
      "avantages": ["Moins sélectif", "Bonne insertion locale"],
      "inconvenients": ["Réseau moins prestigieux"],
      "debouches_equivalents": true
    }},
    {{
      "label": "Plan C — BTS OFPPT Gratuit + Auto-formation",
      "probabilite_succes": 0.85,
      "cout_total_mad": 0,
      "certifications_plan": ["AWS", "Google IT", "Python for Data Science"],
      "debouches_equivalents": true
    }},
    {{
      "label": "Plan D — Bourse internationale (Canada/France)",
      "probabilite_succes": 0.25,
      "cout_total_mad": 0,
      "bourses_disponibles": ["Campus France", "OCP Foundation", "AMCI"]
    }}
  ],
  "etapes_immediates": [
    "Confirmer les résultats Bac avant fin juin",
    "S'inscrire sur Massar Tawjihi avant le 20 juillet",
    "Préparer dossier de candidature UM6P (deadline août)"
  ]
}}
```
""",
        expected_output="""
Un JSON complet avec :
- Plan A principal avec probabilité de succès réaliste
- 3 plans alternatifs B, C, D tous viables et chiffrés en MAD
- Étapes immédiates concrètes (actions dans les 6 prochains mois)
- Exemples d'alumni marocains réels pour chaque voie
- Ressources, bourses et liens disponibles
""",
        agent=agent,
        context=context_tasks,
        output_pydantic=CareerPlanOutput
    )


# ─────────────────────────────────────────────
# TÂCHE 4 — VISUALISATION PLOTLY
# ─────────────────────────────────────────────

def create_visualization_task(agent, context_tasks: list) -> Task:
    """
    # REASONING STEP — Tâche Visualisation Plotly
    
    Mission : Transformer toutes les données en JSON Plotly exploitable par Streamlit.
    """
    
    return Task(
        description="""
# MISSION : Génération des Données de Visualisation Plotly

## Contexte :
Tu reçois : le profil, l'analyse marché et les plans d'orientation.
Ta mission : Transformer TOUT cela en données JSON pour des visualisations Plotly.

### ÉTAPE 1 (THOUGHT) — Design de la visualisation :
L'objectif est que l'étudiant ET ses parents puissent comprendre visuellement :
1. Son parcours actuel → école → diplôme → métier → salaire
2. Comment ses notes se comparent aux profils admis dans les écoles cibles
3. L'évolution de son salaire sur 20 ans
4. Quelles compétences il doit renforcer

### ÉTAPE 2 (ACTION) — Génération des 4 types de visualisations :

**Visualisation 1 — Graphe Sankey (Parcours complet) :**
- Nodes : Niveau actuel → Filière → École → Diplôme → Métier → Salaire
- Liens colorés : vert=certain, orange=probable, rouge=difficile
- Montrer Plans A, B, C simultanément

**Visualisation 2 — Timeline 20 ans (évolution salaire) :**
- Axe X : Années (2024–2044)
- Axe Y : Salaire en MAD/mois
- 3 courbes : Plan A optimiste / Plan A réaliste / Plan B
- Points d'inflexion : diplôme, première promotion, Management

**Visualisation 3 — Radar Chart (Compétences) :**
- Axes : Maths, Sciences, Programmation, Langues, Leadership, Créativité
- Comparaison : Profil actuel vs. Profil requis école cible

**Visualisation 4 — Bar Chart comparatif (Salaires par école) :**
- Écoles : ENSIAS, INPT, UM6P, ENSA, EHTP, OFPPT BTS
- Barres : Salaire débutant vs. Salaire 5 ans

### ÉTAPE 3 (OBSERVATION) — KPIs pour le dashboard :
Calcule et formate les métriques clés :
- Score global d'orientation : X/100
- Probabilité de réussite Plan A : X%
- Salaire estimé à 5 ans : X MAD
- Économies vs chômage : X MAD sur la carrière

## Output Requis (JSON Plotly) :
```json
{{
  "sankey_data": {{
    "node_labels": ["Terminale", "CPGE MPSI", "ENSIAS", "Ingénieur IT", "75K MAD/an"],
    "node_colors": ["#4A90D9", "#27AE60", "#27AE60", "#E67E22", "#2ECC71"],
    "source": [0, 1, 2, 3],
    "target": [1, 2, 3, 4],
    "value": [100, 35, 35, 35],
    "link_colors": ["#4A90D9", "#27AE60", "#E67E22", "#2ECC71"]
  }},
  "timeline_data": [
    {{"annee": 2024, "salaire_optimiste": 0, "salaire_realiste": 0, "label": "Terminale"}},
    {{"annee": 2026, "salaire_optimiste": 0, "salaire_realiste": 0, "label": "CPGE"}},
    {{"annee": 2029, "salaire_optimiste": 14000, "salaire_realiste": 12000, "label": "Diplôme Ingénieur"}},
    {{"annee": 2034, "salaire_optimiste": 28000, "salaire_realiste": 22000, "label": "+5 ans exp."}},
    {{"annee": 2044, "salaire_optimiste": 55000, "salaire_realiste": 40000, "label": "+15 ans / Senior"}}
  ],
  "radar_data": {{
    "categories": ["Mathématiques", "Sciences", "Informatique", "Langues", "Leadership", "Créativité"],
    "actuel": [92, 85, 95, 68, 60, 70],
    "requis_ensias": [90, 80, 85, 70, 65, 55]
  }},
  "salary_comparison": [
    {{"ecole": "ENSIAS", "debut_mad": 14000, "5ans_mad": 28000, "taux_insertion": 95}},
    {{"ecole": "INPT", "debut_mad": 12000, "5ans_mad": 25000, "taux_insertion": 93}},
    {{"ecole": "UM6P", "debut_mad": 18000, "5ans_mad": 35000, "taux_insertion": 97}},
    {{"ecole": "ENSA", "debut_mad": 10000, "5ans_mad": 20000, "taux_insertion": 87}},
    {{"ecole": "EHTP", "debut_mad": 11000, "5ans_mad": 22000, "taux_insertion": 88}},
    {{"ecole": "OFPPT BTS", "debut_mad": 5000, "5ans_mad": 12000, "taux_insertion": 80}}
  ],
  "kpi_summary": {{
    "score_orientation": 87,
    "probabilite_plan_a": 35,
    "salaire_5ans_estime_mad": 28000,
    "gain_carriere_vs_chomage_mad": 4500000,
    "emoji_verdict": "🚀",
    "verdict_text": "Profil EXCELLENT — Haute valeur marché"
  }}
}}
```
Tous les chiffres doivent être cohérents avec les tâches précédentes.
""",
        expected_output="""
Un JSON Plotly complet et exploitable directement par Streamlit contenant :
- Données Sankey pour le parcours filière→métier
- Timeline 20 ans avec 3 scénarios salariaux en MAD
- Radar chart compétences actuelles vs. requises
- Bar chart comparatif salaires 6 écoles marocaines
- KPIs formatés pour le dashboard (scores, probabilités, gains)
Toutes valeurs en Dirhams Marocains (MAD).
""",
        agent=agent,
        context=context_tasks,
        output_pydantic=PlotlyVisualizationOutput
    )


# ─────────────────────────────────────────────
# TÂCHE 5 — RAPPORT FINAL + LOCALISATION DARIJA
# ─────────────────────────────────────────────

def create_final_report_task(agent, context_tasks: list) -> Task:
    """
    # DARIJA LOCALIZATION — Tâche Rapport Final + Traduction
    
    Mission : Produire le rapport final complet en FR + AR + Darija.
    C'est la pièce maîtresse du système.
    """
    
    return Task(
        description="""
# MISSION : Rapport Final d'Orientation + Localisation Darija/Arabe

## Contexte :
Tu reçois TOUS les résultats des tâches précédentes.
Ta mission : Produire le rapport d'orientation FINAL en 3 langues.

### ÉTAPE 1 (THOUGHT) — Structure du rapport final :
Ce rapport sera imprimé et remis à l'étudiant ET à ses parents.
Il doit être :
✅ Complet mais lisible (pas trop long)
✅ Personnalisé (nom de l'étudiant, ses notes réelles)
✅ Actionnable (étapes concrètes avec dates)
✅ En 3 langues : Français (pour l'étudiant), Arabe (formel), Darija (pour les parents)
✅ Avec des exemples d'alumni marocains inspirants

### ÉTAPE 2 (ACTION) — Production du rapport Markdown :

Structure du rapport :
1. **RÉSUMÉ EXÉCUTIF** (1 page, FR)
   - Profil en 3 mots
   - Meilleure filière recommandée
   - Salaire estimé à 5 ans en MAD
   - Score d'orientation /100

2. **ANALYSE ACADÉMIQUE DÉTAILLÉE** (FR)
   - Notes par matière, comparaison avec les admis
   - Forces et points d'amélioration
   - Profil psychologique

3. **PLAN D'ORIENTATION PRINCIPAL (PLAN A)** (FR)
   - Filière recommandée avec justification
   - Écoles cibles (publiques + privées)
   - Étapes détaillées année par année
   - Coût estimé en MAD
   - Salaire projeté

4. **PLANS ALTERNATIFS (B, C, D)** (FR)
   - 3 alternatives réalistes avec pros/cons

5. **ANALYSE DU MARCHÉ MAROCAIN** (FR)
   - Secteur recommandé et tendances
   - Entreprises qui recrutent
   - Salaires concurrentiels en MAD

6. **SECTION PARENTS — نصيحة للوالدين** (ARABE CLASSIQUE)
   عزيز الوالدين...
   [Conseil formel en arabe classique pour les parents]

7. **SECTION DARIJA — للوالدين بالدارجة** (DARIJA MAROCAINE)
   # DARIJA LOCALIZATION : Cette section est critique pour l'inclusion
   
   Chers parents (en darija phonétique + arabe dialectal) :
   "Wlidi/Benti [nom] 3endo/3endha nta3 talya mzyan f..."
   "L-filière li mnasbalia hia..."
   "Ghadi ytkhraj b wahda salary dial..."
   "Rah khassu/khassha d3assou f..."
   
   [TOUTE LA SECTION EN DARIJA — minimum 200 mots]
   [Expliquer le plan comme un parent marocain le ferait à son voisin]

8. **RESOURCES ET CONTACTS** (FR/AR)
   - Liens officiels : Massar Tawjihi, OFPPT, UM6P admissions
   - Numéros ANAPEC
   - Dates importantes (concours, inscriptions)

### ÉTAPE 3 (OBSERVATION) — Révision et qualité :
Avant de soumettre le rapport, vérifie :
✅ La section Darija est-elle authentique et naturelle ?
✅ Les chiffres MAD sont-ils cohérents avec l'analyse marché ?
✅ Les noms d'écoles sont-ils correctement écrits ?
✅ Le plan A est-il réaliste vu le niveau de l'étudiant ?
✅ Les étapes immédiates ont-elles des dates précises ?

## Output Requis : Markdown complet, minimum 1500 mots
Le rapport DOIT inclure :
- Section en arabe classique (الفصحى)
- Section en Darija (الدارجة المغربية) — OBLIGATOIRE
- Tous les chiffres en MAD
- Noms réels d'écoles marocaines (UM6P, EHTP, ENSIAS, ENSA, OFPPT, etc.)
- Exemples d'alumni marocains inspirants
""",
        expected_output="""
Un rapport Markdown complet et professionnel incluant :
1. Résumé exécutif en français
2. Analyse académique détaillée
3. Plan A principal + Plans B/C/D alternatifs
4. Analyse marché marocain avec chiffres MAD
5. Section parents en Arabe classique (الفصحى)
6. Section Darija marocaine authentique pour les parents (minimum 200 mots)
7. Ressources et contacts utiles au Maroc
Minimum 1500 mots, formaté Markdown, prêt à imprimer.
""",
        agent=agent,
        context=context_tasks
    )


# ─────────────────────────────────────────────
# FACTORY — Création de toutes les tâches
# ─────────────────────────────────────────────

def create_all_tasks(agents: dict, student_data: dict) -> list:
    """
    Crée toutes les tâches CrewAI dans l'ordre séquentiel.
    
    # ARCHITECTURE COMPLEXE : Processus séquentiel avec context passing.
    Chaque tâche reçoit en contexte les résultats des tâches précédentes.
    
    Args:
        agents: Dict des 5 agents créés par create_all_agents()
        student_data: Données brutes de l'étudiant
    
    Returns:
        list: Liste ordonnée des tâches CrewAI
    """
    logger.info("📋 [TASKS] Création des tâches CareerBridge AI...")
    
    # Tâche 1 : Profilage (indépendante)
    t1_profiling = create_profiling_task(
        agent=agents["profiler"],
        student_data=student_data
    )
    
    # Tâche 2 : Alignment marché (contexte : tâche 1)
    t2_market = create_market_alignment_task(
        agent=agents["industry_aligner"],
        context_tasks=[t1_profiling]
    )
    
    # Tâche 3 : Plans alternatifs (contexte : tâches 1 + 2)
    t3_plan_b = create_plan_b_task(
        agent=agents["plan_b"],
        context_tasks=[t1_profiling, t2_market]
    )
    
    # Tâche 4 : Visualisation (contexte : tâches 1 + 2 + 3)
    t4_visualization = create_visualization_task(
        agent=agents["visualizer"],
        context_tasks=[t1_profiling, t2_market, t3_plan_b]
    )
    
    # Tâche 5 : Rapport final + Darija (contexte : toutes les tâches)
    t5_final_report = create_final_report_task(
        agent=agents["localizer"],
        context_tasks=[t1_profiling, t2_market, t3_plan_b, t4_visualization]
    )
    
    tasks = [t1_profiling, t2_market, t3_plan_b, t4_visualization, t5_final_report]
    
    logger.info(f"✅ [TASKS] {len(tasks)} tâches créées dans l'ordre séquentiel.")
    for i, task in enumerate(tasks, 1):
        logger.info(f"   Tâche {i}: {task.agent.role[:40]}...")
    
    return tasks


# ─────────────────────────────────────────────
# HELPER — Format des données étudiant
# ─────────────────────────────────────────────

def _format_student_data(student_data: dict) -> str:
    """Formate les données étudiant pour injection dans les prompts."""
    lines = []
    
    if student_data.get("nom"):
        lines.append(f"- **Nom** : {student_data['nom']}")
    if student_data.get("niveau"):
        lines.append(f"- **Niveau** : {student_data['niveau']}")
    if student_data.get("filiere"):
        lines.append(f"- **Filière Bac** : {student_data['filiere']}")
    if student_data.get("ville"):
        lines.append(f"- **Ville** : {student_data['ville']}")
    
    if student_data.get("notes"):
        lines.append("\n**Notes par matière :**")
        for matiere, note in student_data["notes"].items():
            lines.append(f"  - {matiere}: {note}/20")
    
    if student_data.get("passions"):
        lines.append(f"\n**Passions déclarées** : {', '.join(student_data['passions'])}")
    
    if student_data.get("ambition"):
        lines.append(f"\n**Ambition professionnelle** : {student_data['ambition']}")
    
    if student_data.get("bulletin_analysis"):
        lines.append(f"\n**Analyse Bulletin (Vision IA)** :\n{student_data['bulletin_analysis']}")
    
    if student_data.get("voice_profile"):
        lines.append(f"\n**Profil Vocal (STT)** :\n{student_data['voice_profile']}")
    
    return "\n".join(lines) if lines else "Données étudiant non disponibles — Utiliser profil demo."


def get_demo_student_data() -> dict:
    """
    Retourne un profil étudiant demo pour les tests.
    # FALLBACK : Profil représentatif d'un lycéen marocain typique.
    """
    return {
        "nom": "Youssef El Mansouri",
        "niveau": "Terminale",
        "filiere": "Sciences Mathématiques A",
        "ville": "Casablanca",
        "notes": {
            "Mathématiques": 18.5,
            "Physique-Chimie": 17.0,
            "Sciences de l'Ingénieur": 16.5,
            "Informatique": 19.0,
            "Français": 13.5,
            "Arabe": 14.0,
            "Anglais": 15.5,
            "Histoire-Géographie": 12.0,
            "EPS": 15.0
        },
        "passions": ["informatique", "mathématiques", "intelligence artificielle"],
        "ambition": "Devenir ingénieur en IA ou Data Scientist dans une grande entreprise marocaine ou internationale",
        "contexte_familial": "Père employé ONCF, mère professeure primaire. Budget études limité. Préférence famille pour école publique gratuite."
    }


if __name__ == "__main__":
    print("=" * 60)
    print("TEST — tasks_definition.py")
    print("=" * 60)
    
    demo_data = get_demo_student_data()
    print(f"\n[1] Profil demo créé pour : {demo_data['nom']}")
    print(f"   Filière: {demo_data['filiere']}")
    print(f"   Moyenne estimée: {sum(demo_data['notes'].values())/len(demo_data['notes']):.2f}/20")
    print(f"   Matière forte: {max(demo_data['notes'], key=demo_data['notes'].get)} = {max(demo_data['notes'].values())}/20")
    
    formatted = _format_student_data(demo_data)
    print(f"\n[2] Données formatées ({len(formatted)} chars):")
    print(formatted[:300] + "...")
    
    print("\n✅ tasks_definition.py configuré correctement.")
