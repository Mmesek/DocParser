from dataclasses import dataclass
from typing import Any, Optional

TEMPLATES = {
    "Object": "name={name}, documentation={documentation}",
    "Parameter": ["{name}", ": {type_}", " = {default}"],
}

import json


def get_templates():
    with open("code_gen-mk2/python.json", "r", newline="", encoding="utf-8") as file:
        return json.load(file)


TEMPLATES = get_templates()


@dataclass
class Object:
    """Base Object metadata"""

    name: str
    """Object's name"""
    documentation: str
    """Object's docstring"""

    def __str__(self):
        template = TEMPLATES.get(self.__class__.__name__)
        if type(template) is list:
            s = ""
            for _template in template:
                try:
                    s += _template.format_map({k: v for k, v in self.__dict__.items() if v is not Optional})
                except KeyError:
                    continue
        else:
            s = template.format_map({k: v for k, v in self.__dict__.items()})
        return s


@dataclass
class Parameter(Object):
    """Parameter metadata"""

    type_: type
    """Parameter type"""
    optional: bool = False
    """Whether this parameter is optional"""
    array_size: Optional[int] = 0
    """Array size (If it's an array)"""
    mapping_type: Optional[tuple[str, str]] = Optional
    """Tuple representing key and value types for dictonaries (maps) or array type and item type (lists or sets)"""
    default: Optional[Any] = Optional
    """Default value"""


@dataclass
class Argument(Parameter):
    """Argument metadata"""

    value: Any = None


@dataclass
class Function(Object):
    """Function metadata"""

    parameters: list[Parameter]
    """List of parameters in this function"""
    keyword_only: list[Parameter]
    """List of keyword-only parameters in this function"""
    return_type: type
    """Return type"""
    is_method: bool = False
    """Whether it's a method"""
    decorators: Optional[list["Function"]] = Optional
    """List of Functions decorating this function"""
    examples: Optional[str] = Optional
    """Example usage of this function"""
    arguments: Optional[list[Argument]] = Optional
    """Arguments to use with this function"""

    def with_arguments(self, *arguments: Argument) -> "Function":
        """Returns Function with specified arguments for function call rendering"""
        return Function(name=self.name, arguments=arguments)


@dataclass
class Class(Object):
    """Class metadata"""

    bases: list["Class"]
    """Types this Class inherits from"""
    attributes: list[Parameter]
    """Atributes/Fields of this Class"""
    methods: Optional[list[Function]] = Optional
    """List of methods attached to this Class"""
    examples: Optional[str] = Optional
    """Example usage of this Class"""


@dataclass
class Route(Object):
    """Route metadata"""

    method: str
    """Method used with this Route"""
    path: str
    """Path of this Route"""
    parameters: Optional[list[Parameter]] = Optional
    """List of JSON parameters for this Route"""
    query_parameters: Optional[list[Parameter]] = Optional
    """List of query parameters for this Route"""
    required_permissions: Optional[list[str]] = Optional
    """List of required permissions to use this Route"""
    result_type: Optional[Any] = Optional
    """Result type of using this Route, if any"""
    examples: Optional[str] = Optional
    """Example usage of this Route"""
