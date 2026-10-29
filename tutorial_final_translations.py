"""English-source tutorial/UI variants, consistent with reviewed tutorials in text9."""

from text9_translations import TEXT9


def tutorial(i):
    return TEXT9[("text9.fmsg", i)]


def swap_button(s, old, new):
    return s.replace(f"^20~{old}~", f"^20~{new}~")


def swap_buttons(s, changes):
    # Non-colliding remap for control glyphs, preserving formatting tokens.
    for old in changes:
        s = s.replace(f"^20~{old}~", f"[TMP_BUTTON_{old}]")
    for old, new in changes.items():
        s = s.replace(f"[TMP_BUTTON_{old}]", f"^20~{new}~")
    return s


TUTORIAL_FINAL = {
    ("text3.fmsg", 285): (
        "^00 - Correr -\n"
        "Mantén pulsado ^20~13~ para correr. La cámara te seguirá automáticamente.\n"
        "^00 - Giro rápido -\n"
        "Usa ^20~07~ o ^20~08~ para girarte rápidamente y mirar en dirección opuesta."
    ),
    ("text3.fmsg", 287): (
        "^00La linterna ilumina las zonas oscuras y te ayuda a explorar el entorno.\n"
        "^00Usa ^20~10~ para dirigir la linterna hacia donde apunta la cámara."
    ),
    ("text3.fmsg", 293): tutorial(138),
    ("text3.fmsg", 294): tutorial(147),
    ("text3.fmsg", 295): tutorial(148),
    ("text3.fmsg", 299): tutorial(172),
    ("text3.fmsg", 302): tutorial(155),
    ("text3.fmsg", 303): tutorial(156),
    ("text3.fmsg", 304): tutorial(161),
    ("text3.fmsg", 305): tutorial(162),
    ("text3.fmsg", 306): "Menú",
    ("text3.fmsg", 309): tutorial(160),
    ("text3.fmsg", 311): tutorial(166),
    ("text3.fmsg", 312): tutorial(163),
    ("text3.fmsg", 313): tutorial(164),
    ("text3.fmsg", 314): tutorial(167),
    ("text3.fmsg", 315): tutorial(168),
    ("text3.fmsg", 460): tutorial(167),
    ("text3.fmsg", 723): "Zoom",

    ("textnew_02.fmsg", 15): swap_button(tutorial(174), "03", "13"),
    ("textnew_02.fmsg", 16): swap_button(tutorial(160), "04", "17"),
    ("textnew_02.fmsg", 17): swap_buttons(tutorial(138), {"03": "13", "13": "11"}),
    ("textnew_02.fmsg", 18): (
        "^00 - Correr -\n"
        "Mantén pulsado ^20~14~ para correr. La cámara te seguirá automáticamente.\n"
        "^00 - Giro rápido -\n"
        "Usa ^20~07~ o ^20~08~ para girarte rápidamente y mirar en dirección opuesta."
    ),
    ("textnew_02.fmsg", 66): "Consultar equipo",
    ("textnew_02.fmsg", 67): "Templo de Tsukiyomi - Escenario de Tsukiyomi",
    ("textnew_02.fmsg", 68): "Templo Shugen - Zona del altar",
    ("textnew_02.fmsg", 69): "Templo del Eclipse Lunar - Pasillo",
    ("textnew_02.fmsg", 70): "Faro del cabo Tsukiyomi - Acceso al faro",
    ("textnew_02.fmsg", 71): "Trae el documento del que hablamos.\nDéjalo sobre el escritorio.",
    ("textnew_02.fmsg", 72): "^20~09~ o ^20~19~: Seleccionar",
    ("textnew_02.fmsg", 73): "^20~09~ o ^20~00~: Mover",
    ("textnew_02.fmsg", 75): "Activa o desactiva la vibración del mando.",
    ("textnew_02.fmsg", 76): "Activa la vibración del mando.",
    ("textnew_02.fmsg", 77): "Desactiva la vibración del mando.",
    ("textnew_02.fmsg", 78): "Caminar - Adelante",
    ("textnew_02.fmsg", 79): "Caminar - Atrás",
    ("textnew_02.fmsg", 80): "Caminar - Izquierda",
    ("textnew_02.fmsg", 81): "Caminar - Derecha",
    ("textnew_02.fmsg", 82): "Mirar - Arriba",
    ("textnew_02.fmsg", 83): "Mirar - Abajo",
    ("textnew_02.fmsg", 84): "Mirar - Izquierda",
    ("textnew_02.fmsg", 85): "Mirar - Derecha",
    ("textnew_02.fmsg", 86): "Elegir objeto - Arriba",
    ("textnew_02.fmsg", 87): "Elegir objeto - Abajo",
    ("textnew_02.fmsg", 88): "Cambiar objeto - Izquierda",
    ("textnew_02.fmsg", 89): "Cambiar objeto - Derecha",
    ("textnew_02.fmsg", 90): "Mover cámara - Adelante",
    ("textnew_02.fmsg", 91): "Mover cámara - Atrás",
    ("textnew_02.fmsg", 92): "Mover cámara - Izquierda",
    ("textnew_02.fmsg", 93): "Mover cámara - Derecha",
    ("textnew_02.fmsg", 94): "Girar cámara - Arriba",
    ("textnew_02.fmsg", 95): "Girar cámara - Abajo",
    ("textnew_02.fmsg", 96): "Girar cámara - Izquierda",
    ("textnew_02.fmsg", 97): "Girar cámara - Derecha",
    ("textnew_02.fmsg", 98): "Inclinar - Izquierda",
    ("textnew_02.fmsg", 99): "Inclinar - Derecha",
    ("textnew_02.fmsg", 100): "Subir cámara",
    ("textnew_02.fmsg", 101): "Bajar cámara",
    ("textnew_02.fmsg", 102): "Restablecer posición de cámara",
    ("textnew_02.fmsg", 103): "Modo de control del personaje",
    ("textnew_02.fmsg", 104): "Cambiar velocidad de control",
    ("textnew_02.fmsg", 105): "Mostrar u ocultar interfaz",
    ("textnew_02.fmsg", 106): "Salir del modo instantánea",
    ("textnew_02.fmsg", 107): "Girar/Confirmar",
    ("textnew_02.fmsg", 108): "No se puede terminar de configurar los controles porque falta asignar una tecla a una o varias acciones.",
    ("textnew_02.fmsg", 109): "En el modo exploración, pulsa ^20~10~ para inclinar la cámara hacia arriba\ny ^20~10~ para inclinarla hacia abajo.",
    ("textnew_02.fmsg", 111): "En el modo exploración, pulsa ^20~10~ para girar la cámara a la derecha\ny ^20~10~ para girarla a la izquierda.",
    ("textnew_02.fmsg", 113): "En el modo foto, pulsa ^20~10~ para inclinar la cámara hacia arriba\ny ^20~10~ para inclinarla hacia abajo.",
    ("textnew_02.fmsg", 115): "En el modo foto, pulsa ^20~10~ para girar la cámara a la derecha\ny ^20~10~ para girarla a la izquierda.",
    ("textnew_02.fmsg", 117): "Pulsa ^20~04~ para entrar en el modo instantánea. Si ves un lugar interesante, prueba a fotografiarlo.",
    ("textnew_02.fmsg", 118): "^20~00~: Seleccionar",
    ("textnew_02.fmsg", 119): "^20~00~: Mover",
    ("textnew_02.fmsg", 120): "^20~19~: Pasar página",
    ("textnew_02.fmsg", 121): "^20~18~: Seleccionar",
    ("textnew_02.fmsg", 122): "^20~19~: Seleccionar",

    ("system2.fmsg", 51): (
        "Usa el sensor de movimiento del mando inalámbrico y ^20~10~ para controlar\n"
        "la dirección de la cámara en el modo foto.\n"
        "(Este método permite manejar el mando como una cámara de forma intuitiva.)"
    ),
    ("system2.fmsg", 257): "^20~45~^20~46~ o ^20~19~: Página ^20~05~: Siguiente",
    ("system2.fmsg", 258): "Caminar: ^20~44~^20~45~^20~43~^20~46~.",
    ("system2.fmsg", 259): "Mover: ^20~44~^20~45~^20~43~^20~46~.",
    ("system2.fmsg", 278): "MUY FÁCIL: Para disfrutar de la historia sin sobresaltos.\n(No se guardarán las puntuaciones)",
}

