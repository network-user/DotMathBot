"""i18n: get message by key and language."""
from app.locales.ru import TEXTS as RU
from app.locales.en import TEXTS as EN

LOCALES = {"ru": RU, "en": EN}
DEFAULT_LANG = "ru"


def get_text(key: str, lang: str | None = None) -> str:
    """Return localized string for key. Falls back to default language if key missing."""
    lang = lang or DEFAULT_LANG
    if lang not in LOCALES:
        lang = DEFAULT_LANG
    texts = LOCALES[lang]
    if key in texts:
        return texts[key]
    return LOCALES[DEFAULT_LANG].get(key, key)
