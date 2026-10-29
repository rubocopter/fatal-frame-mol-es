"""Exercise real asset backups and recovery without touching the game install."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest
from unittest.mock import patch

import manage_patch as mod


class PatchLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="mol-patch-test-")
        self.addCleanup(self.temp.cleanup)
        self.game = Path(self.temp.name) / "simulated_game"
        self.folder = mod.DIST
        self.manifest = mod.validated_manifest(self.folder)
        live_states = mod.file_states(mod.GAME, self.manifest)
        if set(live_states.values()) == {"original"}:
            originals = mod.GAME
        elif set(live_states.values()) <= {"original", "installed"}:
            # The user may be playing with the patch installed; test against
            # their verified original backup, never against the live patch.
            saved = mod.backup_manifest(mod.GAME)
            if saved is None or saved["files"] != self.manifest["files"]:
                raise ValueError("No verified original game files for tests")
            originals = mod.GAME / mod.BACKUP_FOLDER
        else:
            raise ValueError(f"Unexpected live game file state: {live_states}")
        for name in mod.PATHS:
            source = originals / mod.relative(name)
            target = self.game / mod.relative(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def assert_original(self):
        self.assertEqual(set(mod.file_states(self.game, self.manifest).values()), {"original"})

    def test_install_restore_reinstall(self):
        mod.install(self.game, self.folder)
        states = mod.file_states(self.game, self.manifest)
        self.assertTrue(set(states.values()) <= {"installed", "original"})
        self.assertIn("installed", states.values())
        self.assertIsNotNone(mod.backup_manifest(self.game))
        mod.restore(self.game, self.folder)
        self.assert_original()
        mod.install(self.game, self.folder)
        mod.restore(self.game, self.folder)
        self.assert_original()

    def test_refuses_different_game_version(self):
        target = self.game / mod.relative(mod.PATHS[0])
        target.write_bytes(target.read_bytes() + b"mismatch")
        with self.assertRaisesRegex(ValueError, "unmodified originals"):
            mod.install(self.game, self.folder)
        self.assertFalse((self.game / mod.BACKUP_FOLDER).exists())

    def test_rejects_corrupt_patch_before_backup(self):
        damaged = Path(self.temp.name) / "damaged_patch"
        shutil.copytree(self.folder, damaged)
        asset = damaged / mod.relative(mod.PATHS[0])
        asset.write_bytes(asset.read_bytes() + b"tampered")
        with self.assertRaisesRegex(ValueError, "missing or corrupt"):
            mod.install(self.game, damaged)
        self.assert_original()
        self.assertFalse((self.game / mod.BACKUP_FOLDER).exists())

    def test_failure_mid_install_rolls_back(self):
        actual = mod.atomic_copy
        calls = 0

        def broken_copy(src, dest):
            nonlocal calls
            calls += 1
            if calls == 4:
                raise OSError("simulated disk error")
            return actual(src, dest)

        with patch.object(mod, "atomic_copy", side_effect=broken_copy):
            with self.assertRaisesRegex(OSError, "simulated disk error"):
                mod.install(self.game, self.folder)
        self.assert_original()
        self.assertIsNotNone(mod.backup_manifest(self.game))

    def test_restore_refuses_unknown_asset(self):
        mod.install(self.game, self.folder)
        target = self.game / mod.relative(mod.PATHS[0])
        target.write_bytes(target.read_bytes() + b"changed by user")
        with self.assertRaisesRegex(ValueError, "unexpected game files"):
            mod.restore(self.game, self.folder)


if __name__ == "__main__":
    unittest.main()
