"""
Teslas.ai - Modern GenAI Scientific Research Assistant UI
A production-grade Streamlit interface with glassmorphism design.
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
import time
from dataclasses import dataclass

# ============================================================================
# PAGE CONFIGURATION & MODERN STYLING
# ============================================================================

st.set_page_config(
    page_title="Teslas.ai - Scientific Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Modern glassmorphism styling with gradients
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Dark theme background */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f1f5f9;
    }
    
    /* Glassmorphism cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Gradient text */
    .gradient-text {
        background: linear-gradient(90deg, #0066cc 0%, #6366f1 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }
    
    .status-success { background: #10b981; color: white; }
    .status-warning { background: #f59e0b; color: white; }
    .status-danger { background: #ef4444; color: white; }
    .status-info { background: #3b82f6; color: white; }
    
    /* Token counter styling */
    .token-counter {
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid #6366f1;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 4px;
    }
    
    /* Metric cards */
    .metric-item {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        background: rgba(100, 116, 139, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #0066cc 0%, #6366f1 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "api_url": "http://localhost:8000/api",
        "research_history": [],
        "kb_stats": {"count": 0},
        "total_tokens": 0,
        "current_settings": {},
        "show_advanced": False,
        "last_query": "",
        "api_health": False,
        "active_tab": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_api_health() -> Tuple[bool, str]:
    """Check API health. Returns (is_healthy, version_or_error)."""
    try:
        resp = requests.get(
            f"{st.session_state.api_url}/health",
            timeout=3
        )
        if resp.status_code == 200:
            data = resp.json()
            return True, f"v{data.get('version', '?')}"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Unreachable"
    except Exception as e:
        return False, str(e)[:30]
    return False, "Error"


def get_kb_stats() -> Dict[str, Any]:
    """Fetch KB statistics."""
    try:
        resp = requests.get(f"{st.session_state.api_url}/kb/count", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return {"count": 0}


def list_available_agents() -> List[str]:
    """Get available agents."""
    agents = ["planner", "mathematician", "reviewer", "writer", 
              "data_scientist", "numerical", "literature", "memory_curator"]
    try:
        resp = requests.get(f"{st.session_state.api_url}/agents", timeout=5)
        if resp.status_code == 200:
            return resp.json().get("agents", agents)
    except:
        pass
    return agents


def estimate_tokens(text: str) -> int:
    """Estimate tokens (1 token ≈ 4 chars)."""
    return max(1, len(text) // 4)


def format_execution_time(seconds: float) -> str:
    """Format execution time."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

# ============================================================================
# HEADER & NAVIGATION
# ============================================================================

