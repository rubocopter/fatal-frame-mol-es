# Maiden of Black Water — plan completo de traducción al castellano

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** crear una traducción propia es-ES de Maiden of Black Water para PC, desde los originales ingleses, incluidos sus gráficos, siguiendo el proceso desarrollado para Mask of the Lunar Eclipse.

**Architecture:** proyecto independiente que adapta los lectores FMSG/G1N/KSCL/KSLT, la edición gráfica y el sistema de compilación, auditoría y restauración de Lunar Eclipse. Los originales se conservan autenticados; las traducciones y las regiones gráficas se declaran por separado; cada compilación genera recursos verificables sin instalar automáticamente.

**Tech Stack:** Windows x64, Python 3.10+ y Pillow para desarrollo; Python 3.14 x64, Tk y PyInstaller como referencia inicial para el instalador autónomo. Fijar las versiones efectivamente utilizadas al comenzar.

**Spec:** sección 1 de este documento; implementación de referencia en `E:\Proyectos\fatal-frame-mol-es`, especialmente su README, `docs/graphics-pipeline.md` y `docs/release-design.md`.

Fecha: **30 de octubre de 2026**. Estado: **documentación para ejecución futura**. Solo se ha realizado reconocimiento de archivos. No existe todavía una traducción ni un instalador propios de Maiden of Black Water.

## 1. Encargo y criterios de alcance

El usuario prefiere repetir el trabajo propio realizado con Lunar Eclipse: traducir del inglés al castellano de España, incluyendo los textos dibujados en imágenes. La traducción comunitaria existente no se utilizará como base ni como fuente de textos, fuentes o gráficos.

Se cubrirán historia, subtítulos, notas, documentos, descripciones, tutoriales, mensajes del sistema, interfaz, opciones, capítulos, resultados, Cámara Oscura, modo foto, mapas y extras presentes en la instalación. Inventariar también artbooks y sus comentarios e imágenes con texto inglés. La excepción de dejar gráficos del artbook en inglés pertenecía a Lunar Eclipse; no se aplica automáticamente a este encargo de cobertura completa.

Traducir todo el inglés visible que pertenezca a esas funciones. Conservar nombres propios cuando proceda, créditos personales, marcas, logotipos, símbolos japoneses, ilustraciones y elementos sin contenido traducible. El título comercial del juego se conserva. Cada conservación debe quedar clasificada y justificada; un identificador interno en inglés no equivale a una frase pendiente.

La entrega final debe poder reconstruirse desde originales autenticados y fuentes de traducción, instalarse con una interfaz sencilla y restaurar exactamente el estado anterior. Distinguir siempre cobertura de traducción, validación estructural, revisión visual y revisión dentro del juego. Ninguna cifra sustituye las otras comprobaciones.

## 2. Restricciones globales

- Fuente lingüística: inglés original de esta edición PC. Idioma de destino: es-ES.
- No importar traducciones, fuentes modificadas o imágenes de parches ajenos.
- Mantener independientes los proyectos y las instalaciones de ambos juegos.
- La compilación solo lee originales y escribe en las carpetas de trabajo y salida del proyecto nuevo.
- Las traducciones se vinculan a ruta, índice o nombre de textura y SHA-256 de la fuente inglesa.
- Conservar el número de posiciones FMSG, las entradas vacías y los códigos de control.
- No asumir las cantidades de Lunar Eclipse: 13 FMSG, 103 recursos y sus listas de gráficos son específicas de aquel juego.
- Usar un inventario explícito de recursos seleccionados; no traducir indiscriminadamente todos los idiomas ni todos los archivos que contienen palabras inglesas.
- En gráficos, preservar dimensiones, estructura y bytes ajenos a las regiones declaradas, con la granularidad del formato de compresión.
- Separar los originales de desarrollo del respaldo del estado previo del usuario al instalar.
- No incluir originales, extracciones completas, partidas, respaldos, ejecutables del juego ni fuentes comerciales en Git o en la distribución.
- Publicar o crear repositorios remotos queda para cuando el usuario solicite esa fase; esta documentación no ejecuta ninguna de esas acciones.

## 3. Punto de partida comprobado

Instalación: `E:\Games\FATAL FRAME - PROJECT ZERO Maiden of Black Water`.

