"""Exercise real asset backups and recovery without touching the game install."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
import io
import shutil
import json
import unittest
from unittest.mock import patch

import manage_patch as mod


class PatchLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="mol-patch-test-")
        self.addCleanup(self.temp.cleanup)
        self.game = Path(self.temp.name) / "simulated_game"
        # Lifecycle writes target only this temporary simulated installation.
        running = patch.object(mod, "game_is_running", return_value=False)
        running.start()
        self.addCleanup(running.stop)
        self.folder = mod.DIST
        self.manifest = mod.validated_manifest(self.folder)
        for name in mod.PATHS:
            live = mod.GAME / mod.relative(name)
            expected = self.manifest["files"][name]["original_sha256"]
            if live.is_file() and mod.sha(live) == expected:
                source = live
            else:
                source = mod.GAME / mod.BACKUP_FOLDER / mod.relative(name)
                if not source.is_file() or mod.sha(source) != expected:
                    raise ValueError(f"No verified original game file for test: {name}")
            target = self.game / mod.relative(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def assert_original(self):
        self.assertEqual(set(mod.file_states(self.game, self.manifest).values()), {"original"})

    def test_refuses_install_while_game_running(self):
        with patch.object(mod, "game_is_running", return_value=True):
            with self.assertRaisesRegex(RuntimeError, "Close FATAL_FRAME_MOL"):
                mod.install(self.game, self.folder)
        self.assert_original()
        self.assertFalse((self.game / mod.BACKUP_FOLDER).exists())

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

    def older_patch(self, paths=None):
        older = Path(self.temp.name) / "older_patch"
        shutil.copytree(self.folder, older)
        # Exercise older manifests, including a new build of the same paths.
        paths = mod.LEGACY_PATHS if paths is None else paths
        old_manifest = mod.load_json(older / "manifest.json")
        for name in mod.PATHS:
            if name not in paths:
                (older / mod.relative(name)).unlink()
                del old_manifest["files"][name]
        item = mod.PATHS[0]
        asset = older / mod.relative(item)
        asset.write_bytes(asset.read_bytes() + b"previous draft")
        old_manifest["files"][item]["patched_sha256"] = mod.sha(asset)
        mod.write_json(older / "manifest.json", old_manifest)
        return older

    def test_upgrade_previous_draft_and_restore(self):
        previous = self.older_patch()
        mod.install(self.game, previous)
        prior = mod.backup_manifest(self.game)
        out = io.StringIO()
        with redirect_stdout(out):
            mod.check_status(self.game, self.folder)
        self.assertIn("previous draft: 1", out.getvalue())
        self.assertIn("Eligible for verified upgrade: yes", out.getvalue())
        mod.upgrade(self.game, self.folder)
        self.assertEqual(set(mod.file_states(self.game, self.manifest).values()), {"installed"})
        updated = mod.backup_manifest(self.game)
        self.assertEqual(updated["files"], self.manifest["files"])
        self.assertEqual(
            {p: old["original_sha256"] for p, old in prior["files"].items()},
            {p: updated["files"][p]["original_sha256"] for p in prior["files"]})
        self.assertEqual(len(updated["files"]), len(mod.PATHS))
        mod.restore(self.game, self.folder)
        self.assert_original()

    def test_upgrade_18_file_draft_and_restore(self):
        previous = self.older_patch(mod.PREVIOUS_18_PATHS)
        self.assertEqual(len(mod.validated_manifest(previous)["files"]), 18)
        mod.install(self.game, previous)
        original = mod.backup_manifest(self.game)
        mod.upgrade(self.game, self.folder)
        self.assertEqual(set(mod.file_states(self.game, self.manifest).values()), {"installed"})
        updated = mod.backup_manifest(self.game)
        self.assertEqual(len(updated["files"]), len(mod.PATHS))
        self.assertEqual(updated["files"], self.manifest["files"])
        for key, value in original["files"].items():
            self.assertEqual(value["original_sha256"], updated["files"][key]["original_sha256"])
        mod.restore(self.game, self.folder)
        self.assert_original()

    def test_upgrade_31_file_draft_and_restore(self):
        previous = self.older_patch(mod.PREVIOUS_31_PATHS)
        self.assertEqual(len(mod.validated_manifest(previous)["files"]), 31)
        mod.install(self.game, previous)
        original = mod.backup_manifest(self.game)
        mod.upgrade(self.game, self.folder)
        self.assertEqual(set(mod.file_states(self.game, self.manifest).values()), {"installed"})
        updated = mod.backup_manifest(self.game)
        self.assertEqual(len(updated["files"]), len(mod.PATHS))
        for key, value in original["files"].items():
            self.assertEqual(value["original_sha256"], updated["files"][key]["original_sha256"])
        mod.restore(self.game, self.folder)
        self.assert_original()

    def test_upgrade_42_file_draft_and_restore(self):
        previous = self.older_patch(mod.PREVIOUS_42_PATHS)
        self.assertEqual(len(mod.validated_manifest(previous)["files"]), 42)
        mod.install(self.game, previous)
        original = mod.backup_manifest(self.game)
        mod.upgrade(self.game, self.folder)
        self.assertEqual(set(mod.file_states(self.game, self.manifest).values()), {"installed"})
        updated = mod.backup_manifest(self.game)
        self.assertEqual(updated["files"], self.manifest["files"])
        for key, value in original["files"].items():
            self.assertEqual(value["original_sha256"], updated["files"][key]["original_sha256"])
        mod.restore(self.game, self.folder)
        self.assert_original()

    def test_upgrade_same_paths_with_changed_texture_and_restore(self):
        import layout_translation

        previous = self.older_patch(mod.PATHS)
        item = "binary/layout/en/title_layout_menu_parts.kscl"
        asset = previous / mod.relative(item)
        raw = bytearray(asset.read_bytes())
        index = layout_translation.textures(raw)
        start = index["fnt_menu_newgame_on"][3]
        raw[start + 12] ^= 16
        asset.write_bytes(raw)
        manifest = mod.load_json(previous / "manifest.json")
        manifest["files"][item]["patched_sha256"] = mod.sha(asset)
        mod.write_json(previous / "manifest.json", manifest)
        mod.install(self.game, previous)
        originals = {p: mod.sha(self.game / mod.BACKUP_FOLDER / mod.relative(p))
                     for p in mod.PATHS}
        mod.upgrade(self.game, self.folder)
        self.assertEqual(set(mod.file_states(self.game, self.manifest).values()), {"installed"})
        self.assertEqual(mod.backup_manifest(self.game)["files"], self.manifest["files"])
        self.assertEqual(originals, {p: mod.sha(self.game / mod.BACKUP_FOLDER / mod.relative(p))
                                     for p in mod.PATHS})
        mod.restore(self.game, self.folder)
        self.assert_original()

    def test_upgrade_45_file_draft_and_restore(self):
        previous = self.older_patch(mod.PREVIOUS_45_PATHS)
        self.assertEqual(len(mod.validated_manifest(previous)["files"]), 45)
        mod.install(self.game, previous)
        mod.upgrade(self.game, self.folder)
        self.assertEqual(set(mod.file_states(self.game, self.manifest).values()), {"installed"})
        self.assertEqual(mod.backup_manifest(self.game)["files"], self.manifest["files"])
        mod.restore(self.game, self.folder)
        self.assert_original()

    def test_rejects_incomplete_manifest(self):
        incomplete = Path(self.temp.name) / "incomplete"
        shutil.copytree(self.folder, incomplete)
        manifest = mod.load_json(incomplete / "manifest.json")
        key = mod.PATHS[-1]
        del manifest["files"][key]
        mod.write_json(incomplete / "manifest.json", manifest)
        with self.assertRaisesRegex(ValueError, "Unsupported or incomplete patch manifest"):
            mod.validated_manifest(incomplete)

    def test_upgrade_rejects_foreign_modification(self):
        previous = self.older_patch()
        mod.install(self.game, previous)
        item = mod.PATHS[1]
        target = self.game / mod.relative(item)
        target.write_bytes(target.read_bytes() + b"external mod")
        with self.assertRaisesRegex(ValueError, "unexpected game files"):
            mod.upgrade(self.game, self.folder)
        self.assertEqual(mod.backup_manifest(self.game)["files"],
                         mod.validated_manifest(previous)["files"])
        self.assertFalse((self.game / mod.BACKUP_FOLDER /
                          mod.relative(mod.PATHS[-1])).exists())

    def test_upgrade_failure_after_new_assets_rolls_back(self):
        previous = self.older_patch()
        mod.install(self.game, previous)
        before = {p: mod.sha(self.game / mod.relative(p)) for p in mod.PATHS}
        actual = mod.atomic_copy
        calls = 0

        def fail_after_new_assets(src, dest):
            nonlocal calls
            calls += 1
            if calls == 11:
                raise OSError("interrupted after KSCL backups")
            return actual(src, dest)

        with patch.object(mod, "atomic_copy", side_effect=fail_after_new_assets):
            with self.assertRaisesRegex(OSError, "interrupted after KSCL backups"):
                mod.upgrade(self.game, self.folder)
        self.assertEqual(before, {p: mod.sha(self.game / mod.relative(p)) for p in mod.PATHS})
        self.assertEqual(set(mod.backup_manifest(self.game)["files"]), set(mod.LEGACY_PATHS))
        for name in set(mod.PATHS) - set(mod.LEGACY_PATHS):
            self.assertFalse((self.game / mod.BACKUP_FOLDER / mod.relative(name)).exists())

    def test_upgrade_write_failure_rolls_back(self):
        previous = self.older_patch()
        mod.install(self.game, previous)
        before = {p: mod.sha(self.game / mod.relative(p)) for p in mod.PATHS}
        actual = mod.atomic_copy
        calls = 0

        def broken_copy(src, dest):
            nonlocal calls
            calls += 1
            if calls == 4:
                raise OSError("upgrade interrupted")
            return actual(src, dest)

        with patch.object(mod, "atomic_copy", side_effect=broken_copy):
            with self.assertRaisesRegex(OSError, "upgrade interrupted"):
                mod.upgrade(self.game, self.folder)
        self.assertEqual(before, {p: mod.sha(self.game / mod.relative(p)) for p in mod.PATHS})
        self.assertEqual(mod.backup_manifest(self.game)["files"],
                         mod.validated_manifest(previous)["files"])

    def test_export_refuses_patched_game_as_english_source(self):
        import clean_translation

        previous = self.older_patch()
        mod.install(self.game, previous)
        with (patch.object(clean_translation, "GAME", self.game),
              patch.object(clean_translation, "SOURCE", self.game / "binary/text/USen")):
            with self.assertRaisesRegex(ValueError, "Original English FMSG required"):
                list(clean_translation.source_files())

    def test_layout_rebuild_uses_original_backup_after_upgrade(self):
        import layout_translation

        previous = self.older_patch()
        mod.install(self.game, previous)
        mod.upgrade(self.game, self.folder)
        scratch = Path(self.temp.name) / "layout_build"
        output = scratch / "work/layout_es/binary/layout/en"
        with (patch.object(layout_translation, "ROOT", scratch),
              patch.object(layout_translation, "OUTPUT", output)):
            layout_translation.build(self.game)
        for name in (*mod.KSCL_FILES, *mod.KSLT_FILES):
            rel = Path("binary/layout/en") / name
            self.assertEqual(mod.sha(output / name), mod.sha(self.folder / rel))


if __name__ == "__main__":
    unittest.main()
