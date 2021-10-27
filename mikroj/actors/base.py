from arkitekt.actors.functional import FunctionalFuncActor, FunctionalGenActor
from arkitekt.messages.postman.provide.bounced_provide import BouncedProvideMessage
from koil import koil

class FuncMacroActor(FunctionalFuncActor):

    def __init__(self, *args, macro: str = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert macro, "Please create a provide a macro function"
        self.macro = macro

    async def on_provide(self, message: BouncedProvideMessage):
        self.helper = self.agent.helper
        assert self.template, " please provide a template"


    async def run_macro(self, **kwargs):
        return self.helper.py.run_macro(self.macro.code, **kwargs)



class GenMacroActor(FunctionalGenActor):

    def __init__(self, *args, macro: str = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert self.macro, "Please create a provide a macro function"
        self.macro = macro

    async def on_provide(self, message: BouncedProvideMessage):
        self.helper = self.agent.helper
        assert self.template, " please provide a template"


    async def run_macro(self, **kwargs):
        return self.helper.py.run_macro(self.macro.code, **kwargs)
