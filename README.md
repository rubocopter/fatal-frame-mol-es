# FATAL FRAME / PROJECT ZERO: Mask of the Lunar Eclipse — Traducción al español (España)

Proyecto **privado y en desarrollo** para traducir al castellano los textos de la versión de PC de *FATAL FRAME / PROJECT ZERO: Mask of the Lunar Eclipse*.

La traducción se elabora a partir de los archivos **originales en inglés (`USen`)**. Un parche de terceros se utilizó inicialmente para identificar la ubicación de los recursos; **sus textos no son la base de esta traducción**.

## Estado

- **Borrador:** 7.324 entradas traducidas de un total de 9.030 cadenas FMSG.
- El resto incluye textos pendientes de revisión y entradas que deben mantenerse intactas (nombres propios, códigos, créditos personales y avisos legales). También se han localizado y traducido los encabezados de los créditos.
- Los 13 archivos FMSG se reconstruyen y verifican contra el texto inglés original.
- Fuente G1N adaptada para `á í ó ú ñ Á Í Ó Ú Ñ ¿ ¡`.
- **Prueba preliminar en el juego (29/10/2026):** el usuario confirmó diálogos y tutoriales en español, con tildes aparentemente correctas, tras unos minutos de juego. No se ha validado toda la aventura ni la presentación de todos los textos.
- **Pendiente:** comprobar el ajuste de líneas, la calidad final de la traducción y los gráficos del menú principal. No hay una versión final aprobada.

## Contenido del repositorio

Los módulos `*_translations.py`, `story_*.py` y `manual_translations.py` contienen la traducción editorial. `fmsg_format.py`, `clean_translation.py` y `font_support.py` se encargan de reconstruir los recursos desde una instalación legítima. `manage_patch.py` empaqueta e instala el borrador de forma reversible; `test_manage_patch.py` comprueba instalación, restauración y recuperación ante fallos.

**El repositorio no incluye archivos originales del juego, volcados del texto inglés, archivos de fuentes/recursos propietarios ni parches compilados.** Estos archivos se generan localmente. Los derechos del juego corresponden a sus titulares. Proyecto no oficial y sin relación con KOEI TECMO.

## Preparación local (Windows)

Requisitos: Python 3.10+ y una copia del juego para PC con los archivos de texto originales en inglés.

```powershell
py -m pip install -r requirements.txt
$env:FF_MOL_GAME_DIR = 'E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse'
```

La variable `FF_MOL_GAME_DIR` debe apuntar a la carpeta del juego en tu equipo. Si no se define, se usa la ruta local de desarrollo de Windows.

**Si ya está instalado un parche de prueba**, la compilación necesita los originales: utiliza como `FF_MOL_GAME_DIR` la carpeta `.fatal-frame-es-originals` de una copia de seguridad verificada. Para el subcomando `package`, `--game-root` también debe apuntar a esa carpeta de originales; para `status`, `install` y `restore`, apunta a la instalación real del juego. No sustituyas ni borres los archivos del juego para compilar.

```powershell
py -X utf8 clean_translation.py export
py -X utf8 manual_translations.py
py -X utf8 clean_translation.py build
py -X utf8 font_support.py
py -X utf8 manage_patch.py package --game-root "$env:FF_MOL_GAME_DIR"
py -X utf8 manage_patch.py status --game-root "$env:FF_MOL_GAME_DIR"
```

La salida se almacena en `out/` y las evidencias de compilación y QA en `work/`. Todas estas carpetas están excluidas de Git. `translations_from_english.json` también se genera localmente.

## Prueba del borrador

Solo para pruebas y con el juego cerrado, después de verificar que `status` indica los 14 recursos originales:

```powershell
py -X utf8 manage_patch.py install --game-root "$env:FF_MOL_GAME_DIR"
py -X utf8 manage_patch.py restore --game-root "$env:FF_MOL_GAME_DIR"
```

La instalación comprueba hashes SHA-256, crea una copia de seguridad en `.fatal-frame-es-originals` dentro del directorio del juego y restaura los originales bajo demanda. **Conserva esa copia de seguridad.** La prueba visual en el juego ha sido breve; la traducción sigue siendo un borrador.

## Menú principal y gráficos de interfaz

Varios rótulos ingleses están **dibujados en texturas KSCL**, por ejemplo `Press Any Button` en `binary/layout/en/title_layout.kscl` y `New Game` en `binary/layout/en/title_layout_menu_parts.kscl`. Otros encabezados se encuentran en `cmn_title_mission.kscl`. Esos gráficos no se traducen editando los FMSG: requieren una adaptación de texturas, empaquetado y pruebas independientes. La instalación actual solo sustituye textos FMSG y la fuente; por eso pueden permanecer rótulos del menú en inglés aunque existan traducciones FMSG equivalentes.

La revisión técnica y editorial del 29/10/2026 queda documentada en [docs/review-2026-10-29.md](docs/review-2026-10-29.md).

## Compatibilidad con packs de texturas HD

El pack HD comprobado contiene 358 archivos (`.gmpk`, `.kscl` y `.kslt`) distribuidos en `binary/character`, `binary/stage` y `binary/layout`. Todos están presentes en la instalación de prueba y sus rutas no se solapan con las que modifica este parche: 13 archivos `binary/text/USen/*.fmsg` y la fuente `binary/font/JP/default.g1n`.

Por tanto, el instalador y la restauración de esta traducción conservan los recursos del pack HD. No es necesario reinstalar las texturas ni integrarlas en el parche de traducción. Esta comprobación se limita al pack revisado; otros mods que alteren textos o fuentes podrían entrar en conflicto.

## Pruebas

```powershell
py -X utf8 -m unittest -v test_manage_patch
```

El trabajo editorial seguirá en los módulos de traducción. Antes de publicar una versión distribuible habrá que revisar cobertura, terminología, límites de texto y compatibilidad con los glifos españoles.
