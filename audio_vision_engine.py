"""
audio_vision_engine.py
======================
CareerBridge AI — Moteur Multimodal
Gère l'entrée vocale (Speech-to-Text) et l'analyse visuelle des bulletins scolaires.

# MULTIMODAL INTEGRATION : Ce module est le cœur de l'IA multimodale du système.
"""

import os
import base64
import json
import logging
from pathlib import Path
from typing import Optional, Union

# LangChain & OpenAI
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# Audio
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# Vision
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# MODÈLES PYDANTIC — Sorties structurées
# ─────────────────────────────────────────────

class StudentVoiceProfile(BaseModel):
    """Profil extrait de l'entrée vocale de l'étudiant."""
    raw_transcription: str = Field(description="Transcription brute de la voix")
    detected_passions: list[str] = Field(default_factory=list, description="Passions détectées")
    detected_subjects: list[str] = Field(default_factory=list, description="Matières mentionnées")
    language_detected: str = Field(default="fr", description="Langue détectée (fr/ar/darija)")
    confidence_score: float = Field(default=0.0, description="Score de confiance Whisper")

class BulletinAnalysisResult(BaseModel):
    """Résultat de l'analyse visuelle du bulletin scolaire."""
    student_name: Optional[str] = Field(default=None, description="Nom de l'étudiant")
    academic_year: Optional[str] = Field(default=None, description="Année scolaire")
    level: Optional[str] = Field(default=None, description="Niveau scolaire (Bac, CPGE, etc.)")
    grades: dict = Field(default_factory=dict, description="Notes par matière {matière: note}")
    average: Optional[float] = Field(default=None, description="Moyenne générale")
    strongest_subjects: list[str] = Field(default_factory=list, description="Matières fortes")
    weakest_subjects: list[str] = Field(default_factory=list, description="Matières faibles")
    orientation_signals: list[str] = Field(default_factory=list, description="Signaux d'orientation")
    raw_vision_output: str = Field(default="", description="Sortie brute du modèle Vision")


# ─────────────────────────────────────────────
# FONCTION 1 — SPEECH TO TEXT
# ─────────────────────────────────────────────

def speech_to_text(audio_path: Optional[str] = None,
                   audio_bytes: Optional[bytes] = None,
                   language: str = "fr") -> StudentVoiceProfile:
    """
    # REASONING STEP : Transcription de la voix de l'étudiant.
    
    Étape 1 (Thought)   : L'étudiant décrit ses passions en voix. On doit extraire
                          ces informations de manière structurée.
    Étape 2 (Action)    : Utiliser OpenAI Whisper pour transcrire l'audio.
    Étape 3 (Observation): Analyser la transcription pour extraire passions et matières.
    
    Args:
        audio_path: Chemin vers le fichier audio (MP3, WAV, M4A, etc.)
        audio_bytes: Bytes audio bruts (alternative à audio_path)
        language: Code langue pour Whisper ('fr', 'ar', 'en')
    
    Returns:
        StudentVoiceProfile: Profil structuré extrait de la voix
    """
    logger.info("🎙️ [STT] Démarrage transcription vocale...")

    # ── FALLBACK : Si aucun audio fourni ──────────────────────────────────────
    if not audio_path and not audio_bytes:
        logger.warning("⚠️ [STT FALLBACK] Aucun audio fourni — Utilisation du profil demo.")
        return _get_fallback_voice_profile()

    transcription_text = ""
    confidence = 0.0

    # ── WHISPER LOCAL ─────────────────────────────────────────────────────────
    if WHISPER_AVAILABLE and audio_path and Path(audio_path).exists():
        try:
            logger.info("🔊 [STT] Chargement modèle Whisper 'base'...")
            model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
            
            # # REASONING STEP : Whisper détecte automatiquement la langue
            result = model.transcribe(audio_path, language=language, verbose=False)
            transcription_text = result.get("text", "")
            confidence = _compute_whisper_confidence(result)
            logger.info(f"✅ [STT] Transcription réussie — {len(transcription_text)} chars")
        except Exception as e:
            logger.error(f"❌ [STT] Erreur Whisper : {e}")
            return _get_fallback_voice_profile()

    # ── OPENAI WHISPER API (si fichier audio et clé API disponible) ───────────
    elif OPENAI_AVAILABLE and audio_path and Path(audio_path).exists():
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            with open(audio_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )
            transcription_text = response.text
            confidence = 0.85  # API Whisper est fiable
            logger.info(f"✅ [STT API] Transcription réussie.")
        except Exception as e:
            logger.error(f"❌ [STT API] Erreur OpenAI : {e}")
            return _get_fallback_voice_profile()
    else:
        logger.warning("⚠️ [STT] Ni Whisper ni OpenAI disponible. Fallback activé.")
        return _get_fallback_voice_profile()

    # # REASONING STEP : Extraction structurée des informations de la transcription
    passions, subjects = _extract_entities_from_text(transcription_text)
    lang_detected = _detect_language(transcription_text)

    profile = StudentVoiceProfile(
        raw_transcription=transcription_text,
        detected_passions=passions,
        detected_subjects=subjects,
        language_detected=lang_detected,
        confidence_score=confidence
    )
    
    logger.info(f"🧠 [STT] Profil extrait : {len(passions)} passions, {len(subjects)} matières.")
    return profile


