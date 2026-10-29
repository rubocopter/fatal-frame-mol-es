# FATAL FRAME / PROJECT ZERO: Mask of the Lunar Eclipse — castellano (es-ES)

Proyecto privado para localizar los recursos de la versión PC de *Mask of the Lunar Eclipse*. Repositorio principal: `E:\Proyectos\fatal-frame-mol-es` (GitHub privado: `rubocopter/fatal-frame-mol-es`).

## Estado instalado (29/10/2026)

- **7.331 entradas FMSG traducidas** sobre 9.030 entradas originales, en 13 archivos de `binary/text/USen`. Se parte exclusivamente de los originales ingleses y se comprueba la huella del texto original por entrada. El parche de terceros sirvió para localizar los recursos, nunca como fuente lingüística. El último repaso localizó también el lema «Basado en una historia real» y la línea de créditos «y todo el equipo original».
- **975 entradas conservadas y señaladas por el detector genérico.** No equivalen a 975 frases pendientes en inglés: se comprobaron las restantes entradas con letras y predominan secuencias de control, números, resoluciones, nombres propios, títulos oficiales de la saga, etiquetas que se escriben igual en castellano, otras lenguas del selector y textos legales de bibliotecas. Se conservan deliberadamente los avisos legales y los créditos personales.
- Fuente `binary/font/JP/default.g1n` extendida para `á í ó ú ñ Á Í Ó Ú Ñ ¿ ¡` y comprobación automática de cobertura de glifos.
- **118 rótulos gráficos en castellano en 28 KSCL** (`binary/layout/en`): menú principal, dificultad, pestañas, Cámara Oscura, inventario, galería de fotos, lista de fantasmas, misiones, resultados, bonificaciones, fin de partida y otras pantallas. Se mantienen logotipos, caligrafía japonesa y gráficos no textuales. Los estados normal/seleccionado/animado se han recompuesto por separado. El acabado aprobado en la muestra se ha extendido a los 118 rótulos: Times New Roman normal, negrita y cursiva, halo separado del núcleo de las letras y Segoe Print para el aviso manuscrito de guardado. Es una aproximación a las fuentes originales, no una reproducción exacta.
- **Instalado y verificado en el juego de este equipo:** los 42 archivos (13 FMSG, una fuente G1N y 28 KSCL) y sus respectivos originales respaldados coinciden con el manifiesto SHA-256. Se verificaron los 358 archivos del pack HD: 347 permanecen idénticos en el juego y once KSCL del pack se conservan byte a byte en el respaldo, con la traducción superpuesta en la instalación. La prueba anterior dentro del juego fue breve (diálogos y tutoriales en español). **Esta revisión de los menús todavía no se ha comprobado dentro del juego** ni se ha completado una partida. Sigue siendo una **versión de prueba**.

