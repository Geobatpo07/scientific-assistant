# 🚀 Teslas.ai Modern UI - Getting Started Guide

## 📋 Prerequisites

- Docker & Docker Compose installed
- Python 3.9+ with Streamlit environment
- Backend API running on `http://localhost:8000/api`
- Ollama service running with at least one model

## 🎯 Quick Start

### Step 1: Start the Backend Services
```bash
cd "c:\Users\lgeov\Documents\Data Analytics Projects\scientific-assistant"

# Start Docker services
docker compose up -d

# Verify services are running
docker compose ps

# Expected output:
# NAME                 STATUS
# scientific-assistant-api-1    Up (healthy)
# scientific-assistant-ollama-1 Up
```

### Step 2: Verify API Health
```bash
# Check API endpoint
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","version":"0.2.0",...}
```

### Step 3: Launch Streamlit UI
```bash
# From the project root
streamlit run app/ui/streamlit_app.py

# Console output:
#   You can now view your Streamlit app in your browser.
#   Local URL: http://localhost:8501
```

### Step 4: Access the Interface
Open your browser and navigate to:
```
http://localhost:8501
```

## 🎨 What's New in the Modern Interface

### Visual Enhancements
- ✨ **Glassmorphism Design**: Frosted glass effect with backdrop blur
- 🎨 **Gradient Headers**: Eye-catching multi-color gradients
- 🟢 **Status Indicators**: Color-coded badges for health/status
- 📊 **Token Counters**: Real-time token usage tracking
- 🎭 **Dark Theme**: Professional dark mode with high contrast

### Functional Improvements
- ⚙️ **Advanced Configuration**: Expandable sidebar with full control
- 📈 **Performance Metrics**: Execution time and token tracking
- 📥 **Export Options**: JSON, Markdown, LaTeX downloads
- 🔍 **Enhanced Search**: Multi-source literature search
- 📚 **Knowledge Base**: Semantic search with top-K retrieval
- 📜 **Session History**: Chronological query tracking with metrics

### GenAI-Specific Features
- 🧠 **LLM Configuration**: Temperature, Top-P, Max tokens control
- 🤖 **Agent Pipeline**: Visual agent selection and ordering
- 🔗 **RAG Integration**: Hybrid search (vector + BM25)
- 🌐 **Web Search**: Optional external knowledge augmentation
- 🔐 **Local-First**: All processing stays private

## 📱 User Interface Walkthrough

### Header Section
```
┌─────────────────────────────────────────────────────────┐
│  🔬 Teslas.ai         🟢 API v0.2.0    📚 1 documents   │
│  Multi-Agent Scientific Research • Local GenAI Inference │
└─────────────────────────────────────────────────────────┘
```

### Sidebar Configuration (Expandable Panels)

1. **🔗 API Settings**
   - Modify API endpoint URL
   - Support for custom/local backends

2. **🧠 LLM Configuration**
   - Model selector (phi, mistral, neural-chat, llama2, dolphin-mixtral)
   - Temperature slider (0.0-1.0)
   - Max tokens slider (100-4000)
   - Top-P nucleus sampling

3. **🤖 Agent Pipeline**
   - Multi-select agent list
   - Visual pipeline order display
   - Default: planner, mathematician, reviewer, writer

4. **📚 Knowledge Base & Search**
   - RAG toggle
   - Top-K retrieval slider
   - Hybrid search option
   - Web search toggle

5. **📊 Knowledge Base Stats**
   - Document count display
   - Refresh button

6. **🔧 Advanced Options**
   - Stream output (experimental)
   - Debug mode
   - Result caching

### Main Tabs

#### Tab 1: 🔬 Research
```
┌─ Research Question ──────────────────────┐
│ [Text area with query]                   │
│ 📝 250 chars | 🪙 ~62 tokens | 4 agents │
└──────────────────────────────────────────┘

[▶️ Run Research Button] [⚡ Stream] [📄 LaTeX] [🔍 Debug]

Results (8 tabs):
├─ 📋 Summary - Executive overview
├─ 📐 Mathematics - Equations & insights
├─ 🧮 Numerical - Metrics display
├─ 📊 Data Analysis - JSON output
├─ 📚 Literature - Source links
├─ ✅ Review - Criticisms & improvements
├─ 📄 LaTeX - Academic export
└─ 🛠️ Details - Raw data & logs
```

#### Tab 2: 🔍 Search
```
[Query Input] [Source Dropdown] [Max Results Slider]
[🔎 Search Button]

Results:
├─ Title: "Paper Name"
├─ URL: [Link]
├─ Summary: "Abstract..."
└─ [Expandable for details]
```

#### Tab 3: 📄 Ingest
```
[Upload File / File Path Toggle]

Upload Mode:
├─ File picker
└─ Upload & Ingest button

Path Mode:
├─ Text input: /app/data/raw/document.txt
└─ Ingest button → Status: "✅ 5 chunks created"
```

