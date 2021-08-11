from __future__ import annotations

import glob
from dataclasses import dataclass
from pathlib import Path

from antidote import world
from jinja2 import Environment, PackageLoader, select_autoescape
from markdown import markdown

from obsidian.config import Config
from obsidian.lib import mkdir_p


class Publisher:
    notes: list[Note]

    def __init__(self):
        self.notes = []
        self.kb_root = world.get[str](Config.KB_ROOT)

        for filename in glob.iglob(self.kb_root + "/**/*.md", recursive=True):
            if "#public" in open(filename).read():
                self.notes.append(Note(filename, self))

        self.jinja_env = Environment(
            loader=PackageLoader("obsidian"), autoescape=select_autoescape()
        )

    def publish(self):
        for note in self.notes:
            note.publish()

        self.make_index()

    def make_index(self):
        index = []
        for note in self.notes:
            index.append(f"<li><a href='{note.id}'>{note.title}</a></li>\n")

        ctx = {"body": "".join(index)}
        rendered = self.render_template("index.j2", **ctx)
        with open("dist/index.html", "w") as output_fd:
            output_fd.write(rendered)

    def render_template(self, template_name, **ctx):
        template = self.jinja_env.get_template(template_name)
        return template.render(**ctx)


@dataclass
class Note:
    source_path: str
    publisher: Publisher

    @property
    def id(self) -> str:
        return self.rel_path[0:-3]

    @property
    def title(self) -> str:
        return self.id

    @property
    def rel_path(self) -> str:
        return self.source_path[len(self.publisher.kb_root) :]

    @property
    def dest_dir(self) -> Path:
        return Path(f"dist/{self.rel_path[0:-3]}/")

    @property
    def dest_file(self) -> Path:
        return self.dest_dir / "index.html"

    def publish(self):
        with open(self.source_path) as input_fd:
            source = input_fd.read()
        rendered = markdown(source)
        mkdir_p(self.dest_dir)
        with self.dest_file.open("w") as output_fd:
            output_fd.write(rendered)


def publish():
    publisher = Publisher()
    publisher.publish()


# def publish():
#     kb_root = world.get[str](Config.KB_ROOT)
#
#     public_files = []
#     notes = []
#     for filename in glob.iglob(kb_root + '/**/*.md', recursive=True):
#         if "#public" in open(filename).read():
#             public_files.append(filename)
#
#     for filename in public_files:
#         rel_path = filename[len(kb_root):]
#         with open(filename) as input_fd:
#             source = input_fd.read()
#         rendered = markdown(source)
#         dest_dir = f"dist/{rel_path[0:-3]}/"
#         dest_file = f"{dest_dir}index.html"
#         mkdir_p(dest_dir)
#         with open(dest_file, "w") as output_fd:
#             output_fd.write(rendered)
