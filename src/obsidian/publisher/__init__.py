from __future__ import annotations

from obsidian.publisher.kb import KB
from obsidian.publisher.note import Note
from obsidian.publisher.tag import Tag
from obsidian.publisher.util import url_for


def publish():
    kb = KB()
    kb.publish()
