"""
Teslas.ai - Scientific Research Assistant UI
A professional, researcher-oriented Streamlit interface with FAST/FULL execution modes.

Target Users: Applied mathematics researchers, data scientists, engineers, graduate students
Design Philosophy: Scientific, minimal, professional - clarity, rigor, traceability
"""

import os
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import time
from dataclasses import dataclass

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Teslas.ai - Scientific Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# SCIENTIFIC STYLING - DARK/LIGHT MODE SUPPORT
# ============================================================================

st.markdown("""
<style>
    /* ===== BASE THEME VARIABLES ===== */
    :root {
        --primary-blue: #1e40af;
        --primary-indigo: #4f46e5;
        --secondary-slate: #475569;
        --accent-cyan: #06b6d4;
        --success-green: #10b981;
        --warning-amber: #f59e0b;
        --error-red: #ef4444;
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
    }
    
    /* ===== GLOBAL RESETS ===== */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* ===== MAIN CONTAINER ===== */
    .main {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        padding: 1.5rem;
    }
    
    /* ===== HEADER STYLING ===== */
    .teslas-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding: 1.5rem;
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 12px;
    }
    
    .teslas-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1e40af 0%, #4f46e5 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    
    .teslas-tagline {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
        font-weight: 400;
    }
    
    /* ===== STATUS INDICATORS ===== */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
        white-space: nowrap;
    }
    
    .status-online {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid #10b981;
    }
    
    .status-offline {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
    }
    
    .status-info {
        background: rgba(59, 130, 246, 0.2);
        color: #3b82f6;
        border: 1px solid #3b82f6;
    }
    
    .status-mode {
        background: rgba(79, 70, 229, 0.2);
        color: #6366f1;
        border: 1px solid #6366f1;
        font-family: 'Courier New', monospace;
    }
    
    /* ===== CARDS & CONTAINERS ===== */
    .content-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 8px;
        padding: 1.25rem;
        margin: 0.75rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.3) 0%, rgba(79, 70, 229, 0.3) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--accent-cyan);
        font-family: 'Courier New', monospace;
    }
    
    /* ===== TABS STYLING ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        background: rgba(71, 85, 105, 0.2);
        color: var(--text-secondary);
        padding: 0.6rem 1.2rem;
        border: 1px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, var(--primary-blue) 0%, var(--primary-indigo) 100%);
        color: white;
        border: 1px solid var(--primary-indigo);
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, var(--primary-blue) 0%, var(--primary-indigo) 100%);
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    /* ===== EXECUTION MODE SELECTOR ===== */
    .mode-selector {
        background: rgba(30, 41, 59, 0.7);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    
    /* ===== CODE & EQUATIONS ===== */
    code {
        font-family: 'Courier New', Consolas, Monaco, monospace;
        background: rgba(15, 23, 42, 0.8);
        padding: 0.15rem 0.4rem;
        border-radius: 3px;
        font-size: 0.9em;
    }
    
    pre {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 6px;
        padding: 1rem;
    }
    
    /* ===== PERFORMANCE METRICS ===== */
    .perf-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    
    .perf-table th {
        background: rgba(30, 64, 175, 0.3);
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid var(--primary-indigo);
    }
    
    .perf-table td {
        padding: 0.6rem 0.75rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    /* ===== EXPANDER STYLING ===== */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 6px;
        font-weight: 600;
    }
    
    /* ===== DIVIDER ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.3), transparent);
        margin: 1.5rem 0;
    }
    
    /* ===== LIGHT MODE OVERRIDES (when user sets light theme) ===== */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-primary: #f8fafc;
            --bg-secondary: #f1f5f9;
            --text-primary: #0f172a;
            --text-secondary: #475569;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# Use container-friendly API URL if provided (e.g., http://api:8000/api inside compose)
DEFAULT_API_URL = os.getenv("TESLAS_API_URL", "http://localhost:8000/api")


def init_session_state():
    """Initialize all session state variables for the application."""
    defaults = {
        # API Configuration
        "api_url": DEFAULT_API_URL,
        "api_health": False,
        "api_version": "Unknown",
        
        # Execution Mode
        "execution_mode": "FAST",
        
        # Feature Toggles
        "enable_rag": True,
        "enable_web_search": False,
        "enable_memory": False,
        
        # Research State
        "research_history": [],
        "current_result": None,
        "last_query": "",
        
        # System Stats
        "kb_stats": {"count": 0},
        "total_tokens": 0,
        "total_queries": 0,
        
        # UI State
        "theme_mode": "dark",  # 'dark' or 'light'
        "show_advanced": False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_api_health() -> Tuple[bool, str]:
    """
    Check API health and retrieve version.
    Returns: (is_healthy: bool, version_or_error: str)
    """
    try:
        resp = requests.get(
            f"{st.session_state.api_url}/health",
            timeout=3
        )
        if resp.status_code == 200:
            data = resp.json()
            version = data.get('version', 'unknown')
            st.session_state.api_health = True
            st.session_state.api_version = version
            return True, f"v{version}"
        return False, f"HTTP {resp.status_code}"
    except requests.exceptions.Timeout:
        st.session_state.api_health = False
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        st.session_state.api_health = False
        return False, "Unreachable"
    except Exception as e:
        st.session_state.api_health = False
        return False, str(e)[:30]


def get_kb_stats() -> Dict[str, Any]:
    """Fetch knowledge base statistics from the API."""
    try:
        resp = requests.get(
            f"{st.session_state.api_url}/kb/count",
            timeout=5
        )
        if resp.status_code == 200:
            stats = resp.json()
            st.session_state.kb_stats = stats
            return stats
    except:
        pass
    return {"count": 0}


def format_execution_time(seconds: float) -> str:
    """Format execution time in human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 1 token ≈ 4 characters)."""
    return max(1, len(text) // 4)


def get_mode_description(mode: str) -> str:
    """Get human-readable description of execution mode."""
    descriptions = {
        "FAST": "Quick answers, minimal latency, essential agents (~few minutes)",
        "FULL": "Deep research, maximum rigor, all agents (~tens of minutes)"
    }
    return descriptions.get(mode, "Unknown mode")


def get_mode_icon(mode: str) -> str:
    """Get icon for execution mode."""
    return "⚡" if mode == "FAST" else "🔬"

# ============================================================================
# HEADER COMPONENT
# ============================================================================

def render_header():
    """Render professional header with system status indicators."""
    # Check API health
    health, version = check_api_health()
    kb_count = get_kb_stats().get("count", 0)
    
    # Header layout
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="teslas-header">
            <div>
                <h1 class="teslas-title">🔬 Teslas.ai</h1>
                <p class="teslas-tagline">Scientific Research Assistant</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # API Status
        if health:
            st.markdown(
                f'<div class="status-indicator status-online">🟢 API {version}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="status-indicator status-offline">🔴 {version}</div>',
                unsafe_allow_html=True
            )
    
    with col3:
        # Knowledge Base
        st.markdown(
            f'<div class="status-indicator status-info">📚 {kb_count} docs</div>',
            unsafe_allow_html=True
        )
    
    with col4:
        # Execution Mode
        mode_icon = get_mode_icon(st.session_state.execution_mode)
        st.markdown(
            f'<div class="status-indicator status-mode">{mode_icon} {st.session_state.execution_mode}</div>',
            unsafe_allow_html=True
        )


# ============================================================================
# SIDEBAR - NAVIGATION & CONFIGURATION
# ============================================================================

def render_sidebar():
    """Render sidebar with execution mode selector and configuration options."""
    with st.sidebar:
        # ===== BRANDING =====
        st.markdown("### ⚙️ Configuration")
        st.divider()
        
        # ===== EXECUTION MODE SELECTOR =====
        st.markdown("#### Execution Mode")
        
        mode = st.radio(
            "Select mode:",
            ["FAST", "FULL"],
            index=0 if st.session_state.execution_mode == "FAST" else 1,
            help=(
                "**FAST**: Quick answers, minimal latency, essential agents\n\n"
                "**FULL**: Deep research, maximum rigor, all agents"
            ),
            label_visibility="collapsed"
        )
        st.session_state.execution_mode = mode
        
        # Mode description
        st.caption(get_mode_description(mode))
        
        st.divider()
        
        # ===== FEATURE TOGGLES =====
        st.markdown("#### Features")
        
        st.session_state.enable_rag = st.checkbox(
            "📚 Enable RAG (Knowledge Base)",
            value=st.session_state.enable_rag,
            help="Retrieve relevant documents from knowledge base"
        )
        
        st.session_state.enable_web_search = st.checkbox(
            "🌐 Enable Web Search",
            value=st.session_state.enable_web_search,
            help="Search online scientific literature (arXiv, Scholar, etc.)",
            disabled=(mode == "FAST")  # Disabled in FAST mode
        )
        
        st.session_state.enable_memory = st.checkbox(
            "🧠 Enable Memory",
            value=st.session_state.enable_memory,
            help="Maintain conversation context across queries",
            disabled=(mode == "FAST")  # Disabled in FAST mode
        )
        
        st.divider()
        
        # ===== ADVANCED SETTINGS =====
        with st.expander("🔧 Advanced Settings", expanded=False):
            # API Configuration
            st.markdown("**API Configuration**")
            api_url = st.text_input(
                "API Base URL",
                value=st.session_state.api_url,
                help="FastAPI backend endpoint"
            )
            st.session_state.api_url = api_url
            
            if st.button("🔄 Reconnect", use_container_width=True):
                st.rerun()
            
            st.divider()
            
            # RAG Settings (only if RAG enabled)
            if st.session_state.enable_rag:
                st.markdown("**RAG Parameters**")
                top_k = st.slider(
                    "Top-K Documents",
                    min_value=5,
                    max_value=50,
                    value=15 if mode == "FAST" else 30,
                    step=5,
                    help="Number of documents to retrieve"
                )
                
                final_chunks = st.slider(
                    "Final Chunks",
                    min_value=1,
                    max_value=10,
                    value=3 if mode == "FAST" else 5,
                    help="Chunks after reranking"
                )
        
        st.divider()
        
        # ===== SYSTEM STATUS =====
        st.markdown("#### System Status")
        
        # Status indicators
        if st.session_state.api_health:
            st.success("✅ System Online", icon="🟢")
        else:
            st.error("❌ System Offline", icon="🔴")
        
        # Stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Queries", st.session_state.total_queries)
        with col2:
            st.metric("KB Docs", st.session_state.kb_stats.get("count", 0))
        
        st.divider()
        
        # ===== ABOUT =====
        with st.expander("ℹ️ About Teslas.ai", expanded=False):
            st.markdown("""
            **Teslas.ai** is a multi-agent scientific research assistant 
            powered by local LLM inference.
            
            **Target Users:**
            - Applied mathematics researchers
            - Data scientists
            - Engineers
            - Graduate students
            
            **Core Principles:**
            - Clarity & Rigor
            - Traceability
            - Performance Awareness
            - Reproducibility
            
            All processing is private and local.
            """)

# ============================================================================
# MAIN RESEARCH PANEL
# ============================================================================

def render_research_panel():
    """Render the main research question input panel."""
    st.markdown("## 🔬 Scientific Research Query")
    
    # Example queries based on mode
    if st.session_state.execution_mode == "FAST":
        placeholder = "Example: Analyze the stability of the explicit Euler method for y' = -ky..."
    else:
        placeholder = (
            "Example: Provide a comprehensive analysis of the Runge-Kutta 4th order method, "
            "including stability analysis, error bounds, and comparison with adaptive schemes..."
        )
    
    # Research question input
    research_query = st.text_area(
        "Research Question",
        placeholder=placeholder,
        height=150,
        help="Be specific and detailed. The system will analyze your query using multiple specialized agents.",
        key="research_input",
        label_visibility="collapsed"
    )
    
    # Query metadata display
    if research_query:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"📝 {len(research_query)} characters")
        with col2:
            tokens = estimate_tokens(research_query)
            st.caption(f"🪙 ~{tokens} tokens")
        with col3:
            st.caption(f"{get_mode_icon(st.session_state.execution_mode)} {st.session_state.execution_mode} mode")
    
    st.divider()
    
    # Action buttons
    col_btn, col_opts = st.columns([1, 2])
    
    with col_btn:
        run_button = st.button(
            "▶️ Run Analysis",
            use_container_width=True,
            type="primary",
            disabled=(not research_query or not st.session_state.api_health)
        )
    
    with col_opts:
        # Quick options
        opt_col1, opt_col2, opt_col3 = st.columns(3)
        with opt_col1:
            save_results = st.checkbox("💾 Save Results", value=True)
        with opt_col2:
            generate_latex = st.checkbox("📄 Generate LaTeX", value=True)
        with opt_col3:
            show_trace = st.checkbox("🧭 Show Trace", value=(st.session_state.execution_mode == "FULL"))
    
    # Execute research if button clicked
    if run_button and research_query:
        execute_research(research_query, save_results, generate_latex, show_trace)


# ============================================================================
# RESEARCH EXECUTION
# ============================================================================

def execute_research(query: str, save_results: bool, generate_latex: bool, show_trace: bool):
    """Execute research query and display results."""
    
    # Create progress container
    progress_container = st.container()
    
    with progress_container:
        st.info(f"🤖 Starting {st.session_state.execution_mode} mode analysis...", icon="⏳")
        
        # Progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            start_time = time.time()
            
            # Prepare request payload
            payload = {
                "query": query,
                "mode": st.session_state.execution_mode.lower(),
                "stream": False,
                "metadata": {
                    "enable_rag": st.session_state.enable_rag,
                    "enable_web_search": st.session_state.enable_web_search,
                    "enable_memory": st.session_state.enable_memory,
                    "generate_latex": generate_latex,
                }
            }
            
            # Update progress
            progress_bar.progress(20)
            status_text.text("⏳ Sending request to API...")
            
            # Send request
            resp = requests.post(
                f"{st.session_state.api_url}/research",
                json=payload,
                timeout=900  # 15 minutes max
            )
            
            progress_bar.progress(90)
            status_text.text("⏳ Processing results...")
            
            execution_time = time.time() - start_time
            
            if resp.status_code == 200:
                result = resp.json()
                
                # Update session state
                st.session_state.current_result = result
                st.session_state.last_query = query
                st.session_state.total_queries += 1
                
                # Add to history
                if save_results:
                    st.session_state.research_history.insert(0, {
                        "timestamp": datetime.now().isoformat(),
                        "query": query[:100],
                        "mode": st.session_state.execution_mode,
                        "execution_time": execution_time,
                        "status": result.get("status", "completed")
                    })
                
                # Complete progress
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                time.sleep(0.5)
                
                # Clear progress indicators
                progress_container.empty()
                
                # Display success metrics
                display_execution_metrics(execution_time, result)
                
                # Display results
                display_results(result, show_trace)
                
            else:
                st.error(f"❌ API Error {resp.status_code}: {resp.text[:300]}")
                progress_container.empty()
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Try a simpler query or switch to FAST mode.")
            progress_container.empty()
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Check that the backend is running.")
            progress_container.empty()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            progress_container.empty()


def display_execution_metrics(execution_time: float, result: Dict[str, Any]):
    """Display execution metrics after successful query."""
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Status</div>
            <div class="metric-value">✅</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Execution Time</div>
            <div class="metric-value">{format_execution_time(execution_time)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        mode_display = result.get("mode", st.session_state.execution_mode).upper()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Mode</div>
            <div class="metric-value">{mode_display}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        agents_used = len(result.get("execution_path", []))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Agents</div>
            <div class="metric-value">{agents_used}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()


# ============================================================================
# RESULTS DISPLAY - TABBED LAYOUT
# ============================================================================

def display_results(result: Dict[str, Any], show_trace: bool):
    """Display research results in organized tabbed layout."""
    
    # Determine which tabs to show based on mode and content
    mode = st.session_state.execution_mode
    
    # Base tabs always shown
    tab_names = ["🧠 Summary", "📐 Mathematical Analysis"]
    
    # Add conditional tabs based on content
    if result.get("numerical_results"):
        tab_names.append("🔢 Numerical Results")
    
    if result.get("literature_sources"):
        tab_names.append("📚 Literature & Sources")
    
    if result.get("criticisms") or result.get("improvements"):
        tab_names.append("🧪 Review & Improvements")
    
    if result.get("latex_document"):
        tab_names.append("📄 LaTeX / Report")
    
    if show_trace or mode == "FULL":
        tab_names.append("🧭 Execution Trace")
    
    # Always show performance metrics
    tab_names.append("📊 Performance Metrics")
    
    # Create tabs
    tabs = st.tabs(tab_names)
    tab_idx = 0
    
    # ===== TAB: SUMMARY =====
    with tabs[tab_idx]:
        render_summary_tab(result)
    tab_idx += 1
    
    # ===== TAB: MATHEMATICAL ANALYSIS =====
    with tabs[tab_idx]:
        render_mathematical_tab(result)
    tab_idx += 1
    
    # ===== TAB: NUMERICAL RESULTS (conditional) =====
    if "🔢 Numerical Results" in tab_names:
        with tabs[tab_idx]:
            render_numerical_tab(result)
        tab_idx += 1
    
    # ===== TAB: LITERATURE (conditional) =====
    if "📚 Literature & Sources" in tab_names:
        with tabs[tab_idx]:
            render_literature_tab(result)
        tab_idx += 1
    
    # ===== TAB: REVIEW (conditional) =====
    if "🧪 Review & Improvements" in tab_names:
        with tabs[tab_idx]:
            render_review_tab(result)
        tab_idx += 1
    
    # ===== TAB: LATEX (conditional) =====
    if "📄 LaTeX / Report" in tab_names:
        with tabs[tab_idx]:
            render_latex_tab(result)
        tab_idx += 1
    
    # ===== TAB: EXECUTION TRACE (conditional) =====
    if show_trace or mode == "FULL":
        with tabs[tab_idx]:
            render_trace_tab(result)
        tab_idx += 1
    
    # ===== TAB: PERFORMANCE METRICS (always) =====
    with tabs[tab_idx]:
        render_performance_tab(result)


def render_summary_tab(result: Dict[str, Any]):
    """Render executive summary tab."""
    st.markdown("### Executive Summary")
    
    summary = result.get("summary", "")
    if summary:
        st.markdown(summary)
    else:
        st.info("No summary generated.", icon="ℹ️")
    
    # Key insights (if available)
    insights = result.get("mathematical_insights", [])
    if insights and len(insights) > 0:
        st.markdown("### Key Insights")
        for idx, insight in enumerate(insights[:3], 1):  # Top 3 insights
            st.info(f"**{idx}.** {insight}", icon="💡")


def render_mathematical_tab(result: Dict[str, Any]):
    """Render mathematical analysis tab."""
    st.markdown("### Mathematical Analysis")
    
    insights = result.get("mathematical_insights", [])
    equations = result.get("final_equations", [])
    
    if insights:
        st.markdown("#### Insights")
        for idx, insight in enumerate(insights, 1):
            with st.expander(f"Insight {idx}", expanded=(idx <= 2)):
                st.write(insight)
    
    if equations:
        st.markdown("#### Key Equations")
        for idx, eq in enumerate(equations, 1):
            st.latex(eq)
    
    if not insights and not equations:
        st.info("No mathematical analysis generated.", icon="ℹ️")


def render_numerical_tab(result: Dict[str, Any]):
    """Render numerical results tab."""
    st.markdown("### Numerical Results")
    
    numerical = result.get("numerical_results", {})
    
    if numerical:
        # Display as metrics if possible
        if isinstance(numerical, dict):
            cols = st.columns(min(len(numerical), 3))
            for idx, (key, value) in enumerate(numerical.items()):
                with cols[idx % len(cols)]:
                    st.metric(key, value)
        else:
            st.json(numerical)
    else:
        st.info("No numerical results generated.", icon="ℹ️")


def render_literature_tab(result: Dict[str, Any]):
    """Render literature sources tab."""
    st.markdown("### Literature & Sources")
    
    sources = result.get("literature_sources", [])
    
    if sources:
        for idx, source in enumerate(sources, 1):
            with st.expander(f"📖 Source {idx}: {source.get('title', 'Untitled')[:80]}", expanded=False):
                st.markdown(f"**Title:** {source.get('title', 'N/A')}")
                
                if source.get('authors'):
                    st.markdown(f"**Authors:** {source.get('authors')}")
                
                if source.get('url'):
                    st.markdown(f"**URL:** [{source.get('url')}]({source.get('url')})")
                
                if source.get('summary'):
                    st.markdown(f"**Summary:** {source.get('summary')}")
    else:
        st.info("No literature sources found.", icon="ℹ️")


def render_review_tab(result: Dict[str, Any]):
    """Render criticisms and improvements tab."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Criticisms")
        criticisms = result.get("criticisms", [])
        
        if criticisms:
            for idx, crit in enumerate(criticisms, 1):
                st.warning(f"**{idx}.** {crit}", icon="⚠️")
        else:
            st.success("✅ No critical issues identified", icon="✅")
    
    with col2:
        st.markdown("### 💡 Improvements")
        improvements = result.get("improvements", [])
        
        if improvements:
            for idx, imp in enumerate(improvements, 1):
                st.info(f"**{idx}.** {imp}", icon="💡")
        else:
            st.success("✅ Analysis is optimal", icon="✅")


