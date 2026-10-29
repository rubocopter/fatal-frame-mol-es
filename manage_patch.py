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
LAYOUT = PROJECT / "work" / "layout_es" / "binary" / "layout" / "en"
BACKUP_FOLDER = ".fatal-frame-es-originals"
TEXT_FILES = (
    "system.fmsg", "system2.fmsg", "text1.fmsg", "text2.fmsg",
    "text3.fmsg", "text4.fmsg", "text5.fmsg", "text6.fmsg",
    "text7.fmsg", "text8.fmsg", "text9.fmsg", "textnew_01.fmsg",
    "textnew_02.fmsg",
)
LEGACY_PATHS = [f"binary/text/USen/{name}" for name in TEXT_FILES]
LEGACY_PATHS.append("binary/font/JP/default.g1n")
KSCL_FILES = (
    "title_layout.kscl", "title_layout_menu_parts.kscl",
    "title_layout_difficulty_parts.kscl", "cmn_title_mission.kscl",
)
PATHS = LEGACY_PATHS + [f"binary/layout/en/{name}" for name in KSCL_FILES]


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


def managed_paths(manifest: dict) -> list[str]:
    files = manifest.get("files", {})
    if set(files) == set(PATHS):
        return PATHS
    if set(files) == set(LEGACY_PATHS):
        return LEGACY_PATHS
    raise ValueError("Unsupported or incomplete patch manifest")


def built_file(path: str) -> Path:
    if path.endswith(".fmsg"):
        return FMSG / Path(path).name
    if path.endswith(".g1n"):
        return FONT
    return LAYOUT / Path(path).name


def original_file(game: Path, path: str) -> Path:
    """Use a verified legacy backup for FMSG/G1N and live original KSCL.

    Before the first layout upgrade, a 14-file legacy backup cannot contain
    the newly managed layout assets. Only allow this known local game layout.
    """
    original = game / relative(path)
    if original.is_file():
        return original
    if (game.name == BACKUP_FOLDER and game.parent.resolve() == GAME.resolve()
            and path.startswith("binary/layout/en/")):
        return GAME / relative(path)
    raise FileNotFoundError(f"Original game asset not found: {original}")


