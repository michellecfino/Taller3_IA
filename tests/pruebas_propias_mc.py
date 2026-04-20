from src.logic_core import Atom, And, Or, Not, Implies, Iff  # <--- ¡Faltaba Iff!
from src.model_checking import (
    check_entailment, 
    check_satisfiable, 
    check_valid,
    get_all_models, 
    truth_table
)
from src.utils import formula_to_string, print_truth_table, format_model, format_kb

def test_contraejemplos_visuales():
    """Muestra explícitamente POR QUÉ no hay entailment."""
    p, q = Atom("p"), Atom("q")
    kb = [Implies(p, q)]  # Solo si p entonces q
    
    print("\n--- CONTRAEJEMPLO: Por qué p→q no implica q ---")
    print("KB: Si llueve, entonces el suelo está mojado")
    print("Consulta: ¿El suelo está mojado?")
    
    resultado = check_entailment(kb, q)
    print(f"¿Se sigue? {resultado}")
    
    # Mostrar el contraejemplo manualmente
    print("\nContraejemplo encontrado:")
    print("Modelo donde KB es verdadera pero q es falso:")
    print("p = False, q = False")
    print("Explicación: Puede que el suelo esté seco porque NO llovió")
    
    assert resultado is False
    
def test_enumerar_todos_los_modelos():
    """Muestra TODOS los mundos posibles donde una fórmula es verdadera."""
    p, q = Atom("p"), Atom("q")
    formula = Or(p, q)  # p ∨ q
    
    print("\n--- FÓRMULA: p ∨ q ---")
    print("Todos los modelos donde esta fórmula es VERDADERA:")
    
    tabla = truth_table(formula)
    modelos_verdaderos = [modelo for modelo, valor in tabla if valor]
    
    for i, modelo in enumerate(modelos_verdaderos, 1):
        print(f"{i}. p={modelo['p']}, q={modelo['q']}")
    
    print(f"\nTotal: {len(modelos_verdaderos)} de 4 modelos posibles")
    assert len(modelos_verdaderos) == 3

def test_consistencia_vs_validez():
    """Distingue entre 'siempre verdad' y 'a veces verdad'."""
    p = Atom("p")
    
    print("\n=== DIFERENCIA CLAVE ===")
    
    # Fórmula consistente (satisfacible) pero NO válida
    formula1 = p
    print(f"\n1. Fórmula: {formula_to_string(formula1)}")
    print(f"   ¿Satisfacible? {check_satisfiable(formula1)[0]}")
    print(f"   ¿Válida? {check_valid(formula1)}")
    print("   → Es verdadera EN ALGUNOS mundos (cuando p=True)")
    
    # Fórmula válida (tautología)
    formula2 = Or(p, Not(p))
    print(f"\n2. Fórmula: {formula_to_string(formula2)}")
    print(f"   ¿Satisfacible? {check_satisfiable(formula2)[0]}")
    print(f"   ¿Válida? {check_valid(formula2)}")
    print("   → Es verdadera EN TODOS los mundos")
    
    # Fórmula insatisfacible (contradicción)
    formula3 = And(p, Not(p))
    print(f"\n3. Fórmula: {formula_to_string(formula3)}")
    print(f"   ¿Satisfacible? {check_satisfiable(formula3)[0]}")
    print(f"   ¿Válida? {check_valid(formula3)}")
    print("   → Es falsa EN TODOS los mundos")
    
def test_razonamiento_incompleto():
    """Casos donde la información NO es suficiente para concluir."""
    a, b, c = Atom("a"), Atom("b"), Atom("c")
    
    print("\n--- ESCENARIO: CRIMEN EN LA MANSión ---")
    print("Hechos conocidos:")
    print("- El mayordomo o la secretaria son culpables")
    print("- Si el mayordomo es culpable, entonces la puerta estaba forzada")
    print("- No sabemos si la puerta estaba forzada")
    
    kb = [
        Or(Atom("mayordomo"), Atom("secretaria")),
        Implies(Atom("mayordomo"), Atom("puerta_forzada"))
    ]
    
    print("\n¿Podemos concluir que la secretaria es culpable?")
    resultado = check_entailment(kb, Atom("secretaria"))
    print(f"→ {resultado}")
    
    if not resultado:
        print("NO, porque podría ser el mayordomo el culpable")
    
    print("\n¿Podemos concluir que el mayordomo es culpable?")
    resultado2 = check_entailment(kb, Atom("mayordomo"))
    print(f"→ {resultado2}")
    
    if not resultado2:
        print("NO, porque podría ser la secretaria la culpable")
