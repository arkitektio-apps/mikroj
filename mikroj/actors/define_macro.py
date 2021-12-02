import os
from typing import Tuple

from pydantic.main import BaseModel
from arkitekt.packers.structure import BoundType
from arkitekt.schema import Node
import re
from arkitekt.schema.ports import StructureArgPort, StructureReturnPort
from mikro.schema import Representation

from mikroj.registries.matcher import get_current_matcher

doc = re.compile("\/\*(?P<name>(.|\n)*)\*\/*")

documentation = re.compile(
    "\/\*\W*(?P<name>[^\n]*)\n\W*(?P<doc>[^\/]*)\n*\*.*"
)  # matches the first line in a docstring

in_re = re.compile("#@\W(?P<type>\w*)\W*(?P<key>\w*)")
return_re = re.compile("#@output\W(?P<type>\w*)\W*(?P<key>\w*)")

is_interactive_re = re.compile(".*@interactive*")
activein_re = re.compile(".*\@setactivein.*")
activeout_re = re.compile(".*\@takeactiveout*")


params_re = re.compile(r"#@[^\(]*\((?P<params>[^\)]*)\)")  # line has params


class MacroDefinition(BaseModel):
    setactivein: bool = False  # mirorring CellProfiler approach
    takeactiveout: bool = False
    is_interactive: bool = False
    macro: str


def define_macro(file: str) -> Tuple[Node, MacroDefinition]:

    matcher = get_current_matcher()

    with open(file) as f:
        all = f.read()

    macro_def = MacroDefinition(macro=all)

    with open(file) as f:
        lines = f.readlines()

    x = documentation.match(all)

    macro_def.is_interactive = is_interactive_re.search(all) is not None
    macro_def.setactivein = activein_re.search(all) is not None
    macro_def.takeactiveout = activeout_re.search(all) is not None

    print("noainasoisnaoin", activein_re.search(all))
    if x:
        node_name = x.group("name")
        doc = x.group("doc").replace("*", "").replace("\n", "").strip()

    else:
        raise Exception("Not well defined Macro Documentation")

    args = []
    kwargs = []
    returns = []

    for line in lines:

        inmatch = in_re.match(line)
        if inmatch:
            imageJType = inmatch.group("type")
            key = inmatch.group("key")

            extras = {}
            description = ""

            paramsmatch = params_re.match(line)
            if paramsmatch:
                params = paramsmatch.group("params")
                for param in params.split(","):
                    pair = param.split("=")
                    extras[pair[0].strip()] = pair[1].strip()

            if "value" in extras:

                port = matcher.kwargbuilder_for_type(imageJType)(
                    key=key, description=description, default=extras["value"]
                )
                kwargs.append(port)

            else:
                port = matcher.argbuilder_for_type(imageJType)(
                    key=key, description=description
                )
                args.append(port)

        rematch = return_re.match(line)
        if rematch:
            imageJType = rematch.group("type")
            key = rematch.group("key")

            paramsmatch = params_re.match(line)
            if paramsmatch:
                params = paramsmatch.group("params")
                print(params)

            port = matcher.returnbuilder_for_type(imageJType)(
                key=key, description=description
            )
            returns.append(port)

            print("Return", type, key)

    if macro_def.setactivein:
        # Because this is how the fuckinng macros work apperently :rolling-eyes:
        args.insert(
            0,
            StructureArgPort(
                identifier="representation",
                key="image",
                widget=Representation.get_structure_meta().widget,
            ),
        )

    if macro_def.takeactiveout:
        returns.insert(
            0,
            StructureReturnPort(
                identifier="representation",
                key="image",
            ),
        )

    print(macro_def, node_name)

    return (
        Node(
            **{
                "name": node_name,
                "description": doc,
                "args": args,
                "kwargs": kwargs,
                "returns": returns,
                "package": "macros",
                "interface": os.path.basename(file),
            }
        ),
        macro_def,
    )
