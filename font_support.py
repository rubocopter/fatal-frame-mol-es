"""Build an extended G1N font from the game's original glyphs.

The original font is read-only. Added glyphs are composed from its existing
Latin letters and diacritics. No fan-patch font or translation is imported.
Output is a technical draft until the new codepoints are tested in the game.

G1N layout checked against lehieugch68/G1N-Font-Editor.
"""

from __future__ import annotations

import collections
import hashlib
import json
import struct
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps

from clean_translation import CODE, ROOT
from fmsg_format import GAME

ORIGINAL = GAME / "binary" / "font" / "JP" / "default.g1n"
OUTPUT = ROOT / "work" / "font_original_extended.g1n"
PREVIEW = ROOT / "work" / "spanish_glyphs_preview.png"
EDITED = ROOT / "translations_from_english.json"

CHAR_BASES = {
    "á": "a", "í": "i", "ó": "o", "ú": "u", "ñ": "n",
    "Á": "A", "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N",
    "¿": "?", "¡": "!",
}
LOWER_ACCENT_Y = 34
UPPER_ACCENT_Y = 22
GLYPH_RECORD = 12
FONT_CELL_BYTES = 2450


def cmap_for(data: bytes):
    if data[:8] != b"_N1G0000":
        raise ValueError("Unexpected G1N signature")
    if struct.unpack_from("<II", data, 24) != (1, 1):
        raise ValueError("Expected one 4bpp font page with one palette")
    table_offset = struct.unpack_from("<I", data, 32)[0]
    assert table_offset == 100
    return list(struct.unpack_from("<65536H", data, table_offset))


def font_details(data: bytes):
    codes = cmap_for(data)
    count = max(codes) + 1
    table_end = 100 + 65536 * 2
    atlas = struct.unpack_from("<I", data, 20)[0]
    if table_end + count * GLYPH_RECORD != atlas:
        raise ValueError("Unexpected metadata/atlas layout")
    if len(data) - atlas != count * FONT_CELL_BYTES:
        raise ValueError("Unexpected glyph bitmap size")
    return codes, count, table_end, atlas


def glyph_image(data: bytes, codes: list[int], character: str):
    index = codes[ord(character)]
    if index == 0:
        raise ValueError(f"Missing glyph: {character!r}")
    meta = 100 + 65536 * 2 + index * GLYPH_RECORD
    width, height = data[meta], data[meta + 1]
    width += width % 2
    atlas = struct.unpack_from("<I", data, 20)[0]
    encoded = data[atlas + index * FONT_CELL_BYTES:atlas + (index + 1) * FONT_CELL_BYTES]
    decoded = bytearray()
    for byte in encoded:
        decoded.extend(((byte >> 4) * 16, (byte & 0xF) * 16))
    return Image.frombytes("L", (width, height), bytes(decoded[:width * height]))


