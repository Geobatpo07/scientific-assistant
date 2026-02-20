"""Script to run Teslas.ai locally."""

import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.logger import setup_logging, get_logger
from app.config import settings

setup_logging()
logger = get_logger(__name__)


def check_ollama():
    """Check if Ollama is running."""
    import requests
    
    try:
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
        logger.info("✅ Ollama is running", url=settings.OLLAMA_BASE_URL)
        return True
    except requests.exceptions.ConnectionError:
        logger.warning("⚠ Ollama is not running - using fallback mode", url=settings.OLLAMA_BASE_URL)
        logger.info("For full functionality, start Ollama with: ollama serve")
        return False


def run_api():
    """Run API server."""
    logger.info("Starting FastAPI server...")
    subprocess.run([
        "uv", "run", "uvicorn",
        "app.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload",
    ])


def run_ui():
    """Run Streamlit UI."""
    logger.info("Starting Streamlit UI...")
    
    subprocess.run([
        "uv", "run", "streamlit", "run",
        str(Path(__file__).parent.parent / "app" / "ui" / "streamlit_app.py"),
        "--theme.base", "dark",
    ])


def main():
    """Main launcher."""
    import threading
    
    logger.info("🚀 Teslas.ai Scientific Assistant")
    logger.info("================================")
    
    # Check prerequisites (but don't exit if Ollama unavailable)
    ollama_available = check_ollama()
    if not ollama_available:
        logger.info("💡 Running in FALLBACK MODE - Limited functionality")
        logger.info("   Install and run Ollama for full LLM capabilities: ollama serve")
    
    logger.info("Starting Teslas.ai...")
    logger.info("")
    logger.info("🔵 API Server: http://localhost:8000")
    logger.info("🟢 UI: http://localhost:8501")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    
    try:
        # Start API in background thread
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        
        # Give API time to start
        time.sleep(3)
        
        # Start UI in main thread (blocking)
        run_ui()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
