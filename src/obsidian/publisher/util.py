from __future__ import annotations

from typing import Any
from urllib.parse import quote

from obsidian.publisher.note import Note
from obsidian.publisher.tag import Tag


def url_for(obj: Any) -> str:
    prefix = "/notes"

    if isinstance(obj, Note):
        return f"{prefix}/n/{quote(obj.id)}/"

    if isinstance(obj, Tag):
        return f"{prefix}/t/{obj.tag}/"

    if isinstance(obj, str):
        return f"{prefix}/{obj}"

    raise Exception(f"Unknown type: {type(obj)}")
