"""Castilian translations for the game's original text5 costume gallery."""

ACCESSORIES = {}
for start, character, number in ((516, "Ruka", 7), (523, "Choshiro", 5),
                                 (528, "Misaki", 7), (535, "Madoka", 3)):
    for offset in range(number):
        ACCESSORIES[start + offset] = f"{character} (traje {offset + 1})"

for start, character, count in ((538, "Ruka", 3), (543, "Misaki", 3), (548, "Choshiro", 3)):
    ACCESSORIES[start] = f"{character} (sin accesorios)"
    for style in range(1, count + 1):
        ACCESSORIES[start + style] = f"{character} (gafas {style})"
    if character != "Choshiro":
        ACCESSORIES[start + 4] = f"{character} (adorno para el pelo)"

ACCESSORIES.update({
    552: "Lente Parálisis",
    553: "Lente Explosión",
    554: "Lente Impacto",
    555: "Lente Ampliación",
    556: "Lente Lunar",
    557: "Percepción",
    558: "Infinito",
    559: "Óptimo",
    560: "Modo misión",
    561: "Modo difícil",
    562: "Modo pesadilla",
    563: "Ruka con su ropa habitual.",
    564: "Ruka con un yukata de rayas.",
    565: "Ruka con uniforme escolar.",
    566: "Ruka con un vestido de palabra de honor.",
    567: "Ruka con un yukata de flores.",
    568: "Ruka disfrazada de Samus sin armadura.",
    569: "Choshiro con su ropa habitual.",
    570: "Choshiro con ropa informal marrón.",
    571: "Choshiro vestido de policía.",
    572: "Choshiro con ropa informal azul marino.",
    573: "Misaki con su ropa habitual.",
    574: "Misaki con un yukata de flores y peces de colores.",
    575: "Misaki con uniforme escolar.",
    576: "Misaki con ropa de estilo punk.",
    577: "Misaki con un yukata de mariposas.",
    578: "Misaki disfrazada de Luigi.",
    579: "Madoka con su ropa habitual.",
    580: "Madoka con un vestido.",
    581: "Ruka sin accesorios.",
    582: "Gafas para Ruka (modelo 1).",
    583: "Gafas para Ruka (modelo 2).",
    584: "Gafas para Ruka (modelo 3).",
    585: "Adorno para el pelo de Ruka.",
    586: "Misaki sin accesorios.",
    587: "Gafas para Misaki (modelo 1).",
    588: "Gafas para Misaki (modelo 2).",
    589: "Gafas para Misaki (modelo 3).",
})

ACCESSORIES = {("text5.fmsg", idx): es for idx, es in ACCESSORIES.items()}
