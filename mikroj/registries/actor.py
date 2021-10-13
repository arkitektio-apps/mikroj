from mikroj.parsers.base import Parser
from mikroj.parsers.definition.base import DefinitionParser
from mikroj.parsers.code.base import CodeParser
import pathlib
from functools import reduce
from mikroj.parsers.meta import parse_md_meta


class MacroActorRegistry:

    def __init__(self) -> None:
        self.registered_actors = {}

    def register_actor(self, className, parser):
        self.registered_actors[className] = parser

    def get_actor(self, className):
        return self.registered_actors[className]





def register_macro_actor(className: str):
    print(f"Registering Macro Actors {className}")

    def rea_decorator(parser):
        get_current_macro_actor_registry().register_actor(className, parser)
        return parser

    return rea_decorator





MACRO_ACTOR_REGISTRY = None

def get_current_macro_actor_registry(register_defaults = True) -> MacroActorRegistry:
    global MACRO_ACTOR_REGISTRY
    if MACRO_ACTOR_REGISTRY is None:
        MACRO_ACTOR_REGISTRY = MacroActorRegistry()
        if register_defaults:
            from mikroj.actors.stack import StackToStackActor

    return MACRO_ACTOR_REGISTRY