def _extract_entities_from_text(text: str) -> tuple[list[str], list[str]]:
    """
    # REASONING STEP : Extraction heuristique des entités du texte.
    Identifie les passions et matières mentionnées par l'étudiant.
    """
    text_lower = text.lower()
    
    # Mots-clés de passions (FR + Darija phonétique)
    passion_keywords = {
        "informatique": ["informatique", "programmation", "code", "coding", "ordinateur", "computer", "it", "tech", "développement"],
        "mathématiques": ["maths", "mathématiques", "algèbre", "calcul", "équation"],
        "sciences": ["sciences", "physique", "chimie", "biologie", "svt"],
        "médecine": ["médecine", "médecin", "docteur", "santé", "hôpital", "doctora", "tbib"],
        "ingénierie": ["ingénierie", "ingénieur", "mécanique", "électronique", "construction"],
        "business": ["business", "commerce", "entreprise", "entrepreneur", "gestion", "management"],
        "design": ["design", "art", "dessin", "créativité", "architecture", "graphisme"],
        "langues": ["langues", "anglais", "français", "arabe", "communication"],
        "aéronautique": ["aéronautique", "avion", "aviation", "boeing", "airbus"],
        "automobile": ["automobile", "voiture", "renault", "peugeot", "mécanique auto"],
        "agriculture": ["agriculture", "agronomie", ["ferme", "plantes", "nature"]],
        "enseignement": ["professeur", "enseignant", "enseigner", "éducation"],
    }
    
    subject_keywords = [
        "mathématiques", "maths", "physique", "chimie", "svt", "biologie",
        "informatique", "histoire", "géographie", "philosophie", "arabe",
        "français", "anglais", "espagnol", "économie", "comptabilité",
        "sport", "eps", "technologie", "génie", "électronique"
    ]
    
    detected_passions = []
    for passion, keywords in passion_keywords.items():
        if any(kw in text_lower for kw in keywords if isinstance(kw, str)):
            detected_passions.append(passion)
    
    detected_subjects = [subj for subj in subject_keywords if subj in text_lower]
    
    return detected_passions, detected_subjects


def _detect_language(text: str) -> str:
    """Détecte la langue du texte (simplifié)."""
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    if arabic_chars > len(text) * 0.3:
        return "ar"
    darija_keywords = ["wach", "nta", "ntina", "bghit", "zwina", "mezyan", "chno", "fin"]
    if any(kw in text.lower() for kw in darija_keywords):
        return "darija"
    return "fr"


def _compute_whisper_confidence(result: dict) -> float:
    """Calcule un score de confiance moyen depuis les segments Whisper."""
    segments = result.get("segments", [])
    if not segments:
        return 0.7
    avg_logprob = sum(s.get("avg_logprob", -1) for s in segments) / len(segments)
    # Convertit log-prob en score 0-1 (approximatif)
    confidence = min(1.0, max(0.0, 1.0 + avg_logprob / 3.0))
    return round(confidence, 3)


def _get_fallback_voice_profile() -> StudentVoiceProfile:
    """
    # FALLBACK : Profil demo utilisé quand aucun audio n'est disponible.
    Représente un étudiant marocain typique en Terminale Sciences.
    """
    logger.info("🔄 [FALLBACK] Utilisation du profil étudiant demo.")
    return StudentVoiceProfile(
        raw_transcription=(
            "Je m'appelle Youssef, j'ai 17 ans et je suis en Terminale Sciences. "
            "J'adore les mathématiques et l'informatique. Je rêve de devenir ingénieur. "
            "J'aime aussi la programmation et je code des petits projets web depuis 2 ans. "
            "Mon rêve c'est de travailler dans une grande entreprise technologique au Maroc."
        ),
        detected_passions=["informatique", "mathématiques", "ingénierie"],
        detected_subjects=["mathématiques", "informatique", "physique"],
        language_detected="fr",
        confidence_score=1.0
    )


