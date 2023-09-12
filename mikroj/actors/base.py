import logging
from typing import Any, Protocol, TypeVar, runtime_checkable


from mikroj import constants, structures
from mikroj.language.types import Macro
from mikroj.bridge import ImageJBridge
from rekuest.actors.functional import ThreadedFuncActor
from rekuest.api.schema import (
    DefinitionInput,
)

T = TypeVar("T")


@runtime_checkable
class TranspileAble(Protocol):
    @classmethod
    def from_jreturn(cls: T, value, Any) -> T:
        ...

    def to_jarg(self, bridge: ImageJBridge) -> Any:
        ...


def convert_inputs(kwargs, bridge: ImageJBridge, definition: DefinitionInput):
    transpile_inputs = {}
    for key, value in kwargs.items():
        if key == "active_in":
            value.set_active()
            continue

        if isinstance(value, TranspileAble):
            transpile_inputs[key] = value.to_jarg()
        else:
            transpile_inputs[key] = bridge.py.to_java(value)

    return transpile_inputs


def convert_outputs(macro_output, bridge: ImageJBridge, definition: DefinitionInput):
    transpile_outputs = []
    for port in definition.returns:
        if port.key == "active_out":
            transpile_outputs.append(
                structures.ImageJPlus(bridge.py.active_imageplus())
            )
            continue
        if port.identifier == constants.IMAGEJ_PLUS_IDENTIFIER:
            transpile_outputs.append(
                structures.ImageJPlus.from_jreturn(
                    macro_output.getOutput(port.key), bridge
                )
            )
            continue

        transpile_outputs.append(bridge.py.to_python(macro_output.getOutput(port.key)))

    return transpile_outputs


class FuncMacroActor(ThreadedFuncActor):
    """Base class for actors that run ImageJ macros. They are threaded by default,
      as the pyimagej interface is supposedly thread safe."""

    macro: Macro
    bridge: ImageJBridge

    def assign(self, **kwargs):
        logging.info("Being assigned")
        transpiled_args = convert_inputs(kwargs, self.bridge, self.definition)
        macro_output = self.bridge.run_macro(self.macro.code, {**transpiled_args})
        transpiled_returns = convert_outputs(macro_output, self.bridge, self.definition)

        return tuple(transpiled_returns) if transpiled_returns else None

    class Config:
        underscore_attrs_are_private = True
