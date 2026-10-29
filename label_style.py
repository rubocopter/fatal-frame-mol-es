"""Typography and separate ink/halo layers for the Spanish KSCL interface.

An approximation of the source art, using Windows fonts; no proprietary glyphs
are bundled. The approved menu proof is kept byte-identical by reusing its
renderer. Other families retain their source tint, alignment and opacity.
"""

from pathlib import Path
from statistics import median

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


APPROVED_NAMES = {
    "Press_Any_Button", "Press_Any_Button_Loop",
    "fnt_menu_newgame_off", "fnt_menu_newgame_on", "fnt_menu_newgame_on_loop",
    "option_top_gtext_00_off", "option_top_gtext_00_on", "fnt_title_option",
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



def make_label(source, name, text):
    # Preserve the approved eight-sprite proof without duplicating its recipe.
    if name in APPROVED_NAMES:
        return trial_label(source, name, text)

    heading = name.startswith("fnt_title_")
    italic = name in {"G_fnt_new", "R_fnt_complete", "fnt_film_normal",
                      "fnt_film_select", "fnt_tab_item_normal", "fnt_tab_item_select"}
    handwritten = name == "R_fnt_save_ingame"
    loop = name.endswith(("_loop", "_eff"))
    selected = name.endswith(("_on", "_select", "_sel", "_glow"))
    rating = name.startswith(("fnt_bonus_", "fnt_type_", "fnt_main_", "fnt_basic_"))
    alpha = source.getchannel("A")
    opaque = alpha.histogram()[255] >= source.width * source.height * .99
    strength = ImageChops.multiply(source.convert("L"), alpha)
    peak = strength.getextrema()[1]
    if peak == 0:
        raise ValueError(f"No source lettering: {name}")
    box = strength.point(lambda p: 255 if p >= peak * .65 else 0).getbbox()
    colors = [px for px, value in zip(source.getdata(), strength.getdata())
              if value >= peak * .85]
    ink = tuple(round(median(px[c] for px in colors)) for c in range(3))
    opacity = median(px[3] for px in colors) / 255
    # Colored outer light must be independent of the pale letter interiors.
    halo_pixels = [px for px in source.getdata() if px[3] >= 24 and
                   max(px[:3]) >= 100 and max(px[:3]) - min(px[:3]) >= 45]
    halo = tuple(round(median(px[c] for px in halo_pixels)) for c in range(3)) if halo_pixels else ink
    bold = heading or name in {"Gtext_synopsis", "Gtext_gameover", "res_Gtext_16", "fnt_type_fatal"}
    font_name = ("segoepr.ttf" if handwritten else "timesbd.ttf" if bold else
                 "timesi.ttf" if italic else "times.ttf")
    font = ImageFont.truetype(str(Path("C:/Windows/Fonts") / font_name), 128)
    spacing = 11 if heading else -1.5 if rating else 1.4
    large = Image.new("L", (6500, 350))
    draw = ImageDraw.Draw(large)
    x = 14.
    for ch in text:
        draw.text((round(x), 220), ch, font=font, fill=255, anchor="ls")
        x += draw.textlength(ch, font=font) + spacing
    glyph = large.crop(large.getbbox())
    height = box[3] - box[1]
    reference_h = glyph.height
    references = {"G_fnt_new": "NEW", "R_fnt_complete": "COMPLETE",
                  "Gtext_synopsis": "Summary", "fnt_eqp": "Equipped",
                  "fnt_save": "Latest Autosave", "Gtext_gameover": "Game Over",
                  "res_Gtext_16": "Rank"}
    if name in references:
        reference = Image.new("L", large.size)
        ImageDraw.Draw(reference).text((14, 220), references[name], font=font,
                                       fill=255, anchor="ls")
        b = reference.getbbox()
        reference_h = b[3] - b[1]
    scale = height / reference_h
    margin = 8
    left = heading or box[0] < source.width * .16
    max_width = source.width - (max(margin, box[0]) if left else margin) - margin
    target_w = max(1, min(round(glyph.width * scale), max_width))
    target_h = max(1, min(round(glyph.height * scale), source.height - margin * 2))
    glyph = glyph.resize((target_w, target_h), Image.Resampling.LANCZOS)
    x = box[0] if left else round((box[0] + box[2] - glyph.width) / 2)
    y = box[1]
    x = max(margin, min(x, source.width - glyph.width - margin))
    y = max(margin, min(y, source.height - glyph.height - margin))
    mask = Image.new("L", source.size)
    mask.paste(glyph, (x, y))
    result = Image.new("RGBA", source.size, (0, 0, 0, 255 if opaque else 0))

    def layer(color, coverage, amount=1.):
        paint = Image.new("RGBA", source.size, (*color, 0))
        paint.putalpha(coverage.point(lambda p: round(p * amount)))
        result.alpha_composite(paint)

    shadow = Image.new("L", source.size)
    shadow.paste(glyph, (x + 1, y + 3))
    layer((0, 0, 0), shadow.filter(ImageFilter.GaussianBlur(2)), .8)
    if heading:
        layer((181, 201, 207), mask, opacity)
    elif loop:
        layer(halo, mask.filter(ImageFilter.GaussianBlur(4.5)), .72)
        layer(ink, mask.filter(ImageFilter.GaussianBlur(1.5)), opacity)
    else:
        glow = .65 if selected or rating or handwritten else .35 if halo_pixels else 0
        if glow:
            layer(halo, mask.filter(ImageFilter.GaussianBlur(6 if selected else 4)), glow * opacity)
            layer(halo, mask.filter(ImageFilter.GaussianBlur(1.5)), glow * .6 * opacity)
        layer(ink, mask, opacity)
    return result
