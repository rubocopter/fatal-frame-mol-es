# Ampliación del acabado aprobado — 29/10/2026

El usuario aprobó la muestra del menú principal y Opciones y autorizó extender
ese acabado. Se recompusieron los 118 rótulos localizados en los 28 KSCL.

`label_style.py` contiene tanto la receta aprobada como las variantes por
familia. `layout_translation.py` la aplica a los originales verificados y
`style_preview.py` reutiliza la receta para la muestra independiente.

- Times New Roman normal para los controles y estadísticas; negrita para
  títulos; cursiva para Nuevo, Completo, Película y Consumibles.
- Segoe Print para aproximar el texto manuscrito de Guardando.
- Núcleo de las letras separado del halo, con colores y opacidad derivados
  de los originales fuera de las ocho muestras aprobadas. Se mantienen las
  familias doradas, azules, verdes y rojas.
- Se respeta el anclaje izquierdo de las categorías y títulos y se conservan
  los centros de los controles. Los rótulos largos se ajustan horizontalmente;
  se revisaron las tildes, las descendentes y los márgenes disponibles.

Las tipografías son aproximaciones, no se ha identificado la fuente exacta
del juego. No se modifican los textos de historia, la fuente G1N ni los otros
gráficos que acompañan a los rótulos.

## Verificación realizada

Los 118 payloads seleccionados cambian frente al original. Todos los demás
rangos de bytes de los 28 KSCL permanecen idénticos, incluidos tamaños y
metadatos. Se volvieron a decodificar los resultados comprimidos y se
inspeccionaron los 118 pares en `work/kscl_review/comparison_es_01.png` a
`comparison_es_05.png`. Los ocho sprites de la muestra aprobada conservan
exactamente los mismos payloads de esa muestra. Comparativa resumida:
`work/kscl_review/acabado_extendido.png`.

Se superaron 15 pruebas en `test_manage_patch`, incluida una actualización
42→42 con textura modificada, conservación de todos los originales y
restauración. Se ejecutó `manage_patch.py upgrade` en el juego real: estado
`installed: 42` y respaldo original verificado. Se cotejaron los 42 archivos
instalados y los 42 originales por SHA-256. De los 358 archivos HD, 347 siguen
intactos en el juego y los once KSCL coincidentes se conservan exactamente en
el respaldo original. Informe local: `work/style_install_verification.json`.

**Falta comprobar el acabado dentro del juego**, en particular el espacio
real para rótulos largos y la combinación de los estados animados.

## Paquete y recuperación

Paquete local: `out/fatal-frame-mol-es-esES-2026-10-29-7331-42-assets-estilo.zip`.
Contiene 45 entradas (42 recursos, manifiesto, instalador y guía). Se
verificaron la integridad del ZIP y el hash de cada entrada tras comprimir.
SHA-256: `41e73bf4787a59df89cd589d8f58411f4984bda252970119e1ea70332185a86e`.

El paquete previo de 42 recursos y su manifiesto se conservan localmente en
`work/pre-style-2026-10-29/package`; el ZIP anterior también permanece en
`out`. Se puede volver a ese acabado usando `upgrade --patch-root` con esa
carpeta, con el juego cerrado. `restore` recupera los originales y las once
texturas HD respaldadas, siguiendo las instrucciones del README. No borrar
`.fatal-frame-es-originals`. Los binarios y las imágenes de revisión no se
suben al repositorio privado.
