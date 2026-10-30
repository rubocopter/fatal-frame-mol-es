"""Fixed-capacity UTF-16 layout literals; never change offsets or string lengths."""

import struct

INLINE_LABELS = {
    "change_costume.kscl": {"Costume": "Trajes", "Accessary": "Accesor."},
    "cmn_title_mission.kscl": {"Score": "Ptos."},
    "ghostlist_list_parts.kscl": {"No Photo": "Sin foto"},
    "inventory_layout.kscl": {"COMPLETE!": "COMPLETO"},
    "mission_select.kscl": {"SCORE": "PUNT.", "Rank": "Nota"},
    "photo_details.kscl": {"Subject": "Motivo", "Chapter": "Capít.", "Date": "Día",
        "Location": "Lugar", "Points": "Puntos", "Damage": "Daño", "Film": "Film",
        "Lens": "Obj.", "Photographer": "Fotógrafo", "Patient in front of door": "Paciente ante puerta",
        "Phase II: Resonance": "Fase II: Resonancia"},
    "result.kscl": {"NIGHTMARE": "PESADILLA", "New": "Nvo"},
    "savedata_select_list.kscl": {"NO DATA": "VACÍO", "AUTOSAVE": "AUTOG."},
}


def replacements(raw, filename):
    """Return exact writable ranges, checking the source's length-prefixed field."""
    head = struct.unpack_from("<I", raw, 8)[0] + 0x8C
    result=[]
    for english, spanish in INLINE_LABELS.get(filename, {}).items():
        source=(english+"\0").encode("utf-16le")
        text=spanish.encode("utf-16le")
        capacity=len(source)-2
        if len(text)>capacity:
            raise ValueError(f"Inline label exceeds original capacity: {filename}: {english}")
        pattern=struct.pack("<I",len(source))+source
        start=0;count=0
        while (position:=raw.find(pattern,start,head)) >= 0:
            pos=position+4
            result.append((pos,pos+len(source),text+b' \0'*((capacity-len(text))//2)+b'\0\0'))
            count+=1;start=pos+len(source)
        if not count:
            raise ValueError(f"Original inline label missing: {filename}: {english}")
    return result
