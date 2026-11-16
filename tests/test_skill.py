"""The skill answers as Emkay, and tells the story in order, in English and Danish."""
import json
import re
import sys
from pathlib import Path

import pytest
from ovos_bus_client.message import Message
from ovos_utils.fakebus import FakeBus

ROOT = Path(__file__).parent.parent
# the repository root is the package (as in ovos-skill-personal); load it by path
import importlib.util
_spec = importlib.util.spec_from_file_location("ovos_skill_about_emkay", ROOT / "__init__.py",
                                               submodule_search_locations=[str(ROOT)])
pkg = importlib.util.module_from_spec(_spec)
sys.modules["ovos_skill_about_emkay"] = pkg
_spec.loader.exec_module(pkg)

SKILL_ID = "ovos-skill-about-emkay.emkay-voice"


@pytest.fixture
def skill():
    bus = FakeBus()
    spoken = []
    bus.on("speak", lambda m: spoken.append(Message.deserialize(m) if isinstance(m, str) else m))
    s = pkg.AboutEmkaySkill(bus=bus, skill_id=SKILL_ID)
    s.spoken = spoken
    # speak(wait=True) waits for the audio service; there is none here
    s.speak_dialog = (lambda orig: (lambda key, data=None, wait=False, **kw: orig(key, data, wait=False, **kw)))(s.speak_dialog)
    yield s
    s.shutdown()


def said(skill):
    return [m.data["utterance"] for m in skill.spoken]


def test_who_made_you_is_emkays_maker(skill):
    skill.handle_who_made_you(Message("x"))
    assert "Andreas Lorensen" in said(skill)[-1]


def test_name_meaning(skill):
    skill.handle_name_meaning(Message("x"))
    assert "M K" in said(skill)[-1]


def test_story_in_order(skill):
    skill.handle_story(Message("x"))
    story = said(skill)
    assert len(story) == 5
    assert "Mycroft" in story[0] and "2015" in story[0]
    assert "Mark 1" in story[1]
    assert "Mark 2" in story[2]
    assert "OpenVoiceOS" in story[3]
    assert "Emkay" in story[4] and "M K" in story[4]


LANGS = ["en-US", "da-DK", "de-DE", "nl-NL", "fr-FR", "es-ES", "it-IT",
         "pt-BR", "pt-PT", "ca-ES", "gl-ES", "eu-ES"]


@pytest.mark.parametrize("lang", LANGS)
def test_every_intent_has_its_answers(lang):
    """Each intent the code registers exists, and each dialog it speaks too."""
    loc = ROOT / "locale" / lang
    code = (ROOT / "__init__.py").read_text()
    for intent in loc.glob("*.intent"):
        assert f'"{intent.name}"' in code, intent.name
    for intent in ("story", "what_is_mycroft", "what_is_ovos", "name_meaning"):
        assert (loc / f"{intent}.intent").read_text(encoding="utf-8").strip(), intent
    for dialog in ("who_am_i", "what_am_i", "who_made_me", "when_was_i_born", "where_was_i_born",
                   "what_is_mycroft", "what_is_ovos", "name_meaning",
                   *(d for d, _, _ in pkg.STORY)):
        assert (loc / f"{dialog}.dialog").read_text(encoding="utf-8").strip(), dialog


def test_skill_json_names_this_skill():
    for f in (ROOT / "locale").glob("*/skill.json"):
        assert json.loads(f.read_text(encoding="utf-8"))["skill_id"] == SKILL_ID, f


@pytest.mark.parametrize("lang", LANGS)
def test_dialogs_only_use_known_fields(lang):
    """{name}, {creator} and {year} are all a dialog may ask for."""
    for f in (ROOT / "locale" / lang).glob("*.dialog"):
        for field in re.findall(r"{(\w+)}", f.read_text(encoding="utf-8")):
            assert field in ("name", "creator", "year"), (f.name, field)