def render_header():
    """Render modern header with health status."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("# <span class='gradient-text'>🔬 Teslas.ai</span>", 
                   unsafe_allow_html=True)
        st.caption("Multi-Agent Scientific Research • Local GenAI Inference")
    
    with col2:
        health, version = check_api_health()
        st.session_state.api_health = health
        if health:
            st.markdown(f'<span class="status-badge status-success">🟢 API {version}</span>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="status-badge status-danger">🔴 {version}</span>', 
                       unsafe_allow_html=True)
    
    with col3:
        kb_count = get_kb_stats().get("count", 0)
        st.markdown(f'<span class="status-badge status-info">📚 {kb_count} docs</span>', 
                   unsafe_allow_html=True)
    
    st.divider()


# ============================================================================
# ADVANCED SIDEBAR CONFIGURATION
# ============================================================================

def render_sidebar() -> Dict[str, Any]:
    """Render advanced configuration sidebar."""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Settings
        with st.expander("🔗 API Settings", expanded=False):
            api_url = st.text_input(
                "API Base URL",
                value=st.session_state.api_url,
                help="Teslas.ai API endpoint",
            )
            st.session_state.api_url = api_url
        
        st.divider()
        
        # LLM Configuration
        with st.expander("🧠 LLM Configuration", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                model = st.selectbox(
                    "Model",
                    ["phi", "mistral", "neural-chat", "llama2", "dolphin-mixtral"],
                    help="Ollama model",
                )
            
            with col2:
                temperature = st.slider(
                    "Temperature",
                    0.0, 1.0, 0.3,
                    step=0.05,
                    help="Low=Focused, High=Creative"
                )
            
            max_tokens = st.slider(
                "Max Tokens",
                100, 4000, 1024,
                step=100,
            )
            
            top_p = st.slider(
                "Top-P (Nucleus)",
                0.0, 1.0, 0.9,
                step=0.05,
            )
        
        st.divider()
        
        # Agent Selection
        with st.expander("🤖 Agent Pipeline", expanded=True):
            available_agents = list_available_agents()
            selected_agents = st.multiselect(
                "Active Agents",
                available_agents,
                default=["planner", "mathematician", "reviewer", "writer"],
            )
        
        st.divider()
        
        # RAG Configuration
        with st.expander("📚 Knowledge Base & Search", expanded=True):
            enable_rag = st.checkbox(
                "Enable Knowledge Base Retrieval",
                value=True,
            )
            
            if enable_rag:
                top_k = st.slider("Top-K Documents", 1, 50, 5)
                hybrid_search = st.checkbox("Hybrid Search", value=True)
            else:
                top_k = 0
                hybrid_search = False
            
            enable_web_search = st.checkbox("Enable Web Search", value=True)
        
        st.divider()
        
        # KB Statistics
        with st.expander("📊 Knowledge Base Stats", expanded=True):
            kb_stats = get_kb_stats()
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Documents", kb_stats.get("count", 0))
            
            with col2:
                if st.button("🔄 Refresh", use_container_width=True, key="refresh_sidebar"):
                    st.rerun()
        
        st.divider()
        
        # Advanced Options
        with st.expander("🔧 Advanced Options", expanded=False):
            stream_output = st.checkbox("Stream Output", value=False)
            debug_mode = st.checkbox("Debug Mode", value=False)
            cache_results = st.checkbox("Cache Results", value=True)
        
        st.divider()
        
        # About section
        st.markdown("### ℹ️ About Teslas.ai")
        st.info(
            "**Teslas.ai** is a multi-agent scientific research assistant "
            "powered by local LLM inference. All processing is private.",
            icon="🔒"
        )
        
        return {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "agents": selected_agents,
            "enable_rag": enable_rag,
            "top_k": top_k,
            "hybrid_search": hybrid_search,
            "enable_web_search": enable_web_search,
        }


# ============================================================================
# MAIN TABS
# ============================================================================

def main():
    """Main Streamlit application."""
    render_header()
    config = render_sidebar()
    
    # Main navigation tabs
    tab_research, tab_search, tab_ingest, tab_kb, tab_history = st.tabs([
        "🔬 Research",
        "🔍 Search",
        "📄 Ingest",
        "📚 Knowledge Base",
        "📜 History"
    ])

# ============================================================================
# RESEARCH TAB - ENHANCED
# ============================================================================

def render_research_tab(config: Dict[str, Any]):
    """Render advanced research interface."""
    st.markdown("## 🔬 Scientific Research")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        research_query = st.text_area(
            "Research Question",
            placeholder="Analyze stability of explicit Euler method for ODE y'=-ky with k > 0...",
            height=140,
            help="Be specific and detailed"
        )
    
    with col2:
        st.write("### Templates")
        if st.button("📐 Mathematical", key="template_math"):
            research_query = "Provide rigorous mathematical analysis of: "
        if st.button("🧮 Numerical", key="template_numerical"):
            research_query = "Analyze numerical stability and convergence of: "
        if st.button("📊 Data Science", key="template_data"):
            research_query = "Conduct comprehensive data science analysis on: "
    
    # Query metadata
    if research_query:
        query_tokens = estimate_tokens(research_query)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f'<span class="token-counter">📝 {len(research_query)} chars</span>', 
                       unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span class="token-counter">🪙 ~{query_tokens} tokens</span>', 
                       unsafe_allow_html=True)
        with col3:
            st.markdown(f'<span class="status-badge status-info">Agents: {len(config["agents"])}</span>', 
                       unsafe_allow_html=True)
    
    st.divider()
    
    # Execution controls
    col_run, col_opts = st.columns([1, 3])
    
    with col_run:
        run_research = st.button(
            "▶️ Run Research",
            use_container_width=True,
            type="primary",
        )
    
    with col_opts:
        opt1, opt2, opt3 = st.columns(3)
        with opt1:
            stream_output = st.checkbox("⚡ Stream", value=False)
        with opt2:
            save_latex = st.checkbox("📄 LaTeX", value=True)
        with opt3:
            verbose = st.checkbox("🔍 Debug", value=False)
    
    # Execute research
    if run_research and research_query:
        if not st.session_state.api_health:
            st.error("❌ API is not available. Check configuration in sidebar.")
            return
        
        with st.spinner("🤖 Research in progress..."):
            try:
                start_time = time.time()
                
                payload = {
                    "query": research_query,
                    "agents": config["agents"],
                }
                
                resp = requests.post(
                    f"{st.session_state.api_url}/research",
                    json=payload,
                    timeout=600
                )
                
                execution_time = time.time() - start_time
                
                if resp.status_code == 200:
                    result = resp.json()
                    tokens_used = estimate_tokens(research_query) + estimate_tokens(json.dumps(result))
                    st.session_state.total_tokens += tokens_used
                    
                    # Add to history
                    st.session_state.research_history.insert(0, {
                        "timestamp": datetime.now().isoformat(),
                        "query": research_query[:60],
                        "status": result.get("status", "completed"),
                        "tokens": tokens_used,
                        "time": execution_time,
                        "agents": config["agents"],
                    })
                    
                    # Success message with metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f'<span class="status-badge status-success">✅ Complete</span>', 
                                   unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<span class="token-counter">{tokens_used:,} tokens</span>', 
                                   unsafe_allow_html=True)
                    with col3:
                        st.write(f"⏱️ {format_execution_time(execution_time)}")
                    with col4:
                        st.write(f"📊 Total: {st.session_state.total_tokens:,}")
                    
                    st.divider()
                    
                    # Results display
                    render_result_with_tabs(result)
                else:
                    st.error(f"❌ API Error {resp.status_code}: {resp.text[:200]}")
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Try simpler query.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def render_result_with_tabs(result: Dict[str, Any]):
    """Render research result with comprehensive tabs."""
    result_tabs = st.tabs([
        "📋 Summary",
        "📐 Mathematics",
        "🧮 Numerical",
        "📊 Data Analysis",
        "📚 Literature",
        "✅ Review",
        "📄 LaTeX",
        "🛠️ Details"
    ])
    
    # Tab 1: Summary
    with result_tabs[0]:
        st.markdown("### Executive Summary")
        summary = result.get("summary", "No summary generated")
        st.write(summary)
    
    # Tab 2: Mathematics
    with result_tabs[1]:
        st.markdown("### Mathematical Insights")
        insights = result.get("mathematical_insights", [])
        if insights:
            for i, insight in enumerate(insights, 1):
                st.info(f"{i}. {insight}")
        else:
            st.info("No mathematical insights generated")
        
        equations = result.get("final_equations", [])
        if equations:
            st.markdown("### Key Equations")
            for eq in equations:
                st.latex(eq)
    
    # Tab 3: Numerical
    with result_tabs[2]:
        st.markdown("### Numerical Results")
        numerical = result.get("numerical_results", {})
        if numerical:
            metrics = st.columns(min(3, len(numerical)))
            for idx, (key, value) in enumerate(numerical.items()):
                with metrics[idx % len(metrics)]:
                    st.metric(key, value)
        else:
            st.info("No numerical results")
    
    # Tab 4: Data Analysis
    with result_tabs[3]:
        st.markdown("### Data Analysis")
        data = result.get("data_analysis", {})
        if data:
            st.json(data)
        else:
            st.info("No data analysis results")
    
    # Tab 5: Literature
    with result_tabs[4]:
        st.markdown("### Literature Sources")
        sources = result.get("literature_sources", [])
        if sources:
            for src in sources:
                with st.expander(f"📖 {src.get('title', 'Source')[:70]}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**URL**: {src.get('url', 'N/A')}")
                        st.write(f"**Authors**: {src.get('authors', 'N/A')}")
                    with col2:
                        st.markdown(f"[🔗 Open]({src.get('url', '#')})")
        else:
            st.info("No literature sources found")
    
    # Tab 6: Review
    with result_tabs[5]:
        col_crit, col_improve = st.columns(2)
        
        with col_crit:
            st.markdown("### Criticisms")
            criticisms = result.get("criticisms", [])
            if criticisms:
                for crit in criticisms:
                    st.warning(f"⚠️ {crit}")
            else:
                st.success("✅ No criticisms found")
        
        with col_improve:
            st.markdown("### Improvements")
            improvements = result.get("improvements", [])
            if improvements:
                for imp in improvements:
                    st.info(f"💡 {imp}")
            else:
                st.success("✅ Optimal analysis")
    
    # Tab 7: LaTeX
    with result_tabs[6]:
        st.markdown("### LaTeX Document")
        latex_doc = result.get("latex_document", "")
        if latex_doc:
            st.code(latex_doc, language="latex")
            st.download_button(
                "⬇️ Download .tex",
                data=latex_doc,
                file_name=f"research_{int(time.time())}.tex",
                mime="text/plain",
                key=f"dl_tex_{int(time.time())}"
            )
        else:
            st.info("No LaTeX generated")
    
    # Tab 8: Details
    with result_tabs[7]:
        st.markdown("### Execution Details")
        details_tab1, details_tab2, details_tab3 = st.tabs(["JSON", "Markdown", "Raw"])
        
        with details_tab1:
            st.json(result)
        
        with details_tab2:
            md = export_as_markdown(result)
            st.code(md, language="markdown")
            st.download_button(
                "⬇️ Download .md",
                data=md,
                file_name=f"research_{int(time.time())}.md",
                mime="text/markdown",
                key=f"dl_md_{int(time.time())}"
            )
        
        with details_tab3:
            st.json({
                "Status": result.get("status"),
                "Execution Path": result.get("execution_path"),
                "Errors": result.get("errors", []),
            })


def export_as_markdown(result: Dict[str, Any]) -> str:
    """Export result as markdown."""
    return f"""# Research Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
{result.get('summary', 'N/A')}

