# Distribución privada e instalador

El usuario ha validado los gráficos y pide un repositorio privado separado, con portada y Releases al estilo de `rubocopter/chaos-head-noah-es`, además de un instalador gráfico que permita elegir la carpeta del juego.

Se seguirá el patrón existente: README de presentación, banner propio, instrucciones, compatibilidad, changelog y formularios de incidencias. Repositorio propuesto: `rubocopter/fatal-frame-mol-es-release`, privado. Primera descarga: `v0.1.0`, marcada como versión de prueba; no se anuncia revisión completa de una partida.

El instalador es un ejecutable Windows x64 con Python/Tk embebido. Controles: carpeta, Examinar, Comprobar, Instalar / actualizar y Restaurar copia. Las operaciones de disco se ejecutan fuera del hilo de interfaz. No abre el juego al terminar.

Por indicación posterior del usuario, el instalador sustituye los 103 recursos por las versiones traducidas, aunque haya texturas modificadas previamente. El payload contiene únicamente los recursos modificados de la traducción y sus metadatos. No contiene ejecutables del juego, partidas ni respaldos originales. Se verifica cada archivo distribuido antes de escribir.

No se exige un pack HD. Se comprueba la carpeta, la presencia de los recursos y que el juego esté cerrado. Antes de sustituir se guarda el estado real del usuario, incluidos mods, en `.fatal-frame-es-installer`, separado del respaldo de desarrollo. La restauración verifica que los archivos actuales siguen siendo los instalados antes de recuperar el estado anterior. Instalación y restauración tienen recuperación ante fallos. No se modifican partidas ni se prueba sobre la instalación real. El repositorio queda privado y sin Pages público.
