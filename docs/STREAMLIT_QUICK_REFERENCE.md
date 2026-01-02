# Teslas.ai Modern UI - Quick Reference

## 🎯 Key Features at a Glance

| Feature | Description | Location |
|---------|-------------|----------|
| **Glassmorphism Design** | Modern frosted glass effect cards | Entire UI |
| **Token Tracking** | Real-time token consumption monitoring | Research tab + header |
| **Status Badges** | Color-coded execution status | All tabs |
| **Gradient Headers** | Eye-catching gradient text | Page title |
| **Advanced Config** | Expandable sidebar with full LLM control | Sidebar |
| **Result Export** | JSON, Markdown, LaTeX download options | Research results |
| **Multi-Tab Results** | 8 specialized view tabs for research output | Research tab |
| **Search History** | Chronological query tracking with metrics | History tab |
| **API Health** | Real-time backend status indicator | Header |
| **Agent Pipeline** | Visual agent execution order display | Sidebar |

## 🎨 Design Highlights

### Color Palette
```
Dark Background:  #0f172a (Very dark blue)
Card Background:  #1e293b (Dark slate)
Primary Accent:   #0066cc (Blue)
Secondary:        #6366f1 (Indigo)
Accent:           #ec4899 (Pink)
Success:          #10b981 (Green)
Warning:          #f59e0b (Amber)
Error:            #ef4444 (Red)
```

### CSS Effects
- **Backdrop Blur**: 10px frosted glass effect
- **Gradients**: 90° linear transitions with 3+ colors
- **Shadows**: `0 8px 32px rgba(0, 0, 0, 0.3)`
- **Border Radius**: 12px for cards, 8px for tabs
- **Transitions**: Smooth 0.3s animations

## 📊 UI Sections

### Header
```
[Teslas.ai Logo] [API Status] [KB Count]
🔬 Teslas.ai Multi-Agent Scientific Research
🟢 API v0.2.0    📚 1 documents
```

### Sidebar - Expandable Sections
1. **API Settings**
   - Base URL configuration
   - Custom endpoint support

2. **LLM Configuration**
   - Model selection (phi, mistral, etc.)
   - Temperature (0.0-1.0, 0.05 step)
   - Max tokens (100-4000)
   - Top-P nucleus sampling

3. **Agent Pipeline**
   - Multi-select from 8 available agents
   - Visual pipeline order display
   - Default: planner, mathematician, reviewer, writer

4. **Knowledge Base & Search**
   - RAG toggle
   - Top-K document retrieval (1-50)
   - Hybrid search option
   - Web search toggle

5. **KB Statistics**
   - Document count meter
   - Refresh button

6. **Advanced Options**
   - Stream output toggle
   - Debug mode
   - Result caching

### Main Tabs

#### 🔬 Research Tab
- Query input with 140px height
- Quick template buttons
- Query metadata (chars, tokens, agents)
- Execution controls
- 8-tab result display:
  1. Summary - Executive overview
  2. Mathematics - Equations & insights
  3. Numerical - Metrics display
  4. Data Analysis - JSON output
  5. Literature - Source links
  6. Review - Criticisms & improvements
  7. LaTeX - Academic export
  8. Details - Raw JSON/logs

#### 🔍 Search Tab
- Query input
- Source selector (scientific/arxiv/scholar/code)
- Max results slider (1-50)
- Expandable result cards

#### 📄 Ingest Tab
- Dual-mode toggle (upload/path)
- File uploader or text input
- Status feedback with chunk count

#### 📚 Knowledge Base Tab
- Document statistics
- Semantic search with top-k slider
- Result cards with similarity scores

#### 📜 History Tab
- Aggregate metrics (total queries, tokens, avg time)
- Expandable history items with:
  - Query text
  - Timestamp
  - Status badge
  - Token count
  - Execution time
  - Agent count

## 🎬 Interactive Elements

### Buttons
- **Primary** (type="primary"): Gradient background (blue → indigo)
- **Standard**: Glass card background
- **Width**: use_container_width=True for full-width buttons

### Inputs
- **Text Area**: 140px height for research queries
- **Text Input**: For search and file paths
- **Sliders**: Step granularity for precision control
- **Dropdowns**: Model and source selection

### Feedback
- **Success**: Green badge with checkmark
- **Error**: Red badge with X mark
- **Warning**: Yellow badge with triangle
- **Info**: Blue badge with circle
- **Spinner**: Animated during async operations

## 📈 Performance Metrics

### Token Estimation
```python
tokens = max(1, len(text) // 4)  # ~4 chars per token
```

### Time Formatting
```
< 60s: "12.3s"
< 60m: "2.5m"
≥ 60m: "1.2h"
```

## 🔐 Session State Variables

```python
st.session_state = {
    "api_url": "http://localhost:8000/api",
    "research_history": [],           # Chronological query list
    "kb_stats": {"count": 0},         # Knowledge base size
    "total_tokens": 0,                # Cumulative token count
    "current_settings": {},           # Active configuration
    "show_advanced": False,           # Advanced panel state
    "last_query": "",                 # Previous query text
    "api_health": False,              # API connectivity status
    "active_tab": 0,                  # Current tab index
}
```

## 🚀 Startup & Configuration

### Environment Variables
```bash
OLLAMA_MODEL=phi              # Default model
OLLAMA_HOST=http://ollama:11434  # Ollama endpoint
```

### Docker Compose
```bash
docker compose up -d          # Start services
docker compose logs -f api    # Monitor API logs
docker compose exec api bash  # Access container
```

### Streamlit Server
```bash
streamlit run app/ui/streamlit_app.py
# Access at http://localhost:8501
```

### Configuration File (if needed)
```toml
# ~/.streamlit/config.toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#f1f5f9"
```

## 🎯 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Rerun | `R` or `Cmd+Enter` |
| Clear cache | `C` |
| Settings | `S` |
| About | `A` |

## 🔗 API Endpoints Used

```
GET  /api/health              # Health check
POST /api/research            # Research workflow
POST /api/search              # Literature search
GET  /api/agents              # Available agents
POST /api/ingest              # Document ingestion
GET  /api/kb/count            # KB statistics
POST /api/kb/search           # Knowledge base search
```

## 📦 Dependencies

```
streamlit>=1.28.0             # Web framework
requests>=2.31.0              # HTTP client
python>=3.9                   # Language
```

## 🐛 Troubleshooting

### API Connection Error
- Ensure Docker containers are running: `docker compose ps`
- Check API health: `curl http://localhost:8000/api/health`
- Verify network connectivity

### Slow Response Times
- Reduce query complexity
- Reduce number of agents
- Enable result caching in advanced options
- Check system resources: `docker compose stats`

### Token Counter Inaccuracy
- Token estimation uses ~4 chars per token
- Actual token count depends on tokenizer
- Use as approximate guide only

### Session State Loss
- Session state persists across reruns
- Clear with "Clear History" button
- Browser cache affects persistence

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Ollama Models](https://ollama.ai/models)
- [FastAPI Docs](http://localhost:8000/docs) (when running)

---

**Last Updated**: December 26, 2025  
**Version**: 2.0 (Modern GenAI Interface)  
**Status**: ✅ Production Ready
