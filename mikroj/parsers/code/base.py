

from mikroj.parsers.base import Parser
from html.parser import HTMLParser
import markdown

class CodeParser(Parser):

    def __init__(self, *args, stream=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stream = stream

    def get_code(self):
        raise NotImplementedError()



