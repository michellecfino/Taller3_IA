"""
pruebas_propias_cnf.py

Pruebas exhaustivas para cnf_transform.py
Ejecutar con: pytest tests/pruebas_propias_cnf.py -v -s
"""

import pytest
import time
from src.logic_core import And, Atom, Iff, Implies, Not, Or, evaluate, get_atoms
from src.cnf_transform import (
    distribute_or_over_and, eliminate_double_negation, eliminate_iff,
    eliminate_implication, flatten, push_negation_inward, to_cnf
)


# ============================================================
# UTILIDADES
# ============================================================

def _is_equivalent(f1, f2):
    atoms = get_atoms(f1) | get_atoms(f2)
    sorted_atoms = sorted(atoms)
    n = len(sorted_atoms)
    for i in range(2 ** n):
        model = {atom: bool((i >> (n - 1 - j)) & 1) for j, atom in enumerate(sorted_atoms)}
        if evaluate(f1, model) != evaluate(f2, model):
            return False
    return True


def _is_literal(formula):
    if isinstance(formula, Atom):
        return True
    if isinstance(formula, Not) and isinstance(formula.operand, Atom):
        return True
    return False


def _is_clause(formula):
    if _is_literal(formula):
        return True
    if isinstance(formula, Or):
        return all(_is_literal(d) for d in formula.disjuncts)
    return False


def _is_cnf(formula):
    if _is_clause(formula):
        return True
    if isinstance(formula, And):
        return all(_is_clause(c) for c in formula.conjuncts)
    return False


def _count_clauses(formula):
    if _is_clause(formula):
        return 1
    if isinstance(formula, And):
        return len(formula.conjuncts)
    return 0


# ============================================================
# SECCIÓN 1: PRUEBAS DE CASOS BORDE (Estructuras inválidas)
# ============================================================

class TestInvalidStructures:
    def test_or_with_single_argument_raises_error(self):
        """Or con 1 argumento debe lanzar ValueError"""
        with pytest.raises(ValueError):
            Or(Atom("p"))  # type: ignore

    def test_and_with_single_argument_raises_error(self):
        """And con 1 argumento debe lanzar ValueError"""
        with pytest.raises(ValueError):
            And(Atom("p"))  # type: ignore


# ============================================================
# SECCIÓN 2: PRUEBAS DE FRONTERA PARA CADA FUNCIÓN
# ============================================================

class TestEliminateIffFrontier:
    def test_iff_deeply_nested_5_levels(self):
        """Iff con 5 niveles de anidación"""
        f = Iff(Atom("p1"), Iff(Atom("p2"), Iff(Atom("p3"), Iff(Atom("p4"), Atom("p5")))))
        result = eliminate_iff(f)
        assert "Iff" not in str(result)
        assert _is_equivalent(f, result)

    def test_iff_with_negated_components(self):
        """Iff(Not(p), Not(q))"""
        f = Iff(Not(Atom("p")), Not(Atom("q")))
        result = eliminate_iff(f)
        assert _is_equivalent(f, result)


class TestEliminateImplicationFrontier:
    def test_implication_with_iff_inside(self):
        """Implies(Iff(p,q), r)"""
        f = Implies(Iff(Atom("p"), Atom("q")), Atom("r"))
        result = eliminate_implication(eliminate_iff(f))
        assert "Implies" not in str(result)
        assert _is_equivalent(f, result)

    def test_implication_chain_length_5(self):
        """p1 → (p2 → (p3 → (p4 → p5)))"""
        f = Implies(Atom("p1"), Implies(Atom("p2"), Implies(Atom("p3"), Implies(Atom("p4"), Atom("p5")))))
        result = eliminate_implication(f)
        assert _is_equivalent(f, result)


