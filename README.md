# FATAL FRAME / PROJECT ZERO: Mask of the Lunar Eclipse — castellano

Repositorio de desarrollo privado de la traducción es-ES de la versión PC. Las fuentes de traducción y los generadores viven aquí; la distribución pública se preparará en **otro repositorio de release**, como en Chaos;Head Noah. No se incluyen originales del juego, extracciones ni paquetes compilados en Git.

## Estado actual

- 7.331 entradas traducidas de 9.030, en los 13 FMSG originales ingleses. Las 975 entradas señaladas por el detector incluyen controles, nombres, números, idiomas y avisos legales; no equivalen a 975 frases pendientes.
- Fuente original extendida para las letras españolas y signos de apertura.
- **460 texturas localizadas en 89 archivos de interfaz: 36 KSCL y 53 KSLT.** Incluyen menú principal, dificultad, Opciones, categorías y pestañas, pausa, capítulos, resultados, Cámara Oscura y 21 imágenes de tutorial. Estas últimas contienen 120 regiones de texto repintadas.
- Se traducen también los literales de interfaz contenidos dentro de ocho layouts. Las etiquetas con poco espacio utilizan abreviaturas, conservando su capacidad y sus offsets.
- **Artbook y sus gráficos se mantienen en inglés por petición expresa.** Los textos FMSG del artbook ya traducidos se conservan. No se alteran logotipos, créditos personales, símbolos japoneses ni ilustraciones.
- El paquete contiene **103 recursos**: 13 FMSG, una fuente, 36 KSCL y 53 KSLT. El estado de instalación se consulta con el comando indicado abajo. La revisión de una partida completa sigue pendiente.

La causa del inglés persistente en los menús era que la compilación anterior solo cambiaba los gráficos incluidos dentro de KSCL: quedaban sin localizar las tablas **KSLT externas** en `binary/layout/en/ex_texture`. Ahora se procesan ambas familias. Los nuevos rótulos se ajustan al color, tamaño, alineación y estados de iluminación del original; la tipografía de Windows es una aproximación estética.

## Organización

| Ruta | Contenido |
| --- | --- |
| `translations/` | Traducciones revisadas, por archivo y entrada FMSG |
| `manual_translations.py`, `clean_translation.py` | Generación de traducciones y compilación de textos |
| `fmsg_format.py`, `font_support.py` | Formato FMSG y ampliación de la fuente |
| `layout_translation.py` | Lector y compilador de KSCL/KSLT |
| `external_labels.py`, `inline_labels.py`, `tutorial_labels.py` | Traducciones gráficas, literales y regiones de tutorial |
| `label_style.py`, `external_style.py`, `mixed_labels.py` | Tipografía, halos y conservación de iconos |
| `build.py`, `manage_patch.py`, `audit_graphics.py` | Reconstrucción, paquete/instalación y comparación visual |
| `tests/` | Integridad de recursos y ciclo de parche en instalaciones temporales |
| `docs/` | Documentación actual; notas antiguas en `docs/history/` |
| `work/` | Compilación y QA locales, excluidos de Git |
| `out/` | Paquete actual y ZIP verificado, excluidos de Git |
| `tools/README.md` | Referencias de formatos; sin clones de editores anidados |

Se han retirado el antiguo flujo basado en un parche ajeno, candidatos automáticos no usados, pruebas de estilo antiguas y paquetes sustituidos. Las traducciones actuales se generan exclusivamente desde el inglés original y conservan huellas del texto fuente. Los originales respaldados del juego no forman parte de esta limpieza.

## Reconstrucción completa

Requisitos: Windows, Python 3.10+ y Pillow (`py -m pip install -r requirements.txt`). Los rótulos utilizan las fuentes instaladas Times New Roman, Arial y Segoe Print, sin distribuirlas.

```powershell
cd 'E:\Proyectos\fatal-frame-mol-es'
py -X utf8 build.py
```

