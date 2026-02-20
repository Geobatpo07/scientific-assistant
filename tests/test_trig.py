"""Quick test of trigonometric functions in calculator.py"""
from app.tools.calculator import create_calculator

calc = create_calculator()

expressions = [
    'x**2',
    'sin(x)',
    'exp(x)',
    'log(x)',
    '1/x',
    'x**3 + 2*x**2 + x + 1',
    'cos(x)**2 + sin(x)**2',
    'tan(x)',
    'x**2 * sin(x)'
]

print("Testing trigonometric and special functions:")
print("=" * 70)

for expr in expressions:
    result = calc.symbolic.differentiate(expr, 'x')
    if result.success:
        print(f"✓ {expr:22s} -> {result.results['simplified']}")
    else:
        print(f"✗ {expr:22s} -> ERROR: {result.error_message}")

print("\nTesting integration:")
print("=" * 70)

test_integrals = ['x**2', 'sin(x)', 'exp(x)', 'cos(x)']
for expr in test_integrals:
    result = calc.symbolic.integrate(expr, 'x')
    if result.success:
        print(f"✓ ∫{expr:15s} dx = {result.results['integral']}")
    else:
        print(f"✗ ∫{expr:15s} dx = ERROR: {result.error_message}")

print("\nAll tests completed!")