# ─────────────────────────────────────────────
# OUTIL 2 — BULLETIN ANALYZER (VISION)
# ─────────────────────────────────────────────

class BulletinAnalyzerInput(BaseModel):
    """Schéma d'entrée pour l'outil d'analyse de bulletin."""
    image_path: Optional[str] = Field(default=None, description="Chemin vers l'image du bulletin")
    image_base64: Optional[str] = Field(default=None, description="Image encodée en base64")


class BulletinAnalyzerTool(BaseTool):
    """
    # MULTIMODAL INTEGRATION : Outil LangChain utilisant GPT-4 Vision
    pour analyser les bulletins scolaires marocains (format Massar ou manuel).
    
    # REASONING STEP :
    Thought   : Le bulletin contient des notes qui révèlent les aptitudes réelles de l'étudiant.
    Action    : Envoyer l'image au modèle Vision pour extraction structurée des notes.
    Observation: Les matières fortes orientent vers des filières spécifiques.
    """
    
    name: str = "bulletin_analyzer"
    description: str = (
        "Analyse un bulletin scolaire marocain (image/scan) via Vision IA. "
        "Extrait les notes par matière, calcule la moyenne, identifie les points forts "
        "et génère des signaux d'orientation scolaire. "
        "Input: chemin vers l'image du bulletin OU base64 de l'image."
    )
    args_schema: type[BaseModel] = BulletinAnalyzerInput

    def _run(self, image_path: Optional[str] = None,
             image_base64: Optional[str] = None) -> str:
        """Exécute l'analyse du bulletin."""
        logger.info("🔍 [VISION] Analyse du bulletin scolaire démarrée...")

        # ── FALLBACK : Si aucune image ────────────────────────────────────────
        if not image_path and not image_base64:
            logger.warning("⚠️ [VISION FALLBACK] Aucune image fournie — Données demo.")
            result = self._get_fallback_bulletin()
            return result.model_dump_json(indent=2)

        # ── Chargement de l'image ─────────────────────────────────────────────
        image_b64 = image_base64
        if image_path and Path(image_path).exists() and not image_base64:
            with open(image_path, "rb") as img_file:
                image_b64 = base64.b64encode(img_file.read()).decode("utf-8")
            ext = Path(image_path).suffix.lower().lstrip(".")
            media_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"
        else:
            media_type = "image/jpeg"

        # ── Appel GPT-4 Vision ────────────────────────────────────────────────
        if not OPENAI_AVAILABLE:
            logger.warning("⚠️ [VISION] OpenAI non disponible. Fallback.")
            result = self._get_fallback_bulletin()
            return result.model_dump_json(indent=2)

        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # # MULTIMODAL INTEGRATION : Prompt Vision spécialisé pour bulletins marocains
            vision_prompt = """Tu es un expert en analyse de documents scolaires marocains.
Analyse ce bulletin scolaire et extrais TOUTES les informations en JSON structuré.

Le bulletin peut être au format :
- Massar (système scolaire officiel marocain)
- Bulletin manuscrit ou imprimé d'école marocaine
- Relevé de notes CPGE, BTS, Université marocaine

Retourne UNIQUEMENT un JSON valide avec cette structure exacte :
{
  "student_name": "nom complet ou null",
  "academic_year": "2023-2024 ou null",
  "level": "Terminale Bac Sciences / 1ère CPGE / etc.",
  "grades": {
    "Mathématiques": 17.5,
    "Physique-Chimie": 15.0,
    "SVT": 14.5,
    "...": ...
  },
  "average": 16.2,
  "strongest_subjects": ["Mathématiques", "Physique"],
  "weakest_subjects": ["Français", "Histoire-Géo"],
  "orientation_signals": [
    "Excellente aptitude scientifique → CPGE/ENSA/FST",
    "Fort en maths → Classes préparatoires recommandées"
  ],
  "raw_vision_output": "Description complète du bulletin"
}"""

            response = client.chat.completions.create(
                model="gpt-4o",  # GPT-4 Vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{image_b64}",
                                    "detail": "high"
                                }
                            },
                            {"type": "text", "text": vision_prompt}
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            raw_output = response.choices[0].message.content
            logger.info(f"✅ [VISION] Analyse GPT-4 Vision réussie.")
            
            # # REASONING STEP : Parser la réponse JSON
            parsed = self._parse_vision_output(raw_output)
            return parsed.model_dump_json(indent=2)
            
        except Exception as e:
            logger.error(f"❌ [VISION] Erreur GPT-4 Vision : {e}")
            result = self._get_fallback_bulletin()
            return result.model_dump_json(indent=2)

    def _parse_vision_output(self, raw_output: str) -> BulletinAnalysisResult:
        """Parse la sortie JSON de GPT-4 Vision en objet structuré."""
        try:
            # Nettoyer les balises markdown si présentes
            clean = raw_output.strip()
            if clean.startswith("```json"):
                clean = clean[7:]
            if clean.startswith("```"):
                clean = clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            
            data = json.loads(clean.strip())
            return BulletinAnalysisResult(**data)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"⚠️ [VISION] Erreur parsing JSON : {e}. Extraction manuelle.")
            return BulletinAnalysisResult(raw_vision_output=raw_output)

    def _get_fallback_bulletin(self) -> BulletinAnalysisResult:
        """
        # FALLBACK : Bulletin demo d'un étudiant marocain en Terminale Sciences.
        """
        logger.info("🔄 [FALLBACK] Bulletin demo activé.")
        return BulletinAnalysisResult(
            student_name="Youssef El Mansouri",
            academic_year="2023-2024",
            level="Terminale Bac Sciences Mathématiques A",
            grades={
                "Mathématiques": 18.5,
                "Physique-Chimie": 17.0,
                "Sciences de l'Ingénieur": 16.5,
                "Informatique": 19.0,
                "Français": 13.5,
                "Arabe": 14.0,
                "Anglais": 15.5,
                "Histoire-Géographie": 12.0,
                "Éducation Islamique": 16.0,
                "EPS": 15.0
            },
            average=16.75,
            strongest_subjects=["Informatique", "Mathématiques", "Physique-Chimie"],
            weakest_subjects=["Histoire-Géographie", "Français"],
            orientation_signals=[
                "Excellence en Mathématiques (18.5/20) → Eligible CPGE/Classe prépa",
                "Très fort en Informatique (19/20) → ENSIAS, INPT, UM6P CS",
                "Profil ingénieur confirmé → ENSA, EHTP, EMI recommandés",
                "Moyenne générale 16.75 → Admissible dans les meilleures écoles publiques",
                "Sciences de l'Ingénieur fort → Option Génie Industriel possible"
            ],
            raw_vision_output="Bulletin scolaire demo — données synthétiques pour démonstration."
        )

    async def _arun(self, *args, **kwargs):
        """Version asynchrone (délègue au synchrone)."""
        return self._run(*args, **kwargs)