| Elemento | Resultado observado | Límite de la comprobación |
| --- | --- | --- |
| Ejecutable | `FATAL_FRAME_MOBW.exe`, nativo x64, versión declarada 1.0.0.5 | Repetir huella y versión antes de trabajar |
| Texto inglés | 124 rutas en `binary/text/USen`; 123 FMSG válidos | `RTP_M10A.fmsg` tiene cero bytes; excluirlo de lectura y conservarlo intacto |
| Reconstrucción FMSG | Los 123 archivos válidos se leen y reconstruyen con igualdad exacta de bytes | No se ha probado texto modificado en el juego |
| Posiciones FMSG | 828.487 posiciones; 8.333 entradas no vacías | Incluye identificadores y otros textos conservables; no son 828.487 frases |
| Fuente | `binary/font/JP/Font_default.g1n`, 1.929 glifos; estructura aceptada por el lector | Faltan `áíóúñÁÍÓÚÑ¿¡`; comprobar todos los caracteres que aparezcan en la traducción |
| Layouts ingleses | 1.019 KSCL en `binary/layout/en` | Tablas leídas; falta revisión visual de su contenido |
| Texturas externas | 1.041 KSLT en `binary/layout/ex_texture` | No trasladar la ruta `en/ex_texture` de Lunar Eclipse |
| Conjunto gráfico anterior | 6.251 texturas: 4.841 BC3 y 1.410 RGBA | Se decodificaron cinco muestras; no se ha verificado la recompresión |
| Recursos compartidos | `binary/layout/common_texture/SLECommonTextures.kslt` y `binary/layout/btn_texture/btn_tex.kslt` | No incluidos en el recuento ni en la prueba de lectura anterior |

Hay otros idiomas bajo `binary/text` y `binary/layout`. La ubicación de una textura compartida no demuestra que sea exclusiva del inglés: comprobar qué versión usa el juego.

El reconocimiento automático atribuyó id Tech por la extensión `.wad` de algunos escenarios. Es un falso positivo de la heurística; no sirve para decidir las herramientas ni identifica el motor.

El reconocimiento original está guardado localmente en `E:\Proyectos\fatal-frame-mol-es\work\mobw-recon\MODDING_PLAN.md` y `MODLOG.md`. Esas notas están excluidas de Git; este documento conserva los datos necesarios para retomar el trabajo.

## 4. Cómo se hizo en Lunar Eclipse y qué reutilizar

Se terminó usando una cadena propia en Python/Pillow. Las herramientas externas sirvieron para estudiar formatos, sin ser necesarias para compilar el resultado actual. La traducción actual se genera desde el inglés original y conserva huellas de la fuente.

| Referencia en `E:\Proyectos\fatal-frame-mol-es` | Uso en Maiden of Black Water | Adaptación necesaria |
| --- | --- | --- |
| `fmsg_format.py` | Leer tablas UTF-16 y reconstruir sus bloques | Configuración propia; gestionar explícitamente el archivo vacío |
| `clean_translation.py`, `manual_translations.py`, `translations/` | Exportar originales, declarar traducciones y compilar | Sustituir inventario de 13 archivos, entradas y huellas; nuevas traducciones completas |
| `font_support.py` | Ampliar la fuente con glifos derivados del original | Nombre `Font_default.g1n`, métricas y caracteres reales de este juego |
| `layout_translation.py` | Leer KSCL y KSLT; componer imágenes conservando estructura | Descubrir rutas, recursos, nombres y formatos; nuevas declaraciones |
| `external_labels.py`, `inline_labels.py`, `tutorial_labels.py` | Texturas externas, literales del layout y zonas de capturas | Crear todos los mapas de texto y coordenadas para este título |
| `label_style.py`, `external_style.py`, `mixed_labels.py` | Medir estilo, alinear, dibujar rótulos y conservar iconos | Revisar estética y fondos por familia; no heredar coordenadas |
| `audit_graphics.py`, `tests/test_layout_assets.py` | Comparar originales y recursos recompilados | Máscaras y listas procedentes del inventario nuevo |
| `build.py`, `manage_patch.py` | Compilar, manifestar, empaquetar y gestionar instalación de desarrollo | Ejecutable, rutas, inventarios, respaldos y versión de Maiden of Black Water |
| `installer/`, `installer_entry.py` | Instalador gráfico y prueba del EXE compilado | Identidad, icono, título, payload y detección del juego propios |

Lecciones que deben convertirse en comprobaciones:

