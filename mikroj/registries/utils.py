from typing import Union
import pathlib
import re

from rekuest.api.schema import (
    ArgPortInput,
    DefinitionInput,
    NodeKind,
    PortKindInput,
    ReturnPortInput,
)
from pydantic.main import BaseModel
from mikro.widgets import MY_TOP_REPRESENTATIONS
from mikroj.registries.base import Macro

doc = re.compile("\/\*(?P<name>(.|\n)*)\*\/*")

documentation = re.compile(
    "\/\*\W*(?P<name>[^\n]*)\n\W*(?P<description>[^\/\@]*)\n*\*.*"
)  # matches the first line in a docstring

in_re = re.compile("#@\W(?P<type>\w*)\W*(?P<key>\w*)")
return_re = re.compile("#@output\W(?P<type>\w*)\W*(?P<key>\w*)")

is_interactive_re = re.compile(".*@interactive*")
activein_re = re.compile(".*\@setactivein.*")
interfaces_re = re.compile(".*@interface:(\w*)\n")
activeout_re = re.compile(".*\@takeactiveout*")
donecloseactive_re = re.compile(".*\@donecloseactive*")
filter_re = re.compile(".*\@filter*")
rgb_re = re.compile(".*\@rgb*")


params_re = re.compile(r"#@[^\(]*\((?P<params>[^\)]*)\)")  # line has params


def load_macro(path: Union[str, pathlib.Path]) -> Macro:
    with open(path, "r") as f:
        code = f.read()

    interfaces = interfaces_re.findall(code) or []
    d = documentation.match(code)
    setactivein = bool(activein_re.search(code))
    activeout = bool(activeout_re.search(code))
    filter = bool(filter_re.search(code))
    rgb = bool(rgb_re.search(code))
    if filter:
        interfaces.append("filter")
    if rgb:
        interfaces.append("rgb")

    assert d, "No documentation found in macro"

    m = Macro(
        name=d.group("name"),
        description=d.group("description"),
        code=code,
        interfaces=interfaces,
        setactivein=setactivein,
        takeactiveout=activeout,
        filter=filter,
        rgb=rgb,
    )
    return m


def define_macro(macro: Macro) -> DefinitionInput:
    args = []
    returns = []

    if macro.setactivein:
        args += [
            ArgPortInput(
                kind=PortKindInput.STRUCTURE,
                key="image",
                identifier="@mikro/representation",
                description="Image to be processed",
                widget=MY_TOP_REPRESENTATIONS,
                nullable=False,
            )
        ]

    if macro.takeactiveout:
        returns += [
            ReturnPortInput(
                kind=PortKindInput.STRUCTURE,
                key="image",
                identifier="@mikro/representation",
                description="Image to be processed",
                nullable=False,
            )
        ]

    return DefinitionInput(
        name=macro.name,
        description=macro.description,
        args=args,
        interfaces=macro.interfaces,
        returns=returns,
        interface=macro.name,
        kind=NodeKind.FUNCTION,
    )
