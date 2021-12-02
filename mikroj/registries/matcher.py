from arkitekt.packers.structure import BoundType
from arkitekt.schema.ports import (
    IntArgPort,
    IntReturnPort,
    StringArgPort,
    StringKwargPort,
    StructureArgPort,
    IntArgPort,
    IntReturnPort,
    StructureReturnPort,
)
from mikro.schema import Representation


class PortMatcher:
    def __init__(self) -> None:
        self.typeMap = {}

    def register(self, type, imagejType, argBuilder):
        self.typeMap.setdefault(type, {})[imagejType] = argBuilder

    def argbuilder_for_type(self, imagejType):
        return self.typeMap["arg"][imagejType]

    def kwargbuilder_for_type(self, imagejType):
        return self.typeMap["kwarg"][imagejType]

    def returnbuilder_for_type(self, imagejType):
        return self.typeMap["return"][imagejType]


def string_kwarg_builder(
    default=None,
    **kwargs,
):
    return StringKwargPort(**kwargs, defaultString=default.replace('"', ""))


def imageplus_arg_builder(
    **kwargs,
):
    return StructureArgPort(
        **kwargs,
        identifier="representation",
        widget=Representation.get_structure_meta().widget,
    )


def imageplus_return_builder(
    **kwargs,
):
    return StructureReturnPort(
        **kwargs,
        identifier="representation",
    )


MATCHER = PortMatcher()
MATCHER.register("arg", "String", StringArgPort)
MATCHER.register("kwarg", "String", string_kwarg_builder)
MATCHER.register("return", "Integer", IntReturnPort)
MATCHER.register("arg", "ImagePlus", imageplus_arg_builder)
MATCHER.register("return", "ImagePlus", imageplus_return_builder)
MATCHER.register("arg", "Dataset", imageplus_arg_builder)
MATCHER.register("return", "Dataset", imageplus_return_builder)


def get_current_matcher():
    global MATCHER
    return MATCHER
