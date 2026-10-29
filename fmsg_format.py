"""Read and rebuild the game's FMSG string tables from original game assets."""

from __future__ import annotations

import collections
from dataclasses import dataclass
import os
from pathlib import Path
import re
import struct


ROOT = Path(__file__).resolve().parent
GAME = Path(os.environ.get("FF_MOL_GAME_DIR", r"E:\Games\FATAL FRAME - PROJECT ZERO Mask of the Lunar Eclipse"))
TAGS = re.compile(r"\^[0-9a-fA-F]{2}(?:~[0-9a-fA-F]{2}~)?|%(?:\d+\$)?[-+ .#0-9]*[a-zA-Z]")


@dataclass(frozen=True)
class Fmsg:
    header: bytes
    blocks: tuple[bytes, ...]
    strings: tuple[str, ...]


def load(path: Path) -> Fmsg:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"FMSG":
        raise ValueError(f"Invalid FMSG: {path}")
    count, start = struct.unpack_from("<I", data, 8)[0], struct.unpack_from("<I", data, 16)[0]
    if start < 32 or start > len(data) or count > 100000:
        raise ValueError(f"Implausible FMSG header: {path}")
    pos = start
    blocks, strings = [], []
    for i in range(count):
        if pos + 8 > len(data):
            raise ValueError(f"Truncated FMSG block {i}: {path}")
        count_units, size = struct.unpack_from("<II", data, pos)
        if count_units < 1 or size < 8 + 2 * count_units or pos + size > len(data):
            raise ValueError(f"Invalid FMSG block {i}: {path}")
        raw = data[pos + 8:pos + 8 + 2 * (count_units - 1)]
        strings.append(raw.decode("utf-16le", errors="strict"))
        blocks.append(data[pos:pos + size])
        pos += size
    if pos != len(data):
        raise ValueError(f"Trailing data in FMSG: {path}")
    return Fmsg(data[:start], tuple(blocks), tuple(strings))


def pack(original: Fmsg, new_strings: list[str] | tuple[str, ...]) -> bytes:
    if len(new_strings) != len(original.strings):
        raise ValueError("FMSG string count changed")
    result = bytearray(original.header)
    for old, new, block in zip(original.strings, new_strings, original.blocks):
        if old == new:
            result.extend(block)
            continue
        if "\r" in new or "\x00" in new:
            raise ValueError("Embedded CR / NUL is unsupported")
        payload = new.encode("utf-16le")
        units = len(payload) // 2 + 1
        size = (8 + len(payload) + 2 + 15) // 16 * 16
        result.extend(struct.pack("<II", units, size))
        result.extend(payload)
        result.extend(b"\x00" * (size - 8 - len(payload)))
    return bytes(result)


def tags(text: str) -> collections.Counter:
    return collections.Counter(TAGS.findall(text))
