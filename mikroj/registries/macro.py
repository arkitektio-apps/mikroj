import logging
import os
import pathlib
from typing import Any, Optional, Union

from rekuest.agents.transport.base import AgentTransport

from rekuest.messages import Provision

from koil.qt import QtCoro

from rekuest.actors.functional import FunctionalFuncActor
from rekuest.api.schema import ProvisionFragment, DefinitionFragment, DefinitionInput

from rekuest.definition.registry import ActorBuilder, DefinitionRegistry
from rekuest.qt.builders import QtInLoopBuilder
from mikroj.actors.base import FuncMacroActor
from pydantic import BaseModel, Field, validator
from mikroj.macro_helper import ImageJMacroHelper
from mikroj.registries.base import Macro
from qtpy import QtCore
from mikroj.registries.utils import load_macro, define_macro
from rekuest.structures.registry import StructureRegistry, get_current_structure_registry
logger = logging.getLogger(__name__)


class MacroBuilder:
    """MacroBuilder

    MacroBuilder is a builder for FuncMacroActor.
    """
    __definition__: DefinitionInput

    def __init__(self, definition: DefinitionInput, macro: Macro, helper: ImageJMacroHelper, structure_registry: StructureRegistry) -> None:
        self.__definition__ = definition
        self.macro = macro
        self.helper = helper
        self.structure_registry = structure_registry

    def __call__(self, *args, **kwargs):
        return FuncMacroActor(
            definition=self.__definition__,
            structure_registry=self.structure_registry,
            macro=self.macro,
            helper=self.helper,
            expand_inputs=True,
            shrink_outputs=True,
            *args,
            **kwargs,
        )


class MacroInLoopBuilder(QtCore.QObject):
    """MacroBuilder

    MacroBuilder is a builder for FuncMacroActor.
    """

    provision: ProvisionFragment

    def __init__(self, assign=None, *args, parent=None, **actor_kwargs) -> None:
        super().__init__(*args, parent=parent)
        self.coro = QtCoro(
            lambda f, *args, **kwargs: assign(*args, **kwargs), autoresolve=True
        )
        self.provisions = {}
        self.actor_kwargs = actor_kwargs

    async def on_assign(self, *args, **kwargs) -> None:
        return await self.coro.acall(*args, **kwargs)

    def __call__(self, provision: Provision, transport: AgentTransport):
        ac = FunctionalFuncActor(
            provision=provision,
            transport=transport,
            assign=self.on_assign,
            **self.actor_kwargs,
        )
        return ac


class MacroRegistry(DefinitionRegistry):
    path: str = "mikroj/macros"
    helper: ImageJMacroHelper = Field(default_factory=ImageJMacroHelper)

    @validator("path")
    def path_validator(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"Path {v} does not exist")
        return v

    def load_macros(self):
        pathlist = pathlib.Path(self.path).rglob("*.ijm")
        macro_list = []
        for path in pathlist:
            # because path is object not string
            path_in_str = str(path)
            macro = load_macro(path_in_str)
            structure_registry = self.structure_registry or get_current_structure_registry()

            definition = define_macro(macro)
            actorBuilder = MacroBuilder(definition, macro, self.helper, structure_registry)

            self.register_actorBuilder(actorBuilder)