def test_dependencias_circulares():
    """Muestra cómo Iff crea dependencias bidireccionales."""
    a, b = Atom("a"), Atom("b")
    
    print("\n--- DEPENDENCIAS CIRCULARES ---")
    print("Regla: a ↔ b (a es verdad si y solo si b es verdad)")
    
    kb = [Iff(a, b)]
    
    print("\nCaso 1: Sabemos que a es verdad")
    kb_con_a = kb + [a]
    print(f"¿Se sigue b? {check_entailment(kb_con_a, b)}")
    print("→ Sí, porque a ↔ b significa que son equivalentes")
    
    print("\nCaso 2: Sabemos que a es falso")
    kb_con_not_a = kb + [Not(a)]
    print(f"¿Se sigue ¬b? {check_entailment(kb_con_not_a, Not(b))}")
    print("→ Sí, porque si a es falso, b también debe serlo")
    
    print("\nCaso 3: Sin información adicional")
    print(f"¿Se sigue a? {check_entailment(kb, a)}")
    print("→ No, porque podrían ser ambos verdaderos o ambos falsos")

def test_poder_expresivo():
    """Muestra cómo diferentes conectores cambian las conclusiones."""
    p, q = Atom("p"), Atom("q")
    
    print("\n=== MISMA INFORMACIÓN, DIFERENTE EXPRESIÓN ===")
    
    casos = [
        ("AND", And(p, q)),
        ("OR", Or(p, q)),
        ("IMPLICA", Implies(p, q)),
        ("IFF", Iff(p, q))
    ]
    
    for nombre, formula in casos:
        print(f"\n{nombre}: {formula_to_string(formula)}")
        print(f"  Modelos verdaderos: ", end="")
        tabla = truth_table(formula)
        modelos = [m for m, v in tabla if v]
        print(f"{len(modelos)} de 4")
        for modelo in modelos:
            print(f"    p={modelo['p']}, q={modelo['q']}")
            
def test_sistema_permisos():
    """Casos de uso real: control de acceso a sistema."""
    admin = Atom("es_admin")
    editor = Atom("es_editor")
    puede_editar = Atom("puede_editar")
    puede_borrar = Atom("puede_borrar")
    
    print("\n--- SISTEMA DE PERMISOS ---")
    print("Reglas:")
    print("1. Solo admins o editores pueden editar")
    print("2. Solo admins pueden borrar")
    print("3. Si eres admin, automáticamente puedes editar")
    
    kb = [
        Implies(puede_editar, Or(admin, editor)),
        Implies(puede_borrar, admin),
        Implies(admin, puede_editar)
    ]
    
    print("\nEscenario: Usuario es editor")
    escenario1 = kb + [editor]
    print(f"¿Puede editar? {check_entailment(escenario1, puede_editar)}")
    print(f"¿Puede borrar? {check_entailment(escenario1, puede_borrar)}")
    
    print("\nEscenario: Usuario es admin")
    escenario2 = kb + [admin]
    print(f"¿Puede editar? {check_entailment(escenario2, puede_editar)}")
    print(f"¿Puede borrar? {check_entailment(escenario2, puede_borrar)}")                                    

def test_tablitas(): #todo esto se lo dedico a Beresntein que casi acaba con mi paz mental
    p, q = Atom("p"), Atom("q")
    
    formula1 = Implies(p, q)
    print(f"\n\nTabla de verdad para: {formula_to_string(formula1)}")
    print_truth_table(formula1)
    
    formula2 = Not(And(p, q))
    print(f"\nTabla de verdad para: {formula_to_string(formula2)}")
    print_truth_table(formula2)

    assert True 

def test_caso_criminal_visual():
    pablo = Atom("pablo_culpable")
    coartada = Atom("tiene_coartada")
    
    kb = [Implies(coartada, Not(pablo)), coartada]
    
    print("\n\n--- Análisis de Caso Criminal ---")
    print(f"¿Se sigue que Pablo NO es culpable?")
    resultado = check_entailment(kb, Not(pablo))
    print(f"Resultado del motor lógico: {resultado}")
    
    assert resultado is True
    
