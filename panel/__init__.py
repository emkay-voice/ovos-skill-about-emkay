"""About Emkay's page in ovos-control-panel.

The control panel finds this page through the ``opm.control_panel.page``
entry point (see pyproject.toml and the panel's docs/pages.md). It shows the
story this skill tells, in the device's language, with the pictures from
gui/images. Nothing here is loaded by the skill itself, so the skill needs
no web packages; the panel brings those.
"""


def routes(r):
    # Imported here, so reading PAGE (the panel's registry, this skill's
    # tests) needs no web framework; only the panel calls this.
    from ovos_skill_about_emkay.panel.api import routes as add
    add(r)


PAGE = {
    "api_version": 1,
    "id": "about-emkay",
    "path": "/about-emkay",
    "title": {"key": "aboutEmkay.title", "label": "About Emkay"},
    # facts about the device: right after the panel's own About (order 90)
    "group": "everyday",
    "order": 95,
    "needs": ["ovos-skill-about-emkay"],
    "html": "page.html",
    "icon": "icon.svg",
    "i18n": "i18n",
    "assets": ("ovos_skill_about_emkay", "gui/images"),
    "routes": routes,
}
