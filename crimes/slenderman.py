#Mención honorífica a que soy fan de Law & Order y de ahí saqué el caso que me pareción más curioso de trabajar porque al final
#como que eran culpables pero las declararon inoncentes jaja

"""
slenderman_bosque.py — La Sombra del Slenderman

El caso se sitúa en un bosque donde una joven fue atacada.
Las sospechosas son Anissa y Morgan, quienes afirman haber actuado para complacer a Slenderman.
Morgan ha sido diagnosticada con una condición psiquiátrica (esquizofrenia).
Anissa no tiene un diagnóstico médico, pero fue influenciada por Morgan.

Reglas del Detective:
1. Alguien tiene 'delirio_compartido' si cree en Slenderman y cometió el acto con otra persona.
2. Una persona es 'inimputable' si cometió el acto pero tiene un diagnóstico médico.
3. El 'motivo_mistico' existe si la persona cree que Slenderman le ordenó actuar.
4. Alguien es 'culpable_legal' si cometió el acto, tiene un motivo y NO es inimputable.
5. Existe 'influencia_peligrosa' si una persona inimputable convence a otra de cometer el acto.
"""

from src.crime_case import CrimeCase, QuerySpec
from src.predicate_logic import ExistsGoal, KnowledgeBase, Predicate, Rule, Term

def crear_kb() -> KnowledgeBase:
    """Construye la KB para el caso del Bosque de Slenderman."""
    kb = KnowledgeBase()

    # Constantes
    anissa = Term("anissa")
    morgan = Term("morgan")
    bella = Term("bella")
    slenderman = Term("slenderman")
    esquizofrenia = Term("esquizofrenia")

    # 1. Hechos (Evidencia)
    kb.add_fact(Predicate("ataco_a", (anissa, bella)))
    kb.add_fact(Predicate("ataco_a", (morgan, bella)))
    
    kb.add_fact(Predicate("cree_en", (anissa, slenderman)))
    kb.add_fact(Predicate("cree_en", (morgan, slenderman)))
    
    kb.add_fact(Predicate("orden_de", (slenderman, morgan)))
    kb.add_fact(Predicate("orden_de", (slenderman, anissa)))

    kb.add_fact(Predicate("diagnostico", (morgan, esquizofrenia)))
    
    kb.add_fact(Predicate("sin_diagnostico_medico", (anissa,)))

    X = Term("$X")
    Y = Term("$Y")
    V = Term("$V")
    E = Term("$E")

    #Motivo Místico
    kb.add_rule(Rule(Predicate("motivo_mistico", (X,)), (
        Predicate("cree_en", (X, slenderman)), 
        Predicate("orden_de", (slenderman, X))
    )))

    #Inimputable (Solo para quienes tienen diagnóstico)
    kb.add_rule(Rule(Predicate("inimputable", (X,)), (
        Predicate("ataco_a", (X, V)), 
        Predicate("diagnostico", (X, E))
    )))

    #Culpable Legal
    kb.add_rule(Rule(Predicate("culpable_legal", (X,)), (
        Predicate("ataco_a", (X, V)), 
        Predicate("motivo_mistico", (X,)), 
        Predicate("sin_diagnostico_medico", (X,))
    )))

    # Si X e Y atacaron a la misma persona V, comparten el delirio.
    kb.add_rule(Rule(Predicate("delirio_compartido", (X, Y)), (
        Predicate("cree_en", (X, slenderman)),
        Predicate("cree_en", (Y, slenderman)),
        Predicate("ataco_a", (X, V)),
        Predicate("ataco_a", (Y, V))
    )))

    #Inocente Legal - Morgan tiene un diagnóstico sacado de las patas de mi gato
    kb.add_rule(Rule(Predicate("inocente_legal", (X,)), (
        Predicate("inimputable", (X,)),
    )))

    #Inocente Legal - Anissa está loquita y ve cosas pero no tiene diagnóstico
    kb.add_rule(Rule(Predicate("inocente_legal", (X,)), (
        Predicate("delirio_compartido", (X, Y)),
        Predicate("inimputable", (Y,)),
    )))

    return kb

CASE = CrimeCase(
    id="slenderman_bosque",
    title="La Sombra del Slenderman",
    suspects=("anissa", "morgan"),
    narrative=__doc__,
    description=(
        "Dos jóvenes atacan a una amiga alegando órdenes de un ente ficticio. "
        "El sistema distingue entre responsabilidad penal e inimputabilidad."
    ),
    create_kb=crear_kb,
    queries=(
        QuerySpec(
            description="¿Tiene Morgan un motivo místico para el crimen?",
            goal=Predicate("motivo_mistico", (Term("morgan"),)),
        ),
        QuerySpec(
            description="¿Es Morgan inimputable debido a su diagnóstico?",
            goal=Predicate("inimputable", (Term("morgan"),)),
        ),
        QuerySpec(
            description="¿Es Anissa legalmente culpable?",
            goal=Predicate("culpable_legal", (Term("anissa"),)),
        ),
        QuerySpec(
            description="¿Existe alguien que sea inimputable?",
            goal=ExistsGoal("$X", Predicate("inimputable", (Term("$X"),))),
        ),
        QuerySpec(
            description="¿Hay un delirio compartido entre Anissa y Morgan?",
            goal=Predicate("delirio_compartido", (Term("anissa"), Term("morgan"))),
        ),
    ),
)