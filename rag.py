import numpy as np
from typing import List, Dict
import json
import os

# =========================
# VECTOR DATABASE AVEC FAISS
# =========================
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class VectorDatabase:
    """Vector store avec FAISS + fallback simple"""

    def __init__(self, data_path: str = "data/market_ma.json"):
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.initialized = False
        
        # Charger les données
        self._load_data(data_path)

        if FAISS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(
                    "paraphrase-multilingual-MiniLM-L12-v2"
                )
                self.dimension = 384
                self.index = faiss.IndexFlatL2(self.dimension)
                self.initialized = True
                print("✅ FAISS activé")
                
                # Ajouter les documents chargés
                if self.documents:
                    self.add_documents(self.documents)
                    
            except Exception as e:
                print(f"⚠️ Erreur embeddings: {e}")
                self.initialized = False
        else:
            print("⚠️ FAISS non disponible → fallback activé")
    
    def _load_data(self, data_path: str):
        """Charge les données depuis le fichier JSON"""
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
            print(f"✅ {len(self.documents)} documents chargés depuis {data_path}")
        else:
            print(f"⚠️ Fichier {data_path} non trouvé")

    def add_documents(self, docs: List[Dict]):
        """Ajoute des documents avec embeddings enrichis"""
        if not docs:
            return

        # 🔥 TEXTE ENRICHIE POUR L'EMBEDDING (avec salaires)
        if self.initialized:
            try:
                texts = []
                for d in docs:
                    text = f"""
{d['metier']} 
{d['secteur']} 
{' '.join(d.get('tags', []))} 
Salaire: {d.get('salaire_debutant', '')} 
Demande: {d.get('demande', '')}
{d.get('pourquoi', '')}
"""
                    texts.append(text)
                
                embeddings = self.embedding_model.encode(texts)
                self.index.add(np.array(embeddings).astype("float32"))
                print(f"✅ {len(docs)} documents ajoutés à FAISS")
                
            except Exception as e:
                print(f"⚠️ Erreur add_documents: {e}")
                self.initialized = False

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Recherche intelligente avec fallback"""
        
        # 🟢 MODE FAISS
        if self.initialized and self.documents:
            try:
                query_embedding = self.embedding_model.encode([query])
                distances, indices = self.index.search(
                    np.array(query_embedding).astype("float32"), k
                )
                
                return [
                    self.documents[i]
                    for i in indices[0]
                    if i < len(self.documents)
                ]
                
            except Exception as e:
                print(f"⚠️ Erreur FAISS search: {e}")

        # 🟡 FALLBACK SIMPLE (keyword)
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            text = f"{doc.get('metier', '')} {doc.get('secteur', '')} {' '.join(doc.get('tags', []))}".lower()
            
            if any(word in text for word in query_lower.split()):
                results.append(doc)
        
        return results[:k]
    
    def get_all_documents(self) -> List[Dict]:
        """Retourne tous les documents"""
        return self.documents