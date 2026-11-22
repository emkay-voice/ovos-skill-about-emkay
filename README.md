# <img src='gui/images/emkay.png' width='50' height='50' style='vertical-align:bottom'/> About Emkay

An [OpenVoiceOS](https://openvoiceos.org) skill: who the assistant is and
where it comes from. It answers the questions
[ovos-skill-personal](https://github.com/OpenVoiceOS/ovos-skill-personal)
answers ("who are you", "who made you", "when were you born" …), but as
Emkay, and it tells the story behind the name, with the logo of each part on
the screen while it talks.

It is made for [Emkay](https://github.com/emkay-voice/emkay), OpenVoiceOS in
the browser, and takes the place of ovos-skill-personal there.

## Usage

```
"Who are you?"                 "Hvem er du?"
"Who made you?"                "Hvem har lavet dig?"
"Tell me about yourself"       "Fortæl mig om dig selv"
"Why are you called Emkay?"    "Hvorfor hedder du Emkay?"
"What was Mycroft?"            "Hvad var Mycroft?"
"What is OpenVoiceOS?"         "Hvad er OpenVoiceOS?"
```

"Tell me about yourself" tells the whole story, in five parts:

1. **Mycroft**: in 2015 Mycroft AI, a small company in Kansas, set out to
   build an open source voice assistant.
2. **Mark 1**: its first device, funded on Kickstarter, reached its
   backers in 2016.
3. **Mark 2**: in 2018 Mycroft launched the Mark 2, with a touch screen and
   a face. The two were known as MK1 and MK2.
4. **OpenVoiceOS**: when Mycroft AI closed in 2023, the OpenVoiceOS
   community carried the work on.
5. **Emkay**: OpenVoiceOS in a web browser. M K, after the Mark 1 and the
   Mark 2.

## Why a skill of its own

ovos-skill-personal's answers come from a few settings (creator, year,
place). A whole story with pictures, in every language, is content rather
than settings, and it is Emkay's content, so it belongs in a skill of its
own, as Neon has its own personal skill. The intents and their translations
are ovos-skill-personal's (Apache-2.0, thanks to the OpenVoiceOS community
and its translators), so the same questions work in every language
ovos-skill-personal knows. The story and Emkay's own questions are in
every language Emkay ships (English, Danish, German, Dutch, French,
Spanish, Italian, Portuguese, Catalan, Galician and Basque); a language
without them answers "tell me about yourself" with who it is.

Install one or the other: with both, two skills compete for the same
questions. Emkay blacklists ovos-skill-personal for that reason.

## The pictures

While it talks, the screen shows the logo of the organisation it talks
about, the way a news programme does, and a photo of the device:
Mycroft's logo, the Mark 1, the OpenVoiceOS logo and Emkay's own. Where
each comes from and its license: [CREDITS.md](CREDITS.md). There is no
free picture of the finished Mark 2 yet; that part shows its name until
`gui/images/mark2.png` is there.

## In the control panel

Installed where [ovos-control-panel](https://github.com/OpenVoiceOS/ovos-control-panel)
runs, the skill adds an **About Emkay** page to its menu, right after the
panel's own About. It shows the same story, in the device's language, with
the same pictures, and the name, maker and year from the settings below.

The page is described in `controlpanel.json` (see the panel's
[docs/pages.md](https://github.com/OpenVoiceOS/ovos-control-panel/blob/dev/docs/pages.md)):
the panel draws it, and asks the skill for the story with the message
`ovos.about-emkay.story`. Its texts are in `locale/<lang>/controlpanel.json`.
The skill itself needs no web packages. The panel reads its pages when it
starts, so restart it after installing the skill. Pictures in a page need
ovos-control-panel 0.0.1a81 or newer.

## Settings

| setting | default |
|---|---|
| `assistant_name` | Emkay |
| `creator` | Andreas Lorensen |
| `year_of_birth` | 2026 |

## License

Apache-2.0. The intents and the translations of ovos-skill-personal's
dialogs are from ovos-skill-personal (Apache-2.0).