def glyph_pixels(bitmap: Image.Image, base_pixels: bytes):
    if bitmap.width % 2:
        raise ValueError("Glyph bitmaps must have even width")
    flat = list(bitmap.convert("L").getdata())
    packed = bytearray((min(15, max(0, (flat[i] + 8) // 16)) << 4)
                       | min(15, max(0, (flat[i + 1] + 8) // 16))
                       for i in range(0, len(flat), 2))
    if len(packed) > FONT_CELL_BYTES:
        raise ValueError("Glyph bitmap exceeds fixed cell")
    return bytes(packed) + base_pixels[len(packed):]


def extract_acute(data: bytes, codes: list[int]):
    accent = glyph_image(data, codes, "É")
    plain = glyph_image(data, codes, "E")
    difference = ImageChops.difference(accent, plain)
    upper = difference.crop((0, 0, difference.width, 31))
    box = upper.getbbox()
    if box is None:
        raise ValueError("No acute accent found in original É")
    return accent.crop(box)


def extract_tilde(data: bytes, codes: list[int]):
    tilde = glyph_image(data, codes, "~")
    box = tilde.getbbox()
    if box is None:
        raise ValueError("Original font's tilde is blank")
    return tilde.crop(box)


def compose_glyph(data: bytes, codes: list[int], target: str):
    original = CHAR_BASES[target]
    source = glyph_image(data, codes, original)
    if target in "¿¡":
        visible = source.getbbox()
        glyph = Image.new("L", source.size)
        glyph.paste(ImageOps.flip(ImageOps.mirror(source.crop(visible))),
                    visible[:2])
        return glyph

    glyph = source.copy()
    is_lower = target.islower()
    y = LOWER_ACCENT_Y if is_lower else UPPER_ACCENT_Y
    if target.lower() == "ñ":
        mark = extract_tilde(data, codes)
        # The original '~' is an independent, larger punctuation glyph.
        mark = mark.resize((14 if is_lower else 17, 7), Image.Resampling.LANCZOS)
    else:
        mark = extract_acute(data, codes)
        if is_lower:
            # The source uppercase acute is naturally wider than a lowercase accent.
            mark = mark.resize((8, 8), Image.Resampling.LANCZOS)
    if target == "í":
        # Remove the original dot while retaining the stem.
        glyph.paste(0, (0, 0, glyph.width, 43))
    x = (glyph.width - mark.width) // 2
    glyph.paste(ImageChops.lighter(glyph.crop((x, y, x + mark.width, y + mark.height)), mark),
                (x, y))
    return glyph


def audit(data: bytes):
    codes = cmap_for(data)
    missing = collections.Counter()
    first = {}
    for item in json.loads(EDITED.read_text(encoding="utf-8")):
        for char in CODE.sub("", item["es"]):
            if (not char.isspace() and ord(char) < 65536
                    and codes[ord(char)] == 0):
                missing[char] += 1
                first.setdefault(char, f"{item['file']}#{item['index']}")
    return {"missing": dict(missing), "first_occurrence": first,
            "covered": not bool(missing)}


def build():
    original = ORIGINAL.read_bytes()
    cmap, count, table_end, atlas = font_details(original)
    additions = [char for char in CHAR_BASES if cmap[ord(char)] == 0]
    output = bytearray(original[:table_end])
    for index, char in enumerate(additions, start=count):
        struct.pack_into("<H", output, 100 + ord(char) * 2, index)

    metadata = bytearray(original[table_end:atlas])
    bitmaps = bytearray(original[atlas:])
    for i, char in enumerate(additions):
        base_idx = cmap[ord(CHAR_BASES[char])]
        base_meta = original[table_end + base_idx * GLYPH_RECORD:
                             table_end + (base_idx + 1) * GLYPH_RECORD]
        new_bitmap = compose_glyph(original, cmap, char)
        base_pixel = original[atlas + base_idx * FONT_CELL_BYTES:
                              atlas + (base_idx + 1) * FONT_CELL_BYTES]
        metadata.extend(base_meta[:8] +
                        struct.pack("<I", (count + i) * FONT_CELL_BYTES))
        bitmaps.extend(glyph_pixels(new_bitmap, base_pixel))

    output.extend(metadata)
    output.extend(bitmaps)
    struct.pack_into("<I", output, 8, len(output))
    struct.pack_into("<I", output, 20, atlas + len(additions) * GLYPH_RECORD)
    result = bytes(output)
    new_cmap, new_count, new_meta_end, new_atlas = font_details(result)
    assert new_count == count + len(additions)
    assert new_cmap[32] == cmap[32]
    assert all(new_cmap[code] == old for code, old in enumerate(cmap) if old)
    assert result[new_meta_end:new_meta_end + count * GLYPH_RECORD] == original[table_end:atlas]
    assert result[new_atlas:new_atlas + count * FONT_CELL_BYTES] == original[atlas:]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(result)

    review = Image.new("RGB", (len(additions) * 90, 108), "#151515")
    draw = ImageDraw.Draw(review)
    for i, char in enumerate(additions):
        bitmap = glyph_image(result, new_cmap, char)
        review.paste(bitmap.convert("RGB"), (i * 90 + 8, 24))
        draw.text((i * 90 + 8, 6), char, fill="white")
    review.save(PREVIEW)

    report = {
        "status": "TECHNICAL DRAFT - not tested in game",
        "base_font_sha256": hashlib.sha256(original).hexdigest(),
        "output_font_sha256": hashlib.sha256(result).hexdigest(),
        "original_glyphs": count,
        "added_glyphs": additions,
        "original_font": audit(original),
        "extended_font": audit(result),
        "output": str(OUTPUT),
    }
    (ROOT / "work" / "font_qa.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
