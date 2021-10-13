from arkitekt.schema import Node
from html.parser import HTMLParser
import markdown


class Parser:

    def __init__(self, *args, stream=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stream = stream



class CodeBlockParser(HTMLParser):

    def __init__(self, stream, language, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.language = language
        self.note = False
        self.code_lines = []
        md = markdown.Markdown(extensions=["meta",'fenced_code'])
        html = md.convert(stream)
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "code" and self.language == dict(attrs)["class"]:
            self.note = True

    def handle_endtag(self, tag):
        if tag == "code": self.note = False

    def handle_data(self, data):
        if self.note:
            self.code_lines.append(data)


    def get_code(self):
        return "".join(self.code_lines)











