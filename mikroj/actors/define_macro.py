import re

from arkitekt.api.schema import DefinitionInput
from pydantic.main import BaseModel

doc = re.compile("\/\*(?P<name>(.|\n)*)\*\/*")

documentation = re.compile(
    "\/\*\W*(?P<name>[^\n]*)\n\W*(?P<doc>[^\/\@]*)\n*\*.*"
)  # matches the first line in a docstring

in_re = re.compile("#@\W(?P<type>\w*)\W*(?P<key>\w*)")
return_re = re.compile("#@output\W(?P<type>\w*)\W*(?P<key>\w*)")

is_interactive_re = re.compile(".*@interactive*")
activein_re = re.compile(".*\@setactivein.*")
activeout_re = re.compile(".*\@takeactiveout*")
donecloseactive_re = re.compile(".*\@donecloseactive*")
filter_re = re.compile(".*\@filter*")
rgb_re = re.compile(".*\@rgb*")


params_re = re.compile(r"#@[^\(]*\((?P<params>[^\)]*)\)")  # line has params


class MacroDefinition(BaseModel):
    setactivein: bool = False  # mirorring CellProfiler approach
    takeactiveout: bool = False
    donecloseactive: bool = False
    interactive: bool = False
    filter: bool = False
    macro: str
