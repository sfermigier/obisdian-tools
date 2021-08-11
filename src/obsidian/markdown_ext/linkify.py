# Copy/pasted from: https://github.com/daGrevis/mdx_linkify/

from bleach.linkifier import Linker
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor


class LinkifyExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            "linker_options": [{}, "Options for bleach.linkifier.Linker"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        postprocessor = LinkifyPostprocessor(md, self.getConfig("linker_options"))
        md.postprocessors.register(postprocessor, "linkify", 50)


class LinkifyPostprocessor(Postprocessor):
    def __init__(self, md, linker_options):
        super().__init__(md)
        linker_options.setdefault("skip_tags", ["code"])
        self._linker_options = linker_options

    def run(self, text):
        linker = Linker(**self._linker_options)
        return linker.linkify(text)
