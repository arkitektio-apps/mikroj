from arkitekt.actors.functional import (
    FunctionalThreadedFuncActor,
)
from mikroj.registries.base import Macro
from mikroj.helper import ImageJ


class FuncMacroActor(FunctionalThreadedFuncActor):
    helper: ImageJ
    macro: Macro

    async def run_macro(self, **kwargs):
        return self.helper.py.run_macro(self.macro.code, **kwargs)
