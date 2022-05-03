from __future__ import annotations

import typing
from dataclasses import dataclass, field

import mistune as mistune
from markupsafe import Markup
from mistune.plugins import plugin_url, plugin_task_lists

from obsidian.mistune_ext.tagging import TagPlugin
from obsidian.mistune_ext.wikilinks import WikiPlugin
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
        # extensions = [
        #     TaggingExtension(note=self),
        #     WikiLinkExtension(note=self),
        #     "nl2br",
        #     LinkifyExtension(),
        # ]
        # TODO: extensions
        plugins = [plugin_url, WikiPlugin(self), TagPlugin(self)]
        markdown = mistune.create_markdown(escape=False, plugins=plugins)
        markdown(source)

    @property
    def id(self) -> str:
        return self.rel_path[0:-3]

    @property
    def title(self) -> str:
        # TODO: get the H1 if there is one
        return self.id.split("/")[-1]

    @property
    def html(self) -> Markup:
        with open(self.source_path) as input_fd:
            source = input_fd.read()
        # plugins = [WikiLinkExtension(self), "nl2br", LinkifyExtension()]

        plugins = [plugin_url, plugin_task_lists, TagPlugin(self), WikiPlugin(self)]
        markdown = mistune.create_markdown(escape=False, plugins=plugins)
        rendered = markdown(source)
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

    def add_tag(self, name):
        self.tags.add(Tag(name))

    def add_link(self, link):
        note = self.kb.find_note(link)
        if not note:
            return
        # if not note:
        #     return link, m.start(0), m.end(0)

        self.internal_links.add(note)
