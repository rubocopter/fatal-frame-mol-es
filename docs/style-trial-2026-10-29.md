# Prueba de acabado de los rótulos — 29/10/2026

Muestra visual solicitada antes de extender el acabado al resto de la interfaz.
Se usa Times New Roman normal para los controles y negrita para el título de
Opciones, con espaciado ajustado. Es una aproximación: no se ha identificado
la tipografía original. El halo dorado de selección se dibuja por separado
del núcleo claro de las letras; el estado normal mantiene la sombra oscura.

La prueba incluye ocho sprites en cuatro KSCL: aviso inicial y su efecto,
Nueva partida en sus tres estados, Ajustes generales en dos estados y el
título Opciones. Se conserva la altura de las mayúsculas en Nueva partida,
permitiendo que la p descienda por debajo de la línea base.

Ejecutar desde `E:\Proyectos\fatal-frame-mol-es`:

```powershell
py -X utf8 style_preview.py
```

Resultados locales en `work/style_trial/`: `muestra.png` (comparación breve),
`comparacion.png` (todos los estados), `verification.json` y cuatro recursos
KSCL bajo `binary/layout/en`. Los generados quedan excluidos de Git.

El script exige originales respaldados y archivos instalados con SHA-256
coincidentes con el manifiesto. Los KSCL de muestra parten del parche actual,
modifican solo los ocho payloads seleccionados, conservan tamaño y metadatos,
y se vuelven a leer tras la recompresión DXT5 para elaborar las comparativas.
Se verificaron esas condiciones y se inspeccionaron las dos comparativas.

**La muestra no se ha instalado ni probado dentro del juego.** La instalación
de 42 recursos sigue intacta. Falta valorar el acabado con el usuario y después
comprobar su encaje en las pantallas y animaciones reales antes de extenderlo.
