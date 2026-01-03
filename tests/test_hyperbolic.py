"""Test hyperbolic functions in calculator.py"""
from app.tools.calculator import create_calculator

calc = create_calculator()

print("Testing hyperbolic functions:")
print("=" * 70)

hyperbolic_expressions = [
    ('sinh(x)', 'cosh(x)'),
    ('cosh(x)', 'sinh(x)'),
    ('tanh(x)', '1 - tanh(x)**2'),
    ('asinh(x)', '1/sqrt(x**2 + 1)'),
    ('acosh(x)', '1/sqrt(x**2 - 1)'),
    ('atanh(x)', '1/(1 - x**2)'),
    ('x * sinh(x)', 'Product rule'),
    ('sinh(x)**2 + cosh(x)**2', 'Hyperbolic identity'),
    ('cosh(x)**2 - sinh(x)**2', 'Should be 1'),
]

for expr, expected_note in hyperbolic_expressions:
    result = calc.symbolic.differentiate(expr, 'x')
    if result.success:
        print(f"✓ d/dx[{expr:20s}] = {result.results['simplified']}")
        if expected_note:
            print(f"  Note: {expected_note}")
    else:
        print(f"✗ {expr:20s} -> ERROR: {result.error_message}")

print("\nTesting hyperbolic integration:")
print("=" * 70)

integrals = ['sinh(x)', 'cosh(x)', 'tanh(x)', 'x * cosh(x)']
for expr in integrals:
    result = calc.symbolic.integrate(expr, 'x')
    if result.success:
        print(f"✓ ∫{expr:15s} dx = {result.results['integral']}")
    else:
        print(f"✗ ∫{expr:15s} dx = ERROR: {result.error_message}")

print("\nAll hyperbolic tests completed!")
