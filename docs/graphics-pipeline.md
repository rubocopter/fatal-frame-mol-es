# Recursos gráficos y verificación

## Dos fuentes de texturas

Los KSCL (`LCSK`) contienen el layout y una tabla TLSK incrustada. Los KSLT (`TLSK4100`) externos utilizan esa misma tabla desde el offset cero. La versión inglesa tiene recursos externos bajo `binary/layout/en/ex_texture` que contienen las entradas completas del menú, las categorías de Opciones, las pestañas, los nombres de capítulo y otros rótulos. Traducir solamente la versión incrustada dejaba esos recursos ingleses sin modificar.

El lector de `layout_translation.py` admite ambas cabeceras y valida sus índices, tamaños y formatos RGBA/BC3. BC1 se decodifica para inspección de gráficos conservados, pero no se recompone. La auditoría de los KSLT ingleses cubrió 102 archivos y 592 texturas; se excluyen expresamente los gráficos del artbook. Los nombres propios, teclas estándar, logotipos, ilustraciones y símbolos se preservan.

## Tipografía y conservación

`external_style.py` mide el núcleo de las letras originales, su color, opacidad, alineación y color del halo. Utiliza serif normal o negrita según la familia, conserva los estados seleccionado/normal/animado y trata aparte los estados azules de foco. La fuente es una aproximación mediante fuentes de Windows, no una identificación exacta del tipo de letra comercial.

Las tarjetas de capítulo conservan el separador y el nombre del personaje; solo se sustituyen sus dos líneas de título. Los candados y botones mantienen los bloques ajenos a las leyendas. Las teclas conservan su marco, iluminación y símbolos; solo cambian las palabras del interior. Las pestañas de papel utilizan el grano de su parte sin imprimir.

`tutorial_labels.py` registra las regiones concretas de 21 capturas de tutorial, con el texto inglés visible, su traducción y sus coordenadas originales. Las 57 imágenes de tutorial fueron inspeccionadas. Se preservan escena, retratos, mapas, iconos, transparencia y los píxeles fuera de las regiones declaradas. Las 120 leyendas incluyen los menús mostrados dentro de capturas, acciones, instrucciones y guardado.

En BC3 se copian únicamente los bloques de 4×4 que cubren las regiones modificadas, evitando recomprimir el resto de la imagen. Para RGBA se conserva el resto de los píxeles. No se cambian las dimensiones, offsets ni longitudes de recursos.

`inline_labels.py` sustituye literales UTF-16 con prefijo de longitud dentro del layout. Verifica el original y conserva estrictamente la capacidad del campo con espacios de relleno. Usa abreviaturas cuando una palabra española completa no cabe, como «Ptos.», «AUTOG.» u «Obj.». No se traducen identificadores internos que solo coincidan con una palabra inglesa.

## Verificación y distribución

`build.py` reconstruye todo, valida las entradas y códigos FMSG, verifica la fuente, empaqueta, ejecuta las pruebas y genera las comparaciones a partir de las texturas recompresas. El ZIP se reabre y cada recurso se coteja con el manifiesto. No instala el resultado.

Las pruebas de integridad comparan la totalidad de los archivos con sus originales autenticados: solo se admiten cambios en las regiones de texto y literales declarados. Las pruebas de ciclo se ejecutan en instalaciones temporales e incluyen migración desde 45 recursos, restauración, recuperación ante fallos y bloqueo con el juego abierto. El instalador empaquetado se comprueba también sin acceso a paquetes Python de desarrollo.

El repositorio contiene código y fuentes de traducción. `work/`, `out/`, extracciones y originales están excluidos de Git. El repositorio público de release se preparará aparte cuando se decida distribuir una versión; esta limpieza no publica ni crea repositorios remotos.
