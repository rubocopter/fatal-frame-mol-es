"""Localize English KSCL interface labels, keeping layout and texture sizes.

Reads only the game's original assets. Outputs a separate build in work/;
never writes into the installed game. The brand logo, Japanese graphics,
and illustration assets retain their original pixels.
"""

from __future__ import annotations

import io
import hashlib
import json
import os
from pathlib import Path
import struct

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
GAME = Path(os.environ.get("FF_MOL_GAME_DIR", r"E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse"))
OUTPUT = ROOT / "work" / "layout_es" / "binary" / "layout" / "en"
FONT = Path(r"C:\Windows\Fonts\georgia.ttf")
NARROW_FONT = Path(r"C:\Windows\Fonts\arial.ttf")

# These are the labels actually drawn into the English interface textures.
# Preserve branded logos, Japanese calligraphy, and other non-language art.
LABELS = {
    "audio_list_parts.kscl": {"G_fnt_new": "NUEVO"},
    "change_costume_parts.kscl": {"G_fnt_new": "NUEVO"},
    "gallery_image_parts.kscl": {"G_fnt_new": "NUEVO"},
    "ghostlist_list_parts.kscl": {"G_fnt_new": "NUEVO"},
    "item_exchange_parts.kscl": {"G_fnt_new": "NUEVO"},
    "item_list_parts.kscl": {"G_fnt_new": "NUEVO"},
    "menu_synopsis_list_parts.kscl": {"G_fnt_new": "NUEVO"},
    "mission_select_list.kscl": {"msn_gtext_05": "Superado"},
    "mission_start_layout.kscl": {"Gtext_synopsis": "Resumen"},
    "now_saving_layout.kscl": {"R_fnt_save_ingame": "Guardando..."},
    "pause_layout.kscl": {"fnt_save": "Último autoguardado"},
    "title_layout.kscl": {
        "Press_Any_Button": "Pulsa cualquier botón",
        "Press_Any_Button_Loop": "Pulsa cualquier botón",
    },
    "title_layout_menu_parts.kscl": {
        "fnt_menu_newgame_off": "Nueva partida",
        "fnt_menu_newgame_on": "Nueva partida",
        "fnt_menu_newgame_on_loop": "Nueva partida",
    },
    "title_layout_difficulty_parts.kscl": {
        "fnt_difficulty_easy_off": "Fácil",
        "fnt_difficulty_easy_on": "Fácil",
        "fnt_difficulty_easy_on_loop": "Fácil",
    },
    "cmn_title_mission.kscl": {
        "fnt_title_License": "Información sobre licencias",
        "fnt_title_camera": "Cámara Oscura",
        "fnt_title_costume": "Trajes",
        "fnt_title_ghost": "Lista de fantasmas",
        "fnt_title_item": "Objetos",
        "fnt_title_manual": "Manual",
        "fnt_title_map": "Mapa",
        "fnt_title_menu": "Menú",
        "fnt_title_mission": "Misiones",
        "fnt_title_option": "Opciones",
        "fnt_title_pause": "Pausa",
    },
    "option_menu_parts.kscl": {
        "option_top_gtext_00_off": "Ajustes generales",
        "option_top_gtext_00_on": "Ajustes generales",
    },
    "cmn_tab.kscl": {
        "G_fnt_new": "NUEVO",
        "fnt_tab_item_normal": "Consumibles",
        "fnt_tab_item_select": "Consumibles",
    },
    "camera_menu_parts.kscl": {
        "fnt_film_normal": "Película",
        "fnt_film_select": "Película",
    },
    "inventory_menu_parts.kscl": {
        "fnt_menu_file_glow": "Archivos",
        "fnt_menu_file_normal": "Archivos",
        "fnt_menu_file_select": "Archivos",
    },
    "gallery_top_parts.kscl": {
        "fnt_ghostphoto_normal": "Fotos de espectros",
        "fnt_ghostphoto_select": "Fotos de espectros",
    },
    "photo_layout.kscl": {
        "fnt_onmemory_normal": "Foto temporal",
        "fnt_onmemory_select": "Foto temporal",
        "fnt_sortmenu_dmg_nor": "Daño",
        "fnt_sortmenu_dmg_sel": "Daño",
        "fnt_sortmenu_list_nor": "Lista de fantasmas",
        "fnt_sortmenu_list_sel": "Lista de fantasmas",
        "fnt_sortmenu_mis_nor": "Capítulo",
        "fnt_sortmenu_mis_sel": "Capítulo",
        "fnt_sortmenu_plac_nor": "Lugar",
        "fnt_sortmenu_plac_sel": "Lugar",
        "fnt_sortmenu_pt_nor": "Puntos",
        "fnt_sortmenu_pt_sel": "Puntos",
        "fnt_sortmenu_time_nor": "Fecha",
        "fnt_sortmenu_time_sel": "Fecha",
        "fnt_sorttype": "Ordenar por /",
        "fnt_storage_normal": "Guardar foto",
        "fnt_storage_select": "Guardar foto",
    },
    "ghostlist_layout.kscl": {
        "G_fnt_new": "NUEVO",
        "R_fnt_complete": "COMPLETO",
        "R_fnt_count_photo": "Fotos",
        "R_fnt_total_highscore": "Puntuación máxima",
        "R_fnt_total_photo": "Fotos de fantasmas",
    },
    "mission_select_tab.kscl": {
        "G_fnt_new": "NUEVO",
    },
    "camera_equip_parts.kscl": {
        "fnt_eqp": "Equipado",
    },
    "gameover.kscl": {
        "Gtext_gameover": "Fin de la partida",
        "fnt_save": "Último autoguardado",
    },
    "mission_start_window.kscl": {
        "fnt_mission_start": "Inicio de misión",
        "fnt_mission_start_eff": "Inicio de misión",
    },
    "result.kscl": {
        "res_Gtext_01": "Dificultad",
        "res_Gtext_02": "Tiempo empleado",
        "res_Gtext_03": "Mejor puntuación",
        "res_Gtext_04": "Lista de espíritus",
        "res_Gtext_05": "Muñecas Hozuki",
        "res_Gtext_06": "Puntuación total",
        "res_Gtext_07": "Récord",
        "res_Gtext_08": "Eliminaciones",
        "res_Gtext_16": "Rango",
        "res_Gtext_title": "¡Enhorabuena!",
        "res_Gtext_title_mission_failed": "Misión fallida",
    },
    "tv_rating_layout.kscl": {
        "fnt_basic_combo": "Impactos seguidos",
        "fnt_basic_power": "Potencia básica",
        "fnt_bonus_2kill": "Eliminación explosiva",
        "fnt_bonus_3kill": "Triple eliminación",
        "fnt_bonus_4kill": "Eliminación múltiple",
        "fnt_bonus_blastk": "Eliminación explosiva",
        "fnt_bonus_boost": "Disparo potenciado",
        "fnt_bonus_chance": "Disparo oportuno",
        "fnt_bonus_close": "Disparo cercano",
        "fnt_bonus_core": "Disparo al núcleo",
        "fnt_bonus_double": "Disparo doble",
        "fnt_bonus_dry": "Disparo en seco",
        "fnt_bonus_escape": "Disparo de escape",
        "fnt_bonus_fatal": "Disparo fatal",
        "fnt_bonus_fatalk": "Eliminación fatal",
        "fnt_bonus_fullbody": "Disparo de cuerpo entero",
        "fnt_bonus_grasped": "Disparo al agarrón",
        "fnt_bonus_multi": "Disparo múltiple",
        "fnt_bonus_overk": "Eliminación excesiva",
        "fnt_bonus_rapid": "Disparo rápido",
        "fnt_bonus_specialk": "Eliminación especial",
        "fnt_bonus_tilt": "Disparo inclinado",
        "fnt_bonus_triple": "Disparo triple",
        "fnt_bonus_zero": "Disparo cero",
        "fnt_main_damage": "Daño total",
        "fnt_main_point": "Puntos",
        "fnt_type_doll": "FOTO DE MUÑECA",
        "fnt_type_fatal": "ENCUADRE FATAL",
        "fnt_type_fatal_grance": "MIRADA FATAL",
        "fnt_type_ghost": "FOTO DE FANTASMA",
        "fnt_type_landscape": "PAISAJE",
        "fnt_type_portrait": "RETRATO",
        "fnt_type_psychic": "FOTO PSÍQUICA",
        "fnt_type_psychometry": "PSICOMETRÍA",
        "fnt_type_shutter": "OPORTUNIDAD DE FOTO",
        "fnt_type_spilit": "FOTO DE ESPÍRITU",
        "fnt_type_spilited": "EXPOSICIÓN ESPIRITUAL",
    },
}


