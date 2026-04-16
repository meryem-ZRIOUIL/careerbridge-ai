"""
CareerBridge AI — Interface Streamlit
Orientation scolaire intelligente pour les étudiants marocains.
"""

import streamlit as st
import json
import time
import os
from groq import Groq
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# CONFIGURATION PAGE
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="CareerBridge AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS — THEME GRIS ET BLEU (LIGHT)
# ─────────────────────────────────────────────

st.markdown("""
<style>
  /* Importation police */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  /* Variables couleurs */
  :root {
    --blue-primary: #1E4FBF;
    --blue-light: #3B6FE8;
    --blue-pale: #EBF0FC;
    --blue-border: #C5D3F5;
    --grey-dark: #1A1D23;
    --grey-medium: #4A5568;
    --grey-light: #718096;
    --grey-bg: #F7F8FA;
    --grey-card: #FFFFFF;
    --grey-border: #E2E8F0;
    --grey-hover: #F0F4F8;
    --text-primary: #1A202C;
    --text-secondary: #4A5568;
    --text-muted: #718096;
    --success: #276749;
    --success-bg: #F0FFF4;
    --warning: #744210;
    --warning-bg: #FFFBEB;
  }

  /* Reset général */
  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary);
    background-color: var(--grey-bg);
  }

  /* Main container */
  .main .block-container{
    padding: 2rem 2.5rem;
    max-width: 1200px;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid var(--grey-border);
    width: 300px !important;
  }
  section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1.25rem;
  }

  /* Header principal */
  .cb-header {
    background: linear-gradient(135deg, #1E4FBF 0%, #3B6FE8 100%);
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    color: white;
  }
  .cb-header h1 {
    color: white !important;
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
  }
  .cb-header p {
    color: rgba(255,255,255,0.82);
    font-size: 0.95rem;
    margin: 0;
  }

  /* Titres de section */
  .section-title {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin: 1.5rem 0 0.75rem 0;
  }

  /* Cards */
  .cb-card {
    background: #FFFFFF;
    border: 1px solid var(--grey-border);
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
  }
  .cb-card-blue {
    background: var(--blue-pale);
    border-color: var(--blue-border);
  }

  /* Steps sidebar */
  .step-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0.75rem;
    border-radius: 8px;
    margin-bottom: 0.4rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-secondary);
    cursor: default;
    transition: all 0.15s;
  }
  .step-item.active {
    background: var(--blue-pale);
    color: var(--blue-primary);
    border: 1px solid var(--blue-border);
  }
  .step-item.done {
    background: var(--grey-hover);
    color: var(--text-muted);
    text-decoration: none;
  }
  .step-num {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    font-size: 0.75rem;
    font-weight: 600;
    flex-shrink: 0;
    background: var(--grey-border);
    color: var(--text-muted);
  }
  .step-item.active .step-num {
    background: var(--blue-primary);
    color: white;
  }
  .step-item.done .step-num {
    background: #C6F6D5;
    color: #276749;
    font-size: 0.8rem;
  }

  /* User info form */
  .user-info-card {
    background: #FFFFFF;
    border: 1px solid var(--grey-border);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 1.5rem;
  }

  /* Inputs */
  .stSelectbox > div > div,
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {
    border: 1px solid var(--grey-border) !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    background: #FFFFFF !important;
    color: var(--text-primary) !important;
    box-shadow: none !important;
    transition: border-color 0.15s;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: var(--blue-light) !important;
    box-shadow: 0 0 0 3px rgba(59, 111, 232, 0.12) !important;
  }
  label {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
  }

  /* Boutons */
  .stButton > button {
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 1.25rem !important;
    transition: all 0.15s !important;
  }
  .stButton > button[kind="primary"] {
    background: var(--blue-primary) !important;
    border: none !important;
    color: white !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: var(--blue-light) !important;
    box-shadow: 0 4px 12px rgba(30, 79, 191, 0.3) !important;
  }
  .stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid var(--grey-border) !important;
    color: var(--text-secondary) !important;
  }

  /* Chat interface */
  .chat-container {
    background: #FFFFFF;
    border: 1px solid var(--grey-border);
    border-radius: 12px;
    height: 520px;
    overflow-y: auto;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    scroll-behavior: smooth;
  }

  /* Messages */
  .msg-row {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
    align-items: flex-start;
  }
  .msg-row.user {
    flex-direction: row-reverse;
  }
  .msg-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 600;
  }
  .msg-avatar.ai {
    background: var(--blue-primary);
    color: white;
  }
  .msg-avatar.user {
    background: var(--grey-border);
    color: var(--text-secondary);
  }
  .msg-bubble {
    max-width: 78%;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    font-size: 0.9rem;
    line-height: 1.6;
  }
  .msg-bubble.ai {
    background: var(--grey-bg);
    border: 1px solid var(--grey-border);
    color: var(--text-primary);
    border-top-left-radius: 2px;
  }
  .msg-bubble.user {
    background: var(--blue-primary);
    color: white;
    border-top-right-radius: 2px;
  }
  .msg-time {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
    padding: 0 0.25rem;
  }
  .msg-row.user .msg-time {
    text-align: right;
  }

  /* Recommendation cards */
  .reco-card {
    background: #FFFFFF;
    border: 1px solid var(--grey-border);
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.875rem;
    position: relative;
    transition: box-shadow 0.15s;
  }
  .reco-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.07);
  }
  .reco-rank {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: var(--blue-pale);
    color: var(--blue-primary);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    border: 1px solid var(--blue-border);
  }
  .reco-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.35rem;
  }
  .reco-sub {
    font-size: 0.83rem;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
  }
  .reco-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
  }
  .badge {
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.2rem 0.55rem;
    border-radius: 20px;
    border: 1px solid;
  }
  .badge-blue { background: var(--blue-pale); color: var(--blue-primary); border-color: var(--blue-border); }
  .badge-green { background: #F0FFF4; color: #276749; border-color: #9AE6B4; }
  .badge-orange { background: #FFFBEB; color: #744210; border-color: #F6E05E; }
  .badge-grey { background: var(--grey-hover); color: var(--text-secondary); border-color: var(--grey-border); }

  /* Progress bar */
  .stProgress > div > div > div > div {
    background: var(--blue-primary) !important;
  }

  /* Metrics */
  div[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid var(--grey-border);
    border-radius: 10px;
    padding: 1rem 1.25rem !important;
  }
  div[data-testid="metric-container"] > div > div:first-child {
    font-size: 0.8rem !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  div[data-testid="metric-container"] > div > div:nth-child(2) {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--blue-primary) !important;
  }

  /* Divider */
  hr {
    border: none;
    border-top: 1px solid var(--grey-border);
    margin: 1.5rem 0;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem;
    background: var(--grey-bg);
    border-radius: 8px;
    padding: 0.25rem;
    border: 1px solid var(--grey-border);
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1rem !important;
    color: var(--text-secondary) !important;
  }
  .stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: var(--blue-primary) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
  }

  /* Alerts */
  .cb-alert-info {
    background: var(--blue-pale);
    border: 1px solid var(--blue-border);
    border-left: 4px solid var(--blue-primary);
    border-radius: 8px;
    padding: 0.875rem 1.25rem;
    font-size: 0.875rem;
    color: var(--blue-primary);
    margin-bottom: 1rem;
  }
  .cb-alert-success {
    background: #F0FFF4;
    border: 1px solid #9AE6B4;
    border-left: 4px solid #276749;
    border-radius: 8px;
    padding: 0.875rem 1.25rem;
    font-size: 0.875rem;
    color: #276749;
    margin-bottom: 1rem;
  }

  /* Typing indicator */
  .typing-dots span {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-muted);
    margin: 0 2px;
    animation: bounce 1.2s infinite;
  }
  .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
  .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-6px); }
  }

  /* Sidebar logo */
  .cb-logo {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--grey-border);
  }
  .cb-logo-icon {
    width: 36px;
    height: 36px;
    background: var(--blue-primary);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.1rem;
  }
  .cb-logo-text {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
  }
  .cb-logo-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    font-weight: 400;
  }

  /* User profile display */
  .profile-display {
    background: var(--grey-bg);
    border: 1px solid var(--grey-border);
    border-radius: 8px;
    padding: 0.875rem 1rem;
    font-size: 0.85rem;
    margin-bottom: 1rem;
  }
  .profile-display .field {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem 0;
    color: var(--text-secondary);
  }
  .profile-display .field span:last-child {
    font-weight: 500;
    color: var(--text-primary);
  }

  /* Input area */
  .chat-input-area {
    display: flex;
    gap: 0.5rem;
    align-items: flex-end;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--grey-border); border-radius: 3px; }

  /* Hide Streamlit defaults */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DONNÉES MARCHÉ (from market_ma.json + enrichi)
# ─────────────────────────────────────────────

MARKET_DATA = [
    {"secteur": "Automobile", "metier": "Ingenieur Qualite", "ville": "Tanger / Kenitra",
     "salaire": "9 000 – 12 000 MAD", "demande": "Tres Haute",
     "entreprises": ["Renault-Nissan", "PSA Kenitra", "Yazaki"],
     "formations": ["ENSA Tanger", "FST", "OFPPT BTS"]},
    {"secteur": "IT", "metier": "Developpeur Fullstack", "ville": "Casablanca / Rabat",
     "salaire": "10 000 – 14 000 MAD", "demande": "Critique",
     "entreprises": ["Capgemini", "IBM Maroc", "HPS"],
     "formations": ["ENSIAS", "INPT", "UM6P"]},
    {"secteur": "Aeronautique", "metier": "Technicien Composite", "ville": "Casablanca / Nouaceur",
     "salaire": "8 000 – 13 000 MAD", "demande": "Haute",
     "entreprises": ["Boeing Maroc", "Safran", "Hexcel"],
     "formations": ["UIR", "ENSA Casa", "IMA"]},
    {"secteur": "Energies Renouvelables", "metier": "Ingenieur Solaire", "ville": "Ouarzazate / Tarfaya",
     "salaire": "11 000 – 16 000 MAD", "demande": "Haute",
     "entreprises": ["MASEN", "ONEE", "Nareva"],
     "formations": ["ENSA", "FST", "UM6P"]},
    {"secteur": "Finance", "metier": "Analyste Financier", "ville": "Casablanca",
     "salaire": "9 000 – 15 000 MAD", "demande": "Moyenne",
     "entreprises": ["Attijariwafa Bank", "CIH", "BMCE"],
     "formations": ["ISCAE", "HEM", "ENCG"]},
]

NIVEAUX = [
    "Bac (Terminale)", "Bac+1", "Bac+2 (BTS/DUT)", "Bac+3 (Licence)",
    "Bac+4", "Bac+5 (Master/Ingenieur)", "Doctorat"
]
FILIERES = [
    "Sciences Mathematiques A", "Sciences Mathematiques B",
    "Sciences Physiques", "Sciences de la Vie et de la Terre",
    "Sciences Economiques", "Lettres et Sciences Humaines",
    "Sciences Agricoles", "BTS Informatique", "BTS Electromecanique",
    "Licence Informatique", "Licence Sciences", "Licence Economie",
    "Master/Ingenieur", "Autre"
]


# ─────────────────────────────────────────────
# INIT SESSION STATE
# ─────────────────────────────────────────────

def init_state():
    defaults = {
        "step": "profile",        # profile | chat | reco
        "user_info": {},
        "messages": [],           # chat history
        "reco_generated": False,
        "client": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# SYSTEM PROMPT RAG
# ─────────────────────────────────────────────

def build_system_prompt(user_info: dict) -> str:
    info_str = ""
    if user_info:
        info_str = f"""
Profil de l'etudiant :
- Nom : {user_info.get('nom', 'Non renseigne')}
- Niveau : {user_info.get('niveau', 'Non renseigne')}
- Filiere : {user_info.get('filiere', 'Non renseigne')}
- Ville : {user_info.get('ville', 'Non renseigne')}
- Passions : {user_info.get('passions', 'Non renseigne')}
- Ambition : {user_info.get('ambition', 'Non renseigne')}
"""

    return f"""Tu es CareerBridge AI, un conseiller d'orientation expert dedie aux etudiants marocains.
Tu connais parfaitement le systeme educatif marocain : Massar, Baccalaureat, CPGE, BTS OFPPT, Universites publiques (ENSIAS, INPT, EMI, EHTP, ENSA, ENCG), Grandes Ecoles privees (UM6P, UIR, ISCAE), et le marche du travail marocain.

{info_str}

Contexte marche du travail marocain (donnees actuelles) :
- IT & Digital : 35 000 postes disponibles, croissance +20%/an, salaire moyen 18 000 MAD/mois
- Automobile : 45 000 postes, Tanger/Kenitra, salaire 8 500 MAD/mois
- Aeronautique : 12 000 postes, salaire moyen 22 000 MAD/mois
- Energies Renouvelables : 6 500 postes, croissance +15%/an
- Grille salariale : Bac+2 = 3 500-9 000 MAD | Bac+5 = 8 000-30 000 MAD | Grande Ecole = 12 000-50 000 MAD

Ecoles recommandees par profil :
- Profil scientifique/math fort : CPGE → ENSIAS, INPT, UM6P, EMI, EHTP
- Profil sciences appliquees : ENSA (14 poles), FST, FP
- Profil business/finance : ISCAE, ENCG, HEM
- Profil tech accessible : BTS OFPPT (gratuit), puis Licence Pro
- Profil international : UIR (aeronautique), UM6P (recherche)

Instructions de comportement :
1. Reponds en francais, de facon claire, structuree et bienveillante.
2. Utilise les donnees du profil etudiant pour personnaliser chaque reponse.
3. Cite toujours des chiffres concrets en MAD (salaires, frais de scolarite).
4. Propose des alternatives realistes si le plan principal est tres selectif.
5. Sois honnete sur les taux d'admission (ENSIAS ~3%, CPGE taux d'abandon 30%).
6. Encourage sans induire en erreur. Un BTS bien execute vaut mieux qu'une CPGE abandonnee.
7. Structure tes reponses avec des paragraphes clairs. Utilise des listes quand utile.
8. Si on te demande des informations non liees a l'orientation, recentre poliment la conversation.
"""


# ─────────────────────────────────────────────
# FONCTIONS RAG CHAT
# ─────────────────────────────────────────────

def stream_response(user_message: str):
    """Streaming avec Groq"""
    
    # Chargement explicite du .env
    from dotenv import load_dotenv
    load_dotenv(override=True)   # Force le rechargement
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key or api_key == "":
        yield "Erreur : GROQ_API_KEY non trouvée. Vérifie que le fichier .env est au bon endroit et bien nommé."
        return

    client = Groq(api_key=api_key)
    
    system_prompt = build_system_prompt(st.session_state.user_info)

    messages = [
        {"role": "system", "content": system_prompt}
    ]
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_message})

    try:
        full_response = ""
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1200,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_response += token
                yield token

    except Exception as e:
        yield f"Erreur Groq : {str(e)}"

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="cb-logo">
      <div class="cb-logo-icon">CB</div>
      <div>
        <div class="cb-logo-text">CareerBridge AI</div>
        <div class="cb-logo-sub">Orientation intelligente</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Navigation</div>', unsafe_allow_html=True)

    # Steps navigation
    steps = [
        ("profile", "Mon profil"),
        ("chat", "Conseiller IA"),
        ("reco", "Recommandations"),
    ]
    step_icons = {"profile": "1", "chat": "2", "reco": "3"}
    step_order = ["profile", "chat", "reco"]
    current_idx = step_order.index(st.session_state.step)

    for i, (step_id, step_label) in enumerate(steps):
        is_active = step_id == st.session_state.step
        is_done = i < current_idx
        cls = "active" if is_active else ("done" if is_done else "")
        num = "✓" if is_done else str(i + 1)
        st.markdown(f"""
        <div class="step-item {cls}">
          <div class="step-num">{num}</div>
          {step_label}
        </div>
        """, unsafe_allow_html=True)

    # Profil resume si rempli
    if st.session_state.user_info and st.session_state.step != "profile":
        st.markdown('<div class="section-title">Profil actuel</div>', unsafe_allow_html=True)
        ui = st.session_state.user_info
        st.markdown(f"""
        <div class="profile-display">
          <div class="field"><span>Nom</span><span>{ui.get('nom','—')}</span></div>
          <div class="field"><span>Niveau</span><span>{ui.get('niveau','—')}</span></div>
          <div class="field"><span>Filiere</span><span>{ui.get('filiere','—')[:20]}...</span></div>
          <div class="field"><span>Ville</span><span>{ui.get('ville','—')}</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Modifier le profil", key="edit_profile", use_container_width=True):
            st.session_state.step = "profile"
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-title">Donnees marche 2024</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.8rem; color: #4A5568; line-height:1.7;">
      IT / Digital : <b style="color:#1E4FBF;">35 000 postes</b><br>
      Automobile : <b style="color:#1E4FBF;">45 000 postes</b><br>
      Aeronautique : <b style="color:#1E4FBF;">12 000 postes</b><br>
      Croissance IT : <b style="color:#276749;">+20%/an</b>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE 1 — PROFIL UTILISATEUR
