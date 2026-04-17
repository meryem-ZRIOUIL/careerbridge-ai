import json
from datetime import datetime

# Simuler import de ton orchestrator
from app.streamlit_app import AgentOrchestrator, LLMClient


def run_test_case(name, query, expected_keywords):
    print(f"\n🧪 TEST: {name}")
    
    llm = LLMClient()
    orchestrator = AgentOrchestrator(llm)
    
    result = orchestrator.process_query(
        query=query,
        profile={},
        history=[]
    )
    
    if "response" not in result:
        print("❌ FAIL: No response")
        return False
    
    response = result["response"].lower()
    
    success = any(keyword in response for keyword in expected_keywords)
    
    if success:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        print("Response:", response[:200])
    
    return success


def run_all_tests():
    tests = [
        {
            "name": "Tech profile",
            "query": "Je suis en terminale et j'aime l'informatique",
            "keywords": ["développeur", "data", "tech"]
        },
        {
            "name": "No math constraint",
            "query": "Je veux un métier sans maths",
            "keywords": ["marketing", "commerce"]
        },
        {
            "name": "Cybersecurity interest",
            "query": "Je veux faire cybersécurité",
            "keywords": ["cybersécurité", "sécurité"]
        }
    ]
    
    results = []
    
    for test in tests:
        res = run_test_case(test["name"], test["query"], test["keywords"])
        results.append(res)
    
    print("\n📊 RESULTATS:")
    print(f"{sum(results)}/{len(results)} tests réussis")
    
    if all(results):
        print("🎉 SYSTEME FONCTIONNEL")
    else:
        print("⚠️ PROBLEMES DETECTES")


if __name__ == "__main__":
    run_all_tests()