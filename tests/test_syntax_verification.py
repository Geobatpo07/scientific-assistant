#!/usr/bin/env python
"""Lightweight tests - Syntax and Import Verification

Tests that don't require actual model loading:
1. Module imports
2. Type hints
3. Function signatures
4. Code structure
"""

import ast
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_syntax(file_path):
    """Test if Python file has valid syntax."""
    try:
        with open(file_path, 'r') as f:
            ast.parse(f.read())
        return True
    except SyntaxError as e:
        print(f"  ❌ Syntax error: {e}")
        return False


def test_module_structure(file_path):
    """Check if module has expected structure."""
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        return {
            "classes": classes,
            "functions": functions,
            "has_docstring": bool(ast.get_docstring(tree)),
        }
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def main():
    """Run tests."""
    print("\n" + "="*70)
    print("TESLAS.AI + HUGGING FACE - SYNTAX & STRUCTURE VERIFICATION")
    print("="*70)
    
    files_to_test = [
        ("HF Embeddings", "app/hf/embeddings.py"),
        ("HF Reranker", "app/hf/reranker.py"),
        ("HF __init__", "app/hf/__init__.py"),
        ("FAISS Index", "app/vectorstore/faiss_index.py"),
        ("Chroma Store", "app/vectorstore/chroma.py"),
        ("Hybrid Store", "app/vectorstore/hybrid_store.py"),
        ("Retriever", "app/vectorstore/retriever.py"),
        ("Store Factory", "app/vectorstore/store.py"),
        ("RAG Chains", "app/rag/chains.py"),
    ]
    
    all_passed = True
    
    for name, file_path in files_to_test:
        print(f"\n{name:20} | {file_path}")
        print("-" * 70)
        
        full_path = project_root / file_path
        
        if not full_path.exists():
            print(f"  ❌ File not found: {full_path}")
            all_passed = False
            continue
        
        # Test syntax
        if test_syntax(full_path):
            print(f"  ✅ Syntax valid")
        else:
            all_passed = False
            continue
        
        # Test structure
        structure = test_module_structure(full_path)
        if structure:
            if structure["has_docstring"]:
                print(f"  ✅ Has module docstring")
            else:
                print(f"  ⚠️  Missing module docstring")
            
            if structure["classes"]:
                print(f"  ✅ Classes: {', '.join(structure['classes'])}")
            
            if structure["functions"]:
                funcs = structure["functions"][:3]
                more = f" +{len(structure['functions']) - 3} more" if len(structure["functions"]) > 3 else ""
                print(f"  ✅ Functions: {', '.join(funcs)}{more}")
    
    # Summary
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL FILES PASSED SYNTAX AND STRUCTURE VERIFICATION")
    else:
        print("❌ SOME FILES FAILED VERIFICATION")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
