"""English locale's external KSLT labels, distinct from embedded KSCL sprites."""


def variants(prefix, text, states=("normal", "select")):
    return {f"{prefix}_{state}": text for state in states}


CHAPTERS = [
    ("Preludio", "Florecimiento"), ("Fase I", "La invocación"),
    ("Fase II", "Resonancia"), ("Fase III", "El día perdido"),
    ("Fase IV", "Vacío"), ("Fase V", "Rostros gemelos"),
    ("Fase VI", "Canto Lunar"), ("Fase VII", "Tranquilidad"),
    ("Fase VIII", "Sakuya"), ("Fase IX", "Descenso"),
    ("Fase X", "Pétalos caídos"), ("Fase XI", "Eclipse"),
    ("Fase final", "Reino Sagrado"),
]

EXTERNAL_LABELS = {}


def asset(folder, labels):
    EXTERNAL_LABELS[f"ex_texture/{folder}/{folder}.kslt"] = labels


asset("camera_equip_parts", {"fnt_eqp": "Equipado"})
camera = {}
for key, text in {"camera": "Cámara Oscura", "film": "Película", "lens": "Lentes",
                  "parts": "Mejoras del equipo", "reiseki": "Linterna espiritual"}.items():
    camera.update(variants("fnt_" + key, text))
asset("camera_menu_parts", camera)
tabs = {"G_fnt_new": "NUEVO"}
for key, text in {
    "documents": "Documentos", "eqp": "Cambiar equipo", "ghosts": "Apariciones",
    "hozukidolls": "Muñecas Hozuki", "item": "Consumibles", "keyitem": "Objetos clave",
    "lvup": "Mejoras", "other": "Otros", "pictures": "Fotografías", "records": "Registros",
    "revenants": "Renacidos", "specters": "Espectros", "spiritradio": "Radio espiritual",
    "tapes": "Cintas", "telephone": "Teléfono",
}.items():
    tabs.update(variants("fnt_tab_" + key, text))
asset("cmn_tab", tabs)
headings = {f"R_mission_title_fnt_{i:02}": f"{phase}: {title}"
            for i, (phase, title) in enumerate(CHAPTERS)}
for key, text in {
    "audio": "Voces", "camera": "Cámara Oscura", "controls": "Controles",
    "costume": "Trajes", "file": "Archivos", "gallery": "Galería",
    "ghost": "Lista de fantasmas", "item": "Objetos", "license": "Información sobre licencias",
    "load": "Cargar", "map": "Mapa", "menu": "Menú", "mission": "Misiones",
    "movie": "Vídeos", "notebook": "Cuaderno", "onryo": "Fotos de apariciones",
    "option": "Opciones", "outline": "Resúmenes", "pause": "Pausa", "photo": "Fotos",
    "rec": "Registros", "reiseki": "Linterna espiritual", "save": "Guardar",
    "savepoint": "Punto de guardado", "setup": "Configuración", "shop": "Canjear",
}.items():
    headings["fnt_title_" + key] = text
asset("cmn_title_mission", headings)
for i, (phase, title) in enumerate(CHAPTERS):
    EXTERNAL_LABELS[f"ex_texture/cmn_start_mission/mission_start_{i:02}.kslt"] = {
        f"mission_start_{i:02}": [phase, title]}
asset("film_type", {"film_type" + num: "Tipo-" + ("00" if num == "_z" else num) + " ×"
                    for num in ("07", "14", "61", "90", "_z")})
asset("gallery_top_parts", {**variants("fnt_ghostphoto", "Fotos de apariciones"),
                            **variants("fnt_movie", "Vídeos")})
asset("ghostlist_layout", {"G_fnt_new": "NUEVO", "R_fnt_complete": "COMPLETO",
    "R_fnt_count_photo": "Fotos", "R_fnt_total_highscore": "Puntuación máxima",
    "R_fnt_total_photo": "Fotos de fantasmas"})
inventory = {}
for key, text in {"camera": "Cámara Oscura", "costume": "Trajes", "file": "Archivos",
                  "ghost": "Lista de fantasmas", "item": "Objetos", "map": "Mapa",
                  "photo": "Fotos", "rec": "Registros", "reiseki": "Linterna espiritual",
                  "save": "Guardar", "shop": "Canjear"}.items():
    inventory.update(variants("fnt_menu_" + key, text, ("normal", "select", "glow")))
asset("inventory_menu_parts", inventory)
asset("item_list_parts", {"G_fnt_new": "NUEVO"})
asset("mission_start_window", {
    "fnt_mission_start": "Inicio de misión", "fnt_mission_start_eff": "Inicio de misión",
    "fnt_title_appear_enemy": "Enemigos", "fnt_title_condition_clear": "Objetivo",
    "fnt_title_condition_highscore": "Condición de rango", "fnt_title_own_film": "Tipo de película",
    "fnt_title_own_item": "Objetos", "fnt_title_player": "Personaje", "fnt_title_time_limit": "Tiempo límite"})