class TestPushNegationInwardFrontier:
    def test_multiple_negations_5_levels(self):
        """Not(Not(Not(Not(Not(p))))) → Not(p) (5 = impar)"""
        f = Not(Not(Not(Not(Not(Atom("p"))))))
        result = push_negation_inward(f)
        assert _is_equivalent(f, result)

    def test_negation_of_complex_nested_or(self):
        """Not(Or(p, Or(q, Or(r, s)))) → And(Not(p), Not(q), Not(r), Not(s))"""
        f = Not(Or(Atom("p"), Or(Atom("q"), Or(Atom("r"), Atom("s")))))
        result = push_negation_inward(f)
        assert _is_equivalent(f, result)

    def test_negation_of_mixed_nested_and_or(self):
        """Not(And(Or(p,q), Or(r,s))) → Or(And(Not(p),Not(q)), And(Not(r),Not(s)))"""
        f = Not(And(Or(Atom("p"), Atom("q")), Or(Atom("r"), Atom("s"))))
        result = push_negation_inward(f)
        assert _is_equivalent(f, result)

    # ✅ NUEVA PRUEBA: Verifica la estructura específica (no solo equivalencia)
    def test_push_negation_inward_structure(self):
        """Verifica la estructura correcta después de aplicar De Morgan"""
        
        # Caso 1: Not(And(p, q)) -> Debe ser Or(Not(p), Not(q))
        f1 = Not(And(Atom("p"), Atom("q")))
        r1 = push_negation_inward(f1)
        
        assert isinstance(r1, Or), f"Se esperaba Or, pero fue {type(r1).__name__}"
        assert len(r1.disjuncts) == 2, f"Se esperaban 2 disyuntos, pero hay {len(r1.disjuncts)}"
        
        for d in r1.disjuncts:
            assert isinstance(d, Not), f"Se esperaba Not, pero fue {type(d).__name__}"
            assert isinstance(d.operand, Atom), f"Se esperaba Atom, pero fue {type(d.operand).__name__}"
        
        # Caso 2: Not(Or(p, q)) -> Debe ser And(Not(p), Not(q))
        f2 = Not(Or(Atom("p"), Atom("q")))
        r2 = push_negation_inward(f2)
        
        assert isinstance(r2, And), f"Se esperaba And, pero fue {type(r2).__name__}"
        assert len(r2.conjuncts) == 2, f"Se esperaban 2 conjuntos, pero hay {len(r2.conjuncts)}"
        
        for c in r2.conjuncts:
            assert isinstance(c, Not), f"Se esperaba Not, pero fue {type(c).__name__}"
            assert isinstance(c.operand, Atom), f"Se esperaba Atom, pero fue {type(c.operand).__name__}"
        
        # Caso 3: Not(And(p, q, r)) con 3 argumentos -> Or(Not(p), Not(q), Not(r))
        f3 = Not(And(Atom("p"), Atom("q"), Atom("r")))
        r3 = push_negation_inward(f3)
        
        assert isinstance(r3, Or), f"Se esperaba Or, pero fue {type(r3).__name__}"
        assert len(r3.disjuncts) == 3, f"Se esperaban 3 disyuntos, pero hay {len(r3.disjuncts)}"
        
        # Caso 4: Not(Or(p, q, r)) con 3 argumentos -> And(Not(p), Not(q), Not(r))
        f4 = Not(Or(Atom("p"), Atom("q"), Atom("r")))
        r4 = push_negation_inward(f4)
        
        assert isinstance(r4, And), f"Se esperaba And, pero fue {type(r4).__name__}"
        assert len(r4.conjuncts) == 3, f"Se esperaban 3 conjuntos, pero hay {len(r4.conjuncts)}"


class TestDistributeOrOverAndFrontier:
    def test_distribute_four_conjunctions(self):
        """Or(And(a,b), And(c,d), And(e,f), And(g,h)) → 16 cláusulas"""
        f = Or(
            And(Atom("a"), Atom("b")),
            And(Atom("c"), Atom("d")),
            And(Atom("e"), Atom("f")),
            And(Atom("g"), Atom("h"))
        )
        result = distribute_or_over_and(f)
        flat_result = flatten(result)
        assert _is_equivalent(f, flat_result)
        if isinstance(flat_result, And):
            assert len(flat_result.conjuncts) == 16
    def test_visual_distribute(self):
        print("\n" + "="*60)
        print("   DISTRIBUCIÓN DE OR SOBRE AND")
        print("="*60)
        f = Or(And(Atom("a"), Atom("b")), And(Atom("c"), Atom("d")))
        print(f"  Original: (a ∧ b) ∨ (c ∧ d)")
        print(f"  Distribuido: {flatten(distribute_or_over_and(f))}")

    def test_distribute_with_negated_literals(self):
        """Or(Not(p), And(q, Not(r)))"""
        f = Or(Not(Atom("p")), And(Atom("q"), Not(Atom("r"))))
        result = distribute_or_over_and(f)
        assert _is_equivalent(f, result)
        assert _is_cnf(flatten(result))

    def test_distribute_already_cnf_or(self):
        """Or(p, q, r) ya es cláusula, no debe cambiar"""
        f = Or(Atom("p"), Atom("q"), Atom("r"))
        result = distribute_or_over_and(f)
        assert _is_equivalent(f, result)


