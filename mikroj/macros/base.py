import re
from ..registries.helper import get_running_helper

argument_matcher = re.compile(r'[^\#]*\#\@\s*(?P<type>[^\s]*)\s*(?P<name>[^\s]*)')

class BaseMacro:

    def __init__(self, macro: str) -> None:
        self.macro = macro
        self.required_kwargs = {}

        # Lets check the for arguments
        for line in iter(self.macro.splitlines()):
            m = argument_matcher.match(line)
            if m:
                self.required_kwargs[m.group("name")] = m.group("type")

        super().__init__()

    def run(self,  with_result=True, helper = None, **kwargs):
        for key, value in self.required_kwargs.items():
            assert key in kwargs, f"This macro needs these arguments: {[f'{key}: {value}' for key, value in self.required_kwargs.items()]}"

        myhelper = helper or get_running_helper()
        result = myhelper.py.run_macro(self.macro, kwargs)
        if with_result: return result