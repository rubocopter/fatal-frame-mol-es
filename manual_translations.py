"""Hand-authored Castilian entries translated directly from English USen.

This source deliberately imports nothing from the old fan patch.
Run to regenerate translations_from_english.json with source fingerprints.
"""

import json
from collections import defaultdict
from clean_translation import TRANSLATIONS, digest, source_files
from story_translations import STORY
from story_extra_translations import STORY_EXTRA
from story_remaining_translations import STORY_REMAINING
from story_ongoing_translations import STORY_ONGOING
from story_final_text1 import STORY_FINAL
from tutorial_final_translations import TUTORIAL_FINAL
from artbook_translations import ARTBOOK
from artbook_extended_translations import ARTBOOK_EXTENDED
from artbook_lore_translations import ARTBOOK_LORE
from bonus_ui_translations import BONUS_UI
from credits_translations import CREDITS
from ui_translations import UI
from text2_translations import TEXT2
from text2_scene_translations import SCENE
from text2_lore_translations import LORE
from text3_translations import SCENERY
from text4_translations import CINEMATICS
from text5_translations import RECORDINGS
from text5_ui_translations import GALLERY
from text5_accessories_translations import ACCESSORIES
from text6_translations import TEXT6
from text6_tail_translations import TEXT6_TAIL
from text7_translations import TEXT7
from text8_translations import TEXT8
from text9_translations import TEXT9

# Exact-match replacements are reserved for context-independent UI labels.
COMMON = {
    "Yes": "Sí", "No": "No", "Confirm": "Confirmar",
    "Back": "Volver", "Open": "Abrir", "Check": "Examinar",
    "Pick Up": "Recoger", "Proceed": "Continuar", "Look": "Mirar",
    "Touch": "Tocar", "Crouch": "Agacharse", "Dodge": "Esquivar",
    "Talk": "Hablar", "Take": "Coger", "Camera Obscura": "Cámara Oscura",
    "Normal": "Normal", "Inverted": "Invertido",
    "ON": "Sí", "OFF": "No", "EASY": "Fácil", "NORMAL": "NORMAL",
    "HARD": "Difícil", "NIGHTMARE": "PESADILLA",
    "RANK": "Clasificación", "SCORE": "Puntuación",
    "Type": "Tipo", "Settings": "Opciones",
    "Save": "Guardar", "Lock": "Bloquear", "Unlock": "Desbloquear",
    "Delete": "Eliminar", "Points": "Puntos", "Page": "Página",
    "Damage": "Daño", "Date": "Fecha", "Location": "Lugar",
    "Score": "Puntuación", "Episode": "Episodio",
    "Film": "Película", "Lens": "Lente", "Target": "Objetivo",
    "Photographer": "Fotógrafo", "Category": "Categoría",
    "Costumes": "Trajes", "Accessories": "Accesorios",
    "Subtitles": "Subtítulos", "Brightness": "Brillo", "Volume": "Volumen",
    "Screen Size": "Tamaño de pantalla",
    "Music Volume": "Volumen de música",
    "Sound Effects Volume": "Volumen de efectos",
    "Voice Volume": "Volumen de voces",
    "Output Device": "Dispositivo de salida",
    "Output Type": "Tipo de salida", "Stereo": "Estéreo",
    "Search Mode": "Modo de exploración", "Photo Mode": "Modo foto",
    "Manual": "Manual", "Classic": "Clásico", "Action": "Acción",
    "Walk": "Caminar", "Run": "Correr", "Pause": "Pausa",
    "Look Around": "Mirar alrededor",
    "Look Around Quickly": "Mirar rápidamente",
    "Lock On": "Fijar objetivo",
    "Take Photo (Attack)": "Fotografiar (atacar)",
    "Dodge Attack": "Esquivar ataque",
    "Ready Camera": "Preparar cámara",
    "Put Camera Away": "Guardar cámara",
    "Aim Camera": "Apuntar con la cámara",
    "Aim Camera Backward": "Apuntar hacia atrás",
    "Show Menu": "Abrir menú",
    "Show Detailed Map": "Abrir mapa detallado",
    "Pick Up Item": "Recoger objeto",
    "Select": "Seleccionar", "Next Page": "Página siguiente",
    "Close Window": "Cerrar ventana", "Default": "Predeterminado",
    "Borderless": "Sin bordes", "Fullscreen": "Pantalla completa",
    "Low": "Bajo", "High": "Alto",
    "Short": "Corta", "Long": "Larga",
    "Display Resolution": "Resolución de pantalla",
    "Window Settings": "Modo de ventana",
    "Overall Rendering Quality": "Calidad gráfica general",
    "Texture Quality": "Calidad de texturas",
    "Shadow Quality": "Calidad de sombras",
    "Local Reflection Quality": "Calidad de reflejos locales",
    "Effect Quality": "Calidad de efectos",
    "Anti-Aliasing": "Suavizado de bordes",
    "Depth of Field": "Profundidad de campo",
    "Ambient Occlusion": "Oclusión ambiental",
    "Bloom": "Resplandor",
    "Light Shafts": "Rayos de luz",
    "Detail Distance": "Distancia de detalle",
    "Point Lights Display Distance": "Distancia de luces puntuales",
    "Spirit Stone Flashlight": "Linterna de Piedra Espiritual",
    "Ghost List": "Lista de fantasmas", "Date Taken": "Fecha de captura",
    "Photo Points": "Puntos de foto", "Location Taken": "Lugar de captura",
    "Last Saved": "Último guardado",
    "General Settings": "Opciones generales",
    "Camera Sensitivity": "Sensibilidad de cámara",
    "Display & Sound": "Imagen y sonido",
    "Reset to Default": "Restablecer valores",
    "Camera Controls": "Controles de cámara",
    "Vibration Feature": "Vibración del mando",
    "Gyroscope Sensitivity": "Sensibilidad del giroscopio",
    "Format Settings": "Opciones de formato",
    "Keyboard and Mouse": "Teclado y ratón",
    "Keyboard Only": "Solo teclado",
    "Key Configuration": "Asignación de teclas",
    "Control Type": "Tipo de control",
    "Other": "Otros",
    "Display Language": "Idioma",
    "Japanese": "Japonés", "French": "Francés",
    "German": "Alemán",
    "Traditional Chinese": "Chino tradicional",
    "Simplified Chinese": "Chino simplificado",
    "Custom": "Personalizado",
}

