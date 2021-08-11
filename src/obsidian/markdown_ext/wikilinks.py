"""
WikiLinks Extension for Python-Markdown
======================================

Converts [[WikiLinks]] to relative links.

See <https://Python-Markdown.github.io/extensions/wikilinks>
for documentation.

Original code Copyright [Waylan Limberg](http://achinghead.com/).

All changes Copyright The Python Markdown Project

License: [BSD](https://opensource.org/licenses/bsd-license.php)

"""

import xml.etree.ElementTree as etree

from markdown import Extension
from markdown.inlinepatterns import InlineProcessor

WIKILINK_RE = r"\[\[(.+?)\]\]"


def build_url(label, base, end):
    """Build a url from the label, a base, and an end."""
    return label
    # clean_label = re.sub(r"([ ]+_)|(_[ ]+)|([ ]+)", "_", label)
    # return "{}{}{}".format(base, clean_label, end)


class WikiLinkExtension(Extension):
    def __init__(self, note, **kwargs):
        self.note = note
        self.config = {
            "base_url": ["/", "String to append to beginning or URL."],
            "end_url": ["/", "String to append to end of URL."],
            "html_class": ["wikilink", "CSS hook. Leave blank for none."],
            "build_url": [build_url, "Callable formats URL from label."],
        }

        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        # append to end of inline patterns
        processor = WikiLinksInlineProcessor(WIKILINK_RE, self.note, self.getConfigs())
        md.inlinePatterns.register(processor, "wikilink", 75)


class WikiLinksInlineProcessor(InlineProcessor):
    def __init__(self, pattern, note, config):
        super().__init__(pattern)
        self.config = config
        self.note = note

    def handleMatch(self, m, data):
        from obsidian.publisher import url_for

        link = m.group(1).strip()

        note = self.note.kb.find_note(link)
        if not note:
            return link, m.start(0), m.end(0)

        self.note.internal_links.add(note)

        label = link
        url = url_for(note)
        # url = self.config['build_url'](label, base_url, end_url)
        a = etree.Element("a")
        a.text = label
        a.set("href", url)
        # if html_class:
        #     a.set('class', html_class)

        return a, m.start(0), m.end(0)