1. Revisar tanto las texturas incrustadas en KSCL como las KSLT externas. Cambiar solo KSCL dejó menús en inglés en Lunar Eclipse.
2. Revisar los literales UTF-16 visibles dentro de layouts, aunque no aparezcan en FMSG.
3. Los tutoriales contienen capturas con otros menús y leyendas dentro de la imagen. Cada región se traduce individualmente.
4. Normal, seleccionado, iluminado, animado y foco pueden usar texturas distintas. Cubrir todos los estados.
5. Las comparaciones visuales deben salir del recurso recompilado y reabierto; una imagen intermedia correcta no demuestra que el archivo final lo sea.
6. En BC3 se sustituyen únicamente los bloques 4×4 que intersectan las regiones editadas. En RGBA se conservan los píxeles externos.
7. Abreviar de forma coherente cuando un campo fijo no admita una traducción completa. No cambiar offsets ni confundir un identificador con texto visible.
8. Mantener originales autenticados para recompilar cuando ya esté instalado un borrador. Nunca tomar el español instalado como si fuera inglés original.
9. El instalador de usuario respalda el estado real anterior, incluidos otros mods; ese respaldo no debe convertirse automáticamente en fuente inglesa de desarrollo.
10. La revisión de una partida completa seguía pendiente en Lunar Eclipse. Para este juego debe figurar como una fase propia y no darse por realizada por analogía.

## 5. Organización propuesta del proyecto nuevo

Ruta propuesta para la ejecución futura: **`E:\Proyectos\fatal-frame-mobw-es`**. No se ha creado como parte de esta documentación.

Mantener la organización sencilla de Lunar Eclipse, con módulos Python en la raíz. Copiar solo lo necesario y adaptar antes de ejecutar. No copiar `work/`, `out/`, el historial Git, fuentes de traducción de otro título ni sus respaldos.

| Ruta dentro del proyecto nuevo | Responsabilidad |
| --- | --- |
| `project_config.py` | Única identidad del juego, ejecutable, rutas y nombres de respaldos |
| `inventory.py` | Inventario original, clasificación y hashes |
| `fmsg_format.py`, `clean_translation.py` | Lectura, exportación y compilación de textos |
| `translations/`, `manual_translations.py` | Traducciones propias por archivo y contexto |
| `docs/glosario.md`, `docs/criterios-linguisticos.md` | Terminología y decisiones es-ES |
| `font_support.py` | Auditoría y ampliación de glifos |
| `layout_translation.py`, módulos de rótulos y estilo | Gráficos y literales visibles |
| `audit_graphics.py` | Comparaciones a partir del resultado recompilado |
| `build.py`, `manage_patch.py` | Construcción, paquete y gestión del parche de desarrollo |
| `installer/`, `installer_entry.py` | Instalador autónomo |
| `tests/` | Integridad de formatos y recuperación de instalación |
| `docs/estado.md`, `MODLOG.md` | Cobertura, incidencias, evidencias y siguiente paso |
| `work/`, `out/` | Originales locales, extracciones, QA y compilados; excluidos de Git |

Usar `FF_MOBW_GAME_DIR` para la ruta de instalación y `FF_MOBW_SOURCE_DIR` para la copia autenticada de desarrollo. Respaldo local de desarrollo propuesto: `work/originals/`, con `source_manifest.json`. Respaldo del instalador propuesto dentro del juego: `.fatal-frame-mobw-es-installer`. Registrar la ruta real de cada respaldo; no sobrescribir ni reutilizar carpetas de Lunar Eclipse.

Los contratos que siguen son propuestas para el proyecto futuro, no funciones que ya existan. Conservar las interfaces probadas de los formatos cuando no necesiten cambios:

- `inventory.scan(game_root: Path) -> dict`: produce el inventario versionado de rutas relativas, tamaño, SHA-256, familia y clasificación.
- `fmsg_format.load(path: Path) -> Fmsg` y `pack(original: Fmsg, new_strings: list[str] | tuple[str, ...]) -> bytes`: mismas interfaces que en Lunar Eclipse.
- `font_support.font_details(data: bytes) -> tuple`: conservar su estructura actual mientras la verificación confirme compatibilidad.
- `layout_translation.textures(raw: bytes) -> dict` y `decode(fmt, width, height, pixels)`: mismas interfaces actuales.
- `build.py`: un único punto de reconstrucción; descubre recursos mediante el inventario y las declaraciones de traducción, nunca mediante las listas de Lunar Eclipse.

