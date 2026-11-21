"""The page this skill adds to ovos-control-panel: its description, its
strings in every language the story is told in, and the story it shows."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
# the repository root is the package; load the package and its panel by path
for name, path in (("ovos_skill_about_emkay", ROOT / "__init__.py"),
                   ("ovos_skill_about_emkay.panel", ROOT / "panel" / "__init__.py"),
                   ("ovos_skill_about_emkay.panel.api", ROOT / "panel" / "api.py")):
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, path, submodule_search_locations=[str(path.parent)] if path.name == "__init__.py" else None)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)

panel = sys.modules["ovos_skill_about_emkay.panel"]
api = sys.modules["ovos_skill_about_emkay.panel.api"]
STORY_LANGS = {p.name.split("-")[0].lower() for p in (ROOT / "locale").iterdir()
               if (p / "story_mycroft.dialog").is_file()}


def test_the_page_description_names_files_that_exist():
    page = panel.PAGE
    assert page["api_version"] == 1 and page["id"] == "about-emkay"
    for key in ("html", "icon"):
        assert (ROOT / "panel" / page[key]).is_file(), key
    assert (ROOT / "gui" / "images").is_dir()
    assert callable(page["routes"])


def test_the_page_speaks_every_language_the_story_is_told_in():
    files = {p.stem: json.loads(p.read_text(encoding="utf-8"))
             for p in (ROOT / "panel" / "i18n").glob("*.json")}
    assert STORY_LANGS <= set(files)
    keys = set(files["en"])
    for lang, table in files.items():
        assert set(table) == keys, lang
        assert all(text.strip() for text in table.values()), lang
    html = (ROOT / "panel" / "page.html").read_text(encoding="utf-8")
    for key in keys - {"aboutEmkay.title", "aboutEmkay.error"}:
        assert f'data-i18n="{key}"' in html, key


def test_the_story_is_told_in_the_devices_language_with_its_pictures():
    out = api.story("da-dk")
    assert out["lang"].lower() == "da-dk"
    titles = [p["title"] for p in out["parts"]]
    assert titles == ["Mycroft", "Mark 1", "Mark 2", "OpenVoiceOS", "Emkay"]
    assert "Emkay" in out["parts"][-1]["text"] and "{" not in out["parts"][-1]["text"]
    for part in out["parts"]:
        assert part["image"] is None or (ROOT / "gui" / "images" / part["image"]).is_file()


@pytest.mark.parametrize("lang, folder", [("de-at", "de-de"), ("xx-yy", "en-us"), ("", "en-us")])
def test_a_language_falls_back_to_its_family_then_english(lang, folder):
    assert api.story(lang)["lang"].lower() == folder
