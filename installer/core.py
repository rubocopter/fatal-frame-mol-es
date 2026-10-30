"""Install the translated resources over the user's current files, with snapshots."""

import csv
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import uuid
import zipfile

BACKUP_FOLDER = ".fatal-frame-es-installer"


@dataclass(frozen=True)
class Inspection:
    kind: str
    message: str
    counts: dict


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            value.update(block)
    return value.hexdigest()


def _safe_name(name):
    path = PurePosixPath(name)
    if (path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name
            or str(path) != name or not name.startswith("binary/")
            or path.suffix not in (".fmsg", ".g1n", ".kscl", ".kslt")):
        raise ValueError("Ruta de recurso no válida.")
    return name


def read_payload(bundle):
    bundle = Path(bundle)
    data = json.loads((bundle/"payload.json").read_text(encoding="utf-8"))
    if data.get("schema") != 2 or data.get("mode") != "replace" or not data.get("files"):
        raise ValueError("El paquete de traducción no es válido.")
    archive = bundle/"resources.zip"
    if not archive.is_file() or sha(archive) != data.get("archive_sha256"):
        raise ValueError("El paquete está dañado. Descarga de nuevo el instalador.")
    for name, entry in data["files"].items():
        _safe_name(name)
        if (not re.fullmatch(r"[0-9a-f]{64}", entry.get("patched_sha256", ""))
                or not isinstance(entry.get("bytes"), int) or not 0 < entry["bytes"] < 2**30):
            raise ValueError("Metadatos del paquete no válidos.")
    with zipfile.ZipFile(archive) as source:
        if len(source.namelist()) != len(data["files"]) or set(source.namelist()) != set(data["files"]):
            raise ValueError("El contenido del paquete no coincide con el manifiesto.")
        for name, entry in data["files"].items():
            if source.getinfo(name).file_size != entry["bytes"]:
                raise ValueError("Tamaño de recurso no válido.")
    return data


def game_is_running():
    if os.name != "nt":
        return False
    result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq FATAL_FRAME_MOL.exe", "/FO", "CSV", "/NH"],
                            capture_output=True, text=True, check=True,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return any(row and row[0].lower() == "fatal_frame_mol.exe" for row in csv.reader(result.stdout.splitlines()))


def ensure_game_closed():
    if game_is_running():
        raise RuntimeError("Cierra el juego antes de instalar o restaurar la traducción.")


def _inside(game, path):
    if not path.resolve().is_relative_to(game):
        raise ValueError("Un recurso o respaldo apunta fuera de la carpeta del juego.")
    return path


def game_folder(game, names):
    game = Path(game).expanduser().resolve()
    if not (game/"FATAL_FRAME_MOL.exe").is_file():
        raise ValueError("Selecciona la carpeta que contiene FATAL_FRAME_MOL.exe.")
    _inside(game, game/BACKUP_FOLDER)
    missing = []
    for name in names:
        file = _inside(game, game/_safe_name(name))
        if not file.is_file():
            missing.append(name)
    if missing:
        raise ValueError("Faltan recursos del juego. Comprueba la carpeta elegida.\n"+"\n".join(missing[:4]))
    return game


def backup_manifest(game):
    game = Path(game).resolve()
    root = _inside(game, game/BACKUP_FOLDER)
    if not root.exists():
        return None
    marker = root/"state.json"
    if not marker.is_file():
        # Recover a crash between publishing the first complete snapshot and
        # publishing its active pointer. Ambiguous/unrecognized folders stop.
        candidates = list((root/"snapshots").glob("*/snapshot.json"))
        if not candidates and set(p.name for p in root.iterdir()) <= {"snapshots"}:
            return None
        if len(candidates) != 1:
            raise ValueError("Hay una carpeta de respaldo sin manifiesto. No se sobrescribirá.")
        state = json.loads(_inside(game, candidates[0]).read_text(encoding="utf-8"))
        state["status"] = "prepared"
    else:
        state = json.loads(marker.read_text(encoding="utf-8"))
    if state.get("schema") != 1 or not re.fullmatch(r"[0-9a-f]{32}", state.get("snapshot", "")):
        raise ValueError("El manifiesto del respaldo no es válido.")
    if not state.get("files") or state.get("status") not in ("prepared", "installed", "restoring", "restored"):
        raise ValueError("El estado de la copia de seguridad no es válido.")
    for name, entry in state["files"].items():
        original = _inside(game, root/"snapshots"/state["snapshot"]/"files"/_safe_name(name))
        if not original.is_file() or sha(original) != entry["before_sha256"]:
            raise ValueError(f"La copia de seguridad está dañada: {name}")
    return state


