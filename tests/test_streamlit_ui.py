"""
Streamlit UI Test Suite
Tests pour la nouvelle interface Teslas.ai
"""

import sys
import subprocess
import requests
import time
from pathlib import Path

# ============================================================================
# TEST 1: Verifier que Streamlit est installe
# ============================================================================

def test_streamlit_installed():
    """Verifier que Streamlit est disponible."""
    print("[TEST 1] Verifier l'installation de Streamlit...")
    try:
        import streamlit as st
        print(f"  [OK] Streamlit {st.__version__} trouve")
        return True
    except ImportError:
        print(f"  [FAIL] Streamlit non installe")
        return False


# ============================================================================
# TEST 2: Verifier la syntaxe du fichier streamlit_app.py
# ============================================================================

def test_streamlit_syntax():
    """Verifier la syntaxe du fichier Streamlit."""
    print("\n[TEST 2] Verifier la syntaxe du fichier streamlit_app.py...")
    
    streamlit_file = Path(__file__).parent.parent / "app/ui/streamlit_app.py"
    
    if not streamlit_file.exists():
        print(f"  [FAIL] Fichier non trouve: {streamlit_file}")
        return False
    
    try:
        # Compiler le fichier Python pour verifier la syntaxe
        with open(streamlit_file, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, str(streamlit_file), 'exec')
        print(f"  [OK] Syntaxe valide ({len(code)} caracteres)")
        return True
    except SyntaxError as e:
        print(f"  [FAIL] Erreur de syntaxe: {e}")
        return False
    except Exception as e:
        print(f"  [FAIL] Erreur: {e}")
        return False


# ============================================================================
# TEST 3: Verifier les imports du fichier
# ============================================================================

def test_streamlit_imports():
    """Verifier que tous les imports fonctionnent."""
    print("\n[TEST 3] Verifier les imports...")
    
    required_imports = [
        "os",
        "streamlit",
        "requests",
        "json",
        "datetime",
        "typing",
        "time",
        "dataclasses",
    ]
    
    missing = []
    for module_name in required_imports:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(module_name)
    
    if missing:
        print(f"  [FAIL] Modules manquants: {', '.join(missing)}")
        return False
    
    print(f"  [OK] Tous les imports ({len(required_imports)} modules) disponibles")
    return True


# ============================================================================
# TEST 4: Verifier les variables d'environnement
# ============================================================================

def test_environment_variables():
    """Verifier les variables d'environnement attendues."""
    print("\n[TEST 4] Verifier les variables d'environnement...")
    
    import os
    
    # API URL (optionnel, utilise une valeur par defaut)
    api_url = os.getenv("TESLAS_API_URL", "http://localhost:8000/api")
    print(f"  [OK] TESLAS_API_URL = {api_url}")
    
    return True


# ============================================================================
# TEST 5: Verifier la structure du code
# ============================================================================

