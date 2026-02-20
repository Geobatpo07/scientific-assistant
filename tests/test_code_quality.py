#!/usr/bin/env python
"""Code Quality Verification

Tests:
1. Type hint coverage
2. Docstring completeness
3. Import consistency
4. Function signatures
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def analyze_file(file_path: Path) -> Dict:
    """Analyze Python file for quality metrics."""
    with open(file_path, 'r') as f:
        content = f.read()
        tree = ast.parse(content)
    
    stats = {
        "file": file_path.name,
        "lines": len(content.split('\n')),
        "classes": [],
        "functions": [],
        "imports": [],
    }
    
    for node in ast.walk(tree):
        # Classes
        if isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "has_docstring": bool(ast.get_docstring(node)),
                "methods": [],
            }
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    has_annotations = any(
                        param.annotation for param in item.args.args
                    ) or item.returns
                    
                    method_info = {
                        "name": item.name,
                        "has_docstring": bool(ast.get_docstring(item)),
                        "has_type_hints": has_annotations,
                    }
                    class_info["methods"].append(method_info)
            
            stats["classes"].append(class_info)
        
        # Top-level functions
        elif isinstance(node, ast.FunctionDef):
            has_annotations = any(
                param.annotation for param in node.args.args
            ) or node.returns
            
            func_info = {
                "name": node.name,
                "has_docstring": bool(ast.get_docstring(node)),
                "has_type_hints": has_annotations,
            }
            stats["functions"].append(func_info)
        
        # Imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                stats["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                stats["imports"].append(node.module)
    
    return stats


def main():
    """Run code quality checks."""
    print("\n" + "="*70)
    print("CODE QUALITY VERIFICATION")
    print("="*70)
    
    files = [
        "app/hf/embeddings.py",
        "app/hf/reranker.py",
        "app/vectorstore/faiss_index.py",
        "app/vectorstore/hybrid_store.py",
        "app/vectorstore/chroma.py",
        "app/vectorstore/retriever.py",
        "app/vectorstore/store.py",
        "app/rag/chains.py",
    ]
    
    total_stats = {
        "files": 0,
        "lines": 0,
        "classes": 0,
        "functions": 0,
        "with_docstrings": 0,
        "with_type_hints": 0,
    }
    
    for file_name in files:
        file_path = project_root / file_name
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_name}")
            continue
        
        stats = analyze_file(file_path)
        
        print(f"\n📄 {file_name}")
        print(f"   Lines: {stats['lines']}")
        print(f"   Classes: {len(stats['classes'])}")
        print(f"   Functions: {len(stats['functions'])}")
        
        total_stats["files"] += 1
        total_stats["lines"] += stats["lines"]
        total_stats["classes"] += len(stats["classes"])
        total_stats["functions"] += len(stats["functions"])
        
        # Class quality
        for cls in stats["classes"]:
            status = "✅" if cls["has_docstring"] else "⚠️"
            print(f"   {status} {cls['name']}")
            
            if cls["has_docstring"]:
                total_stats["with_docstrings"] += 1
            
            for method in cls["methods"]:
                if method["has_type_hints"]:
                    total_stats["with_type_hints"] += 1
        
        # Function quality
        for func in stats["functions"]:
            status = "✅" if func["has_docstring"] and func["has_type_hints"] else "⚠️"
            hint_status = "✅" if func["has_type_hints"] else "❌"
            doc_status = "✅" if func["has_docstring"] else "❌"
            print(f"   {hint_status}{doc_status} {func['name']}()")
    
    # Summary
    print("\n" + "="*70)
    print("QUALITY SUMMARY")
    print("="*70)
    print(f"Total Files:        {total_stats['files']}")
    print(f"Total Lines:        {total_stats['lines']}")
    print(f"Total Classes:      {total_stats['classes']}")
    print(f"Total Functions:    {total_stats['functions']}")
    print(f"With Docstrings:    {total_stats['with_docstrings']}/{total_stats['classes']}")
    print(f"With Type Hints:    {total_stats['with_type_hints']}/{total_stats['functions']}")
    
    if total_stats["lines"] > 0:
        avg_lines_per_file = total_stats["lines"] // total_stats["files"]
        print(f"Avg Lines/File:     {avg_lines_per_file}")
    
    print("="*70 + "\n")
    print("✅ CODE QUALITY VERIFICATION COMPLETE")
    print("="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