## Mathematical Insights
{json.dumps(result.get('mathematical_insights', []), indent=2)}

## Numerical Results
{json.dumps(result.get('numerical_results', {}), indent=2)}

## Status
- **Status**: {result.get('status', 'unknown')}
- **Execution Path**: {result.get('execution_path', 'N/A')}
"""


# ============================================================================
# SEARCH TAB - MODERN
# ============================================================================

def render_search_tab():
    """Render literature search interface."""
    st.markdown("## 🔍 Scientific Literature Search")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "Search Query",
            placeholder="Search papers, methodologies, concepts..."
        )
    
    with col2:
        search_type = st.selectbox(
            "Source",
            ["scientific", "arxiv", "scholar", "code"],
            label_visibility="collapsed"
        )
    
    with col3:
        max_results = st.number_input(
            "Results",
            1, 50, 10,
            label_visibility="collapsed"
        )
    
    do_search = st.button("🔎 Search", use_container_width=True, type="primary")
    
    if do_search and search_query:
        if not st.session_state.api_health:
            st.error("API unavailable")
            return
        
        with st.spinner("Searching..."):
            try:
                resp = requests.post(
                    f"{st.session_state.api_url}/search",
                    json={
                        "query": search_query,
                        "search_type": search_type,
                        "max_results": max_results
                    },
                    timeout=30
                )
                
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    st.success(f"✅ Found {len(results)} results")
                    
                    for i, result in enumerate(results, 1):
                        with st.expander(f"{i}. {result.get('title', 'Untitled')[:70]}"):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**Title**: {result.get('title')}")
                                st.markdown(f"**Summary**: {result.get('summary', 'N/A')}")
                            with col2:
                                st.markdown(f"[🔗 Link]({result.get('url', '#')})")
                else:
                    st.error(f"Search failed: {resp.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")


# ============================================================================
# INGEST TAB - FILE MANAGEMENT
# ============================================================================

def render_ingest_tab():
    """Render document ingestion interface."""
    st.markdown("## 📄 Document Ingestion")
    
    st.info(
        "📚 Upload scientific documents (TXT, PDF, Markdown) to build your knowledge base. "
        "Documents are automatically chunked and indexed for retrieval.",
        icon="💡"
    )
    
    ingest_mode = st.radio(
        "Mode",
        ["Upload File", "File Path"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if ingest_mode == "Upload File":
        uploaded_file = st.file_uploader(
            "Choose document",
            type=["txt", "md", "pdf"],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"📄 {uploaded_file.name}")
            with col2:
                st.write(f"Size: {uploaded_file.size / 1024:.1f} KB")
            with col3:
                if st.button("⬆️ Upload", use_container_width=True, key="upload_file"):
                    st.success("✅ Upload successful (backend integration needed)")
    
    else:
        file_path = st.text_input(
            "File Path",
            placeholder="/app/data/raw/document.txt",
            label_visibility="collapsed"
        )
        
        if file_path and st.button("⬆️ Ingest", use_container_width=True, type="primary", key="ingest_file"):
            if not st.session_state.api_health:
                st.error("API unavailable")
                return
            
            with st.spinner("Ingesting..."):
                try:
                    resp = requests.post(
                        f"{st.session_state.api_url}/ingest",
                        params={"file_path": file_path},
                        timeout=60
                    )
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"✅ Ingested!")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Chunks", data.get("chunks_created", 0))
                        with col2:
                            st.metric("Status", data.get("status"))
                    else:
                        st.error(f"Failed: {resp.status_code}\n{resp.text[:200]}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


# ============================================================================
# KNOWLEDGE BASE TAB - ADVANCED SEARCH
# ============================================================================

def render_kb_tab():
    """Render knowledge base management interface."""
    st.markdown("## 📚 Knowledge Base Management")
    
    kb_stats = get_kb_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Documents", kb_stats.get("count", 0))
    with col2:
        st.metric("Indexed", "✅" if kb_stats.get("count", 0) > 0 else "❌")
    with col3:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_kb"):
            st.rerun()
    with col4:
        if st.button("🗑️ Clear", use_container_width=True, key="clear_kb"):
            st.warning("Clear KB functionality coming soon")
    
    st.divider()
    
    st.markdown("### 🔍 Semantic Search")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        kb_query = st.text_input("Query", placeholder="Search your documents...")
    
    with col2:
        kb_k = st.slider("Top-K", 1, 20, 5, label_visibility="collapsed")
    
    if kb_query and st.button("Search", type="primary", use_container_width=True, key="kb_search"):
        if not st.session_state.api_health:
            st.error("API unavailable")
            return
        
        with st.spinner("Searching KB..."):
            try:
                resp = requests.post(
                    f"{st.session_state.api_url}/kb/search",
                    params={"query": kb_query, "k": kb_k},
                    timeout=30
                )
                
                if resp.status_code == 200:
                    kb_result = resp.json()
                    results = kb_result.get("results", [])
                    st.success(f"Found {len(results)} matches")
                    
                    for i, result in enumerate(results, 1):
                        with st.expander(f"{i}. Score: {result.get('score', '?'):.2f}"):
                            st.write(result.get("content", "No content"))
                else:
                    st.error(f"Search failed: {resp.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")


# ============================================================================
# HISTORY TAB - SESSION MANAGEMENT
# ============================================================================

def render_history_tab():
    """Render research history and session management."""
    st.markdown("## 📜 Research History")
    
    if not st.session_state.research_history:
        st.info("No research queries yet. Start by running a research query.", icon="📝")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Queries", len(st.session_state.research_history))
    with col2:
        st.metric("Total Tokens", f"{st.session_state.total_tokens:,}")
    with col3:
        avg_time = sum(h.get("time", 0) for h in st.session_state.research_history) / len(st.session_state.research_history)
        st.metric("Avg Time", format_execution_time(avg_time))
    with col4:
        if st.button("🗑️ Clear History", key="clear_history"):
            st.session_state.research_history = []
            st.rerun()
    
    st.divider()
    
    # History display
    for i, item in enumerate(st.session_state.research_history, 1):
        with st.expander(
            f"**{i}.** {item['query']} • "
            f"{render_status_badge(item['status'])} "
            f"⏱️ {format_execution_time(item.get('time', 0))}",
            expanded=(i == 1)
        ):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.caption(f"🕐 {item['timestamp']}")
            with col2:
                st.write(f"🪙 {item.get('tokens', 0):,}")
            with col3:
                st.write(f"🤖 {len(item.get('agents', []))} agents")
            
            st.markdown(f"**Query**: {item['query']}")


def render_status_badge(status: str) -> str:
    """Render HTML status badge."""
    status_map = {
        "completed": ("✅ Completed", "status-success"),
        "running": ("⏳ Running", "status-warning"),
        "failed": ("❌ Failed", "status-danger"),
        "pending": ("⏸️ Pending", "status-info"),
    }
    text, css_class = status_map.get(status, (status, "status-info"))
    return f'<span class="status-badge {css_class}">{text}</span>'


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main Streamlit application."""
    render_header()
    config = render_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔬 Research",
        "🔍 Search",
        "📄 Ingest",
        "📚 Knowledge Base",
        "📜 History"
    ])
    
    with tab1:
        render_research_tab(config)
    
    with tab2:
        render_search_tab()
    
    with tab3:
        render_ingest_tab()
    
    with tab4:
        render_kb_tab()
    
    with tab5:
        render_history_tab()


if __name__ == "__main__":
    main()
