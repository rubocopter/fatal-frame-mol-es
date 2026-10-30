# Ampliación de interfaz, 30/10/2026

La preparación se realizó en el proyecto mientras el usuario jugaba. Posteriormente confirmó que había cerrado el juego y autorizó instalar el resultado. Se aplicó la actualización 42→45 con el instalador y se comprobaron las 45 huellas instaladas y sus 45 originales respaldados: coinciden con el manifiesto SHA-256. La verificación visual jugando sigue pendiente.

## Traducciones añadidas

| Recurso | Gráficos | Traducción |
| --- | --- | --- |
| `option_menu.kscl` | `photograph_OFF/ON`, `search_OFF/ON` | Modo foto, Modo búsqueda |
| `photo_layout.kscl` | `icon_lock` | Bloquear |
| `pocketbook_layout_list_parts.kscl` | `fusen_left/right` | NUEVO |
| `system_layout.kscl` | `HOLD_OFF/ON`, seis botones `*_hold_*` | MANT. (mantener pulsado) |

Son 15 gráficos nuevos: el inventario pasa de 118 a 133 y de 28 a 31 KSCL. El paquete pasa de 42 a 45 recursos. Artbook y sus contenidos quedan fuera de esta ampliación por petición expresa.

## Conservación y comprobaciones

`mixed_labels.py` recompone las leyendas incluidas en iconos. En BC3 se sustituyen únicamente los bloques de 4×4 correspondientes a la zona de texto del candado y de los botones. El resto del icono permanece idéntico en el archivo. Las etiquetas de papel reutilizan el grano de su mitad sin texto. La tipografía mantiene el método del proyecto y sus estados de iluminación; «MANT.» usa negrita de palo seco como la indicación original.

`test_layout_assets` compara todos los KSCL generados con los originales verificados: tamaños, índices, regiones modificadas, rótulos modificados y conservación de los demás bytes. La prueba de ciclo de parche comprueba instalación, restauración, recuperación ante errores y migración 42→45 en directorios temporales. Incluye el bloqueo al detectar el juego abierto. La simulación utiliza su propio detector de proceso simulado y nunca escribe en la instalación real.

Comparación visual: `work/kscl_review/additions_es.png`. Paquete: `out/fatal-frame-mol-es-draft/`. El ZIP de 45 recursos y su SHA-256 se generan bajo `out/` y quedan excluidos de Git.

Verificación final: 18 pruebas correctas en 42,705 segundos. ZIP comprobado con 48 entradas (45 recursos, manifiesto, instalador y guía); SHA-256 `58a115e4551c0e6f24144accf0a055a2c420fa52d01cef12628dad7b7f6f81db`. Estado final del instalador: `installed: 45`, `Verified original backup: yes`.

## Pendiente de comprobar jugando

Los KSCL instalados de Nueva partida, Pausa y Ajustes generales coinciden con las compilaciones traducidas anteriores, aunque el usuario informa de rótulos ingleses. No se ha determinado todavía qué ruta o selección de recursos los dibuja en esa sesión. Tampoco se da por resuelta la aparición de Inglés, los nombres de capítulos, Score o Key Items solo por existir sus traducciones FMSG. El diagnóstico visual se deja para cuando se pueda probar el juego sin interrumpir al usuario.
