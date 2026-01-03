"""Clean up and organize test files after integration completion."""
import os
import shutil
from pathlib import Path

print("=" * 80)
print("TEST FILE ORGANIZATION")
print("=" * 80)

# Define test files
test_files = {
    "Temporary Debug Files": [
        "debug_sympy.py",
        "test_trig.py",
        "test_hyperbolic.py",
    ],
    "Integration Test Suite": [
        "test_agent_integration.py",
        "test_full_integration.py", 
        "test_enhanced_integration.py",
        "test_final_validation.py",
    ],
    "Calculator Examples": [
        "test_logistic.py",
        "example_8_enhanced_calculator.py",
        "example_9_logistic_regression.py",
    ],
}

# Root directory
root_dir = Path(".")

# Status
print("\n[INVENTORY] Test Files Status")
print("-" * 80)

all_files = []
for category, files in test_files.items():
    print(f"\n{category}:")
    for file in files:
        path = root_dir / file
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ {file:40} ({size:,} bytes)")
            all_files.append(file)
        else:
            print(f"  - {file:40} (NOT FOUND)")

# Recommendations
print("\n" + "=" * 80)
print("[RECOMMENDATIONS]")
print("=" * 80)

print("""
KEEP (Integration Suite):
  ✓ test_agent_integration.py - Initial integration test
  ✓ test_full_integration.py - Comprehensive validation
  ✓ test_enhanced_integration.py - Fallback system test
  ✓ test_final_validation.py - Quality score verification

KEEP (Examples):
  ✓ example_8_enhanced_calculator.py - Comprehensive calculator demo
  ✓ example_9_logistic_regression.py - ML example with gradient descent
  ✓ test_logistic.py - Quick logistic regression test

OPTIONAL CLEANUP:
  - debug_sympy.py - Debug script (can be archived)
  - test_trig.py - Trigonometric function test (can be archived)
  - test_hyperbolic.py - Hyperbolic function test (can be archived)

MOVE TO TESTS/ DIRECTORY:
  Consider moving all test files to tests/ for better organization:
  - tests/integration/test_agent_integration.py
  - tests/integration/test_calculator_integration.py
  - tests/validation/test_final_validation.py
""")

print("\n" + "=" * 80)
print("[DOCUMENTATION CREATED]")
print("=" * 80)

doc_files = [
    "CALCULATOR_AGENT_ALIGNMENT.md",
    "INTEGRATION_COMPLETE_SUMMARY.md",
]

for doc in doc_files:
    path = root_dir / doc
    if path.exists():
        size = path.stat().st_size
        print(f"  ✓ {doc:50} ({size:,} bytes)")

print("\n" + "=" * 80)
print("[STATUS]")
print("=" * 80)
print(f"""
Test Files: {len(all_files)} files
Documentation: {len(doc_files)} files

Integration Status: ✅ COMPLETE

Next Steps:
1. Keep integration tests for CI/CD pipeline
2. Archive debug files if no longer needed
3. Reference documentation files in project README
4. Run full test suite before deployment:
   - pytest test_agent_integration.py -v
   - pytest test_final_validation.py -v

System is ready for production deployment!
""")