def textures(raw: bytes):
    if raw[:4] != b"LCSK":
        raise ValueError("Unexpected KSCL header")
    head = struct.unpack_from("<I", raw, 8)[0] + 0x8C
    count = struct.unpack_from("<I", raw, head + 8)[0]
    table_pointer = struct.unpack_from("<I", raw, head + 16)[0]
    if count < 1 or count > 500 or head >= len(raw):
        raise ValueError("Implausible KSCL texture table")
    table = head + 0x40 + table_pointer
    names = raw[table + count * 20:].split(b"\0", count)[:count]
    if len(names) != count:
        raise ValueError("Missing KSCL texture names")
    result = {}
    for idx in range(count):
        offset = head + struct.unpack_from("<I", raw, table + idx * 20)[0]
        fmt, width, height = struct.unpack_from("<IHH", raw, offset)
        length = struct.unpack_from("<I", raw, offset + 28)[0]
        start = offset + 72
        if not width or not height or start + length > len(raw):
            raise ValueError("Invalid KSCL texture dimensions")
        name = names[idx].decode("utf-8")
        result[name] = (fmt, width, height, start, length)
    return result


def decode(fmt, width, height, pixels):
    if fmt == 0:
        if len(pixels) != width * height * 4:
            raise ValueError("RGBA texture size mismatch")
        return Image.frombytes("RGBA", (width, height), pixels)
    if fmt != 3 or len(pixels) != width * height:
        raise ValueError("Unsupported KSCL texture format")
    dds = bytearray(128)
    dds[:4] = b"DDS "
    struct.pack_into("<III", dds, 4, 124, 0x81007, height)
    struct.pack_into("<II", dds, 16, width, len(pixels))
    struct.pack_into("<I", dds, 76, 32)
    struct.pack_into("<I", dds, 80, 4)
    dds[84:88] = b"DXT5"
    struct.pack_into("<I", dds, 108, 0x1000)
    return Image.open(io.BytesIO(dds + pixels)).convert("RGBA")


