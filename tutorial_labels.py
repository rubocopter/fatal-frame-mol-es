"""Spanish UI inside the original 364x204 tutorial screenshots.

TUTORIALS is JSON-serializable metadata; importing it needs only the standard
library. Each region records the exact visible English, its Spanish replacement,
an exclusive pixel box, and the original lettering style. Coordinates refer to
the unscaled source texture, never to the enlarged review pictures.

The renderer samples the surrounding screenshot to remove each English label,
then draws fitted, antialiased Spanish lettering. It returns every permitted
write rectangle so a caller can preserve pixels/BC blocks outside those areas.
Japanese lens symbols, controller glyphs, portraits, maps and other artwork are
outside the regions. The photographed film packaging is artwork, not a UI
caption. No Artbook assets are included.

Run ``python -B tutorial_labels.py --review`` to make local PNG proofs and an
audit JSON under work/tutorial_review. This never builds or installs a patch.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path


def _region(box, source, text, size=6, style="body", align="left", **options):
    return dict(box=list(box), source=source, text=text, size=size,
                style=style, align=align, **options)


def _title(source, text):
    return _region((6, 10, 138, 25), source, text, 10, "title", font="bold")


def _tabs(selected):
    return [
        _region((18, 39, 74, 50), "Change Equipment", "Cambiar equipo", 5.7,
                "selected" if selected == "equipment" else "tab", "center"),
        _region((86, 39, 137, 50), "Enhancements", "Mejoras", 5.7,
                "selected" if selected == "enhancements" else "tab", "center"),
    ]


def _camera_menu(selected="equipment", lenses=False):
    return [_title("Camera Obscura", "Cámara Oscura"), *_tabs(selected),
            _region((18, 67, 68, 76), "Film", "Película", 5, "selected"
                    if not lenses else "tab", "center"),
            _region((18, 82, 68, 91), "Lenses", "Lentes", 5, "selected"
                    if lenses else "tab", "center"),
            _region((15, 97, 73, 106), "Equipment Upgrades", "Mejoras del equipo",
                    4.8, "tab", "center")]


def _menu_film(number="14"):
    # Repaint the complete string: the p's descender in Type overlaps the
    # neighbouring digits in the tiny source. Preserve the film icon itself.
    return _region((300, 159, 337, 168), f"Type-{number}×10", f"Tipo-{number}×10", 5, "hud")


def _viewfinder_film(number="07", quantity="∞"):
    return _region((254, 187, 291, 194), f"Type-{number}×{quantity}",
                   f"Tipo-{number}×{quantity}", 3.7, "hud")


def _footer(source, text):
    options = {}
    if source.startswith(("Blast:", "Alert:")):
        options = {"accent_text": text.split(":", 1)[0] + ":",
                   "accent_color": [39, 108, 27]}
    return _region((82, 183, 278, 199), source, text, 4.8, "footer", "center", **options)


def _spec(name, regions):
    return {"name": name, "size": [364, 204], "regions": regions}


_NOTEBOOK_EN = [
    "The main island of the", "Rogetsu Islands. Has",
    "historically had little contact", "with the mainland,",
    "so its unique local culture", "has remained intact. Came",
    "to prominence when the", "Rogetsu Hall sanatorium",
    "was built, and when the", "Rogetsu Kagura was made",
    "into a tourist attraction.",
]
_NOTEBOOK_ES = [
    "La isla principal del", "archipiélago de Rogetsu.",
    "Siempre tuvo poco contacto", "con el continente, por lo",
    "que conservó su cultura.", "Cobró importancia al",
    "construirse el sanatorio", "del Pabellón Rogetsu y al",
    "convertirse el Kagura de", "Rogetsu en una atracción", "turística.",
]


_SCREENS = {
    "TU030_1": [
        _region((97, 135, 299, 174), "Examine", "Examinar", 31, "prompt"),
    ],
    "TU030_2": [
        _region((97, 135, 325, 174), "Reach Out", "Extender la mano", 31, "prompt"),
    ],
    "TU030_3": [
        _region((253, 175, 317, 187), "Reach Out", "Extender la mano", 8.3, "prompt"),
    ],
    "TU040_1": [_viewfinder_film()],
    "TU080_1": [
        _title("Notebook", "Cuaderno"),
        _region((98, 49, 161, 59), "Rogetsu Isle", "Isla de Rogetsu", 7.2,
                "paper", "center", sample_strip=[87, 93]),
        _region((79, 73, 123, 83), "Summary", "Resumen", 7.2, "paper_blue",
                sample_strip=[134, 140]),
        _region((50, 72, 68, 80), "NEW", "NUEVO", 2.8, "paper_tag", "center"),
        *[_region((188, y0, 274, y1), en, es, 5.4, "paper", sample_strip=[277, 282])
          for (y0, y1), en, es in zip(
              [(50, 57), (62, 70), (75, 82), (87, 94), (99, 106), (112, 119),
               (124, 131), (136, 143), (148, 155), (161, 168), (173, 180)],
              _NOTEBOOK_EN, _NOTEBOOK_ES)],
        _region((340, 197, 363, 204), "Back", "Volver", 3.8, "footer"),
    ],
    "TU110_1": [
        _title("Save Point", "Punto de guardado"),
        _region((18, 43, 95, 54), "Save", "Guardar", 8.5, "warm"),
        _region((18, 63, 95, 74), "Purchase", "Comprar", 7, "menu"),
        _region((18, 83, 95, 94), "Extras", "Extras", 7, "menu"),
        _region((18, 103, 95, 114), "Costumes", "Trajes", 7, "menu"),
        _region((246, 9, 359, 20), "Phase I : The Summoning",
                "Fase I: La invocación", 7, "chapter", "right"),
        _region((234, 38, 255, 45), "Score", "Puntos", 4.4, "footer"),
        _region((263, 51, 358, 59), "Search the second floor for the mask.",
                "Busca la máscara en la segunda planta.", 4.5, "footer", "right"),
        _region((241, 159, 277, 168), "Type-07×∞", "Tipo-07×∞", 5, "hud"),
        _footer("Save your progress.", "Guarda tu progreso."),
    ],
    "TU140_1": [
        _title("Camera Obscura", "Cámara Oscura"), *_tabs("enhancements"),
        _region((17, 67, 68, 76), "Camera Obscura", "Cámara Oscura", 4.8,
                "selected", "center"),
        _region((19, 82, 68, 91), "Lenses", "Lentes", 5, "tab", "center"),
        _region((173, 40, 224, 49), "Blue Spirit Stone",
                "Piedra espiritual azul", 4.6, "body"),
        _region((218, 64, 257, 71), "Stones Required", "Piedras necesarias",
                3.5, "body", "center"),
        _region((95, 76, 140, 84), "Max. Power", "Potencia máxima", 5.4),
        _region((95, 92, 140, 100), "Sensitivity", "Sensibilidad", 5.4),
        _region((95, 108, 140, 116), "Charge", "Carga", 5.4),
        _region((95, 124, 140, 132), "Storage", "Capacidad", 5.4),
        _region((95, 140, 140, 148), "Spirit Power", "Poder espiritual", 5.4),
        _menu_film(),
        _footer("Increases damage dealt to ghosts.",
                "Aumenta el daño infligido a los fantasmas."),
    ],
    "TU150_0": [
        _title("Menu", "Menú"),
        *[_region((18, y, 95, y + 10), en, es, 7,
                  "warm" if en == "Map" else "menu")
          for y, en, es in [(43, "Map", "Mapa"), (57, "Items", "Objetos"),
                            (71, "File", "Archivos"), (85, "Records", "Registros"),
                            (99, "Ghost List", "Lista de fantasmas")]],
        _region((249, 9, 359, 20), "Prelude : Blossoming",
                "Preludio: Florecimiento", 7, "chapter", "right"),
        _region((234, 38, 255, 45), "Score", "Puntos", 4.4, "footer"),
        _region((263, 51, 358, 59), "Unlock the door to the Aso Museum.",
                "Abre la puerta del Museo Aso.", 4.5, "footer", "right"),
        _region((241, 159, 277, 168), "Type-07×∞", "Tipo-07×∞", 5, "hud"),
        _footer("View a map displaying your current location.",
                "Consulta un mapa de tu ubicación actual."),
    ],
    "TU150_1": [
        _title("Items", "Objetos"),
        _region((20, 39, 74, 50), "Consumables", "Consumibles", 5.7, "tab", "center"),
        _region((86, 39, 136, 50), "Key Items", "Objetos clave", 5.7,
                "selected", "center"),
        _region((47, 68, 103, 76), "Flashlight", "Linterna", 5.8),
        _region((47, 82, 111, 90), "Ivy-Patterned Key", "Llave con hiedra", 5.8),
        _footer('A key with an ivy pattern.\n"Museum" is engraved on it.',
                'Llave decorada con hiedra.\nLleva grabado "Museo".'),
    ],
    "TU150_2": [
        _title("Files", "Archivos"),
        *[_region((x, 39, x + 53, 50), en, es, 5.7,
                  "selected" if en == "Records" else "tab", "center")
          for x, en, es in [(20, "Documents", "Documentos"),
                            (86, "Records", "Registros"),
                            (151, "Other", "Otros"), (216, "Pictures", "Fotografías")]],
        _region((26, 68, 41, 76), "NEW", "NUEVO", 3.8, "tab"),
        _region((43, 68, 132, 77), "Nurse's Memo", "Nota de la enfermera", 5.8),
        _footer("Notes where a key has been left.",
                "Nota que indica dónde han dejado una llave."),
    ],
    "TU150_3": [
        _title("Map", "Mapa"),
        _region((12, 34, 161, 42), "Rogetsu Hall - 2F",
                "Pabellón Rogetsu: planta 2", 5.5),
        _region((15, 43, 161, 51), "Entrance Hall - 2F",
                "Vestíbulo, segunda planta", 5.5),
    ],
    "TU180_1": [
        *_camera_menu(lenses=True),
        _region((151, 69, 181, 76), "Equipped", "Equipado", 3.8, "selected", "center"),
        _menu_film(),
        _footer("Blast: Takes a more powerful\nshot when used. (Low)",
                "Ráfaga: permite hacer una foto\nmás potente (potencia baja)."),
    ],
    "TU190_1": [
        *_camera_menu(),
        _region((132, 68, 200, 77), "Type-07 Film", "Película tipo 07", 6),
        _region((132, 84, 200, 93), "Type-14 Film", "Película tipo 14", 6),
        _region((95, 84, 119, 92), "Equipped", "Equipado", 3.8, "selected", "center"),
        _menu_film(), _footer("Equip film.", "Equipar película."),
    ],
    "TU190_2": [
        _region((143, 145, 253, 169), "Type-14×10", "Tipo-14×10", 15.3),
    ],
    "TU200_1": [
        _title("Camera Obscura", "Cámara Oscura"), *_tabs("enhancements"),
        _region((17, 67, 68, 76), "Camera Obscura", "Cámara Oscura", 4.8,
                "tab", "center"),
        _region((19, 82, 68, 91), "Lenses", "Lentes", 5, "selected", "center"),
        _region((173, 40, 224, 49), "Red Spirit Stone",
                "Piedra espiritual roja", 4.6),
        _region((218, 64, 257, 71), "Stones Required", "Piedras necesarias",
                3.5, "body", "center"),
        _menu_film(),
        _footer("Blast: Takes a more powerful\nshot when used. (Low)",
                "Ráfaga: permite hacer una foto\nmás potente (potencia baja)."),
    ],
    "TU210_1": [
        *_camera_menu(),
        _region((129, 93, 158, 103), "Equipped", "Equipado", 3.8, "selected", "center"),
        _menu_film(),
        _footer("Alert: Indicates timing for Fatal Frame\nshots when equipped.",
                "Alerta: indica cuándo hacer un encuadre\nfatal si está equipado."),
    ],
    "TU302_0": [_viewfinder_film()],
    "TU303_0": [_viewfinder_film("14", "10")],
    "TU303_1": [
        _region((69, 28, 135, 39), "FATAL FRAME", "ENCUADRE FATAL", 7.4,
                "rating", font="bold"),
        _region((69, 41, 116, 49), "Combo Hit", "Impactos seguidos", 5.5, "rating"),
        _region((69, 50, 116, 58), "Point", "Puntos", 5.5, "rating"),
        _region((69, 59, 116, 67), "Damage", "Daño", 5.5, "rating"),
        _region((139, 50, 151, 58), "pts", "ptos.", 4.4, "rating"),
        _viewfinder_film("14", "09"),
    ],
    "TU305_0": [
        _region((178, 95, 354, 117), "Find Misaki Aso.",
                "Encuentra a Misaki Aso.", 15.3, "prompt", "right"),
    ],
    "TU306_0": [
        _region((88, 89, 264, 126), "Now Saving...", "Guardando...", 19,
                "saving", "center", font="handwritten"),
    ],
}

TUTORIALS = {f"ex_texture/tutorial/{name}.kslt": {name: _spec(name, regions)}
             for name, regions in _SCREENS.items()}

# These were inspected at their original resolution. Their contents are scene
# art, Japanese lettering, controller illustrations or unlabelled HUD segments.
INSPECTED_WITHOUT_ENGLISH_UI = [
    "TU000_0", "TU000_1", "TU010_0", "TU010_1", "TU010_2", "TU010_3",
    "TU010_4", "TU010_5", "TU020_0", "TU030_0", "TU040_0", "TU040_2",
    "TU040_3", "TU050_0", "TU070_0", "TU070_1", "TU070_2", "TU070_3",
    "TU080_0", "TU100_0", "TU100_1", "TU100_2", "TU100_3", "TU100_4",
    "TU110_0", "TU140_0", "TU180_0", "TU180_2", "TU190_0", "TU200_0",
    "TU210_0", "TU210_2", "TU300_0", "TU301_0", "TU303_2", "TU304_0",
]


_STYLES = {
    # RGB, halo RGB, halo strength. Body text in these small screenshots is
    # deliberately muted, matching the original rather than bright white.
    "body": ((173, 191, 194), None, 0),
    "title": ((184, 211, 219), (53, 133, 156), .25),
    "menu": ((95, 159, 184), (32, 114, 147), .22),
    "warm": ((229, 223, 204), (220, 84, 43), .35),
    "tab": ((113, 174, 195), (37, 122, 152), .18),
    "selected": ((187, 232, 242), (78, 188, 232), .55),
    "chapter": ((128, 206, 222), (64, 156, 182), .25),
    "footer": ((163, 181, 180), None, 0),
    "hud": ((181, 199, 208), None, 0),
    "prompt": ((184, 202, 199), None, 0),
    "paper": ((64, 79, 78), None, 0),
    "paper_blue": ((41, 52, 137), None, 0),
    "paper_tag": ((43, 89, 103), None, 0),
    "rating": ((184, 218, 237), (88, 158, 231), .65),
    "saving": ((153, 231, 255), (17, 189, 243), .8),
}


@lru_cache(maxsize=6)
def _font(kind):
    from PIL import ImageFont

    filenames = {"serif": "times.ttf", "bold": "timesbd.ttf",
                 "handwritten": "segoepr.ttf"}
    filename = filenames.get(kind)
    if filename is None:
        raise ValueError(f"Unknown tutorial font: {kind}")
    candidates = [Path("C:/Windows/Fonts") / filename,
                  Path("/usr/share/fonts/truetype/dejavu") /
                  ("DejaVuSerif-Bold.ttf" if kind == "bold" else "DejaVuSerif.ttf")]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), 100)
    raise RuntimeError(f"No suitable font installed for tutorial style {kind}")


def _text_mask(region, width, height):
    from PIL import Image, ImageDraw

    font = _font(region.get("font", "serif"))
    lines = region["text"].split("\n")
    glyphs = []
    for text in lines:
        box = font.getbbox(text)
        if box[2] == box[0] or box[3] == box[1]:
            raise ValueError("Tutorial labels must contain visible text")
        tracking = 8 if region["style"] == "title" else 0
        glyph = Image.new("L", (box[2] - box[0] + len(text) * tracking + 4,
                                box[3] - box[1] + 4))
        draw = ImageDraw.Draw(glyph)
        x = 2 - box[0]
        for char in text:
            draw.text((round(x), 2 - box[1]), char, font=font, fill=255)
            x += draw.textlength(char, font=font) + tracking
        glyphs.append(glyph.crop(glyph.getbbox()))
    # Supersample both axes, fitting long Spanish lines horizontally. Keep the
    # same letter height across every line of a multiline description.
    scale = 4
    pad = 1
    line_h = min(float(region["size"]), (height - pad * 2 - (len(lines) - 1)) / len(lines))
    if line_h <= 0 or width <= 2:
        raise ValueError("Tutorial text region is too small")
    max_h = max(g.height for g in glyphs)
    factor = line_h * scale / max_h
    max_w = max(g.width * factor for g in glyphs)
    squeeze = min(1., (width - pad * 2) * scale / max_w)
    fitted = [g.resize((max(1, round(g.width * factor * squeeze)),
                        max(1, round(g.height * factor))), Image.Resampling.LANCZOS)
              for g in glyphs]
    mask = Image.new("L", (width * scale, height * scale))
    accent_mask = Image.new("L", mask.size)
    block_h = len(lines) * line_h * scale + (len(lines) - 1) * scale
    y = round((height * scale - block_h) / 2)
    for index, glyph in enumerate(fitted):
        align = region.get("align", "left")
        x = ((width * scale - glyph.width) // 2 if align == "center" else
             width * scale - glyph.width - pad * scale if align == "right" else pad * scale)
        pos = (x, y + round(line_h * scale) - glyph.height)
        mask.paste(glyph, pos)
        if index == 0 and region.get("accent_text"):
            prefix = round(font.getlength(region["accent_text"]) * factor * squeeze)
            accent_mask.paste(glyph.crop((0, 0, min(prefix, glyph.width), glyph.height)), pos)
        y += round((line_h + 1) * scale)
    return (mask.resize((width, height), Image.Resampling.LANCZOS),
            accent_mask.resize((width, height), Image.Resampling.LANCZOS))


def _background(source, box, region):
    """Reconstruct a local strip using clean rows immediately above/below.

    Column sampling retains horizontal lighting, paper shading and the menu's
    cyan/red tint. Only the label's small rectangle is interpolated; there is no
    blur, opaque panel or global filtering over the screenshot.
    """
    from PIL import Image, ImageFilter, ImageStat

    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if "sample_strip" in region:
        # Blank paper at the same height retains the original ruled lines and
        # grain. Restore the page's horizontal shading from a clean upper row.
        left, right = region["sample_strip"]
        donor = source.crop((left, y0, right, y1)).resize((1, h), Image.Resampling.BOX)
        clean_y = max(0, y0 - 1)
        reference = ImageStat.Stat(source.crop((left, clean_y, right, clean_y + 1))).mean
        shading = source.crop((x0, clean_y, x1, clean_y + 1)).filter(ImageFilter.GaussianBlur(1.5))
        patch = Image.new("RGBA", (w, h))
        for y in range(h):
            row = donor.getpixel((0, y))
            for x in range(w):
                shade = shading.getpixel((x, 0))
                patch.putpixel((x, y), tuple(max(0, min(255, round(row[c] + shade[c] - reference[c])))
                                             for c in range(3)) + (255,))
        return patch
    upper = source.crop((x0, max(0, y0 - 1), x1, max(0, y0 - 1) + 1))
    lower = source.crop((x0, min(source.height - 1, y1),
                         x1, min(source.height - 1, y1) + 1))
    # Avoid stretching high-frequency paper/stone grain into vertical stripes.
    blur = 2.5 if region["style"] == "title" else .65
    upper = upper.filter(ImageFilter.GaussianBlur(blur))
    lower = lower.filter(ImageFilter.GaussianBlur(blur))
    patch = Image.new("RGBA", (w, h))
    for y in range(h):
        patch.paste(Image.blend(upper, lower, (y + 1) / (h + 1)), (0, y))
    return patch


def repaint_tutorial(image, name, spec):
    """Return ``(copy_with_Spanish_UI, [exclusive_changed_rectangles])``.

    ``spec`` is the value at ``TUTORIALS[relative_file][texture_name]``.
    Pillow is loaded lazily. No source image, metadata or filesystem is mutated.
    RGB/RGBA images are supported; original alpha is preserved pixel for pixel,
    including inside lettering regions. Invalid dimensions/regions fail early.
    """
    from PIL import Image, ImageFilter

    if image.mode not in ("RGB", "RGBA"):
        raise ValueError(f"Unsupported tutorial image mode: {image.mode}")
    if spec.get("name", name) != name:
        raise ValueError(f"Tutorial spec name does not match {name}")
    if tuple(spec.get("size", (364, 204))) != image.size:
        raise ValueError(f"Unexpected tutorial dimensions for {name}: {image.size}")
    regions = spec["regions"]
    boxes = []
    for region in regions:
        box = tuple(region["box"])
        if (len(box) != 4 or any(type(v) is not int for v in box) or
                not (0 <= box[0] < box[2] <= image.width and
                     0 <= box[1] < box[3] <= image.height)):
            raise ValueError(f"Invalid tutorial region for {name}: {box}")
        if region["style"] not in _STYLES:
            raise ValueError(f"Unknown tutorial style: {region['style']}")
        boxes.append(box)
    source = image.convert("RGBA")
    result = source.copy()
    for region, box in zip(regions, boxes):
        # Extras is already Spanish. Keeping it in the audit explicitly records
        # this reviewed label while preserving its original glyphs and artwork.
        if region["source"] == region["text"]:
            continue
        patch = _background(source, box, region)
        mask, accent_mask = _text_mask(region, patch.width, patch.height)
        ink, halo, amount = _STYLES[region["style"]]
        if halo:
            radius = 1.6 if region["style"] == "saving" else .7
            glow = Image.new("RGBA", patch.size, (*halo, 0))
            glow.putalpha(mask.filter(ImageFilter.GaussianBlur(radius)).point(
                lambda p: round(p * amount)))
            patch.alpha_composite(glow)
        if region["style"] not in ("paper", "paper_blue", "paper_tag"):
            shadow = Image.new("RGBA", patch.size, (0, 0, 0, 0))
            shifted = Image.new("L", patch.size)
            shifted.paste(mask, (0, 1))
            shadow.putalpha(shifted.filter(ImageFilter.GaussianBlur(.45)).point(
                lambda p: round(p * .45)))
            patch.alpha_composite(shadow)
        lettering = Image.new("RGBA", patch.size, (*ink, 0))
        lettering.putalpha(mask)
        patch.alpha_composite(lettering)
        if region.get("accent_color"):
            accent = Image.new("RGBA", patch.size, (*region["accent_color"], 0))
            accent.putalpha(accent_mask)
            patch.alpha_composite(accent)
        patch.putalpha(source.getchannel("A").crop(box))
        result.paste(patch, box[:2])
    changed = [box for region, box in zip(regions, boxes)
               if region["source"] != region["text"]]
    return result.convert(image.mode), changed


def _review(game, output):
    """Generate proofs from read-only installed textures, plus preservation QA."""
    import hashlib
    import json
    from PIL import Image, ImageChops, ImageDraw, ImageFont
    from layout_translation import decode, textures

    output.mkdir(parents=True, exist_ok=True)
    layout = game / "binary/layout/en"
    all_files = sorted((layout / "ex_texture/tutorial").glob("*.kslt"))
    expected = {Path(path).stem for path in TUTORIALS} | set(INSPECTED_WITHOUT_ENGLISH_UI)
    if {p.stem for p in all_files} != expected:
        raise ValueError("Tutorial source inventory differs from the 57 reviewed assets")
    report = {"inspected": len(all_files), "translated_textures": len(TUTORIALS),
              "regions": 0, "files": {}, "untouched": INSPECTED_WITHOUT_ENGLISH_UI}
    cards = []
    for rel, replacements in TUTORIALS.items():
        path = layout / rel
        raw = path.read_bytes()
        for name, spec in replacements.items():
            fmt, w, h, start, length = textures(raw)[name]
            original = decode(fmt, w, h, raw[start:start + length])
            updated, boxes = repaint_tutorial(original, name, spec)
            if original.getchannel("A").tobytes() != updated.getchannel("A").tobytes():
                raise AssertionError(f"Alpha changed: {name}")
            allowed = Image.new("L", original.size)
            draw = ImageDraw.Draw(allowed)
            for x0, y0, x1, y1 in boxes:
                draw.rectangle((x0, y0, x1 - 1, y1 - 1), fill=255)
            delta = ImageChops.difference(original.convert("RGB"), updated.convert("RGB"))
            outside = ImageChops.multiply(delta, Image.merge("RGB", (ImageChops.invert(allowed),) * 3))
            if outside.getbbox():
                raise AssertionError(f"Pixels changed outside declared regions: {name}")
            if not delta.getbbox():
                raise AssertionError(f"No translation rendered: {name}")
            original.save(output / f"{name}_original.png")
            updated.save(output / f"{name}_es.png")
            proof = Image.new("RGB", (728, 228), (20, 23, 26))
            proof.paste(original.convert("RGB"), (0, 24))
            proof.paste(updated.convert("RGB"), (364, 24))
            ImageDraw.Draw(proof).text((6, 6), f"{name} / EN", fill="white")
            ImageDraw.Draw(proof).text((370, 6), f"{name} / ES", fill="white")
            proof.save(output / f"{name}_comparison.png")
            cards.append(proof)
            report["regions"] += len(boxes)
            report["files"][rel] = {
                "name": name, "original_sha256": hashlib.sha256(raw).hexdigest(),
                "changed_boxes": boxes, "spec": spec,
                "alpha_preserved": True, "outside_regions_preserved": True,
            }
            if path.read_bytes() != raw:
                raise AssertionError(f"Source file changed: {path}")
    # Two comparison cards per row: original and Spanish at native resolution.
    for page, start in enumerate(range(0, len(cards), 10), 1):
        group = cards[start:start + 10]
        sheet = Image.new("RGB", (1456, ((len(group) + 1) // 2) * 228), (15, 18, 20))
        for i, card in enumerate(group):
            sheet.paste(card, ((i % 2) * 728, (i // 2) * 228))
        sheet.save(output / f"review_sheet_{page:02}.png")
    (output / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8")
    print(f"Reviewed {report['inspected']} assets; translated "
          f"{report['translated_textures']} textures / {report['regions']} regions. "
          "Alpha and pixels outside declared regions are unchanged.")


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", action="store_true", help="Generate local review PNGs only")
    parser.add_argument("--game", type=Path, default=Path(os.environ.get(
        "FF_MOL_GAME_DIR", r"E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse")))
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parent / "work/tutorial_review")
    args = parser.parse_args()
    if args.review:
        _review(args.game, args.output)
    else:
        parser.print_help()
