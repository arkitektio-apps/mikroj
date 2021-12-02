from arkitekt.actors.functional import (
    FunctionalFuncActor,
    FunctionalGenActor,
    FunctionalThreadedFuncActor,
    FunctionalThreadedGenActor,
)
from arkitekt.messages.postman.provide.bounced_provide import BouncedProvideMessage
from koil import koil
from mikroj.actors.define_macro import MacroDefinition


class MacroActor:
    async def run_macro(self, **kwargs):
        return self.helper.py.run_macro(self.macro.code, **kwargs)


class FuncMacroActor(FunctionalThreadedFuncActor):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
