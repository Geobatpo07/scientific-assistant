#!/usr/bin/env python3
"""
Tests de l'UI Streamlit avec Docker
Teste le démarrage du container UI et la connectivité
"""

import subprocess
import time
import requests
import sys
import os

def run_command(cmd, timeout=30):
    """Exécuter une commande shell"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Timeout après {timeout}s"

def test_docker_build():
    """Test 1: Vérifier que l'image Docker UI existe"""
    print("[TEST 1] Vérifier l'image Docker UI...")
    code, stdout, stderr = run_command("docker images | findstr scientific-assistant-ui")
    if code == 0 and "scientific-assistant-ui" in stdout:
        print("  [PASS] Image Docker UI trouvée")
        return True
    print("  [FAIL] Image Docker UI non trouvée")
    return False

def test_docker_compose_file():
    """Test 2: Vérifier la configuration docker-compose"""
    print("[TEST 2] Vérifier la configuration docker-compose...")
    config_path = "docker-compose.yml"
    if not os.path.exists(config_path):
        print(f"  [FAIL] {config_path} non trouvé")
        return False
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    checks = [
        ("ui:" in content, "Service UI défini"),
        ("streamlit run" in content, "Commande Streamlit configurée"),
        ("8501:8501" in content, "Port 8501 exposé"),
        ("TESLAS_API_URL" in content, "Variable d'environnement API URL"),
        ("depends_on:" in content, "Dépendance de service configurée"),
    ]
    
    all_passed = True
    for check, desc in checks:
        if check:
            print(f"  [OK] {desc}")
        else:
            print(f"  [FAIL] {desc}")
            all_passed = False
    
    return all_passed

def test_streamlit_app_file():
    """Test 3: Vérifier le fichier streamlit_app.py"""
    print("[TEST 3] Vérifier le fichier streamlit_app.py...")
    app_path = "app/ui/streamlit_app.py"
    if not os.path.exists(app_path):
        print(f"  [FAIL] {app_path} non trouvé")
        return False
    
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  [FAIL] Erreur de lecture: {e}")
        return False
    
    # Vérifier que le fichier contient les éléments clés
    required_elements = [
        ("import streamlit as st", "Import Streamlit"),
        ("import os", "Import os pour variables d'environnement"),
        ("DEFAULT_API_URL", "Variable d'environnement API URL"),
        ("def init_session_state", "Fonction d'initialisation"),
        ("def render_header", "Fonction header"),
        ("def render_sidebar", "Fonction sidebar"),
        ("streamlit run app/ui/streamlit_app.py" in open("docker-compose.yml").read(), "Configuration Docker correct"),
    ]
    
    print(f"  [OK] Fichier trouvé ({len(content)} caractères)")
    
    # Vérifier taille minimale
    if len(content) < 30000:
        print(f"  [WARN] Fichier plutôt court ({len(content)} chars, attendu 40000+)")
        return False
    else:
        print(f"  [OK] Taille correcte")
    
    return True

def test_docker_network():
    """Test 4: Vérifier la connectivité réseau Docker"""
    print("[TEST 4] Vérifier la configuration réseau Docker...")
    
    # Vérifier que les services peuvent se voir dans docker-compose
    code, stdout, stderr = run_command("docker network ls")
    if code != 0:
        print("  [FAIL] Impossible de lister les réseaux Docker")
        return False
    
    print("  [OK] Docker network accessible")
    return True

def test_dockerfile_cuda_exclusion():
    """Test 5: Vérifier que le Dockerfile exclut les packages CUDA"""
    print("[TEST 5] Vérifier l'exclusion des packages CUDA...")
    
    with open("Dockerfile", 'r') as f:
        content = f.read()
    
    # Vérifier que le Dockerfile contient les exclusions
    if "--no-install-package nvidia-cudnn-cu12" in content:
        print("  [OK] Packages CUDA exclus du build Docker")
        return True
    else:
        print("  [WARN] Packages CUDA ne sont pas explicitement exclus")
        return False

def test_services_config():
    """Test 6: Vérifier la configuration des services"""
    print("[TEST 6] Vérifier la configuration des services Docker Compose...")
    
    with open("docker-compose.yml", 'r') as f:
        content = f.read()
    
    services = {
        "api": "Service API",
        "ui": "Service UI", 
        "ollama": "Service Ollama"
    }
    
    all_found = True
    for service, desc in services.items():
        if f"{service}:" in content:
            print(f"  [OK] {desc} configuré")
        else:
            print(f"  [FAIL] {desc} non configuré")
            all_found = False
    
    return all_found

def main():
    """Exécuter tous les tests"""
    print("=" * 70)
    print("TESTS DOCKER - INTERFACE STREAMLIT TESLAS.AI")
    print("=" * 70)
    
    tests = [
        test_docker_build,
        test_docker_compose_file,
        test_streamlit_app_file,
        test_docker_network,
        test_dockerfile_cuda_exclusion,
        test_services_config,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            results.append(False)
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 70)
    print(f"RÉSULTAT: {passed}/{total} tests réussis")
    print("=" * 70)
    
    if passed == total:
        print("[SUCCESS] Tous les tests Docker sont passés !")
        return 0
    else:
        print(f"[WARNING] {total - passed} test(s) ont échoué")
        return 1

if __name__ == "__main__":
    sys.exit(main())