#### Tab 4: 📚 Knowledge Base
```
[📚 Documents: 5] [Indexed: ✅] [🔄 Refresh] [🗑️ Clear]

Semantic Search:
├─ Query input
├─ Top-K slider (1-20)
└─ Search button → [Results with scores]
```

#### Tab 5: 📜 History
```
[Metrics]
├─ Total Queries: 12
├─ Total Tokens: 45,230
├─ Avg Time: 2.3m
└─ [🗑️ Clear History]

Query History:
├─ 1. "Stability analysis..." • ✅ Complete • 3,240 tokens • 2m 15s
├─ 2. "Neural networks..." • ✅ Complete • 2,890 tokens • 1m 45s
└─ ... (most recent first)
```

## 🧪 Testing the Interface

### Test 1: API Connectivity
1. Open the app
2. Check header for API status badge
3. Expected: 🟢 Green badge with version number

### Test 2: Research Query
1. Navigate to Research tab
2. Enter query: "Analyze stability of explicit Euler method"
3. Select 2-3 agents in sidebar
4. Click "Run Research"
5. Expected: Results in 8 tabs with metrics

### Test 3: Document Ingestion
1. Navigate to Ingest tab
2. Select "File Path" mode
3. Enter: `/app/data/raw/test_note.txt`
4. Click "Ingest"
5. Expected: Success message with chunk count

### Test 4: Knowledge Base Search
1. Navigate to Knowledge Base tab
2. Enter search query: "Euler method"
3. Click "Search"
4. Expected: Retrieved documents with scores

### Test 5: History Tracking
1. Run 2-3 research queries
2. Navigate to History tab
3. Expected: All queries with timestamps and metrics

## ⚙️ Configuration Tweaks

### Change Default Model
In sidebar → LLM Configuration → Model selector

### Adjust Research Agents
In sidebar → Agent Pipeline → Select/deselect agents

### Enable RAG Features
In sidebar → Knowledge Base & Search → Enable/disable RAG

### Debug Mode
In sidebar → Advanced Options → Enable Debug Mode
(Shows raw API requests/responses)

## 📊 Performance Tips

### For Faster Responses
1. Reduce number of agents (2-3 optimal)
2. Lower max tokens setting
3. Disable web search if not needed
4. Increase temperature (more creative, faster)

### For Better Quality
1. Increase agent count (4-5 optimal)
2. Lower temperature (more deterministic)
3. Enable RAG for domain knowledge
4. Use detailed queries

## 🔧 Troubleshooting

### "API is not available" Error
```bash
# Check if Docker services are running
docker compose ps

# If not running:
docker compose up -d

# Check logs:
docker compose logs api
```

### Slow Response Times
```bash
# Check system resources
docker compose stats

# Reduce query complexity
# Lower agent count in sidebar
# Disable features in Advanced Options
```

### Session State Issues
```bash
# Clear Streamlit cache
# Press 'C' key in browser, or
# Stop and restart: streamlit run ...
```

### Token Counter Seems Wrong
- Estimation: ~1 token per 4 characters
- This is approximate for English text
- Actual tokens depend on tokenizer

## 🎓 Example Queries

### Mathematical Analysis
```
"Provide rigorous mathematical analysis of the convergence properties 
of gradient descent with adaptive learning rates. Include relevant theorems 
and proofs."
```

### Numerical Methods
```
"Analyze the stability region and accuracy of the Runge-Kutta 4th order 
method for stiff differential equations. Compare with implicit methods."
```

### Data Science
```
"Conduct comprehensive data science analysis on the iris dataset. Include 
exploratory analysis, feature importance, clustering, and classification 
model comparison."
```

## 📚 Resource Links

- Teslas.ai Project: [GitHub Repository]
- Streamlit Docs: https://docs.streamlit.io
- Ollama Models: https://ollama.ai/models
- API Swagger Docs: http://localhost:8000/docs

## 🎯 Next Steps

1. ✅ Run the interface: `streamlit run app/ui/streamlit_app.py`
2. ✅ Test all tabs with sample queries
3. ✅ Configure sidebar settings to your preference
4. ✅ Try document ingestion with your own files
5. ✅ Experiment with different agent combinations

## 📝 Notes

- All data processing is local (no cloud sync)
- Knowledge base is persistent in `./chroma/` directory
- Session history is stored in browser session state
- Configuration changes take effect immediately

## 🚨 Important Information

### API Requirements
- Backend must be running on `http://localhost:8000/api`
- Ollama must be accessible (default: `http://ollama:11434`)
- Docker network must be properly configured

### Data Privacy
- ✅ All queries processed locally
- ✅ No data sent to external services (unless web search enabled)
- ✅ Knowledge base stored locally in Chroma DB
- ✅ Complete control over processing

### System Requirements
- Minimum: 2 CPU cores, 4GB RAM
- Recommended: 4+ CPU cores, 8GB+ RAM
- Ollama model size affects memory usage (phi: ~3GB)

---

**Status**: ✅ Ready to Use  
**Version**: 2.0 Modern GenAI Interface  
**Last Updated**: December 26, 2025