## 6. Riesgos a cubrir en la revisión

| Condición | Comportamiento esperado | Fase que lo comprueba |
| --- | --- | --- |
| Instalación con un parche o mod previo | Detectar procedencia dudosa de fuentes y conservar el estado real al instalar | 1, 2 y 8 |
| FMSG vacío, huecos e identificadores | Conservar estructura y clasificar sin inflar cobertura | 1 y 3 |
| Texto inglés en KSLT, tutoriales o estados alternativos | Localizarlo o registrar una conservación justificada | 5 y 7 |
| Glifo presente en tabla pero invisible, o traducción recortada | Verificar en pantalla, con contexto y todos los estados relevantes | 4 y 7 |
| Instalación interrumpida o mod posterior al parche | Recuperar la operación y evitar sobrescribir cambios posteriores al restaurar | 8 y 9 |

## 7. Fases de ejecución y entregables

### Fase 1. Preparar el proyecto y autenticar la fuente

**Archivos:** `project_config.py`, `inventory.py`, `.gitignore`, `tests/test_inventory.py`, `docs/estado.md` y `MODLOG.md` del proyecto nuevo.

- [ ] Crear el proyecto independiente e identificar su raíz Git antes de copiar herramientas.
- [ ] Registrar versión del ejecutable, SHA-256, idiomas presentes y fecha del inventario. Usar la instalación local como referencia, sin inferir compatibilidad con otras versiones.
- [ ] Examinar el inglés para detectar un parche previo. Si hay recursos modificados, obtener originales verificables de una copia o respaldo del usuario; un hash recién calculado no acredita por sí solo su procedencia original.
- [ ] Implementar `inventory.scan` y crear `work/source_manifest.json` con rutas relativas, tamaños, hashes, familia, idioma y estado de cada recurso.
- [ ] Crear una copia de desarrollo autenticada para todos los recursos que se vayan incorporando; comprobar cada copia contra el manifiesto antes de usarla.
- [ ] Probar que el inventario clasifica el archivo de cero bytes y que una alteración posterior de una fuente se detecta antes de compilar.

**Salida verificable:** inventario de esta instalación, originales preservados y configuración que no apunta a Lunar Eclipse.

### Fase 2. Adaptar las herramientas y comprobar un cambio mínimo

**Archivos:** módulos de formatos, `clean_translation.py`, `font_support.py`, `layout_translation.py`, `tests/test_formats.py` y configuración.

- [ ] Adaptar imports, variables de entorno, fuente `Font_default.g1n`, rutas de KSLT y ejecutable. Eliminar las listas y cifras fijas de Lunar Eclipse.
- [ ] Antes de cambiar los lectores, añadir casos que comprueben reconstrucción FMSG exacta, rechazo de cabeceras corruptas y detección de fuentes cuyo hash haya cambiado. Conservar la prueba de cero bytes como exclusión explícita.
- [ ] Repetir lectura y reconstrucción exacta de todos los FMSG válidos con las herramientas ya separadas del proyecto anterior.
- [ ] Probar decodificación y recompresión de muestras RGBA y BC3. Comparar índices y tamaños; usar máscaras de bloques para evaluar qué bytes pueden cambiar.
- [ ] Preparar un borrador mínimo con una frase, una etiqueta gráfica y los caracteres españoles necesarios. Compilarlo en `work/` y probar primero el ciclo de respaldo/restauración en una instalación temporal.
- [ ] Verificar ese borrador dentro del juego, con el juego cerrado durante las escrituras, y guardar capturas de texto, etiqueta y glifos. Usar la guía de automatización de juegos durante esta fase futura.

**Salida verificable:** una prueba funcional pequeña que demuestra texto y gráficos es-ES antes de traducir todo el contenido.

### Fase 3. Exportar, clasificar y traducir los FMSG

**Archivos:** `clean_translation.py`, `manual_translations.py`, `translations/`, glosario y criterios lingüísticos; `tests/test_text_assets.py`.

