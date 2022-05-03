from __future__ import annotations

import typing
from dataclasses import dataclass

# define regex for Wiki links
# fmt: off
from devtools import debug

WIKI_PATTERN = (
    r'\[\['  # [[
    r'([\s\S]+?)'  # Some page
    r'\]\](?!\])'  # ]]
)
# fmt: on

if typing.TYPE_CHECKING:
    from obsidian.publisher.note import Note


@dataclass
class WikiPlugin:
    note: Note

    # define how to parse matched item
    def parse_wiki(self, inline, m, state):
        # ``inline`` is ``md.inline``, see below
        # ``m`` is matched regex item
        title = m.group(1)
        self.note.add_link(title)
        return "wiki", title

    # define how to render HTML
    def render_html_wiki(self, title):
        from obsidian.publisher import url_for

        note = self.note.kb.find_note(title)
        if not note:
            print(f"Missing note: {title}")
            return title

        link = url_for(note)
        return f'<a href="{link}">{title}</a>'

    def plugin_wiki(self, md):
        # this is an inline grammar, so we register wiki rule into md.inline
        md.inline.register_rule("wiki", WIKI_PATTERN, self.parse_wiki)

        # add wiki rule into active rules
        md.inline.rules.append("wiki")

        # add HTML renderer
        if md.renderer.NAME == "html":
            md.renderer.register("wiki", self.render_html_wiki)

    __call__ = plugin_wiki