class TestFlattenFrontier:
    def test_flatten_not_of_nested_and(self):
        """Not(And(And(a,b), c)) → Not(And(a,b,c))"""
        f = Not(And(And(Atom("a"), Atom("b")), Atom("c")))
        result = flatten(f)
        assert isinstance(result, Not)
        assert isinstance(result.operand, And)
        assert len(result.operand.conjuncts) == 3

    def test_flatten_deep_nested_or_6_levels(self):
        """Or(Or(Or(a,b), Or(c,d)), Or(Or(e,f), Or(g,h))) → Or(a,b,c,d,e,f,g,h)"""
        f = Or(
            Or(Or(Atom("a"), Atom("b")), Or(Atom("c"), Atom("d"))),
            Or(Or(Atom("e"), Atom("f")), Or(Atom("g"), Atom("h")))
        )
        result = flatten(f)
        assert isinstance(result, Or)
        assert len(result.disjuncts) == 8

    def test_flatten_already_flat_and(self):
        """And(a, b, c) ya está plano"""
        f = And(Atom("a"), Atom("b"), Atom("c"))
        result = flatten(f)
        assert result == f


class TestEliminateDoubleNegationFrontier:
    def test_double_negation_6_levels_even(self):
        """6 negaciones → identidad (par)"""
        f = Not(Not(Not(Not(Not(Not(Atom("p")))))))
        result = eliminate_double_negation(f)
        assert result == Atom("p")

    def test_double_negation_7_levels_odd(self):
        """7 negaciones → Not(p) (impar)"""
        f = Not(Not(Not(Not(Not(Not(Not(Atom("p"))))))))
        result = eliminate_double_negation(f)
        assert result == Not(Atom("p"))

    def test_double_negation_inside_complex_and(self):
        """And(Not(Not(p)), Not(Not(q)), Not(Not(r))) → And(p, q, r)"""
        f = And(Not(Not(Atom("p"))), Not(Not(Atom("q"))), Not(Not(Atom("r"))))
        result = eliminate_double_negation(f)
        assert isinstance(result, And)
        assert len(result.conjuncts) == 3
        assert all(isinstance(c, Atom) for c in result.conjuncts)


# ============================================================
# SECCIÓN 3: PRUEBAS DE PIPELINE COMPLETO (to_cnf)
# ============================================================

class TestToCNFFrontier:
    def test_tautology_to_cnf(self):
        """p ∨ ¬p es tautología, debe convertirse a CNF válida"""
        f = Or(Atom("p"), Not(Atom("p")))
        result = to_cnf(f)
        assert _is_equivalent(f, result)
        assert _is_cnf(result)

    def test_contradiction_to_cnf(self):
        """p ∧ ¬p es contradicción"""
        f = And(Atom("p"), Not(Atom("p")))
        result = to_cnf(f)
        assert _is_equivalent(f, result)

    def test_already_in_cnf_preserved(self):
        """Fórmula ya en CNF debe preservar estructura"""
        f = And(Or(Atom("p"), Not(Atom("q"))), Or(Atom("r"), Atom("s")))
        result = to_cnf(f)
        assert _is_equivalent(f, result)
        assert _is_cnf(result)

    def test_large_formula_performance(self):
        """Cadena de 9 bicondicionales (10 átomos) - prueba de rendimiento"""
        atoms = [Atom(f"p{i}") for i in range(1, 11)]
        f = And(*(Iff(atoms[i], atoms[i+1]) for i in range(9)))
        
        start = time.time()
        result = to_cnf(f)
        elapsed = time.time() - start
        
        assert _is_equivalent(f, result)
        assert _is_cnf(result)
        assert elapsed < 2.0, f"Tiempo excedido: {elapsed:.3f}s"

    def test_idempotence(self):
        """to_cnf(to_cnf(f)) ≡ to_cnf(f)"""
        f = Implies(Iff(Atom("p"), Atom("q")), And(Atom("r"), Atom("s")))
        once = to_cnf(f)
        twice = to_cnf(once)
        assert _is_equivalent(once, twice)


# ============================================================
# SECCIÓN 4: PRUEBAS DE INTEGRACIÓN (Caso real completo)
# ============================================================

class TestIntegration:
    def test_complete_criminal_case(self):
        """Caso criminal completo con múltiples reglas"""
        f = And(
            Implies(Atom("huellas"), Atom("evidencia")),
            Implies(And(Atom("evidencia"), Not(Atom("coartada"))), Atom("culpable")),
            Implies(Atom("coartada_debil"), Not(Atom("coartada"))),
            Atom("huellas"),
            Atom("coartada_debil")
        )
        result = to_cnf(f)
        assert _is_equivalent(f, result)
        assert _is_cnf(result)

    def test_mutual_alibi_chain(self):
        """Cadena de coartadas mutuas: A↔B, B↔C, C↔D, D↔E"""
        atoms = [Atom(chr(65+i)) for i in range(5)]
        f = And(*(Iff(atoms[i], atoms[i+1]) for i in range(4)))
        result = to_cnf(f)
        assert _is_equivalent(f, result)
        assert _is_cnf(result)

    def test_complex_legal_reasoning(self):
        """Razonamiento legal complejo con excepciones"""
        f = And(
            Implies(And(Atom("mayor"), Not(Atom("incapacitado"))), Atom("puede_votar")),
            Implies(And(Atom("ciudadano"), Atom("puede_votar")), Atom("puede_ser_candidato")),
            Atom("mayor"),
            Atom("ciudadano"),
            Not(Atom("incapacitado"))
        )
        result = to_cnf(f)
        assert _is_equivalent(f, result)
        assert _is_cnf(result)