def _inspect(game, payload):
    state = backup_manifest(game)
    hashes = {name: sha(game/name) for name in payload["files"]}
    installed = sum(value == payload["files"][name]["patched_sha256"] for name, value in hashes.items())
    if state and state["status"] in ("prepared", "restoring"):
        return Inspection("recovery", "Operación interrumpida. Se recuperará la copia anterior antes de reintentar.", {"installed": installed})
    if state and state["status"] == "installed" and installed == len(hashes):
        return Inspection("installed", "La traducción ya está instalada y verificada.", {"installed": installed})
    if state and state["status"] != "restored":
        return Inspection("update", "Se puede reinstalar o actualizar. Se guardará una nueva copia del estado actual.", {"installed": installed})
    return Inspection("ready", "Juego localizado. Se sustituirán los recursos y se guardará una copia de los actuales.", {"installed": installed})


def inspect(game, bundle):
    payload = read_payload(bundle)
    return _inspect(game_folder(game, payload["files"]), payload)


def atomic_copy(source, target):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".es-install-", delete=False) as file:
            temporary = Path(file.name)
        shutil.copy2(source, temporary)
        os.replace(temporary, target)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def _write_state(game, state):
    marker = game/BACKUP_FOLDER/"state.json"
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=marker.parent,
                                     prefix=".state-", delete=False) as file:
        path = Path(file.name)
        json.dump(state, file, ensure_ascii=False, indent=2)
        file.write("\n")
    try:
        os.replace(path, marker)
    finally:
        path.unlink(missing_ok=True)


def _notify(callback, message, current, total):
    if callback:
        callback(message, current, total)


def _rollback(game, names, source, expected):
    errors = []
    for name in reversed(names):
        try:
            atomic_copy(source/name, game/name)
            if sha(game/name) != expected[name]:
                raise ValueError("La huella no coincide")
        except Exception as error:
            errors.append(f"{name}: {error}")
    if errors:
        raise RuntimeError("No se pudo recuperar el estado previo: "+"; ".join(errors))


