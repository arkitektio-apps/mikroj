import logging
from typing import Optional

from pydantic import BaseModel, Field

from arkitekt import useInstanceID
from rekuest.actors.actify import reactify
from rekuest.actors.base import Actor, ActorTransport
from rekuest.actors.types import Passport
from rekuest.agents.base import BaseAgent
from rekuest.api.schema import (
    TemplateFragment,
    acreate_template,
)
from rekuest.definition.registry import DefinitionRegistry
from rekuest.structures.default import get_default_structure_registry
from rekuest.structures.registry import StructureRegistry
from rekuest.widgets import StringWidget

from .actors.base import FuncMacroActor
from .language.define import define_macro
from .language.parse import parse_macro
from .language.transpile import TranspileRegistry
from .bridge import ImageJBridge

logger = logging.getLogger(__name__)


class MacroExtension(BaseModel):
    """MacroExtension

    The MacroExtension is an extension for the Rekuest Agent that allows
    the user to deploy ImageJ Macros as Actors (from any app) on this agent.
    """

    transpile_registry: TranspileRegistry = Field(default_factory=TranspileRegistry)
    bridge: ImageJBridge
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
            bridge=self.bridge,
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
