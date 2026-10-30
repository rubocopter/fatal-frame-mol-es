"""Rebuild, verify and package the development draft; never install it."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import manage_patch as patch


ROOT = Path(__file__).resolve().parent


def run(*args, source):
    env = dict(os.environ, FF_MOL_GAME_DIR=str(source))
    subprocess.run([sys.executable, "-X", "utf8", *args], cwd=ROOT, env=env, check=True)


def archive():
    manifest = patch.validated_manifest(patch.DIST)
    target = ROOT / "out/fatal-frame-mol-es-latest.zip"
    helpers = ["manifest.json", "manage_patch.py", "external_labels.py", "tutorial_labels.py", "README.txt"]
    names = patch.PATHS + helpers
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for name in names:
            bundle.write(patch.DIST / name, name)
    with zipfile.ZipFile(target) as bundle:
        if bundle.testzip() is not None or set(bundle.namelist()) != set(names):
            raise ValueError("Archive content mismatch")
        for name, entry in manifest["files"].items():
            if hashlib.sha256(bundle.read(name)).hexdigest() != entry["patched_sha256"]:
                raise ValueError(f"Archive asset mismatch: {name}")
    checksum = patch.sha(target)
    target.with_suffix(".zip.sha256").write_text(checksum + "  " + target.name + "\n", encoding="utf-8")
    print(f"Verified ZIP: {len(names)} entries; SHA-256 {checksum}", flush=True)


def main():
    # A previous installation supplies authenticated originals. Without one,
    # the pristine game is the source. No file operation writes into the game.
    backup = patch.backup_manifest(patch.GAME)
    original = patch.GAME / patch.BACKUP_FOLDER if backup else patch.GAME
    for script, args in [
        ("clean_translation.py", ["export"]), ("manual_translations.py", []),
        ("clean_translation.py", ["build"]), ("font_support.py", []),
    ]:
        run(script, *args, source=original)
    run("layout_translation.py", source=patch.GAME)
    run("manage_patch.py", "package", "--game-root", str(original), source=patch.GAME)
    run("-m", "unittest", "discover", "-s", "tests", "-v", source=patch.GAME)
    run("audit_graphics.py", source=patch.GAME)
    archive()
    print("Build verified. Installation requires the separate, explicit upgrade command.")


if __name__ == "__main__":
    main()