# Contextual translations, keyed by English resource address.
SPECIAL = {
    ("system2.fmsg", 2): "Español",
    ("system2.fmsg", 7): "Cambia el idioma de los textos y subtítulos.",
    ("system2.fmsg", 9): "Se cambiará el idioma de los textos.\n¿Quieres continuar?",
    ("system2.fmsg", 29): "%ls  %d puntos\n¿Quieres comprarlo? (Puntos actuales: %d)",
    ("system2.fmsg", 30): "No tienes suficientes puntos.",
    ("system2.fmsg", 45): "Apuntar hacia atrás\nCorrer",
    ("system2.fmsg", 50): "Sensor de movimiento ^20~41~^20~10~ ",
    ("system2.fmsg", 53): "Sensibilidad del sensor de movimiento",
    ("system2.fmsg", 54): "Ajusta la sensibilidad del sensor de movimiento del mando.",
    ("system2.fmsg", 57): "Se ha añadido el siguiente contenido:\n%ls",
    ("system2.fmsg", 58): "Se ha eliminado el contenido descargable.\nVuelve a instalarlo para acceder a él.",
    ("system2.fmsg", 59): "Se han eliminado los trajes o accesorios descargables.\nLos personajes volverán a vestir sus trajes predeterminados.\nVuelve a instalar el contenido para recuperarlo.",
    ("system2.fmsg", 66): "Aquí no se puede utilizar el modo instantánea.",
    ("system2.fmsg", 67): "El modo instantánea no está disponible.",
    ("system2.fmsg", 68): "Activa o desactiva la vibración del mando.",
    ("system2.fmsg", 69): "Activa la vibración del mando.",
    ("system2.fmsg", 70): "Desactiva la vibración del mando.",
    ("system2.fmsg", 79): "Configura los controles del teclado.",
    ("system2.fmsg", 80): "Elige si prefieres jugar solo con el teclado o con teclado y ratón.",
    ("system2.fmsg", 81): "Cambia los controles del teclado y el ratón.\nSelecciona una acción y asígnale una tecla.",
    ("system2.fmsg", 82): "Cambia los controles del teclado.\nSelecciona una acción y asígnale una tecla.",
    ("system2.fmsg", 83): "¿Quieres restablecer las teclas predeterminadas?",
    ("system2.fmsg", 84): "Esta acción ya está asignada a otra tecla.\n¿Quieres cambiar la asignación?\n%ls",
    ("system2.fmsg", 153): "Selecciona la resolución de pantalla.",
    ("system2.fmsg", 154): "Cambia el modo de ventana.",
    ("system2.fmsg", 155): "Selecciona la calidad gráfica general.",
    ("system2.fmsg", 156): "Selecciona la calidad de las texturas.",
    ("system2.fmsg", 157): "Selecciona la calidad de las sombras.",
    ("system2.fmsg", 158): "Selecciona la calidad de los reflejos locales en tiempo real.",
    ("system2.fmsg", 159): "Selecciona la calidad de los efectos.",
    ("system2.fmsg", 160): "Cambia el suavizado de bordes.",
    ("system2.fmsg", 161): "Cambia la profundidad de campo.",
    ("system2.fmsg", 162): "Cambia la oclusión ambiental.",
    ("system2.fmsg", 163): "Cambia el resplandor.",
    ("system2.fmsg", 164): "Cambia los rayos de luz.",
    ("system2.fmsg", 165): "Cambia la distancia de dibujado.",
    ("system2.fmsg", 166): "Cambia la distancia de visualización de luces puntuales.",
    ("system2.fmsg", 176): "Modifica las opciones gráficas.",
    ("system2.fmsg", 177): "Restablece las opciones predeterminadas.\n(No incluye los gráficos ni las teclas asignadas.)",
    ("system2.fmsg", 178): "¿Seguro que quieres salir del juego?",
    ("system2.fmsg", 181): "¿Quieres restablecer las opciones gráficas?",
    ("system2.fmsg", 183): "^20~26~: Confirmar",
    ("system2.fmsg", 184): "^20~27~: Volver",
    ("system2.fmsg", 185): "^20~42~ / ^20~30~: Volver",
    ("system2.fmsg", 191): "Información sobre licencias",
    ("system2.fmsg", 192): "Consulta la información sobre licencias.",
    ("system2.fmsg", 193): "^20~04~ Cambiar de cuenta",
    ("system2.fmsg", 194): "Se ha cambiado de cuenta.\nVolviendo a la pantalla de título.",
    ("system2.fmsg", 195): "^20~25~: Opciones de formato",
    ("system2.fmsg", 196): "^20~03~: Opciones de formato",
    ("system2.fmsg", 197): "Se ha desconectado el mando.\nVuelve a conectarlo.",
    ("system2.fmsg", 198): "Activa o desactiva la vibración del mando.",
    ("system2.fmsg", 199): "Activa la vibración del mando.",
    ("system2.fmsg", 200): "Desactiva la vibración del mando.",

    ("system.fmsg", 318): "¿Quieres usar %ls?",
    ("system.fmsg", 319): "¿Quieres equiparte con %ls?",
    ("system.fmsg", 320): "¿Quieres restablecer todos los ajustes?",
    ("system.fmsg", 326): "Cambia los ajustes de juego y controles.",
    ("system.fmsg", 327): "Ajusta la velocidad de movimiento de la cámara.",
    ("system.fmsg", 328): "Ajusta la imagen y el volumen.",
    ("system.fmsg", 329): "Restablece todos los ajustes predeterminados.",
    ("system.fmsg", 330): "Controles de cámara",
    ("system.fmsg", 331): "Vibración del mando",
    ("system.fmsg", 332): "Exploración: vertical",
    ("system.fmsg", 333): "Exploración: horizontal",
    ("system.fmsg", 334): "Fotografía: vertical",
    ("system.fmsg", 335): "Fotografía: horizontal",
    ("system.fmsg", 336): "Ajusta los controles de la cámara en el modo foto.",
    ("system.fmsg", 337): "Activa o desactiva la vibración del mando.",
    ("system.fmsg", 338): "Ajusta el movimiento vertical de la cámara al explorar.",
    ("system.fmsg", 339): "Ajusta el movimiento horizontal de la cámara al explorar.",
    ("system.fmsg", 340): "Ajusta el movimiento vertical de la cámara al fotografiar.",
    ("system.fmsg", 341): "Ajusta el movimiento horizontal de la cámara al fotografiar.",
    ("system.fmsg", 342): "Giroscopio ^20~41~^20~10~ ",
    ("system.fmsg", 345): "Controla la dirección de la cámara con ^20~10~.\n(Recomendado para jugadores experimentados.)",
    ("system.fmsg", 348): "Activa la vibración del mando.",
    ("system.fmsg", 349): "Desactiva la vibración del mando.",
    ("system.fmsg", 366): "Exploración: vertical",
    ("system.fmsg", 367): "Exploración: horizontal",
    ("system.fmsg", 368): "Fotografía: vertical",
    ("system.fmsg", 369): "Fotografía: horizontal",
    ("system.fmsg", 370): "Ajusta la velocidad vertical de la cámara al explorar.",
    ("system.fmsg", 371): "Ajusta la velocidad horizontal de la cámara al explorar.",
    ("system.fmsg", 372): "Ajusta la velocidad vertical de la cámara en el modo foto.",
    ("system.fmsg", 373): "Ajusta la velocidad horizontal de la cámara en el modo foto.",
    ("system.fmsg", 377): "Activa o desactiva los subtítulos.",
    ("system.fmsg", 378): "Ajusta el brillo de la pantalla.",
    ("system.fmsg", 383): "Muestra los subtítulos durante los diálogos.",
    ("system.fmsg", 384): "Oculta los subtítulos durante los diálogos.",
    ("system.fmsg", 385): "Opciones de imagen",
    ("system.fmsg", 386): "Opciones de juego",
    ("system.fmsg", 387): "Opciones de sonido",
    ("system.fmsg", 388): "Configura la imagen.",
    ("system.fmsg", 389): "Configura el juego y los controles.",
    ("system.fmsg", 390): "Configura el sonido.",
    ("system.fmsg", 391): "Restablece los ajustes predeterminados.",
    ("system.fmsg", 396): "Ajusta el modo de visualización.",
    ("system.fmsg", 397): "Elige si quieres mostrar los subtítulos durante los diálogos.",
    ("system.fmsg", 399): "Ajusta el tamaño y la posición de la imagen.",
    ("system.fmsg", 406): "Los diálogos mostrarán subtítulos.",
    ("system.fmsg", 407): "Los diálogos no mostrarán subtítulos.",
    ("system.fmsg", 408): "Estilo de control",
    ("system.fmsg", 409): "Vibración",
    ("system.fmsg", 410): "Exploración: vertical",
    ("system.fmsg", 411): "Exploración: horizontal",
    ("system.fmsg", 412): "Fotografía: vertical",
    ("system.fmsg", 413): "Fotografía: horizontal",
    ("system.fmsg", 414): "Ajusta los controles de cámara del modo foto.",
    ("system.fmsg", 415): "Activa o desactiva la vibración del mando.",
    ("system.fmsg", 416): "Ajusta el movimiento vertical de la cámara al explorar.",
    ("system.fmsg", 417): "Ajusta el movimiento horizontal de la cámara al explorar.",
    ("system.fmsg", 418): "Ajusta el movimiento vertical de la cámara al fotografiar.",
    ("system.fmsg", 419): "Ajusta el movimiento horizontal de la cámara al fotografiar.",
    ("system.fmsg", 433): "Utiliza ^20~10~ para mover la cámara en el modo foto.\n(El encuadre también aparece en la pantalla.)",
    ("system.fmsg", 434): "Activa la vibración del mando.",
    ("system.fmsg", 435): "Desactiva la vibración del mando.",
    ("system.fmsg", 600): "Puntos actuales:",
    ("system.fmsg", 601): "Puntos gastados:",
    ("system.fmsg", 611): "¿Quieres salir sin añadir los objetos?",
    ("system.fmsg", 621): "¿Volver a la pantalla de título?",
    ("system.fmsg", 707): "Volver al juego",
    ("system.fmsg", 708): "Cierra el menú de pausa y continúa la partida.",
    ("system.fmsg", 709): "Volver a la escena",
    ("system.fmsg", 710): "Cierra el menú de pausa y reanuda la escena.",
    ("system.fmsg", 711): "Saltar escena",
    ("system.fmsg", 712): "Omite la escena actual y continúa la partida.",
    ("system.fmsg", 714): "Cambia las opciones del juego.",
    ("system.fmsg", 719): "Salir del juego",
    ("system.fmsg", 720): "Salir y volver a la pantalla de título.\n(Conservarás el progreso hasta el último punto de control.)",
    ("system.fmsg", 721): "Último guardado",
    ("system.fmsg", 722): "Hace menos de 1 min",
    ("system.fmsg", 723): "Hace unos %d min",
    ("system.fmsg", 724): "Hace más de 1 hora",
    ("system.fmsg", 727): "Saldrás del episodio actual y volverás a la pantalla de\ntítulo. Puedes retomarlo desde el último punto de\ncontrol seleccionando \"Cargar partida\".",
    ("system.fmsg", 734): "A la pantalla de título",
    ("system.fmsg", 735): "Salir y volver a la pantalla de título.\nSelecciona \"Cargar partida\" para volver al último punto de control.",
    ("system.fmsg", 763): "Ordenar por",
    ("system.fmsg", 770): "Página %d / %d",
    ("system.fmsg", 772): "Guardar y bloquear",
    ("system.fmsg", 776): "¿Quieres guardar\nla fotografía seleccionada?",
    ("system.fmsg", 777): "¿Quieres guardar y bloquear\nla fotografía seleccionada?",
    ("system.fmsg", 778): "¿Quieres desbloquear\nla fotografía seleccionada?",
    ("system.fmsg", 779): "¿Quieres eliminar\nla fotografía seleccionada?",
    ("system.fmsg", 780): "No puedes eliminar\nfotografías bloqueadas.",
    ("system.fmsg", 781): "Guardando fotografía...",
    ("system.fmsg", 782): "No puedes guardar\nmás fotografías.",
    ("system.fmsg", 783): "Bloqueando fotografía...",
    ("system.fmsg", 784): "Desbloqueando fotografía...",
    ("system.fmsg", 785): "Eliminando fotografía...",
    ("system.fmsg", 786): "No se pudo cargar la fotografía.",
    ("system.fmsg", 787): "Esta fotografía no se ha\nguardado y se perderá.",
    ("system.fmsg", 789): "Este juego es una obra de ficción. Cualquier parecido\ncon personas u organizaciones reales es coincidencia.\nContiene algunas imágenes explícitas.",
    ("system.fmsg", 838): "Cambia la ropa del personaje por el traje seleccionado.",
    ("system.fmsg", 839): "Cambia las gafas del personaje por las seleccionadas.",
    ("system.fmsg", 840): "Ponle al personaje las gafas seleccionadas.",
    ("system.fmsg", 841): "Quítale al personaje las gafas seleccionadas.",
    ("system.fmsg", 842): "Ponle al personaje el accesorio seleccionado.",
    ("system.fmsg", 843): "Quítale al personaje el accesorio seleccionado.",
    ("system.fmsg", 844): "¿Quieres aplicar los cambios de vestuario?",
    ("system.fmsg", 845): "Ya puedes utilizar %ls.",
    ("system.fmsg", 855): "Has desbloqueado la dificultad PESADILLA.",
    ("system.fmsg", 857): "%ls\nya está disponible en el modo instantánea.",
    ("system.fmsg", 885): "Se han encontrado datos de la versión descargable.\nSelecciona \"Nueva partida\" para continuar.",
    ("system.fmsg", 886): "Se han encontrado datos de la versión descargable.\n¿Quieres continuar?",
    ("system.fmsg", 887): "Si empiezas una partida nueva, perderás los datos guardados.\n¿Quieres continuar?",
    ("system.fmsg", 888): "Se han encontrado datos de la versión física.\n¿Quieres crear datos para la versión descargable?\n(Se sobrescribirán los datos de la versión física.)",
    ("system.fmsg", 889): "Sobrescribiendo los datos guardados...",
    ("system.fmsg", 911): "No queda espacio para las fotografías.\nSe detendrá la transferencia.",
    ("system.fmsg", 918): "Caminar",
    ("system.fmsg", 919): "Mirar alrededor",
    ("system.fmsg", 920): "Correr",
    ("system.fmsg", 921): "Desplazamiento lateral",
    ("system.fmsg", 923): "Recoger objeto",
    ("system.fmsg", 925): "Apuntar con la cámara",
    ("system.fmsg", 926): "Apuntar hacia atrás",
    ("system.fmsg", 927): "Acción",
    ("system.fmsg", 928): "Esquivar ataque",
    ("system.fmsg", 929): "Preparar cámara",
    ("system.fmsg", 930): "Abrir menú",
    ("system.fmsg", 931): "Pausa",
    ("system.fmsg", 932): "Abrir mapa detallado",
    ("system.fmsg", 935): "Mirar rápidamente",
    ("system.fmsg", 936): "Fijar objetivo",
    ("system.fmsg", 937): "Fotografiar (atacar)",
    ("system.fmsg", 940): "Usar lente mejorada",
    ("system.fmsg", 942): "Cambiar lente mejorada",
    ("system.fmsg", 943): "Cambiar película",
    ("system.fmsg", 951): "Correr/Fijar objetivo",
    ("system.fmsg", 952): "Preparar/Guardar cámara",
    ("system.fmsg", 953): "Modo de control",
    ("system.fmsg", 957): "Selecciona el tipo de control.",
    ("system.fmsg", 958): "Usa controles similares a los de entregas anteriores.",
    ("system.fmsg", 959): "Usa controles propios de un juego de acción.",
    ("system.fmsg", 960): "Ajusta la sensibilidad del giroscopio del mando.",
    ("system.fmsg", 962): "Consulta los controles y las instrucciones del juego en el enlace.\nPuedes abrirlo desde un ordenador o un móvil.",
    ("system.fmsg", 988): "No disponible mientras no se haya instalado por completo el juego.",
    ("system.fmsg", 989): "Consulta la información del manual.",
    ("system.fmsg", 990): "Mostrar marco del visor",
    ("system.fmsg", 991): "Muestra u oculta el marco del visor en el modo foto.",
    ("system.fmsg", 994): "Muestra el marco del visor en el modo foto.",
    ("system.fmsg", 995): "Oculta el marco del visor en el modo foto.",
    ("system.fmsg", 996): "Vibración del mando",
    ("system.fmsg", 997): "Vibración del mando",
    ("system.fmsg", 53): "^20~10~: Acercar",
    ("system.fmsg", 344): "Usa el giroscopio del mando y ^20~10~ para dirigir la cámara en el modo foto.\n(Esta configuración permite mover el mando como si fuera una cámara real.)",
    ("system.fmsg", 352): "En el modo de exploración, mueve ^20~10~ hacia arriba para mirar arriba\ny ^20~10~ hacia abajo para mirar abajo.",
    ("system.fmsg", 353): "En el modo de exploración, mueve ^20~10~ hacia abajo para mirar arriba\ny ^20~10~ hacia arriba para mirar abajo.",
    ("system.fmsg", 432): "Usa el sensor de movimiento del mando y ^20~10~ para dirigir la cámara en el modo foto.\n(Esta configuración permite mover el mando como si fuera una cámara real.)",
    ("system.fmsg", 452): "Monoaural",
    ("system.fmsg", 453): "Elige el dispositivo por el que se reproducirá el sonido del juego.",
    ("system.fmsg", 454): "Elige cómo se reproducirá el sonido del juego por el televisor.",
    ("system.fmsg", 455): "Ajusta el volumen de la música del juego.",
    ("system.fmsg", 456): "Ajusta el volumen de los efectos de sonido del juego.",
    ("system.fmsg", 457): "Ajusta el volumen de las voces del juego.",
    ("system.fmsg", 460): "El televisor reproducirá sonido estéreo.",
    ("system.fmsg", 461): "El televisor reproducirá sonido monoaural.",
    ("system.fmsg", 466): "Consulta tu posición actual y tu destino.",
    ("system.fmsg", 467): "Utiliza tus objetos y consulta sus detalles.",
    ("system.fmsg", 468): "Mejora la Cámara Oscura y cambia la película y las lentes.",
    ("system.fmsg", 470): "Consulta y guarda las fotografías que has tomado.",
    ("system.fmsg", 471): "Consulta la lista de fantasmas que has fotografiado.",
    ("system.fmsg", 473): "Cambia el equipamiento de la Cámara Oscura.",
    ("system.fmsg", 475): "Gasta puntos para mejorar la Cámara Oscura.",
    ("system.fmsg", 477): "Cambia el tipo de película.",
    ("system.fmsg", 478): "Cambia la lente equipada.",
    ("system.fmsg", 480): "Gasta puntos para mejorar las funciones básicas de la Cámara Oscura.",
    ("system.fmsg", 482): "Gasta puntos para mejorar las prestaciones de una lente.",
    ("system.fmsg", 483): "Elige una ranura para equipar la lente.",
    ("system.fmsg", 581): "No se puede mejorar más.",
    ("system.fmsg", 582): "¿Quieres gastar %d puntos para mejorar la función %ls de la Cámara Oscura?",
    ("system.fmsg", 583): "¿Quieres gastar %d puntos para mejorar %ls?",
    ("system.fmsg", 584): "Puntos necesarios",
    ("system.fmsg", 585): "Nivel máximo",
    ("system.fmsg", 586): "Valor máximo",
    ("system.fmsg", 588): "Elegir dificultad",
    ("system.fmsg", 589): "Iniciar capítulo",
    ("system.fmsg", 590): "Consultar objetos",
    ("system.fmsg", 592): "Elige el capítulo que quieres jugar.",
    ("system.fmsg", 593): "Comienza el capítulo.",
    ("system.fmsg", 864): "En posesión",
    ("system.fmsg", 895): "Puntuación máxima",
    ("system.fmsg", 912): "Cámara %02d",
    # Remaining visible English abbreviations/phrases after the full corpus review.
    # Keep names, game titles, language-selection alternatives and legal notices intact.
    ("text2.fmsg", 357): "¿Kagura?",
    ("text4.fmsg", 2): "pts\n\nveces",
    ("text4.fmsg", 8): "pts\n\nveces",
    ("text3.fmsg", 467): "Nv.",
    ("text3.fmsg", 599): "Nv.",
    # The brand name is retained; only the English tagline is localized.
    ("textnew_01.fmsg", 13): "Fatal Frame\nBasado en una historia real.",
    ("textnew_01.fmsg", 825): "y todo el equipo original",
}

