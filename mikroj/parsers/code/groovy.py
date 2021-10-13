
from mikroj.parsers.base import CodeBlockParser
from mikroj.parsers.code.base import CodeParser
from mikroj.registries.macro import register_code_parser


@register_code_parser("groovy")
class GroovyParser(CodeParser):
    language = "language-groovy"

    def __init__(self, *args, stream=None, **kwargs) -> None:
        super().__init__(*args, stream=stream, **kwargs)
        self.parser = CodeBlockParser(stream, self.language)

    def get_code(self):
        return self.parser.get_code()