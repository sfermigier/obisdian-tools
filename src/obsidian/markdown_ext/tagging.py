import re

from markdown import Extension, Markdown
from markdown.preprocessors import Preprocessor

TAG_RE = r"(^|\s)#([\w-]+)"


class TaggingExtension(Extension):
    def __init__(self, note, **kwargs):
        self.note = note
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown):
        processor = TaggingPreprocessor(note=self.note)
        md.preprocessors.register(processor, "tagging", 0)


class TaggingPreprocessor(Preprocessor):
    def __init__(self, note):
        self.note = note
        super().__init__()

    def run(self, lines):
        from obsidian.publish import Tag

        new_lines = []
        for line in lines:
            matches = re.findall(TAG_RE, line)
            if not matches:
                new_lines.append(line)
                continue

            for _, tag in matches:
                self.note.tags.add(Tag(tag))

        return new_lines