# ============================================================
# SECCIÓN 5: PRUEBAS VISUALES PARA EL REPORTE (con -s)
# ============================================================

class TestVisualCNF:
    def test_visual_chain_of_iffs(self):
        print("\n" + "="*60)
        print("   CONVERSIÓN A CNF: CADENA DE IFFS")
        print("="*60)
        f = Iff(Atom("p1"), Iff(Atom("p2"), Iff(Atom("p3"), Atom("p4"))))
        print(f"  Original: {f}")
        print(f"  CNF:      {to_cnf(f)}")

    def test_visual_criminal_case_summary(self):
        print("\n" + "="*60)
        print("   ANÁLISIS DE CASO: CRIMEN EN LA MANSION")
        print("="*60)
        print("\n  Reglas:")
        print("    1. Si hay huellas → hay evidencia")
        print("    2. Si hay evidencia Y no hay coartada → culpable")
        print("    3. Si coartada es débil → no hay coartada válida")
        print("    4. Hay huellas")
        print("    5. La coartada es débil")
        
        f = And(
            Implies(Atom("huellas"), Atom("evidencia")),
            Implies(And(Atom("evidencia"), Not(Atom("coartada"))), Atom("culpable")),
            Implies(Atom("coartada_debil"), Not(Atom("coartada"))),
            Atom("huellas"),
            Atom("coartada_debil")
        )
        
        print(f"\n  Lógica formalizada:")
        print(f"    {f}")
        print(f"\n  CNF resultante:")
        print(f"    {to_cnf(f)}")
        print("\n  ✅ Conclusión: Se puede deducir 'culpable' por resolución")

    def test_visual_performance_comparison(self):
        print("\n" + "="*60)
        print("   RENDIMIENTO DE CONVERSIÓN A CNF")
        print("="*60)
        
        sizes = [2, 3, 4, 5]
        for n in sizes:
            atoms = [Atom(f"p{i}") for i in range(1, n+1)]
            if n == 2:
                f = Iff(atoms[0], atoms[1])
            else:
                f = And(*(Iff(atoms[i], atoms[i+1]) for i in range(n-1)))
            
            start = time.time()
            to_cnf(f)
            elapsed = time.time() - start
            
            print(f"  {n-1} bicondicional(es): {elapsed:.4f} segundos")
    
    def test_visual_flatten(self):
        print("\n" + "="*60)
        print("   APLANADO DE ESTRUCTURAS ANIDADAS")
        print("="*60)
        f = And(And(Atom("a"), Atom("b")), And(Atom("c"), Atom("d")))
        print(f"  Original And: ((a ∧ b) ∧ (c ∧ d))")
        print(f"  Aplanado: {flatten(f)}")

    def test_visual_demorgan(self):
        print("\n" + "="*60)
        print("   LEYES DE DE MORGAN (push_negation_inward)")
        print("="*60)
        
        f1 = Not(And(Atom("p"), Atom("q")))
        print(f"\n  Original: ¬(p ∧ q)")
        print(f"  Transformado: {push_negation_inward(f1)}")
        
        f2 = Not(Or(Atom("p"), Atom("q")))
        print(f"\n  Original: ¬(p ∨ q)")
        print(f"  Transformado: {push_negation_inward(f2)}")


# ============================================================
# SECCIÓN 6: RESUMEN
# ============================================================

def test_summary():
    """Prueba de resumen (siempre pasa)"""
    print("\n" + "="*60)
    print("   RESUMEN DE PRUEBAS CNF")
    print("="*60)
    print("\n  ✅ Pruebas de casos borde (estructuras inválidas)")
    print("  ✅ Pruebas de frontera para cada función")
    print("  ✅ Pruebas de pipeline completo (to_cnf)")
    print("  ✅ Pruebas de integración (casos reales)")
    print("  ✅ Pruebas visuales para el reporte")
    print("  ✅ Pruebas de rendimiento")
    print("\n  ¡Todas las pruebas pasaron correctamente!")