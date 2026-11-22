"""About Emkay: who the assistant is and where it comes from.

Emkay's own version of ovos-skill-personal. It answers the same questions,
with the same intents and translations (taken from ovos-skill-personal,
Apache-2.0), but as Emkay, and it tells the story behind the name: Mycroft's
Mark 1 and Mark 2 (MK1, MK2), the OpenVoiceOS community that carried the
work on, and Emkay, OpenVoiceOS in a browser. While it talks, the screen
shows the logo of the part it is talking about.

Emkay blacklists ovos-skill-personal, so the two do not answer the same
question. On any other OpenVoiceOS install it can replace it the same way.

Settings (as in ovos-skill-personal):
    assistant_name   "Emkay"
    creator          "Andreas Lorensen"
    year_of_birth    2026
(Where it was born, Denmark, is in each language's dialog, so it reads
right in every language.)
"""
from os.path import dirname, isfile, join
from pathlib import Path

from ovos_bus_client.message import Message
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill

#: the story, in order: (dialog, picture, title on the screen)
STORY = (
    ("story_mycroft", "mycroft.png", "Mycroft"),
    ("story_mark1", "mark1.png", "Mark 1"),
    ("story_mark2", "mark2.png", "Mark 2"),
    ("story_ovos", "ovos.png", "OpenVoiceOS"),
    ("story_emkay", "emkay.png", "Emkay"),
)


#: the skill's own folder: its dialogs and pictures
HERE = Path(__file__).resolve().parent


def story_folder(lang: str) -> Path:
    """The locale folder the story is read from for ``lang``: the language
    itself, then the same language in another country, then English."""
    root = HERE / "locale"
    lang = (lang or "en-us").lower()
    folders = {p.name.lower(): p for p in root.iterdir() if p.is_dir()}
    if lang in folders:
        return folders[lang]
    base = lang.split("-")[0]
    for name, path in sorted(folders.items()):
        if name.split("-")[0] == base and (path / "story_mycroft.dialog").is_file():
            return path
    return folders["en-us"]


def first_line(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return ""


def story(lang: str, facts: dict) -> list[dict]:
    """The five parts of the story, each with the picture it shows (or
    none), for the control panel's page."""
    folder = story_folder(lang)
    parts = []
    for dialog, image, title in STORY:
        path = folder / f"{dialog}.dialog"
        if not path.is_file():
            path = story_folder("en-us") / f"{dialog}.dialog"
        text = first_line(path)
        for key, value in facts.items():
            text = text.replace("{" + key + "}", str(value))
        part = {"id": dialog, "title": title, "text": text}
        if (HERE / "gui" / "images" / image).is_file():
            part["image"] = image
        parts.append(part)
    return parts


class AboutEmkaySkill(OVOSSkill):

    def initialize(self):
        # the control panel's page (controlpanel.json) asks for the story
        self.add_event("ovos.about-emkay.story", self.handle_page_story, speak_errors=False)

    def handle_page_story(self, message: Message):
        self.bus.emit(message.response({"parts": story(self.lang, self.facts)}))

    @classproperty
    def runtime_requirements(self):
        # all answers are local; nothing needs a network or a screen
        return RuntimeRequirements(internet_before_load=False,
                                   network_before_load=False,
                                   gui_before_load=False,
                                   requires_internet=False,
                                   requires_network=False,
                                   requires_gui=False,
                                   no_internet_fallback=True,
                                   no_network_fallback=True,
                                   no_gui_fallback=True)

    @property
    def facts(self) -> dict:
        """The values the dialogs fill in, from the settings."""
        return {
            "name": self.settings.get("assistant_name") or "Emkay",
            "creator": self.settings.get("creator") or "Andreas Lorensen",
            "year": self.settings.get("year_of_birth") or 2026,
            # only ovos-skill-personal's dialogs in languages Emkay does
            # not ship still ask for it; Emkay's say Denmark in their language
            "location": "Denmark",
        }

    # -- the screen ----------------------------------------------------------

    def picture(self, image: str, title: str):
        """Show `image` from gui/images with `title`; just the title when the
        picture is not there (there is no free picture of the Mark 2 yet,
        see CREDITS.md)."""
        path = join(dirname(__file__), "gui", "images", image)
        if isfile(path):
            self.gui.show_image(path, title=title, fill="PreserveAspectFit",
                                override_idle=30)
        else:
            self.gui.show_text(title, title=title, override_idle=30)

    def say(self, dialog: str, image: str = None, title: str = None, wait=False):
        if image and self.gui.connected:
            self.picture(image, title or self.facts["name"])
        self.speak_dialog(dialog, self.facts, wait=wait)

    # -- the questions ovos-skill-personal answers ---------------------------

    @intent_handler("who_are_you.intent")
    def handle_who_are_you(self, message: Message):
        self.say("who_am_i", "emkay.png")

    @intent_handler("what_are_you.intent")
    def handle_what_are_you(self, message: Message):
        self.say("what_am_i", "emkay.png")

    @intent_handler("who_made_you.intent")
    def handle_who_made_you(self, message: Message):
        self.say("who_made_me", "emkay.png")

    @intent_handler("when_were_you_born.intent")
    def handle_when_were_you_born(self, message: Message):
        self.say("when_was_i_born")

    @intent_handler("where_were_you_born.intent")
    def handle_where_were_you_born(self, message: Message):
        self.say("where_was_i_born")

    # -- Emkay's own ---------------------------------------------------------

    @intent_handler("story.intent")
    def handle_story(self, message: Message):
        """The whole story, one part per picture. Languages without the story
        (only the questions above are translated everywhere) get who_am_i."""
        if not self.dialog_renderer or "story_mycroft" not in self.dialog_renderer.templates:
            return self.handle_who_are_you(message)
        for dialog, image, title in STORY:
            self.say(dialog, image, title, wait=True)
        self.gui.release()

    @intent_handler("what_is_mycroft.intent")
    def handle_what_is_mycroft(self, message: Message):
        self.say("what_is_mycroft", "mycroft.png", "Mycroft")

    @intent_handler("what_is_ovos.intent")
    def handle_what_is_ovos(self, message: Message):
        self.say("what_is_ovos", "ovos.png", "OpenVoiceOS")

    @intent_handler("name_meaning.intent")
    def handle_name_meaning(self, message: Message):
        self.say("name_meaning", "emkay.png")
