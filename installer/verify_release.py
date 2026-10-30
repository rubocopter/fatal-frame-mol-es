"""Exercise the actual frozen EXE against all resources in a temporary fake game."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import manage_patch as patch


def main():
    output = patch.PROJECT/"out/release/v0.1.0"
    executable = output/"FATAL-FRAME-MOL-ES-Setup.exe"
    manifest = patch.validated_manifest(patch.DIST)
    with tempfile.TemporaryDirectory(prefix="mol-frozen-installer-") as folder:
        root = Path(folder)
        game = root/"Juego temporal con espacios"
        game.mkdir()
        (game/"FATAL_FRAME_MOL.exe").write_bytes(b"Non-executable test marker")
        before = {}
        for index, (name, entry) in enumerate(manifest["files"].items()):
            source = patch.GAME/patch.BACKUP_FOLDER/name
            if patch.sha(source) != entry["original_sha256"]:
                raise ValueError(f"Source backup mismatch: {name}")
            data = bytearray(source.read_bytes())
            # Simulate another texture mod on two independently versioned resources.
            if index in (15, 60):
                data[-1] ^= 32
            target = game/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            before[name] = hashlib.sha256(data).hexdigest()
        outcomes = {}
        for action in ("check", "install", "check", "restore"):
            report = root/f"{len(outcomes)}-{action}.json"
            result = subprocess.run([str(executable), "--action", action, "--game-dir", str(game), "--report", str(report)],
                                    capture_output=True, text=True, timeout=120)
            if not report.is_file():
                raise RuntimeError(f"Frozen installer did not report {action}: {result.returncode}")
            data = json.loads(report.read_text(encoding="utf-8"))
            if result.returncode or not data["ok"]:
                raise RuntimeError(f"Frozen installer failed: {action}: {data}")
            outcomes[f"{len(outcomes)}-{action}"] = data
            if action == "install":
                for name, entry in manifest["files"].items():
                    if patch.sha(game/name) != entry["patched_sha256"]:
                        raise ValueError(f"Installed hash mismatch: {name}")
            if action == "restore":
                for name, expected in before.items():
                    if patch.sha(game/name) != expected:
                        raise ValueError(f"Restored modded file mismatch: {name}")
        outcomes["verified_assets"] = len(before)
        outcomes["modded_base_files"] = 2
        outcomes["installer_sha256"] = patch.sha(executable)
        (output/"validation.json").write_text(json.dumps(outcomes, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Frozen EXE verified: check/install/check/restore, 103 assets, two prior texture mods restored exactly.")


if __name__ == "__main__":
    main()
