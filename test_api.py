# test_api.py
import os
from dotenv import load_dotenv
from groq import Groq

# Charger le .env
load_dotenv()

# Récupérer la clé
api_key = os.getenv("GROQ_API_KEY")

print(f"🔑 Clé trouvée: {'OUI ✅' if api_key else 'NON ❌'}")
if api_key:
    print(f"   Début: {api_key[:10]}...")
    
    # Tester l'API
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Dis Bonjour en une phrase"}],
            max_tokens=50
        )
        print(f"\n✅ API fonctionne !")
        print(f"   Réponse: {response.choices[0].message.content}")
    except Exception as e:
        print(f"\n❌ Erreur API: {e}")
else:
    print("\n❌ Clé non trouvée dans .env")
    print("   Vérifie que le fichier .env contient:")
    print('   GROQ_API_KEY="gsk_votre_clé"')