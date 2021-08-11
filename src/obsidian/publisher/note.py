from __future__ import annotations

import typing
from dataclasses import dataclass, field

from markdown import markdown
from markupsafe import Markup

from obsidian.markdown_ext.linkify import LinkifyExtension
from obsidian.markdown_ext.tagging import TaggingExtension
from obsidian.markdown_ext.wikilinks import WikiLinkExtension
from obsidian.publisher.tag import Tag

if typing.TYPE_CHECKING:
    from obsidian.publisher import KB


@dataclass
class Note:
    source_path: str
    kb: KB

    internal_links: set[Note] = field(init=False, default_factory=set)
    tags: set[Tag] = field(init=False, default_factory=set)

    def __hash__(self):
        return hash(self.id)

    def parse(self):
        with open(self.source_path) as input_fd:
            source = input_fd.read()
        extensions = [
            TaggingExtension(note=self),
            WikiLinkExtension(note=self),
            "nl2br",
            LinkifyExtension(),
        ]
        markdown(source, extensions=extensions)

    @property
    def id(self) -> str:
        return self.rel_path[0:-3]

    @property
    def title(self) -> str:
        # TODO: get the H1 if the is one
        return self.id.split("/")[-1]

    @property
    def html(self) -> Markup:
        with open(self.source_path) as input_fd:
            source = input_fd.read()
        extensions = [WikiLinkExtension(self), "nl2br", LinkifyExtension()]
        rendered = markdown(source, extensions=extensions)
        return Markup(rendered)

    @property
    def rel_path(self) -> str:
        return self.source_path[len(self.kb.kb_root) :]

    @property
    def backlinks(self) -> list[Note]:
        result = []
        for note in self.kb.notes:
            if self in note.internal_links:
                result.append(note)

        return result
