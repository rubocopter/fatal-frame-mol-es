"""Build the self-contained replacement installer from the verified draft."""

import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tkinter
import zipfile

from PIL import Image, ImageDraw
import manage_patch as patch

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
PAYLOAD = ROOT/"work/installer_payload"
OUTPUT = ROOT/"out/release"/f"v{VERSION}"


def notices():
    sections = ["FATAL FRAME / PROJECT ZERO — Traducción al castellano\n"
                "Dependencias del instalador. Sus licencias se conservan a continuación.\n"
                "Los recursos modificados del juego conservan los derechos de sus titulares.\n"]
    for name in ("pyinstaller", "altgraph", "packaging", "pyinstaller-hooks-contrib"):
        distribution = metadata.distribution(name)
        sections.append(f"\n{'='*70}\n{name} {distribution.version}\n")
        found = False
        for entry in distribution.files or []:
            if any(part.lower().startswith(("license", "copying")) for part in entry.parts):
                path = Path(distribution.locate_file(entry))
                if path.is_file():
                    sections.append(path.read_text(encoding="utf-8", errors="replace"))
                    found = True
        if not found:
            sections.append(distribution.metadata.get("License", "License metadata not supplied"))
    for path in [Path(sys.base_prefix)/"LICENSE.txt"]:
        if not path.is_file():
            raise FileNotFoundError(f"License notice missing: {path}")
        sections.append(f"\n{'='*70}\n{path.name} — {path.parent.name}\n"+path.read_text(encoding="utf-8", errors="replace"))
    # Python 3.14's Tcl/Tk 9 stores its library and notices in zipfs archives.
    for library in ("tcl", "tk"):
        archives = list((Path(sys.base_prefix)/"tcl").glob(f"lib{library}*.zip"))
        if len(archives) != 1:
            raise ValueError(f"Cannot identify bundled {library} library")
        with zipfile.ZipFile(archives[0]) as bundle:
            license_text = bundle.read(f"{library}_library/license.terms").decode("utf-8")
        sections.append(f"\n{'='*70}\n{archives[0].name}\n"+license_text)
    return "\n\n".join(sections)+"\n"


def prepare():
    manifest = patch.validated_manifest(patch.DIST)
    PAYLOAD.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    files = {}
    with zipfile.ZipFile(PAYLOAD/"resources.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in patch.PATHS:
            entry = manifest["files"][name]
            if entry["original_sha256"] == entry["patched_sha256"]:
                raise ValueError(f"An unmodified original would be distributed: {name}")
            archive.write(patch.DIST/name, name)
            files[name] = {"bytes": entry["bytes"], "patched_sha256": entry["patched_sha256"]}
    data = {"schema": 2, "mode": "replace", "version": VERSION,
            "archive_sha256": patch.sha(PAYLOAD/"resources.zip"), "files": files}
    (PAYLOAD/"payload.json").write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
    notice = notices()
    (PAYLOAD/"THIRD_PARTY_NOTICES.txt").write_text(notice, encoding="utf-8")
    (OUTPUT/"THIRD_PARTY_NOTICES.txt").write_text(notice, encoding="utf-8")
    icon = Image.new("RGBA", (256,256), (17,25,31,255))
    draw = ImageDraw.Draw(icon)
    draw.ellipse((32,30,224,222),fill=(196,180,136))
    draw.ellipse((83,6,252,185),fill=(17,25,31))
    icon.save(PAYLOAD/"luna.ico", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
    from installer.core import read_payload
    read_payload(PAYLOAD)
    print(f"Replacement payload verified: {len(files)} modified resources.", flush=True)


def main():
    prepare()
    scratch = ROOT/"work/installer_build"
    scratch.mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
                    "--name", "FATAL-FRAME-MOL-ES-Setup", "--paths", str(ROOT),
                    "--distpath", str(OUTPUT), "--workpath", str(scratch/"work"), "--specpath", str(scratch),
                    "--icon", str(PAYLOAD/"luna.ico"), "--add-data", str(PAYLOAD)+os.pathsep+"payload",
                    str(ROOT/"installer_entry.py")], cwd=ROOT, check=True)
    names = ["FATAL-FRAME-MOL-ES-Setup.exe", "THIRD_PARTY_NOTICES.txt"]
    lines = [patch.sha(OUTPUT/name)+"  "+name for name in names]
    (OUTPUT/"SHA256SUMS.txt").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"Installer built: {OUTPUT}")


if __name__ == "__main__":
    main()
