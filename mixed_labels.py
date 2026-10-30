"""Localize lettering embedded in icons without redrawing their artwork."""

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def region(name, size):
    if name == "icon_lock":
        return (0, 80, 120, 120)
    if name.startswith("cmn_button_") and "_hold_" in name:
        return (8, 68, 88, 96)
    return (0, 0, *size)


def fitted_mask(text, size, font_name, height):
    font = ImageFont.truetype("C:/Windows/Fonts/" + font_name, 100)
    mask = Image.new("L", (1200, 160))
    ImageDraw.Draw(mask).text((5, 5), text, font=font, fill=255)
    mask = mask.crop(mask.getbbox())
    width = min(size[0], round(mask.width * height / mask.height))
    return mask.resize((width, height), Image.Resampling.LANCZOS)


def repaint(source, name, text, make_label):
    box = region(name, source.size)
    if name == "icon_lock":
        result = source.copy()
        result.paste(make_label(source.crop(box), name, text), box[:2])
        return result, box
    if name.startswith("HOLD_") or "_hold_" in name:
        result = source.copy()
        result.paste((0, 0, 0, 0), box)
        selected = name.lower().endswith("_on")
        badge = (22, 70, 76, 88) if name.startswith("cmn_button_") else (13, 21, 66, 39)
        layer = Image.new("RGBA", source.size)
        ImageDraw.Draw(layer).rounded_rectangle(badge, radius=4,
            fill=(255, 255, 255, 255) if selected else (173, 166, 156, 255))
        if selected:
            glow = layer.filter(ImageFilter.GaussianBlur(3))
            result.alpha_composite(glow)
        else:
            shadow = Image.new("RGBA", source.size)
            ImageDraw.Draw(shadow).rounded_rectangle(
                (badge[0]-2, badge[1]-1, badge[2]+2, badge[3]+2), radius=5, fill=(0,0,0,220))
            result.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(1)))
        result.alpha_composite(layer)
        mask = fitted_mask(text, (badge[2]-badge[0]-4, badge[3]-badge[1]-4), "arialbd.ttf", 12)
        ink = Image.new("RGBA", mask.size, (113, 146, 180) if selected else (0,0,0))
        ink.putalpha(mask)
        result.alpha_composite(ink, (round((badge[0]+badge[2]-mask.width)/2), badge[1]+2))
        # Composite effects are restricted to the lettering region as well.
        preserved = source.copy()
        preserved.paste(result.crop(box), box[:2])
        return preserved, box
    if name.startswith("fusen_"):
        result = source.copy()
        # The unprinted half of each paper tab supplies its original grain.
        left = name == "fusen_left"
        erase = (10, 16, 57, 52) if left else (67, 18, 112, 51)
        clean = (63, 16, 110, 52) if left else (17, 18, 62, 51)
        result.paste(source.crop(clean), erase[:2])
        mask = fitted_mask(text, (source.width-22, 30), "segoepr.ttf", 27)
        ink = Image.new("RGBA", mask.size, (135, 100, 22))
        ink.putalpha(mask.point(lambda p: round(p * .85)))
        result.alpha_composite(ink, ((source.width-mask.width)//2, 20))
        return result, box
    return make_label(source, name, text), box
