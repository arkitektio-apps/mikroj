from arkitekt.qt.agent import QtAgent
from arkitekt.schema.node import Node
from mikroj.registries.macro import get_current_macro_registry, QueryNodeDefinition
import logging

logger = logging.getLogger(__name__)


class MikroJAgent(QtAgent):
    def __init__(self, helper, *args, strict=False, **kwargs) -> None:
        super().__init__(*args, strict=strict, **kwargs)
        self.helper = helper

    def load_macros(self, filepath):
        logger.debug(f"Opening Macros in {filepath}")
        macro_associations = get_current_macro_registry().scan_folder(
            folder_path=filepath
        )

        for defi, actorBuilder in macro_associations:
            if isinstance(defi, QueryNodeDefinition):
                self.registry.templatedUnqueriedNodes.append(
                    (defi.dict(), actorBuilder, {})
                )
            if isinstance(defi, Node):
                self.registry.templatedNewNodes.append((defi, actorBuilder, {}))
