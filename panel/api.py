"""The story, read from this skill's own dialog files, for the panel's page."""
import json
from pathlib import Path
from typing import Any

PACKAGE = Path(__file__).resolve().parent.parent
SKILL_ID = "ovos-skill-about-emkay.emkay-voice"
#: the defaults the skill itself uses (see the skill's ``facts``)
DEFAULTS = {"name": "Emkay", "creator": "Andreas Lorensen", "year": 2026, "location": "Denmark"}


def _locale(lang: str) -> Path:
    """The skill's locale folder for ``lang``: the language itself, then the
    same language in another country, then English."""
    root = PACKAGE / "locale"
    lang = (lang or "en-us").lower()
    folders = {p.name.lower(): p for p in root.iterdir() if p.is_dir()}
    if lang in folders:
        return folders[lang]
    base = lang.split("-")[0]
    for name, path in sorted(folders.items()):
        if name.split("-")[0] == base and (path / "story_mycroft.dialog").is_file():
            return path
    return folders["en-us"]


def _first_line(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return ""


def _facts() -> dict[str, Any]:
    """The skill's settings, as the skill fills in its dialogs."""
    facts = dict(DEFAULTS)
    try:
        from ovos_config.locations import get_xdg_config_save_path
        path = Path(get_xdg_config_save_path()) / "skills" / SKILL_ID / "settings.json"
        settings = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, ImportError):
        return facts
    for key, setting in (("name", "assistant_name"), ("creator", "creator"), ("year", "year_of_birth")):
        if settings.get(setting):
            facts[key] = settings[setting]
    return facts


def story(lang: str) -> dict[str, Any]:
    """The five parts of the story, with the picture each part shows."""
    from ovos_skill_about_emkay import STORY

    folder = _locale(lang)
    facts = _facts()
    parts = []
    for dialog, image, title in STORY:
        path = folder / f"{dialog}.dialog"
        if not path.is_file():
            path = _locale("en-us") / f"{dialog}.dialog"
        text = _first_line(path)
        for key, value in facts.items():
            text = text.replace("{" + key + "}", str(value))
        has_image = (PACKAGE / "gui" / "images" / image).is_file()
        parts.append({"title": title, "text": text, "image": image if has_image else None})
    return {"lang": folder.name, "parts": parts}


def routes(r) -> None:
    @r.api.get("/about-emkay/story")
    def api_about_emkay_story() -> dict[str, Any]:
        try:
            # the user's layer first, read fresh, so a language just changed shows
            lang = r.config.user_or_merged(["lang"]) or "en-us"
        except Exception:  # noqa: BLE001 - a broken config still gets the story
            lang = "en-us"
        return story(lang)