def test_misterio_final():
    print("\n\n--- EL MISTERIO DE LOS TRES SOSPECHOSOS ---")
    a = Atom("Ana")
    b = Atom("Bernardo")
    c = Atom("Carlos")
       
    # Reglas:
    # 1. Al menos uno es culpable: (Ana v Bernardo v Carlos)
    # 2. Si Ana es culpable, Bernardo también: (Ana -> Bernardo)
    # 3. Carlos es inocente: ¬Carlos
    kb = [
        Or(a, b, c),
        Implies(a, b),
        Not(c)
    ]
        
    print("Si sabemos que Carlos es inocente y Ana siempre implica a Bernardo...")
    # ¿Podemos asegurar que Bernardo es culpable?
        # Ojo: Si Ana fuera inocente, Bernardo igual podría ser culpable por la regla 1
        # Pero si Ana fuera culpable, Bernardo TIENE que serlo.
        # ¿Es Bernardo culpable en todos los escenarios posibles?
        
    resultado = check_entailment(kb, b)
    print(f"¿Es Bernardo culpable obligatoriamente?: {resultado}")
    print("\nTabla de la combinación de reglas (KB):")
    print_truth_table(And(*kb))
        
def test_leyes_fundamentales():
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    
    # Ley de la Idempotencia: (p ∨ p) ↔ p
    assert check_valid(Iff(Or(p, p), p))
    
    # Ley de Absorción: p ∨ (p ∧ q) ↔ p
    assert check_valid(Iff(Or(p, And(p, q)), p))
    
    # Ley Distributiva: p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r)
    distributiva = Iff(
        And(p, Or(q, r)),
        Or(And(p, q), And(p, r))
    )
    assert check_valid(distributiva)
    
    # Contraposición: (p → q) ↔ (¬q → ¬p)
    assert check_valid(Iff(Implies(p, q), Implies(Not(q), Not(p))))
    
def test_atomos_fantasma_y_complejidad():
    p, q, r, s, t = [Atom(f"at_{i}") for i in range(5)]
    
    # Caso: La KB habla de 'p', pero la consulta es sobre 'q' (un átomo nuevo)
    # KB: {p}. ¿Se sigue q? No, porque hay modelos donde p es V pero q es F.
    assert check_entailment([p], q) is False
    
    # Caso: 5 átomos (32 modelos). Si p0 es verdad y p0 -> p1 -> ... -> p4
    # Entonces p4 debe ser verdad.
    kb_cadena = [
        p,
        Implies(p, q),
        Implies(q, r),
        Implies(r, s),
        Implies(s, t)
    ]
    assert check_entailment(kb_cadena, t) is True
def test_casos_frontera_pro():
    p = Atom("p")
    q = Atom("q")

    # KB Vacía: No debería implicar nada que no sea una verdad universal
    assert check_entailment([], p) is False
    assert check_entailment([], Or(p, Not(p))) is True # Tautología sí se implica
    
    # KB con Fórmulas Repetidas: No debería afectar el resultado
    assert check_entailment([p, p, p], p) is True
    
    # Si la KB es falsa, la implicación es verdadera por defecto
    formula_loca = Implies(And(p, Not(p)), q)
    assert check_valid(formula_loca) is True
def test_acertijo_smullyan():
    # p: A es caballero, q: B es caballero
    p, q = Atom("p"), Atom("q")
    
    # Si A es caballero (p), su afirmación (¬p ∨ q) es verdadera.
    # Si A es villano (¬p), su afirmación (¬p ∨ q) es falsa.
    # Esto se modela como: p ↔ (¬p ∨ q)
    kb = [Iff(p, Or(Not(p), q))]
    
    # ¿Qué podemos deducir?
    # Resultado esperado: Ambos son caballeros.
    assert check_entailment(kb, p) is True
    assert check_entailment(kb, q) is True
    
def test_identidades_completas():
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    # Ley de Morgan para 3 átomos: ¬(p ∨ q ∨ r) ↔ (¬p ∧ ¬q ∧ ¬r)
    assert check_valid(Iff(Not(Or(p, q, r)), And(Not(p), Not(q), Not(r))))
    # Distributividad del And sobre el Or
    assert check_valid(Iff(And(p, Or(q, r)), Or(And(p, q), And(p, r))))
    # Doble negación profunda
    assert check_valid(Iff(Not(Not(Not(Not(p)))), p))

