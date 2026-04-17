import os
from typing import Tuple

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class LLMClient:
    """Client LLM robuste avec fallback sécurisé"""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        self.model = "llama-3.3-70b-versatile"

        self.prompt_templates = {
            "default": "Tu es un expert en orientation professionnelle.",
            "creative": "Tu es un mentor bienveillant et inspirant.",
            "analytical": "Tu es un analyste précis et factuel."
        }

        self.current_template = "default"

        if GROQ_AVAILABLE and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                print("✅ LLM connecté")
            except Exception as e:
                print(f"⚠️ Erreur LLM init: {e}")
        else:
            print("⚠️ Mode fallback LLM activé")

    def generate(self, prompt: str, system_role: str = None, template: str = None) -> str:
        """Génère une réponse avec fallback sécurisé"""

        system_content = system_role or self.prompt_templates.get(
            template or self.current_template,
            self.prompt_templates["default"]
        )

        # 🟢 MODE API
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )

                return response.choices[0].message.content

            except Exception as e:
                print(f"⚠️ Erreur LLM: {e}")

        # 🟡 FALLBACK LOCAL
        return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Réponse de secours si API indisponible"""

        return (
            "⚠️ Mode dégradé activé.\n\n"
            "Je peux analyser ton profil, mais certaines réponses avancées sont limitées.\n\n"
            "➡️ Voici une suggestion basée sur ton profil :\n"
            "- Explore les métiers liés à tes intérêts\n"
            "- Évite les domaines incompatibles avec tes contraintes\n"
            "- Concentre-toi sur les compétences pratiques\n"
        )

    def ab_test(self, prompt: str) -> Tuple[str, str]:
        """Compare deux styles de réponse"""

        response_a = self.generate(prompt, template="default")
        response_b = self.generate(prompt, template="creative")

        return response_a, response_b