- [ ] Exportar por ruta e índice el texto inglés exacto y su SHA-256; conservar huecos, códigos, contexto de archivo y duplicados.
- [ ] Clasificar cada entrada no vacía como traducible, identificador, nombre propio, control, número, idioma, crédito o conservación justificada. No contabilizar cadenas vacías como frases.
- [ ] Crear un glosario propio: nombres, lugares, conceptos, equipo, mecánicas y acciones. Usar «tú» y convenciones de España; no trasladar nombres de personajes o lugares de Lunar Eclipse.
- [ ] Traducir por grupos con contexto: interfaz y controles; tutoriales; historia y subtítulos; documentos y notas; objetos y fantasmas; extras y artbooks. Revisar concordancia, voz narrativa y terminología entre grupos.
- [ ] Conservar marcadores y variables según su función. La comparación de sus cantidades ayuda, pero revisar también su orden y significado cuando corresponda.
- [ ] Probar traducciones con variables, códigos de color, saltos y signos españoles; un cambio en el inglés debe invalidar su traducción vinculada hasta revisarla.
- [ ] Compilar y reabrir cada FMSG. Verificar mismos índices y cantidad de entradas, traducciones esperadas, códigos conservados y ausencia de cambios en entradas no declaradas.
- [ ] Generar informe de entradas traducidas, conservadas y pendientes, además de una lista revisable de inglés residual. Cada excepción debe tener motivo.

**Salida verificable:** traducciones propias desde el inglés y tablas recompiladas trazables, con cobertura basada en contenido real.

### Fase 4. Ampliar y comprobar la fuente

**Archivos:** `font_support.py`, `tests/test_font_assets.py`; atlas e informes bajo `work/`.

- [ ] Auditar todos los caracteres utilizados por los textos finales, incluidos mayúsculas acentuadas, diéresis, eñe y signos de apertura. Verificar también puntuación elegida para el proyecto.
- [ ] Reutilizar letras y diacríticos de la fuente original para componer lo que falte, comprobando las métricas de este juego. No copiar el archivo G1N modificado de Lunar Eclipse.
- [ ] Probar que los glifos originales permanecen intactos y que los añadidos disponen de mapa, métricas y bitmap válidos.
- [ ] Generar una lámina de glifos y ejemplos de frases; comprobar tamaño, acentos, posición vertical y espaciado.
- [ ] Verificar dentro del juego en subtítulos, documentos y menús que utilicen esta fuente; registrar dónde se usa otra fuente o texto gráfico.

**Salida verificable:** fuente ampliada a partir del original de Maiden of Black Water, legible en los contextos reales.

### Fase 5. Inventariar y traducir los gráficos y literales

**Archivos:** `layout_translation.py`, `external_labels.py`, `inline_labels.py`, `tutorial_labels.py`, módulos de estilo, `audit_graphics.py` y `tests/test_layout_assets.py`.

- [ ] Exportar láminas de contacto del conjunto inglés, KSLT externos, `common_texture` y `btn_texture`. Revisar visualmente todo el inventario; OCR puede ayudar, pero no cerrar la revisión por sí solo.
- [ ] Registrar por recurso y textura: nombre, formato, dimensiones, inglés visible, traducción, estados, regiones autorizadas, hash original y clasificación. Resolver alias o nombres repetidos sin perder entradas.
- [ ] Buscar otros recursos visibles con inglés fuera de esas carpetas, especialmente texturas de documentos, extras y posibles vídeos con texto incrustado. Registrar la ruta y tratamiento necesario de cualquier formato adicional; no declararlo cubierto con las pruebas KSCL/KSLT.
- [ ] Traducir menú principal, dificultad, opciones, pestañas, pausa, capítulos, resultados, equipo, Cámara Oscura, listas, mapas, modo foto, avisos y extras que realmente existan en esta edición.
- [ ] Para cada rótulo, cubrir estados normal, seleccionado, brillo y animación. Conservar retratos, separadores, iconos, teclas, candados y otros elementos fuera de la región de texto.
- [ ] Traducir las regiones inglesas dentro de capturas de tutorial: una imagen puede contener varios menús, indicaciones y estados.
- [ ] Medir estilo, color, opacidad, halo, alineación y espacio disponible. Reutilizar técnicas de Times New Roman, Arial o Segoe Print cuando encajen; documentar aproximaciones, sin distribuir las fuentes de Windows.
- [ ] Aplicar máscaras por región: bloques 4×4 en BC3 y píxeles en RGBA. Validar otros formatos antes de editarlos; no forzar un codificador incompatible.
- [ ] Inventariar literales visibles del layout con longitud fija. Exigir coincidencia de fuente y conservar longitud, capacidad y offsets; aplicar abreviaturas documentadas cuando sea necesario.
- [ ] Añadir pruebas que fallen ante cambios fuera de las regiones declaradas, desplazamiento de estructura o pérdida de una variante gráfica. Comprobar que un identificador interno parecido a una etiqueta no se modifica.
- [ ] Recompilar, reabrir y decodificar los recursos finales. Generar comparaciones original/castellano de cada textura modificada, incluidas las variantes.
- [ ] Revisar todas las comparaciones y registrar cada gráfico como traducido, conservado con motivo o pendiente. La aceptación exige cero pendientes traducibles.

