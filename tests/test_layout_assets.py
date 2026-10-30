"""Validate built assets against verified originals, with read-only game access."""

import unittest

import layout_translation as layout
import manage_patch as patch
from mixed_labels import region


class LayoutIntegrity(unittest.TestCase):
    def test_only_declared_texture_regions_change(self):
        manifest = patch.validated_manifest(patch.DIST)
        for filename, labels in layout.LABELS.items():
            with self.subTest(asset=filename):
                key = "binary/layout/en/" + filename
                expected = manifest["files"][key]["original_sha256"]
                source = patch.GAME / patch.BACKUP_FOLDER / key
                if not source.is_file():
                    source = patch.GAME / key
                self.assertEqual(patch.sha(source), expected)
                original = source.read_bytes()
                built = (layout.OUTPUT / filename).read_bytes()
                self.assertEqual(len(original), len(built))
                index = layout.textures(original)
                self.assertEqual(index, layout.textures(built))
                allowed = bytearray(len(original))
                from inline_labels import replacements as inline_replacements
                if filename in layout.INLINE_LABELS:
                    for start, end, text in inline_replacements(original, filename):
                        self.assertEqual(built[start:end], text)
                        allowed[start:end] = b'\1' * (end-start)
                for name in labels:
                    fmt, width, height, start, length = index[name]
                    if isinstance(labels[name], dict):
                        boxes = [r["box"] for r in labels[name]["regions"] if r["source"] != r["text"]]
                    elif filename.endswith(".kslt") and isinstance(labels[name], list):
                        boxes = [(0, 0, 780, 152)]
                    elif name.startswith("btn_PCKey_"):
                        from external_style import keycap_region
                        boxes = [keycap_region(name, labels[name])]
                    else:
                        boxes = [region(name, (width, height))]
                    for x0, y0, x1, y1 in boxes:
                        if fmt == 3:
                            for row in range(y0//4, (y1+3)//4):
                                a = start + (row*(width//4) + x0//4)*16
                                b = start + (row*(width//4) + (x1+3)//4)*16
                                allowed[a:b] = b'\1' * (b-a)
                        else:
                            for row in range(y0, y1):
                                a = start + (row*width+x0)*4
                                b = start + (row*width+x1)*4
                                allowed[a:b] = b'\1' * (b-a)
                    self.assertNotEqual(original[start:start+length], built[start:start+length])
                self.assertTrue(all(a == b or ok for a, b, ok in zip(original, built, allowed)),
                                "Unexpected change to artwork, another texture or KSCL metadata")


if __name__ == "__main__":
    unittest.main()
