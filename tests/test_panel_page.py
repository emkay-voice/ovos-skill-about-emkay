"""The page this skill adds to ovos-control-panel: its controlpanel.json,
its strings in every language they are written in, and the story it shows."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
# the repository root is the package; load it by path
if "ovos_skill_about_emkay" not in sys.modules:
    spec = importlib.util.spec_from_file_location("ovos_skill_about_emkay", ROOT / "__init__.py",
                                                  submodule_search_locations=[str(ROOT)])
    module = importlib.util.module_from_spec(spec)
    sys.modules["ovos_skill_about_emkay"] = module
    spec.loader.exec_module(module)
skill = sys.modules["ovos_skill_about_emkay"]
PAGE = json.loads((ROOT / "controlpanel.json").read_text(encoding="utf-8"))
FACTS = {"name": "Emkay", "creator": "Andreas Lorensen", "year": 2026, "location": "Denmark"}


def test_the_page_names_files_that_exist_and_its_own_messages():
    assert PAGE["controlpanel"] == 1 and PAGE["id"] == "about-emkay"
    assert (ROOT / PAGE["icon"]).is_file() and (ROOT / PAGE["pictures"]).is_dir()
    for block in PAGE["blocks"]:
        if "query" in block:
            assert block["query"].startswith(PAGE["bus"])


def test_the_page_speaks_every_language_it_is_written_in():
    files = {p.parent.name: json.loads(p.read_text(encoding="utf-8"))
             for p in (ROOT / "locale").glob("*/controlpanel.json")}
    keys = set(files["en-US"])
    used = {b["text"] for b in PAGE["blocks"] if b["type"] == "text"} | {PAGE["title"]}
    assert used == keys
    for lang, table in files.items():
        assert set(table) == keys, lang
        assert all(text.strip() for text in table.values()), lang


def test_the_story_is_told_with_its_pictures():
    parts = skill.story("da-dk", FACTS)
    assert [p["title"] for p in parts] == ["Mycroft", "Mark 1", "Mark 2", "OpenVoiceOS", "Emkay"]
    assert "Emkay" in parts[-1]["text"] and "{" not in parts[-1]["text"]
    for part in parts:
        assert "image" not in part or (ROOT / "gui" / "images" / part["image"]).is_file()
    # there is no free picture of the Mark 2 yet (CREDITS.md)
    assert "image" not in parts[2]


@pytest.mark.parametrize("lang, folder", [("da-dk", "da-dk"), ("de-at", "de-de"), ("xx-yy", "en-us"), ("", "en-us")])
def test_a_language_falls_back_to_its_family_then_english(lang, folder):
    assert skill.story_folder(lang).name.lower() == folder


def test_the_skill_answers_the_pages_question():
    from types import SimpleNamespace
    from ovos_bus_client.message import Message
    sent = []
    me = SimpleNamespace(bus=SimpleNamespace(emit=sent.append), lang="en-us", facts=FACTS)
    skill.AboutEmkaySkill.handle_page_story(me, Message("ovos.about-emkay.story"))
    assert sent and sent[0].msg_type == "ovos.about-emkay.story.response"
    assert [p["id"] for p in sent[0].data["parts"]][0] == "story_mycroft"