def test_inferencia_avanzada():
    p, q, r, s = Atom("p"), Atom("q"), Atom("r"), Atom("s")
    # Dilema Constructivo: ((p→q) ∧ (r→s) ∧ (p ∨ r)) ⊨ (q ∨ s)
    kb = [Implies(p, q), Implies(r, s), Or(p, r)]
    assert check_entailment(kb, Or(q, s)) is True
    # Reducción al absurdo: (p→q) ∧ (p→¬q) ⊨ ¬p
    kb_absurdo = [Implies(p, q), Implies(p, Not(q))]
    assert check_entailment(kb_absurdo, Not(p)) is True

def test_satisfaccion_extrema():
    atoms = [Atom(f"x{i}") for i in range(6)]
    # Una cadena que solo es verdad si todos son verdaderos
    formula = And(*atoms)
    sat, model = check_satisfiable(formula)
    assert sat is True
    assert all(model.values()) is True
    
    # Una contradicción escondida en una cadena larga
    contradicion = And(Implies(atoms[0], atoms[1]), 
                       Implies(atoms[1], atoms[2]), 
                       atoms[0], 
                       Not(atoms[2]))
    sat_c, _ = check_satisfiable(contradicion)
    assert sat_c is False

def test_acertijos_clasicos():
    # El acertijo de los dos caminos (Uno miente, otro dice verdad)
    # p: camino A es el correcto, q: el guardia de A dice la verdad
    p, q = Atom("p"), Atom("q")
    # "Si le pregunto al otro guardia si este camino es el correcto, dirá que NO"
    # Esto se modela como una inconsistencia si el camino es correcto.
    acertijo = Iff(q, Not(p)) 
    # Aquí se prueba la satisfacibilidad para ver qué modelos sobreviven
    assert check_satisfiable(acertijo)[0] is True

def test_bordes_y_limites():
    p = Atom("p")
    # ¿Qué pasa si la KB tiene la misma fórmula 10 veces?
    assert check_entailment([p] * 10, p) is True
    # ¿Qué pasa si consultamos una tautología sobre una KB vacía?
    assert check_entailment([], Or(p, Not(p))) is True
    # ¿Qué pasa si la fórmula es solo un átomo y su negación?
    assert check_valid(Or(p, Not(p))) is True    
def test_visualizacion_total():
    print("\n" + "="*40)
    print(" EXPLORACIÓN DE TODAS LAS RAMAS LÓGICAS ")
    print("="*40)
    
    p, q = Atom("p"), Atom("q")
    casos = [
        ("Identidad", Iff(p, p)),
        ("Contradicción", And(p, Not(p))),
        ("Leyes de De Morgan", Iff(Not(And(p, q)), Or(Not(p), Not(q)))),
        ("Implicación Vacua", Implies(And(p, Not(p)), q))
    ]
    
    for nombre, formula in casos:
        print(f"\n>>> Rama: {nombre}")
        print(f"Fórmula: {formula_to_string(formula)}")
        print(f"¿Es Válida?: {check_valid(formula)}")
        print(f"¿Es Satisfacible?: {check_satisfiable(formula)[0]}")
    
    assert True    
def test_asociatividad_y_conmutatividad():
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    # (p ∧ (q ∧ r)) ↔ ((p ∧ q) ∧ r)
    f1 = And(p, And(q, r))
    f2 = And(And(p, q), r)
    assert check_valid(Iff(f1, f2)) is True
    
    # (p ∨ q) ↔ (q ∨ p)
    assert check_valid(Iff(Or(p, q), Or(q, p))) is True

def test_principio_explosion():
    """Si la base de conocimiento es inconsistente, implica CUALQUIER cosa."""
    p = Atom("p")
    q = Atom("q") # q no tiene nada que ver con p
    kb = [p, Not(p)]
    assert check_entailment(kb, q) is True

def test_negacion_anidada_extrema():
    p = Atom("p")
    # 10 negaciones: ¬¬¬¬¬¬¬¬¬¬p ↔ p (par = identidad)
    formula = p
    for _ in range(10):
        formula = Not(formula)
    assert check_valid(Iff(formula, p)) is True
    
    # 11 negaciones: ¬...p ↔ ¬p (impar = negación)
    formula_impar = Not(formula)
    assert check_valid(Iff(formula_impar, Not(p))) is True

