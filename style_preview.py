"""Build a separate, non-installed typography trial from verified KSCL originals.

Uses Windows Times New Roman for this approximation; does not claim to identify
the game's original typeface. The preview reopens the compressed output, rather
than showing only the intermediate rendering. No game assets are embedded here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

import layout_translation as layout


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


def trial_label(source, name, text):
    heading = name.startswith("fnt_title_")
    option = name.startswith("option_top_")
    loop = name.endswith(("_Loop", "_loop"))
    selected = name.endswith("_on") or name.startswith("Press_Any_Button")
    opaque = source.getchannel("A").histogram()[255] >= source.width * source.height * .99
    # Exclude the dark shadow and low-opacity halo when measuring the letters.
    light = source.convert("L")
    alpha = source.getchannel("A")
    core = ImageChops.multiply(light, alpha)
    peak = core.getextrema()[1]
    box = core.point(lambda p: 255 if p >= peak * .65 else 0).getbbox()
    if box is None:
        raise ValueError(f"No lettering in {name}")
    size = 128
    font = ImageFont.truetype(str(Path("C:/Windows/Fonts") /
                                    ("timesbd.ttf" if heading else "times.ttf")), size)
    spacing = 11 if heading else 1.4
    mask = Image.new("L", (5000, 260))
    draw = ImageDraw.Draw(mask)
    x = 10.
    for ch in text:
        draw.text((round(x), 170), ch, font=font, fill=255, anchor="ls")
        x += draw.textlength(ch, font=font) + spacing
    glyph = mask.crop(mask.getbbox())
    target_h = box[3] - box[1]
    # "Nueva partida" has descenders absent from "New Game". Match its
    # capital height, allowing the p to descend below the original baseline.
    reference_h = glyph.height
    if name.startswith("fnt_menu_newgame"):
        reference = Image.new("L", mask.size)
        ImageDraw.Draw(reference).text((10, 170), "New Game", font=font,
                                       fill=255, anchor="ls")
        ref_box = reference.getbbox()
        reference_h = ref_box[3] - ref_box[1]
    scale = target_h / reference_h
    target_w = min(round(glyph.width * scale), source.width - 24)
    # Keep the cap height: fit long Spanish lines horizontally rather than
    # making every letter smaller in both axes.
    glyph = glyph.resize((target_w, round(glyph.height * scale)), Image.Resampling.LANCZOS)
    x = box[0] if heading else round((box[0] + box[2] - glyph.width) / 2)
    y = box[1]
    x = max(12, min(x, source.width - glyph.width - 12))
    mask = Image.new("L", source.size)
    mask.paste(glyph, (x, y))
    result = Image.new("RGBA", source.size, (0, 0, 0, 255 if opaque else 0))

    def layer(color, coverage, strength=1.):
        ink = Image.new("RGBA", source.size, (*color, 0))
        ink.putalpha(coverage.point(lambda p: round(p * strength)))
        result.alpha_composite(ink)

    shadow = Image.new("L", source.size)
    shadow.paste(glyph, (x + 1, y + 3))
    layer((0, 0, 0), shadow.filter(ImageFilter.GaussianBlur(2)), .85)
    if heading:
        layer((181, 201, 207), mask)
    elif loop:
        layer((221, 187, 43), mask.filter(ImageFilter.GaussianBlur(4.5)), .72)
        layer((228, 211, 91), mask.filter(ImageFilter.GaussianBlur(1.5)), .78)
    elif selected:
        halo = (245, 216, 149) if option else (255, 182, 27)
        layer(halo, mask.filter(ImageFilter.GaussianBlur(6)), .8)
        layer(halo, mask.filter(ImageFilter.GaussianBlur(2.5)), .78)
        layer((255, 247, 217), mask)
    elif option:
        layer((171, 140, 45), mask.filter(ImageFilter.GaussianBlur(6)), .45)
        layer((205, 191, 140), mask, .76)
    else:
        layer((204, 201, 183), mask)
    return result


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