# Identical source strings have the same translation; other button-layout variants
# are populated by the generator's exact-English translation memory.

for idx, mode, order in [
    (260, "exploración", ("47", "48")),
    (261, "exploración", ("48", "47")),
    (262, "exploración", ("50", "49")),
    (263, "exploración", ("49", "50")),
    (264, "foto", ("47", "48")),
    (265, "foto", ("48", "47")),
    (266, "foto", ("50", "49")),
    (267, "foto", ("49", "50")),
    (268, "exploración", ("47", "48")),
    (269, "exploración", ("48", "47")),
    (270, "exploración", ("50", "49")),
    (271, "exploración", ("49", "50")),
    (272, "foto", ("47", "48")),
    (273, "foto", ("48", "47")),
    (274, "foto", ("50", "49")),
    (275, "foto", ("49", "50")),
]:
    if idx in (260, 261, 264, 265, 268, 269, 272, 273):
        value = (f"En el modo {mode}, usa ^20~{order[0]}~ para subir la cámara\n"
                 f"y ^20~{order[1]}~ para bajarla.")
    else:
        value = (f"En el modo {mode}, usa ^20~{order[0]}~ para girar la cámara a la derecha\n"
                 f"y ^20~{order[1]}~ para girarla a la izquierda.")
    TUTORIAL_FINAL[("system2.fmsg", idx)] = value

