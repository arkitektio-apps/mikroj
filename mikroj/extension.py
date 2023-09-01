from reaktion.actor import FlowActor
from rekuest.agents.errors import ProvisionException
from rekuest.agents.base import BaseAgent

import logging
from rekuest.register import register_func
from rekuest.actors.base import Actor
from rekuest.actors.types import Passport, Assignment
from rekuest.actors.transport.local_transport import (
    AgentActorTransport,
    AgentActorAssignTransport,
)
from fluss.api.schema import aget_flow
from rekuest.api.schema import aget_template, NodeKind
from rekuest.messages import Provision
from typing import Optional
from rekuest.api.schema import (
    PortInput,
    DefinitionInput,
    TemplateFragment,
    NodeKind,
    acreate_template,
    adelete_node,
    afind,
)
from fakts.fakts import Fakts
from fluss.api.schema import (
    FlowFragment,
    LocalNodeFragment,
    GraphNodeFragment,
)
from reaktion.utils import infer_kind_from_graph
from rekuest.widgets import SliderWidget, StringWidget
from rekuest.structures.default import get_default_structure_registry
from rekuest.structures.registry import StructureRegistry
from pydantic import BaseModel, Field
from rekuest.agents.extension import AgentExtension

from rekuest.definition.registry import DefinitionRegistry
from rekuest.actors.actify import reactify
from .macro_helper import ImageJMacroHelper
from .language.types import Macro
from .language.parse import parse_macro
from .language.define import define_macro
from .language.transpile import TranspileRegistry
from .actors.base import FuncMacroActor
from arkitekt import useInstanceID
from rekuest.actors.base import ActorTransport

logger = logging.getLogger(__name__)


class MacroBuilder:
    """MacroBuilder

    MacroBuilder is a builder for FuncMacroActor.
    """

    def __init__(
        self,
        definition: DefinitionInput,
        macro: Macro,
        helper: ImageJMacroHelper,
        structure_registry: StructureRegistry,
    ) -> None:
        self.definition = definition
        self.macro = macro
        self.helper = helper
        self.structure_registry = structure_registry

    def __call__(self, *args, **kwargs):
        return FuncMacroActor(
            structure_registry=self.structure_registry,
            macro=self.macro,
            helper=self.helper,
            expand_inputs=True,
            shrink_outputs=True,
            *args,
            **kwargs,
        )


class MacroExtension(BaseModel):
    transpile_registry: TranspileRegistry = Field(default_factory=TranspileRegistry)
    helper: ImageJMacroHelper
    structure_registry: StructureRegistry = Field(
        default_factory=get_default_structure_registry
    )

    async def aspawn_actor_from_template(
        self,
        template: TemplateFragment,
        passport: Passport,
        transport: ActorTransport,
        agent: "BaseAgent",
    ) -> Optional[Actor]:
        """Spawns an Actor from a Provision. This function closely mimics the
        spawining protocol within an actor. But maps template"""

        x = template
        assert "code" in x.params, "Template is not a code"
        macro = parse_macro(x.params["code"])
        definition = define_macro(macro, self.transpile_registry)

        return FuncMacroActor(
            macro=macro,
            passport=passport,
            transport=transport,
            structure_registry=self.structure_registry,
            helper=self.helper,
            definition=definition,
            agent=agent,
            collector=agent.collector,
        )

    async def aregister_definitions(
        self, definition_registry: DefinitionRegistry, instance_id: str = None
    ):
        definition, actorBuilder = reactify(
            self.deploy_imagej_macro,
            self.structure_registry,
            widgets={"code": StringWidget(as_paragraph=True)},
            interfaces=["imagej:deploymacro"],
        )

        definition_registry.register_at_interface(
            "deploy_macro",
            definition=definition,
            structure_registry=self.structure_registry,
            actorBuilder=actorBuilder,
        )

    async def deploy_imagej_macro(self, code: str) -> TemplateFragment:
        """Deploy ImageJ Macro

        Deploys an image macro and converts it to a local template

        Parameters
        ----------
        code : str
            The macro code

        Returns
        -------
        TemplateFragment
            The newly created image
        """
        macro = parse_macro(code)
        definition = define_macro(macro, self.transpile_registry)

        template = await acreate_template(
            macro.name,
            definition,
            useInstanceID(),  # TODO: make this configurable
            params={"code": code},
            extensions=["macro"],
        )
        return template
