"""
Aloha Browser Engine — HTML Parser
Strips CSS, JS, navigation bars, footers, ads, and layout noise.
Converts structural content into Markdown.
"""

from html.parser import HTMLParser


class AlohaHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.output = []
        self.metadata = {"title": "", "description": ""}
        self.ignore_stack = []
        self.current_href = None
        self.in_title = False

        # Noise tags that contain non-content visual/script clutter
        self.noise_tags = {
            'script', 'style', 'head', 'iframe', 'svg', 
            'nav', 'footer', 'aside', 'form', 'button', 'noscript'
        }

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)

        # Meta Title & Description Extraction
        if tag == 'title':
            self.in_title = True
        elif tag == 'meta':
            name = attr_dict.get('name', '').lower()
            prop = attr_dict.get('property', '').lower()
            if name == 'description' or prop == 'og:description':
                self.metadata['description'] = attr_dict.get('content', '')

        # Track noise elements to ignore their contents completely
        if tag in self.noise_tags or attr_dict.get('role') in ['navigation', 'banner', 'contentinfo']:
            self.ignore_stack.append(tag)
            return

        if self.ignore_stack:
            return

        # HTML -> Markdown Conversion Rules
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            self.output.append(f"\n\n{'#' * level} ")
        elif tag == 'p':
            self.output.append("\n\n")
        elif tag == 'li':
            self.output.append("\n- ")
        elif tag == 'code':
            self.output.append("`")
        elif tag == 'pre':
            self.output.append("\n```\n")
        elif tag == 'a':
            self.current_href = attr_dict.get('href', '')
            self.output.append("[")

    def handle_endtag(self, tag):
        if self.ignore_stack:
            if tag in self.noise_tags or tag == self.ignore_stack[-1]:
                self.ignore_stack.pop()
            return

        if tag == 'title':
            self.in_title = False
        elif tag == 'a' and self.current_href:
            self.output.append(f"]({self.current_href})")
            self.current_href = None
        elif tag == 'code':
            self.output.append("`")
        elif tag == 'pre':
            self.output.append("\n```\n")

    def handle_data(self, data):
        if self.in_title:
            self.metadata['title'] += data.strip()
            return

        if not self.ignore_stack:
            text = data.strip()
            if text:
                self.output.append(text + " ")

    def get_raw_markdown(self) -> str:
        return "".join(self.output)


def parse_html_to_markdown(raw_html: str) -> dict:
    """Parses raw HTML into clean structured Markdown and metadata."""
    parser = AlohaHTMLParser()
    parser.feed(raw_html)
    return {
        "metadata": parser.metadata,
        "raw_markdown": parser.get_raw_markdown()
    }


if __name__ == "__main__":
    sample_html = "<html><head><style>b{color:red}</style></head><body><h1>Hello</h1><p>Test text</p></body></html>"
    parsed = parse_html_to_markdown(sample_html)
    print("🌺 Parsed Output:", parsed['raw_markdown'].strip())
