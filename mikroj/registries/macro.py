import logging
import os
import pathlib
from typing import Optional, Union

from arkitekt.definition.registry import DefinitionRegistry
from mikroj.actors.base import FuncMacroActor
from pydantic import BaseModel, validator

from mikroj.registries.utils import load_macro, define_macro

logger = logging.getLogger(__name__)


class QueryNodeDefinition(BaseModel):
    package: Optional[str]
    interface: Optional[str]
    q: Optional[str]


class MacroRegistry(DefinitionRegistry):
    path: str = "mikroj/macros"

    @validator("path")
    def path_validator(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"Path {v} does not exist")
        return v

    def load_macros(self):
        print(self.path)
        pathlist = pathlib.Path(self.path).rglob("*.ijm")
        macro_list = []
        for path in pathlist:
            print(path)
            # because path is object not string
            path_in_str = str(path)
            macro = load_macro(path_in_str)

            definition = define_macro(macro)
            actorBuilder = lambda provision, transport: FuncMacroActor(
                provision=provision,
                transport=transport,
                macro=macro,
                expand_inputs=True,
                shrink_outputs=True,
            )

            self.register_actor_with_defintion(actorBuilder, definition)