**Salida verificable:** interfaz y demás inglés gráfico localizado, con inventario exhaustivo y evidencia de conservación del resto del recurso.

### Fase 6. Integrar una compilación reproducible

**Archivos:** `build.py`, `manage_patch.py`, `audit_graphics.py`, pruebas de paquete y documentación de reconstrucción.

- [ ] Encadenar autenticación de fuentes, exportación, compilación de textos, fuente, gráficos y literales, informes de cobertura, paquete, pruebas y auditoría visual.
- [ ] Hacer que todas las fases usen la misma fuente autenticada, también para gráficos cuando ya haya una traducción instalada.
- [ ] Crear un manifiesto por recurso modificado con ruta relativa, tamaño, SHA-256 original y SHA-256 final. Mantener aparte la clasificación de recursos conservados.
- [ ] Generar `out/fatal-frame-mobw-es-draft/` y `out/fatal-frame-mobw-es-latest.zip`, con checksum. Obtener las rutas desde el manifiesto propio, no desde la cifra 103 ni las migraciones históricas de Lunar Eclipse.
- [ ] Reabrir el ZIP y comprobar lista exacta de archivos, integridad y hashes. Rechazar recursos originales sin cambios o rutas fuera de la raíz prevista.
- [ ] Verificar dos reconstrucciones con mismos originales, herramientas y traducciones: los recursos deben coincidir en hash. Si se exige ZIP idéntico, fijar también sus metadatos de fecha y orden.
- [ ] Comprobar que la compilación completa no altera la instalación y que termina con un informe explícito de pendientes y validaciones realizadas.

**Salida verificable:** paquete reconstruible que contiene exclusivamente los recursos modificados y auxiliares necesarios.

### Fase 7. Revisar en el juego y corregir

**Archivos:** `docs/qa-en-juego.md`, `docs/estado.md`, `MODLOG.md` y correcciones de traducción; capturas locales bajo `work/`.

- [ ] Crear una matriz de escenas y pantallas: arranque, todos los menús y estados, controles de teclado y mando, tutoriales, subtítulos, documentos, mapas, equipos, capítulos, finales y extras accesibles.
- [ ] Verificar texto completo, tamaño, saltos, glifos, legibilidad, sincronía de subtítulos y consistencia de terminología.
- [ ] Revisar todas las familias de gráficos modificadas dentro del juego. Buscar específicamente inglés residual de recursos externos y capturas de tutorial.
- [ ] Registrar incidencia, ubicación, evidencia, corrección y resultado de la repetición. No corregir directamente los compilados: cambiar las fuentes del proyecto y reconstruir.
- [ ] Realizar una partida completa y una revisión dirigida del contenido no cubierto por esa ruta. Identificar con precisión capítulos o extras todavía no verificados.
- [ ] Mantener el estado «borrador» o «prueba» mientras quede contenido sin verificar. Separar el porcentaje traducido del porcentaje revisado en el juego.

**Salida verificable:** registro de revisión con pruebas concretas y límites declarados; para una entrega completa, cero incidencias bloqueantes y cobertura de todo el alcance.

### Fase 8. Adaptar la instalación y la restauración

**Archivos:** `manage_patch.py`, `installer/core.py`, `installer/gui.py`, `installer_entry.py`, `tests/test_manage_patch.py` y `tests/test_installer.py`.