# ─────────────────────────────────────────────

if st.session_state.step == "profile":
    st.markdown("""
    <div class="cb-header">
      <h1>Bienvenue sur CareerBridge AI</h1>
      <p>Renseignez votre profil pour recevoir une orientation personnalisee au marche marocain</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="cb-alert-info">
      Remplissez ce formulaire une seule fois. Vos informations guideront toutes les recommandations du conseiller IA.
    </div>
    """, unsafe_allow_html=True)

    with st.form("profile_form", clear_on_submit=False):
        st.markdown('<div class="section-title">Informations personnelles</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet", placeholder="Ex : Youssef El Mansouri",
                                value=st.session_state.user_info.get("nom", ""))
        with col2:
            ville = st.text_input("Ville de residence", placeholder="Ex : Casablanca",
                                  value=st.session_state.user_info.get("ville", ""))

        st.markdown('<div class="section-title">Parcours scolaire</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            niveau = st.selectbox("Niveau d'etudes actuel", NIVEAUX,
                                  index=NIVEAUX.index(st.session_state.user_info.get("niveau", NIVEAUX[0]))
                                  if st.session_state.user_info.get("niveau") in NIVEAUX else 0)
        with col4:
            filiere = st.selectbox("Filiere / Specialite", FILIERES,
                                   index=FILIERES.index(st.session_state.user_info.get("filiere", FILIERES[0]))
                                   if st.session_state.user_info.get("filiere") in FILIERES else 0)

        st.markdown('<div class="section-title">Vos interets et ambitions</div>', unsafe_allow_html=True)
        passions = st.text_area(
            "Domaines qui vous passionnent",
            placeholder="Ex : informatique, mathematiques, conception, business, sciences...",
            value=st.session_state.user_info.get("passions", ""),
            height=90
        )
        ambition = st.text_area(
            "Votre ambition professionnelle",
            placeholder="Ex : Devenir ingenieur en intelligence artificielle, travailler dans une grande entreprise...",
            value=st.session_state.user_info.get("ambition", ""),
            height=90
        )

        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn2:
            submitted = st.form_submit_button("Continuer", use_container_width=True, type="primary")

    if submitted:
        if not nom.strip():
            st.error("Veuillez renseigner votre nom.")
        else:
            st.session_state.user_info = {
                "nom": nom.strip(),
                "ville": ville.strip(),
                "niveau": niveau,
                "filiere": filiere,
                "passions": passions.strip(),
                "ambition": ambition.strip(),
            }
            # Message de bienvenue initial
            if not st.session_state.messages:
                welcome = (
                    f"Bonjour {nom.strip()} ! Je suis votre conseiller d'orientation CareerBridge AI.\n\n"
                    f"J'ai pris connaissance de votre profil : niveau **{niveau}**, filiere **{filiere}**, "
                    f"base a **{ville}**.\n\n"
                    f"Je suis la pour vous aider a explorer les filieres d'etudes adaptees a votre profil, "
                    f"les ecoles marocaines correspondantes, les salaires et debouches sur le marche du travail marocain. "
                    f"Posez-moi toutes vos questions !"
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": welcome,
                    "time": time.strftime("%H:%M")
                })
            st.session_state.step = "chat"
            st.rerun()


