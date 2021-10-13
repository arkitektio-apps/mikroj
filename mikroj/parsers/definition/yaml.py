from mikroj.parsers.base import CodeBlockParser
from mikroj.parsers.definition.base import DefinitionParser
from mikroj.registries.macro import register_definition_parser
import yaml

@register_definition_parser("yaml")
class YamlParser(DefinitionParser):
    language = "language-yaml"

    def __init__(self, *args, stream=None, **kwargs) -> None:
        super().__init__(*args, stream=stream, **kwargs)
        self.parser = CodeBlockParser(stream, self.language)

    def get_definition(self):
        return yaml.load(self.parser.get_code(), Loader=yaml.FullLoader)