def validated_manifest(folder: Path) -> dict:
    manifest = load_json(folder / "manifest.json")
    files = manifest.get("files", {})
    if manifest.get("schema") != 1:
        raise ValueError("Unsupported or incomplete patch manifest")
    paths = managed_paths(manifest)
    for entry in files.values():
        for key in ("original_sha256", "patched_sha256"):
            value = entry.get(key, "")
            if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError(f"Bad manifest hash: {key}")
    for item in paths:
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
    if sha(game / relative(LEGACY_PATHS[-1])) != font_qa["base_font_sha256"]:
        raise ValueError("The game's original font has changed")

    from layout_translation import LABELS
    if set(LABELS) != set(KSCL_FILES):
        raise ValueError("Incomplete translated KSCL inventory")
    if load_json(PROJECT / "work" / "layout_es_qa.json") != {
            filename: list(labels) for filename, labels in LABELS.items()}:
        raise ValueError("Layout translation QA is missing or outdated")

    files = {}
    for item in PATHS:
        original = original_file(game, item)
        built = built_file(item)
        if not original.is_file() or not built.is_file():
            raise FileNotFoundError(f"Missing original or draft asset: {item}")
        files[item] = {
            "original_sha256": sha(original),
            "patched_sha256": sha(built),
            "bytes": built.stat().st_size,
        }

    DIST.mkdir(parents=True, exist_ok=True)
    for item in PATHS:
        built = built_file(item)
        dest = DIST / relative(item)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built, dest)
    write_json(DIST / "manifest.json", {
        "schema": 1,
        "language": "es-ES",
        "source": "Original game's English (USen) files; third-party fan translations were not used",
        "status": "DRAFT: in-game full story and layout validation still pending",
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
        "  python manage_patch.py upgrade  (si ya hay un borrador instalado)\n"
        "  python manage_patch.py restore\n\n"
        "Incluye 13 FMSG, fuente G1N y 4 KSCL de títulos y menús.\n"
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
    if data.get("schema") != 1:
        raise ValueError("Invalid backup manifest")
    for item in managed_paths(data):
        entry = data["files"][item]
        stored = folder / relative(item)
        if not stored.is_file() or sha(stored) != entry["original_sha256"]:
            raise ValueError(f"Missing or corrupt original backup: {item}")
    return data


def file_states(game: Path, manifest: dict) -> dict[str, str]:
    states = {}
    for item in managed_paths(manifest):
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
    if backup:
        for item in managed_paths(backup):
            if (item in states and states[item] == "unexpected"
                    and backup["files"][item]["original_sha256"] == manifest["files"][item]["original_sha256"]
                    and sha(game / relative(item)) == backup["files"][item]["patched_sha256"]):
                states[item] = "previous draft"
    for state in ("original", "installed", "previous draft", "unexpected", "missing"):
        entries = [p for p, s in states.items() if s == state]
        if entries:
            print(f"{state}: {len(entries)}" + (f" ({', '.join(entries)})" if state in ("unexpected", "missing") else ""))
    print(f"Verified original backup: {'yes' if backup else 'no'}")
    if backup:
        previous = managed_paths(backup)
        eligible = (set(previous) <= set(managed_paths(manifest))
                    and all(backup["files"][p]["original_sha256"] == manifest["files"][p]["original_sha256"]
                            for p in previous)
                    and all(s in ("original", "installed", "previous draft") for s in states.values()))
        print(f"Eligible for verified upgrade: {'yes' if eligible else 'no'}")


def ensure_original_backup(game: Path, manifest: dict) -> dict:
    existing = backup_manifest(game)
    if existing is not None:
        if existing["files"] != manifest["files"]:
            raise ValueError("Existing backup belongs to another patch build")
        return existing
    folder = game / BACKUP_FOLDER
    temp = Path(tempfile.mkdtemp(prefix=".es-originals-staging-", dir=game))
    try:
        for item in managed_paths(manifest):
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
        for item in managed_paths(manifest):
            atomic_copy(folder / relative(item), game / relative(item))
            if sha(game / relative(item)) != manifest["files"][item]["patched_sha256"]:
                raise ValueError(f"Post-install verification failed: {item}")
            completed.append(item)
    except Exception:
        failures = []
        for item in reversed(completed + [p for p in managed_paths(manifest) if p not in completed]):
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
    print(f"Installed {len(managed_paths(manifest))} assets; originals backed up at {game / BACKUP_FOLDER}")


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
    for item in managed_paths(manifest):
        if states[item] == "original":
            continue
        atomic_copy(game / BACKUP_FOLDER / relative(item), game / relative(item))
        if sha(game / relative(item)) != manifest["files"][item]["original_sha256"]:
            raise ValueError(f"Restore verification failed for: {item}")
    print(f"Restored all {len(managed_paths(manifest))} original game assets; verified backup retained")


def upgrade(game: Path, folder: Path) -> None:
    """Upgrade a previously installed draft while retaining verified originals.

    Accept only assets matching the original or the exact installed draft
    recorded in the backup manifest. Stage the entire previous live state and
    roll back both assets and manifest if any write fails.
    """
    ensure_game_closed()
    manifest = validated_manifest(folder)
    backup = backup_manifest(game)
    if backup is None:
        raise ValueError("No verified prior patch backup; use install for original game assets")
    prior_paths = managed_paths(backup)
    new_paths = managed_paths(manifest)
    if not set(prior_paths) <= set(new_paths):
        raise ValueError("Cannot remove managed files when upgrading")
    if any(backup["files"][item]["original_sha256"] != manifest["files"][item]["original_sha256"]
           for item in prior_paths):
        raise ValueError("Prior backup originals do not match this game build")
    added = [item for item in new_paths if item not in prior_paths]
    states = file_states(game, backup)
    bad = {p: state for p, state in states.items() if state not in ("original", "installed")}
    for item in added:
        source = game / relative(item)
        if not source.is_file() or sha(source) != manifest["files"][item]["original_sha256"]:
            bad[item] = "unexpected" if source.exists() else "missing"
    if bad:
        raise ValueError(f"Refusing to overwrite unexpected game files: {bad}")

    marker = game / BACKUP_FOLDER / "backup_manifest.json"
    with tempfile.TemporaryDirectory(prefix=".es-upgrade-staging-", dir=game) as temp_name:
        staging = Path(temp_name)
        for item in new_paths:
            dest = staging / relative(item)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(game / relative(item), dest)
            if sha(dest) != sha(game / relative(item)):
                raise ValueError(f"Cannot stage current asset: {item}")
        old_marker = staging / "backup_manifest.json"
        shutil.copy2(marker, old_marker)
        try:
            for item in added:
                new_backup = game / BACKUP_FOLDER / relative(item)
                if new_backup.exists():
                    raise ValueError(f"Untracked backup asset exists: {item}")
                atomic_copy(staging / relative(item), new_backup)
                if sha(new_backup) != manifest["files"][item]["original_sha256"]:
                    raise ValueError(f"New original backup failed verification: {item}")
            for item in new_paths:
                atomic_copy(folder / relative(item), game / relative(item))
                if sha(game / relative(item)) != manifest["files"][item]["patched_sha256"]:
                    raise ValueError(f"Upgrade verification failed: {item}")
            new_marker = staging / "new_backup_manifest.json"
            write_json(new_marker, {"schema": 1, "files": manifest["files"]})
            atomic_copy(new_marker, marker)
            backup_manifest(game)
        except Exception:
            failures = []
            for item in new_paths:
                try:
                    atomic_copy(staging / relative(item), game / relative(item))
                    if sha(game / relative(item)) != sha(staging / relative(item)):
                        raise ValueError("Checksum mismatch")
                except Exception as exc:
                    failures.append(f"{item}: {exc}")
            try:
                atomic_copy(old_marker, marker)
                for item in added:
                    (game / BACKUP_FOLDER / relative(item)).unlink(missing_ok=True)
                backup_manifest(game)
            except Exception as exc:
                failures.append(f"backup manifest: {exc}")
            if failures:
                raise RuntimeError("Upgrade rollback failed for: " + "; ".join(failures))
            raise
    print(f"Upgraded {len(new_paths)} assets; original backup preserved at {game / BACKUP_FOLDER}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("package", "status", "install", "upgrade", "restore"))
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
    elif args.action == "upgrade":
        upgrade(game, folder)
    else:
        restore(game, folder)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