def encode(image, fmt, expected):
    if fmt == 0:
        pixels = image.tobytes()
    else:
        fd = io.BytesIO()
        image.save(fd, format="DDS", pixel_format="DXT5")
        pixels = fd.getvalue()[128:]
    if len(pixels) != expected:
        raise ValueError(f"Re-encoded texture size changed: {len(pixels)} != {expected}")
    return pixels


def make_label(source: Image.Image, name: str, spanish: str):
    width, height = source.size
    alpha = source.getchannel("A")
    opaque = alpha.histogram()[255] >= width * height * 0.99
    if opaque:
        # Some animated title sprites are fully opaque black DXT5 images.
        # Their alpha bounding box describes the *background*, not the letters.
        original_box = source.convert("L").point(
            lambda value: 255 if value > 90 else 0).getbbox()
    else:
        # Exclude wide, low-alpha halos from the text geometry.
        original_box = alpha.point(lambda value: 255 if value >= 96 else 0).getbbox()
    if original_box is None:
        raise ValueError(f"No source lettering found: {name}")
    heading = name.startswith("fnt_title_")
    glowing = (name.endswith(("_on", "_on_loop", "_select", "_sel", "_glow", "_eff"))
               or "Press_Any_Button" in name)
    looping = name.endswith(("_loop", "_on_loop"))
    # Preserve the source's dominant lettering tint (blue, gold, red, etc.).
    # Some sprites are intentionally dim while their selected partners glow.
    colors = [(r, g, b) for r, g, b, a in source.getdata()
              if (opaque or a >= 96) and r + g + b > 105]
    if colors:
        colors.sort(key=sum)
        bright = colors[3 * len(colors) // 4:]
        color = tuple(round(sum(c[i] for c in bright) / len(bright)) for i in range(3))
    else:
        color = (180, 201, 209) if heading else (212, 204, 187)
    # Match the source sprite's original vertical size and anchor; fit long labels.
    font_size = 64
    font = ImageFont.truetype(str(NARROW_FONT if name.startswith("fnt_bonus_") else FONT), font_size)
    letter_spacing = 4 if heading else 0
    def draw_text(layer, xy, fill):
        d = ImageDraw.Draw(layer)
        x, y = xy
        if letter_spacing == 0:
            d.text((x, y), spanish, font=font, fill=fill, anchor="ls")
        else:
            # Each glyph shares the same baseline; top anchoring separately
            # placed characters shifts accented letters and mixed case.
            for ch in spanish:
                d.text((round(x), y), ch, font=font, fill=fill, anchor="ls")
                x += d.textlength(ch, font=font) + letter_spacing
    measure = Image.new("RGBA", (max(1500, width * 3), height * 3))
    draw_text(measure, (12, font_size + 12), (*color, 255))
    box = measure.getchannel("A").getbbox()
    if box is None:
        raise ValueError(f"Empty rendered label: {name}")
    glyph = measure.crop(box)
    max_width = max(8, width - (original_box[0] + 8 if heading else 12))
    target_height = max(9, original_box[3] - original_box[1])
    ratio = min(max_width / glyph.width, target_height / glyph.height)
    glyph = glyph.resize((max(1, round(glyph.width * ratio)), max(1, round(glyph.height * ratio))), Image.Resampling.LANCZOS)
    result = Image.new("RGBA", source.size, (0, 0, 0, 255) if opaque else (0, 0, 0, 0))
    # Anchor the translated line to the original text's center for menu controls.
    x = original_box[0] if heading else round((original_box[0] + original_box[2] - glyph.width) / 2)
    y = round((original_box[1] + original_box[3] - glyph.height) / 2)
    x = max(2, min(x, width - glyph.width - 2))
    y = max(2, min(y, height - glyph.height - 2))
    mask = Image.new("L", source.size)
    mask.paste(glyph.getchannel("A"), (x + 1, y + 2))
    shadow_alpha = mask.filter(ImageFilter.GaussianBlur(2.2 if heading else 3))
    shadow = Image.new("RGBA", source.size, (0, 0, 0, 0))
    shadow.putalpha(shadow_alpha.point(lambda p: round(p * 0.50)))
    result.alpha_composite(shadow)
    if glowing:
        # The glow source must be a single-channel alpha mask. Pasting an L
        # image into RGBA makes its rectangular bounds fully opaque, causing
        # visible colored plates behind selected labels after DXT5 encoding.
        glow_mask = Image.new("L", source.size)
        glow_mask.paste(glyph.getchannel("A"), (x, y))
        alpha = glow_mask.filter(ImageFilter.GaussianBlur(5 if looping else 3))
        glow = Image.new("RGBA", source.size, (*color, 0))
        glow.putalpha(alpha.point(lambda p: round(p * (0.86 if looping else 0.62))))
        result.alpha_composite(glow)
    result.alpha_composite(glyph, (x, y))
    if looping:
        result = result.filter(ImageFilter.GaussianBlur(1.7))
    return result


def build(game: Path = GAME):
    report = {}
    backup = game / ".fatal-frame-es-originals"
    marker = backup / "backup_manifest.json"
    recorded = json.loads(marker.read_text(encoding="utf-8")).get("files", {}) if marker.is_file() else {}
    for filename, replacements in LABELS.items():
        rel = Path("binary") / "layout" / "en" / filename
        original = game / rel
        key = rel.as_posix()
        if key in recorded:
            expected = recorded[key]["original_sha256"]
            saved = backup / rel
            if saved.is_file() and hashlib.sha256(saved.read_bytes()).hexdigest() == expected:
                original = saved
            elif not original.is_file() or hashlib.sha256(original.read_bytes()).hexdigest() != expected:
                raise ValueError(f"Original KSCL missing or unverified: {filename}")
        raw = original.read_bytes()
        index = textures(raw)
        unknown = set(replacements) - set(index)
        if unknown:
            raise ValueError(f"Missing expected textures in {filename}: {unknown}")
        rebuilt = bytearray(raw)
        for name, spanish in replacements.items():
            fmt, width, height, start, length = index[name]
            image = decode(fmt, width, height, raw[start:start + length])
            updated = make_label(image, name, spanish)
            rebuilt[start:start + length] = encode(updated, fmt, length)
        if len(rebuilt) != len(raw):
            raise ValueError(f"KSCL size changed: {filename}")
        # Verify the headers, untouched regions and texture indexing survived.
        if textures(rebuilt) != index:
            raise ValueError(f"Repacked KSCL metadata differs: {filename}")
        dest = OUTPUT / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(rebuilt)
        report[filename] = list(replacements)
    path = ROOT / "work" / "layout_es_qa.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Localized {sum(map(len, report.values()))} interface sprites in {len(report)} KSCL assets: {OUTPUT}")


if __name__ == "__main__":
    build()
