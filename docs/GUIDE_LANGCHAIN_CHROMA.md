# 🎯 Guide d'utilisation : LangChain-Chroma Integration

## Résumé de l'intégration

Votre projet `scientific-assistant` utilise maintenant **`langchain-chroma`** comme support d'intelligence combiné avec **ChromaDB**. Cette intégration vous offre le meilleur des deux mondes :

- ✅ **Performance de ChromaDB** : Base de données vectorielle rapide et efficace
- ✅ **Écosystème LangChain** : Compatibilité totale avec tous les outils LangChain
- ✅ **Compatibilité backward** : Votre code existant fonctionne sans modification

## 📚 Fichiers modifiés

### 1. `app/vectorstore/chroma.py`
**Avant** : Utilisait ChromaDB directement
**Après** : Utilise `langchain-chroma.Chroma` pour une intégration LangChain complète

**Nouvelles fonctionnalités** :
```python
# Méthode add_documents() pour les objets Document LangChain
store.add_documents([
    Document(page_content="...", metadata={...})
])

# Méthode as_retriever() pour les chaînes LangChain
retriever = store.as_retriever(search_kwargs={"k": 5})
```

### 2. `app/llm/embeddings.py`
**Avant** : Classe `EmbeddingService` standard
**Après** : Hérite de `langchain_core.embeddings.Embeddings`

**Nouvelles méthodes** :
```python
embeddings = get_embeddings()

# Interface LangChain (nouvelle)
query_emb = embeddings.embed_query("question")
doc_embs = embeddings.embed_documents(["doc1", "doc2"])

# Interface legacy (conservée)
emb = embeddings.embed_text("texte")
embs = embeddings.embed_texts(["texte1", "texte2"])
```

## 🚀 Exemples d'utilisation

### Exemple 1 : Utilisation basique

```python
from app.vectorstore.chroma import ChromaVectorStore

# Initialiser
store = ChromaVectorStore()

# Ajouter des textes
texts = ["Théorème de Pythagore", "Régression linéaire"]
metadatas = [{"source": "math"}, {"source": "stats"}]
store.add_texts(texts, metadatas)

# Rechercher
results = store.search("mathématiques", k=5)
```

### Exemple 2 : Avec LangChain Documents

```python
from langchain_core.documents import Document

docs = [
    Document(
        page_content="Contenu scientifique",
        metadata={"author": "Einstein", "year": 1905}
    )
]

store.add_documents(docs)
```

### Exemple 3 : Comme Retriever LangChain

```python
# Obtenir un retriever
retriever = store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}
)

# Utiliser dans une chaîne
docs = retriever.invoke("ma question")

# Ou dans une chaîne RAG complète
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
    llm=your_llm,
    retriever=retriever
)
```

### Exemple 4 : Accès direct à ChromaDB

```python
# Accéder à la collection ChromaDB sous-jacente
collection = store.collection

# Opérations avancées
all_docs = collection.get(include=["documents", "metadatas"])
```

## 📂 Fichiers de démonstration

### `examples/example_5_langchain_chroma.py`
Démontre les fonctionnalités de base :
- Ajout de textes simples
- Utilisation de Documents LangChain
- Interface Retriever
- Compatibilité des embeddings

**Lancer** :
```bash
uv run python examples/example_5_langchain_chroma.py
```

### `examples/example_6_scientific_rag.py`
Démontre une utilisation RAG complète :
- Création d'une base de connaissances scientifiques
- Requêtes avec contexte
- Recherche filtrée par métadonnées
- Accès direct à ChromaDB

**Lancer** :
```bash
uv run python examples/example_6_scientific_rag.py
```

### `tests/test_compatibility.py`
Vérifie la compatibilité backward :
- Tests des opérations de base
- Validation du retriever
- Vérification de la compatibilité

**Lancer** :
```bash
uv run python tests/test_compatibility.py
```

## 🔧 Configuration

Aucun changement nécessaire dans votre configuration. Les paramètres existants fonctionnent :

```python
# app/config.py
CHROMA_COLLECTION_NAME = "scientific_db"
CHROMA_PERSIST_DIR = Path("./chroma")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
```

