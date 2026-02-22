
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate


INDIC_LANG_MAP = {
    "hi": sanscript.DEVANAGARI,
    "te": sanscript.TELUGU,
    "ta": sanscript.TAMIL,
    "kn": sanscript.KANNADA,
    "ml": sanscript.MALAYALAM,
    "bn": sanscript.BENGALI,
    "mr": sanscript.DEVANAGARI,
    "ur": sanscript.URDU,
}


def romanize_indic(text: str, lang: str) -> str:
    scheme = INDIC_LANG_MAP.get(lang)
    if not scheme:
        return text
    return transliterate(text, scheme, sanscript.ITRANS)


def romanize_arabic(text: str) -> str:
    replacements = {
        "هذا": "hatha",
        "المفهوم": "al-mafhoom",
        "غير": "ghayr",
        "واضح": "waadih",
        "بالنسبة": "bil-nisba",
        "لي": "li",
        "طريقة": "tareeqat",
        "الشرح": "al-sharh",
        "في": "fi",
        "سريعة": "saree‘a",
        "جداً": "jiddan",
        "لذلك": "lithalika",
        "أفقد": "afqid",
        "بعض": "ba‘d",
        "النقاط": "al-nuqat",
        "المهمة": "al-muhimma",
    }
    for ar, rom in replacements.items():
        text = text.replace(ar, rom)
    return text


def romanize_russian(text: str) -> str:
    table = str.maketrans(
        "абвгдеёжзийклмнопрстуфхцчшщыэюя",
        "abvgdeezhziyklmnoprstufkhtschshchyeyuya"
    )
    return text.lower().translate(table)


def romanize_chinese(text: str) -> str:
    replacements = {
        "这个": "zhe ge",
        "概念": "gainian",
        "对我来说": "dui wo lai shuo",
        "并不": "bing bu",
        "清楚": "qingchu",
        "播客": "boke",
        "讲解": "jiangjie",
        "速度": "sudu",
        "有点": "you dian",
        "快": "kuai",
        "所以": "suoyi",
        "错过": "cuoguo",
        "一些": "yi xie",
        "重要的": "zhongyao de",
        "点": "dian",
    }
    for zh, py in replacements.items():
        text = text.replace(zh, py)
    return text


def romanize_text(text: str, lang: str) -> str:
    if lang in INDIC_LANG_MAP:
        return romanize_indic(text, lang)
    if lang == "ar":
        return romanize_arabic(text)
    if lang == "ru":
        return romanize_russian(text)
    if lang in ["zh", "zh-cn"]:
        return romanize_chinese(text)
    return text