El paquete compilado está en `E:\Proyectos\fatal-frame-mol-es\out\fatal-frame-mol-es-draft\`. ZIP de esta revisión: `E:\Proyectos\fatal-frame-mol-es\out\fatal-frame-mol-es-esES-2026-10-29-7331-42-assets-estilo.zip` (SHA-256 `41e73bf4787a59df89cd589d8f58411f4984bda252970119e1ea70332185a86e`; comprobante `.zip.sha256` contiguo). El ZIP contiene 45 entradas comprobadas tras comprimir: 42 recursos, manifiesto, instalador y guía. Nunca se suben a GitHub los originales del juego ni los paquetes compilados.

## Requisitos y rutas (Windows)

- Juego: `E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse`.
- Proyecto y herramientas de construcción: `E:\Proyectos\fatal-frame-mol-es`.
- Copia de seguridad verificada del parche anterior: `E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse\.fatal-frame-es-originals` — **no borrar**.
- **Para aplicar el parche compilado:** Python 3.10+ (`py` en PowerShell). No se necesita Pillow ni ejecutar las herramientas de terceros.
- **Solo para regenerar** el paquete a partir de los archivos originales: instalar Pillow con `cd 'E:\Proyectos\fatal-frame-mol-es'; py -m pip install -r 'E:\Proyectos\fatal-frame-mol-es\requirements.txt'`. El generador KSCL utiliza las fuentes de Windows `C:\Windows\Fonts\times.ttf`, `timesbd.ttf`, `timesi.ttf` y `segoepr.ttf`.

Las herramientas de terceros estudiadas están bajo `E:\Proyectos\fatal-frame-mol-es\tools\` y se excluyen de Git. **No hace falta abrir sus interfaces ni instalar nada de ellas para aplicar el parche**: los scripts del proyecto generan los archivos necesarios.

## Instalar o actualizar el borrador

**Cerrar el juego** antes de ejecutar comandos. Desde PowerShell:

```powershell
cd 'E:\Proyectos\fatal-frame-mol-es'
py -X utf8 manage_patch.py status --game-root 'E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse'
```

**La actualización a 42 recursos y la posterior revisión de acabado (42→42) ya se realizaron y verificaron el 29/10/2026.** `status` debe mostrar `installed: 42` y `Verified original backup: yes`. El instalador también admite migrar desde los borradores de 14, 18 o 31 recursos. Solo si alguna otra instalación sigue pendiente de actualizar, ejecutar:

```powershell
py -X utf8 manage_patch.py upgrade --game-root 'E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse'
```

Para una instalación original sin parche anterior (solo cuando `status` indique todos los archivos `original`):

```powershell
py -X utf8 manage_patch.py install --game-root 'E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse'
```

Para restaurar los originales después de instalar o actualizar **esta versión**, manteniendo la copia de seguridad:

```powershell
py -X utf8 manage_patch.py restore --game-root 'E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse'
```

`status` distingue `previous draft`, `installed`, `original` y archivos ajenos al parche. `upgrade` verifica SHA-256 de los antiguos archivos parcheados, de los respaldos originales y de los nuevos KSCL. Rechaza un recurso modificado por un tercero, y tiene recuperación ante errores de escritura. Si la comprobación falla, revisar el error; no copiar archivos manualmente sobre el juego.

**Texturas HD:** el pack ubicado en `C:\Users\Oni\Downloads\fatal frame 4 texturas hd\binary` incluye 358 archivos. De ellos, 347 siguen intactos en el juego. Los once KSCL que coinciden con el parche se han traducido partiendo de los archivos HD instalados: `camera_menu_parts`, `cmn_tab`, `ghostlist_layout`, `mission_select_tab`, `audio_list_parts`, `change_costume_parts`, `gallery_image_parts`, `ghostlist_list_parts`, `item_exchange_parts`, `item_list_parts` y `menu_synopsis_list_parts`. Sus versiones HD originales se preservan y verifican por SHA-256 en `.fatal-frame-es-originals`; `restore` recupera exactamente esas versiones. No se necesita reinstalar el pack HD.

## Volver a generar el paquete desde los originales

Si se modifican las traducciones en los módulos `*_translations.py` o los recursos KSCL, ejecutar en `E:\Proyectos\fatal-frame-mol-es`:

```powershell
cd 'E:\Proyectos\fatal-frame-mol-es'
$env:FF_MOL_GAME_DIR = 'E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse\.fatal-frame-es-originals'
py -X utf8 clean_translation.py export
py -X utf8 manual_translations.py
py -X utf8 clean_translation.py build
py -X utf8 font_support.py
$env:FF_MOL_GAME_DIR = 'E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse'
py -X utf8 layout_translation.py
py -X utf8 manage_patch.py package --game-root 'E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse\.fatal-frame-es-originals'
py -X utf8 -m unittest -v test_manage_patch
```

**Es fundamental usar la copia original para FMSG y G1N**, porque el juego tiene un borrador aplicado; el exportador bloquea expresamente intentar usarlo como origen inglés. El generador KSCL lee los originales verificados en `.fatal-frame-es-originals`, incluidas las once texturas HD de interfaz; solo para recursos nuevos que nunca fueron gestionados utiliza el archivo vivo del juego. El script comprueba estructura y metadatos de los KSCL.

La ampliación del acabado está documentada en [docs/style-rollout-2026-10-29.md](docs/style-rollout-2026-10-29.md). El código, QA y pruebas se documentan en [docs/review-2026-10-29.md](docs/review-2026-10-29.md). Los archivos `work/`, `out/`, `tools/`, `translations_from_english.json` y los archivos originales del juego están excluidos del repositorio. Los derechos del juego pertenecen a sus titulares; proyecto no oficial, sin relación con KOEI TECMO.
