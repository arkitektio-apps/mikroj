from typing import Optional
import markdown
from pydantic import BaseModel

class MDMeta(BaseModel):
    title: str
    code_parser: Optional[str] = "groovy"
    definition_parser: Optional[str] = "yaml"
    actor: str

    def get_code_parsers(self):
        return[i.strip() for i in self.code_parser.split(",")]

    def get_definition_parsers(self):
        return [i.strip() for i in self.definition_parser.split(",")]




def parse_md_meta(stream):
    md = markdown.Markdown(extensions=["meta",'fenced_code'])
    html = md.convert(stream)
    _meta = {}
    for key, item in md.Meta.items():
        if isinstance(item, list):
            item = item[0]
        _meta[key] = item
    return MDMeta(**_meta)

