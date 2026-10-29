"""Build a separate, non-installed typography trial from verified KSCL originals.

Uses Windows Times New Roman for this approximation; does not claim to identify
the game's original typeface. The preview reopens the compressed output, rather
than showing only the intermediate rendering. No game assets are embedded here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import layout_translation as layout
from label_style import trial_label


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "work" / "style_trial"
CASES = {
    "title_layout.kscl": {
        "Press_Any_Button": "Pulsa cualquier botón",
        "Press_Any_Button_Loop": "Pulsa cualquier botón",
    },
    "title_layout_menu_parts.kscl": {
        "fnt_menu_newgame_off": "Nueva partida",
        "fnt_menu_newgame_on": "Nueva partida",
        "fnt_menu_newgame_on_loop": "Nueva partida",
    },
    "option_menu_parts.kscl": {
        "option_top_gtext_00_off": "Ajustes generales",
        "option_top_gtext_00_on": "Ajustes generales",
    },
    "cmn_title_mission.kscl": {"fnt_title_option": "Opciones"},
}



def build():
    game = layout.GAME
    backup = game / ".fatal-frame-es-originals"
    entries = json.loads((backup / "backup_manifest.json").read_text(encoding="utf8"))["files"]
    rows, report = [], []
    for filename, labels in CASES.items():
        rel = Path("binary/layout/en") / filename
        raw = (backup / rel).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entries[rel.as_posix()]["original_sha256"]
        current = (game / rel).read_bytes()
        assert hashlib.sha256(current).hexdigest() == entries[rel.as_posix()]["patched_sha256"]
        rebuilt = bytearray(current)
        index = layout.textures(raw)
        assert index == layout.textures(current)
        for name, text in labels.items():
            fmt, w, h, start, length = index[name]
            original = layout.decode(fmt, w, h, raw[start:start + length])
            generated = trial_label(original, name, text)
            rebuilt[start:start + length] = layout.encode(generated, fmt, length)
        dest = OUTPUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(rebuilt)
        reread = dest.read_bytes()
        assert layout.textures(reread) == index
        position = 0
        ranges = sorted((index[n][3], index[n][3] + index[n][4]) for n in labels)
        for start, end in ranges:
            assert reread[position:start] == current[position:start]
            position = end
        assert reread[position:] == current[position:]
        for name, text in labels.items():
            fmt, w, h, start, length = index[name]
            images = [layout.decode(fmt, w, h, data[start:start + length])
                      for data in (raw, current, reread)]
            rows.append((name, images))
        report.append({"file": rel.as_posix(), "sprites": len(labels),
                       "sha256": hashlib.sha256(reread).hexdigest()})
    sheet = Image.new("RGB", (1590, 80 + 150 * len(rows)), (23, 27, 32))
    draw = ImageDraw.Draw(sheet)
    ui = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
    small = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    for col, title in enumerate(("Original inglés", "Español instalado", "Prueba de estilo")):
        draw.text((col * 530 + 18, 18), title, font=ui, fill=(225, 216, 186))
    for i, (name, images) in enumerate(rows):
        y = 70 + i * 150
        draw.text((18, y), name, font=small, fill=(158, 170, 182))
        factor = min(1., 495 / images[0].width)
        for col, im in enumerate(images):
            im = im.resize((round(im.width * factor), round(im.height * factor)), Image.Resampling.LANCZOS)
            x = col * 530 + (530 - im.width) // 2
            sheet.paste(im, (x, y + 35), im)
    sheet.save(OUTPUT / "comparacion.png")
    # A shorter comparison for reviewing the design without internal filenames.
    selected_rows = [(0, "Pantalla inicial"), (2, "Nueva partida · normal"),
                     (3, "Nueva partida · seleccionado"),
                     (6, "Ajustes generales · seleccionado"), (7, "Título de Opciones")]
    compact = Image.new("RGB", (1590, 80 + 150 * len(selected_rows)), (23, 27, 32))
    compact_draw = ImageDraw.Draw(compact)
    compact.paste(sheet.crop((0, 0, 1590, 65)), (0, 0))
    for target, (source_row, title) in enumerate(selected_rows):
        source_y = 70 + source_row * 150
        target_y = 70 + target * 150
        compact.paste(sheet.crop((0, source_y + 30, 1590, source_y + 145)),
                      (0, target_y + 30))
        compact_draw.text((18, target_y), title, font=small, fill=(158, 170, 182))
    compact.save(OUTPUT / "muestra.png")
    (OUTPUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print(f"Trial only: {sum(e['sprites'] for e in report)} sprites / {len(report)} KSCL; game unchanged")
    print(OUTPUT / "comparacion.png")


if __name__ == "__main__":
    build()