TUTORIAL_FINAL.update({
    ("system2.fmsg", 276): (
        "^00En este modo, el personaje se mueve por el\n"
        "mundo y recoge objetos, entre otras acciones.\n"
        "                        - Movimiento -\n\n"
        "Caminar: Usa [COLOR:Set ]^20~44~^20~45~^20~43~^20~46~[COLOR:Reset ] para desplazarte.\n\n"
        "Correr: Mantén pulsado [COLOR:Set ]^20~34~[COLOR:Reset ] para correr hacia delante.\n\n"
        "Desplazamiento lateral: Mantén pulsado [COLOR:Set ]^20~15~[COLOR:Reset ]\n"
        "y usa [COLOR:Set ]^20~09~[COLOR:Reset ] para moverte de lado.\n"
        "^00                    - Control de cámara -\n\n"
        "Mirar alrededor: [COLOR:Set ]^20~47~^20~49~^20~48~^20~50~[COLOR:Reset ].\n\n"
        "Centrar: [COLOR:Set ]^20~36~[COLOR:Reset ].\n\n"
        "^00                      - Exploración -\n\n"
        "Enfocar: Mantén pulsado [COLOR:Set ]^20~29~[COLOR:Reset ].\n\n"
        "Tocar objetos: Mantén pulsado [COLOR:Set ]^20~29~[COLOR:Reset ] junto\n"
        "al objeto que quieras tocar.\n\n"
        "Interactuar: [COLOR:Set ]^20~40~[COLOR:Reset ].\n\n"
        "Cambiar al modo foto: [COLOR:Set ]^20~33~[COLOR:Reset ]."
    ),
    ("system2.fmsg", 277): (
        "^00En este modo manejas la Cámara Oscura.\n\n"
        "                  - Control de cámara 1 -\n\n"
        "Cambiar posición: Usa [COLOR:Set ]^20~44~^20~45~^20~43~^20~46~[COLOR:Reset ]\n"
        "para ajustar la posición.\n\n"
        "Cambiar enfoque: Mueve la cámara con [COLOR:Set ]^20~47~^20~49~^20~48~^20~50~[COLOR:Reset ].\n"
        "^00                   - Control de cámara 2 -\n\n"
        "Enfoque rápido: Mantén pulsado [COLOR:Set ]^20~47~^20~49~^20~48~^20~50~[COLOR:Reset ]\n"
        "y usa [COLOR:Set ]^20~10~[COLOR:Reset ].\n\n"
        "Cambiar ángulo: [COLOR:Set ]^20~37~[COLOR:Reset ] / [COLOR:Set ]^20~38~[COLOR:Reset ].\n"
        "^00                    - Fotografiar 1 -\n\n"
        "Disparar: Pulsa [COLOR:Set ]^20~14~[COLOR:Reset ].\n\n"
        "Fijar objetivo: Mantén pulsado [COLOR:Set ]^20~32~[COLOR:Reset ] para fijar ^20~32~.\n\n"
        "Cambiar película: [COLOR:Set ]^20~53~^20~54~[COLOR:Reset ].\n"
        "^00                    - Fotografiar 2 -\n\n"
        "Cambiar lente: [COLOR:Set ]^20~51~^20~52~[COLOR:Reset ].\n\n"
        "Disparo especial: Pulsa [COLOR:Set ]^20~35~[COLOR:Reset ] para usar\n"
        "la capacidad de la lente.\n\n"
        "Cambiar al modo exploración: [COLOR:Set ]^20~33~[COLOR:Reset ]."
    ),
})
