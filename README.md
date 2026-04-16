# 🎓 CareerBridge AI
### Système Multi-Agents d'Orientation Scolaire Intelligent pour le Maroc

<div align="center">

![CareerBridge AI Banner](https://img.shields.io/badge/CareerBridge_AI-Multi_Agent_System-green?style=for-the-badge&logo=graduation-cap)

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.28+-red?style=flat-square)](https://github.com/joaomdmoura/crewAI)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-orange?style=flat-square)](https://langchain.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io)
[![GPT-4o](https://img.shields.io/badge/GPT--4o-Vision_Ready-412991?style=flat-square&logo=openai)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**نظام ذكي متعدد الوكلاء للتوجيه المدرسي في المملكة المغربية**

*Aligner les ambitions des étudiants marocains avec les besoins réels de l'industrie*

</div>

---

## 🎯 Problème & Vision

Le Maroc fait face à un **paradoxe de l'emploi critique** :
- **13% de chômage** chez les diplômés
- **45,000 postes vacants** dans l'automobile
- **35,000 postes IT** non-pourvus faute de compétences adaptées
- **12,000 postes** en aéronautique sans candidats qualifiés

> **CareerBridge AI** résout ce désalignement en guidant chaque étudiant marocain vers la filière qui correspond à ses forces réelles ET aux besoins du marché.

---

## 🏗️ Architecture Multi-Agents

```
┌─────────────────────────────────────────────────────────┐
│                    CAREERBRIDGE AI                       │
│              Système Multi-Agents CrewAI                 │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   [INPUT LAYER]   [AGENT LAYER]    [OUTPUT LAYER]
        │                 │                 │
   🎙️ Audio STT    ┌──────┴──────┐    📊 Plotly Charts
   📄 Vision PDF   │  5 AGENTS   │    📋 Rapport MD
   📝 Formulaire   │  CREWAI     │    🌍 Darija/Arabe
                   └──────┬──────┘    💾 JSON Data
                          │
            ┌─────────────┼────────────────┐
            │             │                │
      [Agent 1]     [Agent 2]        [Agent 3]
   🎓 Profiler   📊 Industry       🔄 Plan B
   Dr.Fatima     Aligner           Generator
   Zahra         Karim Benali      Nadia Oulhaj
            │             │                │
            └─────────────┼────────────────┘
                          │
                    ┌─────┴──────┐
                    │            │
              [Agent 4]    [Agent 5]
           📈 Career       🌍 Darija
           Visualizer      Localizer
           Mehdi Tazi      Aicha Bennani
```

---

## 🤖 Les 5 Agents IA

| Agent | Persona | Rôle | Outils |
|-------|---------|------|--------|
| 🎓 **Profiler** | Dr. Fatima Zahra El Idrissi | Analyse académique & psychologique | Vision PDF, Massar |
| 📊 **Industry Aligner** | Karim Benali (ex-McKinsey) | Alignment passion/marché marocain | Industry API, PDF RAG |
| 🔄 **Plan B Generator** | Nadia Oulhaj (OFPPT → ENSIAS) | Parcours alternatifs viables | PDF RAG, Market |
| 📈 **Career Visualizer** | Mehdi Tazi (OCP Digital) | Données Plotly & KPIs | PDF RAG |
| 🌍 **Darija Localizer** | Aicha Bennani (IRCAM) | Traduction Darija/Arabe/FR | LLM direct |

---

## 🛠️ Stack Technologique

```
┌─────────────────────────────────────────────────────────┐
│  LAYER         │  TECHNOLOGIE          │  USAGE         │
├────────────────┼───────────────────────┼────────────────┤
│ Orchestration  │ CrewAI 0.28+          │ Multi-agents   │
│ LLM Backbone   │ GPT-4o (OpenAI)       │ Raisonnement   │
│ RAG Engine     │ LangChain + ChromaDB  │ PDF filières   │
│ Vision IA      │ GPT-4o Vision         │ Bulletins      │
│ Speech-to-Text │ Whisper (local/API)   │ Voix étudiant  │
│ Structured Out │ Pydantic v2           │ JSON agents    │
│ Visualization  │ Plotly               │ Graphes MAD    │
│ Frontend       │ Streamlit 1.36+       │ UI/UX          │
│ Embeddings     │ OpenAI / HuggingFace  │ RAG search     │
│ Vector Store   │ ChromaDB              │ Persistence    │
└────────────────┴───────────────────────┴────────────────┘
```

---

## ✨ Fonctionnalités Clés

### 🎙️ Entrée Multimodale
- **Speech-to-Text** (Whisper) : L'étudiant décrit ses passions en voix
- **Vision IA** (GPT-4o) : Analyse automatique des bulletins Massar
- **Formulaire** : Saisie manuelle des notes et ambitions

### 🤖 Intelligence Multi-Agents
- **Délégation entre agents** (`allow_delegation=True`)
- **Mémoire partagée** (context passing séquentiel)
- **Raisonnement explicite** (Thought → Action → Observation)
- **RAG sur PDF** : Filières OFPPT, ENSA, CPGE, Universités

### 📊 Analyse Marché Marocain
- Données sectorielles : IT (+20%/an), Aéronautique, Automobile
- Salaires en Dirhams (MAD) — sources : ANAPEC, HCP
- ROI calculé en mois par filière
- Entreprises qui recrutent (Boeing, OCP, Renault, Safran...)

### 🌍 Localisation Darija/Arabe
- Rapport final en **3 langues** : Français / Arabe classique / Darija
- Section parents adaptée culturellement
- Expressions marocaines authentiques pour l'inclusion

### 📈 Visualisations Plotly
- **Graphe Sankey** : Parcours Terminale → Métier → Salaire
- **Timeline 20 ans** : Évolution salariale en MAD
- **Radar Chart** : Compétences actuelles vs. requises
- **Bar Chart** : Comparaison salaires par école

---

## 🚀 Installation & Démarrage

### Prérequis
- Python 3.10+
- OpenAI API Key (GPT-4o + Whisper API)
- Git

### Installation Rapide

```bash
# 1. Cloner le repository
git clone https://github.com/careerbridge-ai/maroc.git
cd careerbridge_ai

# 2. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec votre clé API OpenAI

# 5. Lancer l'application
streamlit run streamlit_app.py
```

### Configuration `.env`

```env
# Obligatoire
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx

# Optionnel — API Marché Marocain externe
MOROCCO_JOBS_API_URL=https://api.anapec.org/v1
MOROCCO_JOBS_API_KEY=your_anapec_key

# Optionnel — RAG PDF
PDF_FILIERES_DIR=./data/pdf_filières
CHROMA_PERSIST_DIR=./data/chroma_db
```

---

## 📁 Structure du Projet

```
careerbridge_ai/
│
├── 🎯 streamlit_app.py          # Interface principale Streamlit
├── 🤖 agents_config.py          # Configuration des 5 agents CrewAI
├── 📋 tasks_definition.py       # Définition des 5 tâches séquentielles
├── 🔧 tools_manager.py          # PDFSearchTool + IndustryMarketTool (RAG)
├── 🎙️ audio_vision_engine.py   # Speech-to-Text + Vision Bulletin
│
├── 📄 requirements.txt          # Dépendances Python
├── 📖 README.md                 # Documentation (ce fichier)
├── .env.example                 # Template variables d'environnement
│
├── data/
│   ├── pdf_filières/            # PDFs filières marocaines (OFPPT, ENSA...)
│   │   ├── guide_cpge_maroc.pdf
│   │   ├── ofppt_bts_catalogue.pdf
│   │   ├── ensa_programmes.pdf
│   │   └── ...
│   └── chroma_db/               # Index vectoriel ChromaDB (auto-généré)
│
└── tests/
    ├── test_agents.py
    ├── test_tools.py
    └── test_audio_vision.py
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest tests/ -v

# Test unitaire des modules
python audio_vision_engine.py
python tools_manager.py
python tasks_definition.py

# Test avec données demo (sans API)
DEMO_MODE=true streamlit run streamlit_app.py
```

---

## 🔬 Critères Techniques Détaillés

### 1. Architecture Complexe (CrewAI)
```python
crew = Crew(
    agents=[profiler, industry_aligner, plan_b, visualizer, localizer],
    tasks=[t1, t2, t3, t4, t5],
    process=Process.sequential,  # Séquentiel optimisé
    memory=True,                 # Mémoire partagée entre agents
    verbose=True                 # Logs de raisonnement
)
```
- ✅ **5 agents** avec `allow_delegation=True`
- ✅ **Processus séquentiel** avec context passing entre tâches
- ✅ **Mémoire partagée** pour cohérence inter-agents

### 2. Comportement Autonome (ReAct)
Chaque agent implémente le pattern **Thought → Action → Observation** :
```
# REASONING STEP :
Thought   : Analyser les forces cachées de l'étudiant au-delà des notes
Action    : Utiliser BulletinAnalyzerTool + PDFSearchTool
Observation: 19/20 en Informatique = profil ENSIAS confirmé
```

### 3. Tool-Use Avancé
| Outil | Technologie | Données |
|-------|-------------|---------|
| `PDFSearchTool` | LangChain RAG + ChromaDB | Filières, salaires, écoles |
| `IndustryMarketTool` | API JSON + fallback statique | Marché, emplois, secteurs |
| `BulletinAnalyzerTool` | GPT-4o Vision | Bulletins Massar |
| `speech_to_text()` | Whisper local/API | Audio étudiant |

### 4. IA Multimodale
- **Vision** : Analyse de bulletins scolaires (images JPG/PNG/PDF)
- **Audio** : Transcription des passions de l'étudiant (MP3/WAV/M4A)
- **Texte** : RAG sur PDFs des filières marocaines

### 5. Localisation Darija/Arabe
```python
# DARIJA LOCALIZATION
# Agent Aicha Bennani traduit et adapte culturellement le rapport
# Output : Section en Darija authentique pour les parents marocains
# "Ouldi/Benti 3endo/3endha l-mosta3dad d l-ingénieur"
```

---

## 📊 Exemples de Sorties

### Visualisation Sankey (Parcours Carrière)
```
Terminale SMA → CPGE MPSI → ENSIAS → Ingénieur IT → 75,000 MAD/an
      │                                     │
      └→ ENSA (Plan B) → Ingénieur → 48,000 MAD/an
      └→ OFPPT BTS → Certif. AWS → Dev → 36,000 MAD/an
```

### Rapport Darija (Extrait)
```
"Ouldi Youssef 3endo nta3 talya mzyan bzaf f l-maths w l-informatique.
L-filière li mnasbalia hia l-ENSIAS f Rabat — école publique, b la flous.
Ghadi ytkhraj b 14,000 drhem f l-shahr, men ba3d 5 snin: 28,000 drhem..."
```

### JSON Structuré (Pydantic)
```json
{
  "score_orientation": 87,
  "probabilite_plan_a": 35,
  "salaire_5ans_estime_mad": 28000,
  "verdict_text": "Profil EXCELLENT — Haute valeur marché 🚀",
  "top_secteurs": [
    {"secteur": "IT & Digital", "score_total": 9.2, "salaire_debut_mad": 14000}
  ]
}
```

---

## 🌍 Écoles Marocaines Référencées

| École | Ville | Secteur | Salaire Débutant |
|-------|-------|---------|-----------------|
| UM6P | Ben Guerir | Sciences/IA/Data | 18,000 MAD |
| ENSIAS | Rabat | Informatique/IA | 14,000 MAD |
| INPT | Rabat | Télécoms/Réseaux | 12,000 MAD |
| EMI | Rabat | Génie Multi | 11,500 MAD |
| EHTP | Casablanca | Travaux Publics | 11,000 MAD |
| ENSET | Rabat | Enseignement Tech | 8,000 MAD |
| ENSA (×14) | Multiple | Ingénierie | 10,000 MAD |
| UIR | Rabat | Aéro/IT/Mgt | 12,000 MAD |
| ISCAE | Casablanca | Business/Finance | 9,000 MAD |
| OFPPT BTS | Nationwide | Tech/Industrie | 5,000 MAD |

---

## 🤝 Contribution

```bash
# Fork → Feature Branch → Pull Request
git checkout -b feature/nouveau-secteur-energie
git commit -m "feat: Ajout secteur énergies renouvelables (données MASEN)"
git push origin feature/nouveau-secteur-energie
```

**Priorités de contribution :**
1. Ajout de PDFs officiels (catalogues OFPPT, guides ENSA)
2. Intégration API ANAPEC officielle
3. Amélioration de la qualité Darija (dialectes régionaux)
4. Tests d'intégration end-to-end

---

## 📄 Licence

MIT License — Libre d'utilisation pour l'éducation et l'orientation au Maroc.

---

## 👥 Équipe

Développé dans le cadre du **Hackathon IA Agentique Maroc 2024**
pour réduire l'écart école-emploi au Royaume du Maroc.

---

<div align="center">

**🇲🇦 للمغرب وأبنائه — Pour le Maroc et sa jeunesse 🇲🇦**

*CareerBridge AI — Construire les ponts entre les rêves et les carrières*

</div>