def render_latex_tab(result: Dict[str, Any]):
    """Render LaTeX document tab with export options."""
    st.markdown("### LaTeX Report")
    
    latex_doc = result.get("latex_document", "")
    
    if latex_doc:
        st.code(latex_doc, language="latex")
        
        # Export options
        col1, col2 = st.columns([1, 3])
        
        with col1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="⬇️ Download .tex",
                data=latex_doc,
                file_name=f"teslas_research_{timestamp}.tex",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            st.caption("💡 Compile with pdflatex or your preferred LaTeX distribution")
    else:
        st.info("LaTeX document not generated. Enable LaTeX generation in options.", icon="ℹ️")


def render_trace_tab(result: Dict[str, Any]):
    """Render execution trace tab (for advanced users)."""
    st.markdown("### Execution Trace")
    
    execution_path = result.get("execution_path", [])
    errors = result.get("errors", [])
    
    if execution_path:
        st.markdown("#### Agent Execution Order")
        for idx, agent in enumerate(execution_path, 1):
            st.code(f"{idx}. {agent}", language="text")
    
    if errors:
        st.markdown("#### Errors & Warnings")
        for error in errors:
            st.error(error, icon="⚠️")
    
    # Raw result JSON
    with st.expander("🔍 Raw JSON Response", expanded=False):
        st.json(result)