- [ ] Identificar `FATAL_FRAME_MOBW.exe`, carpeta elegida, recursos presentes y versión soportada. Bloquear escrituras con el juego abierto y rechazar carpetas de Lunar Eclipse.
- [ ] Mantener el modo estricto de desarrollo contra originales autenticados; definir por separado el instalador de distribución que sustituye los recursos incluidos y respalda sus bytes previos, aunque contengan mods, siguiendo el comportamiento pedido para Lunar Eclipse.
- [ ] No exigir un paquete HD. Informar qué versión está soportada y qué recursos sustituye el paquete, sin prometer compatibilidad con versiones sin probar.
- [ ] Validar el payload antes de escribir. Guardar estado previo exacto en `.fatal-frame-mobw-es-installer` y mantenerlo al actualizar.
- [ ] Usar escrituras seguras, estados de operación y recuperación. Al restaurar, detectar recursos alterados después de instalar para no borrar un mod posterior sin una decisión explícita.
- [ ] Implementar selector de carpeta, Examinar, Comprobar, Instalar/actualizar y Restaurar copia; ejecutar operaciones de disco fuera del hilo gráfico y no iniciar el juego automáticamente.
- [ ] Probar en carpetas temporales: instalación, reinstalación, actualización propia, restauración exacta con mods previos, payload corrupto, fuente ausente, juego abierto e interrupciones durante respaldo, instalación y restauración.
- [ ] Probar que instalar en un destino ya traducido no convierte el borrador anterior en supuesto original; la actualización debe conservar el respaldo inicial del usuario.

**Salida verificable:** ciclo reversible con pruebas de fallos, independiente del respaldo de desarrollo y del juego anterior.

### Fase 9. Construir y verificar el instalador autónomo

**Archivos:** `installer/build_release.py`, `installer/verify_release.py`, dependencias fijadas y notas de terceros.

- [ ] Generar el EXE Windows x64 con Python/Tk embebidos y nombre propio `FATAL-FRAME-MOBW-ES-Setup.exe`. Crear icono y presentación adecuados a este título.
- [ ] Incluir solo payload validado, metadatos y avisos de dependencias. Preparar `SHA256SUMS.txt` y `THIRD_PARTY_NOTICES.txt` para la versión real de la entrega.
- [ ] Ejecutar el EXE compilado sobre una instalación temporal de recursos, sin depender de paquetes Python de desarrollo. Probar comprobar/instalar/comprobar/restaurar y comparar cada hash.
- [ ] Simular mods anteriores en textos y gráficos y verificar su restauración exacta. Adaptar el número de recursos del informe al manifiesto real.
- [ ] Revisar la interfaz gráfica, mensajes de error y rutas con espacios y caracteres españoles. Conservar el informe de validación local sin incluir copias de recursos en la descarga.

**Salida verificable:** EXE realmente probado, checksums y avisos de terceros, con un informe de su ciclo completo.

### Fase 10. Preparar documentación y distribución

**Archivos:** README, guía de instalación/restauración, compatibilidad, changelog, incidencias, créditos y material de presentación propios.

- [ ] Documentar requisitos, selección del inglés, versión probada, alcance, recursos modificados, respaldo y restauración, además de limitaciones reales.
- [ ] Separar fuentes privadas de desarrollo y repositorio de distribución, siguiendo la organización de Lunar Eclipse. Nombre propuesto para el segundo: `fatal-frame-mobw-es-release`; mantenerlo privado inicialmente si se crea.
- [ ] Crear banner y portada propios cuando corresponda. Conservar los créditos de herramientas y dependencias utilizadas sin atribuir autoría a traductores cuyos textos no se han usado.
- [ ] Preparar una versión de prueba si la revisión dentro del juego no está cerrada; usar números de cobertura obtenidos del informe real, nunca los de Lunar Eclipse.
- [ ] Revisar contenido de Git, EXE y ZIP para excluir originales, respaldos, extracciones completas y archivos ajenos a la entrega.
- [ ] Cuando el usuario pida distribuirlo, subir únicamente los artefactos verificados y documentar la versión exacta. No publicar como efecto secundario de compilar.

**Salida verificable:** entrega documentada y preparada para su distribución, con estado de revisión honesto.

## 8. Comandos previstos para el proyecto futuro

Estos comandos son el contrato de uso que deberá implementar el proyecto nuevo. **No existen todavía como flujo adaptado de Maiden of Black Water y no deben ejecutarse en el proyecto de Lunar Eclipse para este juego.**

```powershell
cd 'E:\Proyectos\fatal-frame-mobw-es'
$env:FF_MOBW_GAME_DIR = 'E:\Games\FATAL FRAME - PROJECT ZERO Maiden of Black Water'
$env:FF_MOBW_SOURCE_DIR = 'E:\Proyectos\fatal-frame-mobw-es\work\originals'
py -X utf8 build.py
py -X utf8 -m unittest discover -s tests -v
py -X utf8 audit_graphics.py
py -X utf8 -m installer.build_release
py -X utf8 -m installer.verify_release
```

