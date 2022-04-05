from typing import Union
import pathlib
import re
from arkitekt.api.schema import DefinitionInput, NodeType
from pydantic.main import BaseModel
from mikroj.registries.base import Macro

doc = re.compile("\/\*(?P<name>(.|\n)*)\*\/*")

documentation = re.compile(
    "\/\*\W*(?P<name>[^\n]*)\n\W*(?P<description>[^\/\@]*)\n*\*.*"
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


def load_macro(path: Union[str, pathlib.Path]) -> Macro:
    with open(path, "r") as f:
        code = f.read()

    d = documentation.match(code)
    assert d, "No documentation found in macro"

    return Macro(name=d.group("name"), description=d.group("description"), code=code)


def define_macro(macro: Macro) -> DefinitionInput:

    return DefinitionInput(
        name=macro.name,
        description=macro.description,
        args=[],
        kwargs=[],
        returns=[],
        interface=macro.name,
        type=NodeType.FUNCTION,
    )
