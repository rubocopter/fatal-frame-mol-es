import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from installer import core


def digest(data):
    return hashlib.sha256(data).hexdigest()


class ReplacementInstaller(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mol-installer-test-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.game = root / "Juego con espacios"
        self.bundle = root / "payload"
        self.game.mkdir()
        self.bundle.mkdir()
        (self.game / "FATAL_FRAME_MOL.exe").write_bytes(b"test marker")
        self.paths = ["binary/text/USen/system.fmsg", "binary/font/JP/default.g1n",
                      "binary/layout/en/title_layout.kscl"]
        self.before = {}
        self.after = {}
        files = {}
        for i, name in enumerate(self.paths):
            source = b"source data " * (i+10)
            target = b"Spanish text " + source + b" translated"
            entry = self.game / name
            entry.parent.mkdir(parents=True, exist_ok=True)
            entry.write_bytes(source)
            self.before[name] = source
            self.after[name] = target
            files[name] = {"patched_sha256": digest(target), "bytes": len(target)}
        with zipfile.ZipFile(self.bundle / "resources.zip", "w", zipfile.ZIP_DEFLATED) as archive:
            for name, data in self.after.items():
                archive.writestr(name, data)
        (self.bundle / "payload.json").write_text(json.dumps(
            {"schema": 2, "mode": "replace", "version": "0.1.0", "files": files,
             "archive_sha256": digest((self.bundle / "resources.zip").read_bytes())}), encoding="utf-8")
        running = patch.object(core, "game_is_running", return_value=False)
        running.start()
        self.addCleanup(running.stop)

    def assert_files(self, expected):
        for name, value in expected.items():
            self.assertEqual((self.game / name).read_bytes(), value)

    def test_install_recheck_restore(self):
        self.assertEqual(core.inspect(self.game, self.bundle).kind, "ready")
        core.install(self.game, self.bundle)
        self.assert_files(self.after)
        self.assertEqual(core.inspect(self.game, self.bundle).kind, "installed")
        core.restore(self.game, self.bundle)
        self.assert_files(self.before)
        self.assertEqual(core.inspect(self.game, self.bundle).kind, "ready")
        self.assertIsNotNone(core.backup_manifest(self.game))

    def test_wrong_folder_does_not_write(self):
        (self.game / "FATAL_FRAME_MOL.exe").unlink()
        with self.assertRaisesRegex(ValueError, "FATAL_FRAME_MOL.exe"):
            core.install(self.game, self.bundle)
        self.assert_files(self.before)
        self.assertFalse((self.game / core.BACKUP_FOLDER).exists())

    def test_modified_base_is_installed_and_restored(self):
        modified = dict(self.before)
        modified[self.paths[0]] = b"another texture mod"
        (self.game / self.paths[0]).write_bytes(modified[self.paths[0]])
        core.install(self.game, self.bundle)
        self.assert_files(self.after)
        core.restore(self.game, self.bundle)
        self.assert_files(modified)

    def test_corrupt_payload_does_not_write(self):
        (self.bundle / "resources.zip").write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "paquete"):
            core.install(self.game, self.bundle)
        self.assert_files(self.before)
        self.assertFalse((self.game / core.BACKUP_FOLDER).exists())

    def test_bad_resource_hash_does_not_write(self):
        meta = self.bundle / "payload.json"
        data = json.loads(meta.read_text())
        data["files"][self.paths[1]]["patched_sha256"] = "0" * 64
        meta.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "recurso"):
            core.install(self.game, self.bundle)
        self.assert_files(self.before)
        self.assertFalse((self.game / core.BACKUP_FOLDER).exists())

    def test_running_game_does_not_write(self):
        with patch.object(core, "game_is_running", return_value=True):
            with self.assertRaises(RuntimeError):
                core.install(self.game, self.bundle)
        self.assert_files(self.before)

    def test_previous_build_upgrade_preserves_originals(self):
        core.install(self.game, self.bundle)
        item = self.paths[0]
        older = b"previous Spanish draft"
        (self.game / item).write_bytes(older)
        self.assertEqual(core.inspect(self.game, self.bundle).kind, "update")
        core.install(self.game, self.bundle)
        self.assert_files(self.after)
        core.restore(self.game, self.bundle)
        self.assert_files({**self.after, item: older})

    def test_restore_write_failure_rolls_back(self):
        core.install(self.game, self.bundle)
        actual = core.atomic_copy
        calls = 0
        def faulty(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated disk failure")
            return actual(src, dst)
        with patch.object(core, "atomic_copy", side_effect=faulty):
            with self.assertRaisesRegex(OSError, "disk failure"):
                core.restore(self.game, self.bundle)
        self.assert_files(self.after)

    def test_install_write_failure_rolls_back(self):
        actual = core.atomic_copy
        calls = 0
        def faulty(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated install failure")
            return actual(src, dst)
        with patch.object(core, "atomic_copy", side_effect=faulty):
            with self.assertRaisesRegex(OSError, "install failure"):
                core.install(self.game, self.bundle)
        self.assert_files(self.before)

    def test_restore_does_not_overwrite_a_later_mod(self):
        core.install(self.game, self.bundle)
        changed = self.game / self.paths[0]
        changed.write_bytes(b"a mod installed afterwards")
        with self.assertRaisesRegex(ValueError, "modificados"):
            core.restore(self.game, self.bundle)
        self.assertEqual(changed.read_bytes(), b"a mod installed afterwards")
        self.assertEqual((self.game/self.paths[1]).read_bytes(), self.after[self.paths[1]])

    def test_zip_path_traversal_rejected(self):
        metadata = self.bundle / "payload.json"
        data = json.loads(metadata.read_text())
        data["files"]["binary/../../outside.fmsg"] = next(iter(data["files"].values()))
        metadata.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Ruta"):
            core.install(self.game, self.bundle)
        self.assert_files(self.before)

    def test_retry_after_interruption_preserves_prior_mods(self):
        modified = dict(self.before)
        modified[self.paths[0]] = b"existing mod before interruption"
        (self.game/self.paths[0]).write_bytes(modified[self.paths[0]])
        actual = core.atomic_copy
        calls = 0
        def interrupted(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise KeyboardInterrupt()
            return actual(src, dst)
        with patch.object(core, "atomic_copy", side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt):
                core.install(self.game, self.bundle)
        self.assertEqual(core.backup_manifest(self.game)["status"], "prepared")
        core.install(self.game, self.bundle)
        core.restore(self.game, self.bundle)
        self.assert_files(modified)

    def test_failed_first_backup_can_be_retried(self):
        actual = core.shutil.copy2
        calls = 0
        def faulty(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("backup copy failed")
            return actual(src, dst)
        with patch.object(core.shutil, "copy2", side_effect=faulty):
            with self.assertRaisesRegex(OSError, "backup copy failed"):
                core.install(self.game, self.bundle)
        self.assert_files(self.before)
        self.assertEqual(core.inspect(self.game, self.bundle).kind, "ready")
        core.install(self.game, self.bundle)
        core.restore(self.game, self.bundle)
        self.assert_files(self.before)

    def test_reinstall_after_interrupted_restore_keeps_the_original_backup(self):
        core.install(self.game, self.bundle)
        actual = core.atomic_copy
        calls = 0
        def interrupted(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise KeyboardInterrupt()
            return actual(src, dst)
        with patch.object(core, "atomic_copy", side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt):
                core.restore(self.game, self.bundle)
        self.assertEqual(core.backup_manifest(self.game)["status"], "restoring")
        core.install(self.game, self.bundle)
        core.restore(self.game, self.bundle)
        self.assert_files(self.before)


if __name__ == "__main__":
    unittest.main()
