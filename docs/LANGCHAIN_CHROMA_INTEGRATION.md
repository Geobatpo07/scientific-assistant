# Intégration LangChain-Chroma avec ChromaDB

## 📋 Résumé

Vous utilisez maintenant **`langchain-chroma`** comme support d'intelligence combiné avec **ChromaDB**. Cette intégration vous donne accès à toutes les fonctionnalités de LangChain tout en bénéficiant de la performance de ChromaDB.

## ✅ Ce qui a été fait

### 1. Mise à jour de `app/vectorstore/chroma.py`
- ✅ Intégration de `langchain-chroma` avec la classe `Chroma`
- ✅ Support natif des `Document` LangChain
- ✅ Interface `as_retriever()` pour une utilisation directe dans les chaînes LangChain
- ✅ Méthodes améliorées : `add_texts()`, `add_documents()`, `search()`
- ✅ Compatibilité backward avec le code existant

### 2. Mise à jour de `app/llm/embeddings.py`
- ✅ `EmbeddingService` hérite maintenant de `langchain_core.embeddings.Embeddings`
- ✅ Implémentation de `embed_query()` et `embed_documents()` (requis par LangChain)
- ✅ Compatibilité backward : `embed_text()` et `embed_texts()` toujours disponibles
- ✅ Fonctionnel avec tous les composants LangChain

### 3. Exemple complet créé : `examples/example_5_langchain_chroma.py`
- ✅ Démonstration de l'ajout de textes simples
- ✅ Utilisation de `Document` LangChain
- ✅ Interface `Retriever` LangChain
- ✅ Vérification de la compatibilité des embeddings

## 🎯 Avantages de cette intégration

### 1. **Compatibilité LangChain complète**
```python
# Utilisation directe comme retriever dans les chaînes LangChain
from app.vectorstore.chroma import get_vector_store

store = get_vector_store()
retriever = store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# Utilisation dans une chaîne RAG
from langchain.chains import RetrievalQA
qa_chain = RetrievalQA.from_chain_type(
    llm=your_llm,
    retriever=retriever
)
```

### 2. **Support des Documents LangChain**
```python
from langchain_core.documents import Document

docs = [
    Document(
        page_content="Votre contenu ici",
        metadata={"source": "livre.pdf", "page": 42}
    )
]

store.add_documents(docs)
```

### 3. **Embeddings standardisés**
```python
from app.llm.embeddings import get_embeddings

embeddings = get_embeddings()

# Interface LangChain
query_emb = embeddings.embed_query("Ma question")
doc_embs = embeddings.embed_documents(["Doc 1", "Doc 2"])

# API legacy (toujours disponible)
emb = embeddings.embed_text("Texte")
embs = embeddings.embed_texts(["Texte 1", "Texte 2"])
```

## 📦 Dépendances

Les packages suivants sont déjà installés dans votre `pyproject.toml` :

```toml
dependencies = [
    "chromadb>=0.4.0",           # Base de données vectorielle
    "langchain>=0.1.0",          # Framework LangChain
    "langchain-chroma>=1.1.0",   # Intégration ChromaDB ✨
    "langchain-community>=0.4.1", # Extensions communautaires
    "sentence-transformers>=2.2.0", # Modèles d'embeddings
]
```

## 🚀 Utilisation

### Exemple basique

```python
from app.vectorstore.chroma import ChromaVectorStore

# Initialiser le store
store = ChromaVectorStore()

# Ajouter des textes
texts = [
    "Le théorème de Pythagore...",
    "La régression linéaire...",
]
metadatas = [
    {"source": "math", "topic": "geometry"},
    {"source": "stats", "topic": "regression"},
]

store.add_texts(texts, metadatas)

# Rechercher
results = store.search("théorème mathématique", k=5)

for result in results:
    print(f"Content: {result['content']}")
    print(f"Score: {result['score']}")
    print(f"Metadata: {result['metadata']}")
```

### Avec LangChain Documents

```python
from langchain_core.documents import Document

docs = [
    Document(
        page_content="Contenu scientifique ici",
        metadata={"author": "Einstein", "year": 1905}
    )
]

store.add_documents(docs)
```

### Utilisation comme Retriever

```python
# Obtenir un retriever LangChain
retriever = store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}
)

# Utiliser dans une chaîne
docs = retriever.invoke("Ma question")
```

## 🔧 Configuration

Votre configuration dans `app/config.py` reste inchangée :

```python
CHROMA_COLLECTION_NAME = "scientific_db"
CHROMA_PERSIST_DIR = Path("./chroma")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
```

## 🧪 Tests

Lancez l'exemple pour vérifier que tout fonctionne :

```bash
uv run python examples/example_5_langchain_chroma.py
```

Vous devriez voir :
- ✅ Tous les exemples s'exécutent avec succès
- ✅ Les recherches retournent des résultats pertinents
- ✅ Les embeddings fonctionnent correctement
- ✅ L'interface retriever fonctionne

## 📊 Fonctionnalités avancées

### Recherche hybride avec reranking

La méthode `search()` inclut automatiquement :
- ✅ Recherche sémantique (via embeddings)
- ✅ Boost par mots-clés
- ✅ Reranking intelligent
- ✅ Scores de similarité calculés

### Persistance

```python
# Mode persistant (par défaut)
store = ChromaVectorStore(
    collection_name="my_collection",
    persist_dir="./my_chroma_data"
)

# Mode éphémère (tests)
test_store = ChromaVectorStore(
    collection_name="test_collection"
)
```

## 🎓 Prochaines étapes

Vous pouvez maintenant :

1. **Utiliser dans vos agents** : Intégrez le retriever dans vos agents LangGraph
2. **Créer des chaînes RAG** : Construisez des pipelines RAG complets avec LangChain
3. **Améliorer les embeddings** : Testez d'autres modèles d'embeddings
4. **Ajouter du reranking** : Intégrez des modèles de reranking pour améliorer les résultats

## 🔗 Ressources

- [LangChain Chroma Documentation](https://python.langchain.com/docs/integrations/vectorstores/chroma)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [LangChain Embeddings](https://python.langchain.com/docs/modules/data_connection/text_embedding/)

## 💡 Notes importantes

- ✅ **Compatibilité backward** : Votre code existant continue de fonctionner
- ✅ **Performance** : ChromaDB reste la base de données vectorielle sous-jacente
- ✅ **Flexibilité** : Vous pouvez accéder directement à la collection ChromaDB via `store.collection`
- ✅ **Intégration** : Compatible avec tous les composants LangChain (chaînes, agents, etc.)

---

**Status** : ✅ Intégration complète et fonctionnelle !
