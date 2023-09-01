from rekuest.api.schema import (
    PortInput,
    PortKindInput,
    WidgetInput,
    ChoiceInput,
    WidgetKind,
    Scope,
)
from rekuest.widgets import SliderWidget, ChoiceWidget, ChoiceReturnWidget
from pydantic.main import BaseModel
from mikroj import constants
from .types import Parameter, DataType
from typing import Callable, Optional


def parameter_to_assign_widget(p: Parameter) -> Optional[WidgetInput]:
    if p.type in [DataType.INT, DataType.FLOAT, DataType.DOUBLE]:
        if p.min and p.max:
            return SliderWidget(min=p.min, max=p.max)

    if p.choices:
        return ChoiceWidget(
            choices=[ChoiceInput(value=value, label=value) for value in p.choices]
        )


def parameter_to_return_widget(p: Parameter) -> Optional[WidgetInput]:
    if p.choices:
        return ChoiceReturnWidget(
            choices=[ChoiceInput(value=value, label=value) for value in p.choices]
        )


def to_int(p: Parameter) -> PortInput:
    return PortInput(
        kind=PortKindInput.INT,
        key=p.key,
        label=p.label,
        description=p.description,
        nullable=p.required,
        scope=Scope.GLOBAL,
        default=p.value,
        assignWidget=parameter_to_assign_widget(p),
        returnWidget=parameter_to_return_widget(p),
    )


def to_float(p: Parameter) -> PortInput:
    return PortInput(
        kind=PortKindInput.FLOAT,
        key=p.key,
        label=p.label,
        description=p.description,
        nullable=p.required,
        scope=Scope.GLOBAL,
        default=p.value,
        assignWidget=parameter_to_assign_widget(p),
        returnWidget=parameter_to_return_widget(p),
    )


def to_str(p: Parameter) -> PortInput:
    return PortInput(
        kind=PortKindInput.STRING,
        key=p.key,
        label=p.label,
        description=p.description,
        nullable=p.required,
        scope=Scope.GLOBAL,
        default=p.value,
        assignWidget=parameter_to_assign_widget(p),
        returnWidget=parameter_to_return_widget(p),
    )


def to_bool(p: Parameter) -> PortInput:
    return PortInput(
        kind=PortKindInput.BOOL,
        key=p.key,
        label=p.label,
        description=p.description,
        nullable=p.required,
        scope=Scope.GLOBAL,
        default=p.value,
        assignWidget=parameter_to_assign_widget(p),
        returnWidget=parameter_to_return_widget(p),
    )


def to_date(p: Parameter) -> PortInput:
    return PortInput(
        kind=PortKindInput.STRING,
        key=p.key,
        label=p.label,
        description=p.description,
        nullable=p.required,
        scope=Scope.GLOBAL,
        default=p.value,
        assignWidget=WidgetInput(kind=WidgetKind.DateWidget),
    )


def to_color(p: Parameter) -> PortInput:
    return PortInput(
        kind=PortKindInput.STRING,
        key=p.key,
        label=p.label,
        description=p.description,
        nullable=p.required,
        scope=Scope.GLOBAL,
        default=p.value,
        assignWidget=WidgetInput(kind=WidgetKind.ColorWidget),
    )


def to_image_plus(p: Parameter) -> PortInput:
    return PortInput(
        kind=PortKindInput.STRUCTURE,
        identifier=constants.IMAGEJ_PLUS_IDENTIFIER,
        key=p.key,
        label=p.label,
        description=p.description,
        nullable=p.required,
        scope=Scope.LOCAL,
        default=p.value,
        assignWidget=parameter_to_assign_widget(p),
        returnWidget=parameter_to_return_widget(p),
    )


def to_file(p: Parameter) -> PortInput:
    return PortInput(
        kind=PortKindInput.STRUCTURE,
        identifier=constants.IMAGEJ_FILE_IDENTIFIER,
        key=p.key,
        label=p.label,
        description=p.description,
        nullable=p.required,
        scope=Scope.LOCAL,
        default=p.value,
        assignWidget=parameter_to_assign_widget(p),
        returnWidget=parameter_to_return_widget(p),
    )


def to_dataset(p: Parameter) -> PortInput:
    return PortInput(
        kind=PortKindInput.STRUCTURE,
        identifier=constants.IMAGEJ_DATASET_IDENTIFIER,
        key=p.key,
        label=p.label,
        description=p.description,
        nullable=p.required,
        scope=Scope.LOCAL,
        default=p.value,
        assignWidget=parameter_to_assign_widget(p),
        returnWidget=parameter_to_return_widget(p),
    )


class TranspileRegistry(BaseModel):
    type_map: dict[DataType, Callable[[Parameter], PortInput]] = {
        DataType.BIGINTEGER: to_int,
        DataType.BOOLEAN: to_bool,
        DataType.DOUBLE: to_float,
        DataType.FLOAT: to_float,
        DataType.INT: to_int,
        DataType.LONG: to_int,
        DataType.SHORT: to_int,
        DataType.STRING: to_str,
        DataType.CHAR: to_str,
        DataType.DATE: to_date,
        DataType.FILE: to_file,
        DataType.IMAGEPLUS: to_image_plus,
        DataType.DATASET: to_dataset,
        DataType.COLOR_RGB: to_color,
    }

    def transpile_parameter_to_port(self, p: Parameter) -> PortInput:
        return self.type_map[p.type](p)
