# 🧪 Scientific Assistant - Multi-Agent Research System

> **Assistant scientifique multi-agents local pour la recherche rigoureuse en mathématiques, méthodes numériques et data science.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![LangChain](https://img.shields.io/badge/LangChain-Powered-orange.svg)](https://www.langchain.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-purple.svg)](https://ollama.ai)

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [Installation rapide](#-installation-rapide)
- [Utilisation](#-utilisation)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [Développement](#-développement)

---

## 🎯 Vue d'ensemble

**Scientific Assistant** est un système multi-agents **local-first** conçu pour la recherche scientifique rigoureuse. Il combine 8 agents spécialisés avec RAG (Retrieval-Augmented Generation) pour fournir des analyses précises, reproductibles et citées.

### ✨ Pourquoi Scientific Assistant ?

- 🔒 **100% Local** - Vos données restent privées (Ollama + ChromaDB)
- 🎯 **Spécialisé** - Conçu pour la recherche scientifique rigoureuse
- 🤖 **Multi-agents** - 8 agents experts travaillent en synergie
- 📚 **RAG avancé** - Recherche hybride vectorielle + mots-clés
- 🔬 **Reproductible** - Génération de code Python exécutable
- 📝 **Documentation** - LaTeX, citations APA/BibTeX automatiques

### 🤖 Les 8 Agents spécialisés

| Agent | Rôle | Expertise |
|-------|------|-----------|
| **Planner** | Orchestration | Décomposition des tâches de recherche |
| **Mathematician** | Analyse symbolique | Preuves mathématiques, théorèmes |
| **Numerical** | Simulation | Méthodes numériques, convergence |
| **Data Scientist** | Statistiques | ML, analyse de données, incertitudes |
| **Literature** | Recherche | RAG + web search, citations |
| **Reviewer** | Qualité | Vérification, détection d'erreurs |
| **Writer** | Rédaction | Écriture académique, LaTeX |
| **Memory** | Connaissance | Gestion de la base de connaissances |

---

## 🚀 Fonctionnalités

### 💡 Capacités principales

- ✅ **Analyse mathématique** symbolique (SymPy)
- ✅ **Simulations numériques** (NumPy, SciPy, scikit-learn)
- ✅ **Ingestion de documents** (PDF, TXT, Markdown)
- ✅ **Recherche sémantique** avec embeddings
- ✅ **Génération de code** Python exécutable
- ✅ **Citations automatiques** (APA, BibTeX)
- ✅ **Export LaTeX** pour publications

### 🏗️ Stack technique

- **LLM** : Ollama (mistral, llama2, neural-chat...)
- **Orchestration** : LangChain + LangGraph
- **Vector DB** : ChromaDB + FAISS (hybrid)
- **Embeddings** : sentence-transformers
- **API** : FastAPI
- **UI** : Streamlit
- **Logging** : Loguru

---

## ⚡ Installation rapide

### Prérequis

- **Python 3.11+**
- **[Ollama](https://ollama.ai)** installé et en cours d'exécution
- **[uv](https://github.com/astral-sh/uv)** (gestionnaire de packages rapide)

### Installation en 3 étapes

#### 1️⃣ Installer uv et cloner le projet

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Cloner le repository
git clone https://github.com/Geobatpo07/scientific-assistant.git
cd scientific-assistant
```

#### 2️⃣ Installer les dépendances

```bash
# Synchroniser l'environnement (très rapide avec uv!)
uv sync

# Télécharger un modèle Ollama
ollama pull mistral
```

#### 3️⃣ Lancer l'application

```bash
# Méthode 1 : Script tout-en-un (recommandé)
uv run python scripts/run_local.py

# Méthode 2 : PowerShell
.\Makefile.ps1 run

# Méthode 3 : Docker
docker compose up -d --build
```

**Accès** :
- 🌐 Interface Web : http://localhost:8501
- 📡 API : http://localhost:8000
- 📚 Documentation API : http://localhost:8000/docs

### 🎛️ Configuration (optionnel)

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Personnaliser si nécessaire (les valeurs par défaut fonctionnent)
# - Modèle LLM
# - Taille des chunks
# - Niveau de log
# etc.
```

---

## 💻 Utilisation

### Interface Web (Streamlit)

1. Ouvrez http://localhost:8501
2. Entrez votre question de recherche
3. Sélectionnez les agents désirés
4. Cliquez sur "Run Research"
5. Explorez les résultats dans les onglets

### API REST

```bash
# Lancer une recherche
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze stability of explicit Euler method",
    "agents": ["planner", "mathematician", "numerical", "reviewer"]
  }'

# Rechercher dans la base de connaissances
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "finite difference methods",
    "search_type": "scientific",
    "max_results": 5
  }'

# Vérifier le statut
curl http://localhost:8000/api/health
```

### API Python

```python
from app.agents.graph import create_orchestrator

orchestrator = create_orchestrator()
context = orchestrator.run_research(
    "What are the stability conditions for the Euler method?"
)

print(context.final_summary)
print(context.mathematical_insights)
print(context.numerical_results)
```

### Via REST API

```bash
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{
# Créer l'orchestrateur
orchestrator = create_orchestrator()

# Lancer une recherche
context = orchestrator.run_research(
    "What are the stability conditions for the Euler method?"
)

# Accéder aux résultats
print(context.final_summary)
print(context.mathematical_insights)
print(context.numerical_results)
---

## 📚 Gestion de la base de connaissances

### Ingestion de documents

```bash
# Ingérer un PDF
uv run python scripts/ingest_docs.py data/papers/mon_article.pdf

# Ingérer un dossier complet
uv run python scripts/ingest_docs.py data/papers/

# Réinitialiser la base (attention !)
uv run python scripts/reset_db.py --confirm
```

**Formats supportés** : PDF, TXT, Markdown

**Processus** :
1. Chargement du document
2. Découpage en chunks (avec overlap)
3. Génération d'embeddings
4. Stockage dans ChromaDB
5. Indexation FAISS pour recherche rapide

---

## 🐳 Docker (Recommandé)

```bash
# Construire et démarrer
docker compose up -d --build

# Voir les logs
---

## 📐 Architecture

### Structure du projet

```
scientific-assistant/
├── 📁 app/                     # Code source principal
│   ├── agents/                 # 🤖 Système multi-agents
│   ├── vectorstore/            # 🗄️ ChromaDB + FAISS + LangChain-Chroma
│   ├── llm/                    # 🧠 Intégration Ollama + Embeddings
│   ├── rag/                    # 📚 Chaînes RAG + Citations
│   ├── tools/                  # 🔧 Outils scientifiques
│   ├── ingestion/              # 📥 Traitement documents
│   ├── api/                    # 🌐 FastAPI REST
│   ├── ui/                     # 🎨 Interface Streamlit
│   └── utils/                  # 📝 Logging (Loguru), helpers
├── 📁 docs/                    # 📖 Documentation complète
├── 📁 examples/                # 💡 Exemples de code
├── 📁 scripts/                 # 🛠️ Scripts utilitaires
├── 📁 tests/                   # 🧪 Tests unitaires
├── 📁 data/                    # 💾 Documents ingérés
├── 📁 chroma/                  # 🗃️ Persistence ChromaDB
├── 📄 pyproject.toml          # 📦 Dépendances (uv)
├── 🐳 docker-compose.yml      # Docker orchestration
└── 📄 README.md
```

### Flux de traitement

```
Question → PlannerAgent → Routage spécialisé
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
MathAgent  NumericalAgent  DataScientist
    ↓           ↓           ↓
    └───────────┼───────────┘
                ↓
         ReviewerAgent
                ↓
          WriterAgent
                ↓
          MemoryAgent
                ↓
         Résultat final
```

### Stack RAG hybride

- **ChromaDB** : Stockage persistant + métadonnées riches
- **FAISS** : Recherche rapide top-K (IDs uniquement)
- **LangChain-Chroma** : Intégration avec l'écosystème LangChain
- **Reranking** : Similarité cosinus + boost mots-clés
- **Fallback** : Si FAISS vide, utilise ChromaDB seul

---

## 📚 Documentation

📖 **Documentation complète disponible dans [docs/](docs/)**

### Guides principaux

- 🚀 **[Guide de démarrage](docs/GETTING_STARTED.md)** - Installation et premiers pas
- 🔗 **[LangChain-Chroma](docs/GUIDE_LANGCHAIN_CHROMA.md)** - Intégration vector store
- 📝 **[Logging Loguru](docs/LOGURU_SUMMARY.md)** - Système de logs
- 🎨 **[Design Guide](docs/DESIGN_GUIDE.md)** - Interface et design
- 📑 **[Index complet](docs/README.md)** - Navigation complète

### Exemples de code

- `examples/example_5_langchain_chroma.py` - Utilisation ChromaDB
- `examples/example_6_scientific_rag.py` - RAG scientifique
- `examples/example_7_loguru_features.py` - Logging avancé

---

## 🛠️ Développement

### Tests

```bash
# Tous les tests
uv run pytest tests/

# Avec couverture
uv run pytest --cov=app tests/

# Test spécifique
uv run pytest tests/test_agents.py -v
```

### Qualité du code

```bash
# Formatter (Black)
black app/ tests/

# Trier les imports
isort app/ tests/

# Type checking
mypy app/

# Linter
ruff check app/
```

### Contribuer

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amazing`)
3. Committez (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Ouvrez une Pull Request

---

## 🐛 Dépannage

### Problèmes courants

**Ollama introuvable**
```bash
# Installer depuis https://ollama.ai
ollama serve  # Lancer dans un terminal séparé
```

**Erreurs ChromaDB**
```bash
# Réinitialiser la base de données
uv run python scripts/reset_db.py --confirm
```

**Problèmes de mémoire**
- Réduire `CHUNK_SIZE` dans `.env`
- Utiliser un modèle plus petit (phi, mistral au lieu de llama2-70b)
- Limiter `TOP_K_RETRIEVAL`

**Logs pour débogage**
```bash
# Les logs sont dans logs/
tail -f logs/scientific_assistant_*.log
```

### ⚙️ Optimisation des performances

- **Modèles** : Préférer `mistral` ou `phi` pour l'itération rapide
- **Température** : Garder basse (0.3) pour la reproductibilité
- **Retrieval** : Ajuster `TOP_K_RETRIEVAL` (qualité vs vitesse)
- **Chunking** : Optimiser `CHUNK_SIZE` et `CHUNK_OVERLAP`
- **Docker** : Un seul worker par défaut, scaler prudemment

---

## 📜 Licence

MIT License - voir [LICENSE](LICENSE)

---

## 🙏 Remerciements

Construit avec :
- **[LangChain](https://www.langchain.com/)** - Orchestration multi-agents
- **[Ollama](https://ollama.ai)** - Inférence LLM locale
- **[ChromaDB](https://www.trychroma.com/)** - Base vectorielle
- **[Loguru](https://github.com/Delgan/loguru)** - Logging moderne
- **[Streamlit](https://streamlit.io/)** - Interface rapide
- **[FastAPI](https://fastapi.tiangolo.com/)** - API performante

Inspiré par LangChain et LlamaIndex.

---

<div align="center">

**Made with ⚡ for rigorous scientific research**

[Documentation](docs/) • [Examples](examples/) • [Issues](https://github.com/Geobatpo07/scientific-assistant/issues)

</div>