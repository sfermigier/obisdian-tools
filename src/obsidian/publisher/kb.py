from __future__ import annotations

import glob
from typing import Optional

from antidote import world
from jinja2 import Environment, PackageLoader, select_autoescape

from obsidian.config import Config
from obsidian.lib import mkdir_p
from obsidian.publisher.note import Note
from obsidian.publisher.tag import Tag
from obsidian.publisher.util import url_for


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
