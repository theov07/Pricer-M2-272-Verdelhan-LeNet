#!/usr/bin/env python3

print("=== TEST VALEURS EXTRÊMES 10^-20 ===")
print("Tests threshold jusqu'à 10^-20:")

import math

test_cases = [
    1e-20,    # 10^-20 → 10^-22 en fraction  
    1e-18,    # 10^-18 → 10^-20 en fraction
    1e-15,    # 10^-15 → 10^-17 en fraction
    1e-10,    # 10^-10 → 10^-12 en fraction
    1e-5,     # 10^-5 → 10^-7 en fraction
    0.001,    # 0.001% → 0.00001 en fraction
    0.1,      # 0.1% → 0.001 en fraction
    1,        # 1% → 0.01 en fraction
]

print("Pourcentage → Fraction:")
for percent in test_cases:
    fraction = percent / 100
    print(f"{percent:25} % → {fraction:25} (fraction)")

print("\nNotation scientifique:")
for percent in test_cases:
    fraction = percent / 100
    print(f"{percent:.2e} % → {fraction:.2e} (fraction)")

print("\n=== TEST AFFICHAGE JAVASCRIPT ===")
print("Simulation de (params.threshold * 100).toFixed(20):")

fractions = [1e-22, 1e-20, 1e-17, 1e-12, 1e-7, 1e-5, 1e-3, 1e-2]

for fraction in fractions:
    percent = fraction * 100
    formatted = f"{percent:.20f}"
    print(f"Fraction {fraction:.2e} → {formatted}%")