asset("option_menu", {**variants("photograph", "Modo foto", ("OFF", "ON")),
                      **variants("search", "Modo de exploración", ("OFF", "ON"))})
options = {}
for i, text in enumerate(["Ajustes generales", "Sensibilidad de cámara", "Imagen y sonido",
                          "Restablecer ajustes", "Ajustes gráficos", "Información sobre licencias"]):
    options.update(variants(f"option_top_gtext_{i:02}", text, ("off", "on")))
asset("option_menu_parts", options)
asset("pause_layout", {"fnt_save": "Último autoguardado"})
photo = {"fnt_sorttype": "Ordenar por /", "icon_lock": "Bloquear"}
for key, text in {"onmemory": "Foto temporal", "storage": "Guardar foto"}.items():
    photo.update(variants("fnt_" + key, text))
for key, text in {"dmg": "Daño", "list": "Lista de fantasmas", "mis": "Capítulo",
                  "plac": "Lugar", "pt": "Puntos", "time": "Fecha"}.items():
    photo.update(variants("fnt_sortmenu_" + key, text, ("nor", "sel")))
asset("photo_layout", photo)
asset("pocketbook_layout_list_parts", {"fusen_left": "NUEVO", "fusen_right": "NUEVO"})
asset("result", {
    "res_Gtext_01": "Dificultad", "res_Gtext_02": "Tiempo empleado", "res_Gtext_03": "Mejor puntuación",
    "res_Gtext_04": "Lista de espíritus", "res_Gtext_05": "Muñecas Hozuki", "res_Gtext_06": "Puntuación total",
    "res_Gtext_07": "Récord", "res_Gtext_08": "Eliminaciones", "res_Gtext_09": "Tiempo de juego",
    "res_Gtext_16": "Rango", "res_Gtext_title": "¡Enhorabuena!",
    "res_Gtext_title_mission": "Misión superada", "res_Gtext_title_mission_failed": "Misión fallida"})
buttons = {"HOLD_OFF": "MANT.", "HOLD_ON": "MANT."}
for key in ("l", "maru", "zl", "zr"):
    buttons.update(variants("cmn_button_" + key + "_hold", "MANT.", ("off", "on")))
# Translate words on keycaps; preserve letters, symbols and standard key abbreviations.
for key, text in {"Backspace": "Retro.", "Delete": "Supr", "End": "Fin", "Home": "Inicio",
                  "PageDown": "AvPág", "PageUp": "RePág", "PrtSc": "ImprPant",
                  "LSHIFT": "Mayús", "RSHIFT": "Mayús"}.items():
    buttons.update(variants("btn_PCKey_" + key, text, ("off", "on")))
for key in ("ADD", "DECIMAL", "DIVIDE", "MULTIPLY", "SUBTRACT", "NUMPADENTER", *[f"NUMPAD{i}" for i in range(10)]):
    buttons.update(variants("btn_PCKey_" + key, "Núm", ("off", "on")))
asset("system_layout", buttons)
title = {"Press_Any_Button": "Pulsa cualquier botón", "Press_Any_Button_Loop": "Pulsa cualquier botón"}
for key, text in {"easy": "Fácil", "hard": "Difícil", "nightmare": "Pesadilla"}.items():
    title.update(variants("fnt_difficulty_" + key, text, ("off", "on", "on_loop")))
for key, text in {"newgame": "Nueva partida", "loadgame": "Cargar partida", "option": "Opciones",
                  "exitgame": "Salir del juego"}.items():
    title.update(variants("fnt_menu_" + key, text, ("off", "on", "on_loop")))
asset("title_layout", title)
asset("tv_rating_layout", {
    "R_pts": "ptos.", "fnt_basic_chain": "Cadena", "fnt_basic_combo": "Impactos seguidos",
    "fnt_bonus_2Kill": "Doble eliminación", "fnt_bonus_3Kill": "Triple eliminación",
    "fnt_bonus_boost": "Disparo potenciado", "fnt_bonus_close": "Disparo cercano",
    "fnt_bonus_double": "Disparo doble", "fnt_bonus_escape": "Disparo de escape",
    "fnt_bonus_fatalk": "Eliminación fatal", "fnt_bonus_justk": "Eliminación precisa",
    "fnt_bonus_max": "Disparo máximo", "fnt_bonus_overk": "Eliminación excesiva",
    "fnt_bonus_rorschach": "Disparo Rorschach", "fnt_bonus_shutter": "Oportunidad de foto",
    "fnt_bonus_specialk": "Eliminación especial", "fnt_bonus_surprise": "Disparo sorpresa",
    "fnt_bonus_triple": "Disparo triple", "fnt_bonus_zero": "Disparo cero",
    "fnt_main_damage": "Daño", "fnt_main_point": "Puntos", "fnt_type_fatal": "ENCUADRE FATAL"})

from tutorial_labels import TUTORIALS
EXTERNAL_LABELS.update(TUTORIALS)
