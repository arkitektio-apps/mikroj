from rekuest.api.schema import (
    DefinitionInput,
    NodeKind,
)
from .types import Macro, Parameter, DataType
from .transpile import TranspileRegistry


def define_macro(
    macro: Macro, transpile_registry: TranspileRegistry
) -> DefinitionInput:
    args = []
    returns = []

    if macro.context.setactivein:
        args += [
            Parameter(
                key="active_in",
                type=DataType.IMAGEPLUS,
                required=True,
                label="Active In",
                description="Image to be processed",
            ),
        ]

    if macro.context.takeactiveout:
        returns += [
            Parameter(
                key="active_out",
                type=DataType.IMAGEPLUS,
                required=True,
                label="Active Out",
                description="Image that was processed",
            ),
        ]

    args += macro.inputs
    returns += macro.outputs

    return DefinitionInput(
        name=macro.name,
        description=macro.description,
        args=[transpile_registry.transpile_parameter_to_port(p) for p in args],
        returns=[transpile_registry.transpile_parameter_to_port(p) for p in returns],
        kind=NodeKind.FUNCTION,
        interfaces=[],
        portGroups=[],
    )
