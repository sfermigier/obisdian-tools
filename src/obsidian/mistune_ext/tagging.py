from __future__ import annotations

import typing
from dataclasses import dataclass

from mistune import Markdown

TAG_PATTERN = r"(^|\s)#([\w-]+)"

if typing.TYPE_CHECKING:
    from obsidian.publisher.note import Note


@dataclass
class TagPlugin:
    note: Note

    # define how to parse matched item
    def parse_tag(self, inline, m, state):
        # ``inline`` is ``md.inline``, see below
        # ``m`` is matched regex item
        name = m.group(2)
        self.note.add_tag(name)
        return "tag", name

    # define how to render HTML
    def render_html_tag(self, name):
        return f'<a href="/notes/t/{name}">#{name}</a> '

    def plugin_tag(self, md: Markdown):
        # this is an inline grammar, so we register wiki rule into md.inline
        md.inline.register_rule("tag", TAG_PATTERN, self.parse_tag)

        # add wiki rule into active rules
        md.inline.rules.append("tag")

        # add HTML renderer
        if md.renderer.NAME == "html":
            md.renderer.register("tag", self.render_html_tag)

    __call__ = plugin_tag
