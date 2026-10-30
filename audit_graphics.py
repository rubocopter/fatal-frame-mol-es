"""Generate contact sheets from original and recompressed localized textures."""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import layout_translation as layout


def original(game, rel):
    marker = game / ".fatal-frame-es-originals/backup_manifest.json"
    records = json.loads(marker.read_text(encoding="utf-8"))["files"] if marker.is_file() else {}
    if rel.as_posix() in records:
        return game / ".fatal-frame-es-originals" / rel
    return game / rel


def build():
    out=layout.ROOT/"work/graphics_review";out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for filename,labels in layout.LABELS.items():
        raw=original(layout.GAME,Path("binary/layout/en")/filename).read_bytes()
        updated=(layout.OUTPUT/filename).read_bytes(); index=layout.textures(raw)
        for name,spanish in labels.items():
            fmt,w,h,s,n=index[name]
            images=[layout.decode(fmt,w,h,b[s:s+n]) for b in (raw,updated)]
            rows.append((filename,name,spanish,images))
    font=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf",14)
    for offset in range(0,len(rows),20):
        group=rows[offset:offset+20]
        sheet=Image.new("RGB",(1500,90+len(group)*126),(27,30,36));draw=ImageDraw.Draw(sheet)
        draw.text((20,10),"Original inglés / español recompreso",font=font,fill="white")
        for i,(filename,name,spanish,images) in enumerate(group):
            y=50+i*126
            draw.text((10,y),filename+" / "+name,font=font,fill=(190,190,150))
            for col,im in enumerate(images):
                im.thumbnail((720,96));sheet.paste(im,(col*750+12,y+25),im)
        sheet.save(out/f"comparison_{offset//20:02}.png")
    (out/"inventory.json").write_text(json.dumps(layout.LABELS,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Reviewed build: {len(rows)} sprites in {len(layout.LABELS)} files; sheets in {out}")


if __name__=="__main__":
    build()