# ─────────────────────────────────────────────
# PAGE 2 — CHATBOT RAG
# ─────────────────────────────────────────────

elif st.session_state.step == "chat":
    st.markdown("""
    <div class="cb-header">
      <h1>Conseiller d'Orientation IA</h1>
      <p>Posez vos questions sur les filieres, ecoles et debouches professionnels au Maroc</p>
    </div>
    """, unsafe_allow_html=True)

    # Suggested questions
    st.markdown('<div class="section-title">Questions frequentes</div>', unsafe_allow_html=True)
    suggested_qs = [
        "Quelles ecoles correspondent a mon profil ?",
        "Quel salaire puis-je esperer apres mes etudes ?",
        "Quels secteurs recrutent le plus au Maroc ?",
        "Comment integrer l'ENSIAS ou l'INPT ?",
        "Quelles sont les meilleures filieres IT ?",
        "Que faire si je rate le concours des grandes ecoles ?",
    ]
    cols = st.columns(3)
    for i, q in enumerate(suggested_qs):
        with cols[i % 3]:
            if st.button(q, key=f"sq_{i}", use_container_width=True):
                st.session_state["pending_message"] = q

    st.markdown("---")

    # Affichage des messages
    chat_html = '<div class="chat-container" id="chat-container">'
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"].replace("\n", "<br>")
        t = msg.get("time", "")
        if role == "assistant":
            chat_html += f"""
            <div class="msg-row">
              <div class="msg-avatar ai">IA</div>
              <div>
                <div class="msg-bubble ai">{content}</div>
                <div class="msg-time">{t}</div>
              </div>
            </div>"""
        else:
            initials = st.session_state.user_info.get("nom", "U")[:1].upper()
            chat_html += f"""
            <div class="msg-row user">
              <div class="msg-avatar user">{initials}</div>
              <div>
                <div class="msg-bubble user">{content}</div>
                <div class="msg-time">{t}</div>
              </div>
            </div>"""
    chat_html += '</div>'

    chat_placeholder = st.empty()
    chat_placeholder.markdown(chat_html, unsafe_allow_html=True)

    # Zone de saisie
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Votre question",
            placeholder="Tapez votre question sur l'orientation au Maroc...",
            key="chat_input",
            label_visibility="collapsed"
        )
    with col_send:
        send_clicked = st.button("Envoyer", type="primary", use_container_width=True)

    # Gestion du message
    pending = st.session_state.pop("pending_message", None)
    message_to_send = pending or (user_input.strip() if send_clicked else None)

    if message_to_send:
        st.session_state.messages.append({
            "role": "user",
            "content": message_to_send,
            "time": time.strftime("%H:%M")
        })

        # Streaming
        response_placeholder = st.empty()
        full_resp = ""
        for chunk in stream_response(message_to_send):
            full_resp += chunk
            preview = full_resp.replace("\n", "<br>")
            response_placeholder.markdown(f"""
            <div class="msg-row" style="margin-top:0.5rem;">
              <div class="msg-avatar ai">IA</div>
              <div>
                <div class="msg-bubble ai">{preview}<span style="opacity:0.5;"> ...</span></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        response_placeholder.empty()
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_resp,
            "time": time.strftime("%H:%M")
        })
        st.rerun()

    # Navigation
    st.markdown("---")
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("Effacer la conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col_nav2:
        if st.button("Voir les recommandations", type="primary", use_container_width=True):
            st.session_state.step = "reco"
            st.session_state.reco_generated = False
            st.rerun()


# ─────────────────────────────────────────────
# PAGE 3 — RECOMMANDATIONS
# ─────────────────────────────────────────────

elif st.session_state.step == "reco":
    st.markdown("""
    <div class="cb-header">
      <h1>Recommandations Personnalisees</h1>
      <p>Analyse du marche du travail marocain adaptee a votre profil</p>
    </div>
    """, unsafe_allow_html=True)

    ui = st.session_state.user_info
    niveau = ui.get("niveau", "")
    filiere = ui.get("filiere", "")
    passions_text = ui.get("passions", "").lower()
    ambition_text = ui.get("ambition", "").lower()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Secteurs analyzes", "6")
    with col2:
        st.metric("Postes disponibles", "105 000+")
    with col3:
        st.metric("Croissance moyenne", "+14%/an")
    with col4:
        st.metric("Salaire moyen (Bac+5)", "14 000 MAD")

    st.markdown("---")

    # Scoring simple pour classer les recommandations
    def score_sector(sector: dict) -> float:
        score = 0.0
        keywords = passions_text + " " + ambition_text
        for ent in sector.get("entreprises", []):
            if ent.lower() in keywords:
                score += 0.2
        sec = sector.get("secteur", "").lower()
        if any(w in keywords for w in ["informatique", "digital", "code", "python", "data", "ia"]):
            if "it" in sec:
                score += 0.5
        if any(w in keywords for w in ["auto", "voiture", "mecanique", "usine"]):
            if "auto" in sec:
                score += 0.5
        if any(w in keywords for w in ["energie", "solaire", "eolien", "vert"]):
            if "energie" in sec:
                score += 0.5
        if any(w in keywords for w in ["finance", "banque", "economie", "gestion"]):
            if "finance" in sec:
                score += 0.5
        if any(w in keywords for w in ["avion", "aeronautique", "boeing"]):
            if "aero" in sec:
                score += 0.5
        # bonus demande
        demande_map = {"Critique": 0.3, "Tres Haute": 0.25, "Haute": 0.15, "Moyenne": 0.05}
        score += demande_map.get(sector.get("demande", ""), 0)
        return score

    scored = sorted(MARKET_DATA, key=score_sector, reverse=True)

    tabs = st.tabs(["Secteurs recommandes", "Comparatif salaires", "Toutes les opportunites"])

    with tabs[0]:
        st.markdown('<div class="section-title">Meilleurs secteurs pour votre profil</div>', unsafe_allow_html=True)

        demande_badge = {
            "Critique": "badge-blue",
            "Tres Haute": "badge-orange",
            "Haute": "badge-green",
            "Moyenne": "badge-grey"
        }
        rank_labels = ["Recommande N°1", "Recommande N°2", "Recommande N°3"]

        for i, sector in enumerate(scored[:3]):
            badge_cls = demande_badge.get(sector["demande"], "badge-grey")
            formations_str = " ".join([f'<span class="badge badge-grey">{f}</span>' for f in sector["formations"]])
            entreprises_str = " ".join([f'<span class="badge badge-blue">{e}</span>' for e in sector["entreprises"]])

            st.markdown(f"""
            <div class="reco-card">
              <div class="reco-rank">{rank_labels[i]}</div>
              <div class="reco-title">{sector['secteur']} — {sector['metier']}</div>
              <div class="reco-sub">{sector['ville']} | {sector['salaire']}</div>
              <div class="reco-badges">
                <span class="badge {badge_cls}">Demande : {sector['demande']}</span>
                {entreprises_str}
              </div>
              <div style="margin-top:0.6rem; font-size:0.8rem; color:#718096; font-weight:500;">Formations adaptees :</div>
              <div class="reco-badges" style="margin-top:0.3rem;">{formations_str}</div>
            </div>
            """, unsafe_allow_html=True)

    with tabs[1]:
        st.markdown('<div class="section-title">Comparatif des salaires debutant</div>', unsafe_allow_html=True)

        salary_data = {
            "Bac+2 (BTS OFPPT)": 5500,
            "Bac+3 (Licence)": 7000,
            "Bac+5 (ENSA / FST)": 10000,
            "Bac+5 Grande Ecole (ENSIAS / INPT)": 14000,
            "Bac+5 UM6P": 18000,
            "Master specialise": 15000,
        }

        # Bar chart avec st.bar_chart
        import pandas as pd
        df = pd.DataFrame({
            "Salaire debutant (MAD/mois)": list(salary_data.values())
        }, index=list(salary_data.keys()))
        st.bar_chart(df, color="#1E4FBF", height=320)

        st.markdown("""
        <div class="cb-alert-info" style="margin-top:1rem;">
          Ces chiffres sont des moyennes constatees. Les salaires varient selon l'entreprise, la ville et les competences additionnelles.
        </div>
        """, unsafe_allow_html=True)

    with tabs[2]:
        st.markdown('<div class="section-title">Toutes les opportunites du marche marocain</div>', unsafe_allow_html=True)
        for sector in MARKET_DATA:
            badge_cls = demande_badge.get(sector["demande"], "badge-grey")
            col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 1])
            with col_a:
                st.markdown(f"**{sector['secteur']}** — {sector['metier']}")
            with col_b:
                st.markdown(f"<small style='color:#718096;'>{sector['ville']}</small>", unsafe_allow_html=True)
            with col_c:
                st.markdown(f"<small><b>{sector['salaire']}</b></small>", unsafe_allow_html=True)
            with col_d:
                st.markdown(f'<span class="badge {badge_cls}">{sector["demande"]}</span>', unsafe_allow_html=True)
            st.markdown("<hr style='margin:0.5rem 0;border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Plan d'action
    st.markdown("---")
    st.markdown('<div class="section-title">Plan d\'action recommande</div>', unsafe_allow_html=True)

    top_sector = scored[0] if scored else {}
    col_plan1, col_plan2 = st.columns(2)
    with col_plan1:
        st.markdown(f"""
        <div class="cb-card cb-card-blue">
          <div style="font-size:0.85rem; font-weight:600; color:#1E4FBF; margin-bottom:0.75rem;">Dans les 3 prochains mois</div>
          <ul style="font-size:0.875rem; color:#4A5568; margin:0; padding-left:1.25rem; line-height:2;">
            <li>Consolider les matieres scientifiques cles</li>
            <li>Preparer le dossier de candidature Massar Tawjihi</li>
            <li>Visiter les journees portes ouvertes des ecoles cibles</li>
            <li>Obtenir une premiere certification en ligne (gratuite)</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_plan2:
        st.markdown(f"""
        <div class="cb-card">
          <div style="font-size:0.85rem; font-weight:600; color:#1A202C; margin-bottom:0.75rem;">Ressources utiles</div>
          <ul style="font-size:0.875rem; color:#4A5568; margin:0; padding-left:1.25rem; line-height:2;">
            <li><b>Massar Tawjihi</b> — Inscription orientation nationale</li>
            <li><b>OFPPT</b> — Formations BTS gratuites</li>
            <li><b>ANAPEC</b> — Bourse et aide a l'emploi</li>
            <li><b>OCP Foundation</b> — Bourses excellentes</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col_back, col_chat = st.columns(2)
    with col_back:
        if st.button("Retour au conseiller IA", use_container_width=True):
            st.session_state.step = "chat"
            st.rerun()
    with col_chat:
        if st.button("Poser une question sur ces recommandations", type="primary", use_container_width=True):
            st.session_state.step = "chat"
            st.session_state["pending_message"] = f"Peux-tu m'expliquer plus en detail les opportunites dans le secteur {top_sector.get('secteur', '')} ?"
            st.rerun()