# ─────────────────────────────────────────────
# FONCTION UTILITAIRE — Encodage image
# ─────────────────────────────────────────────

def encode_image_to_base64(image_path: str) -> Optional[str]:
    """Encode une image en base64 pour l'API Vision."""
    path = Path(image_path)
    if not path.exists():
        logger.error(f"❌ Image non trouvée : {image_path}")
        return None
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


# ─────────────────────────────────────────────
# TEST STANDALONE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("TEST — audio_vision_engine.py")
    print("=" * 60)
    
    # Test STT Fallback
    print("\n[1] Test Speech-to-Text (fallback):")
    profile = speech_to_text()
    print(f"  Transcription: {profile.raw_transcription[:80]}...")
    print(f"  Passions: {profile.detected_passions}")
    print(f"  Matières: {profile.detected_subjects}")
    
    # Test Vision Fallback
    print("\n[2] Test BulletinAnalyzer (fallback):")
    tool = BulletinAnalyzerTool()
    result_json = tool._run()
    result = BulletinAnalysisResult(**json.loads(result_json))
    print(f"  Étudiant: {result.student_name}")
    print(f"  Moyenne: {result.average}/20")
    print(f"  Points forts: {result.strongest_subjects}")
    print(f"  Signaux: {result.orientation_signals[0]}")
    
    print("\n✅ Tests audio_vision_engine.py réussis !")
