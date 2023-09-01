from concurrent.futures import ThreadPoolExecutor
import logging
from rekuest.actors.functional import (
    ThreadedFuncActor,
)
from rekuest.api.schema import (
    ProvisionFragment,
    ProvisionFragmentTemplate,
    DefinitionFragment,
    DefinitionInput,
)
from mikro.api.schema import (
    RepresentationFragment,
    RepresentationVarietyInput,
    from_xarray,
    from_df,
)
from rekuest.definition.validate import auto_validate
from mikroj.macro_helper import ImageJMacroHelper
from mikroj.language.types import Macro
from mikro.traits import Representation
import xarray as xr
from pydantic import Field
from typing import Protocol, TypeVar, runtime_checkable, Any
from mikroj import constants, structures

T = TypeVar("T")


@runtime_checkable
class TranspileAble(Protocol):
    @classmethod
    def from_jreturn(cls: T, value, Any) -> T:
        ...

    def to_jarg(self, helper: ImageJMacroHelper) -> Any:
        ...


def convert_inputs(kwargs, helper: ImageJMacroHelper, definition: DefinitionInput):
    transpile_inputs = {}
    for key, value in kwargs.items():
        if key == "active_in":
            value.set_active(helper)
            continue

        if isinstance(value, TranspileAble):
            transpile_inputs[key] = value.to_jarg(helper)
        else:
            transpile_inputs[key] = helper.py.to_java(value)

    return transpile_inputs


def convert_outputs(
    macro_output, helper: ImageJMacroHelper, definition: DefinitionInput
):
    transpile_outputs = []
    for port in definition.returns:
        if port.key == "active_out":
            transpile_outputs.append(
                structures.ImageJPlus(helper.py.active_imageplus())
            )
            continue
        if port.identifier == constants.IMAGEJ_PLUS_IDENTIFIER:
            transpile_outputs.append(
                structures.ImageJPlus.from_jreturn(
                    macro_output.getOutput(port.key), helper
                )
            )
            continue

        transpile_outputs.append(helper.py.to_python(macro_output.getOutput(port.key)))

    return transpile_outputs


class FuncMacroActor(ThreadedFuncActor):
    macro: Macro
    helper: ImageJMacroHelper

    def assign(self, **kwargs):
        logging.info("Being assigned")
        transpiled_args = convert_inputs(kwargs, self.helper, self.definition)
        macro_output = self.helper.py.run_macro(self.macro.code, {**transpiled_args})
        transpiled_returns = convert_outputs(macro_output, self.helper, self.definition)

        return tuple(transpiled_returns) if transpiled_returns else None

    class Config:
        underscore_attrs_are_private = True
