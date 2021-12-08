from typing import Optional, Union

import pydantic
from arkitekt.schema.node import Node
from mikroj.actors.base import FuncMacroActor
from mikroj.actors.define_macro import MacroDefinition, define_macro
from mikroj.actors.default import DefaultMacroActor
from mikroj.parsers.base import Parser
from mikroj.parsers.definition.base import DefinitionParser
from mikroj.parsers.code.base import CodeParser
import pathlib
from functools import reduce
from mikroj.parsers.meta import MDMeta, parse_md_meta
from mikroj.registries.actor import get_current_macro_actor_registry
from pydantic import BaseModel
import logging
import os


logger = logging.getLogger(__name__)


class QueryNodeDefinition(BaseModel):
    package: Optional[str]
    interface: Optional[str]
    q: Optional[str]


class MacroRegistry:
    def __init__(self) -> None:
        self.registered_macros = {}
        self.registered_definition_parser = {}
        self.registered_code_parser = {}
        self.registered_definitions = {}

    def register_definition_parser(self, className, parser):
        self.registered_definition_parser[className] = parser

    def register_code_parser(self, className, parser):
        self.registered_code_parser[className] = parser

    def get_definition_for_interface(self, interface) -> MacroDefinition:
        return self.registered_definitions[interface]

    def scan_folder(self, folder_path="macros"):
        assert os.path.exists(folder_path), f"Folder {folder_path} does not exist"

        pathlist = pathlib.Path(folder_path).rglob("*.ijm")
        macro_list = []
        for path in pathlist:
            # because path is object not string
            path_in_str = str(path)
            logger.debug(f"Found file {path}")
            node, definition = define_macro(path_in_str)
            self.registered_definitions[node.interface] = definition
            actorBuilder = lambda: DefaultMacroActor()

            macro_list.append((node, actorBuilder))

        return macro_list


def register_definition_parser(className: str):
    def rea_decorator(parser):
        assert issubclass(parser, Parser), "Parser must subclass Parser"
        logger.info(f"Registering Definition Parser {parser} for {className}")
        get_current_macro_registry().register_definition_parser(className, parser)
        return parser

    return rea_decorator


def register_code_parser(className: str):
    def rea_decorator(parser):
        assert issubclass(parser, Parser), "Parser must subclass Parser"
        logger.info(f"Registering Code parser {parser} for {className}")
        get_current_macro_registry().register_code_parser(className, parser)
        return parser

    return rea_decorator


MACRO_REGISTRY = None


def get_current_macro_registry(register_defaults=True) -> MacroRegistry:
    global MACRO_REGISTRY
    if MACRO_REGISTRY is None:
        MACRO_REGISTRY = MacroRegistry()

    return MACRO_REGISTRY
