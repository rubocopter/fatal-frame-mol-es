"""Source-measured typography for the external English interface textures."""

from statistics import median
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from mixed_labels import repaint


def lettering(source, name, text):
    alpha = source.getchannel("A")
    strength = ImageChops.multiply(source.convert("L"), alpha)
    peak = strength.getextrema()[1]
    if not peak:
        raise ValueError(f"Empty lettering: {name}")
    core = strength.point(lambda p: 255 if p >= peak * .65 else 0)
    box = core.getbbox()
    colors = [p for p, v in zip(source.getdata(), strength.getdata()) if v >= peak * .85]
    ink = tuple(round(median(p[c] for p in colors)) for c in range(3))
    opacity = median(p[3] for p in colors) / 255
    halo_colors = [p for p in source.getdata() if p[3] >= 20 and max(p[:3]) >= 100
                   and max(p[:3]) - min(p[:3]) >= 45]
    halo = tuple(round(median(p[c] for p in halo_colors)) for c in range(3)) if halo_colors else ink
    heading = name.startswith("fnt_title_")
    bold = heading or name.startswith(("res_Gtext_0", "fnt_main_", "fnt_type_"))
    italic = name == "R_fnt_complete"
    font = ImageFont.truetype("C:/Windows/Fonts/" +
                             ("arial.ttf" if name.startswith("film_type") else
                              "timesbd.ttf" if bold else "timesi.ttf" if italic else "times.ttf"), 160)
    tracking = 11 if heading else 5 if name.startswith("mission_start_") else 1.4
    mask = Image.new("L", (8000, 360)); draw = ImageDraw.Draw(mask); x = 12.
    for ch in text:
        draw.text((round(x), 230), ch, font=font, fill=255, anchor="ls")
        x += draw.textlength(ch, font=font) + tracking
    glyph = mask.crop(mask.getbbox())
    height = box[3] - box[1]
    # Keep the capital height stable when Spanish introduces ascenders/descenders.
    capital = Image.new("L", (1000,360))
    ImageDraw.Draw(capital).text((10, 230), "A", font=font, fill=255, anchor="ls")
    cap = capital.getbbox()
    factor = height / glyph.height
    if any(ch in text for ch in "pqgjy") and name.startswith("fnt_menu_"):
        factor = height / (cap[3] - cap[1])
    margin = 8
    right = name.startswith("R_mission_title_")
    left = heading or (not right and box[0] < source.width * .14)
    available = source.width - (max(margin, box[0]) if left else margin) - margin
    glyph = glyph.resize((max(1, min(round(glyph.width * factor), available)),
                          max(1, min(round(glyph.height * factor), source.height-2*margin))), Image.Resampling.LANCZOS)
    x = source.width - margin - glyph.width if right else box[0] if left else round((box[0]+box[2]-glyph.width)/2)
    x = max(margin, min(x, source.width-margin-glyph.width))
    y = max(margin, min(box[1], source.height-margin-glyph.height))
    mask = Image.new("L", source.size);mask.paste(glyph,(x,y))
    opaque = alpha.histogram()[255] >= source.width*source.height*.99
    result = Image.new("RGBA", source.size, (0,0,0,255 if opaque else 0))

    def paint(color, coverage, amount=1.):
        layer = Image.new("RGBA", source.size, (*color,0))
        layer.putalpha(coverage.point(lambda p: round(p*amount)))
        result.alpha_composite(layer)

    shadow = Image.new("L",source.size);shadow.paste(glyph,(x+1,y+2))
    paint((0,0,0),shadow.filter(ImageFilter.GaussianBlur(1.5)),.7)
    loop = name.lower().endswith(("_loop", "_eff"))
    selected = name.lower().endswith(("_on","_select","_sel","_glow"))
    if not heading and (selected or halo_colors or loop):
        paint(halo,mask.filter(ImageFilter.GaussianBlur(4.5)),.95*opacity)
        paint(halo,mask.filter(ImageFilter.GaussianBlur(1.8)),.8*opacity)
    paint(ink,mask.filter(ImageFilter.GaussianBlur(1.25)) if loop or name.endswith("_glow") else mask,opacity)
    return result


def keycap(source, name, text):
    result = source.copy()
    # Keep the key's bevel and illumination, replacing only its interior text.
    box = keycap_region(name, text)
    x0,y0,x1,y1 = box
    selected = name.endswith("_on")
    for y in range(y0,y1):
        row = [source.getpixel((x,y)) for x in range(28,71)]
        clean = ([p for p in row if p[2] > p[0] and p[0] < 220] if selected
                 else [p for p in row if p[0] >= 100])
        if not clean:
            clean = row
        color = tuple(round(median(p[c] for p in clean)) for c in range(4))
        for x in range(x0,x1):
            result.putpixel((x,y),color)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 64)
    mask=Image.new("L",(500,150));ImageDraw.Draw(mask).text((5,5),text,font=font,fill=255)
    mask=mask.crop(mask.getbbox())
    height=12 if text=="Núm" else min(21,round(mask.height*(x1-x0-2)/mask.width))
    width=min(x1-x0-2,round(mask.width*height/mask.height))
    mask=mask.resize((width,height),Image.Resampling.LANCZOS)
    ink=Image.new("RGBA",mask.size,(255,255,255) if selected else (0,0,0));ink.putalpha(mask)
    result.alpha_composite(ink,(x0+(x1-x0-width)//2,y0+(y1-y0-height)//2))
    return result, box


def keycap_region(name, text):
    if text == "Núm":
        return (27,28,71,48)
    if "SHIFT_" in name:
        return (27,44,71,69)
    return (27,28,71,69)


def render(source, name, text):
    if isinstance(text, dict):
        from tutorial_labels import repaint_tutorial
        return repaint_tutorial(source, name, text)
    if isinstance(text, list):
        # Chapter card: keep the separator and character's name untouched.
        result=source.copy()
        for box, line in zip([(0,0,780,80),(0,80,780,152)],text):
            result.paste(lettering(source.crop(box),name,line),box[:2])
        return result, (0,0,780,152)
    if name.startswith("btn_PCKey_"):
        return keycap(source,name,text)
    return repaint(source,name,text,lettering)
