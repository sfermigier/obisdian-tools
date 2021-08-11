from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Tag:
    tag: str

    def __str__(self):
        return self.tag
