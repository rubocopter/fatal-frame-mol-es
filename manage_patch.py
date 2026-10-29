"""Package, verify and safely install/restore the English-based Spanish draft.

The installed game's files are modified only by the explicit `install` and
`restore` subcommands. The archive contains a byte-for-byte backup of the
original assets and is retained after a successful restore.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


PROJECT = Path(__file__).resolve().parent
GAME = Path(r"E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse")
DIST = PROJECT / "out" / "fatal-frame-mol-es-draft"
FONT = PROJECT / "work" / "font_original_extended.g1n"
FMSG = PROJECT / "out" / "clean_es_draft" / "binary" / "text" / "USen"
BACKUP_FOLDER = ".fatal-frame-es-originals"
TEXT_FILES = (
    "system.fmsg", "system2.fmsg", "text1.fmsg", "text2.fmsg",
    "text3.fmsg", "text4.fmsg", "text5.fmsg", "text6.fmsg",
    "text7.fmsg", "text8.fmsg", "text9.fmsg", "textnew_01.fmsg",
    "textnew_02.fmsg",
)
PATHS = [f"binary/text/USen/{name}" for name in TEXT_FILES]
PATHS.append("binary/font/JP/default.g1n")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fd:
        for block in iter(lambda: fd.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path: str) -> Path:
    if path not in PATHS:
        raise ValueError(f"Unexpected managed path: {path}")
    return Path(*path.split("/"))


def validated_manifest(folder: Path) -> dict:
    manifest = load_json(folder / "manifest.json")
    files = manifest.get("files", {})
    if manifest.get("schema") != 1 or set(files) != set(PATHS):
        raise ValueError("Unsupported or incomplete patch manifest")
    for entry in files.values():
        for key in ("original_sha256", "patched_sha256"):
            value = entry.get(key, "")
            if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError(f"Bad manifest hash: {key}")
    for item in PATHS:
        destination = folder / relative(item)
        if not destination.is_file() or sha(destination) != files[item]["patched_sha256"]:
            raise ValueError(f"Patch file missing or corrupt: {destination}")
    return manifest


def package(game: Path) -> None:
    qa = load_json(PROJECT / "work" / "clean_es_qa.json")
    font_qa = load_json(PROJECT / "work" / "font_qa.json")
    if qa["warnings"] or not font_qa["extended_font"]["covered"]:
        raise ValueError("Translation or font QA reports warnings")
    if len(TEXT_FILES) != len(list(FMSG.glob("*.fmsg"))):
        raise ValueError("Unexpected text file count in the build")
    if sha(FONT) != font_qa["output_font_sha256"]:
        raise ValueError("Extended font does not match font QA")
    if sha(game / relative(PATHS[-1])) != font_qa["base_font_sha256"]:
        raise ValueError("The game's original font has changed")

    files = {}
    for item in PATHS:
        original = game / relative(item)
        built = FONT if item == PATHS[-1] else FMSG / Path(item).name
        if not original.is_file() or not built.is_file():
            raise FileNotFoundError(f"Missing original or draft asset: {item}")
        files[item] = {
            "original_sha256": sha(original),
            "patched_sha256": sha(built),
            "bytes": built.stat().st_size,
        }

    DIST.mkdir(parents=True, exist_ok=True)
    for item in PATHS:
        built = FONT if item == PATHS[-1] else FMSG / Path(item).name
        dest = DIST / relative(item)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built, dest)
    write_json(DIST / "manifest.json", {
        "schema": 1,
        "language": "es-ES",
        "source": "Original game's English (USen) files; third-party fan translations were not used",
        "status": "DRAFT: in-game font and layout validation still pending",
        "translation_qa": {
            "total_entries": qa["total_entries"],
            "translated_entries": qa["translated_entries"],
            "untranslated_or_unreviewed_entries": qa["untranslated_or_unreviewed_entries"],
        },
        "files": files,
    })
    shutil.copy2(Path(__file__), DIST / "manage_patch.py")
    (DIST / "README.txt").write_text(
        "Traducción es-ES de FATAL FRAME / PROJECT ZERO: Mask of the Lunar Eclipse\n"
        "BORRADOR: aún sin verificación visual completa dentro del juego.\n\n"
        "Se basa exclusivamente en los textos ingleses originales.\n"
        "No incluye textos del parche ajeno usado para localizar archivos.\n\n"
        "Ejecutar en Windows, con el juego cerrado:\n"
        "  python manage_patch.py status\n"
        "  python manage_patch.py install\n"
        "  python manage_patch.py restore\n\n"
        "El instalador verifica los archivos del juego mediante SHA-256 y crea\n"
        "una copia de seguridad en .fatal-frame-es-originals. No la borres.\n"
        "La instalación queda bloqueada si el juego no coincide con la versión\n"
        "original de este equipo o si los archivos del parche están dañados.\n"
        "Puedes indicar otra ruta con --game-root <ruta>.\n",
        encoding="utf-8",
    )
    validated_manifest(DIST)
    print(f"Draft package with {len(PATHS)} verified assets: {DIST}")


def game_is_running() -> bool:
    if os.name != "nt":
        return False
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq FATAL_FRAME_MOL.exe", "/FO", "CSV", "/NH"],
        capture_output=True, text=True, check=True,
    )
    return any(row and row[0].lower() == "fatal_frame_mol.exe"
               for row in csv.reader(result.stdout.splitlines()))


def ensure_game_closed() -> None:
    if game_is_running():
        raise RuntimeError("Close FATAL_FRAME_MOL.exe before installing or restoring files")


def atomic_copy(src: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".es-patch-", dir=destination.parent,
                                         delete=False) as fd:
            temporary = Path(fd.name)
        shutil.copy2(src, temporary)
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def backup_manifest(game: Path) -> dict | None:
    folder = game / BACKUP_FOLDER
    marker = folder / "backup_manifest.json"
    if not folder.exists():
        return None
    if not marker.is_file():
        raise ValueError(f"An unrecognized or incomplete backup exists: {folder}")
    data = load_json(marker)
    if data.get("schema") != 1 or set(data.get("files", {})) != set(PATHS):
        raise ValueError("Invalid backup manifest")
    for item in PATHS:
        entry = data["files"][item]
        stored = folder / relative(item)
        if not stored.is_file() or sha(stored) != entry["original_sha256"]:
            raise ValueError(f"Missing or corrupt original backup: {item}")
    return data


def file_states(game: Path, manifest: dict) -> dict[str, str]:
    states = {}
    for item in PATHS:
        target = game / relative(item)
        if not target.is_file():
            states[item] = "missing"
            continue
        current = sha(target)
        entry = manifest["files"][item]
        states[item] = ("original" if current == entry["original_sha256"]
                        else "installed" if current == entry["patched_sha256"]
                        else "unexpected")
    return states


def check_status(game: Path, folder: Path) -> None:
    manifest = validated_manifest(folder)
    states = file_states(game, manifest)
    backup = backup_manifest(game)
    for state in ("original", "installed", "unexpected", "missing"):
        entries = [p for p, s in states.items() if s == state]
        if entries:
            print(f"{state}: {len(entries)}" + (f" ({', '.join(entries)})" if state in ("unexpected", "missing") else ""))
    print(f"Verified original backup: {'yes' if backup else 'no'}")


def ensure_original_backup(game: Path, manifest: dict) -> dict:
    existing = backup_manifest(game)
    if existing is not None:
        if existing["files"] != manifest["files"]:
            raise ValueError("Existing backup belongs to another patch build")
        return existing
    folder = game / BACKUP_FOLDER
    temp = Path(tempfile.mkdtemp(prefix=".es-originals-staging-", dir=game))
    try:
        for item in PATHS:
            dest = temp / relative(item)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(game / relative(item), dest)
            if sha(dest) != manifest["files"][item]["original_sha256"]:
                raise ValueError(f"Backup verification failed: {item}")
        backup = {"schema": 1, "files": manifest["files"]}
        write_json(temp / "backup_manifest.json", backup)
        temp.rename(folder)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    backup_manifest(game)
    return backup


def install(game: Path, folder: Path) -> None:
    ensure_game_closed()
    manifest = validated_manifest(folder)
    states = file_states(game, manifest)
    if any(state != "original" for state in states.values()):
        raise ValueError(f"Installation requires unmodified originals; found: {states}")
    ensure_original_backup(game, manifest)
    completed = []
    try:
        for item in PATHS:
            atomic_copy(folder / relative(item), game / relative(item))
            if sha(game / relative(item)) != manifest["files"][item]["patched_sha256"]:
                raise ValueError(f"Post-install verification failed: {item}")
            completed.append(item)
    except Exception:
        failures = []
        for item in reversed(completed + [p for p in PATHS if p not in completed]):
            target = game / relative(item)
            expected = manifest["files"][item]["original_sha256"]
            if target.exists() and sha(target) == expected:
                continue
            try:
                atomic_copy(game / BACKUP_FOLDER / relative(item), target)
                if sha(target) != expected:
                    raise ValueError("Checksum still mismatches")
            except Exception as exc:
                failures.append(f"{item}: {exc}")
        if failures:
            raise RuntimeError("Automatic rollback failed for: " + "; ".join(failures))
        raise
    print(f"Installed {len(PATHS)} assets; originals backed up at {game / BACKUP_FOLDER}")


def restore(game: Path, folder: Path) -> None:
    ensure_game_closed()
    manifest = validated_manifest(folder)
    backup = backup_manifest(game)
    if backup is None or backup["files"] != manifest["files"]:
        raise ValueError("No matching verified original backup exists")
    states = file_states(game, manifest)
    bad = {path: state for path, state in states.items() if state not in ("original", "installed")}
    if bad:
        raise ValueError(f"Refusing to overwrite unexpected game files: {bad}")
    for item in PATHS:
        if states[item] == "original":
            continue
        atomic_copy(game / BACKUP_FOLDER / relative(item), game / relative(item))
        if sha(game / relative(item)) != manifest["files"][item]["original_sha256"]:
            raise ValueError(f"Restore verification failed for: {item}")
    print(f"Restored all {len(PATHS)} original game assets; verified backup retained")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("package", "status", "install", "restore"))
    parser.add_argument("--game-root", type=Path, default=GAME)
    parser.add_argument("--patch-root", type=Path, default=None)
    args = parser.parse_args()
    game = args.game_root.resolve()
    folder = args.patch_root or (PROJECT if (PROJECT / "manifest.json").is_file() else DIST)
    if args.action == "package":
        package(game)
    elif args.action == "status":
        check_status(game, folder)
    elif args.action == "install":
        install(game, folder)
    else:
        restore(game, folder)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
