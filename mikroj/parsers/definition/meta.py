from mikroj.parsers.definition.base import DefinitionParser
import markdown

from mikroj.registries.macro import register_definition_parser


@register_definition_parser("meta")
class MetaParser(DefinitionParser):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.md = markdown.Markdown(extensions=["meta",'fenced_code'])
        self.html = self.md.convert(self.stream)
        self._definition = {}
        for key, item in self.md.Meta.items():
            if isinstance(item, list):
                item = item[0]
            self._definition[key] = item

    def get_definition(self):
        return self._definition