## 📦 Dépendances installées

```toml
[project.dependencies]
chromadb = ">=0.4.0"           # Base de données vectorielle
langchain = ">=0.1.0"          # Framework LangChain
langchain-chroma = ">=1.1.0"   # Intégration officielle ⭐
langchain-community = ">=0.4.1" # Extensions
sentence-transformers = ">=2.2.0" # Embeddings
```

## 🎓 Avantages de cette intégration

### 1. **Interopérabilité totale**
Votre `ChromaVectorStore` est maintenant compatible avec :
- Tous les composants LangChain (chaînes, agents, etc.)
- Les retrievers LangChain
- Les Documents LangChain
- Les embeddings LangChain

### 2. **Fonctionnalités avancées**
- Recherche hybride (sémantique + mots-clés)
- Reranking automatique
- Scores de similarité calculés
- Filtrage par métadonnées

### 3. **Flexibilité**
- Accès direct à ChromaDB si nécessaire
- Interface LangChain pour l'intégration
- Compatibilité backward complète

### 4. **Performance**
- ChromaDB reste la base de données sous-jacente
- Embeddings optimisés avec sentence-transformers
- Recherche vectorielle rapide

## 🔍 Fonctionnalités clés

### Recherche avec reranking intelligent

```python
results = store.search("ma requête", k=5)

# Chaque résultat contient :
# - content: le texte du document
# - metadata: les métadonnées
# - distance: distance vectorielle
# - score: score de similarité (0-1)
# - keyword_match: booléen si mot-clé trouvé
```

### Persistance automatique

```python
# Mode persistant (production)
store = ChromaVectorStore(
    collection_name="my_data",
    persist_dir="./chroma_data"
)

# Mode éphémère (tests)
test_store = ChromaVectorStore(
    collection_name="test_data"
)  # "test" dans le nom active le mode éphémère
```

## 🧪 Tests et validation

Tous les tests passent avec succès :
- ✅ Compatibilité backward complète
- ✅ Nouvelles fonctionnalités opérationnelles
- ✅ Exemples fonctionnels
- ✅ Intégration LangChain validée

## 📖 Documentation

- **Guide complet** : [LANGCHAIN_CHROMA_INTEGRATION.md](LANGCHAIN_CHROMA_INTEGRATION.md)
- **Code source** : [app/vectorstore/chroma.py](app/vectorstore/chroma.py)
- **Embeddings** : [app/llm/embeddings.py](app/llm/embeddings.py)
- **Exemples** : [examples/](examples/)

## 💡 Prochaines étapes suggérées

1. **Intégrer dans vos agents**
   ```python
   from app.vectorstore.chroma import get_vector_store
   
   retriever = get_vector_store().as_retriever()
   # Utiliser dans vos agents LangGraph
   ```

2. **Créer des chaînes RAG**
   ```python
   from langchain.chains import RetrievalQA
   
   qa = RetrievalQA.from_chain_type(
       llm=your_llm,
       retriever=retriever
   )
   ```

3. **Améliorer le reranking**
   - Intégrer des modèles de reranking spécialisés
   - Ajouter des filtres de métadonnées avancés

4. **Optimiser les embeddings**
   - Tester d'autres modèles (BGE, E5, etc.)
   - Fine-tuner sur votre domaine scientifique

## ✅ Checklist de migration

- ✅ `langchain-chroma` installé
- ✅ `ChromaVectorStore` mis à jour
- ✅ `EmbeddingService` compatible LangChain
- ✅ Exemples créés et testés
- ✅ Tests de compatibilité validés
- ✅ Documentation complète

## 🎉 Résultat

Votre assistant scientifique bénéficie maintenant de :
- **Meilleure intégration** avec l'écosystème LangChain
- **Plus de flexibilité** pour construire des chaînes RAG
- **Compatibilité totale** avec votre code existant
- **Fonctionnalités avancées** prêtes à l'emploi

---

**Date de mise à jour** : 1er janvier 2026
**Status** : ✅ Intégration complète et opérationnelle
