# FATAL FRAME / PROJECT ZERO: Mask of the Lunar Eclipse — castellano (es-ES)

Proyecto privado para localizar los recursos de la versión PC de *Mask of the Lunar Eclipse*. Repositorio principal: `E:\Proyectos\fatal-frame-mol-es` (GitHub privado: `rubocopter/fatal-frame-mol-es`).

## Estado del borrador (29/10/2026)

- **7.329 entradas FMSG traducidas** sobre 9.030 entradas originales, en 13 archivos de `binary/text/USen`. Se parte exclusivamente de los originales ingleses y se comprueba la huella del texto original por entrada. El parche de terceros sirvió para localizar los recursos, nunca como fuente lingüística.
- **977 entradas señaladas como pendientes por el detector genérico.** No equivalen a 977 frases en inglés: entre ellas hay secuencias de control, números, resoluciones, nombres propios, títulos de la saga, etiquetas que se escriben igual en castellano y textos legales de bibliotecas. Se conservan deliberadamente los avisos legales y los créditos personales.
- Fuente `binary/font/JP/default.g1n` extendida para `á í ó ú ñ Á Í Ó Ú Ñ ¿ ¡` y comprobación automática de cobertura de glifos.
- **19 rótulos gráficos en castellano en cuatro KSCL** (`binary/layout/en`): pulsa cualquier botón, nueva partida, fácil y encabezados de menús. Se mantienen logotipos, caligrafía japonesa y demás gráficos no textuales.
- **Solo existe una prueba previa y breve dentro del juego:** el usuario vio diálogos y tutoriales en español, con tildes correctas. Los cuatro KSCL nuevos **aún no se han comprobado en el juego**, ni se ha completado una partida con el parche actualizado. Sigue siendo una **versión de prueba**, sin QA editorial ni visual completa.

El paquete compilado se genera localmente en `E:\Proyectos\fatal-frame-mol-es\out\fatal-frame-mol-es-draft\`. Nunca se suben a GitHub los archivos originales del juego ni los paquetes compilados.

## Requisitos y rutas (Windows)

- Juego: `E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse`.
- Proyecto y herramientas de construcción: `E:\Proyectos\fatal-frame-mol-es`.
- Copia de seguridad verificada del parche anterior: `E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse\.fatal-frame-es-originals` — **no borrar**.
- Python 3.10+ (`py` en PowerShell) y Pillow. Instalar solo si faltan: `cd 'E:\Proyectos\fatal-frame-mol-es'; py -m pip install -r 'E:\Proyectos\fatal-frame-mol-es\requirements.txt'`.
- Fuente de Windows `C:\Windows\Fonts\georgia.ttf` para generar los rótulos KSCL.

Las herramientas de terceros estudiadas están bajo `E:\Proyectos\fatal-frame-mol-es\tools\` y se excluyen de Git. **No hace falta abrir sus interfaces ni instalar nada de ellas para aplicar el parche**: los scripts del proyecto generan los archivos necesarios.

## Instalar o actualizar el borrador

**Cerrar el juego** antes de ejecutar comandos. Desde PowerShell:

```powershell
cd 'E:\Proyectos\fatal-frame-mol-es'
py -X utf8 manage_patch.py status --game-root 'E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse'
```

La instalación de este equipo conserva el **borrador anterior de 14 archivos**. Para pasar al parche nuevo con 18 archivos, ejecutar:

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

**Texturas HD:** los 358 recursos del pack revisado afectan a `binary/character`, `binary/stage` y otros recursos de `binary/layout`, pero no coinciden con los 18 archivos del parche. No es necesario reinstalar el pack HD. No se han modificado otros mods.

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

**Es fundamental usar la copia original para FMSG y G1N**, porque el juego tiene un borrador aplicado; el exportador bloquea expresamente intentar usarlo como origen inglés. Para KSCL el generador usa los cuatro originales de la instalación mientras están intactos y, después de actualizar el juego, lee automáticamente los originales verificados de `.fatal-frame-es-originals`.

El código, QA y pruebas se documentan en [docs/review-2026-10-29.md](docs/review-2026-10-29.md). Los archivos `work/`, `out/`, `tools/`, `translations_from_english.json` y los archivos originales del juego están excluidos del repositorio. Los derechos del juego pertenecen a sus titulares; proyecto no oficial, sin relación con KOEI TECMO.