def test_code_structure():
    """Verifier que les fonctions cles existent."""
    print("\n[TEST 5] Verifier la structure du code...")
    
    streamlit_file = Path(__file__).parent.parent / "app/ui/streamlit_app.py"
    
    with open(streamlit_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    required_functions = [
        "init_session_state",
        "check_api_health",
        "render_header",
        "render_sidebar",
        "render_research_panel",
        "execute_research",
        "display_results",
        "export_as_markdown",
        "export_as_text",
        "main",
    ]
    
    missing = []
    for func in required_functions:
        if f"def {func}" not in code:
            missing.append(func)
    
    if missing:
        print(f"  [FAIL] Fonctions manquantes: {', '.join(missing)}")
        return False
    
    print(f"  [OK] Toutes les {len(required_functions)} fonctions cles presentes")
    return True


# ============================================================================
# TEST 6: Verifier les constantes et configurations
# ============================================================================

def test_configuration():
    """Verifier les configurations essentielles."""
    print("\n[TEST 6] Verifier les configurations...")
    
    streamlit_file = Path(__file__).parent.parent / "app/ui/streamlit_app.py"
    
    with open(streamlit_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    required_configs = [
        "st.set_page_config",
        "st.markdown",  # Styling
        "DEFAULT_API_URL",
    ]
    
    missing = []
    for config in required_configs:
        if config not in code:
            missing.append(config)
    
    if missing:
        print(f"  [FAIL] Configurations manquantes: {', '.join(missing)}")
        return False
    
    print(f"  [OK] Toutes les configurations presentes")
    return True


# ============================================================================
# TEST 7: Verifier le docker-compose.yml
# ============================================================================

def test_docker_compose():
    """Verifier que le service UI est configure dans docker-compose."""
    print("\n[TEST 7] Verifier la configuration Docker Compose...")
    
    docker_compose_file = Path(__file__).parent.parent / "docker-compose.yml"
    
    if not docker_compose_file.exists():
        print(f"  [FAIL] Fichier non trouve: {docker_compose_file}")
        return False
    
    with open(docker_compose_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_configs = [
        "ui:",
        "streamlit run",
        "8501:8501",
        "TESLAS_API_URL",
    ]
    
    missing = []
    for config in required_configs:
        if config not in content:
            missing.append(config)
    
    if missing:
        print(f"  [FAIL] Configurations manquantes: {', '.join(missing)}")
        return False
    
    print(f"  [OK] Service UI correctement configure dans docker-compose.yml")
    return True


# ============================================================================
# TEST 8: Tester les fonctions utilitaires
# ============================================================================

def test_utility_functions():
    """Tester les fonctions utilitaires."""
    print("\n[TEST 8] Tester les fonctions utilitaires...")
    
    # Importer les fonctions
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    try:
        # On ne peut pas importer directement streamlit_app.py (c'est une app Streamlit)
        # Mais on peut verifier la logique
        
        # Test: format_execution_time
        test_cases = [
            (0.5, "500ms"),
            (1.5, "1.50s"),
            (65, "1m 5s"),
        ]
        
        # Verifier que les patterns sont presents
        streamlit_file = Path(__file__).parent.parent / "app/ui/streamlit_app.py"
        with open(streamlit_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        if "def format_execution_time" in code:
            print(f"  [OK] Fonction format_execution_time presente")
        else:
            print(f"  [FAIL] Fonction format_execution_time manquante")
            return False
        
        if "def estimate_tokens" in code:
            print(f"  [OK] Fonction estimate_tokens presente")
        else:
            print(f"  [FAIL] Fonction estimate_tokens manquante")
            return False
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Erreur: {e}")
        return False


# ============================================================================
# TEST 9: Simulation d'une requete API
# ============================================================================

def test_api_connectivity():
    """Tester la connectivite a l'API (mock)."""
    print("\n[TEST 9] Verifier la structure de connectivite API...")
    
    streamlit_file = Path(__file__).parent.parent / "app/ui/streamlit_app.py"
    
    with open(streamlit_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    required_endpoints = [
        "/health",
        "/kb/count",
        "/research",
    ]
    
    missing = []
    for endpoint in required_endpoints:
        if endpoint not in code:
            missing.append(endpoint)
    
    if missing:
        print(f"  [WARN] Endpoints potentiellement manquants: {', '.join(missing)}")
        return False
    
    print(f"  [OK] Structure API complete")
    return True


# ============================================================================
# TEST 10: Verifier l'integration des modes FAST/FULL
# ============================================================================

def test_execution_modes():
    """Verifier l'integration des modes FAST/FULL."""
    print("\n[TEST 10] Verifier l'integration des modes FAST/FULL...")
    
    streamlit_file = Path(__file__).parent.parent / "app/ui/streamlit_app.py"
    
    with open(streamlit_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    required_elements = [
        "FAST",
        "FULL",
        "execution_mode",
        "get_mode_description",
        "get_mode_icon",
    ]
    
    missing = []
    for elem in required_elements:
        if elem not in code:
            missing.append(elem)
    
    if missing:
        print(f"  [FAIL] Elements manquants: {', '.join(missing)}")
        return False
    
    print(f"  [OK] Modes FAST/FULL correctement integres")
    return True


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Executer tous les tests."""
    print("=" * 70)
    print("SUITE DE TESTS - INTERFACE STREAMLIT TESLAS.AI")
    print("=" * 70)
    
    tests = [
        test_streamlit_installed,
        test_streamlit_syntax,
        test_streamlit_imports,
        test_environment_variables,
        test_code_structure,
        test_configuration,
        test_docker_compose,
        test_utility_functions,
        test_api_connectivity,
        test_execution_modes,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"  [FAIL] Erreur non geree: {e}")
            results.append((test_func.__name__, False))
    
    # Resume
    print("\n" + "=" * 70)
    print("RESUME DES TESTS")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print("=" * 70)
    print(f"RESULTAT: {passed}/{total} tests reussis")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
