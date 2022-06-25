import logging
import os
import pathlib
from typing import Any, Optional, Union
from arkitekt.actors.builder import ActorBuilder

from arkitekt.definition.registry import DefinitionRegistry
from arkitekt.qt.builders import QtInLoopBuilder
from mikroj.actors.base import FuncMacroActor
from pydantic import BaseModel, Field, validator
from mikroj.macro_helper import ImageJMacroHelper
from mikroj.registries.base import Macro

from mikroj.registries.utils import load_macro, define_macro

logger = logging.getLogger(__name__)


class MacroBuilder(ActorBuilder):
    """MacroBuilder

    MacroBuilder is a builder for FuncMacroActor.
    """

    def __init__(self, macro: Macro, helper: ImageJMacroHelper):
        self.macro = macro
        self.helper = helper

    def __call__(self, *args, **kwargs):
        return FuncMacroActor(
            macro=self.macro,
            helper=self.helper,
            expand_inputs=True,
            shrink_outputs=True,
            *args,
            **kwargs,
        )


class MacroRegistry(DefinitionRegistry):
    path: str = "mikroj/macros"
    helper: ImageJMacroHelper = Field(default_factory=ImageJMacroHelper)

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

            actorBuilder = MacroBuilder(macro, self.helper)

            self.register_actor_with_defintion(actorBuilder, definition)