def install(game, bundle, progress=None):
    ensure_game_closed()
    payload = read_payload(bundle)
    game = game_folder(game, payload["files"])
    prior = backup_manifest(game)
    if prior and prior["status"] in ("prepared", "restoring"):
        restore(game, bundle, progress)
        prior = backup_manifest(game)
    if _inspect(game, payload).kind == "installed":
        return "La traducción ya está instalada y verificada."
    files = payload["files"]
    total = len(files)*3
    with tempfile.TemporaryDirectory(prefix="ff-mol-es-prepare-") as folder:
        prepared = Path(folder)
        with zipfile.ZipFile(Path(bundle)/"resources.zip") as archive:
            for i, (name, entry) in enumerate(files.items(), 1):
                content = archive.read(name)
                if hashlib.sha256(content).hexdigest() != entry["patched_sha256"]:
                    raise ValueError(f"El recurso del paquete está dañado: {name}")
                target = prepared/name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
                _notify(progress, "Verificando los recursos de la traducción…", i, total)
        ensure_game_closed()
        identifier = uuid.uuid4().hex
        snapshot = game/BACKUP_FOLDER/"snapshots"/identifier
        state = {"schema": 1, "version": payload["version"], "snapshot": identifier,
                 "previous_snapshot": prior["snapshot"] if prior else None, "status": "prepared", "files": {}}
        # Stage outside the persistent backup folder, on the same volume.
        # Failed or interrupted copying cannot poison the active snapshot.
        with tempfile.TemporaryDirectory(prefix=".fatal-frame-es-backup-", dir=game) as temporary:
            staged_snapshot = Path(temporary)
            for i, (name, entry) in enumerate(files.items(), 1):
                source = game/name
                before = sha(source)
                target = staged_snapshot/"files"/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                if sha(target) != before or sha(source) != before:
                    raise ValueError(f"Un recurso ha cambiado al crear el respaldo: {name}")
                state["files"][name] = {"before_sha256": before, "patched_sha256": entry["patched_sha256"]}
                _notify(progress, "Guardando una copia de tus archivos actuales…", len(files)+i, total)
            (staged_snapshot/"snapshot.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            staged_snapshot.rename(snapshot)
        _write_state(game, state)
        attempted = []
        try:
            ensure_game_closed()
            for i, name in enumerate(files, 1):
                if sha(game/name) != state["files"][name]["before_sha256"]:
                    raise ValueError(f"El archivo ha cambiado antes de instalar: {name}")
                attempted.append(name)
                atomic_copy(prepared/name, game/name)
                if sha(game/name) != files[name]["patched_sha256"]:
                    raise ValueError(f"No se pudo verificar el recurso instalado: {name}")
                _notify(progress, "Instalando y verificando la traducción…", len(files)*2+i, total)
            state["status"] = "installed"
            _write_state(game, state)
        except Exception:
            _rollback(game, attempted, snapshot/"files", {n: e["before_sha256"] for n,e in state["files"].items()})
            if prior:
                _write_state(game, prior)
            else:
                state["status"] = "restored"
                _write_state(game, state)
            raise
    return "Traducción instalada y verificada. Se ha conservado una copia de tus archivos anteriores."


def restore(game, bundle, progress=None):
    ensure_game_closed()
    payload = read_payload(bundle)
    game = game_folder(game, payload["files"])
    state = backup_manifest(game)
    if not state:
        raise ValueError("No hay una copia anterior para restaurar.")
    if state["status"] == "restored":
        return "La copia anterior ya está restaurada."
    current = {}
    for name, entry in state["files"].items():
        current[name] = sha(game/name)
        if current[name] not in (entry["before_sha256"], entry["patched_sha256"]):
            raise ValueError("Hay recursos modificados después de instalar. Se conservan tus cambios; no se restaurará encima.")
    snapshot = game/BACKUP_FOLDER/"snapshots"/state["snapshot"]/"files"
    with tempfile.TemporaryDirectory(prefix="ff-mol-es-restore-") as folder:
        previous = Path(folder)
        for name in current:
            target = previous/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(game/name, target)
            if sha(target) != current[name]:
                raise ValueError("Un recurso ha cambiado durante la preparación.")
        ensure_game_closed()
        attempted = []
        prior_state = dict(state)
        state["status"] = "restoring"
        _write_state(game, state)
        try:
            for i, name in enumerate(current, 1):
                if sha(game/name) != current[name]:
                    raise ValueError("Un recurso ha cambiado antes de restaurar.")
                attempted.append(name)
                atomic_copy(snapshot/name, game/name)
                if sha(game/name) != state["files"][name]["before_sha256"]:
                    raise ValueError("No se pudo verificar el recurso restaurado.")
                _notify(progress, "Restaurando la copia anterior…", i, len(current))
            state["status"] = "restored"
            _write_state(game, state)
        except Exception:
            _rollback(game, attempted, previous, current)
            _write_state(game, prior_state)
            raise
    return "Copia anterior restaurada y verificada, incluidos los mods que había antes de instalar."