def render_performance_tab(result: Dict[str, Any]):
    """Render performance metrics tab."""
    st.markdown("### Performance Metrics")
    
    # Extract timing information if available
    metadata = result.get("metadata", {})
    timing = metadata.get("timing", {})
    
    if timing:
        st.markdown("#### Execution Breakdown")
        
        # Create performance table
        st.markdown("""
        <table class="perf-table">
            <thead>
                <tr>
                    <th>Stage</th>
                    <th>Time</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
        """, unsafe_allow_html=True)
        
        total_time = sum(timing.values())
        for stage, time_val in timing.items():
            percentage = (time_val / total_time * 100) if total_time > 0 else 0
            st.markdown(f"""
                <tr>
                    <td>{stage.replace('_', ' ').title()}</td>
                    <td>{format_execution_time(time_val)}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            """, unsafe_allow_html=True)
        
        st.markdown("</tbody></table>", unsafe_allow_html=True)
    
    # System information
    st.markdown("#### System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Mode", result.get("mode", "unknown").upper())
    
    with col2:
        st.metric("Agents Used", len(result.get("execution_path", [])))
    
    with col3:
        st.metric("Status", result.get("status", "unknown").upper())
    
    # Export options
    st.divider()
    st.markdown("#### Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export as JSON
        json_data = json.dumps(result, indent=2)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"teslas_results_{timestamp}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Export as Markdown
        md_data = export_as_markdown(result)
        st.download_button(
            label="📥 Download Markdown",
            data=md_data,
            file_name=f"teslas_results_{timestamp}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col3:
        # Export as Text
        text_data = export_as_text(result)
        st.download_button(
            label="📥 Download TXT",
            data=text_data,
            file_name=f"teslas_results_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True
        )


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_as_markdown(result: Dict[str, Any]) -> str:
    """Export research results as Markdown."""
    query = result.get("query", "N/A")
    mode = result.get("mode", "unknown").upper()
    status = result.get("status", "unknown")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md = f"""# Teslas.ai Research Report

**Generated:** {timestamp}
**Mode:** {mode}
**Status:** {status}

---

## Query

{query}

---

## Summary

{result.get('summary', 'No summary available.')}

---

## Mathematical Insights

"""
    
    insights = result.get('mathematical_insights', [])
    if insights:
        for idx, insight in enumerate(insights, 1):
            md += f"{idx}. {insight}\n"
    else:
        md += "No mathematical insights generated.\n"
    
    md += "\n---\n\n## Equations\n\n"
    
    equations = result.get('final_equations', [])
    if equations:
        for eq in equations:
            md += f"$$\n{eq}\n$$\n\n"
    else:
        md += "No equations generated.\n"
    
    md += "\n---\n\n## Numerical Results\n\n"
    
    numerical = result.get('numerical_results', {})
    if numerical:
        md += f"```json\n{json.dumps(numerical, indent=2)}\n```\n"
    else:
        md += "No numerical results.\n"
    
    md += "\n---\n\n## Literature Sources\n\n"
    
    sources = result.get('literature_sources', [])
    if sources:
        for idx, source in enumerate(sources, 1):
            md += f"{idx}. **{source.get('title', 'Untitled')}**\n"
            if source.get('authors'):
                md += f"   - Authors: {source.get('authors')}\n"
            if source.get('url'):
                md += f"   - URL: {source.get('url')}\n"
            md += "\n"
    else:
        md += "No literature sources found.\n"
    
    md += "\n---\n\n## Execution Path\n\n"
    
    execution_path = result.get('execution_path', [])
    if execution_path:
        for idx, agent in enumerate(execution_path, 1):
            md += f"{idx}. {agent}\n"
    else:
        md += "No execution path recorded.\n"
    
    md += "\n---\n\n*Generated by Teslas.ai Scientific Research Assistant*\n"
    
    return md


def export_as_text(result: Dict[str, Any]) -> str:
    """Export research results as plain text."""
    query = result.get("query", "N/A")
    mode = result.get("mode", "unknown").upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    text = f"""
================================================================================
TESLAS.AI RESEARCH REPORT
================================================================================

Generated: {timestamp}
Mode: {mode}
Status: {result.get('status', 'unknown')}

================================================================================
QUERY
================================================================================

{query}

================================================================================
SUMMARY
================================================================================

{result.get('summary', 'No summary available.')}

================================================================================
MATHEMATICAL INSIGHTS
================================================================================

"""
    
    insights = result.get('mathematical_insights', [])
    if insights:
        for idx, insight in enumerate(insights, 1):
            text += f"{idx}. {insight}\n\n"
    else:
        text += "No mathematical insights generated.\n\n"
    
    text += """
================================================================================
NUMERICAL RESULTS
================================================================================

"""
    
    numerical = result.get('numerical_results', {})
    if numerical:
        text += json.dumps(numerical, indent=2) + "\n\n"
    else:
        text += "No numerical results.\n\n"
    
    text += """
================================================================================
LITERATURE SOURCES
================================================================================

"""
    
    sources = result.get('literature_sources', [])
    if sources:
        for idx, source in enumerate(sources, 1):
            text += f"{idx}. {source.get('title', 'Untitled')}\n"
            if source.get('authors'):
                text += f"   Authors: {source.get('authors')}\n"
            if source.get('url'):
                text += f"   URL: {source.get('url')}\n"
            text += "\n"
    else:
        text += "No literature sources found.\n\n"
    
    text += """
================================================================================
EXECUTION PATH
================================================================================

"""
    
    execution_path = result.get('execution_path', [])
    if execution_path:
        for idx, agent in enumerate(execution_path, 1):
            text += f"{idx}. {agent}\n"
    else:
        text += "No execution path recorded.\n"
    
    text += "\n================================================================================\n"
    text += "Generated by Teslas.ai Scientific Research Assistant\n"
    text += "================================================================================\n"
    
    return text


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    render_research_panel()
    
    # Footer
    st.divider()
    st.caption("🔬 Teslas.ai - Scientific Research Assistant | Local GenAI Inference | All processing is private and secure")


if __name__ == "__main__":
    main()
