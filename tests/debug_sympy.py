"""Debug trigonometric function issues"""
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

print("Testing SymPy operations step by step:")
print("=" * 70)

# Test 1: Basic parsing
print("\n1. Parsing sin(x):")
x = sp.Symbol('x', real=True)
transformations = standard_transformations + (implicit_multiplication_application,)
expr = parse_expr('sin(x)', local_dict={'x': x}, transformations=transformations)
print(f"   Parsed: {expr}")
print(f"   Type: {type(expr)}")

# Test 2: Differentiation  
print("\n2. Differentiating sin(x):")
try:
    deriv = sp.diff(expr, x)
    print(f"   Derivative: {deriv}")
    print(f"   Type: {type(deriv)}")
except Exception as e:
    print(f"   ERROR in diff: {e}")

# Test 3: Simplification
print("\n3. Simplifying derivative:")
try:
    simplified = sp.trigsimp(deriv)
    print(f"   Trigsimplified: {simplified}")
except Exception as e:
    print(f"   ERROR in trigsimp: {e}")

try:
    simplified2 = sp.simplify(deriv)
    print(f"   Simplified: {simplified2}")
except Exception as e:
    print(f"   ERROR in simplify: {e}")

# Test 4: Direct method call
print("\n4. Testing derivative.simplify():")
try:
    simplified3 = deriv.simplify()
    print(f"   Method simplify: {simplified3}")
except Exception as e:
    print(f"   ERROR in method: {e}")

# Test 5: Check degrees
print("\n5. Checking variable presence:")
try:
    deg = sp.degree(deriv, x)
    print(f"   Degree: {deg}")
except Exception as e:
    print(f"   ERROR in degree: {e}")

print("\n6. Testing with str() conversion:")
print(f"   str(deriv): {str(deriv)}")
print(f"   deriv == 0: {deriv == 0}")
print(f"   Free symbols: {deriv.free_symbols}")

print("\nAll debug tests completed!")