def test_silogismos_complejos():
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    # Modus Tollens: ((p → q) ∧ ¬q) ⊨ ¬p
    assert check_entailment([Implies(p, q), Not(q)], Not(p)) is True
    
    # Silogismo Disyuntivo: ((p ∨ q) ∧ ¬p) ⊨ q
    assert check_entailment([Or(p, q), Not(p)], q) is True

def test_conteo_de_modelos():
    """Verifica que el número de filas en la tabla sea exactamente 2^n."""
    p, q, r, s = Atom("p"), Atom("q"), Atom("r"), Atom("s")
    # 4 átomos distintos = 16 modelos
    tabla = truth_table(And(p, q, r, s))
    assert len(tabla) == 16
    
    # En un AND de 4 átomos, solo 1 fila debe ser True
    filas_true = [resultado for modelo, resultado in tabla if resultado]
    assert len(filas_true) == 1

def test_iff_transitivo():
    # ((p ↔ q) ∧ (q ↔ r)) → (p ↔ r)
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    formula = Implies(And(Iff(p, q), Iff(q, r)), Iff(p, r))
    assert check_valid(formula) is True    
def test_iff_identidad_profunda():
    p, q = Atom("p"), Atom("q")
    # (p ↔ q) ↔ ((p → q) ∧ (q → p))
    # Esta es la definición misma del Iff.
    definicion = Iff(Iff(p, q), And(Implies(p, q), Implies(q, p)))
    assert check_valid(definicion) is True
def test_operadores_idempotentes():
    p = Atom("p")
    # En lugar de And(p), probamos And(p, p)
    # (p ∧ p) ↔ p
    assert check_valid(Iff(And(p, p), p)) is True
    # (p ∨ p) ↔ p
    assert check_valid(Iff(Or(p, p), p)) is True

def test_distributividad_or_and():
    # p ∨ (q ∧ r) ↔ (p ∨ q) ∧ (p ∨ r)
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    f1 = Or(p, And(q, r))
    f2 = And(Or(p, q), Or(p, r))
    assert check_valid(Iff(f1, f2)) is True

def test_todas_las_variables_falsas():
    # ¬p1 ∧ ¬p2 ∧ ... ∧ ¬p5
    atoms = [Atom(f"p{i}") for i in range(5)]
    formula = And(*[Not(a) for a in atoms])
    sat, model = check_satisfiable(formula)
    assert sat is True
    assert all(not val for val in model.values()) is True    
    
def test_exclusion_tercero_compleja():
    p, q = Atom("p"), Atom("q")
    # (p → q) ∨ (q → p) 
    # Aunque no lo parezca, ¡esto siempre es verdad en lógica clásica!
    assert check_valid(Or(Implies(p, q), Implies(q, p))) is True

def test_kb_consistente_pero_debil():
    p, q = Atom("p"), Atom("q")
    kb = [Or(p, q)]
    # Si solo sabemos p ∨ q, no podemos asegurar p
    assert check_entailment(kb, p) is False
    # Pero si negamos q, entonces p TIENE que ser verdad
    kb.append(Not(q))
    assert check_entailment(kb, p) is True

def test_transitividad_iff_larga():
    a, b, c, d = Atom("a"), Atom("b"), Atom("c"), Atom("d")
    # (a ↔ b) ∧ (b ↔ c) ∧ (c ↔ d) ⊨ (a ↔ d)
    kb = [Iff(a, b), Iff(b, c), Iff(c, d)]
    assert check_entailment(kb, Iff(a, d)) is True

def test_implicaciones_anidadas():
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    # p → (q → r)  es equivalente a  (p ∧ q) → r
    f1 = Implies(p, Implies(q, r))
    f2 = Implies(And(p, q), r)
    assert check_valid(Iff(f1, f2)) is True

def test_get_all_models_unique_atoms():
    p, q = Atom("p"), Atom("q")
    models = get_all_models({"p", "p", "q", "q"})
    assert len(models) == 4

def test_not_de_tautologia():
    p = Atom("p")
    # ¬(p ∨ ¬p) debe ser insatisfacible
    formula = Not(Or(p, Not(p)))
    sat, _ = check_satisfiable(formula)
    assert sat is False

def test_kb_tres_variables_interconectadas():
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    # KB: p ∨ q, p → r, q → r
    # ¿Se sigue r? Sí, es el caso de análisis de casos.
    kb = [Or(p, q), Implies(p, r), Implies(q, r)]
    assert check_entailment(kb, r) is True    