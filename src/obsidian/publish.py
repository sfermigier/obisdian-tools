from __future__ import annotations

import glob
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import quote

from antidote import world
from jinja2 import Environment, PackageLoader, select_autoescape
from markdown import markdown
from markupsafe import Markup

from obsidian.config import Config
from obsidian.lib import mkdir_p
from obsidian.markdown_ext.linkify import LinkifyExtension
from obsidian.markdown_ext.tagging import TaggingExtension
from obsidian.markdown_ext.wikilinks import WikiLinkExtension


class KB:
    notes: list[Note]

    def __init__(self):
        self.notes = []

        self.kb_root = world.get[str](Config.KB_ROOT)
        self.public_paths = world.get(Config.PUBLIC)
        self.dist = "dist/notes"

        self.gather_notes()

        self.jinja_env = Environment(
            loader=PackageLoader("obsidian"), autoescape=select_autoescape()
        )

    def gather_notes(self):
        for filename in glob.iglob(self.kb_root + "/**/*.md", recursive=True):
            if "#private" in open(filename).read():
                continue
            note = Note(filename, self)
            if self.is_note_public(note):
                self.notes.append(note)

        for note in self.notes:
            note.parse()

    def is_note_public(self, note: Note) -> bool:
        for path in self.public_paths:
            if note.id.startswith(path):
                return True
        return False

    def find_note(self, id: str) -> Optional[Note]:
        for note in self.notes:
            if note.id.endswith(id):
                return note
        return None

    def publish(self):
        mkdir_p(f"{self.dist}/n")
        mkdir_p(f"{self.dist}/t")

        for note in self.notes:
            self.make_note(note)

        self.make_index()
        self.make_tags()

    def make_note(self, note: Note):
        rendered = self.render_template("note.j2", note=note)

        dest_dir = f"{self.dist}/n/{note.id}"
        mkdir_p(dest_dir)
        with open(f"{dest_dir}/index.html", "w") as output_fd:
            output_fd.write(rendered)

    def make_index(self):
        index = []
        notes = sorted(self.notes, key=lambda n: n.id)
        for note in notes:
            url = url_for(note)
            index.append(f"<li><a href='{url}'>{note.id}</a></li>\n")

        ctx = {"body": "".join(index), "title": "Index"}
        rendered = self.render_template("page.j2", **ctx)
        with open(f"{self.dist}/index.html", "w") as output_fd:
            output_fd.write(rendered)

    def make_tags(self):
        tags = self.all_tags()

        result = []
        for tag in tags:
            url = url_for(Tag(tag))
            result.append(f"<li><a href='{url}'>{tag}</a></li>\n")

            self.make_tag_page(tag)

        ctx = {"body": "".join(result), "title": "Tags"}
        rendered = self.render_template("page.j2", **ctx)
        with open(f"{self.dist}/t/index.html", "w") as output_fd:
            output_fd.write(rendered)

    def all_tags(self):
        tag_set = set()
        for note in self.notes:
            for tag in note.tags:
                tag_set.add(tag)
        tags = sorted(tag_set)
        return tags

    def make_tag_page(self, tag):
        notes = self.get_notes_for_tag(tag)

        result = []
        for note in notes:
            url = url_for(note)
            result.append(f"<li><a href='{url}'>{note.id}</a></li>\n")

        ctx = {"body": "".join(result), "title": f"Tag: {tag}"}
        rendered = self.render_template("page.j2", **ctx)
        mkdir_p(f"{self.dist}/t/{tag}")
        with open(f"{self.dist}/t/{tag}/index.html", "w") as output_fd:
            output_fd.write(rendered)

    def get_notes_for_tag(self, tag) -> list[Note]:
        notes = set()
        for note in self.notes:
            for note_tag in note.tags:
                if note_tag == tag:
                    notes.add(note)
        return sorted(notes, key=lambda n: n.id)

    def render_template(self, template_name, **ctx):
        template = self.jinja_env.get_template(template_name)
        return template.render(url_for=url_for, **ctx)


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


@dataclass(frozen=True, order=True)
class Tag:
    tag: str

    def __str__(self):
        return self.tag


def url_for(obj: Any) -> str:
    prefix = "/notes"

    if isinstance(obj, Note):
        return f"{prefix}/n/{quote(obj.id)}/"

    if isinstance(obj, Tag):
        return f"{prefix}/t/{obj.tag}/"

    if isinstance(obj, str):
        return f"{prefix}/{obj}"

    raise Exception(f"Unknown type: {type(obj)}")


def publish():
    kb = KB()
    kb.publish()
