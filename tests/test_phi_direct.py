#!/usr/bin/env python
"""Test direct Ollama connection with phi model."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# First, clear any cached LLM instances
if 'app.llm.ollama' in sys.modules:
    del sys.modules['app.llm.ollama']

# Import and configure
from app.config import settings

# Ensure we're using phi
print(f"Current OLLAMA_MODEL setting: {settings.OLLAMA_MODEL}")

# Test direct curl command
import subprocess
result = subprocess.run([
    "docker", "exec", "teslas_ollama", "curl", "-X", "POST",
    "http://localhost:11434/api/generate",
    "-d", '{"model": "phi", "prompt": "What is 2+2?", "stream": false}'
], capture_output=True, text=True)

print(f"Direct curl test: {result.returncode}")
if result.returncode == 0:
    print(f"Response: {result.stdout[:200]}")
else:
    print(f"Error: {result.stderr}")

# Now test with LangChain
print("\nTesting with LangChain...")

try:
    from langchain_community.chat_models import ChatOllama
    
    llm = ChatOllama(
        model="phi",
        base_url="http://127.0.0.1:11434",
        temperature=0.3,
    )
    
    response = llm.invoke("What is 2+2? Answer briefly.")
    print(f"LangChain response: {response.content[:100]}")
    
except Exception as e:
    print(f"LangChain error: {e}")
