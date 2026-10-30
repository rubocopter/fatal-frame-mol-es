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

from PIL import Image

from label_style import make_label
from mixed_labels import repaint


ROOT = Path(__file__).resolve().parent
GAME = Path(os.environ.get("FF_MOL_GAME_DIR", r"E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse"))
OUTPUT = ROOT / "work" / "layout_es" / "binary" / "layout" / "en"

# These are the labels actually drawn into the English interface textures.
# Preserve branded logos, Japanese calligraphy, and other non-language art.
LABELS = {
    "option_menu.kscl": {
        "photograph_OFF": "Modo foto",
        "photograph_ON": "Modo foto",
        "search_OFF": "Modo búsqueda",
        "search_ON": "Modo búsqueda",
    },
    "pocketbook_layout_list_parts.kscl": {
        "fusen_left": "NUEVO",
        "fusen_right": "NUEVO",
    },
    "system_layout.kscl": {
        "HOLD_OFF": "MANT.", "HOLD_ON": "MANT.",
        "cmn_button_l_hold_off": "MANT.", "cmn_button_l_hold_on": "MANT.",
        "cmn_button_zl_hold_off": "MANT.", "cmn_button_zl_hold_on": "MANT.",
        "cmn_button_zr_hold_off": "MANT.", "cmn_button_zr_hold_on": "MANT.",
    },
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
        "icon_lock": "Bloquear",
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

from external_labels import EXTERNAL_LABELS
LABELS.update(EXTERNAL_LABELS)
from inline_labels import INLINE_LABELS
for _filename in INLINE_LABELS:
    LABELS.setdefault(_filename, {})


def textures(raw: bytes):
    if raw[:4] == b"LCSK":
        head = struct.unpack_from("<I", raw, 8)[0] + 0x8C
    elif raw[:4] == b"TLSK":
        head = 0
    else:
        raise ValueError("Unexpected KSCL/KSLT header")
    if raw[head:head+4] != b"TLSK":
        raise ValueError("Missing KSLT texture table")
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
    if fmt not in (1, 3) or len(pixels) != width * height // (2 if fmt == 1 else 1):
        raise ValueError("Unsupported KSCL texture format")
    dds = bytearray(128)
    dds[:4] = b"DDS "
    struct.pack_into("<III", dds, 4, 124, 0x81007, height)
    struct.pack_into("<II", dds, 16, width, len(pixels))
    struct.pack_into("<I", dds, 76, 32)
    struct.pack_into("<I", dds, 80, 4)
    dds[84:88] = b"DXT1" if fmt == 1 else b"DXT5"
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
        if filename in INLINE_LABELS:
            from inline_labels import replacements as inline_replacements
            for start, end, text in inline_replacements(raw, filename):
                rebuilt[start:end] = text
        for name, spanish in replacements.items():
            fmt, width, height, start, length = index[name]
            image = decode(fmt, width, height, raw[start:start + length])
            if filename.endswith(".kslt"):
                from external_style import render
                updated, box = render(image, name, spanish)
            else:
                updated, box = repaint(image, name, spanish, make_label)
            pixels = encode(updated, fmt, length)
            if fmt == 3:
                # BC3 encodes 4x4 blocks. Keep every block outside the text
                # region byte-identical, including the padlock/button art.
                boxes = [box] if isinstance(box, tuple) else box
                for x0, y0, x1, y1 in boxes:
                    for row in range(y0 // 4, (y1 + 3) // 4):
                        a = (row * (width // 4) + x0 // 4) * 16
                        b = (row * (width // 4) + (x1 + 3) // 4) * 16
                        rebuilt[start+a:start+b] = pixels[a:b]
            else:
                rebuilt[start:start + length] = pixels
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
    print(f"Localized {sum(map(len, report.values()))} interface sprites in {len(report)} KSCL/KSLT assets: {OUTPUT}")


if __name__ == "__main__":
    build()