OVERRIDES = (SPECIAL, STORY, STORY_EXTRA, STORY_REMAINING, STORY_ONGOING, STORY_FINAL, TUTORIAL_FINAL, ARTBOOK, ARTBOOK_EXTENDED, ARTBOOK_LORE, BONUS_UI, CREDITS, SCENE, LORE, SCENERY, CINEMATICS, RECORDINGS, GALLERY, ACCESSORIES, TEXT6, TEXT6_TAIL, TEXT7, TEXT8, TEXT9, TEXT2, UI)


def translation_for(key, english, fallback=None):
    for overrides in OVERRIDES:
        if key in overrides:
            return overrides[key]
    return COMMON.get(english, fallback)


def main():
    result = []
    present = set()
    originals = list(source_files())
    # Reuse translations only when all manually translated occurrences of the
    # *exact original English string* agree. Ambiguous contextual phrases are
    # deliberately excluded; markup/control codes remain byte-for-byte equal.
    memory = defaultdict(set)
    for path, data in originals:
        for index, en in enumerate(data.strings):
            key = (path.name, index)
            es = translation_for(key, en)
            if es is not None and es != en:
                memory[en].add(es)
    safe_memory = {en: next(iter(values)) for en, values in memory.items() if len(values) == 1}
    for path, data in originals:
        for index, en in enumerate(data.strings):
            key = (path.name, index)
            es = translation_for(key, en, safe_memory.get(en))
            if es is None:
                continue
            present.add(key)
            if es == en:
                continue
            result.append({"file": path.name, "index": index,
                           "source_sha256": digest(en), "es": es})
    missing = set().union(*(set(o) for o in OVERRIDES)) - present
    if missing:
        raise ValueError(f"Overrides missing from English sources: {missing}")
    TRANSLATIONS.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(result)} original-English translations in {TRANSLATIONS}")

if __name__ == "__main__":
    main()