Las pruebas requieren fuentes locales autenticadas para los casos de integración; los casos del instalador usan carpetas temporales. Registrar qué casos se ejecutan o se omiten. Para una entrega no basta con que solo pasen los casos independientes de los recursos reales.

`build.py` incluirá sus comprobaciones habituales; ejecutar pruebas por separado solo durante desarrollo, diagnóstico o validación específica de cambios. La instalación y restauración serán acciones separadas del proceso de compilación.

## 9. Seguimiento, aceptación y relevo

Al terminar cada fase, actualizar `docs/estado.md` y `MODLOG.md` con fuentes utilizadas, versión, resultados, incidencias y siguiente acción concreta. Guardar en Git código, traducciones y decisiones; dejar las extracciones e informes que contienen contenido original bajo `work/`.

Registrar por separado:

- Entradas traducibles, traducidas, conservadas y pendientes, con su clasificación.
- Recursos gráficos revisados, texturas traducibles, traducidas, conservadas y pendientes, incluidos estados y regiones.
- Cobertura de caracteres y verificaciones de fuente.
- Pantallas, escenas, capítulos y extras comprobados dentro del juego.
- Cantidad real de recursos empaquetados y resultado de instalación/restauración.

Criterios de aceptación final:

- [ ] Todo texto inglés traducible del alcance tiene traducción propia es-ES y revisión contextual.
- [ ] Todo gráfico con inglés ha sido localizado o conserva una excepción justificada compatible con el alcance.
- [ ] Fuente y códigos funcionan, sin texto recortado ni glifos ausentes en los contextos revisados.
- [ ] Los recursos se reabren correctamente y no cambian bytes fuera de los campos o regiones autorizados.
- [ ] Compilación reproducible, manifiestos y archivo comprimido verificados.
- [ ] Revisión dentro del juego completada, incluidas rutas y extras que una sola partida no cubre.
- [ ] Instalador compilado comprobado sobre instalaciones temporales y restauración exacta, incluidos mods previos.
- [ ] Documentación y versión describen el estado real; no se distribuyen originales o respaldos.

### Instrucción para retomar en otro chat

> Lleva a cabo el plan `E:\Proyectos\fatal-frame-mol-es\docs\superpowers\plans\2026-10-30-maiden-of-black-water-castellano.md` en un proyecto independiente propuesto en `E:\Proyectos\fatal-frame-mobw-es`. El juego está en `E:\Games\FATAL FRAME - PROJECT ZERO Maiden of Black Water`. Quiero una traducción propia del inglés al castellano de España, incluidos sus gráficos y extras, siguiendo las herramientas y el proceso de `E:\Proyectos\fatal-frame-mol-es`. Empieza verificando el estado actual y autenticando originales; después adapta y prueba texto, fuente y un rótulo antes de abordar toda la traducción. No utilices parches de traducción ajenos como base. Documenta cobertura, conserva la estética y comprueba los recursos recompilados, el juego y la restauración antes de darlo por terminado.

## 10. Referencias

Documentación local del proyecto de referencia:

- [README y proceso actual de Lunar Eclipse](../../../README.md).
- [Formatos gráficos, regiones y comprobaciones](../../graphics-pipeline.md).
- [Comportamiento del instalador y organización de distribución](../../release-design.md).
- [Herramientas y revisiones estudiadas](../../../tools/README.md).

Fuentes primarias ya consultadas durante el reconocimiento:

- [PJ5-FMSG-Extractor](https://github.com/lehieugch68/PJ5-FMSG-Extractor).
- [PJ5-KSCL-Unpacker](https://github.com/lehieugch68/PJ5-KSCL-Unpacker).
- [G1N-Font-Editor](https://github.com/lehieugch68/G1N-Font-Editor).
- [Confirmación del uso de las mismas herramientas en ambos juegos](https://steamcommunity.com/app/2130460/discussions/0/3790380616225025736/).

La compatibilidad detallada registrada en este documento procede de pruebas locales de lectura y reconstrucción sin modificaciones. Las fases de traducción, recompresión, prueba dentro del juego e instalación de Maiden of Black Water permanecen pendientes.
