""" Python types for ImageJ Macro Defintions"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class DataType(str, Enum):
    BOOLEAN = "boolean"
    BIGINTEGER = "biginteger"
    BYTE = "byte"
    SHORT = "short"
    INT = "int"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    CHAR = "char"
    STRING = "string"
    DATASET = "dataset"
    IMAGEPLUS = "imageplus"
    COLOR_RGB = "color_rgb"
    DATE = "date"
    FILE = "file"


class Visibility(str, Enum):
    NORMAL = "NORMAL"
    """ parameter is included in the history for purposes of data provenance,
      and included as a parameter when recording scripts."""
    TRANSIENT = "TRANSIENT"
    """ parameter is excluded from the history for the purposes of data provenance,
      but still included as a parameter when recording scripts."""
    INVISIBLE = "INVISIBLE"
    """ parameter is excluded from the history for the purposes of data provenance, 
    and also excluded as a parameter when recording scripts. This option should only 
    be used for parameters with no effect on the final output, such as a “verbose” 
    flag."""
    MESSAGE = "MESSAGE"
    """: parameter value is intended as a message only, not editable by the user 
    nor included as an input or output parameter. The option required should be
      set to false."""


class Parameter(BaseModel):
    key: str
    type: DataType
    label: Optional[str]
    min: Optional[float]
    max: Optional[float]
    step_size: Optional[float] = Field(alias="stepSize")
    choices: Optional[List[str]]
    is_list: bool = Field(
        default=False,
        alias="is_list",
        description="Whether the parameter is a list or not",
    )
    required: bool = Field(
        default=True,
        alias="required",
        description="Whether the parameter is required or not",
    )
    description: Optional[str] = Field(
        default=None,
        alias="description",
        description="Description of the parameter (mouse over)",
    )
    persist: bool = Field(
        default=False,
        alias="persist",
        description=(
            "Per default, variable values are persisted between runs of a script. "
            "This means that parameter values from a previous run are used as starting "
            "value. Please note that a persisted value will overwrite a defined default"
            "value."
        ),
    )
    style: Optional[str]
    value: Optional[str] = Field(
        default=None, alias="value", description="Default value"
    )
    visibility: Visibility = Visibility.NORMAL

    @validator("type", pre=True, always=True)
    def validate_type(cls, value):
        value = value.lower()
        if value == "character":
            value = "char"
        if value == "integer":
            value = "int"

        return DataType(value)


class Context(BaseModel):
    setactivein: bool = False  # mirorring CellProfiler approach
    takeactiveout: bool = False
    donecloseactive: bool = False
    interactive: bool = False
    getroisout: bool = False
    getresults: bool = False
    filter: bool = False
    rgb: bool = False


class Macro(BaseModel):
    code: str = Field(description="The code of the macro")
    name: Optional[str] = Field(description="Doc string Name of the Macro")
    description: Optional[str] = Field(
        description="Doc string decsription of the Macro"
    )
    context: Context = Field(
        default_factory=Context,
        description="""Extracted Context of the Macro (e.g. if after running the active
          image should be returned""",
    )
    inputs: List[Parameter] = Field(
        default_factory=list, description="Inputso of this Macro"
    )
    outputs: List[Parameter] = Field(
        default_factory=list, description="Outputs of this Macro"
    )
