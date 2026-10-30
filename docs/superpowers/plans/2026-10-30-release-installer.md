# Distribución privada e instalador Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Crear un repositorio privado de presentación y una release descargable con instalador gráfico funcional.

**Architecture:** Fuentes y pruebas del instalador en el repositorio de desarrollo; portada, banner, captura real, Ko-fi de onitaku y documentación en un checkout separado. El ejecutable empaqueta los 103 recursos modificados y guarda una copia del estado real anterior de cada instalación.

**Tech Stack:** Python 3.14, Tkinter/ttk, PyInstaller, GitHub CLI.

**Spec:** `docs/release-design.md`.

## Global Constraints

- Repositorio de release privado, sin cambiar la visibilidad del de desarrollo.
- No modificar la instalación real durante pruebas.
- No distribuir ejecutables del juego, originales sin modificar, partidas ni respaldos.
- Selector de ruta, comprobación, instalación/actualización y restauración.
- Sustituir recursos aunque contengan otros mods. No exigir una base HD ni hashes originales para instalar.

## Review Focus

- Ruta equivocada o juego abierto: se rechaza antes de escribir.
- Contenido corrupto: se rechaza antes de escribir recursos en el juego.
- Actualización: se guarda el estado previo exacto, incluidos los mods; se recuperan operaciones interrumpidas.
- Ejecutable empaquetado: funciona sin Python instalado.
- Documentación y descarga: enlaces a versión real y compatibilidad explícita.

## Trabajo

- [x] Preparar portada, Ko-fi y documentación en checkout de distribución independiente.
- [x] Añadir pruebas del servicio de sustitución, copia, restauración e interrupciones e implementar.
- [x] Implementar GUI y compilación del ejecutable con avisos de dependencias.
- [x] Probar el EXE real en carpeta temporal: 103 recursos y dos mods restaurados exactamente; revisar visualmente la GUI y guardar su captura.
- [x] Verificar contenido del artefacto y crear repositorio privado y prerelease.
- [x] Comprobar privacidad, descarga, huellas y árbol final del repositorio remoto.

## Resultado verificado

- Repositorio privado: https://github.com/rubocopter/fatal-frame-mol-es-release
- Prerelease publicada: https://github.com/rubocopter/fatal-frame-mol-es-release/releases/tag/v0.1.0
- `main` y etiqueta apuntan a `8278a031b1c9dcf116f97f242f31c603a7b9f063`; checkout de distribución limpio.
- Árbol remoto: 11 archivos de documentación y presentación; no contiene ejecutables ni recursos del juego.
- Tres adjuntos publicados y descargados de nuevo; sus SHA-256 coinciden con los archivos compilados.
- SHA-256 del EXE: `bcff4b18d75c72a632782dd67ff93d66b35d2d7aabd7f50a6f29edc8a7b5abf6`.
- 33 pruebas superadas. EXE real comprobado sobre 103 recursos temporales, con restauración exacta de dos mods previos.
- Revisión independiente del servicio: sin bloqueos pendientes. Pruebas e interfaz no han instalado nada sobre el juego real.