El comando exporta los originales, genera traducciones, compila textos y fuente, recompone los gráficos, valida el paquete, ejecuta las pruebas, genera comparaciones desde los archivos recompresos y comprueba el ZIP. **No instala nada en el juego.** Utiliza el respaldo original verificado si ya hay un parche instalado.

Salidas actuales:

- `out/fatal-frame-mol-es-draft/`: paquete preparado, con manifiesto SHA-256 y gestor de instalación.
- `out/fatal-frame-mol-es-latest.zip` y `.zip.sha256`: copia comprimida verificada.
- `work/graphics_review/`: comparaciones original/español e inventario de traducciones.
- `work/clean_es_qa.json`, `work/font_qa.json`, `work/layout_es_qa.json`: informes de compilación.

Para repetir solo las pruebas o las láminas de comparación:

```powershell
py -X utf8 -m unittest discover -s tests -v
py -X utf8 audit_graphics.py
```

## Instalación de desarrollo

Juego local: `E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse`. Respaldo original: `.fatal-frame-es-originals` dentro de esa instalación; **no borrar**. Incluye los originales HD que ya estaban instalados antes de traducir.

Con el juego cerrado:

```powershell
py -X utf8 manage_patch.py status
py -X utf8 manage_patch.py upgrade
```

`upgrade` migra los borradores anteriores de 14, 18, 31, 42 o 45 recursos, comprueba cada archivo y amplía el respaldo. Para una instalación original se usa `install`; para recuperar sus originales, `restore`. Se puede indicar `--game-root <ruta>`. Este gestor de desarrollo rechaza el juego abierto, versiones diferentes y modificaciones inesperadas; recupera los archivos anteriores si falla una escritura.

Para instalar desde el paquete compilado se ejecuta su propio `manage_patch.py`. Requiere únicamente Python; Pillow y los generadores son dependencias de desarrollo.

## Instalador de distribución

La portada y las descargas se mantienen en el repositorio privado [fatal-frame-mol-es-release](https://github.com/rubocopter/fatal-frame-mol-es-release), con Ko-fi de [onitaku](https://ko-fi.com/onitaku). Su checkout local es `E:\Proyectos\fatal-frame-mol-es-release`. Contiene documentación y gráficos de presentación; el EXE se aloja en Releases.

El instalador gráfico sustituye los **103 recursos**, aunque ya contengan otros mods, sin exigir un paquete HD ni hashes originales. Guarda el estado anterior exacto en `.fatal-frame-es-installer`, independiente de `.fatal-frame-es-originals`. **Restaurar copia** recupera los recursos anteriores, incluidos sus mods. El EXE incluye Python y Tcl/Tk; el usuario solo selecciona la carpeta del juego.

Para construirlo a partir del paquete generado por `build.py`, con Python 3.14 x64:

```powershell
py -m pip install -r requirements-installer.txt
py -X utf8 -m installer.build_release
py -X utf8 -m installer.verify_release
```

Salidas: `out/release/v0.1.0/FATAL-FRAME-MOL-ES-Setup.exe`, `SHA256SUMS.txt` y `THIRD_PARTY_NOTICES.txt`. `verify_release` ejecuta el EXE compilado sobre una copia temporal de los 103 recursos, simula dos mods y verifica instalación y restauración exacta. Lee los respaldos locales para preparar esa copia y no escribe en el juego. Su informe `validation.json` es local y no se sube como archivo de distribución.

`installer/core.py` implementa las operaciones y su recuperación; `installer/gui.py` contiene la interfaz. Las pruebas están en `tests/test_installer.py`.

## Documentación

- [Formatos gráficos, conservación y verificación](docs/graphics-pipeline.md).
- [Herramientas de referencia](tools/README.md).
- [Notas históricas](docs/history/README.md).

Proyecto no oficial, sin relación con KOEI TECMO. Los derechos del juego pertenecen a sus titulares.
