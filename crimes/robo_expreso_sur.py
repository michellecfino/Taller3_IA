"""
robo_expreso_sur.py — El Robo en el Expreso del Sur

El collar de esmeraldas de la Marquesa desapareció del vagón privado del tren nocturno.
Elena fue vista en el vagón privado durante el robo; sus huellas están en el estuche de joyas.
Don Rodrigo fue grabado por la cámara de seguridad en el vagón de equipaje durante toda la noche.
El vagón de equipaje es el extremo opuesto al vagón privado; es imposible haber estado en ambos a la vez.
La Marquesa es la víctima directa del robo y presenció el incidente.
La Marquesa acusa a Elena.
Victor declara que Elena estuvo con él en el vagón comedor toda la noche.
Elena declara que Victor estuvo con ella en el vagón comedor toda la noche.

Como detective, he llegado a las siguientes conclusiones:
Quien fue grabado en cámara en un lugar alejado de la escena durante el crimen está descartado.
La víctima del crimen no tiene razón para mentir; es testigo imparcial.
La acusación de un testigo imparcial es creíble.
Quien estaba en la escena y es acusado de forma creíble es culpable.
Quien da coartada a un culpable lo está defendiendo.
Si dos personas se dan coartada mutuamente, tienen una alianza de coartadas entre sí.
"""

from src.crime_case import CrimeCase, QuerySpec
from src.predicate_logic import ExistsGoal, KnowledgeBase, Predicate, Rule, Term


def crear_kb() -> KnowledgeBase:
    """Construye la KB según la narrativa del módulo."""
    kb = KnowledgeBase()

    # Constantes del caso
    elena          = Term("elena")
    victor         = Term("victor")
    don_rodrigo    = Term("don_rodrigo")
    marquesa       = Term("marquesa")
    estuche_joyas  = Term("estuche_joyas")
    vagon_equipaje = Term("vagon_equipaje")

    # === YOUR CODE HERE ===
    # === YOUR CODE HERE ===

    # 1. Hechos (Evidencia y testimonios)
    # Elena estaba en la escena y sus huellas están en el estuche
    kb.add_fact(Predicate("en_escena", (elena,)))
    kb.add_fact(Predicate("huellas_en", (elena, estuche_joyas)))

    # Don Rodrigo grabado en lugar alejado
    kb.add_fact(Predicate("grabado_en_camara", (don_rodrigo, vagon_equipaje)))
    kb.add_fact(Predicate("lugar_alejado", (vagon_equipaje,)))

    # Estatus de la Marquesa y su acusación
    kb.add_fact(Predicate("victima", (marquesa,)))
    kb.add_fact(Predicate("acusa_a", (marquesa, elena)))

    # Coartadas mutuas (Victor y Elena)
    kb.add_fact(Predicate("da_coartada", (victor, elena)))
    kb.add_fact(Predicate("da_coartada", (elena, victor)))

    # 2. Reglas de Deducción
    X = Term("$X")
    Y = Term("$Y")
    Lugar = Term("$Lugar")

    # "Quien fue grabado en cámara en un lugar alejado de la escena está descartado."
    kb.add_rule(Rule(
        head=Predicate("descartado", (X,)),
        body=(
            Predicate("grabado_en_camara", (X, Lugar)),
            Predicate("lugar_alejado", (Lugar,)),
        )
    ))

    # "La víctima del crimen es testigo imparcial."
    kb.add_rule(Rule(
        head=Predicate("testigo_imparcial", (X,)),
        body=(Predicate("victima", (X,)),)
    ))

    # "La acusación de un testigo imparcial es creíble."
    kb.add_rule(Rule(
        head=Predicate("acusacion_creible", (X, Y)),
        body=(
            Predicate("testigo_imparcial", (X,)),
            Predicate("acusa_a", (X, Y)),
        )
    ))

    # "Quien estaba en la escena y es acusado de forma creíble es culpable."
    kb.add_rule(Rule(
        head=Predicate("culpable", (X,)),
        body=(
            Predicate("en_escena", (X,)),
            Predicate("acusacion_creible", (Y, X)),
        )
    ))

    # "Quien da coartada a un culpable lo está defendiendo."
    kb.add_rule(Rule(
        head=Predicate("defiende_al_culpable", (X,)),
        body=(
            Predicate("da_coartada", (X, Y)),
            Predicate("culpable", (Y,)),
        )
    ))

    # "Si dos personas se dan coartada mutuamente, tienen una alianza de coartadas entre sí."
    kb.add_rule(Rule(
        head=Predicate("alianza_coartadas", (X, Y)),
        body=(
            Predicate("da_coartada", (X, Y)),
            Predicate("da_coartada", (Y, X)),
        )
    ))

    # === END YOUR CODE ===

    # === END YOUR CODE ===

    return kb


CASE = CrimeCase(
    id="robo_expreso_sur",
    title="El Robo en el Expreso del Sur",
    suspects=("elena", "victor", "don_rodrigo"),
    narrative=__doc__,
    description=(
        "El collar de la Marquesa desapareció en un tren nocturno. "
        "Don Rodrigo tiene coartada de cámara. Elena estaba en la escena con huellas en el estuche. "
        "La víctima la acusa. Victor y Elena se cubren mutuamente."
    ),
    create_kb=crear_kb,
    queries=(
        QuerySpec(
            description="¿Don Rodrigo está descartado?",
            goal=Predicate("descartado", (Term("don_rodrigo"),)),
        ),
        QuerySpec(
            description="¿La acusación de la Marquesa contra Elena es creíble?",
            goal=Predicate("acusacion_creible", (Term("marquesa"), Term("elena"))),
        ),
        QuerySpec(
            description="¿Elena es culpable?",
            goal=Predicate("culpable", (Term("elena"),)),
        ),
        QuerySpec(
            description="¿Victor defiende al culpable?",
            goal=Predicate("defiende_al_culpable", (Term("victor"),)),
        ),
        QuerySpec(
            description="¿Existe alianza de coartadas entre Elena y Victor?",
            goal=ExistsGoal("$X", Predicate("alianza_coartadas", (Term("$X"), Term("victor")))),
        ),
    ),
)
