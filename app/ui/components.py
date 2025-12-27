"""Streamlit UI components for Teslas.ai."""

import streamlit as st
from typing import Optional, List


def render_header():
    """Render application header."""
    st.set_page_config(
        page_title="Teslas.ai - Scientific Assistant",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://raw.githubusercontent.com/Geobatpo07/scientific-assistant/main/assets/tesla_icon.png" if False else "⚡", width=60)
    with col2:
        st.markdown("# ⚡ Tesla - Multi-Agent Scientific Assistant")
        st.markdown("*Rigorous AI-powered research for mathematics, numerical methods, and data science*")
    
    st.divider()


def render_sidebar():
    """Render sidebar with options."""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Model selection
        st.markdown("### LLM Settings")
        model = st.selectbox(
            "Ollama Model",
            ["mistral", "neural-chat", "dolphin-mixtral", "llama2"],
            help="Select the local LLM to use"
        )
        
        temperature = st.slider(
            "Temperature",
            0.0, 1.0, 0.3,
            help="Lower = more deterministic, Higher = more creative"
        )
        
        # Agent selection
        st.markdown("### Agent Selection")
        agents = st.multiselect(
            "Agents to Use",
            ["planner", "mathematician", "numerical", "data_scientist", 
             "literature", "reviewer", "writer", "memory"],
            default=["planner", "mathematician", "reviewer", "writer"],
            help="Select which agents to include in the workflow"
        )
        
        # RAG settings
        st.markdown("### RAG Settings")
        top_k = st.slider("Top-K Retrieval", 1, 20, 5)
        rerank = st.checkbox("Enable Re-ranking", value=True)
        
        st.divider()
        
        # Info
        st.markdown("### About Tesla")
        st.info(
            "Tesla is a local multi-agent scientific assistant "
            "designed for researchers in mathematics, numerical methods, "
            "and data science. All computation runs locally using Ollama."
        )
        
        return {
            "model": model,
            "temperature": temperature,
            "agents": agents,
            "top_k": top_k,
            "rerank": rerank,
        }


def render_research_tab():
    """Render research tab."""
    st.markdown("## 🔬 Scientific Research")
    
    # Research query input
    query = st.text_area(
        "Research Question",
        placeholder="Enter your research question or mathematical problem...",
        height=100,
        help="Be specific and detailed for better results"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        run_button = st.button("▶️ Run Research", use_container_width=True)
    with col2:
        st.empty()
    
    return query, run_button


def render_search_tab():
    """Render search tab."""
    st.markdown("## 🔍 Scientific Literature Search")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Search Query",
            placeholder="Search for papers, concepts, or methodologies..."
        )
    with col2:
        search_type = st.selectbox(
            "Source",
            ["scientific", "arxiv", "scholar", "code"]
        )
    
    search_button = st.button("🔎 Search", use_container_width=False)
    
    return search_query, search_type, search_button


def render_ingest_tab():
    """Render document ingestion tab."""
    st.markdown("## 📄 Document Ingestion")
    
    st.info(
        "Upload scientific papers or documents to build your personal knowledge base. "
        "Supported formats: PDF, TXT, MD"
    )
    
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "txt", "md", "docx"],
        help="PDF, text, or markdown files"
    )
    
    ingest_button = st.button("⬆️ Ingest Document", use_container_width=True)
    
    return uploaded_file, ingest_button


def render_results(result: dict):
    """Render research results."""
    if not result:
        return
    
    # Tabs for different result sections
    tabs = st.tabs([
        "📋 Summary",
        "📐 Mathematics",
        "🧮 Numerical",
        "📊 Data",
        "📚 Literature",
        "✅ Review",
        "🔖 LaTeX",
    ])
    
    # Summary tab
    with tabs[0]:
        st.markdown("### Research Summary")
        st.markdown(result.get("summary", "No summary available"))
    
    # Mathematical insights
    with tabs[1]:
        st.markdown("### Mathematical Insights")
        for insight in result.get("mathematical_insights", [])[:3]:
            st.markdown(f"- {insight}")
        
        if result.get("final_equations"):
            st.markdown("### Key Equations")
            for eq in result.get("final_equations", [])[:5]:
                st.latex(eq)
    
    # Numerical results
    with tabs[2]:
        st.markdown("### Numerical Results")
        for key, value in list(result.get("numerical_results", {}).items())[:5]:
            st.write(f"**{key}**: {value}")
    
    # Data analysis
    with tabs[3]:
        st.markdown("### Data Analysis")
        for key, value in list(result.get("data_analysis", {}).items())[:5]:
            st.write(f"**{key}**: {value}")
    
    # Literature
    with tabs[4]:
        st.markdown("### Literature Sources")
        for source in result.get("literature_sources", [])[:10]:
            st.write(f"**{source.get('title', 'N/A')}**")
            st.caption(source.get('url', 'N/A'))
    
    # Review
    with tabs[5]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Criticisms")
            for crit in result.get("criticisms", []):
                st.warning(crit)
        with col2:
            st.markdown("### Improvements")
            for imp in result.get("improvements", []):
                st.info(imp)
    
    # LaTeX
    with tabs[6]:
        if result.get("latex_document"):
            st.markdown("### LaTeX Document")
            st.code(result.get("latex_document"), language="latex")
            st.download_button(
                "📥 Download LaTeX",
                result.get("latex_document"),
                "research.tex",
                "text/plain",
            )
    
    # Execution info
    st.divider()
    st.markdown("### Execution Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Agents Used", len(result.get("execution_path", [])))
    with col2:
        st.metric("Errors", len(result.get("errors", [])))
    with col3:
        st.metric("Equations Generated", len(result.get("final_equations", [])))
    
    if result.get("errors"):
        st.warning("⚠️ Errors encountered:")
        for error in result.get("errors", []):
            st.write(f"- {error}")
